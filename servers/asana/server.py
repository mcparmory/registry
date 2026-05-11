#!/usr/bin/env python3
"""
Asana MCP Server

API Info:
- API License: Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0)
- Contact: Asana Support (https://asana.com/support)
- Terms of Service: https://asana.com/terms

Generated: 2026-05-11 23:03:37 UTC
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
from mcp.types import ToolAnnotations
from pydantic import Field

BASE_URL = os.getenv("BASE_URL", "https://app.asana.com/api/1.0")
SERVER_NAME = "Asana"
SERVER_VERSION = "1.0.5"

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
    'oauth2',
    'personalAccessToken',
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
    _auth_handlers["personalAccessToken"] = _auth.BearerTokenAuth(env_var="BEARER_TOKEN", token_format="Bearer")
    logging.info("Authentication configured: personalAccessToken")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for personalAccessToken not configured: {error_msg}")
    _auth_handlers["personalAccessToken"] = None

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

mcp = FastMCP("Asana", middleware=[_JsonCoercionMiddleware()])

# Tags: Access requests
@mcp.tool(
    title="List Access Requests",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_access_requests(
    target: str = Field(..., description="The globally unique identifier of the target object for which to retrieve pending access requests."),
    user: str | None = Field(None, description="Filters results to access requests submitted by a specific user. Accepts the literal string 'me' for the authenticated user, a user's email address, or a user's globally unique identifier."),
) -> dict[str, Any] | ToolResult:
    """Retrieves pending access requests for a specified target object, optionally filtered to a specific user. Useful for reviewing who is awaiting permission to access a resource."""

    # Construct request model with validation
    try:
        _request = _models.GetAccessRequestsRequest(
            query=_models.GetAccessRequestsRequestQuery(target=target, user=user)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_access_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/access_requests"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_access_requests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_access_requests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_access_requests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Access requests
@mcp.tool(
    title="Request Access",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def request_access(
    target: str = Field(..., description="The unique global ID (gid) of the private object you are requesting access to. Supports projects and portfolios."),
    message: str | None = Field(None, description="An optional message to accompany the access request, allowing the requester to provide context or justification for why access is needed."),
) -> dict[str, Any] | ToolResult:
    """Submits an access request for a private project or portfolio, notifying the owner so they can grant or deny access."""

    # Construct request model with validation
    try:
        _request = _models.CreateAccessRequest(
            body=_models.CreateAccessRequestBody(data=_models.CreateAccessRequestBodyData(target=target, message=message))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for request_access: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/access_requests"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("request_access")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("request_access", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="request_access",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Access requests
@mcp.tool(
    title="Approve Access Request",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def approve_access_request(access_request_gid: str = Field(..., description="The globally unique identifier of the access request to approve.")) -> dict[str, Any] | ToolResult:
    """Approves a pending access request, granting the requester access to the associated target object. Use this to fulfill access requests that have been reviewed and authorized."""

    # Construct request model with validation
    try:
        _request = _models.ApproveAccessRequest(
            path=_models.ApproveAccessRequestPath(access_request_gid=access_request_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for approve_access_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/access_requests/{access_request_gid}/approve", _request.path.model_dump(by_alias=True)) if _request.path else "/access_requests/{access_request_gid}/approve"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("approve_access_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("approve_access_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="approve_access_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Access requests
@mcp.tool(
    title="Reject Access Request",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def reject_access_request(access_request_gid: str = Field(..., description="The globally unique identifier of the access request to reject.")) -> dict[str, Any] | ToolResult:
    """Rejects a pending access request for a target object, denying the requester permission to access the resource. Use this to explicitly decline access requests that should not be granted."""

    # Construct request model with validation
    try:
        _request = _models.RejectAccessRequest(
            path=_models.RejectAccessRequestPath(access_request_gid=access_request_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reject_access_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/access_requests/{access_request_gid}/reject", _request.path.model_dump(by_alias=True)) if _request.path else "/access_requests/{access_request_gid}/reject"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reject_access_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reject_access_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reject_access_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Allocations
@mcp.tool(
    title="Get Allocation",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_allocation(allocation_gid: str = Field(..., description="The globally unique identifier for the allocation you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single allocation, including all associated details and metadata. Use this to fetch full information about a specific allocation by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetAllocationRequest(
            path=_models.GetAllocationRequestPath(allocation_gid=allocation_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_allocation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/allocations/{allocation_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/allocations/{allocation_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_allocation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_allocation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_allocation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Allocations
@mcp.tool(
    title="Update Allocation",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_allocation(
    allocation_gid: str = Field(..., description="The globally unique identifier of the allocation to update."),
    data: _models.AllocationRequest | None = Field(None, description="An object containing the allocation fields to update; only the fields included will be modified, all other fields will retain their current values."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing allocation by replacing only the fields provided in the request body, leaving all unspecified fields unchanged. Returns the complete updated allocation record."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAllocationRequest(
            path=_models.UpdateAllocationRequestPath(allocation_gid=allocation_gid),
            body=_models.UpdateAllocationRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_allocation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/allocations/{allocation_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/allocations/{allocation_gid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_allocation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_allocation", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_allocation",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Allocations
@mcp.tool(
    title="Delete Allocation",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_allocation(allocation_gid: str = Field(..., description="The globally unique identifier of the allocation to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an existing allocation by its unique identifier. Returns an empty data record upon successful deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAllocationRequest(
            path=_models.DeleteAllocationRequestPath(allocation_gid=allocation_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_allocation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/allocations/{allocation_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/allocations/{allocation_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_allocation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_allocation", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_allocation",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Allocations
@mcp.tool(
    title="List Allocations",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_allocations(
    parent: str | None = Field(None, description="The unique identifier of the project to filter allocations by, returning only allocations associated with that project."),
    assignee: str | None = Field(None, description="The unique identifier of the user or placeholder to filter allocations by, returning only allocations assigned to that individual or placeholder resource."),
    workspace: str | None = Field(None, description="The unique identifier of the workspace to scope the allocation results to, limiting results to allocations within that workspace."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of allocations, optionally filtered by project, assignee, or workspace. Useful for reviewing how resources are distributed across tasks and team members."""

    # Construct request model with validation
    try:
        _request = _models.GetAllocationsRequest(
            query=_models.GetAllocationsRequestQuery(parent=parent, assignee=assignee, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_allocations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/allocations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_allocations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_allocations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_allocations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Allocations
@mcp.tool(
    title="Create Allocation",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_allocation(data: _models.CreateAllocationBodyData | None = Field(None, description="The allocation data to create, including all relevant fields for the new allocation record.")) -> dict[str, Any] | ToolResult:
    """Creates a new allocation and returns the full record of the newly created allocation."""

    # Construct request model with validation
    try:
        _request = _models.CreateAllocationRequest(
            body=_models.CreateAllocationRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_allocation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/allocations"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_allocation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_allocation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_allocation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Attachments
@mcp.tool(
    title="Get Attachment",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_attachment(attachment_gid: str = Field(..., description="The globally unique identifier of the attachment to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the full record for a single attachment, including its metadata and download URL. Requires the attachments:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetAttachmentRequest(
            path=_models.GetAttachmentRequestPath(attachment_gid=attachment_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/attachments/{attachment_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/attachments/{attachment_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_attachment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_attachment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Attachments
@mcp.tool(
    title="Delete Attachment",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_attachment(attachment_gid: str = Field(..., description="The globally unique identifier (GID) of the attachment to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific attachment by its unique identifier. Returns an empty data record upon successful deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAttachmentRequest(
            path=_models.DeleteAttachmentRequestPath(attachment_gid=attachment_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/attachments/{attachment_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/attachments/{attachment_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_attachment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_attachment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Attachments
@mcp.tool(
    title="List Attachments",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_attachments(parent: str = Field(..., description="The globally unique identifier (GID) of the parent object whose attachments you want to retrieve. Must reference a project, project brief, or task.")) -> dict[str, Any] | ToolResult:
    """Retrieves all attachments associated with a specified project, project brief, or task. For projects, this returns files in the 'Key resources' section; for tasks, this includes all associated files including inline images."""

    # Construct request model with validation
    try:
        _request = _models.GetAttachmentsForObjectRequest(
            query=_models.GetAttachmentsForObjectRequestQuery(parent=parent)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_attachments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/attachments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_attachments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_attachments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_attachments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Attachments
@mcp.tool(
    title="Upload Attachment",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def upload_attachment(
    resource_subtype: Literal["asana", "external"] | None = Field(None, description="Specifies the attachment type. Use 'asana' for direct file uploads or 'external' for linking an external URL resource. When set to 'external', the 'parent', 'name', and 'url' fields are also required."),
    file_: str | None = Field(None, alias="file", description="Base64-encoded file content for upload. The binary file content to upload. Required when 'resource_subtype' is 'asana' (direct file upload). Files from third-party services such as Dropbox, Box, Vimeo, or Google Drive cannot be attached via the API.", json_schema_extra={'format': 'byte'}),
    parent: str | None = Field(None, description="The unique identifier (GID) of the parent object to attach to — must be a task, project, or project brief. Required for all attachment types."),
    url: str | None = Field(None, description="The publicly accessible URL of the external resource to attach. Required when 'resource_subtype' is 'external'."),
    name: str | None = Field(None, description="A display name for the external resource being attached. Required when 'resource_subtype' is 'external'."),
    connect_to_app: bool | None = Field(None, description="When true, associates the current OAuth app with this external attachment to enable an in-task app components widget. Only applicable to external attachments on a parent task, requires OAuth authentication, and the app must be installed on a project containing the parent task."),
) -> dict[str, Any] | ToolResult:
    """Upload a file or link an external resource as an attachment to a task, project, or project brief in Asana. Supports direct file uploads (up to 100MB) or external URL attachments; multipart/form-data encoding is required for file uploads."""

    # Construct request model with validation
    try:
        _request = _models.CreateAttachmentForObjectRequest(
            body=_models.CreateAttachmentForObjectRequestBody(resource_subtype=resource_subtype, file_=file_, parent=parent, url=url, name=name, connect_to_app=connect_to_app)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/attachments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_attachment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_attachment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Audit log API
@mcp.tool(
    title="List Audit Log Events",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_audit_log_events(
    workspace_gid: str = Field(..., description="The globally unique identifier for the workspace or organization whose audit log events you want to retrieve."),
    start_at: str | None = Field(None, description="Restricts results to events created at or after this timestamp. Must be provided in ISO 8601 date-time format. Note that events before October 8th, 2021 are not available."),
    end_at: str | None = Field(None, description="Restricts results to events created strictly before this timestamp (exclusive upper bound). Must be provided in ISO 8601 date-time format."),
    event_type: str | None = Field(None, description="Restricts results to events of a specific type. Refer to the supported audit log events documentation for the full list of valid event type values."),
    actor_type: Literal["user", "asana", "asana_support", "anonymous", "external_administrator"] | None = Field(None, description="Restricts results to events performed by actors of a specific type. Use this only when filtering by actor type without a specific actor ID; omit this parameter if actor_gid is provided. Valid values are user, asana, asana_support, anonymous, or external_administrator."),
    actor_gid: str | None = Field(None, description="Restricts results to events triggered by the actor with this specific globally unique identifier. When provided, actor_type should be omitted."),
    resource_gid: str | None = Field(None, description="Restricts results to events associated with the resource that has this globally unique identifier."),
    limit: int | None = Field(None, description="The number of audit log events to return per page. Must be between 1 and 100 inclusive. Use the offset from the previous response to retrieve the next page of results.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of audit log events captured in a workspace or organization, sorted by creation time in ascending order. Supports filtering by time range, event type, actor, and resource, and can be polled continuously to stream new events as they are captured."""

    # Construct request model with validation
    try:
        _request = _models.GetAuditLogEventsRequest(
            path=_models.GetAuditLogEventsRequestPath(workspace_gid=workspace_gid),
            query=_models.GetAuditLogEventsRequestQuery(start_at=start_at, end_at=end_at, event_type=event_type, actor_type=actor_type, actor_gid=actor_gid, resource_gid=resource_gid, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_audit_log_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/audit_log_events", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/audit_log_events"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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

# Tags: Budgets
@mcp.tool(
    title="List Budgets",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_budgets(parent: str = Field(..., description="The globally unique identifier of the parent object whose budgets should be retrieved. Currently only project identifiers are supported as valid parents.")) -> dict[str, Any] | ToolResult:
    """Retrieves all budgets associated with a given parent object. Returns at most one budget per parent, which must be a project."""

    # Construct request model with validation
    try:
        _request = _models.GetBudgetsRequest(
            query=_models.GetBudgetsRequestQuery(parent=parent)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_budgets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/budgets"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_budgets")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_budgets", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_budgets",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Budgets
@mcp.tool(
    title="Create Budget",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_budget(data: _models.BudgetRequest | None = Field(None, description="The budget object containing all required fields to define the new budget, such as name, amount, currency, and associated scope or time period.")) -> dict[str, Any] | ToolResult:
    """Creates a new budget with the specified configuration. Use this to define spending limits and tracking parameters for a project, team, or time period."""

    # Construct request model with validation
    try:
        _request = _models.CreateBudgetRequest(
            body=_models.CreateBudgetRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_budget: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/budgets"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_budget")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_budget", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_budget",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Budgets
@mcp.tool(
    title="Get Budget",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_budget(budget_gid: str = Field(..., description="The globally unique identifier of the budget to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single budget, including all associated details and metadata. Use this to inspect a specific budget by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetBudgetRequest(
            path=_models.GetBudgetRequestPath(budget_gid=budget_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_budget: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/budgets/{budget_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/budgets/{budget_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_budget")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_budget", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_budget",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Budgets
@mcp.tool(
    title="Update Budget",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_budget(
    budget_gid: str = Field(..., description="The globally unique identifier of the budget to update."),
    data: _models.BudgetRequest | None = Field(None, description="An object containing the budget fields to update; only the fields included will be modified, all others will retain their current values."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing budget by replacing only the fields provided in the request body, leaving all unspecified fields unchanged."""

    # Construct request model with validation
    try:
        _request = _models.UpdateBudgetRequest(
            path=_models.UpdateBudgetRequestPath(budget_gid=budget_gid),
            body=_models.UpdateBudgetRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_budget: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/budgets/{budget_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/budgets/{budget_gid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_budget")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_budget", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_budget",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Budgets
@mcp.tool(
    title="Delete Budget",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_budget(budget_gid: str = Field(..., description="The globally unique identifier of the budget to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an existing budget by its unique identifier. Returns an empty data record upon successful deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteBudgetRequest(
            path=_models.DeleteBudgetRequestPath(budget_gid=budget_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_budget: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/budgets/{budget_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/budgets/{budget_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_budget")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_budget", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_budget",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom field settings
@mcp.tool(
    title="List Project Custom Field Settings",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_project_custom_field_settings(
    project_gid: str = Field(..., description="The globally unique identifier of the project whose custom field settings you want to retrieve."),
    limit: int | None = Field(None, description="The number of custom field settings to return per page. Must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all custom field settings configured on a specific project, returned in compact form. Use opt_fields to request additional field data beyond the default compact representation."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldSettingsForProjectRequest(
            path=_models.GetCustomFieldSettingsForProjectRequestPath(project_gid=project_gid),
            query=_models.GetCustomFieldSettingsForProjectRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_custom_field_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/custom_field_settings", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/custom_field_settings"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_custom_field_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_custom_field_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_custom_field_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom field settings
@mcp.tool(
    title="List Portfolio Custom Field Settings",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_portfolio_custom_field_settings(
    portfolio_gid: str = Field(..., description="The globally unique identifier of the portfolio whose custom field settings you want to retrieve."),
    limit: int | None = Field(None, description="The number of custom field setting objects to return per page. Must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all custom field settings configured on a specific portfolio, returned in compact form. Requires the portfolios:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldSettingsForPortfolioRequest(
            path=_models.GetCustomFieldSettingsForPortfolioRequestPath(portfolio_gid=portfolio_gid),
            query=_models.GetCustomFieldSettingsForPortfolioRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_portfolio_custom_field_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/portfolios/{portfolio_gid}/custom_field_settings", _request.path.model_dump(by_alias=True)) if _request.path else "/portfolios/{portfolio_gid}/custom_field_settings"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_portfolio_custom_field_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_portfolio_custom_field_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_portfolio_custom_field_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom field settings
@mcp.tool(
    title="List Goal Custom Field Settings",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_goal_custom_field_settings(
    goal_gid: str = Field(..., description="The globally unique identifier of the goal whose custom field settings you want to retrieve."),
    limit: int | None = Field(None, description="The number of custom field settings to return per page. Must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all custom field settings associated with a specific goal in compact form. Use opt_fields to request additional fields beyond the default compact representation."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldSettingsForGoalRequest(
            path=_models.GetCustomFieldSettingsForGoalRequestPath(goal_gid=goal_gid),
            query=_models.GetCustomFieldSettingsForGoalRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_goal_custom_field_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/goals/{goal_gid}/custom_field_settings", _request.path.model_dump(by_alias=True)) if _request.path else "/goals/{goal_gid}/custom_field_settings"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_goal_custom_field_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_goal_custom_field_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_goal_custom_field_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom field settings
@mcp.tool(
    title="List Team Custom Field Settings",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_team_custom_field_settings(team_gid: str = Field(..., description="The globally unique identifier for the team whose custom field settings you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves all custom field settings associated with a specific team, returned in compact form. Use opt_fields to request additional field data beyond the default compact representation."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldSettingsForTeamRequest(
            path=_models.GetCustomFieldSettingsForTeamRequestPath(team_gid=team_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_custom_field_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_gid}/custom_field_settings", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_gid}/custom_field_settings"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_team_custom_field_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_team_custom_field_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_team_custom_field_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom fields
@mcp.tool(
    title="Create Custom Field",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_custom_field(data: _models.CustomFieldCreateRequest | None = Field(None, description="The request body containing the custom field definition, including required properties such as workspace, name, and type (one of: text, enum, multi_enum, number, date, or people).")) -> dict[str, Any] | ToolResult:
    """Creates a new custom field within a specified workspace, supporting types such as text, enum, multi_enum, number, date, or people. The field name must be unique within the workspace and cannot conflict with existing task property names."""

    # Construct request model with validation
    try:
        _request = _models.CreateCustomFieldRequest(
            body=_models.CreateCustomFieldRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/custom_fields"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_custom_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_custom_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom fields
@mcp.tool(
    title="Get Custom Field",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_custom_field(custom_field_gid: str = Field(..., description="The globally unique identifier of the custom field to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete metadata definition for a specific custom field, including type-specific properties such as enum options, validation rules, and display settings."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldRequest(
            path=_models.GetCustomFieldRequestPath(custom_field_gid=custom_field_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_fields/{custom_field_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_fields/{custom_field_gid}"
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

# Tags: Custom fields
@mcp.tool(
    title="Update Custom Field",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_custom_field(
    custom_field_gid: str = Field(..., description="The globally unique identifier of the custom field to update."),
    data: _models.CustomFieldRequest | None = Field(None, description="An object containing only the custom field properties you wish to update; omitted fields retain their current values."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing custom field by its unique identifier, applying only the fields provided in the request body while leaving unspecified fields unchanged. Note that a custom field's type cannot be changed, enum options must be managed separately, and locked fields can only be updated by the user who locked them."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCustomFieldRequest(
            path=_models.UpdateCustomFieldRequestPath(custom_field_gid=custom_field_gid),
            body=_models.UpdateCustomFieldRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_fields/{custom_field_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_fields/{custom_field_gid}"
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

# Tags: Custom fields
@mcp.tool(
    title="Delete Custom Field",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_custom_field(custom_field_gid: str = Field(..., description="The globally unique identifier of the custom field to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an existing custom field by its unique identifier. Note that locked custom fields can only be deleted by the user who originally locked the field."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomFieldRequest(
            path=_models.DeleteCustomFieldRequestPath(custom_field_gid=custom_field_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_fields/{custom_field_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_fields/{custom_field_gid}"
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

# Tags: Custom fields
@mcp.tool(
    title="List Workspace Custom Fields",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_workspace_custom_fields(
    workspace_gid: str = Field(..., description="The globally unique identifier of the workspace or organization whose custom fields you want to retrieve."),
    limit: int | None = Field(None, description="The number of custom field records to return per page. Must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of all custom fields defined in a given workspace or organization. Returns compact representations suitable for discovery and reference."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFieldsForWorkspaceRequest(
            path=_models.GetCustomFieldsForWorkspaceRequestPath(workspace_gid=workspace_gid),
            query=_models.GetCustomFieldsForWorkspaceRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_custom_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/custom_fields", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/custom_fields"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom fields
@mcp.tool(
    title="Create Enum Option",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_enum_option(
    custom_field_gid: str = Field(..., description="The globally unique identifier of the custom field to which the new enum option will be added."),
    data: _models.EnumOptionRequest | None = Field(None, description="The payload defining the new enum option's properties, such as its name, color, and enabled state."),
) -> dict[str, Any] | ToolResult:
    """Creates a new enum option and appends it to the specified custom field's list of selectable values. A custom field supports up to 500 enum options (including disabled ones); locked fields can only be modified by the user who locked them."""

    # Construct request model with validation
    try:
        _request = _models.CreateEnumOptionForCustomFieldRequest(
            path=_models.CreateEnumOptionForCustomFieldRequestPath(custom_field_gid=custom_field_gid),
            body=_models.CreateEnumOptionForCustomFieldRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_enum_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_fields/{custom_field_gid}/enum_options", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_fields/{custom_field_gid}/enum_options"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_enum_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_enum_option", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_enum_option",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom fields
@mcp.tool(
    title="Reorder Enum Option",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def reorder_enum_option(
    custom_field_gid: str = Field(..., description="The globally unique identifier of the custom field whose enum options are being reordered."),
    enum_option: str | None = Field(None, description="The unique identifier of the enum option to move to a new position within the custom field."),
    before_enum_option: str | None = Field(None, description="The unique identifier of an existing enum option in this custom field; the target enum option will be inserted immediately before it. Mutually exclusive with after_enum_option."),
    after_enum_option: str | None = Field(None, description="The unique identifier of an existing enum option in this custom field; the target enum option will be inserted immediately after it. Mutually exclusive with before_enum_option."),
) -> dict[str, Any] | ToolResult:
    """Repositions a specific enum option within a custom field's ordered list by placing it before or after another existing enum option. Locked custom fields can only be reordered by the user who locked the field."""

    # Construct request model with validation
    try:
        _request = _models.InsertEnumOptionForCustomFieldRequest(
            path=_models.InsertEnumOptionForCustomFieldRequestPath(custom_field_gid=custom_field_gid),
            body=_models.InsertEnumOptionForCustomFieldRequestBody(data=_models.InsertEnumOptionForCustomFieldRequestBodyData(enum_option=enum_option, before_enum_option=before_enum_option, after_enum_option=after_enum_option) if any(v is not None for v in [enum_option, before_enum_option, after_enum_option]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reorder_enum_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_fields/{custom_field_gid}/enum_options/insert", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_fields/{custom_field_gid}/enum_options/insert"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reorder_enum_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reorder_enum_option", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reorder_enum_option",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom fields
@mcp.tool(
    title="Update Enum Option",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_enum_option(
    enum_option_gid: str = Field(..., description="The globally unique identifier of the enum option to update."),
    name: str | None = Field(None, description="The display name of the enum option as it appears in the custom field."),
    enabled: bool | None = Field(None, description="Controls whether this enum option is selectable by users on the custom field. At least one option must remain enabled on the field."),
    color: str | None = Field(None, description="The color associated with the enum option for visual identification. Defaults to none if not specified."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing enum option on a custom field, allowing changes to its name, color, or enabled state. Locked custom fields can only be modified by the user who locked them, and at least one enabled enum option must remain on the field."""

    # Construct request model with validation
    try:
        _request = _models.UpdateEnumOptionRequest(
            path=_models.UpdateEnumOptionRequestPath(enum_option_gid=enum_option_gid),
            body=_models.UpdateEnumOptionRequestBody(data=_models.UpdateEnumOptionRequestBodyData(name=name, enabled=enabled, color=color) if any(v is not None for v in [name, enabled, color]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_enum_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/enum_options/{enum_option_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/enum_options/{enum_option_gid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_enum_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_enum_option", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_enum_option",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom types
@mcp.tool(
    title="List Custom Types",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_custom_types(
    project: str = Field(..., description="The globally unique identifier of the project whose associated custom types you want to retrieve."),
    limit: int | None = Field(None, description="The number of custom types to return per page. Accepts values between 1 and 100 inclusive.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all custom types associated with a specified project. Use `opt_fields` to request additional fields beyond the default compact representation."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomTypesRequest(
            query=_models.GetCustomTypesRequestQuery(project=project, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_types: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/custom_types"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom types
@mcp.tool(
    title="Get Custom Type",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_custom_type(custom_type_gid: str = Field(..., description="The globally unique identifier of the custom type to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single custom type by its unique identifier. Use this to inspect the full definition and configuration of a specific custom type."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomTypeRequest(
            path=_models.GetCustomTypeRequestPath(custom_type_gid=custom_type_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/custom_types/{custom_type_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/custom_types/{custom_type_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_type", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_type",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool(
    title="List Resource Events",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_resource_events(
    resource: str = Field(..., description="The unique ID of the resource (task, project, or goal) whose events you want to retrieve."),
    sync: str | None = Field(None, description="A sync token from a previous response used to fetch only new events since that point in time. Omit on the first request to receive a fresh sync token; if the token has expired (HTTP 412), use the new token returned in that error response to resume."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all events that have occurred on a resource (task, project, or goal) since a given sync token was created. Returns up to 100 events per request, with a new sync token to paginate forward through additional events."""

    # Construct request model with validation
    try:
        _request = _models.GetEventsRequest(
            query=_models.GetEventsRequestQuery(resource=resource, sync=sync)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_resource_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/events"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_resource_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_resource_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_resource_events",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Exports
@mcp.tool(
    title="Export Graph",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def export_graph(parent: str | None = Field(None, description="The globally unique ID of the parent object (goal, project, portfolio, or team) whose graph data should be exported.")) -> dict[str, Any] | ToolResult:
    """Initiates an asynchronous graph export job for a goal, team, portfolio, or project. Use the jobs endpoint to monitor progress; exports exceeding 1,000 tasks are cached for 4 hours, with subsequent requests returning the cached result."""

    # Construct request model with validation
    try:
        _request = _models.CreateGraphExportRequest(
            body=_models.CreateGraphExportRequestBody(data=_models.CreateGraphExportRequestBodyData(parent=parent) if any(v is not None for v in [parent]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_graph: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/exports/graph"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_graph")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_graph", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_graph",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Exports
@mcp.tool(
    title="Create Resource Export",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_resource_export(
    workspace: str | None = Field(None, description="The GID of the workspace whose resources will be exported. Only one in-progress export is permitted per workspace at a time."),
    export_request_parameters: list[_models.ResourceExportRequestParameter] | None = Field(None, description="An array of export request parameter objects, where each object specifies a resource GID and its associated export options (such as filters and fields). Providing multiple entries for the same resource type achieves a disjunctive filter but may produce duplicate results. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Initiates an asynchronous bulk export of workspace resources (tasks, teams, or messages) in gzip-compressed JSON Lines format. Export progress can be monitored via the jobs endpoint, and the resulting file is accessible for 30 days after completion."""

    # Construct request model with validation
    try:
        _request = _models.CreateResourceExportRequest(
            body=_models.CreateResourceExportRequestBody(data=_models.CreateResourceExportRequestBodyData(workspace=workspace, export_request_parameters=export_request_parameters) if any(v is not None for v in [workspace, export_request_parameters]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_resource_export: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/exports/resource"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_resource_export")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_resource_export", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_resource_export",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goal relationships
@mcp.tool(
    title="Get Goal Relationship",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_goal_relationship(goal_relationship_gid: str = Field(..., description="The unique identifier of the goal relationship to retrieve. This ID is returned when a goal relationship is created or listed.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single goal relationship, including details about how two goals are linked. Use this to inspect the nature and status of a specific goal-to-goal connection."""

    # Construct request model with validation
    try:
        _request = _models.GetGoalRelationshipRequest(
            path=_models.GetGoalRelationshipRequestPath(goal_relationship_gid=goal_relationship_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_goal_relationship: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/goal_relationships/{goal_relationship_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/goal_relationships/{goal_relationship_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_goal_relationship")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_goal_relationship", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_goal_relationship",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goal relationships
@mcp.tool(
    title="Update Goal Relationship",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_goal_relationship(
    goal_relationship_gid: str = Field(..., description="The globally unique identifier of the goal relationship to update."),
    data: _models.GoalRelationshipRequest | None = Field(None, description="The fields to update on the goal relationship; only provided fields will be modified, all others remain unchanged."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing goal relationship by replacing only the fields provided in the request body, leaving all other fields unchanged. Returns the complete updated goal relationship record."""

    # Construct request model with validation
    try:
        _request = _models.UpdateGoalRelationshipRequest(
            path=_models.UpdateGoalRelationshipRequestPath(goal_relationship_gid=goal_relationship_gid),
            body=_models.UpdateGoalRelationshipRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_goal_relationship: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/goal_relationships/{goal_relationship_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/goal_relationships/{goal_relationship_gid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_goal_relationship")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_goal_relationship", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_goal_relationship",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goal relationships
@mcp.tool(
    title="List Goal Relationships",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_goal_relationships(
    supported_goal: str = Field(..., description="The globally unique identifier of the supported goal whose relationships you want to retrieve. This is a required field that scopes the results to a specific goal."),
    limit: int | None = Field(None, description="The maximum number of goal relationship records to return per page, between 1 and 100.", ge=1, le=100),
    resource_subtype: str | None = Field(None, description="Filters the returned goal relationships to only those matching the specified resource subtype, such as a subgoal relationship."),
) -> dict[str, Any] | ToolResult:
    """Retrieves compact goal relationship records for a specified supported goal, allowing you to explore how goals are connected within your workspace."""

    # Construct request model with validation
    try:
        _request = _models.GetGoalRelationshipsRequest(
            query=_models.GetGoalRelationshipsRequestQuery(limit=limit, supported_goal=supported_goal, resource_subtype=resource_subtype)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_goal_relationships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/goal_relationships"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_goal_relationships")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_goal_relationships", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_goal_relationships",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goal relationships
@mcp.tool(
    title="Add Goal Supporting Relationship",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_goal_supporting_relationship(
    goal_gid: str = Field(..., description="The unique identifier of the parent goal to which the supporting resource will be linked."),
    supporting_resource: str = Field(..., description="The unique identifier of the resource to add as a supporting relationship to the parent goal. Must be the GID of a goal, project, task, or portfolio."),
    insert_before: str | None = Field(None, description="The GID of an existing subgoal of the parent goal; the new subgoal will be inserted immediately before it. Cannot be used together with `insert_after`. Only supported when adding a subgoal."),
    insert_after: str | None = Field(None, description="The GID of an existing subgoal of the parent goal; the new subgoal will be inserted immediately after it. Cannot be used together with `insert_before`. Only supported when adding a subgoal."),
    contribution_weight: float | None = Field(None, description="A weight between 0 and 1 (inclusive) that determines how much the supporting resource's progress contributes to the parent goal's overall progress. Must be greater than 0 for the supporting resource to count toward automatically calculated parent goal metrics. Defaults to 0."),
) -> dict[str, Any] | ToolResult:
    """Links a supporting resource (goal, project, task, or portfolio) to a parent goal, establishing a progress relationship between them. Returns the newly created goal relationship record."""

    # Construct request model with validation
    try:
        _request = _models.AddSupportingRelationshipRequest(
            path=_models.AddSupportingRelationshipRequestPath(goal_gid=goal_gid),
            body=_models.AddSupportingRelationshipRequestBody(data=_models.AddSupportingRelationshipRequestBodyData(supporting_resource=supporting_resource, insert_before=insert_before, insert_after=insert_after, contribution_weight=contribution_weight))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_goal_supporting_relationship: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/goals/{goal_gid}/addSupportingRelationship", _request.path.model_dump(by_alias=True)) if _request.path else "/goals/{goal_gid}/addSupportingRelationship"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_goal_supporting_relationship")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_goal_supporting_relationship", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_goal_supporting_relationship",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goal relationships
@mcp.tool(
    title="Remove Goal Supporting Relationship",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_goal_supporting_relationship(
    goal_gid: str = Field(..., description="The unique identifier of the parent goal from which the supporting relationship will be removed."),
    supporting_resource: str = Field(..., description="The unique identifier of the supporting resource to unlink from the parent goal; must be the identifier of a goal, project, task, or portfolio."),
) -> dict[str, Any] | ToolResult:
    """Removes a supporting relationship between a child resource and a parent goal, unlinking a goal, project, task, or portfolio that was previously set as a supporting resource."""

    # Construct request model with validation
    try:
        _request = _models.RemoveSupportingRelationshipRequest(
            path=_models.RemoveSupportingRelationshipRequestPath(goal_gid=goal_gid),
            body=_models.RemoveSupportingRelationshipRequestBody(data=_models.RemoveSupportingRelationshipRequestBodyData(supporting_resource=supporting_resource))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_goal_supporting_relationship: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/goals/{goal_gid}/removeSupportingRelationship", _request.path.model_dump(by_alias=True)) if _request.path else "/goals/{goal_gid}/removeSupportingRelationship"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_goal_supporting_relationship")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_goal_supporting_relationship", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_goal_supporting_relationship",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals
@mcp.tool(
    title="Get Goal",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_goal(goal_gid: str = Field(..., description="The globally unique identifier of the goal to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single goal, including all associated fields and metadata. Requires the goals:read scope, with additional time_periods:read scope needed to access the time_period field."""

    # Construct request model with validation
    try:
        _request = _models.GetGoalRequest(
            path=_models.GetGoalRequestPath(goal_gid=goal_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_goal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/goals/{goal_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/goals/{goal_gid}"
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
@mcp.tool(
    title="Update Goal",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_goal(
    goal_gid: str = Field(..., description="The globally unique identifier of the goal to update."),
    data: _models.GoalUpdateRequest | None = Field(None, description="An object containing the goal fields to update; only the fields included will be modified, all unspecified fields retain their current values."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing goal by replacing only the fields provided in the request body, leaving all other fields unchanged. Returns the complete updated goal record."""

    # Construct request model with validation
    try:
        _request = _models.UpdateGoalRequest(
            path=_models.UpdateGoalRequestPath(goal_gid=goal_gid),
            body=_models.UpdateGoalRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_goal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/goals/{goal_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/goals/{goal_gid}"
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
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals
@mcp.tool(
    title="Delete Goal",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_goal(goal_gid: str = Field(..., description="The globally unique identifier of the goal to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an existing goal by its unique identifier. Returns an empty data record upon successful deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteGoalRequest(
            path=_models.DeleteGoalRequestPath(goal_gid=goal_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_goal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/goals/{goal_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/goals/{goal_gid}"
    _http_headers = {}

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
@mcp.tool(
    title="List Goals",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_goals(
    portfolio: str | None = Field(None, description="The globally unique identifier of a portfolio to filter goals that support it."),
    project: str | None = Field(None, description="The globally unique identifier of a project to filter goals that support it."),
    task: str | None = Field(None, description="The globally unique identifier of a task to filter goals that support it."),
    is_workspace_level: bool | None = Field(None, description="When true, filters results to only workspace-level goals. Must be used together with the workspace parameter."),
    team: str | None = Field(None, description="The globally unique identifier of a team to filter goals belonging to that team."),
    workspace: str | None = Field(None, description="The globally unique identifier of a workspace to filter goals within that workspace."),
    time_periods: list[str] | None = Field(None, description="A comma-separated list of globally unique time period identifiers to filter goals associated with those periods. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of compact goal records, optionally filtered by workspace, team, portfolio, project, task, or time period. Requires the goals:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetGoalsRequest(
            query=_models.GetGoalsRequestQuery(portfolio=portfolio, project=project, task=task, is_workspace_level=is_workspace_level, team=team, workspace=workspace, time_periods=time_periods)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_goals: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/goals"
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
@mcp.tool(
    title="Create Goal",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_goal(data: _models.GoalRequest | None = Field(None, description="The goal object containing the details for the new goal, such as name, owner, due date, and associated workspace or team.")) -> dict[str, Any] | ToolResult:
    """Creates a new goal within a specified workspace or team. Returns the full record of the newly created goal."""

    # Construct request model with validation
    try:
        _request = _models.CreateGoalRequest(
            body=_models.CreateGoalRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_goal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/goals"
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
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals
@mcp.tool(
    title="Set Goal Metric",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def set_goal_metric(
    goal_gid: str = Field(..., description="The globally unique identifier of the goal to which the metric will be attached."),
    precision: int | None = Field(None, description="Only applicable for metrics of type Number. Specifies the number of decimal places to display, where 0 means integer values, 1 rounds to the nearest tenth, and so on. Must be between 0 and 6 inclusive. Note: for percentage format, the precision applies to the raw decimal value before conversion to a percentage display."),
    unit: Literal["none", "currency", "percentage"] | None = Field(None, description="The unit of measurement for the goal metric. Use 'currency' to enable currency formatting, 'percentage' for percentage-based progress, or 'none' for a unitless number."),
    currency_code: str | None = Field(None, description="The ISO 4217 currency code used to format the metric value. Only applicable when the unit is set to 'currency'; otherwise this field is null."),
    initial_number_value: float | None = Field(None, description="The starting value of the numeric goal metric, representing the baseline from which progress is measured."),
    target_number_value: float | None = Field(None, description="The target value the numeric goal metric must reach to be considered complete. Must differ from the initial value."),
    current_number_value: float | None = Field(None, description="The current value of the numeric goal metric, reflecting progress made so far between the initial and target values."),
    progress_source: Literal["manual", "subgoal_progress", "project_task_completion", "project_milestone_completion", "task_completion", "external"] | None = Field(None, description="Defines how the goal's progress value is calculated. Choose 'manual' for user-entered progress, one of the automatic options to derive progress from subgoals, projects, or tasks, or 'external' for integration-managed progress from a source such as Salesforce."),
    is_custom_weight: bool | None = Field(None, description="Only applicable when progress_source is 'subgoal_progress', 'project_task_completion', 'project_milestone_completion', or 'task_completion'. When true, each supporting object's custom weight is used in the progress calculation; when false, all supporting objects are treated as equally weighted."),
) -> dict[str, Any] | ToolResult:
    """Creates and attaches a progress metric to a specified goal, defining how goal completion is measured and tracked. If a metric already exists on the goal, it will be replaced entirely."""

    # Construct request model with validation
    try:
        _request = _models.CreateGoalMetricRequest(
            path=_models.CreateGoalMetricRequestPath(goal_gid=goal_gid),
            body=_models.CreateGoalMetricRequestBody(data=_models.CreateGoalMetricRequestBodyData(precision=precision, unit=unit, currency_code=currency_code, initial_number_value=initial_number_value, target_number_value=target_number_value, current_number_value=current_number_value, progress_source=progress_source, is_custom_weight=is_custom_weight) if any(v is not None for v in [precision, unit, currency_code, initial_number_value, target_number_value, current_number_value, progress_source, is_custom_weight]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_goal_metric: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/goals/{goal_gid}/setMetric", _request.path.model_dump(by_alias=True)) if _request.path else "/goals/{goal_gid}/setMetric"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_goal_metric")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_goal_metric", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_goal_metric",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals
@mcp.tool(
    title="Update Goal Metric Value",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_goal_metric_value(
    goal_gid: str = Field(..., description="The globally unique identifier of the goal whose metric value you want to update."),
    current_number_value: float | None = Field(None, description="The new current value to record for the goal's numeric metric, reflecting the latest progress toward the goal's target."),
) -> dict[str, Any] | ToolResult:
    """Updates the current numeric value of an existing goal metric, allowing progress tracking against a defined target. Requires the goal to already have a numeric metric configured; returns the complete updated goal metric record."""

    # Construct request model with validation
    try:
        _request = _models.UpdateGoalMetricRequest(
            path=_models.UpdateGoalMetricRequestPath(goal_gid=goal_gid),
            body=_models.UpdateGoalMetricRequestBody(data=_models.UpdateGoalMetricRequestBodyData(current_number_value=current_number_value) if any(v is not None for v in [current_number_value]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_goal_metric_value: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/goals/{goal_gid}/setMetricCurrentValue", _request.path.model_dump(by_alias=True)) if _request.path else "/goals/{goal_gid}/setMetricCurrentValue"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_goal_metric_value")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_goal_metric_value", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_goal_metric_value",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals
@mcp.tool(
    title="Add Goal Followers",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_goal_followers(
    goal_gid: str = Field(..., description="The unique identifier of the goal to which followers will be added."),
    followers: list[str] = Field(..., description="A list of users to add as followers to the goal. Each item can be the string 'me' to reference the authenticated user, a user's email address, or a user's GID. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Adds one or more followers (collaborators) to a specified goal. Returns the complete updated goal record reflecting the new followers."""

    # Construct request model with validation
    try:
        _request = _models.AddFollowersRequest(
            path=_models.AddFollowersRequestPath(goal_gid=goal_gid),
            body=_models.AddFollowersRequestBody(data=_models.AddFollowersRequestBodyData(followers=followers))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_goal_followers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/goals/{goal_gid}/addFollowers", _request.path.model_dump(by_alias=True)) if _request.path else "/goals/{goal_gid}/addFollowers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_goal_followers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_goal_followers", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_goal_followers",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals
@mcp.tool(
    title="Remove Goal Followers",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_goal_followers(
    goal_gid: str = Field(..., description="The globally unique identifier of the goal from which followers will be removed."),
    followers: list[str] = Field(..., description="A list of users to remove as followers from the goal. Each item can be the string 'me' to reference the authenticated user, a user's email address, or a user's globally unique identifier (gid). Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Removes one or more followers (collaborators) from a specified goal. Returns the complete updated goal record reflecting the removed followers."""

    # Construct request model with validation
    try:
        _request = _models.RemoveFollowersRequest(
            path=_models.RemoveFollowersRequestPath(goal_gid=goal_gid),
            body=_models.RemoveFollowersRequestBody(data=_models.RemoveFollowersRequestBodyData(followers=followers))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_goal_followers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/goals/{goal_gid}/removeFollowers", _request.path.model_dump(by_alias=True)) if _request.path else "/goals/{goal_gid}/removeFollowers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_goal_followers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_goal_followers", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_goal_followers",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals
@mcp.tool(
    title="List Parent Goals",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_parent_goals(goal_gid: str = Field(..., description="The globally unique identifier of the goal whose parent goals you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a compact list of all parent goals associated with a specified goal. Useful for traversing goal hierarchies and understanding how a goal rolls up into broader objectives."""

    # Construct request model with validation
    try:
        _request = _models.GetParentGoalsForGoalRequest(
            path=_models.GetParentGoalsForGoalRequestPath(goal_gid=goal_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_parent_goals: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/goals/{goal_gid}/parentGoals", _request.path.model_dump(by_alias=True)) if _request.path else "/goals/{goal_gid}/parentGoals"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_parent_goals")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_parent_goals", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_parent_goals",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals
@mcp.tool(
    title="Add Custom Field to Goal",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_custom_field_to_goal(
    goal_gid: str = Field(..., description="The globally unique identifier of the goal to which the custom field setting will be added."),
    custom_field: str | _models.CustomFieldCreateRequest = Field(..., description="The globally unique identifier of the custom field to associate with the goal."),
    is_important: bool | None = Field(None, description="When set to true, marks this custom field as important for the goal, causing it to be prominently displayed in list views of the goal."),
    insert_before: str | None = Field(None, description="The GID of an existing custom field setting on this goal before which the new custom field setting will be inserted to control display order. Cannot be used together with insert_after."),
    insert_after: str | None = Field(None, description="The GID of an existing custom field setting on this goal after which the new custom field setting will be inserted to control display order. Cannot be used together with insert_before."),
) -> dict[str, Any] | ToolResult:
    """Associates a custom field with a goal by creating a custom field setting, allowing the field to appear and be tracked on the specified goal."""

    # Construct request model with validation
    try:
        _request = _models.AddCustomFieldSettingForGoalRequest(
            path=_models.AddCustomFieldSettingForGoalRequestPath(goal_gid=goal_gid),
            body=_models.AddCustomFieldSettingForGoalRequestBody(data=_models.AddCustomFieldSettingForGoalRequestBodyData(custom_field=custom_field, is_important=is_important, insert_before=insert_before, insert_after=insert_after))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_custom_field_to_goal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/goals/{goal_gid}/addCustomFieldSetting", _request.path.model_dump(by_alias=True)) if _request.path else "/goals/{goal_gid}/addCustomFieldSetting"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_custom_field_to_goal")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_custom_field_to_goal", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_custom_field_to_goal",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals
@mcp.tool(
    title="Remove Custom Field from Goal",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_custom_field_from_goal(
    goal_gid: str = Field(..., description="The globally unique identifier of the goal from which the custom field setting will be removed."),
    custom_field: str = Field(..., description="The globally unique identifier of the custom field to remove from the goal."),
) -> dict[str, Any] | ToolResult:
    """Removes a custom field setting from a specified goal, detaching the custom field and its associated data from the goal. Requires the goals:write scope."""

    # Construct request model with validation
    try:
        _request = _models.RemoveCustomFieldSettingForGoalRequest(
            path=_models.RemoveCustomFieldSettingForGoalRequestPath(goal_gid=goal_gid),
            body=_models.RemoveCustomFieldSettingForGoalRequestBody(data=_models.RemoveCustomFieldSettingForGoalRequestBodyData(custom_field=custom_field))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_custom_field_from_goal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/goals/{goal_gid}/removeCustomFieldSetting", _request.path.model_dump(by_alias=True)) if _request.path else "/goals/{goal_gid}/removeCustomFieldSetting"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_custom_field_from_goal")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_custom_field_from_goal", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_custom_field_from_goal",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Jobs
@mcp.tool(
    title="Get Job",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_job(job_gid: str = Field(..., description="The globally unique identifier of the job to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the full record for a specific asynchronous job by its unique identifier. Useful for polling job status and accessing output resources such as new tasks, projects, portfolios, or templates created by the job."""

    # Construct request model with validation
    try:
        _request = _models.GetJobRequest(
            path=_models.GetJobRequestPath(job_gid=job_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/jobs/{job_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/jobs/{job_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Memberships
@mcp.tool(
    title="List Memberships",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_memberships(
    parent: str | None = Field(None, description="The globally unique identifier of the parent resource to retrieve memberships for; accepted parent types are goal, project, portfolio, custom_type, or custom_field. Optional when both member and resource_subtype are provided together."),
    member: str | None = Field(None, description="The globally unique identifier of a user or team to filter memberships by; when combined with resource_subtype and no parent is specified, returns all memberships of that subtype for this member."),
    resource_subtype: Literal["project_membership"] | None = Field(None, description="Specifies the membership subtype to return; required when parent is absent, and must be paired with a member GID to retrieve all memberships of that type for the given member."),
) -> dict[str, Any] | ToolResult:
    """Retrieves compact membership records for a given parent resource (goal, project, portfolio, custom type, or custom field), optionally filtered by a specific member. Alternatively, when no parent is specified, returns all memberships of a given subtype for a specific member by combining the member and resource_subtype parameters."""

    # Construct request model with validation
    try:
        _request = _models.GetMembershipsRequest(
            query=_models.GetMembershipsRequestQuery(parent=parent, member=member, resource_subtype=resource_subtype)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/memberships"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_memberships")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_memberships", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_memberships",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Memberships
@mcp.tool(
    title="Create Membership",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_membership(data: _models.CreateMembershipRequest | None = Field(None, description="The membership details including the resource to join (goal, project, portfolio, custom type, or custom field) and the member to add (Team or User).")) -> dict[str, Any] | ToolResult:
    """Creates a new membership linking a Team or User to a goal, project, portfolio, custom type, or custom field. Returns the full record of the newly created membership."""

    # Construct request model with validation
    try:
        _request = _models.CreateMembershipRequest(
            body=_models.CreateMembershipRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/memberships"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_membership")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_membership", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_membership",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Memberships
@mcp.tool(
    title="Get Membership",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_membership(membership_gid: str = Field(..., description="The globally unique identifier of the membership record to retrieve, applicable across all membership types (project, goal, portfolio, custom type, or custom field).")) -> dict[str, Any] | ToolResult:
    """Retrieves a single membership record by its unique identifier, returning details for any supported membership type including project, goal, portfolio, custom type, or custom field memberships."""

    # Construct request model with validation
    try:
        _request = _models.GetMembershipRequest(
            path=_models.GetMembershipRequestPath(membership_gid=membership_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/memberships/{membership_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/memberships/{membership_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_membership")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_membership", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_membership",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Memberships
@mcp.tool(
    title="Update Membership",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_membership(
    membership_gid: str = Field(..., description="The globally unique identifier of the membership to update."),
    access_level: str | None = Field(None, description="The access level to assign to the member. Valid values vary by resource type: goals support 'viewer', 'commenter', 'editor', or 'admin'; projects support 'admin', 'editor', or 'commenter'; portfolios support 'admin', 'editor', or 'viewer'; custom fields support 'admin', 'editor', or 'user'."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing membership by replacing only the fields provided in the request body, leaving all other fields unchanged. Supports memberships on goals, projects, portfolios, custom types, and custom fields."""

    # Construct request model with validation
    try:
        _request = _models.UpdateMembershipRequest(
            path=_models.UpdateMembershipRequestPath(membership_gid=membership_gid),
            body=_models.UpdateMembershipRequestBody(data=_models.UpdateMembershipRequestBodyData(access_level=access_level) if any(v is not None for v in [access_level]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/memberships/{membership_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/memberships/{membership_gid}"
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
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Memberships
@mcp.tool(
    title="Delete Membership",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_membership(membership_gid: str = Field(..., description="The globally unique identifier of the membership to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently removes an existing membership from a goal, project, portfolio, custom type, or custom field. Returns an empty data record upon successful deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteMembershipRequest(
            path=_models.DeleteMembershipRequestPath(membership_gid=membership_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/memberships/{membership_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/memberships/{membership_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_membership")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_membership", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_membership",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organization exports
@mcp.tool(
    title="Create Organization Export",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_organization_export(organization: str | None = Field(None, description="The globally unique identifier of the workspace or organization to export.")) -> dict[str, Any] | ToolResult:
    """Initiates an export request for an entire Asana organization. Asana processes and completes the export asynchronously after the request is submitted."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrganizationExportRequest(
            body=_models.CreateOrganizationExportRequestBody(data=_models.CreateOrganizationExportRequestBodyData(organization=organization) if any(v is not None for v in [organization]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_organization_export: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/organization_exports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_organization_export")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_organization_export", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_organization_export",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Organization exports
@mcp.tool(
    title="Get Organization Export",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_organization_export(organization_export_gid: str = Field(..., description="The globally unique identifier of the organization export request to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the current status and details of a previously requested organization export. Use this to check export progress or access the resulting download URL once complete."""

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationExportRequest(
            path=_models.GetOrganizationExportRequestPath(organization_export_gid=organization_export_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization_export: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organization_exports/{organization_export_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/organization_exports/{organization_export_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_organization_export")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_organization_export", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_organization_export",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Portfolio memberships
@mcp.tool(
    title="List Portfolio Memberships",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_portfolio_memberships(
    portfolio: str | None = Field(None, description="The unique identifier of the portfolio to filter memberships by. Required unless filtering by workspace and user."),
    workspace: str | None = Field(None, description="The unique identifier of the workspace to filter memberships by. Must be combined with a user identifier when specified."),
    user: str | None = Field(None, description="Identifies the user whose memberships to filter by. Accepts the string 'me' for the current user, a user's email address, or a user's global ID (gid)."),
    limit: int | None = Field(None, description="The number of membership records to return per page. Accepts values between 1 and 100 inclusive.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of portfolio memberships in compact representation. You must provide either a portfolio ID, a portfolio and user combination, or a workspace and user combination to filter results."""

    # Construct request model with validation
    try:
        _request = _models.GetPortfolioMembershipsRequest(
            query=_models.GetPortfolioMembershipsRequestQuery(portfolio=portfolio, workspace=workspace, user=user, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_portfolio_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/portfolio_memberships"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_portfolio_memberships")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_portfolio_memberships", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_portfolio_memberships",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Portfolio memberships
@mcp.tool(
    title="Get Portfolio Membership",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_portfolio_membership(portfolio_membership_gid: str = Field(..., description="The unique identifier (GID) of the portfolio membership to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete details of a single portfolio membership record. Use this to inspect a specific user's membership relationship within a portfolio."""

    # Construct request model with validation
    try:
        _request = _models.GetPortfolioMembershipRequest(
            path=_models.GetPortfolioMembershipRequestPath(portfolio_membership_gid=portfolio_membership_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_portfolio_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/portfolio_memberships/{portfolio_membership_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/portfolio_memberships/{portfolio_membership_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_portfolio_membership")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_portfolio_membership", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_portfolio_membership",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Portfolio memberships
@mcp.tool(
    title="List Portfolio Memberships",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_portfolio_memberships_for_portfolio(
    portfolio_gid: str = Field(..., description="The globally unique identifier of the portfolio whose memberships you want to retrieve."),
    user: str | None = Field(None, description="Filters memberships to a specific user. Accepts the string 'me' for the authenticated user, a user's email address, or a user's globally unique identifier."),
    limit: int | None = Field(None, description="The number of membership records to return per page. Must be between 1 and 100 inclusive.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all membership records for a specified portfolio, returning compact representations of each member. Optionally filter results by a specific user."""

    # Construct request model with validation
    try:
        _request = _models.GetPortfolioMembershipsForPortfolioRequest(
            path=_models.GetPortfolioMembershipsForPortfolioRequestPath(portfolio_gid=portfolio_gid),
            query=_models.GetPortfolioMembershipsForPortfolioRequestQuery(user=user, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_portfolio_memberships_for_portfolio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/portfolios/{portfolio_gid}/portfolio_memberships", _request.path.model_dump(by_alias=True)) if _request.path else "/portfolios/{portfolio_gid}/portfolio_memberships"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_portfolio_memberships_for_portfolio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_portfolio_memberships_for_portfolio", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_portfolio_memberships_for_portfolio",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Portfolios
@mcp.tool(
    title="List Portfolios",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_portfolios(
    workspace: str = Field(..., description="The unique identifier of the workspace or organization used to filter the returned portfolios."),
    owner: str | None = Field(None, description="The unique identifier of the user whose portfolios should be returned. Standard API users are limited to their own portfolios; Service Accounts may specify any user or omit this parameter to retrieve all portfolios in the workspace."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a compact list of portfolios owned by the current API user within a specified workspace. Service Accounts can optionally filter by owner or retrieve all portfolios across the workspace."""

    # Construct request model with validation
    try:
        _request = _models.GetPortfoliosRequest(
            query=_models.GetPortfoliosRequestQuery(workspace=workspace, owner=owner)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_portfolios: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/portfolios"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_portfolios")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_portfolios", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_portfolios",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Portfolios
@mcp.tool(
    title="Create Portfolio",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_portfolio(data: _models.PortfolioRequest | None = Field(None, description="Request body containing the portfolio details, including the name and workspace to create the portfolio in.")) -> dict[str, Any] | ToolResult:
    """Creates a new portfolio in a specified workspace with a given name. Note that portfolios created via the API will not include default UI state (such as the 'Priority' custom field) to allow integrations to define their own initial configuration."""

    # Construct request model with validation
    try:
        _request = _models.CreatePortfolioRequest(
            body=_models.CreatePortfolioRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_portfolio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/portfolios"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_portfolio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_portfolio", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_portfolio",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Portfolios
@mcp.tool(
    title="Get Portfolio",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_portfolio(portfolio_gid: str = Field(..., description="The globally unique identifier of the portfolio to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single portfolio, including all associated metadata. Requires the portfolios:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetPortfolioRequest(
            path=_models.GetPortfolioRequestPath(portfolio_gid=portfolio_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_portfolio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/portfolios/{portfolio_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/portfolios/{portfolio_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_portfolio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_portfolio", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_portfolio",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Portfolios
@mcp.tool(
    title="Update Portfolio",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_portfolio(
    portfolio_gid: str = Field(..., description="The globally unique identifier of the portfolio to update."),
    data: _models.PortfolioUpdateRequest | None = Field(None, description="An object containing the portfolio fields to update; only the fields included will be modified, all unspecified fields retain their current values."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing portfolio by replacing only the fields provided in the request body, leaving all other fields unchanged. Returns the complete updated portfolio record."""

    # Construct request model with validation
    try:
        _request = _models.UpdatePortfolioRequest(
            path=_models.UpdatePortfolioRequestPath(portfolio_gid=portfolio_gid),
            body=_models.UpdatePortfolioRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_portfolio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/portfolios/{portfolio_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/portfolios/{portfolio_gid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_portfolio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_portfolio", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_portfolio",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Portfolios
@mcp.tool(
    title="Delete Portfolio",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_portfolio(portfolio_gid: str = Field(..., description="The globally unique identifier of the portfolio to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an existing portfolio by its unique identifier. Returns an empty data record upon successful deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeletePortfolioRequest(
            path=_models.DeletePortfolioRequestPath(portfolio_gid=portfolio_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_portfolio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/portfolios/{portfolio_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/portfolios/{portfolio_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_portfolio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_portfolio", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_portfolio",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Portfolios
@mcp.tool(
    title="List Portfolio Items",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_portfolio_items(
    portfolio_gid: str = Field(..., description="The globally unique identifier of the portfolio whose items you want to retrieve."),
    limit: int | None = Field(None, description="The number of items to return per page, allowing pagination through large portfolios. Must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of items within a specified portfolio in compact form. Useful for inspecting the contents of a portfolio, such as projects or other resources it contains."""

    # Construct request model with validation
    try:
        _request = _models.GetItemsForPortfolioRequest(
            path=_models.GetItemsForPortfolioRequestPath(portfolio_gid=portfolio_gid),
            query=_models.GetItemsForPortfolioRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_portfolio_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/portfolios/{portfolio_gid}/items", _request.path.model_dump(by_alias=True)) if _request.path else "/portfolios/{portfolio_gid}/items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_portfolio_items")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_portfolio_items", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_portfolio_items",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Portfolios
@mcp.tool(
    title="Add Portfolio Item",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_portfolio_item(
    portfolio_gid: str = Field(..., description="The globally unique identifier of the portfolio to which the item will be added."),
    item: str = Field(..., description="The globally unique identifier of the project or item to add to the portfolio."),
    insert_before: str | None = Field(None, description="The ID of an existing portfolio item before which the new item will be inserted. Cannot be used together with insert_after."),
    insert_after: str | None = Field(None, description="The ID of an existing portfolio item after which the new item will be inserted. Cannot be used together with insert_before."),
) -> dict[str, Any] | ToolResult:
    """Adds a project or item to a specified portfolio, optionally controlling its position relative to an existing item. Returns an empty data block on success."""

    # Construct request model with validation
    try:
        _request = _models.AddItemForPortfolioRequest(
            path=_models.AddItemForPortfolioRequestPath(portfolio_gid=portfolio_gid),
            body=_models.AddItemForPortfolioRequestBody(data=_models.AddItemForPortfolioRequestBodyData(item=item, insert_before=insert_before, insert_after=insert_after))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_portfolio_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/portfolios/{portfolio_gid}/addItem", _request.path.model_dump(by_alias=True)) if _request.path else "/portfolios/{portfolio_gid}/addItem"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_portfolio_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_portfolio_item", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_portfolio_item",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Portfolios
@mcp.tool(
    title="Remove Portfolio Item",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_portfolio_item(
    portfolio_gid: str = Field(..., description="The globally unique identifier of the portfolio from which the item will be removed."),
    item: str = Field(..., description="The globally unique identifier of the item to remove from the portfolio."),
) -> dict[str, Any] | ToolResult:
    """Removes a specific item from a portfolio, unlinking it from the portfolio's collection. Returns an empty data block upon success."""

    # Construct request model with validation
    try:
        _request = _models.RemoveItemForPortfolioRequest(
            path=_models.RemoveItemForPortfolioRequestPath(portfolio_gid=portfolio_gid),
            body=_models.RemoveItemForPortfolioRequestBody(data=_models.RemoveItemForPortfolioRequestBodyData(item=item))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_portfolio_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/portfolios/{portfolio_gid}/removeItem", _request.path.model_dump(by_alias=True)) if _request.path else "/portfolios/{portfolio_gid}/removeItem"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_portfolio_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_portfolio_item", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_portfolio_item",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Portfolios
@mcp.tool(
    title="Add Custom Field to Portfolio",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_custom_field_to_portfolio(
    portfolio_gid: str = Field(..., description="The globally unique identifier of the portfolio to which the custom field setting will be added."),
    custom_field: str | _models.CustomFieldCreateRequest = Field(..., description="The globally unique identifier (GID) of the custom field to associate with the portfolio."),
    is_important: bool | None = Field(None, description="When set to true, marks this custom field as important for the portfolio, causing it to be prominently displayed in list views of the portfolio's items."),
    insert_before: str | None = Field(None, description="The GID of an existing custom field setting on this portfolio before which the new custom field setting will be inserted to control ordering. Cannot be used together with insert_after."),
    insert_after: str | None = Field(None, description="The GID of an existing custom field setting on this portfolio after which the new custom field setting will be inserted to control ordering. Cannot be used together with insert_before."),
) -> dict[str, Any] | ToolResult:
    """Associates a custom field with a portfolio by creating a custom field setting, allowing the field to appear and be tracked within the portfolio. Optionally controls the display prominence and ordering of the field relative to other custom field settings on the portfolio."""

    # Construct request model with validation
    try:
        _request = _models.AddCustomFieldSettingForPortfolioRequest(
            path=_models.AddCustomFieldSettingForPortfolioRequestPath(portfolio_gid=portfolio_gid),
            body=_models.AddCustomFieldSettingForPortfolioRequestBody(data=_models.AddCustomFieldSettingForPortfolioRequestBodyData(custom_field=custom_field, is_important=is_important, insert_before=insert_before, insert_after=insert_after))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_custom_field_to_portfolio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/portfolios/{portfolio_gid}/addCustomFieldSetting", _request.path.model_dump(by_alias=True)) if _request.path else "/portfolios/{portfolio_gid}/addCustomFieldSetting"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_custom_field_to_portfolio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_custom_field_to_portfolio", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_custom_field_to_portfolio",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Portfolios
@mcp.tool(
    title="Remove Portfolio Custom Field",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_portfolio_custom_field(
    portfolio_gid: str = Field(..., description="The globally unique identifier of the portfolio from which the custom field setting will be removed."),
    custom_field: str = Field(..., description="The globally unique identifier of the custom field to detach from the portfolio."),
) -> dict[str, Any] | ToolResult:
    """Removes a custom field setting from a portfolio, detaching it so the field no longer appears or collects data for that portfolio. Requires portfolios:write scope."""

    # Construct request model with validation
    try:
        _request = _models.RemoveCustomFieldSettingForPortfolioRequest(
            path=_models.RemoveCustomFieldSettingForPortfolioRequestPath(portfolio_gid=portfolio_gid),
            body=_models.RemoveCustomFieldSettingForPortfolioRequestBody(data=_models.RemoveCustomFieldSettingForPortfolioRequestBodyData(custom_field=custom_field))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_portfolio_custom_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/portfolios/{portfolio_gid}/removeCustomFieldSetting", _request.path.model_dump(by_alias=True)) if _request.path else "/portfolios/{portfolio_gid}/removeCustomFieldSetting"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_portfolio_custom_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_portfolio_custom_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_portfolio_custom_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Portfolios
@mcp.tool(
    title="Add Portfolio Members",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_portfolio_members(
    portfolio_gid: str = Field(..., description="The globally unique identifier of the portfolio to which members will be added."),
    members: str = Field(..., description="A comma-separated list of user identifiers to add as portfolio members; each identifier can be the string 'me', a user's email address, or a user's globally unique identifier (gid). Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Adds one or more users as members of the specified portfolio, granting them access to view and collaborate on it. Returns the updated portfolio record."""

    # Construct request model with validation
    try:
        _request = _models.AddMembersForPortfolioRequest(
            path=_models.AddMembersForPortfolioRequestPath(portfolio_gid=portfolio_gid),
            body=_models.AddMembersForPortfolioRequestBody(data=_models.AddMembersForPortfolioRequestBodyData(members=members))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_portfolio_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/portfolios/{portfolio_gid}/addMembers", _request.path.model_dump(by_alias=True)) if _request.path else "/portfolios/{portfolio_gid}/addMembers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_portfolio_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_portfolio_members", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_portfolio_members",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Portfolios
@mcp.tool(
    title="Remove Portfolio Members",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_portfolio_members(
    portfolio_gid: str = Field(..., description="The globally unique identifier of the portfolio from which members will be removed."),
    members: str = Field(..., description="A comma-separated list of user identifiers to remove from the portfolio. Each identifier can be the string 'me' (current user), a user's email address, or a user's globally unique identifier (gid)."),
) -> dict[str, Any] | ToolResult:
    """Removes one or more users from the membership list of a specified portfolio. Returns the updated portfolio record reflecting the changes."""

    # Construct request model with validation
    try:
        _request = _models.RemoveMembersForPortfolioRequest(
            path=_models.RemoveMembersForPortfolioRequestPath(portfolio_gid=portfolio_gid),
            body=_models.RemoveMembersForPortfolioRequestBody(data=_models.RemoveMembersForPortfolioRequestBodyData(members=members))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_portfolio_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/portfolios/{portfolio_gid}/removeMembers", _request.path.model_dump(by_alias=True)) if _request.path else "/portfolios/{portfolio_gid}/removeMembers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_portfolio_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_portfolio_members", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_portfolio_members",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Portfolios
@mcp.tool(
    title="Duplicate Portfolio",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def duplicate_portfolio(
    portfolio_gid: str = Field(..., description="The globally unique identifier of the portfolio to duplicate."),
    name: str | None = Field(None, description="The display name to assign to the newly duplicated portfolio."),
    include: str | None = Field(None, description="A comma-separated list of optional elements to copy into the duplicate portfolio. Custom field settings and views are always included automatically. Valid values are: description, members, permissions, templates, rules, child_projects, child_portfolios."),
) -> dict[str, Any] | ToolResult:
    """Creates a duplicate of an existing portfolio and returns an asynchronous job that handles the duplication process. Custom field settings and views are always copied; additional elements such as members, rules, and child projects can be optionally included."""

    # Construct request model with validation
    try:
        _request = _models.DuplicatePortfolioRequest(
            path=_models.DuplicatePortfolioRequestPath(portfolio_gid=portfolio_gid),
            body=_models.DuplicatePortfolioRequestBody(data=_models.DuplicatePortfolioRequestBodyData(name=name, include=include) if any(v is not None for v in [name, include]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for duplicate_portfolio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/portfolios/{portfolio_gid}/duplicate", _request.path.model_dump(by_alias=True)) if _request.path else "/portfolios/{portfolio_gid}/duplicate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("duplicate_portfolio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("duplicate_portfolio", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="duplicate_portfolio",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Project briefs
@mcp.tool(
    title="Get Project Brief",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_project_brief(project_brief_gid: str = Field(..., description="The globally unique identifier for the project brief to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the full record for a specific project brief, including its title, description, and associated project details."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectBriefRequest(
            path=_models.GetProjectBriefRequestPath(project_brief_gid=project_brief_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_brief: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project_briefs/{project_brief_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/project_briefs/{project_brief_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_brief")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_brief", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_brief",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project briefs
@mcp.tool(
    title="Update Project Brief",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_project_brief(
    project_brief_gid: str = Field(..., description="The globally unique identifier of the project brief to update."),
    data: _models.ProjectBriefRequest | None = Field(None, description="An object containing the project brief fields to update; only the fields included will be modified, all omitted fields retain their current values."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing project brief by replacing only the fields provided in the request body, leaving all other fields unchanged. Returns the complete updated project brief record."""

    # Construct request model with validation
    try:
        _request = _models.UpdateProjectBriefRequest(
            path=_models.UpdateProjectBriefRequestPath(project_brief_gid=project_brief_gid),
            body=_models.UpdateProjectBriefRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project_brief: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project_briefs/{project_brief_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/project_briefs/{project_brief_gid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project_brief")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project_brief", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project_brief",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Project briefs
@mcp.tool(
    title="Delete Project Brief",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_project_brief(project_brief_gid: str = Field(..., description="The globally unique identifier of the project brief to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an existing project brief by its unique identifier. Returns an empty data record upon successful deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteProjectBriefRequest(
            path=_models.DeleteProjectBriefRequestPath(project_brief_gid=project_brief_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project_brief: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project_briefs/{project_brief_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/project_briefs/{project_brief_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_project_brief")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_project_brief", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_project_brief",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project briefs
@mcp.tool(
    title="Create Project Brief",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_project_brief(
    project_gid: str = Field(..., description="The globally unique identifier of the project for which the brief will be created."),
    data: _models.ProjectBriefRequest | None = Field(None, description="The request body containing the fields and values for the new project brief to be created."),
) -> dict[str, Any] | ToolResult:
    """Creates a new project brief for the specified project, returning the full record of the newly created brief. Project briefs provide a structured summary of project goals, context, and key information."""

    # Construct request model with validation
    try:
        _request = _models.CreateProjectBriefRequest(
            path=_models.CreateProjectBriefRequestPath(project_gid=project_gid),
            body=_models.CreateProjectBriefRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project_brief: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/project_briefs", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/project_briefs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_project_brief")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_project_brief", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_project_brief",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Project memberships
@mcp.tool(
    title="Get Project Membership",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_project_membership(project_membership_gid: str = Field(..., description="The unique identifier (GID) of the project membership record to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete details of a single project membership record, including the member's role and access level within the project."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectMembershipRequest(
            path=_models.GetProjectMembershipRequestPath(project_membership_gid=project_membership_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project_memberships/{project_membership_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/project_memberships/{project_membership_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_membership")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_membership", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_membership",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project memberships
@mcp.tool(
    title="List Project Memberships",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_project_memberships(
    project_gid: str = Field(..., description="The globally unique identifier of the project whose memberships you want to retrieve."),
    user: str | None = Field(None, description="Filter memberships to a specific user, identified by their GID, email address, or the keyword 'me' to refer to the authenticated user."),
    limit: int | None = Field(None, description="The number of membership records to return per page, between 1 and 100 inclusive.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all membership records for a specified project, showing which users belong to it. Optionally filter results to a single user and control pagination with a per-page limit."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectMembershipsForProjectRequest(
            path=_models.GetProjectMembershipsForProjectRequestPath(project_gid=project_gid),
            query=_models.GetProjectMembershipsForProjectRequestQuery(user=user, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/project_memberships", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/project_memberships"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_memberships")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_memberships", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_memberships",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project portfolio settings
@mcp.tool(
    title="Get Project Portfolio Setting",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_project_portfolio_setting(project_portfolio_setting_gid: str = Field(..., description="The globally unique identifier of the project portfolio setting to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single project portfolio setting. Requires the `project_portfolio_settings:read` scope."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectPortfolioSettingRequest(
            path=_models.GetProjectPortfolioSettingRequestPath(project_portfolio_setting_gid=project_portfolio_setting_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_portfolio_setting: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project_portfolio_settings/{project_portfolio_setting_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/project_portfolio_settings/{project_portfolio_setting_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_portfolio_setting")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_portfolio_setting", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_portfolio_setting",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project portfolio settings
@mcp.tool(
    title="Update Project Portfolio Setting",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_project_portfolio_setting(
    project_portfolio_setting_gid: str = Field(..., description="The globally unique identifier of the project portfolio setting to update."),
    is_access_control_inherited: bool | None = Field(None, description="Controls whether portfolio members automatically inherit access to the associated project; when true, portfolio membership grants project access."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing project portfolio setting by replacing only the fields provided in the request body, leaving all other fields unchanged. Returns the complete updated project portfolio setting record."""

    # Construct request model with validation
    try:
        _request = _models.UpdateProjectPortfolioSettingRequest(
            path=_models.UpdateProjectPortfolioSettingRequestPath(project_portfolio_setting_gid=project_portfolio_setting_gid),
            body=_models.UpdateProjectPortfolioSettingRequestBody(data=_models.UpdateProjectPortfolioSettingRequestBodyData(is_access_control_inherited=is_access_control_inherited) if any(v is not None for v in [is_access_control_inherited]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project_portfolio_setting: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project_portfolio_settings/{project_portfolio_setting_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/project_portfolio_settings/{project_portfolio_setting_gid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project_portfolio_setting")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project_portfolio_setting", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project_portfolio_setting",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Project portfolio settings
@mcp.tool(
    title="List Project Portfolio Settings",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_project_portfolio_settings(
    project_gid: str = Field(..., description="The globally unique identifier of the project whose portfolio settings you want to retrieve."),
    limit: int | None = Field(None, description="The number of portfolio settings to return per page. Must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all project portfolio settings associated with a specific project, returned as a compact representation. Requires the project_portfolio_settings:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectPortfolioSettingsForProjectRequest(
            path=_models.GetProjectPortfolioSettingsForProjectRequestPath(project_gid=project_gid),
            query=_models.GetProjectPortfolioSettingsForProjectRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_portfolio_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/project_portfolio_settings", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/project_portfolio_settings"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_portfolio_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_portfolio_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_portfolio_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project statuses
@mcp.tool(
    title="Get Project Status",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_project_status(project_status_gid: str = Field(..., description="The unique global identifier of the project status update to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single project status update by its unique identifier. Note: this endpoint is deprecated; new integrations should use the `/status_updates/{status_gid}` route instead."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectStatusRequest(
            path=_models.GetProjectStatusRequestPath(project_status_gid=project_status_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project_statuses/{project_status_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/project_statuses/{project_status_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project statuses
@mcp.tool(
    title="Delete Project Status",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_project_status(project_status_gid: str = Field(..., description="The unique identifier of the project status update to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific project status update by its unique identifier. Note: this endpoint is deprecated; new integrations should use the status updates route instead."""

    # Construct request model with validation
    try:
        _request = _models.DeleteProjectStatusRequest(
            path=_models.DeleteProjectStatusRequestPath(project_status_gid=project_status_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project_statuses/{project_status_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/project_statuses/{project_status_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_project_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_project_status", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_project_status",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project statuses
@mcp.tool(
    title="List Project Statuses",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_project_statuses(project_gid: str = Field(..., description="Globally unique identifier for the project.")) -> dict[str, Any] | ToolResult:
    """Retrieves all compact project status update records for a given project. Note: this endpoint is deprecated — new integrations should use the `/status_updates` route instead."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectStatusesForProjectRequest(
            path=_models.GetProjectStatusesForProjectRequestPath(project_gid=project_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_statuses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/project_statuses", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/project_statuses"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_statuses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_statuses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_statuses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project statuses
@mcp.tool(
    title="Create Project Status",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_project_status(
    project_gid: str = Field(..., description="The globally unique identifier of the project on which to create the status update."),
    data: _models.ProjectStatusBase | None = Field(None, description="The request body containing the status update fields, such as title, text, color, and other relevant status details."),
) -> dict[str, Any] | ToolResult:
    """Creates a new status update on a specified project and returns the full record of the newly created status. Note: this endpoint is deprecated; new integrations should use the `/status_updates` route instead."""

    # Construct request model with validation
    try:
        _request = _models.CreateProjectStatusForProjectRequest(
            path=_models.CreateProjectStatusForProjectRequestPath(project_gid=project_gid),
            body=_models.CreateProjectStatusForProjectRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/project_statuses", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/project_statuses"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_project_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_project_status", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_project_status",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Project templates
@mcp.tool(
    title="Get Project Template",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_project_template(project_template_gid: str = Field(..., description="The globally unique identifier of the project template to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single project template, including all its configuration and metadata. Requires the project_templates:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectTemplateRequest(
            path=_models.GetProjectTemplateRequestPath(project_template_gid=project_template_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project_templates/{project_template_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/project_templates/{project_template_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project templates
@mcp.tool(
    title="Delete Project Template",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_project_template(project_template_gid: str = Field(..., description="The globally unique identifier of the project template to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an existing project template by its unique identifier. This action is irreversible and returns an empty data record upon success."""

    # Construct request model with validation
    try:
        _request = _models.DeleteProjectTemplateRequest(
            path=_models.DeleteProjectTemplateRequestPath(project_template_gid=project_template_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project_templates/{project_template_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/project_templates/{project_template_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_project_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_project_template", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_project_template",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project templates
@mcp.tool(
    title="List Project Templates",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_project_templates(
    team: str | None = Field(None, description="The team to filter projects on."),
    workspace: str | None = Field(None, description="The workspace to filter results on."),
) -> dict[str, Any] | ToolResult:
    """Retrieves compact records for all project templates available in a given team or workspace. Requires the project_templates:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectTemplatesRequest(
            query=_models.GetProjectTemplatesRequestQuery(team=team, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/project_templates"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project templates
@mcp.tool(
    title="List Team Project Templates",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_team_project_templates(team_gid: str = Field(..., description="Globally unique identifier for the team.")) -> dict[str, Any] | ToolResult:
    """Retrieves all project templates belonging to a specified team, returning compact template records. Useful for discovering reusable project structures available within a team."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectTemplatesForTeamRequest(
            path=_models.GetProjectTemplatesForTeamRequestPath(team_gid=team_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_project_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_gid}/project_templates", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_gid}/project_templates"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_team_project_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_team_project_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_team_project_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project templates
@mcp.tool(
    title="Create Project from Template",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_project_from_template(
    project_template_gid: str = Field(..., description="The globally unique identifier of the project template to instantiate. Retrieve this value from the get project template endpoint."),
    name: str | None = Field(None, description="The display name to assign to the newly created project."),
    team: str | None = Field(None, description="The unique identifier of the team to assign to the new project. Applicable only when the workspace is an organization; defaults to the same team as the source project template if omitted."),
    is_strict: bool | None = Field(None, description="Controls how unfulfilled date variables are handled. When true, the request fails with an error if any date variable is missing a value; when false, missing date variables fall back to a default such as the current date."),
    requested_dates: list[_models.DateVariableRequest] | None = Field(None, description="An array of objects mapping each template date variable (identified by its GID from the template's requested_dates array) to a specific calendar date. Required when the project template contains date variables such as a task start date."),
    requested_roles: list[_models.RequestedRoleRequest] | None = Field(None, description="An array of objects mapping each template role to a specific user identifier, used to assign team members to predefined roles defined in the project template."),
) -> dict[str, Any] | ToolResult:
    """Instantiates a new project from an existing project template, returning an asynchronous job that handles the creation process. Supports mapping template date variables and roles to specific calendar dates and users at instantiation time."""

    # Construct request model with validation
    try:
        _request = _models.InstantiateProjectRequest(
            path=_models.InstantiateProjectRequestPath(project_template_gid=project_template_gid),
            body=_models.InstantiateProjectRequestBody(data=_models.InstantiateProjectRequestBodyData(name=name, team=team, is_strict=is_strict, requested_dates=requested_dates, requested_roles=requested_roles) if any(v is not None for v in [name, team, is_strict, requested_dates, requested_roles]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project_from_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project_templates/{project_template_gid}/instantiateProject", _request.path.model_dump(by_alias=True)) if _request.path else "/project_templates/{project_template_gid}/instantiateProject"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_project_from_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_project_from_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_project_from_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool(
    title="List Projects",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_projects(
    workspace: str | None = Field(None, description="The GID of the workspace or organization used to filter the returned projects. Providing this filter is recommended to prevent request timeouts on large domains."),
    archived: bool | None = Field(None, description="When provided, filters results to only include projects whose archived status matches this value. Set to true to return only archived projects, or false to return only active projects."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a filtered list of compact project records accessible to the authenticated user. Use the available filters to narrow results — filtering by workspace is strongly recommended to avoid timeouts on large domains."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectsRequest(
            query=_models.GetProjectsRequestQuery(workspace=workspace, archived=archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/projects"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool(
    title="Create Project",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_project(data: _models.ProjectRequest | None = Field(None, description="The request body containing project details such as name, workspace, team, and privacy settings required to create the project.")) -> dict[str, Any] | ToolResult:
    """Creates a new project within a specified workspace or organization, optionally associating it with a team. Returns the full record of the newly created project."""

    # Construct request model with validation
    try:
        _request = _models.CreateProjectRequest(
            body=_models.CreateProjectRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/projects"
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

# Tags: Projects
@mcp.tool(
    title="Get Project",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_project(project_gid: str = Field(..., description="The globally unique identifier (GID) of the project to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single project, including all available fields and metadata. Requires the `projects:read` scope; accessing the `team` field additionally requires `teams:read`."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectRequest(
            path=_models.GetProjectRequestPath(project_gid=project_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}"
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

# Tags: Projects
@mcp.tool(
    title="Update Project",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_project(
    project_gid: str = Field(..., description="The globally unique identifier (GID) of the project to update."),
    data: _models.ProjectUpdateRequest | None = Field(None, description="An object containing only the project fields you wish to update; omit any fields that should remain unchanged to avoid overwriting concurrent edits. Note: updating the `team` field is deprecated — use `POST /memberships` instead to share a project with a team."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing project by its unique identifier, applying only the fields provided in the request body while leaving unspecified fields unchanged. Returns the complete updated project record."""

    # Construct request model with validation
    try:
        _request = _models.UpdateProjectRequest(
            path=_models.UpdateProjectRequestPath(project_gid=project_gid),
            body=_models.UpdateProjectRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}"
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

# Tags: Projects
@mcp.tool(
    title="Delete Project",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_project(project_gid: str = Field(..., description="The globally unique identifier (GID) of the project to be deleted.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an existing project by its unique identifier. This action is irreversible and returns an empty data record upon success."""

    # Construct request model with validation
    try:
        _request = _models.DeleteProjectRequest(
            path=_models.DeleteProjectRequestPath(project_gid=project_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}"
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

# Tags: Projects
@mcp.tool(
    title="Duplicate Project",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def duplicate_project(
    project_gid: str = Field(..., description="The globally unique identifier (GID) of the source project to duplicate."),
    name: str | None = Field(None, description="The display name to assign to the newly created duplicate project."),
    team: str | None = Field(None, description="The GID of the team to assign the new project to. If omitted, the duplicate inherits the same team as the source project."),
    include: str | None = Field(None, description="A comma-separated list of optional elements to copy into the duplicate project. Tasks, project views, and rules are always included automatically. Explicitly specify any combination of optional fields: allocations, forms, members, notes, permissions, task_assignee, task_attachments, task_dates, task_dependencies, task_followers, task_notes, task_projects, task_subtasks, task_tags, task_templates, task_type_default."),
    should_skip_weekends: bool | None = Field(None, description="Required when shifting task dates: determines whether auto-shifted due and start dates should skip Saturday and Sunday when recalculating offsets."),
    due_on: str | None = Field(None, description="An ISO 8601 date (YYYY-MM-DD) to set as the last due date in the duplicated project; all other due dates are offset proportionally relative to this anchor date."),
    start_on: str | None = Field(None, description="An ISO 8601 date (YYYY-MM-DD) to set as the first start date in the duplicated project; all other start dates are offset proportionally relative to this anchor date."),
) -> dict[str, Any] | ToolResult:
    """Creates an asynchronous duplication job that copies an existing project into a new project, with configurable options for which elements (members, tasks, dates, etc.) to include. Returns a job object that can be polled to track duplication progress."""

    # Construct request model with validation
    try:
        _request = _models.DuplicateProjectRequest(
            path=_models.DuplicateProjectRequestPath(project_gid=project_gid),
            body=_models.DuplicateProjectRequestBody(data=_models.DuplicateProjectRequestBodyData(name=name, team=team, include=include,
                    schedule_dates=_models.DuplicateProjectRequestBodyDataScheduleDates(should_skip_weekends=should_skip_weekends, due_on=due_on, start_on=start_on) if any(v is not None for v in [should_skip_weekends, due_on, start_on]) else None) if any(v is not None for v in [name, team, include, should_skip_weekends, due_on, start_on]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for duplicate_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/duplicate", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/duplicate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("duplicate_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("duplicate_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="duplicate_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool(
    title="List Task Projects",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_task_projects(
    task_gid: str = Field(..., description="The unique identifier (GID) of the task whose associated projects you want to retrieve."),
    limit: int | None = Field(None, description="The number of project records to return per page. Must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all projects that contain a specified task. Returns a compact representation of each associated project."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectsForTaskRequest(
            path=_models.GetProjectsForTaskRequestPath(task_gid=task_gid),
            query=_models.GetProjectsForTaskRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_task_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/projects", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/projects"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_task_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_task_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_task_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool(
    title="Create Team Project",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_team_project(
    team_gid: str = Field(..., description="The globally unique identifier of the team with which the new project will be shared."),
    data: _models.ProjectRequest | None = Field(None, description="The project details and configuration to use when creating the new team project."),
) -> dict[str, Any] | ToolResult:
    """Creates a new project shared with the specified team. Returns the full record of the newly created project."""

    # Construct request model with validation
    try:
        _request = _models.CreateProjectForTeamRequest(
            path=_models.CreateProjectForTeamRequestPath(team_gid=team_gid),
            body=_models.CreateProjectForTeamRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_team_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_gid}/projects", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_gid}/projects"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_team_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_team_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_team_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool(
    title="List Workspace Projects",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_workspace_projects(
    workspace_gid: str = Field(..., description="Globally unique identifier for the workspace or organization."),
    archived: bool | None = Field(None, description="Filters results to only include projects matching the specified archived status. When set to true, only archived projects are returned; when false, only active projects are returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieves compact records for all projects within a specified workspace. Note: this endpoint may time out for large domains; use the memberships endpoint to fetch projects for a specific team."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectsForWorkspaceRequest(
            path=_models.GetProjectsForWorkspaceRequestPath(workspace_gid=workspace_gid),
            query=_models.GetProjectsForWorkspaceRequestQuery(archived=archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/projects", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/projects"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool(
    title="Create Project in Workspace",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_project_in_workspace(
    workspace_gid: str = Field(..., description="The globally unique identifier of the workspace or organization in which to create the project."),
    data: _models.ProjectRequest | None = Field(None, description="The project details to use when creating the new project, such as name, team, and other project attributes."),
) -> dict[str, Any] | ToolResult:
    """Creates a new project within the specified workspace or organization. If the workspace is an organization, a team must also be provided to share the project with."""

    # Construct request model with validation
    try:
        _request = _models.CreateProjectForWorkspaceRequest(
            path=_models.CreateProjectForWorkspaceRequestPath(workspace_gid=workspace_gid),
            body=_models.CreateProjectForWorkspaceRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project_in_workspace: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/projects", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/projects"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_project_in_workspace")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_project_in_workspace", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_project_in_workspace",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool(
    title="Search Projects in Workspace",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_projects(
    workspace_gid: str = Field(..., description="The globally unique identifier of the workspace or organization to search within."),
    text: str | None = Field(None, description="Full-text search string matched against project names to narrow results."),
    sort_by: Literal["due_date", "created_at", "completed_at", "modified_at"] | None = Field(None, description="Field by which to sort results; defaults to `modified_at` if not specified."),
    sort_ascending: bool | None = Field(None, description="When `true`, results are returned in ascending sort order; defaults to descending (`false`)."),
    completed: bool | None = Field(None, description="Filter projects by completion status: `true` returns only completed projects, `false` returns only incomplete projects."),
    teams_any: str | None = Field(None, alias="teams.any", description="Comma-separated list of team GIDs; returns projects belonging to any of the specified teams."),
    owner_any: str | None = Field(None, alias="owner.any", description="Comma-separated list of user GIDs or the string `me`; returns projects owned by any of the specified users."),
    members_any: str | None = Field(None, alias="members.any", description="Comma-separated list of user GIDs or the string `me`; returns projects where any of the specified users are members."),
    members_not: str | None = Field(None, alias="members.not", description="Comma-separated list of user GIDs or the string `me`; excludes projects where any of the specified users are members."),
    portfolios_any: str | None = Field(None, alias="portfolios.any", description="Comma-separated list of portfolio GIDs; returns projects that belong to any of the specified portfolios."),
    completed_on: str | None = Field(None, description="ISO 8601 date string to match projects completed on an exact date, or `null` to match projects with no completion date."),
    completed_on_before: str | None = Field(None, alias="completed_on.before", description="ISO 8601 date string; returns projects completed strictly before this date."),
    completed_on_after: str | None = Field(None, alias="completed_on.after", description="ISO 8601 date string; returns projects completed strictly after this date."),
    completed_at_before: str | None = Field(None, alias="completed_at.before", description="ISO 8601 datetime string; returns projects whose completion timestamp is strictly before this datetime."),
    completed_at_after: str | None = Field(None, alias="completed_at.after", description="ISO 8601 datetime string; returns projects whose completion timestamp is strictly after this datetime."),
    created_on: str | None = Field(None, description="ISO 8601 date string to match projects created on an exact date, or `null` to match projects with no creation date recorded."),
    created_on_before: str | None = Field(None, alias="created_on.before", description="ISO 8601 date string; returns projects created strictly before this date."),
    created_on_after: str | None = Field(None, alias="created_on.after", description="ISO 8601 date string; returns projects created strictly after this date."),
    created_at_before: str | None = Field(None, alias="created_at.before", description="ISO 8601 datetime string; returns projects whose creation timestamp is strictly before this datetime."),
    created_at_after: str | None = Field(None, alias="created_at.after", description="ISO 8601 datetime string; returns projects whose creation timestamp is strictly after this datetime."),
    due_on: str | None = Field(None, description="ISO 8601 date string to match projects with a due date on an exact date, or `null` to match projects with no due date."),
    due_on_before: str | None = Field(None, alias="due_on.before", description="ISO 8601 date string; returns projects with a due date strictly before this date."),
    due_on_after: str | None = Field(None, alias="due_on.after", description="ISO 8601 date string; returns projects with a due date strictly after this date."),
    due_at_before: str | None = Field(None, alias="due_at.before", description="ISO 8601 datetime string; returns projects whose due datetime is strictly before this datetime."),
    due_at_after: str | None = Field(None, alias="due_at.after", description="ISO 8601 datetime string; returns projects whose due datetime is strictly after this datetime."),
    start_on: str | None = Field(None, description="ISO 8601 date string to match projects with a start date on an exact date, or `null` to match projects with no start date."),
    start_on_before: str | None = Field(None, alias="start_on.before", description="ISO 8601 date string; returns projects with a start date strictly before this date."),
    start_on_after: str | None = Field(None, alias="start_on.after", description="ISO 8601 date string; returns projects with a start date strictly after this date."),
) -> dict[str, Any] | ToolResult:
    """Search and filter projects within a workspace using advanced criteria including text, ownership, membership, portfolio, dates, and custom fields. Results are eventually consistent and require a premium Asana account; use list_projects instead when immediate consistency after writes is needed."""

    # Construct request model with validation
    try:
        _request = _models.SearchProjectsForWorkspaceRequest(
            path=_models.SearchProjectsForWorkspaceRequestPath(workspace_gid=workspace_gid),
            query=_models.SearchProjectsForWorkspaceRequestQuery(text=text, sort_by=sort_by, sort_ascending=sort_ascending, completed=completed, teams_any=teams_any, owner_any=owner_any, members_any=members_any, members_not=members_not, portfolios_any=portfolios_any, completed_on=completed_on, completed_on_before=completed_on_before, completed_on_after=completed_on_after, completed_at_before=completed_at_before, completed_at_after=completed_at_after, created_on=created_on, created_on_before=created_on_before, created_on_after=created_on_after, created_at_before=created_at_before, created_at_after=created_at_after, due_on=due_on, due_on_before=due_on_before, due_on_after=due_on_after, due_at_before=due_at_before, due_at_after=due_at_after, start_on=start_on, start_on_before=start_on_before, start_on_after=start_on_after)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/projects/search", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/projects/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool(
    title="Add Custom Field to Project",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_custom_field_to_project(
    project_gid: str = Field(..., description="The unique identifier of the project to which the custom field will be added."),
    custom_field: str | _models.CustomFieldCreateRequest = Field(..., description="The globally unique identifier (GID) of the custom field to associate with the project."),
    is_important: bool | None = Field(None, description="When true, marks this custom field as important for the project, causing it to be prominently displayed in list views of the project's items."),
    insert_before: str | None = Field(None, description="The GID of an existing custom field setting on this project before which the new setting will be inserted to control ordering. Cannot be used together with insert_after."),
    insert_after: str | None = Field(None, description="The GID of an existing custom field setting on this project after which the new setting will be inserted to control ordering. Cannot be used together with insert_before."),
) -> dict[str, Any] | ToolResult:
    """Associates a custom field with a project by creating a custom field setting, allowing the field to appear and be used within that project. Optionally controls the field's display prominence and its position relative to other custom field settings."""

    # Construct request model with validation
    try:
        _request = _models.AddCustomFieldSettingForProjectRequest(
            path=_models.AddCustomFieldSettingForProjectRequestPath(project_gid=project_gid),
            body=_models.AddCustomFieldSettingForProjectRequestBody(data=_models.AddCustomFieldSettingForProjectRequestBodyData(custom_field=custom_field, is_important=is_important, insert_before=insert_before, insert_after=insert_after))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_custom_field_to_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/addCustomFieldSetting", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/addCustomFieldSetting"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_custom_field_to_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_custom_field_to_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_custom_field_to_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool(
    title="Remove Custom Field from Project",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_custom_field_from_project(
    project_gid: str = Field(..., description="The globally unique identifier of the project from which the custom field setting will be removed."),
    custom_field: str = Field(..., description="The globally unique identifier of the custom field to detach from the project."),
) -> dict[str, Any] | ToolResult:
    """Removes a custom field setting from a project, detaching it so the field no longer appears or collects data for that project. Requires projects:write scope."""

    # Construct request model with validation
    try:
        _request = _models.RemoveCustomFieldSettingForProjectRequest(
            path=_models.RemoveCustomFieldSettingForProjectRequestPath(project_gid=project_gid),
            body=_models.RemoveCustomFieldSettingForProjectRequestBody(data=_models.RemoveCustomFieldSettingForProjectRequestBodyData(custom_field=custom_field))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_custom_field_from_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/removeCustomFieldSetting", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/removeCustomFieldSetting"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_custom_field_from_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_custom_field_from_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_custom_field_from_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool(
    title="Get Project Task Counts",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_project_task_counts(project_gid: str = Field(..., description="The globally unique identifier of the project whose task counts you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves task count statistics for a specific project, including total, incomplete, and completed task counts (milestones are included). All fields are excluded by default and must be explicitly requested using opt_fields."""

    # Construct request model with validation
    try:
        _request = _models.GetTaskCountsForProjectRequest(
            path=_models.GetTaskCountsForProjectRequestPath(project_gid=project_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_task_counts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/task_counts", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/task_counts"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_task_counts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_task_counts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_task_counts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool(
    title="Add Project Members",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_project_members(
    project_gid: str = Field(..., description="The globally unique identifier of the project to which members will be added."),
    members: str = Field(..., description="A comma-separated list of user identifiers to add as project members. Each identifier can be the string 'me', a user's email address, or a user's globally unique identifier (gid)."),
) -> dict[str, Any] | ToolResult:
    """Adds one or more users as members of the specified project. Note that added members may also become followers depending on their personal notification settings."""

    # Construct request model with validation
    try:
        _request = _models.AddMembersForProjectRequest(
            path=_models.AddMembersForProjectRequestPath(project_gid=project_gid),
            body=_models.AddMembersForProjectRequestBody(data=_models.AddMembersForProjectRequestBodyData(members=members))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_project_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/addMembers", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/addMembers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_project_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_project_members", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_project_members",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool(
    title="Remove Project Members",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_project_members(
    project_gid: str = Field(..., description="The globally unique identifier of the project from which members will be removed."),
    members: str = Field(..., description="A comma-separated list of users to remove from the project, where each user can be identified by their GID, email address, or the literal string 'me' to reference the authenticated user."),
) -> dict[str, Any] | ToolResult:
    """Removes one or more users from the member list of a specified project. Returns the updated project record reflecting the new membership."""

    # Construct request model with validation
    try:
        _request = _models.RemoveMembersForProjectRequest(
            path=_models.RemoveMembersForProjectRequestPath(project_gid=project_gid),
            body=_models.RemoveMembersForProjectRequestBody(data=_models.RemoveMembersForProjectRequestBodyData(members=members))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_project_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/removeMembers", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/removeMembers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_project_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_project_members", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_project_members",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool(
    title="Add Project Followers",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_project_followers(
    project_gid: str = Field(..., description="The unique identifier of the project to which followers will be added."),
    followers: str = Field(..., description="A comma-separated list of user identifiers to add as followers; each identifier can be the string 'me', a user's email address, or a user's GID."),
) -> dict[str, Any] | ToolResult:
    """Adds one or more users as followers to a project, automatically making them members if they are not already. Followers receive 'tasks added' notifications for the project."""

    # Construct request model with validation
    try:
        _request = _models.AddFollowersForProjectRequest(
            path=_models.AddFollowersForProjectRequestPath(project_gid=project_gid),
            body=_models.AddFollowersForProjectRequestBody(data=_models.AddFollowersForProjectRequestBodyData(followers=followers))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_project_followers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/addFollowers", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/addFollowers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_project_followers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_project_followers", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_project_followers",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool(
    title="Remove Project Followers",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_project_followers(
    project_gid: str = Field(..., description="The globally unique identifier of the project from which followers will be removed."),
    followers: str = Field(..., description="A comma-separated list of users to remove as followers. Each user can be identified by their GID, email address, or the string 'me' to reference the authenticated user."),
) -> dict[str, Any] | ToolResult:
    """Removes one or more users from following a project without affecting their project membership status. Returns the updated project record."""

    # Construct request model with validation
    try:
        _request = _models.RemoveFollowersForProjectRequest(
            path=_models.RemoveFollowersForProjectRequestPath(project_gid=project_gid),
            body=_models.RemoveFollowersForProjectRequestBody(data=_models.RemoveFollowersForProjectRequestBodyData(followers=followers))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_project_followers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/removeFollowers", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/removeFollowers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_project_followers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_project_followers", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_project_followers",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool(
    title="Save Project as Template",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def save_project_as_template(
    project_gid: str = Field(..., description="The unique identifier of the project to convert into a template."),
    name: str = Field(..., description="The display name to assign to the newly created project template."),
    public: bool = Field(..., description="Controls whether the project template is publicly visible to all members of its team. Set to false to restrict visibility."),
    team: str | None = Field(None, description="The GID of the team to associate with the new project template. Required when the source project belongs to an organization; do not use alongside workspace."),
    workspace: str | None = Field(None, description="The GID of the workspace to associate with the new project template. Only applicable when the source project exists in a workspace rather than an organization; do not use alongside team."),
) -> dict[str, Any] | ToolResult:
    """Converts an existing project into a reusable project template by initiating an asynchronous job. Returns a job object that can be monitored for completion status."""

    # Construct request model with validation
    try:
        _request = _models.ProjectSaveAsTemplateRequest(
            path=_models.ProjectSaveAsTemplateRequestPath(project_gid=project_gid),
            body=_models.ProjectSaveAsTemplateRequestBody(data=_models.ProjectSaveAsTemplateRequestBodyData(name=name, team=team, workspace=workspace, public=public))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for save_project_as_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/saveAsTemplate", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/saveAsTemplate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("save_project_as_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("save_project_as_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="save_project_as_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Rates
@mcp.tool(
    title="List Rates",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_rates(
    parent: str | None = Field(None, description="The globally unique identifier of the parent project whose rates should be retrieved."),
    resource: str | None = Field(None, description="The globally unique identifier of a user or placeholder to filter rates down to a single specific resource."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of rate records associated with a parent project, optionally filtered to a specific user or placeholder resource. Modifying placeholder rates requires an Enterprise or Enterprise+ plan."""

    # Construct request model with validation
    try:
        _request = _models.GetRatesRequest(
            query=_models.GetRatesRequestQuery(parent=parent, resource=resource)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_rates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rates"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_rates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_rates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_rates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Rates
@mcp.tool(
    title="Create Rate",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_rate(
    parent: str = Field(..., description="The globally unique ID of the parent project to which this rate will be assigned."),
    resource: str = Field(..., description="The globally unique ID of the resource (user or placeholder) for whom the rate is being set."),
    rate: float = Field(..., description="The monetary value of the rate to assign to the resource, representing the billing amount per unit of time."),
) -> dict[str, Any] | ToolResult:
    """Creates a billing rate for a specific resource (user or placeholder) within a parent project, defining the monetary value charged for that resource's time."""

    # Construct request model with validation
    try:
        _request = _models.CreateRateRequest(
            body=_models.CreateRateRequestBody(data=_models.CreateRateRequestBodyData(parent=parent, resource=resource, rate=rate))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_rate: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/rates"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_rate")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_rate", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_rate",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Rates
@mcp.tool(
    title="Get Rate",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_rate(rate_gid: str = Field(..., description="The globally unique identifier for the rate to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single rate, including all associated pricing details and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetRateRequest(
            path=_models.GetRateRequestPath(rate_gid=rate_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_rate: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rates/{rate_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/rates/{rate_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_rate")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_rate", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_rate",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Rates
@mcp.tool(
    title="Update Rate",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_rate(
    rate_gid: str = Field(..., description="The globally unique identifier of the rate record to update."),
    rate: float | None = Field(None, description="The new monetary value to assign to the rate. Must be a valid numeric amount."),
) -> dict[str, Any] | ToolResult:
    """Updates the monetary value of an existing rate record. Only the rate field can be modified; all other fields remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.UpdateRateRequest(
            path=_models.UpdateRateRequestPath(rate_gid=rate_gid),
            body=_models.UpdateRateRequestBody(data=_models.UpdateRateRequestBodyData(rate=rate) if any(v is not None for v in [rate]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_rate: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rates/{rate_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/rates/{rate_gid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_rate")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_rate", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_rate",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Rates
@mcp.tool(
    title="Delete Rate",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_rate(rate_gid: str = Field(..., description="The globally unique identifier of the rate to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a rate by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRateRequest(
            path=_models.DeleteRateRequestPath(rate_gid=rate_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_rate: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/rates/{rate_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/rates/{rate_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_rate")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_rate", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_rate",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reactions
@mcp.tool(
    title="List Reactions",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_reactions(
    target: str = Field(..., description="The globally unique identifier (GID) of the object to fetch reactions from. Must reference a valid status update or story."),
    emoji_base: str = Field(..., description="Filters results to only include reactions that use this emoji base character. Only reactions matching this exact emoji will be returned."),
    limit: int | None = Field(None, description="The maximum number of reactions to return per page. Must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all reactions matching a specific emoji on a given object, such as a status update or story. Returns a paginated list of reactions filtered by the specified emoji base character."""

    # Construct request model with validation
    try:
        _request = _models.GetReactionsOnObjectRequest(
            query=_models.GetReactionsOnObjectRequestQuery(limit=limit, target=target, emoji_base=emoji_base)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_reactions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/reactions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_reactions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_reactions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_reactions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sections
@mcp.tool(
    title="Get Section",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_section(section_gid: str = Field(..., description="The globally unique identifier (GID) of the section to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete details for a single section by its unique identifier. Useful for inspecting section metadata such as its name, project association, and ordering."""

    # Construct request model with validation
    try:
        _request = _models.GetSectionRequest(
            path=_models.GetSectionRequestPath(section_gid=section_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_section: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sections/{section_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/sections/{section_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_section")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_section", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_section",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sections
@mcp.tool(
    title="Update Section",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_section(
    section_gid: str = Field(..., description="The globally unique identifier of the section to update."),
    name: str | None = Field(None, description="The new display name for the section. Must be a non-empty string."),
    insert_before: str | None = Field(None, description="The unique identifier of an existing section before which this section should be repositioned. Mutually exclusive with insert_after."),
    insert_after: str | None = Field(None, description="The unique identifier of an existing section after which this section should be repositioned. Mutually exclusive with insert_before."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing section's name or position within its project. Only the fields provided will be modified; all other section properties remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSectionRequest(
            path=_models.UpdateSectionRequestPath(section_gid=section_gid),
            body=_models.UpdateSectionRequestBody(data=_models.UpdateSectionRequestBodyData(name=name, insert_before=insert_before, insert_after=insert_after) if any(v is not None for v in [name, insert_before, insert_after]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_section: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sections/{section_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/sections/{section_gid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_section")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_section", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_section",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Sections
@mcp.tool(
    title="Delete Section",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_section(section_gid: str = Field(..., description="The globally unique identifier (GID) of the section to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an existing section by its unique identifier. The section must be empty and cannot be the last remaining section in the project."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSectionRequest(
            path=_models.DeleteSectionRequestPath(section_gid=section_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_section: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sections/{section_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/sections/{section_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_section")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_section", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_section",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sections
@mcp.tool(
    title="List Project Sections",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_project_sections(project_gid: str = Field(..., description="Globally unique identifier for the project.")) -> dict[str, Any] | ToolResult:
    """Retrieves all sections within a specified project, returning compact records for each. Useful for understanding a project's organizational structure before creating or moving tasks."""

    # Construct request model with validation
    try:
        _request = _models.GetSectionsForProjectRequest(
            path=_models.GetSectionsForProjectRequestPath(project_gid=project_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_sections: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/sections", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/sections"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_sections")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_sections", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_sections",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Sections
@mcp.tool(
    title="Create Section",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_section(
    project_gid: str = Field(..., description="The unique identifier of the project in which the new section will be created."),
    name: str | None = Field(None, description="The display name for the new section. Must be a non-empty string."),
    insert_before: str | None = Field(None, description="The GID of an existing section in this project before which the new section will be inserted. Mutually exclusive with insert_after; only one may be provided."),
    insert_after: str | None = Field(None, description="The GID of an existing section in this project after which the new section will be inserted. Mutually exclusive with insert_before; only one may be provided."),
) -> dict[str, Any] | ToolResult:
    """Creates a new section within a specified project to help organize tasks. Returns the full record of the newly created section."""

    # Construct request model with validation
    try:
        _request = _models.CreateSectionForProjectRequest(
            path=_models.CreateSectionForProjectRequestPath(project_gid=project_gid),
            body=_models.CreateSectionForProjectRequestBody(data=_models.CreateSectionForProjectRequestBodyData(name=name, insert_before=insert_before, insert_after=insert_after) if any(v is not None for v in [name, insert_before, insert_after]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_section: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/sections", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/sections"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_section")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_section", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_section",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Sections
@mcp.tool(
    title="Add Task to Section",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_task_to_section(
    section_gid: str = Field(..., description="The unique identifier of the section to which the task will be added."),
    task: str | None = Field(None, description="The unique identifier of the task to add to the section. Note: tasks with a resource_subtype of 'section' (separators) are not supported."),
    insert_before: str | None = Field(None, description="The unique identifier of an existing task in this section before which the added task should be inserted. Mutually exclusive with insert_after."),
    insert_after: str | None = Field(None, description="The unique identifier of an existing task in this section after which the added task should be inserted. Mutually exclusive with insert_before."),
) -> dict[str, Any] | ToolResult:
    """Moves a task into a specific section within a project, removing it from any other sections. The task is placed at the top of the section by default, or at a specific position using insert_before or insert_after."""

    # Construct request model with validation
    try:
        _request = _models.AddTaskForSectionRequest(
            path=_models.AddTaskForSectionRequestPath(section_gid=section_gid),
            body=_models.AddTaskForSectionRequestBody(data=_models.AddTaskForSectionRequestBodyData(task=task, insert_before=insert_before, insert_after=insert_after) if any(v is not None for v in [task, insert_before, insert_after]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_task_to_section: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sections/{section_gid}/addTask", _request.path.model_dump(by_alias=True)) if _request.path else "/sections/{section_gid}/addTask"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_task_to_section")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_task_to_section", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_task_to_section",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Sections
@mcp.tool(
    title="Reorder Section",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def reorder_section(
    project_gid: str = Field(..., description="The unique identifier of the project that contains the sections being reordered."),
    section: str | None = Field(None, description="The unique identifier of the section you want to move to a new position within the project."),
    before_section: str | None = Field(None, description="The unique identifier of the reference section that the moved section should be placed immediately before. Mutually exclusive with `after_section`."),
    after_section: str | None = Field(None, description="The unique identifier of the reference section that the moved section should be placed immediately after. Mutually exclusive with `before_section`."),
) -> dict[str, Any] | ToolResult:
    """Move a section to a new position within a project by placing it before or after another section. Exactly one of `before_section` or `after_section` must be provided; sections cannot be moved across projects."""

    # Construct request model with validation
    try:
        _request = _models.InsertSectionForProjectRequest(
            path=_models.InsertSectionForProjectRequestPath(project_gid=project_gid),
            body=_models.InsertSectionForProjectRequestBody(data=_models.InsertSectionForProjectRequestBodyData(section=section, before_section=before_section, after_section=after_section) if any(v is not None for v in [section, before_section, after_section]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reorder_section: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/sections/insert", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/sections/insert"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reorder_section")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reorder_section", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reorder_section",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Status updates
@mcp.tool(
    title="Get Status Update",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_status_update(status_update_gid: str = Field(..., description="The unique identifier of the status update to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single status update by its unique identifier. Useful for fetching the full details of a specific project or task status update."""

    # Construct request model with validation
    try:
        _request = _models.GetStatusRequest(
            path=_models.GetStatusRequestPath(status_update_gid=status_update_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_status_update: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/status_updates/{status_update_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/status_updates/{status_update_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_status_update")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_status_update", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_status_update",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Status updates
@mcp.tool(
    title="Delete Status Update",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_status_update(status_update_gid: str = Field(..., description="The unique identifier of the status update to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific status update by its unique identifier. Returns an empty data record upon successful deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteStatusRequest(
            path=_models.DeleteStatusRequestPath(status_update_gid=status_update_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_status_update: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/status_updates/{status_update_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/status_updates/{status_update_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_status_update")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_status_update", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_status_update",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Status updates
@mcp.tool(
    title="List Status Updates",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_status_updates(
    parent: str = Field(..., description="The globally unique identifier (GID) of the object whose status updates should be retrieved. Must reference a project, portfolio, or goal."),
    limit: int | None = Field(None, description="The maximum number of status update records to return per page, between 1 and 100.", ge=1, le=100),
    created_since: str | None = Field(None, description="Filters results to only include status updates created at or after this timestamp, specified in ISO 8601 date-time format."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of status updates for a specified project, portfolio, or goal. Results can be filtered by creation date to surface only recent updates."""

    # Construct request model with validation
    try:
        _request = _models.GetStatusesForObjectRequest(
            query=_models.GetStatusesForObjectRequestQuery(limit=limit, parent=parent, created_since=created_since)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_status_updates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/status_updates"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_status_updates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_status_updates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_status_updates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Status updates
@mcp.tool(
    title="Create Status Update",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_status_update(
    limit: int | None = Field(None, description="The number of results to return per page, must be between 1 and 100.", ge=1, le=100),
    data: _models.StatusUpdateRequest | None = Field(None, description="The payload containing the status update details to be created on the target object."),
) -> dict[str, Any] | ToolResult:
    """Creates a new status update on a specified object, such as a project or task. Returns the full record of the newly created status update."""

    # Construct request model with validation
    try:
        _request = _models.CreateStatusForObjectRequest(
            query=_models.CreateStatusForObjectRequestQuery(limit=limit),
            body=_models.CreateStatusForObjectRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_status_update: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/status_updates"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_status_update")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_status_update", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_status_update",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Stories
@mcp.tool(
    title="Get Story",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_story(story_gid: str = Field(..., description="The globally unique identifier (GID) of the story to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the full record for a single story by its unique identifier. Requires the stories:read scope, with additional attachments:read scope needed to access previews and attachments fields."""

    # Construct request model with validation
    try:
        _request = _models.GetStoryRequest(
            path=_models.GetStoryRequestPath(story_gid=story_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_story: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/stories/{story_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/stories/{story_gid}"
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

# Tags: Stories
@mcp.tool(
    title="Update Story",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_story(
    story_gid: str = Field(..., description="The globally unique identifier of the story to update."),
    text: str | None = Field(None, description="The plain text content of the comment story to set. Cannot be used together with html_text; only one may be specified per request."),
    is_pinned: bool | None = Field(None, description="Whether the story should be pinned to its parent resource. Pinning is supported only for comment and attachment story types."),
    sticker_name: Literal["green_checkmark", "people_dancing", "dancing_unicorn", "heart", "party_popper", "people_waving_flags", "splashing_narwhal", "trophy", "yeti_riding_unicorn", "celebrating_people", "determined_climbers", "phoenix_spreading_love"] | None = Field(None, description="The name of the sticker to display on the story. Set to null to remove an existing sticker. Must be one of the supported sticker identifiers."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing story on a task, allowing edits to comment text, pin status, or sticker. Only comment stories support text updates, and only comment and attachment stories can be pinned."""

    # Construct request model with validation
    try:
        _request = _models.UpdateStoryRequest(
            path=_models.UpdateStoryRequestPath(story_gid=story_gid),
            body=_models.UpdateStoryRequestBody(data=_models.UpdateStoryRequestBodyData(text=text, is_pinned=is_pinned, sticker_name=sticker_name) if any(v is not None for v in [text, is_pinned, sticker_name]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_story: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/stories/{story_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/stories/{story_gid}"
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

# Tags: Stories
@mcp.tool(
    title="Delete Story",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_story(story_gid: str = Field(..., description="The globally unique identifier of the story to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a story by its unique identifier. Only the story's creator can delete it; returns an empty data record on success."""

    # Construct request model with validation
    try:
        _request = _models.DeleteStoryRequest(
            path=_models.DeleteStoryRequestPath(story_gid=story_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_story: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/stories/{story_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/stories/{story_gid}"
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

# Tags: Stories
@mcp.tool(
    title="List Task Stories",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_task_stories(task_gid: str = Field(..., description="The task to operate on.")) -> dict[str, Any] | ToolResult:
    """Retrieves all stories (comments, activity, and system events) associated with a specific task. Returns compact story records in chronological order."""

    # Construct request model with validation
    try:
        _request = _models.GetStoriesForTaskRequest(
            path=_models.GetStoriesForTaskRequestPath(task_gid=task_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_task_stories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/stories", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/stories"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_task_stories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_task_stories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_task_stories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Stories
@mcp.tool(
    title="Add Task Comment",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_task_comment(
    task_gid: str = Field(..., description="The unique identifier (GID) of the task to which the story will be added."),
    text: str | None = Field(None, description="The plain text content of the comment to post on the task. Cannot be used together with html_text."),
    is_pinned: bool | None = Field(None, description="Whether the story should be pinned to the top of the task's story feed, making it prominently visible."),
    sticker_name: Literal["green_checkmark", "people_dancing", "dancing_unicorn", "heart", "party_popper", "people_waving_flags", "splashing_narwhal", "trophy", "yeti_riding_unicorn", "celebrating_people", "determined_climbers", "phoenix_spreading_love"] | None = Field(None, description="The name of the sticker to attach to this story. Omit or set to null if no sticker is desired."),
) -> dict[str, Any] | ToolResult:
    """Adds a comment story to a task, authored by the currently authenticated user and timestamped at the time of the request. Returns the full record of the newly created story."""

    # Construct request model with validation
    try:
        _request = _models.CreateStoryForTaskRequest(
            path=_models.CreateStoryForTaskRequestPath(task_gid=task_gid),
            body=_models.CreateStoryForTaskRequestBody(data=_models.CreateStoryForTaskRequestBodyData(text=text, is_pinned=is_pinned, sticker_name=sticker_name) if any(v is not None for v in [text, is_pinned, sticker_name]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_task_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/stories", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/stories"
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
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool(
    title="List Tags",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_tags(workspace: str | None = Field(None, description="The unique identifier of the workspace used to filter the returned tags to only those belonging to that workspace.")) -> dict[str, Any] | ToolResult:
    """Retrieves a list of compact tag records, optionally filtered by workspace. Requires the 'tags:read' scope."""

    # Construct request model with validation
    try:
        _request = _models.GetTagsRequest(
            query=_models.GetTagsRequestQuery(workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/tags"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

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
@mcp.tool(
    title="Create Tag",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_tag(data: _models.TagCreateRequest | None = Field(None, description="The request body containing the tag details, including the required workspace or organization identifier and any additional tag properties such as name and color.")) -> dict[str, Any] | ToolResult:
    """Creates a new tag within a specified workspace or organization, returning the full record of the newly created tag. Requires the tags:write scope, and the tag's workspace association is permanent once set."""

    # Construct request model with validation
    try:
        _request = _models.CreateTagRequest(
            body=_models.CreateTagRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/tags"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

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
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool(
    title="Get Tag",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_tag(tag_gid: str = Field(..., description="The globally unique identifier (GID) of the tag to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single tag, including its name, color, and associated metadata. Requires the tags:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetTagRequest(
            path=_models.GetTagRequestPath(tag_gid=tag_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tags/{tag_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/tags/{tag_gid}"
    _http_headers = {}

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
@mcp.tool(
    title="Update Tag",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_tag(
    tag_gid: str = Field(..., description="The globally unique identifier of the tag to update."),
    data: _models.TagBase | None = Field(None, description="An object containing the tag fields to update. Only include fields you wish to change to avoid overwriting concurrent updates from other users."),
) -> dict[str, Any] | ToolResult:
    """Updates the properties of an existing tag by its unique identifier. Only fields provided in the request body will be modified; unspecified fields remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTagRequest(
            path=_models.UpdateTagRequestPath(tag_gid=tag_gid),
            body=_models.UpdateTagRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tags/{tag_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/tags/{tag_gid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_tag", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_tag",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool(
    title="Delete Tag",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_tag(tag_gid: str = Field(..., description="The globally unique identifier of the tag to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an existing tag by its unique identifier. Returns an empty data record upon successful deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTagRequest(
            path=_models.DeleteTagRequestPath(tag_gid=tag_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tags/{tag_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/tags/{tag_gid}"
    _http_headers = {}

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
@mcp.tool(
    title="List Task Tags",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_task_tags(
    task_gid: str = Field(..., description="The unique identifier (GID) of the task whose tags you want to retrieve."),
    limit: int | None = Field(None, description="The number of tag results to return per page, must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all tags associated with a specific task, returned as compact tag representations. Requires the tags:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetTagsForTaskRequest(
            path=_models.GetTagsForTaskRequestPath(task_gid=task_gid),
            query=_models.GetTagsForTaskRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_task_tags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/tags"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_task_tags")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_task_tags", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_task_tags",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool(
    title="List Workspace Tags",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_workspace_tags(workspace_gid: str = Field(..., description="Globally unique identifier for the workspace or organization.")) -> dict[str, Any] | ToolResult:
    """Retrieves compact tag records for all tags within a specified workspace. Useful for discovering and filtering available tags to organize and categorize work items."""

    # Construct request model with validation
    try:
        _request = _models.GetTagsForWorkspaceRequest(
            path=_models.GetTagsForWorkspaceRequestPath(workspace_gid=workspace_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_tags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/tags"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_tags")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_tags", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_tags",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tags
@mcp.tool(
    title="Create Tag in Workspace",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_tag_in_workspace(
    workspace_gid: str = Field(..., description="The globally unique identifier of the workspace or organization in which to create the tag."),
    data: _models.TagCreateTagForWorkspaceRequest | None = Field(None, description="The tag details to create, including properties such as name, color, and any other supported tag fields."),
) -> dict[str, Any] | ToolResult:
    """Creates a new tag within a specified workspace or organization. Returns the full record of the newly created tag."""

    # Construct request model with validation
    try:
        _request = _models.CreateTagForWorkspaceRequest(
            path=_models.CreateTagForWorkspaceRequestPath(workspace_gid=workspace_gid),
            body=_models.CreateTagForWorkspaceRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_tag_in_workspace: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/tags"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_tag_in_workspace")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_tag_in_workspace", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_tag_in_workspace",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Task templates
@mcp.tool(
    title="List Task Templates",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_task_templates(project: str | None = Field(None, description="The unique identifier of the project whose task templates should be returned. This filter is required to scope results to a specific project.")) -> dict[str, Any] | ToolResult:
    """Retrieves a list of compact task template records for a specified project. A project must be provided to filter and return the relevant task templates."""

    # Construct request model with validation
    try:
        _request = _models.GetTaskTemplatesRequest(
            query=_models.GetTaskTemplatesRequestQuery(project=project)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_task_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/task_templates"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

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

# Tags: Task templates
@mcp.tool(
    title="Get Task Template",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_task_template(task_template_gid: str = Field(..., description="The globally unique identifier (GID) of the task template to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single task template, including all its fields and configuration. Requires the task_templates:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetTaskTemplateRequest(
            path=_models.GetTaskTemplateRequestPath(task_template_gid=task_template_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/task_templates/{task_template_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/task_templates/{task_template_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_task_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_task_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_task_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Task templates
@mcp.tool(
    title="Delete Task Template",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_task_template(task_template_gid: str = Field(..., description="The globally unique identifier of the task template to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an existing task template by its unique identifier. This action is irreversible and returns an empty data record upon success."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTaskTemplateRequest(
            path=_models.DeleteTaskTemplateRequestPath(task_template_gid=task_template_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_task_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/task_templates/{task_template_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/task_templates/{task_template_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_task_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_task_template", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_task_template",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Task templates
@mcp.tool(
    title="Instantiate Task from Template",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def instantiate_task_from_template(
    task_template_gid: str = Field(..., description="The globally unique identifier of the task template to instantiate a new task from."),
    name: str | None = Field(None, description="The display name for the newly created task. If omitted, the task inherits the name defined in the source task template."),
) -> dict[str, Any] | ToolResult:
    """Creates a new task by instantiating a task template, returning an asynchronous job that handles the task creation process. Use this to spin up pre-configured tasks from reusable templates."""

    # Construct request model with validation
    try:
        _request = _models.InstantiateTaskRequest(
            path=_models.InstantiateTaskRequestPath(task_template_gid=task_template_gid),
            body=_models.InstantiateTaskRequestBody(data=_models.InstantiateTaskRequestBodyData(name=name) if any(v is not None for v in [name]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for instantiate_task_from_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/task_templates/{task_template_gid}/instantiateTask", _request.path.model_dump(by_alias=True)) if _request.path else "/task_templates/{task_template_gid}/instantiateTask"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("instantiate_task_from_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("instantiate_task_from_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="instantiate_task_from_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="List Tasks",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_tasks(
    assignee: str | None = Field(None, description="Filter tasks by the GID of the assigned user. To find unassigned tasks, use assignee.any = null. Requires workspace to also be specified."),
    project: str | None = Field(None, description="Filter tasks belonging to the specified project GID."),
    section: str | None = Field(None, description="Filter tasks belonging to the specified section GID within a project."),
    workspace: str | None = Field(None, description="Filter tasks within the specified workspace GID. Requires assignee to also be specified."),
    completed_since: str | None = Field(None, description="Return only tasks that are incomplete or were completed on or after this timestamp, provided in ISO 8601 date-time format."),
    modified_since: str | None = Field(None, description="Return only tasks modified on or after this timestamp in ISO 8601 date-time format. Modifications include property changes and association updates such as assigning, renaming, completing, or adding stories."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a filtered list of compact task records based on assignee, project, section, workspace, or time-based criteria. At least one of project, tag, or both assignee and workspace must be specified."""

    # Construct request model with validation
    try:
        _request = _models.GetTasksRequest(
            query=_models.GetTasksRequestQuery(assignee=assignee, project=project, section=section, workspace=workspace, completed_since=completed_since, modified_since=modified_since)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/tasks"
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
@mcp.tool(
    title="Create Task",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_task(data: _models.TaskRequest | None = Field(None, description="The task fields to set on the new task, such as name, workspace, projects, assignee, due date, and other task attributes. A workspace must be determinable either directly or via an associated project or parent task.")) -> dict[str, Any] | ToolResult:
    """Creates a new task in a specified workspace, project, or as a child of a parent task. Any fields not explicitly provided will be assigned their default values."""

    # Construct request model with validation
    try:
        _request = _models.CreateTaskRequest(
            body=_models.CreateTaskRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/tasks"
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
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="Get Task",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_task(task_gid: str = Field(..., description="The unique global identifier (GID) of the task to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single task, including all fields and metadata. Note that accessing memberships requires projects:read and project_sections:read scopes, and actual_time_minutes requires time_tracking_entries:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetTaskRequest(
            path=_models.GetTaskRequestPath(task_gid=task_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}"
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
@mcp.tool(
    title="Update Task",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_task(
    task_gid: str = Field(..., description="The unique identifier (GID) of the task to update."),
    data: _models.TaskRequest | None = Field(None, description="An object containing only the task fields you wish to update; omitted fields will retain their current values."),
) -> dict[str, Any] | ToolResult:
    """Updates specific fields of an existing task by its unique identifier. Only the fields provided in the request body will be modified; all other fields remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTaskRequest(
            path=_models.UpdateTaskRequestPath(task_gid=task_gid),
            body=_models.UpdateTaskRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}"
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

# Tags: Tasks
@mcp.tool(
    title="Delete Task",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_task(task_gid: str = Field(..., description="The unique global identifier (GID) of the task to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific task by moving it to the requesting user's trash, where it can be recovered within 30 days before being completely removed from the system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTaskRequest(
            path=_models.DeleteTaskRequestPath(task_gid=task_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}"
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

# Tags: Tasks
@mcp.tool(
    title="Duplicate Task",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def duplicate_task(
    task_gid: str = Field(..., description="The unique identifier (GID) of the task to duplicate."),
    name: str | None = Field(None, description="The name to assign to the newly duplicated task."),
    include: str | None = Field(None, description="A comma-separated list of fields to copy from the original task to the duplicate. Supported fields include: assignee, attachments, dates, dependencies, followers, notes, parent, projects, subtasks, and tags."),
) -> dict[str, Any] | ToolResult:
    """Duplicates an existing task and returns an asynchronous job that handles the duplication process. You can specify a new name and choose which fields to carry over to the duplicated task."""

    # Construct request model with validation
    try:
        _request = _models.DuplicateTaskRequest(
            path=_models.DuplicateTaskRequestPath(task_gid=task_gid),
            body=_models.DuplicateTaskRequestBody(data=_models.DuplicateTaskRequestBodyData(name=name, include=include) if any(v is not None for v in [name, include]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for duplicate_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/duplicate", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/duplicate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("duplicate_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("duplicate_task", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="duplicate_task",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="List Project Tasks",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_project_tasks(
    project_gid: str = Field(..., description="The globally unique identifier (GID) of the project whose tasks you want to retrieve."),
    completed_since: str | None = Field(None, description="Filters results to include only incomplete tasks or tasks completed after this point in time. Accepts an ISO 8601 date-time string or the keyword 'now' to filter relative to the current moment."),
    limit: int | None = Field(None, description="The number of task records to return per page. Must be between 1 and 100 inclusive.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all tasks within a specified project, ordered by their priority within that project. Tasks may belong to multiple projects simultaneously."""

    # Construct request model with validation
    try:
        _request = _models.GetTasksForProjectRequest(
            path=_models.GetTasksForProjectRequestPath(project_gid=project_gid),
            query=_models.GetTasksForProjectRequestQuery(completed_since=completed_since, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_gid}/tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_gid}/tasks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_tasks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_tasks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="List Section Tasks",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_section_tasks(
    section_gid: str = Field(..., description="The globally unique identifier of the section whose tasks you want to retrieve."),
    limit: int | None = Field(None, description="Number of task records to return per page. Must be between 1 and 100.", ge=1, le=100),
    completed_since: str | None = Field(None, description="Filters results to include only incomplete tasks or tasks completed after the specified time. Accepts an ISO 8601 date-time string or the keyword 'now'."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all tasks within a specified board section, returning compact task records. Only applicable to board view sections."""

    # Construct request model with validation
    try:
        _request = _models.GetTasksForSectionRequest(
            path=_models.GetTasksForSectionRequestPath(section_gid=section_gid),
            query=_models.GetTasksForSectionRequestQuery(limit=limit, completed_since=completed_since)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_section_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sections/{section_gid}/tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/sections/{section_gid}/tasks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_section_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_section_tasks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_section_tasks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="List Tasks by Tag",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_tasks_by_tag(
    tag_gid: str = Field(..., description="The globally unique identifier of the tag whose associated tasks you want to retrieve."),
    limit: int | None = Field(None, description="The number of task records to return per page, must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all tasks associated with a specific tag, returning compact task records. A task may belong to multiple tags simultaneously."""

    # Construct request model with validation
    try:
        _request = _models.GetTasksForTagRequest(
            path=_models.GetTasksForTagRequestPath(tag_gid=tag_gid),
            query=_models.GetTasksForTagRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tasks_by_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tags/{tag_gid}/tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/tags/{tag_gid}/tasks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tasks_by_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tasks_by_tag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tasks_by_tag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="List User Task List Tasks",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_user_task_list_tasks(
    user_task_list_gid: str = Field(..., description="The globally unique identifier for the user task list whose tasks you want to retrieve."),
    completed_since: str | None = Field(None, description="Filters results to only include tasks that are incomplete or were completed on or after this point in time. Accepts an ISO 8601 date-time string or the keyword 'now' to return only currently incomplete tasks."),
    limit: int | None = Field(None, description="The number of task objects to return per page, between 1 and 100 inclusive.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves the compact list of tasks from a user's My Tasks list, including both complete and incomplete tasks by default. Use the completed_since filter to narrow results, such as returning only incomplete tasks by passing 'now'."""

    # Construct request model with validation
    try:
        _request = _models.GetTasksForUserTaskListRequest(
            path=_models.GetTasksForUserTaskListRequestPath(user_task_list_gid=user_task_list_gid),
            query=_models.GetTasksForUserTaskListRequestQuery(completed_since=completed_since, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_task_list_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user_task_lists/{user_task_list_gid}/tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/user_task_lists/{user_task_list_gid}/tasks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_task_list_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_task_list_tasks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_task_list_tasks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="List Subtasks",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_subtasks(task_gid: str = Field(..., description="The task to operate on.")) -> dict[str, Any] | ToolResult:
    """Retrieves a compact list of all subtasks belonging to a specified task. Useful for exploring task hierarchies and understanding nested work breakdowns."""

    # Construct request model with validation
    try:
        _request = _models.GetSubtasksForTaskRequest(
            path=_models.GetSubtasksForTaskRequestPath(task_gid=task_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_subtasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/subtasks", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/subtasks"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_subtasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_subtasks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_subtasks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="Create Subtask",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_subtask(
    task_gid: str = Field(..., description="The unique identifier (GID) of the parent task to which the new subtask will be added."),
    data: _models.TaskRequest | None = Field(None, description="The subtask details to create, including fields such as name, assignee, due date, and notes."),
) -> dict[str, Any] | ToolResult:
    """Creates a new subtask under the specified parent task and returns the full record of the newly created subtask."""

    # Construct request model with validation
    try:
        _request = _models.CreateSubtaskForTaskRequest(
            path=_models.CreateSubtaskForTaskRequestPath(task_gid=task_gid),
            body=_models.CreateSubtaskForTaskRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_subtask: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/subtasks", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/subtasks"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_subtask")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_subtask", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_subtask",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="Set Task Parent",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def set_task_parent(
    task_gid: str = Field(..., description="The unique identifier of the task whose parent relationship will be updated."),
    parent: str = Field(..., description="The unique identifier of the task to set as the new parent, or null to remove the existing parent and make the task top-level."),
    insert_after: str | None = Field(None, description="The unique identifier of an existing subtask of the new parent after which this task should be inserted, or null to insert at the beginning of the subtask list. Cannot be used together with insert_before."),
    insert_before: str | None = Field(None, description="The unique identifier of an existing subtask of the new parent before which this task should be inserted, or null to insert at the end of the subtask list. Cannot be used together with insert_after."),
) -> dict[str, Any] | ToolResult:
    """Sets or removes the parent of a task, making it a subtask of another task or a top-level task when parent is null. Optionally controls the position of the task within the parent's subtask list."""

    # Construct request model with validation
    try:
        _request = _models.SetParentForTaskRequest(
            path=_models.SetParentForTaskRequestPath(task_gid=task_gid),
            body=_models.SetParentForTaskRequestBody(data=_models.SetParentForTaskRequestBodyData(parent=parent, insert_after=insert_after, insert_before=insert_before))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_task_parent: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/setParent", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/setParent"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_task_parent")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_task_parent", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_task_parent",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="List Task Dependencies",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_task_dependencies(
    task_gid: str = Field(..., description="The unique identifier (GID) of the task whose dependencies you want to retrieve."),
    limit: int | None = Field(None, description="The number of dependency records to return per page. Must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all tasks that a given task depends on, returned as compact representations. Useful for understanding task prerequisites and dependency chains within a project."""

    # Construct request model with validation
    try:
        _request = _models.GetDependenciesForTaskRequest(
            path=_models.GetDependenciesForTaskRequestPath(task_gid=task_gid),
            query=_models.GetDependenciesForTaskRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_task_dependencies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/dependencies", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/dependencies"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_task_dependencies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_task_dependencies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_task_dependencies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="Add Task Dependencies",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_task_dependencies(
    task_gid: str = Field(..., description="The unique identifier (GID) of the task to which dependencies will be added."),
    dependencies: list[str] | None = Field(None, description="An array of task GIDs to mark as dependencies of the specified task; order is not significant and each item should be a valid task GID string."),
) -> dict[str, Any] | ToolResult:
    """Marks one or more tasks as dependencies of a specified task, establishing that the target task depends on their completion. A task may have at most 30 dependents and dependencies combined."""

    # Construct request model with validation
    try:
        _request = _models.AddDependenciesForTaskRequest(
            path=_models.AddDependenciesForTaskRequestPath(task_gid=task_gid),
            body=_models.AddDependenciesForTaskRequestBody(data=_models.AddDependenciesForTaskRequestBodyData(dependencies=dependencies) if any(v is not None for v in [dependencies]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_task_dependencies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/addDependencies", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/addDependencies"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_task_dependencies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_task_dependencies", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_task_dependencies",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="Remove Task Dependencies",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_task_dependencies(
    task_gid: str = Field(..., description="The unique identifier (GID) of the task from which dependencies will be removed."),
    dependencies: list[str] | None = Field(None, description="An array of task GIDs representing the dependency tasks to unlink from the specified task. Order is not significant; each item should be a valid task GID string."),
) -> dict[str, Any] | ToolResult:
    """Unlinks one or more dependency tasks from a specified task, removing the requirement that those tasks must be completed before this task can proceed."""

    # Construct request model with validation
    try:
        _request = _models.RemoveDependenciesForTaskRequest(
            path=_models.RemoveDependenciesForTaskRequestPath(task_gid=task_gid),
            body=_models.RemoveDependenciesForTaskRequestBody(data=_models.RemoveDependenciesForTaskRequestBodyData(dependencies=dependencies) if any(v is not None for v in [dependencies]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_task_dependencies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/removeDependencies", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/removeDependencies"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_task_dependencies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_task_dependencies", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_task_dependencies",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="List Task Dependents",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_task_dependents(
    task_gid: str = Field(..., description="The unique identifier (GID) of the task whose dependents you want to retrieve."),
    limit: int | None = Field(None, description="The number of dependent task records to return per page. Must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves compact representations of all tasks that depend on a specified task. Useful for understanding downstream impact when changes are made to a task."""

    # Construct request model with validation
    try:
        _request = _models.GetDependentsForTaskRequest(
            path=_models.GetDependentsForTaskRequestPath(task_gid=task_gid),
            query=_models.GetDependentsForTaskRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_task_dependents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/dependents", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/dependents"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_task_dependents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_task_dependents", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_task_dependents",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="Add Task Dependents",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_task_dependents(
    task_gid: str = Field(..., description="The unique identifier of the task that will become the dependency (i.e., the task that others will depend on)."),
    dependents: list[str] | None = Field(None, description="An array of task GIDs to mark as dependents of the specified task. Order is not significant; each item should be a valid task GID string."),
) -> dict[str, Any] | ToolResult:
    """Marks one or more tasks as dependents of the specified task, meaning those tasks depend on this task being completed. A task can have at most 30 dependents and dependencies combined."""

    # Construct request model with validation
    try:
        _request = _models.AddDependentsForTaskRequest(
            path=_models.AddDependentsForTaskRequestPath(task_gid=task_gid),
            body=_models.AddDependentsForTaskRequestBody(data=_models.AddDependentsForTaskRequestBodyData(dependents=dependents) if any(v is not None for v in [dependents]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_task_dependents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/addDependents", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/addDependents"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_task_dependents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_task_dependents", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_task_dependents",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="Remove Task Dependents",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_task_dependents(
    task_gid: str = Field(..., description="The unique identifier of the task from which dependents will be unlinked."),
    dependents: list[str] | None = Field(None, description="An array of task GIDs representing the dependent tasks to unlink from the specified task. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Unlinks one or more dependent tasks from a specified task, removing the dependency relationship. Requires tasks:write scope."""

    # Construct request model with validation
    try:
        _request = _models.RemoveDependentsForTaskRequest(
            path=_models.RemoveDependentsForTaskRequestPath(task_gid=task_gid),
            body=_models.RemoveDependentsForTaskRequestBody(data=_models.RemoveDependentsForTaskRequestBodyData(dependents=dependents) if any(v is not None for v in [dependents]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_task_dependents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/removeDependents", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/removeDependents"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_task_dependents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_task_dependents", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_task_dependents",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="Add Task to Project",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_task_to_project(
    task_gid: str = Field(..., description="The unique identifier of the task to add to the project."),
    project: str = Field(..., description="The unique identifier of the project to add the task to."),
    insert_after: str | None = Field(None, description="The GID of an existing task in the project after which this task should be inserted. Pass null to place the task at the beginning of the list or, when combined with `section`, at the beginning of that section. Cannot be used together with `insert_before`."),
    insert_before: str | None = Field(None, description="The GID of an existing task in the project before which this task should be inserted. Pass null to place the task at the end of the list or, when combined with `section`, at the end of that section. Cannot be used together with `insert_after`."),
    section: str | None = Field(None, description="The GID of a section within the project into which the task should be placed. By default the task is added to the end of the section; combine with `insert_after: null` to place at the beginning, `insert_before: null` to place at the end, or a non-null `insert_before`/`insert_after` task GID to position relative to a specific task within the section."),
) -> dict[str, Any] | ToolResult:
    """Adds a task to a specified project, optionally positioning it relative to another task or within a section. Can also be used to reorder a task already in the project; a task may belong to at most 20 projects."""

    # Construct request model with validation
    try:
        _request = _models.AddProjectForTaskRequest(
            path=_models.AddProjectForTaskRequestPath(task_gid=task_gid),
            body=_models.AddProjectForTaskRequestBody(data=_models.AddProjectForTaskRequestBodyData(project=project, insert_after=insert_after, insert_before=insert_before, section=section))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_task_to_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/addProject", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/addProject"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_task_to_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_task_to_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_task_to_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="Remove Task from Project",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_task_from_project(
    task_gid: str = Field(..., description="The unique identifier of the task to be removed from the project."),
    project: str = Field(..., description="The unique identifier of the project from which the task should be removed."),
) -> dict[str, Any] | ToolResult:
    """Removes a task from a specified project without deleting the task itself. The task remains in the system and can still belong to other projects."""

    # Construct request model with validation
    try:
        _request = _models.RemoveProjectForTaskRequest(
            path=_models.RemoveProjectForTaskRequestPath(task_gid=task_gid),
            body=_models.RemoveProjectForTaskRequestBody(data=_models.RemoveProjectForTaskRequestBodyData(project=project))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_task_from_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/removeProject", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/removeProject"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_task_from_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_task_from_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_task_from_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="Add Tag to Task",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_task_tag(
    task_gid: str = Field(..., description="The unique global identifier (GID) of the task to which the tag will be added."),
    tag: str = Field(..., description="The unique global identifier (GID) of the tag to attach to the task."),
) -> dict[str, Any] | ToolResult:
    """Adds an existing tag to a specified task, associating them for organization and filtering purposes. Returns an empty data block on success."""

    # Construct request model with validation
    try:
        _request = _models.AddTagForTaskRequest(
            path=_models.AddTagForTaskRequestPath(task_gid=task_gid),
            body=_models.AddTagForTaskRequestBody(data=_models.AddTagForTaskRequestBodyData(tag=tag))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_task_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/addTag", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/addTag"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_task_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_task_tag", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_task_tag",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="Remove Task Tag",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_task_tag(
    task_gid: str = Field(..., description="The unique global identifier (GID) of the task from which the tag will be removed."),
    tag: str = Field(..., description="The unique global identifier (GID) of the tag to remove from the task."),
) -> dict[str, Any] | ToolResult:
    """Removes a tag from a specified task, dissociating the tag without deleting it. Returns an empty data block on success."""

    # Construct request model with validation
    try:
        _request = _models.RemoveTagForTaskRequest(
            path=_models.RemoveTagForTaskRequestPath(task_gid=task_gid),
            body=_models.RemoveTagForTaskRequestBody(data=_models.RemoveTagForTaskRequestBodyData(tag=tag))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_task_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/removeTag", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/removeTag"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_task_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_task_tag", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_task_tag",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="Add Task Followers",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_task_followers(
    task_gid: str = Field(..., description="The unique identifier (GID) of the task to which followers will be added."),
    followers: list[str] = Field(..., description="A list of users to add as followers, where each entry can be the string 'me', a user's email address, or a user's GID. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Adds one or more followers to a specified task, associating them with it for updates and visibility. Returns the complete updated task record upon success."""

    # Construct request model with validation
    try:
        _request = _models.AddFollowersForTaskRequest(
            path=_models.AddFollowersForTaskRequestPath(task_gid=task_gid),
            body=_models.AddFollowersForTaskRequestBody(data=_models.AddFollowersForTaskRequestBodyData(followers=followers))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_task_followers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/addFollowers", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/addFollowers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_task_followers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_task_followers", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_task_followers",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="Remove Task Followers",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_task_followers(
    task_gid: str = Field(..., description="The unique identifier (GID) of the task from which followers will be removed."),
    followers: list[str] = Field(..., description="A list of users to remove as followers from the task. Each item can be the string 'me', a user's email address, or a user's GID. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Removes one or more specified followers from a task, leaving all other followers unaffected. Returns the complete, updated task record after the removal."""

    # Construct request model with validation
    try:
        _request = _models.RemoveFollowerForTaskRequest(
            path=_models.RemoveFollowerForTaskRequestPath(task_gid=task_gid),
            body=_models.RemoveFollowerForTaskRequestBody(data=_models.RemoveFollowerForTaskRequestBodyData(followers=followers))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_task_followers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/removeFollowers", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/removeFollowers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_task_followers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_task_followers", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_task_followers",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="Get Task by Custom ID",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_task_by_custom_id(
    workspace_gid: str = Field(..., description="The globally unique identifier for the workspace or organization in which to search for the task."),
    custom_id: str = Field(..., description="The custom ID shortcode assigned to the task, typically formatted as a prefix followed by a number (e.g., a project code and sequence number)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a task using its human-readable custom ID shortcode within a specified workspace. Useful when referencing tasks by their display identifiers rather than internal GIDs."""

    # Construct request model with validation
    try:
        _request = _models.GetTaskForCustomIdRequest(
            path=_models.GetTaskForCustomIdRequestPath(workspace_gid=workspace_gid, custom_id=custom_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task_by_custom_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/tasks/custom_id/{custom_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/tasks/custom_id/{custom_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_task_by_custom_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_task_by_custom_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_task_by_custom_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="Search Tasks in Workspace",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_tasks(
    workspace_gid: str = Field(..., description="The globally unique identifier of the workspace or organization to search within."),
    text: str | None = Field(None, description="Full-text search string matched against both task name and description."),
    resource_subtype: Literal["default_task", "milestone", "approval", "custom"] | None = Field(None, description="Filters results to tasks of a specific subtype. Use 'default_task' for standard tasks, 'milestone' for milestones, 'approval' for approval tasks, or 'custom' for custom task types."),
    assignee_any: str | None = Field(None, alias="assignee.any", description="Returns tasks assigned to any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'."),
    assignee_not: str | None = Field(None, alias="assignee.not", description="Excludes tasks assigned to any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'."),
    portfolios_any: str | None = Field(None, alias="portfolios.any", description="Returns tasks belonging to any of the specified portfolios. Accepts a comma-separated list of portfolio GIDs."),
    projects_any: str | None = Field(None, alias="projects.any", description="Returns tasks belonging to any of the specified projects. Accepts a comma-separated list of project GIDs. Note: combining with sections.any returns tasks matching either filter, not just the section."),
    projects_not: str | None = Field(None, alias="projects.not", description="Excludes tasks belonging to any of the specified projects. Accepts a comma-separated list of project GIDs."),
    projects_all: str | None = Field(None, alias="projects.all", description="Returns tasks belonging to all of the specified projects. Accepts a comma-separated list of project GIDs."),
    sections_any: str | None = Field(None, alias="sections.any", description="Returns tasks in any of the specified sections or columns. Accepts a comma-separated list of section GIDs. To retrieve only tasks in a section, omit projects.any."),
    sections_not: str | None = Field(None, alias="sections.not", description="Excludes tasks in any of the specified sections or columns. Accepts a comma-separated list of section GIDs."),
    sections_all: str | None = Field(None, alias="sections.all", description="Returns tasks in all of the specified sections or columns. Accepts a comma-separated list of section GIDs."),
    tags_any: str | None = Field(None, alias="tags.any", description="Returns tasks with any of the specified tags. Accepts a comma-separated list of tag GIDs."),
    tags_not: str | None = Field(None, alias="tags.not", description="Excludes tasks with any of the specified tags. Accepts a comma-separated list of tag GIDs."),
    tags_all: str | None = Field(None, alias="tags.all", description="Returns tasks that have all of the specified tags. Accepts a comma-separated list of tag GIDs."),
    teams_any: str | None = Field(None, alias="teams.any", description="Returns tasks belonging to any of the specified teams. Accepts a comma-separated list of team GIDs."),
    followers_any: str | None = Field(None, alias="followers.any", description="Returns tasks followed by any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'."),
    followers_not: str | None = Field(None, alias="followers.not", description="Excludes tasks followed by any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'."),
    created_by_any: str | None = Field(None, alias="created_by.any", description="Returns tasks created by any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'."),
    created_by_not: str | None = Field(None, alias="created_by.not", description="Excludes tasks created by any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'."),
    assigned_by_any: str | None = Field(None, alias="assigned_by.any", description="Returns tasks assigned by any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'."),
    assigned_by_not: str | None = Field(None, alias="assigned_by.not", description="Excludes tasks assigned by any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'."),
    liked_by_not: str | None = Field(None, alias="liked_by.not", description="Excludes tasks liked by any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'."),
    commented_on_by_not: str | None = Field(None, alias="commented_on_by.not", description="Excludes tasks commented on by any of the specified users. Accepts a comma-separated list of user GIDs or the special value 'me'."),
    due_on_before: str | None = Field(None, alias="due_on.before", description="Returns tasks with a due date strictly before the specified date. Accepts an ISO 8601 date string."),
    due_on_after: str | None = Field(None, alias="due_on.after", description="Returns tasks with a due date strictly after the specified date. Accepts an ISO 8601 date string."),
    due_on: str | None = Field(None, description="Returns tasks with a due date exactly matching the specified date, or pass null to match tasks with no due date. Accepts an ISO 8601 date string or null."),
    due_at_before: str | None = Field(None, alias="due_at.before", description="Returns tasks with a due datetime strictly before the specified datetime. Accepts an ISO 8601 datetime string with timezone."),
    due_at_after: str | None = Field(None, alias="due_at.after", description="Returns tasks with a due datetime strictly after the specified datetime. Accepts an ISO 8601 datetime string with timezone."),
    start_on_before: str | None = Field(None, alias="start_on.before", description="Returns tasks with a start date strictly before the specified date. Accepts an ISO 8601 date string."),
    start_on_after: str | None = Field(None, alias="start_on.after", description="Returns tasks with a start date strictly after the specified date. Accepts an ISO 8601 date string."),
    start_on: str | None = Field(None, description="Returns tasks with a start date exactly matching the specified date, or pass null to match tasks with no start date. Accepts an ISO 8601 date string or null."),
    created_on_before: str | None = Field(None, alias="created_on.before", description="Returns tasks created strictly before the specified date. Accepts an ISO 8601 date string."),
    created_on_after: str | None = Field(None, alias="created_on.after", description="Returns tasks created strictly after the specified date. Accepts an ISO 8601 date string."),
    created_on: str | None = Field(None, description="Returns tasks created on exactly the specified date, or pass null to match tasks with no creation date recorded. Accepts an ISO 8601 date string or null."),
    created_at_before: str | None = Field(None, alias="created_at.before", description="Returns tasks created strictly before the specified datetime. Accepts an ISO 8601 datetime string with timezone."),
    created_at_after: str | None = Field(None, alias="created_at.after", description="Returns tasks created strictly after the specified datetime. Accepts an ISO 8601 datetime string with timezone."),
    completed_on_before: str | None = Field(None, alias="completed_on.before", description="Returns tasks completed strictly before the specified date. Accepts an ISO 8601 date string."),
    completed_on_after: str | None = Field(None, alias="completed_on.after", description="Returns tasks completed strictly after the specified date. Accepts an ISO 8601 date string."),
    completed_on: str | None = Field(None, description="Returns tasks completed on exactly the specified date, or pass null to match tasks with no completion date. Accepts an ISO 8601 date string or null."),
    completed_at_before: str | None = Field(None, alias="completed_at.before", description="Returns tasks completed strictly before the specified datetime. Accepts an ISO 8601 datetime string with timezone."),
    completed_at_after: str | None = Field(None, alias="completed_at.after", description="Returns tasks completed strictly after the specified datetime. Accepts an ISO 8601 datetime string with timezone."),
    modified_on_before: str | None = Field(None, alias="modified_on.before", description="Returns tasks last modified strictly before the specified date. Accepts an ISO 8601 date string."),
    modified_on_after: str | None = Field(None, alias="modified_on.after", description="Returns tasks last modified strictly after the specified date. Accepts an ISO 8601 date string."),
    modified_on: str | None = Field(None, description="Returns tasks last modified on exactly the specified date, or pass null to match tasks with no modification date. Accepts an ISO 8601 date string or null."),
    modified_at_before: str | None = Field(None, alias="modified_at.before", description="Returns tasks last modified strictly before the specified datetime. Accepts an ISO 8601 datetime string with timezone."),
    modified_at_after: str | None = Field(None, alias="modified_at.after", description="Returns tasks last modified strictly after the specified datetime. Accepts an ISO 8601 datetime string with timezone."),
    is_blocking: bool | None = Field(None, description="When true, filters to incomplete tasks that have at least one incomplete dependent task blocking them from being considered done."),
    is_blocked: bool | None = Field(None, description="When true, filters to tasks that have at least one incomplete dependency that must be resolved before the task can be completed."),
    has_attachment: bool | None = Field(None, description="When true, filters to tasks that have one or more file attachments."),
    completed: bool | None = Field(None, description="When true, returns only completed tasks; when false, returns only incomplete tasks. Omit to return both."),
    is_subtask: bool | None = Field(None, description="When true, filters results to subtasks only; when false, excludes subtasks from results."),
    sort_by: Literal["due_date", "created_at", "completed_at", "likes", "modified_at"] | None = Field(None, description="Field by which to sort the returned tasks. Defaults to 'modified_at'. Use in combination with sort_ascending to control order direction."),
    sort_ascending: bool | None = Field(None, description="When true, results are sorted in ascending order by the sort_by field; when false (default), results are sorted in descending order."),
) -> dict[str, Any] | ToolResult:
    """Search tasks within a workspace using advanced filters including text, assignees, projects, dates, custom fields, and more. Requires a premium Asana workspace or premium team membership; results are eventually consistent and support manual pagination via sort and limit."""

    # Construct request model with validation
    try:
        _request = _models.SearchTasksForWorkspaceRequest(
            path=_models.SearchTasksForWorkspaceRequestPath(workspace_gid=workspace_gid),
            query=_models.SearchTasksForWorkspaceRequestQuery(text=text, resource_subtype=resource_subtype, assignee_any=assignee_any, assignee_not=assignee_not, portfolios_any=portfolios_any, projects_any=projects_any, projects_not=projects_not, projects_all=projects_all, sections_any=sections_any, sections_not=sections_not, sections_all=sections_all, tags_any=tags_any, tags_not=tags_not, tags_all=tags_all, teams_any=teams_any, followers_any=followers_any, followers_not=followers_not, created_by_any=created_by_any, created_by_not=created_by_not, assigned_by_any=assigned_by_any, assigned_by_not=assigned_by_not, liked_by_not=liked_by_not, commented_on_by_not=commented_on_by_not, due_on_before=due_on_before, due_on_after=due_on_after, due_on=due_on, due_at_before=due_at_before, due_at_after=due_at_after, start_on_before=start_on_before, start_on_after=start_on_after, start_on=start_on, created_on_before=created_on_before, created_on_after=created_on_after, created_on=created_on, created_at_before=created_at_before, created_at_after=created_at_after, completed_on_before=completed_on_before, completed_on_after=completed_on_after, completed_on=completed_on, completed_at_before=completed_at_before, completed_at_after=completed_at_after, modified_on_before=modified_on_before, modified_on_after=modified_on_after, modified_on=modified_on, modified_at_before=modified_at_before, modified_at_after=modified_at_after, is_blocking=is_blocking, is_blocked=is_blocked, has_attachment=has_attachment, completed=completed, is_subtask=is_subtask, sort_by=sort_by, sort_ascending=sort_ascending)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/tasks/search", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/tasks/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_tasks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_tasks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Team memberships
@mcp.tool(
    title="Get Team Membership",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_team_membership(team_membership_gid: str = Field(..., description="The unique identifier (GID) of the team membership record to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete membership record for a single team membership, including details about the member and their associated team. Requires the `team_memberships:read` scope, with additional `teams:read` scope needed to access team details."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamMembershipRequest(
            path=_models.GetTeamMembershipRequestPath(team_membership_gid=team_membership_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/team_memberships/{team_membership_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/team_memberships/{team_membership_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_team_membership")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_team_membership", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_team_membership",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Team memberships
@mcp.tool(
    title="List Team Memberships",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_team_memberships(
    limit: int | None = Field(None, description="The number of team membership records to return per page, between 1 and 100.", ge=1, le=100),
    team: str | None = Field(None, description="The globally unique identifier (GID) of the team whose memberships should be returned."),
    user: str | None = Field(None, description="Identifies the user whose team memberships to retrieve; accepts the string \"me\", a user email address, or a user GID. Must be used together with the workspace parameter."),
    workspace: str | None = Field(None, description="The globally unique identifier (GID) of the workspace to scope the results to. Must be used together with the user parameter."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of compact team membership records, optionally filtered by team, user, or workspace. Requires the team_memberships:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamMembershipsRequest(
            query=_models.GetTeamMembershipsRequestQuery(limit=limit, team=team, user=user, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/team_memberships"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_team_memberships")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_team_memberships", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_team_memberships",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Team memberships
@mcp.tool(
    title="List Team Memberships for Team",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_team_memberships_for_team(
    team_gid: str = Field(..., description="The globally unique identifier of the team whose memberships you want to retrieve."),
    limit: int | None = Field(None, description="The number of membership records to return per page, accepting values between 1 and 100.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all team memberships for a specified team, returning compact membership records for each member. Requires the team_memberships:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamMembershipsForTeamRequest(
            path=_models.GetTeamMembershipsForTeamRequestPath(team_gid=team_gid),
            query=_models.GetTeamMembershipsForTeamRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_memberships_for_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_gid}/team_memberships", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_gid}/team_memberships"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_team_memberships_for_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_team_memberships_for_team", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_team_memberships_for_team",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Team memberships
@mcp.tool(
    title="List User Team Memberships",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_user_team_memberships(
    user_gid: str = Field(..., description="The unique identifier for the user whose team memberships will be retrieved. Accepts the string 'me' for the authenticated user, a user's email address, or a user's global ID (gid)."),
    workspace: str = Field(..., description="The globally unique identifier (gid) of the workspace used to scope the team membership results to a specific organization or workspace."),
    limit: int | None = Field(None, description="The number of team membership records to return per page, allowing pagination through large result sets. Must be an integer between 1 and 100.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all team memberships for a specified user within a given workspace, returning compact membership records. Requires the team_memberships:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamMembershipsForUserRequest(
            path=_models.GetTeamMembershipsForUserRequestPath(user_gid=user_gid),
            query=_models.GetTeamMembershipsForUserRequestQuery(limit=limit, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_team_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_gid}/team_memberships", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_gid}/team_memberships"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_team_memberships")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_team_memberships", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_team_memberships",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool(
    title="Create Team",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_team(data: _models.TeamRequest | None = Field(None, description="The configuration details for the new team, such as name and settings.")) -> dict[str, Any] | ToolResult:
    """Creates a new team within the current workspace. Use this to organize members and resources under a named group."""

    # Construct request model with validation
    try:
        _request = _models.CreateTeamRequest(
            body=_models.CreateTeamRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/teams"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_team", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_team",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool(
    title="Get Team",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_team(team_gid: str = Field(..., description="The globally unique identifier (GID) for the team to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the full details for a single team by its unique identifier. Requires the teams:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamRequest(
            path=_models.GetTeamRequestPath(team_gid=team_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_team", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_team",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool(
    title="Update Team",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_team(
    team_gid: str = Field(..., description="The globally unique identifier for the team to be updated."),
    data: _models.TeamRequest | None = Field(None, description="The team fields to update, provided as a data object containing the properties and their new values."),
) -> dict[str, Any] | ToolResult:
    """Updates the properties of an existing team within the current workspace. Use this to modify team details such as name or description."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTeamRequest(
            path=_models.UpdateTeamRequestPath(team_gid=team_gid),
            body=_models.UpdateTeamRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_gid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_team", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_team",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool(
    title="List Workspace Teams",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_workspace_teams(
    workspace_gid: str = Field(..., description="The globally unique identifier for the workspace or organization whose teams you want to retrieve."),
    limit: int | None = Field(None, description="The number of team records to return per page. Must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves compact records for all teams within a specified workspace or organization that are visible to the authorized user. Requires the 'teams:read' scope."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamsForWorkspaceRequest(
            path=_models.GetTeamsForWorkspaceRequestPath(workspace_gid=workspace_gid),
            query=_models.GetTeamsForWorkspaceRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_teams: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/teams", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/teams"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_teams")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_teams", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_teams",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool(
    title="List User Teams",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_user_teams(
    user_gid: str = Field(..., description="The unique identifier for the user whose teams you want to retrieve. Accepts the literal string 'me' for the authenticated user, a user's email address, or a numeric user GID."),
    organization: str = Field(..., description="The GID of the workspace or organization used to filter the returned teams, ensuring only teams within that context are included."),
    limit: int | None = Field(None, description="The number of team records to return per page. Must be an integer between 1 and 100 inclusive.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all teams that a specified user belongs to, optionally filtered by a workspace or organization. Returns compact team records for the given user."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamsForUserRequest(
            path=_models.GetTeamsForUserRequestPath(user_gid=user_gid),
            query=_models.GetTeamsForUserRequestQuery(limit=limit, organization=organization)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_teams: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_gid}/teams", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_gid}/teams"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_teams")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_teams", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_teams",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool(
    title="Add Team Member",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_team_member(
    team_gid: str = Field(..., description="The unique identifier of the team to which the user will be added."),
    user: str | None = Field(None, description="The identifier of the user to add to the team — accepts the literal string 'me' for the current user, a user's email address, or a user's globally unique identifier (GID)."),
) -> dict[str, Any] | ToolResult:
    """Adds a user to the specified team, creating a new team membership record. The requesting user must already be a member of the team, and the user being added must belong to the same organization."""

    # Construct request model with validation
    try:
        _request = _models.AddUserForTeamRequest(
            path=_models.AddUserForTeamRequestPath(team_gid=team_gid),
            body=_models.AddUserForTeamRequestBody(data=_models.AddUserForTeamRequestBodyData(user=user) if any(v is not None for v in [user]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_team_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_gid}/addUser", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_gid}/addUser"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_team_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_team_member", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_team_member",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool(
    title="Remove Team Member",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_team_member(
    team_gid: str = Field(..., description="The globally unique identifier of the team from which the user will be removed."),
    user: str | None = Field(None, description="The identifier of the user to remove, accepted as the string 'me' (for the requesting user), an email address, or a user GID."),
) -> dict[str, Any] | ToolResult:
    """Removes a specified user from a team. The user making this request must be a member of the team to remove themselves or others."""

    # Construct request model with validation
    try:
        _request = _models.RemoveUserForTeamRequest(
            path=_models.RemoveUserForTeamRequestPath(team_gid=team_gid),
            body=_models.RemoveUserForTeamRequestBody(data=_models.RemoveUserForTeamRequestBodyData(user=user) if any(v is not None for v in [user]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_team_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_gid}/removeUser", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_gid}/removeUser"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_team_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_team_member", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_team_member",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time periods
@mcp.tool(
    title="Get Time Period",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_time_period(time_period_gid: str = Field(..., description="The globally unique identifier of the time period to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the full details of a specific time period by its unique identifier. Useful for accessing goal-tracking intervals such as fiscal quarters or annual periods."""

    # Construct request model with validation
    try:
        _request = _models.GetTimePeriodRequest(
            path=_models.GetTimePeriodRequestPath(time_period_gid=time_period_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_time_period: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/time_periods/{time_period_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/time_periods/{time_period_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_time_period")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_time_period", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_time_period",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time periods
@mcp.tool(
    title="List Time Periods",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_time_periods(
    workspace: str = Field(..., description="The globally unique identifier of the workspace whose time periods should be retrieved."),
    limit: int | None = Field(None, description="The number of time period records to return per page, between 1 and 100.", ge=1, le=100),
    start_on: str | None = Field(None, description="Filters results to time periods starting on or after this date, specified in ISO 8601 date format."),
    end_on: str | None = Field(None, description="Filters results to time periods ending on or before this date, specified in ISO 8601 date format."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of compact time period records for a given workspace. Useful for browsing available time periods such as fiscal quarters or sprints."""

    # Construct request model with validation
    try:
        _request = _models.GetTimePeriodsRequest(
            query=_models.GetTimePeriodsRequestQuery(limit=limit, start_on=start_on, end_on=end_on, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_time_periods: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/time_periods"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_time_periods")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_time_periods", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_time_periods",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time tracking entries
@mcp.tool(
    title="List Task Time Tracking Entries",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_task_time_tracking_entries(task_gid: str = Field(..., description="The task to operate on.")) -> dict[str, Any] | ToolResult:
    """Retrieves all time tracking entries logged against a specific task. Requires the time_tracking_entries:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetTimeTrackingEntriesForTaskRequest(
            path=_models.GetTimeTrackingEntriesForTaskRequestPath(task_gid=task_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_task_time_tracking_entries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/time_tracking_entries", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/time_tracking_entries"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_task_time_tracking_entries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_task_time_tracking_entries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_task_time_tracking_entries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time tracking entries
@mcp.tool(
    title="Create Time Entry",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_time_entry(
    task_gid: str = Field(..., description="The unique identifier (GID) of the task on which the time tracking entry will be created."),
    duration_minutes: int | None = Field(None, description="The amount of time to log for this entry, expressed in whole minutes. Must be greater than 0."),
    entered_on: str | None = Field(None, description="The calendar date this time entry is logged against, in ISO 8601 date format (YYYY-MM-DD). Defaults to today if omitted."),
    attributable_to: str | None = Field(None, description="The GID of the project this time entry should be attributed to, allowing time to be associated with a specific project context."),
    billable_status: Literal["billable", "nonBillable", "notApplicable"] | None = Field(None, description="The billable classification of this time entry: 'billable' for client-chargeable time, 'nonBillable' for internal time, or 'notApplicable' when billing status is not relevant."),
    description: str | None = Field(None, description="A free-text note describing the work performed during this time entry, providing context for the logged time."),
) -> dict[str, Any] | ToolResult:
    """Logs a new time tracking entry on a specified task, recording duration, date, billable status, and optional project attribution. Returns the newly created time tracking entry record."""

    # Construct request model with validation
    try:
        _request = _models.CreateTimeTrackingEntryRequest(
            path=_models.CreateTimeTrackingEntryRequestPath(task_gid=task_gid),
            body=_models.CreateTimeTrackingEntryRequestBody(data=_models.CreateTimeTrackingEntryRequestBodyData(duration_minutes=duration_minutes, entered_on=entered_on, attributable_to=attributable_to, billable_status=billable_status, description=description) if any(v is not None for v in [duration_minutes, entered_on, attributable_to, billable_status, description]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_time_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_gid}/time_tracking_entries", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_gid}/time_tracking_entries"
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
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time tracking entries
@mcp.tool(
    title="Get Time Tracking Entry",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_time_tracking_entry(time_tracking_entry_gid: str = Field(..., description="The globally unique identifier (GID) of the time tracking entry to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single time tracking entry. Requires the time_tracking_entries:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetTimeTrackingEntryRequest(
            path=_models.GetTimeTrackingEntryRequestPath(time_tracking_entry_gid=time_tracking_entry_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_time_tracking_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/time_tracking_entries/{time_tracking_entry_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/time_tracking_entries/{time_tracking_entry_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_time_tracking_entry")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_time_tracking_entry", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_time_tracking_entry",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time tracking entries
@mcp.tool(
    title="Update Time Tracking Entry",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_time_tracking_entry(
    time_tracking_entry_gid: str = Field(..., description="The globally unique identifier of the time tracking entry to update."),
    duration_minutes: int | None = Field(None, description="The amount of time to log for this entry, expressed in whole minutes."),
    entered_on: str | None = Field(None, description="The calendar date on which this time entry is logged, in ISO 8601 date format. Defaults to today if not specified."),
    attributable_to: str | None = Field(None, description="The unique identifier (GID) of the project to which this time entry's effort is attributed."),
    billable_status: Literal["billable", "nonBillable", "notApplicable"] | None = Field(None, description="The billable status of this time entry. Use 'billable' for client-chargeable work, 'nonBillable' for internal work, or 'notApplicable' when billing status is irrelevant."),
    description: str | None = Field(None, description="A free-text description summarizing the work performed during this time entry."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing time tracking entry by its unique identifier, modifying only the fields provided while leaving all other fields unchanged. Returns the complete updated time tracking entry record."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTimeTrackingEntryRequest(
            path=_models.UpdateTimeTrackingEntryRequestPath(time_tracking_entry_gid=time_tracking_entry_gid),
            body=_models.UpdateTimeTrackingEntryRequestBody(data=_models.UpdateTimeTrackingEntryRequestBodyData(duration_minutes=duration_minutes, entered_on=entered_on, attributable_to=attributable_to, billable_status=billable_status, description=description) if any(v is not None for v in [duration_minutes, entered_on, attributable_to, billable_status, description]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_time_tracking_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/time_tracking_entries/{time_tracking_entry_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/time_tracking_entries/{time_tracking_entry_gid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_time_tracking_entry")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_time_tracking_entry", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_time_tracking_entry",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time tracking entries
@mcp.tool(
    title="Delete Time Tracking Entry",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_time_tracking_entry(time_tracking_entry_gid: str = Field(..., description="The globally unique identifier (GID) of the time tracking entry to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific time tracking entry by its unique identifier. Returns an empty data record upon successful deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTimeTrackingEntryRequest(
            path=_models.DeleteTimeTrackingEntryRequestPath(time_tracking_entry_gid=time_tracking_entry_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_time_tracking_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/time_tracking_entries/{time_tracking_entry_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/time_tracking_entries/{time_tracking_entry_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_time_tracking_entry")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_time_tracking_entry", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_time_tracking_entry",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time tracking entries
@mcp.tool(
    title="List Time Tracking Entries",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_time_tracking_entries(
    task: str | None = Field(None, description="The globally unique identifier of the task to scope results to only time tracking entries associated with that task."),
    attributable_to: str | None = Field(None, description="The globally unique identifier of the project to scope results to only time tracking entries attributed to that project."),
    portfolio: str | None = Field(None, description="The globally unique identifier of the portfolio to scope results to only time tracking entries belonging to tasks within that portfolio."),
    user: str | None = Field(None, description="The globally unique identifier of the user to scope results to only time tracking entries logged by that user."),
    workspace: str | None = Field(None, description="The globally unique identifier of the workspace to scope results to. When filtering by workspace, at least one of `entered_on_start_date` or `entered_on_end_date` must also be provided."),
    entered_on_start_date: str | None = Field(None, description="The inclusive start date for filtering entries by their entry date, in ISO 8601 date format (YYYY-MM-DD). Use together with `entered_on_end_date` to define a date range."),
    entered_on_end_date: str | None = Field(None, description="The inclusive end date for filtering entries by their entry date, in ISO 8601 date format (YYYY-MM-DD). Use together with `entered_on_start_date` to define a date range."),
    timesheet_approval_status: str | None = Field(None, description="The globally unique identifier of a timesheet approval status to scope results to only time tracking entries matching that approval state."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of time tracking entries, optionally filtered by task, project, portfolio, user, workspace, date range, or timesheet approval status. Requires the `time_tracking_entries:read` scope."""

    # Construct request model with validation
    try:
        _request = _models.GetTimeTrackingEntriesRequest(
            query=_models.GetTimeTrackingEntriesRequestQuery(task=task, attributable_to=attributable_to, portfolio=portfolio, user=user, workspace=workspace, entered_on_start_date=entered_on_start_date, entered_on_end_date=entered_on_end_date, timesheet_approval_status=timesheet_approval_status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_time_tracking_entries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/time_tracking_entries"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_time_tracking_entries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_time_tracking_entries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_time_tracking_entries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Timesheet approval statuses
@mcp.tool(
    title="Get Timesheet Approval Status",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_timesheet_approval_status(timesheet_approval_status_gid: str = Field(..., description="The globally unique identifier (GID) of the timesheet approval status record to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete record for a single timesheet approval status, including its current state and associated metadata. Requires the timesheet_approval_statuses:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetTimesheetApprovalStatusRequest(
            path=_models.GetTimesheetApprovalStatusRequestPath(timesheet_approval_status_gid=timesheet_approval_status_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_timesheet_approval_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/timesheet_approval_statuses/{timesheet_approval_status_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/timesheet_approval_statuses/{timesheet_approval_status_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_timesheet_approval_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_timesheet_approval_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_timesheet_approval_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Timesheet approval statuses
@mcp.tool(
    title="Update Timesheet Approval Status",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def update_timesheet_approval_status(
    timesheet_approval_status_gid: str = Field(..., description="The globally unique identifier of the timesheet approval status record to update."),
    approval_status: Literal["submitted", "draft", "approved", "rejected"] = Field(..., description="The target approval state to transition to. Valid values are 'submitted' (submit for review), 'draft' (recall a submission), 'approved' (approve the timesheet), or 'rejected' (reject the timesheet). Allowed transitions depend on the current state of the record."),
    message: str | None = Field(None, description="An optional message to accompany the status transition, such as a reason for approval or rejection."),
) -> dict[str, Any] | ToolResult:
    """Transitions a timesheet approval status to a new state, such as submitting, recalling, approving, or rejecting. Only the provided fields are updated; invalid state transitions return a 400 error."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTimesheetApprovalStatusRequest(
            path=_models.UpdateTimesheetApprovalStatusRequestPath(timesheet_approval_status_gid=timesheet_approval_status_gid),
            body=_models.UpdateTimesheetApprovalStatusRequestBody(data=_models.UpdateTimesheetApprovalStatusRequestBodyData(approval_status=approval_status, message=message))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_timesheet_approval_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/timesheet_approval_statuses/{timesheet_approval_status_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/timesheet_approval_statuses/{timesheet_approval_status_gid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_timesheet_approval_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_timesheet_approval_status", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_timesheet_approval_status",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Timesheet approval statuses
@mcp.tool(
    title="List Timesheet Approval Statuses",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_timesheet_approval_statuses(
    workspace: str = Field(..., description="The globally unique identifier of the workspace whose timesheet approval statuses should be retrieved."),
    user: str | None = Field(None, description="The globally unique identifier of a specific user to narrow results to only their timesheet approval statuses."),
    from_date: str | None = Field(None, description="The inclusive start date for filtering timesheet approval statuses, in ISO 8601 date format (YYYY-MM-DD)."),
    to_date: str | None = Field(None, description="The inclusive end date for filtering timesheet approval statuses, in ISO 8601 date format (YYYY-MM-DD)."),
    approval_statuses: str | None = Field(None, description="One or more approval status values to filter by; accepted values are draft, submitted, approved, or rejected. Multiple values may be provided as a comma-separated list."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of timesheet approval statuses for a given workspace, with optional filtering by user, date range, or approval status. Requires the timesheet_approval_statuses:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetTimesheetApprovalStatusesRequest(
            query=_models.GetTimesheetApprovalStatusesRequestQuery(workspace=workspace, user=user, from_date=from_date, to_date=to_date, approval_statuses=approval_statuses)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_timesheet_approval_statuses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/timesheet_approval_statuses"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_timesheet_approval_statuses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_timesheet_approval_statuses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_timesheet_approval_statuses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Timesheet approval statuses
@mcp.tool(
    title="Create Timesheet Approval Status",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_timesheet_approval_status(
    user: str = Field(..., description="The globally unique identifier of the user whose timesheet approval status is being created."),
    workspace: str = Field(..., description="The globally unique identifier of the workspace in which the timesheet exists."),
    start_date: str = Field(..., description="The start date of the timesheet week in ISO 8601 date format; must be a Monday."),
    end_date: str = Field(..., description="The end date of the timesheet week in ISO 8601 date format; must be the Sunday immediately following the start date."),
) -> dict[str, Any] | ToolResult:
    """Creates a new timesheet approval status for a specific user's weekly timesheet within a workspace. The week must span exactly Monday through the following Sunday."""

    # Construct request model with validation
    try:
        _request = _models.CreateTimesheetApprovalStatusRequest(
            body=_models.CreateTimesheetApprovalStatusRequestBody(data=_models.CreateTimesheetApprovalStatusRequestBodyData(user=user, workspace=workspace, start_date=start_date, end_date=end_date))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_timesheet_approval_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/timesheet_approval_statuses"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_timesheet_approval_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_timesheet_approval_status", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_timesheet_approval_status",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Typeahead
@mcp.tool(
    title="Search Workspace Typeahead",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_workspace_typeahead(
    workspace_gid: str = Field(..., description="The globally unique identifier for the workspace or organization to search within."),
    resource_type: Literal["custom_field", "goal", "project", "project_template", "portfolio", "tag", "task", "team", "user"] = Field(..., description="The type of resource to search for. Accepts a single type from the supported set: custom_field, goal, project, project_template, portfolio, tag, task, team, or user. Multiple types are not supported."),
    query: str | None = Field(None, description="The search string used to match relevant objects by name or other identifying fields. Omitting or passing an empty string returns results ordered by relevance heuristics (e.g., recency or contact frequency) for the authenticated user."),
    count: int | None = Field(None, description="The maximum number of results to return, between 1 and 100. Defaults to 20 if omitted; if fewer matches exist than requested, all available results are returned."),
) -> dict[str, Any] | ToolResult:
    """Performs a fast typeahead/auto-completion search within a workspace, returning a compact list of matching objects (users, projects, tasks, etc.) ordered by relevance. Results are limited to a single page and are optimized for speed rather than exhaustive accuracy."""

    # Construct request model with validation
    try:
        _request = _models.TypeaheadForWorkspaceRequest(
            path=_models.TypeaheadForWorkspaceRequestPath(workspace_gid=workspace_gid),
            query=_models.TypeaheadForWorkspaceRequestQuery(resource_type=resource_type, query=query, count=count)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_workspace_typeahead: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/typeahead", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/typeahead"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_workspace_typeahead")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_workspace_typeahead", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_workspace_typeahead",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User task lists
@mcp.tool(
    title="Get User Task List",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_user_task_list(user_task_list_gid: str = Field(..., description="The globally unique identifier for the user task list to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the full record for a specific user task list, including all associated metadata. Requires the tasks:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetUserTaskListRequest(
            path=_models.GetUserTaskListRequestPath(user_task_list_gid=user_task_list_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_task_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user_task_lists/{user_task_list_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/user_task_lists/{user_task_list_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_task_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_task_list", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_task_list",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User task lists
@mcp.tool(
    title="Get User Task List by User",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_user_task_list_by_user(
    user_gid: str = Field(..., description="The unique identifier for the user whose task list you want to retrieve. Accepts the literal string 'me' for the authenticated user, a user's email address, or a user's global ID (gid)."),
    workspace: str = Field(..., description="The global ID (gid) of the workspace in which to look up the user's task list. Each user has one task list per workspace."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the full task list record for a specified user within a given workspace. Requires the tasks:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetUserTaskListForUserRequest(
            path=_models.GetUserTaskListForUserRequestPath(user_gid=user_gid),
            query=_models.GetUserTaskListForUserRequestQuery(workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_task_list_by_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_gid}/user_task_list", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_gid}/user_task_list"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_task_list_by_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_task_list_by_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_task_list_by_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool(
    title="List Users",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_users(
    workspace: str | None = Field(None, description="The unique ID of a workspace or organization to restrict results to only users belonging to that workspace or organization."),
    team: str | None = Field(None, description="The unique ID of a team to restrict results to only users belonging to that team."),
    limit: int | None = Field(None, description="The number of user records to return per page. Must be an integer between 1 and 100 inclusive.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves user records across all workspaces and organizations accessible to the authenticated user, with optional filtering by workspace or team. Requires the 'users:read' scope and returns results sorted by user ID."""

    # Construct request model with validation
    try:
        _request = _models.GetUsersRequest(
            query=_models.GetUsersRequestQuery(workspace=workspace, team=team, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users"
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
@mcp.tool(
    title="Get User",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_user(
    user_gid: str = Field(..., description="The unique identifier for the user to retrieve. Accepts a user GID, an email address, or the string 'me' to reference the currently authenticated user."),
    workspace: str | None = Field(None, description="The GID of a workspace used to filter the user results, useful when a user belongs to multiple workspaces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the full profile record for a single user, identified by their GID, email address, or the shorthand 'me' for the authenticated user. Optionally scoped to a specific workspace."""

    # Construct request model with validation
    try:
        _request = _models.GetUserRequest(
            path=_models.GetUserRequestPath(user_gid=user_gid),
            query=_models.GetUserRequestQuery(workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_gid}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool(
    title="Update User",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_user(
    user_gid: str = Field(..., description="The unique identifier for the target user, which can be the literal string 'me' to reference the authenticated user, a user's email address, or a numeric user GID."),
    workspace: str | None = Field(None, description="Filters the operation to a specific workspace by its GID, useful when a user belongs to multiple workspaces."),
    data: _models.UserUpdateRequest | None = Field(None, description="An object containing the user fields to update; only the fields included here will be modified, all omitted fields retain their current values."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing user's profile by replacing only the fields provided in the request body, leaving all other fields unchanged. Returns the complete updated user record."""

    # Construct request model with validation
    try:
        _request = _models.UpdateUserRequest(
            path=_models.UpdateUserRequestPath(user_gid=user_gid),
            query=_models.UpdateUserRequestQuery(workspace=workspace),
            body=_models.UpdateUserRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_gid}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool(
    title="List User Favorites",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_user_favorites(
    user_gid: str = Field(..., description="The unique identifier of the user whose favorites to retrieve. Accepts the literal string 'me' to reference the authenticated user, a user's email address, or a user's GID."),
    resource_type: Literal["portfolio", "project", "tag", "task", "user", "project_template"] = Field(..., description="The type of Asana resource to filter favorites by. Must be one of the supported resource types: portfolio, project, tag, task, user, or project_template."),
    workspace: str = Field(..., description="The GID of the workspace in which to look up the user's favorites. All returned favorites will belong to this workspace."),
    limit: int | None = Field(None, description="The number of favorite items to return per page. Must be between 1 and 100 inclusive.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all favorites for a specified user within a given workspace, filtered by resource type, ordered as they appear in the user's Asana sidebar. Note: currently only returns favorites for the authenticated user."""

    # Construct request model with validation
    try:
        _request = _models.GetFavoritesForUserRequest(
            path=_models.GetFavoritesForUserRequestPath(user_gid=user_gid),
            query=_models.GetFavoritesForUserRequestQuery(limit=limit, resource_type=resource_type, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_favorites: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_gid}/favorites", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_gid}/favorites"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_favorites")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_favorites", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_favorites",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool(
    title="List Team Members",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_team_members(team_gid: str = Field(..., description="The globally unique identifier of the team whose members you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves all users who are members of a specified team, returned as compact records sorted alphabetically. Limited to 2000 results; use the users endpoint for larger result sets."""

    # Construct request model with validation
    try:
        _request = _models.GetUsersForTeamRequest(
            path=_models.GetUsersForTeamRequestPath(team_gid=team_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_gid}/users", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_gid}/users"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_team_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_team_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_team_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool(
    title="List Workspace Users",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_workspace_users(workspace_gid: str = Field(..., description="The globally unique identifier of the workspace or organization whose users you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a compact list of all users in the specified workspace or organization, sorted alphabetically. Results are capped at 2000 users; use the /users endpoint for larger result sets."""

    # Construct request model with validation
    try:
        _request = _models.GetUsersForWorkspaceRequest(
            path=_models.GetUsersForWorkspaceRequestPath(workspace_gid=workspace_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/users", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/users"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_users")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_users", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_users",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool(
    title="Get Workspace User",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_workspace_user(
    workspace_gid: str = Field(..., description="The globally unique identifier of the workspace or organization in which to look up the user."),
    user_gid: str = Field(..., description="The identifier for the target user — accepts the literal string \"me\" (for the authenticated user), a user's email address, or a user's globally unique identifier (GID)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the full profile record for a specific user within a given workspace or organization. Requires the `users:read` scope."""

    # Construct request model with validation
    try:
        _request = _models.GetUserForWorkspaceRequest(
            path=_models.GetUserForWorkspaceRequestPath(workspace_gid=workspace_gid, user_gid=user_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workspace_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/users/{user_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/users/{user_gid}"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool(
    title="Update Workspace User",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_workspace_user(
    workspace_gid: str = Field(..., description="The globally unique identifier of the workspace or organization in which the user will be updated."),
    user_gid: str = Field(..., description="The identifier of the user to update, which can be the string 'me' to reference the authenticated user, a user's email address, or a user's globally unique identifier (GID)."),
    data: _models.UserUpdateRequest | None = Field(None, description="The user fields to update within the workspace. Only fields included here will be changed; omitted fields retain their current values."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing user's information within a specified workspace or organization. Only the fields provided in the request body will be modified; all other fields remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.UpdateUserForWorkspaceRequest(
            path=_models.UpdateUserForWorkspaceRequestPath(workspace_gid=workspace_gid, user_gid=user_gid),
            body=_models.UpdateUserForWorkspaceRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_workspace_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/users/{user_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/users/{user_gid}"
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
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool(
    title="Get Webhook",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_webhook(webhook_gid: str = Field(..., description="The globally unique identifier of the webhook to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the full details of a specific webhook by its unique identifier. Requires the webhooks:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhookRequest(
            path=_models.GetWebhookRequestPath(webhook_gid=webhook_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/webhooks/{webhook_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/webhooks/{webhook_gid}"
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

# Tags: Webhooks
@mcp.tool(
    title="Delete Webhook",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_webhook(webhook_gid: str = Field(..., description="The globally unique identifier of the webhook to permanently delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a webhook, stopping all future event deliveries to its target URL. Note that in-flight requests sent before deletion may still arrive, but no new requests will be issued."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWebhookRequest(
            path=_models.DeleteWebhookRequestPath(webhook_gid=webhook_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/webhooks/{webhook_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/webhooks/{webhook_gid}"
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

# Tags: Workspace memberships
@mcp.tool(
    title="Get Workspace Membership",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_workspace_membership(workspace_membership_gid: str = Field(..., description="The unique identifier (GID) of the workspace membership to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the complete membership record for a single workspace membership, including details about the member and their role within the workspace."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspaceMembershipRequest(
            path=_models.GetWorkspaceMembershipRequestPath(workspace_membership_gid=workspace_membership_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workspace_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspace_memberships/{workspace_membership_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspace_memberships/{workspace_membership_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workspace_membership")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workspace_membership", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workspace_membership",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspace memberships
@mcp.tool(
    title="List User Workspace Memberships",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_user_workspace_memberships(
    user_gid: str = Field(..., description="The unique identifier for the user whose workspace memberships to retrieve. Accepts the literal string 'me' for the authenticated user, a registered email address, or a numeric user GID."),
    limit: int | None = Field(None, description="The number of membership records to return per page. Must be between 1 and 100 inclusive; use pagination to retrieve additional results beyond the first page.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves all workspace memberships for a specified user, returning compact membership records. Useful for discovering which workspaces a user belongs to."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspaceMembershipsForUserRequest(
            path=_models.GetWorkspaceMembershipsForUserRequestPath(user_gid=user_gid),
            query=_models.GetWorkspaceMembershipsForUserRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_workspace_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_gid}/workspace_memberships", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_gid}/workspace_memberships"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_workspace_memberships")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_workspace_memberships", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_workspace_memberships",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspace memberships
@mcp.tool(
    title="List Workspace Memberships",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_workspace_memberships(
    workspace_gid: str = Field(..., description="The globally unique identifier of the workspace or organization whose memberships you want to retrieve."),
    user: str | None = Field(None, description="Filter memberships to a specific user, identified by the string 'me' (current user), an email address, or a user GID."),
    limit: int | None = Field(None, description="The number of membership records to return per page. Must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves compact membership records for all members of a specified workspace or organization. Optionally filter results by a specific user."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspaceMembershipsForWorkspaceRequest(
            path=_models.GetWorkspaceMembershipsForWorkspaceRequestPath(workspace_gid=workspace_gid),
            query=_models.GetWorkspaceMembershipsForWorkspaceRequestQuery(user=user, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/workspace_memberships", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/workspace_memberships"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_memberships")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_memberships", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_memberships",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool(
    title="List Workspaces",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_workspaces(limit: int | None = Field(None, description="Number of workspace records to return per page. Must be between 1 and 100.", ge=1, le=100)) -> dict[str, Any] | ToolResult:
    """Retrieves all workspaces visible to the authorized user. Returns compact records for each workspace, requiring the workspaces:read scope."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesRequest(
            query=_models.GetWorkspacesRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspaces: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/workspaces"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool(
    title="Get Workspace",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_workspace(workspace_gid: str = Field(..., description="The globally unique identifier for the workspace or organization to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the full details of a single workspace or organization. Requires the workspace's unique identifier to return its complete record."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspaceRequest(
            path=_models.GetWorkspaceRequestPath(workspace_gid=workspace_gid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workspace: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workspace")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workspace", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workspace",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool(
    title="Update Workspace",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_workspace(
    workspace_gid: str = Field(..., description="The globally unique identifier of the workspace or organization to update."),
    name: str | None = Field(None, description="The new display name to assign to the workspace."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing workspace by modifying its properties, currently limited to renaming the workspace. Returns the complete updated workspace record."""

    # Construct request model with validation
    try:
        _request = _models.UpdateWorkspaceRequest(
            path=_models.UpdateWorkspaceRequestPath(workspace_gid=workspace_gid),
            body=_models.UpdateWorkspaceRequestBody(data=_models.UpdateWorkspaceRequestBodyData(name=name) if any(v is not None for v in [name]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_workspace: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_workspace")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_workspace", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_workspace",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool(
    title="Add Workspace User",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_workspace_user(
    workspace_gid: str = Field(..., description="The unique identifier of the workspace or organization to which the user will be added."),
    user: str | None = Field(None, description="The identifier of the user to add, accepted as the literal string 'me' (current user), an email address, or a user GID."),
) -> dict[str, Any] | ToolResult:
    """Adds a user to a workspace or organization by user ID or email address. Returns the full user record for the newly added user."""

    # Construct request model with validation
    try:
        _request = _models.AddUserForWorkspaceRequest(
            path=_models.AddUserForWorkspaceRequestPath(workspace_gid=workspace_gid),
            body=_models.AddUserForWorkspaceRequestBody(data=_models.AddUserForWorkspaceRequestBodyData(user=user) if any(v is not None for v in [user]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_workspace_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/addUser", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/addUser"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_workspace_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_workspace_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_workspace_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool(
    title="Remove Workspace User",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_workspace_user(
    workspace_gid: str = Field(..., description="The unique identifier of the workspace or organization from which the user will be removed."),
    user: str | None = Field(None, description="The identifier of the user to remove, which can be the literal string 'me', an email address, or a user's globally unique ID."),
) -> dict[str, Any] | ToolResult:
    """Removes a user from a workspace or organization, transferring ownership of their resources to the admin or PAT owner. The caller must be a workspace admin; the target user can be identified by their user ID or email address."""

    # Construct request model with validation
    try:
        _request = _models.RemoveUserForWorkspaceRequest(
            path=_models.RemoveUserForWorkspaceRequestPath(workspace_gid=workspace_gid),
            body=_models.RemoveUserForWorkspaceRequestBody(data=_models.RemoveUserForWorkspaceRequestBodyData(user=user) if any(v is not None for v in [user]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_workspace_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/removeUser", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/removeUser"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_workspace_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_workspace_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_workspace_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool(
    title="List Workspace Events",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_workspace_events(
    workspace_gid: str = Field(..., description="The globally unique identifier for the target workspace or organization whose events should be retrieved."),
    sync: str | None = Field(None, description="A sync token from a previous response used to fetch only events that occurred after that token was issued; omit this parameter on the first request to receive a fresh token. If the token has expired, the API returns a 412 error along with a new valid sync token to use going forward."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all events that have occurred in a workspace since a given sync token was issued, enabling incremental polling for changes. Returns up to 1000 events per request; if more exist, the response includes a flag to continue paginating with a refreshed sync token."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspaceEventsRequest(
            path=_models.GetWorkspaceEventsRequestPath(workspace_gid=workspace_gid),
            query=_models.GetWorkspaceEventsRequestQuery(sync=sync)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_gid}/events", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_gid}/events"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_events",
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
        print("  python asana_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Asana MCP Server")

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
    logger.info("Starting Asana MCP Server")
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

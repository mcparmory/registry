#!/usr/bin/env python3
"""
Box MCP Server

API Info:
- API License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
- Contact: Box, Inc <devrel@box.com> (https://developer.box.com)
- Terms of Service: https://cloud.app.box.com/s/rmwxu64h1ipr41u49w3bbuvbsa29wku9

Generated: 2026-05-11 19:32:49 UTC
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
import re
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

BASE_URL = os.getenv("BASE_URL", "https://api.box.com/2.0")
OPERATION_URL_MAP: dict[str, str] = {
    "upload_file_version": os.getenv("SERVER_URL_UPLOAD_FILE_VERSION", "https://upload.box.com/api/2.0"),
    "upload_file": os.getenv("SERVER_URL_UPLOAD_FILE", "https://upload.box.com/api/2.0"),
    "create_upload_session": os.getenv("SERVER_URL_CREATE_UPLOAD_SESSION", "https://upload.box.com/api/2.0"),
    "create_file_upload_session": os.getenv("SERVER_URL_CREATE_FILE_UPLOAD_SESSION", "https://upload.box.com/api/2.0"),
    "get_upload_session": os.getenv("SERVER_URL_GET_UPLOAD_SESSION", "https://upload.box.com/api/2.0"),
    "upload_file_part": os.getenv("SERVER_URL_UPLOAD_FILE_PART", "https://upload.box.com/api/2.0"),
    "abort_upload_session": os.getenv("SERVER_URL_ABORT_UPLOAD_SESSION", "https://upload.box.com/api/2.0"),
    "list_upload_session_parts": os.getenv("SERVER_URL_LIST_UPLOAD_SESSION_PARTS", "https://upload.box.com/api/2.0"),
    "commit_upload_session": os.getenv("SERVER_URL_COMMIT_UPLOAD_SESSION", "https://upload.box.com/api/2.0"),
    "download_zip_archive": os.getenv("SERVER_URL_DOWNLOAD_ZIP_ARCHIVE", "https://dl.boxcloud.com/2.0"),
}
SERVER_NAME = "Box"
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

    # Per-operation URL override (OAS 3.0 path/operation-level servers)
    _url_override = OPERATION_URL_MAP.get(tool_name or "")
    if _url_override:
        path = _url_override + path  # Absolute URL bypasses httpx base_url

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

def parse_metadata_template(value: str | None = None) -> dict | None:
    """Helper function for parameter transformation"""
    if value is None:
        return None
    parts = value.split('/', 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(f'metadata_template must be in scope/templateKey format, got: {value!r}')
    return {'scope': parts[0], 'templateKey': parts[1]}

def parse_name_and_login(value: str | None = None) -> dict | None:
    """Helper function for parameter transformation"""
    if value is None:
        return None
    value = value.strip()
    match = re.match(r'^(.*?)<([^>]+)>$', value)
    if match:
        display_name = match.group(1).strip()
        login = match.group(2).strip()
        if not login:
            raise ValueError('Login email inside angle brackets must not be empty.')
        return {'name': display_name, 'login': login}
    # No angle brackets — treat entire value as display name only (app user case)
    if not value:
        raise ValueError('name_and_login must not be an empty string.')
    return {'name': value, 'login': None}

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
    'OAuth2Security',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["OAuth2Security"] = _auth.OAuth2Auth()
    logging.info("Authentication configured: OAuth2Security")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for OAuth2Security not configured: {error_msg}")
    _auth_handlers["OAuth2Security"] = None

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

mcp = FastMCP("Box", middleware=[_JsonCoercionMiddleware()])

# Tags: Files
@mcp.tool(
    title="Get File",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_file(
    file_id: str = Field(..., description="The unique identifier of the file to retrieve. The file ID can be found in the Box web app URL when viewing the file."),
    boxapi: str | None = Field(None, description="A shared link URL and optional password used to access files that have not been explicitly shared with the authenticated user. Use the format `shared_link=[link]` or `shared_link=[link]&shared_link_password=[password]` for password-protected links."),
) -> dict[str, Any] | ToolResult:
    """Retrieves metadata and details for a specific file by its unique identifier. Optionally supports accessing files via a shared link, including password-protected ones."""

    # Construct request model with validation
    try:
        _request = _models.GetFilesIdRequest(
            path=_models.GetFilesIdRequestPath(file_id=file_id),
            header=_models.GetFilesIdRequestHeader(boxapi=boxapi)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

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

# Tags: Trashed files
@mcp.tool(
    title="Restore File",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def restore_file(
    file_id: str = Field(..., description="The unique identifier of the file to restore from the trash. The file ID can be found in the Box web app URL when viewing the file."),
    name: str | None = Field(None, description="An optional new name to assign to the file upon restoration, useful if a naming conflict exists in the destination folder."),
    parent: _models.PostFilesIdBodyParent | None = Field(None, description="An optional parent folder object specifying where the file should be restored to, used when the original parent folder has been deleted."),
) -> dict[str, Any] | ToolResult:
    """Restores a file from the trash back to its original location or a specified parent folder. An optional new parent folder can be provided if the original folder no longer exists."""

    # Construct request model with validation
    try:
        _request = _models.PostFilesIdRequest(
            path=_models.PostFilesIdRequestPath(file_id=file_id),
            body=_models.PostFilesIdRequestBody(name=name, parent=parent)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for restore_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("restore_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("restore_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="restore_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Files
@mcp.tool(
    title="Update File",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_file(
    file_id: str = Field(..., description="The unique identifier of the file to update. Find this ID in the Box web app by opening the file and copying the numeric ID from the URL."),
    name: str | None = Field(None, description="A new name for the file. Must be unique within the parent folder; the uniqueness check is case-insensitive."),
    description: str | None = Field(None, description="A text description for the file, visible in the Box web app sidebar and included in search indexing. Maximum 256 characters.", max_length=256),
    parent: _models.PutFilesIdBodyParent | None = Field(None, description="The parent folder to move the file into. Provide an object with the target folder's ID to relocate the file."),
    shared_link: _models.PutFilesIdBodySharedLink | None = Field(None, description="Shared link settings for the file. Provide an object with access level and permission options to create or update the file's shared link."),
    access: Literal["lock"] | None = Field(None, description="The type of lock to apply to the file. Must be set to 'lock' to lock the file and restrict editing by other users."),
    expires_at: str | None = Field(None, description="The date and time at which the file lock automatically expires, in ISO 8601 format."),
    is_download_prevented: bool | None = Field(None, description="Whether downloading the file is prevented while the lock is active. Set to true to block downloads during the lock period."),
    disposition_at: str | None = Field(None, description="The retention expiration timestamp for the file in ISO 8601 format. Once set, this date can only be extended, never shortened."),
    can_download: Literal["open", "company"] | None = Field(None, description="Controls who can download the file: 'open' allows anyone with access, while 'company' restricts downloads to members of the owner's enterprise, overriding collaboration role permissions."),
    collections_: list[_models.PutFilesIdBodyCollectionsItem] | None = Field(None, alias="collections", description="An array of collection objects (each with an 'id') to assign the file to. Currently only the favorites collection is supported. Pass an empty array or null to remove the file from all collections."),
    tags: list[str] | None = Field(None, description="An array of string tags to associate with the file, visible in the Box web and mobile apps. To modify tags, retrieve the current list, apply changes, and submit the full updated array. Maximum 100 tags per item, each tag between 1 and 100 characters.", min_length=1, max_length=100),
) -> dict[str, Any] | ToolResult:
    """Updates a file's metadata or settings, including renaming, moving to a new parent folder, managing shared links, applying locks, updating tags, and modifying collection membership."""

    # Construct request model with validation
    try:
        _request = _models.PutFilesIdRequest(
            path=_models.PutFilesIdRequestPath(file_id=file_id),
            body=_models.PutFilesIdRequestBody(name=name, description=description, parent=parent, shared_link=shared_link, disposition_at=disposition_at, collections_=collections_, tags=tags,
                lock=_models.PutFilesIdRequestBodyLock(access=access, expires_at=expires_at, is_download_prevented=is_download_prevented) if any(v is not None for v in [access, expires_at, is_download_prevented]) else None,
                permissions=_models.PutFilesIdRequestBodyPermissions(can_download=can_download) if any(v is not None for v in [can_download]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}"
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

# Tags: Files
@mcp.tool(
    title="Delete File",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_file(file_id: str = Field(..., description="The unique identifier of the file to delete. Visible in the file's URL on the Box web application.")) -> dict[str, Any] | ToolResult:
    """Deletes a specified file from Box, either permanently or by moving it to the trash depending on enterprise settings."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFilesIdRequest(
            path=_models.DeleteFilesIdRequestPath(file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}"
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

# Tags: App item associations
@mcp.tool(
    title="List File App Item Associations",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_file_app_item_associations(
    file_id: str = Field(..., description="The unique identifier of the file whose app item associations should be retrieved. The file ID appears in the Box web app URL when viewing the file."),
    limit: str | None = Field(None, description="The maximum number of app item associations to return per page. Must be between 1 and 1000."),
    application_type: str | None = Field(None, description="Filters results to only include app items belonging to the specified application type. When omitted, associations for all application types are returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all app items associated with a file, including associations inherited from ancestor folders. Association type and ID are returned even if the requesting user lacks View permission on the app item."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetFilesIdAppItemAssociationsRequest(
            path=_models.GetFilesIdAppItemAssociationsRequestPath(file_id=file_id),
            query=_models.GetFilesIdAppItemAssociationsRequestQuery(limit=_limit, application_type=application_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_app_item_associations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/app_item_associations", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/app_item_associations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_app_item_associations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_app_item_associations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_app_item_associations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Downloads
@mcp.tool(
    title="Download File",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def download_file(
    file_id: str = Field(..., description="The unique identifier of the file to download. Visible in the Box web app URL when viewing the file."),
    version: str | None = Field(None, description="The specific version ID of the file to download. If omitted, the latest version is returned."),
    range_: str | None = Field(None, alias="range", description="Specifies a partial byte range of the file to download, using the format bytes={start_byte}-{end_byte}. Useful for resumable downloads or streaming large files."),
    boxapi: str | None = Field(None, description="The shared link URL and optional password for accessing a file that has not been explicitly shared with the authenticated user. Use the format shared_link=[link] or shared_link=[link]&shared_link_password=[password] for password-protected links."),
) -> dict[str, Any] | ToolResult:
    """Downloads the binary content of a file from Box. Supports partial downloads via byte ranges, specific version retrieval, and access to shared link items."""

    # Construct request model with validation
    try:
        _request = _models.GetFilesIdContentRequest(
            path=_models.GetFilesIdContentRequestPath(file_id=file_id),
            query=_models.GetFilesIdContentRequestQuery(version=version),
            header=_models.GetFilesIdContentRequestHeader(range_=range_, boxapi=boxapi)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for download_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/content", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/content"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

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

# Tags: Uploads
@mcp.tool(
    title="Upload File Version",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def upload_file_version(
    file_id: str = Field(..., description="The unique identifier of the file to update. Visible in the Box web app URL when viewing the file."),
    name: str | None = Field(None, description="An optional new name to rename the file when this new version is uploaded. If omitted, the existing file name is retained."),
    content_modified_at: str | None = Field(None, description="The date and time the file content was last modified, in ISO 8601 format. If omitted, the time of upload is used as the modification time."),
    file_: str | None = Field(None, alias="file", description="Base64-encoded file content for upload. The binary content of the file to upload. This part must appear after the attributes part in the multipart request body; reversing the order will result in a 400 error.", json_schema_extra={'format': 'byte'}),
) -> dict[str, Any] | ToolResult:
    """Uploads a new version of an existing file's content, optionally renaming it or setting a custom last-modified timestamp. For files over 50MB, use the Chunk Upload APIs instead."""

    # Construct request model with validation
    try:
        _request = _models.PostFilesIdContentRequest(
            path=_models.PostFilesIdContentRequestPath(file_id=file_id),
            body=_models.PostFilesIdContentRequestBody(file_=file_,
                attributes=_models.PostFilesIdContentRequestBodyAttributes(name=name, content_modified_at=content_modified_at) if any(v is not None for v in [name, content_modified_at]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_file_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/content", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/content"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_file_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_file_version", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_file_version",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Uploads
@mcp.tool(
    title="Upload File",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def upload_file(
    name: str | None = Field(None, description="The name to assign to the uploaded file. Must be unique (case-insensitive) within the destination folder."),
    id_: str | None = Field(None, alias="id", description="The ID of the parent folder where the file will be uploaded. Use `0` to upload to the user's root folder."),
    content_created_at: str | None = Field(None, description="The original creation timestamp of the file in ISO 8601 format. Defaults to the upload time if not provided."),
    content_modified_at: str | None = Field(None, description="The last modified timestamp of the file in ISO 8601 format. Defaults to the upload time if not provided."),
    file_: str | None = Field(None, alias="file", description="Base64-encoded file content for upload. The binary content of the file to upload. Must appear after the attributes part in the multipart request body.", json_schema_extra={'format': 'byte'}),
) -> dict[str, Any] | ToolResult:
    """Uploads a small file (under 50MB) to a specified Box folder. The attributes must be sent before the file content in the request body, or a 400 error will be returned."""

    # Construct request model with validation
    try:
        _request = _models.PostFilesContentRequest(
            body=_models.PostFilesContentRequestBody(file_=file_,
                attributes=_models.PostFilesContentRequestBodyAttributes(name=name, content_created_at=content_created_at, content_modified_at=content_modified_at,
                    parent=_models.PostFilesContentRequestBodyAttributesParent(id_=id_) if any(v is not None for v in [id_]) else None) if any(v is not None for v in [name, id_, content_created_at, content_modified_at]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/files/content"
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
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Uploads (Chunked)
@mcp.tool(
    title="Create Upload Session",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_upload_session(
    folder_id: str | None = Field(None, description="The ID of the destination folder where the new file will be stored upon upload completion."),
    file_name: str | None = Field(None, description="The name to assign to the new file once the upload session is complete."),
) -> dict[str, Any] | ToolResult:
    """Initiates a chunked upload session for uploading a new file, returning a session ID and upload URLs to use for subsequent chunk uploads."""

    # Construct request model with validation
    try:
        _request = _models.PostFilesUploadSessionsRequest(
            body=_models.PostFilesUploadSessionsRequestBody(folder_id=folder_id, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_upload_session: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/files/upload_sessions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_upload_session")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_upload_session", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_upload_session",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Uploads (Chunked)
@mcp.tool(
    title="Create File Upload Session",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_file_upload_session(
    file_id: str = Field(..., description="The unique identifier of the existing file for which the upload session will be created. The file ID can be found in the file's URL in the Box web application."),
    file_name: str | None = Field(None, description="An optional new name to assign to the file upon completing the upload session, replacing the current file name."),
) -> dict[str, Any] | ToolResult:
    """Creates a chunked upload session for an existing file, enabling large file uploads to be split into multiple parts. Use the returned session to upload individual chunks and complete the upload."""

    # Construct request model with validation
    try:
        _request = _models.PostFilesIdUploadSessionsRequest(
            path=_models.PostFilesIdUploadSessionsRequestPath(file_id=file_id),
            body=_models.PostFilesIdUploadSessionsRequestBody(file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_file_upload_session: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/upload_sessions", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/upload_sessions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_file_upload_session")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_file_upload_session", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_file_upload_session",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Uploads (Chunked)
@mcp.tool(
    title="Get Upload Session",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_upload_session(upload_session_id: str = Field(..., description="The unique identifier of the upload session to retrieve, obtained when the upload session was created.")) -> dict[str, Any] | ToolResult:
    """Retrieve the current status and details of an active chunked file upload session. The upload session ID is obtained from the Create upload session endpoint."""

    # Construct request model with validation
    try:
        _request = _models.GetFilesUploadSessionsIdRequest(
            path=_models.GetFilesUploadSessionsIdRequestPath(upload_session_id=upload_session_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_upload_session: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/upload_sessions/{upload_session_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/upload_sessions/{upload_session_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_upload_session")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_upload_session", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_upload_session",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Uploads (Chunked)
@mcp.tool(
    title="Upload File Part",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def upload_file_part(
    upload_session_id: str = Field(..., description="The unique identifier of the upload session to which this file part belongs."),
    digest: str = Field(..., description="The RFC 3230 message digest of the uploaded chunk used to verify integrity. Must be a base64-encoded SHA1 hash formatted as `sha=<BASE64_ENCODED_DIGEST>`."),
    content_range: str = Field(..., alias="content-range", description="The inclusive byte range of this chunk within the full file, formatted as `bytes <start>-<end>/<total>`. The start must be a multiple of the session's part size, the end must be a multiple of the part size minus one, and ranges must not overlap with any previously uploaded part."),
    body: str | None = Field(None, description="Base64-encoded binary request body. The raw binary content of the file chunk being uploaded for this part.", json_schema_extra={'format': 'byte'}),
) -> dict[str, Any] | ToolResult:
    """Uploads a single binary chunk of a file as part of an active chunked upload session. Each part must conform to the byte range and part size defined when the upload session was created."""

    # Construct request model with validation
    try:
        _request = _models.PutFilesUploadSessionsIdRequest(
            path=_models.PutFilesUploadSessionsIdRequestPath(upload_session_id=upload_session_id),
            header=_models.PutFilesUploadSessionsIdRequestHeader(digest=digest, content_range=content_range),
            body=_models.PutFilesUploadSessionsIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_file_part: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/upload_sessions/{upload_session_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/upload_sessions/{upload_session_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/octet-stream"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_file_part")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_file_part", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_file_part",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/octet-stream",
        whole_body_base64=True,
        headers=_http_headers,
    )

    return _response_data

# Tags: Uploads (Chunked)
@mcp.tool(
    title="Abort Upload Session",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def abort_upload_session(upload_session_id: str = Field(..., description="The unique identifier of the upload session to abort, as returned by the Create or Get upload session endpoints.")) -> dict[str, Any] | ToolResult:
    """Permanently aborts an active upload session and discards all uploaded data. This action is irreversible and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFilesUploadSessionsIdRequest(
            path=_models.DeleteFilesUploadSessionsIdRequestPath(upload_session_id=upload_session_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for abort_upload_session: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/upload_sessions/{upload_session_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/upload_sessions/{upload_session_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("abort_upload_session")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("abort_upload_session", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="abort_upload_session",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Uploads (Chunked)
@mcp.tool(
    title="List Upload Session Parts",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_upload_session_parts(
    upload_session_id: str = Field(..., description="The unique identifier of the upload session whose uploaded parts you want to list."),
    offset: str | None = Field(None, description="The zero-based index of the first item to return, enabling pagination through large result sets. Must not exceed 10000; requests beyond this limit will be rejected with a 400 error."),
    limit: str | None = Field(None, description="The maximum number of uploaded parts to return in a single response. Accepts values up to 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all file chunks uploaded so far within a specific upload session, allowing you to track multipart upload progress."""

    _offset = _parse_int(offset)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetFilesUploadSessionsIdPartsRequest(
            path=_models.GetFilesUploadSessionsIdPartsRequestPath(upload_session_id=upload_session_id),
            query=_models.GetFilesUploadSessionsIdPartsRequestQuery(offset=_offset, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_upload_session_parts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/upload_sessions/{upload_session_id}/parts", _request.path.model_dump(by_alias=True)) if _request.path else "/files/upload_sessions/{upload_session_id}/parts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_upload_session_parts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_upload_session_parts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_upload_session_parts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Uploads (Chunked)
@mcp.tool(
    title="Commit Upload Session",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def commit_upload_session(
    upload_session_id: str = Field(..., description="The unique identifier of the upload session to commit."),
    digest: str = Field(..., description="The RFC 3230 message digest of the entire file used to verify integrity. Must be a Base64-encoded SHA1 hash formatted as `sha=<BASE64_ENCODED_DIGEST>`."),
    parts: list[_models.UploadPart] | None = Field(None, description="An ordered list of part details representing all uploaded chunks that should be assembled into the final file. Each item should describe a previously uploaded part."),
) -> dict[str, Any] | ToolResult:
    """Finalizes an upload session by assembling all uploaded chunks into a complete file. Must be called after all parts have been uploaded to close the session and persist the file."""

    # Construct request model with validation
    try:
        _request = _models.PostFilesUploadSessionsIdCommitRequest(
            path=_models.PostFilesUploadSessionsIdCommitRequestPath(upload_session_id=upload_session_id),
            header=_models.PostFilesUploadSessionsIdCommitRequestHeader(digest=digest),
            body=_models.PostFilesUploadSessionsIdCommitRequestBody(parts=parts)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for commit_upload_session: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/upload_sessions/{upload_session_id}/commit", _request.path.model_dump(by_alias=True)) if _request.path else "/files/upload_sessions/{upload_session_id}/commit"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("commit_upload_session")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("commit_upload_session", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="commit_upload_session",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Files
@mcp.tool(
    title="Copy File",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def copy_file(
    file_id: str = Field(..., description="The unique identifier of the file to copy. Visible in the Box web app URL when viewing the file."),
    name: str | None = Field(None, description="An optional new name for the copied file. Must not exceed 255 characters; non-printable ASCII characters, forward/backward slashes, and reserved names like '.' and '..' are automatically sanitized.", max_length=255),
    version: str | None = Field(None, description="The ID of a specific file version to copy. If omitted, the latest version of the file is copied."),
    id_: str | None = Field(None, alias="id", description="The ID of the destination folder where the copied file will be placed. Use '0' to copy the file to the root folder."),
) -> dict[str, Any] | ToolResult:
    """Creates a copy of an existing file, optionally placing it in a different folder, renaming it, or copying a specific version. Returns the metadata of the newly created file copy."""

    # Construct request model with validation
    try:
        _request = _models.PostFilesIdCopyRequest(
            path=_models.PostFilesIdCopyRequestPath(file_id=file_id),
            body=_models.PostFilesIdCopyRequestBody(name=name, version=version,
                parent=_models.PostFilesIdCopyRequestBodyParent(id_=id_) if any(v is not None for v in [id_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for copy_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/copy", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/copy"
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
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Files
@mcp.tool(
    title="Get File Thumbnail",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_file_thumbnail(
    file_id: str = Field(..., description="The unique identifier of the file for which to retrieve a thumbnail. The file ID can be found in the URL when viewing the file in the Box web application."),
    extension: Literal["png", "jpg"] = Field(..., description="The image format for the thumbnail. PNG supports sizes up to 256x256; JPG supports sizes up to 320x320."),
    min_height: int | None = Field(None, description="The minimum desired height of the thumbnail in pixels. The returned thumbnail will be at least this tall, within the supported size range of 32 to 320 pixels.", ge=32, le=320),
    min_width: int | None = Field(None, description="The minimum desired width of the thumbnail in pixels. The returned thumbnail will be at least this wide, within the supported size range of 32 to 320 pixels.", ge=32, le=320),
    max_height: int | None = Field(None, description="The maximum desired height of the thumbnail in pixels. The returned thumbnail will not exceed this height, within the supported size range of 32 to 320 pixels.", ge=32, le=320),
    max_width: int | None = Field(None, description="The maximum desired width of the thumbnail in pixels. The returned thumbnail will not exceed this width, within the supported size range of 32 to 320 pixels.", ge=32, le=320),
) -> dict[str, Any] | ToolResult:
    """Retrieves a scaled-down thumbnail image of a file in PNG or JPG format. Supports various sizes for image and video file types."""

    # Construct request model with validation
    try:
        _request = _models.GetFilesIdThumbnailIdRequest(
            path=_models.GetFilesIdThumbnailIdRequestPath(file_id=file_id, extension=extension),
            query=_models.GetFilesIdThumbnailIdRequestQuery(min_height=min_height, min_width=min_width, max_height=max_height, max_width=max_width)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_thumbnail: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/thumbnail.{extension}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/thumbnail.{extension}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_thumbnail")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_thumbnail", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_thumbnail",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collaborations (List)
@mcp.tool(
    title="List File Collaborations",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_file_collaborations(
    file_id: str = Field(..., description="The unique identifier of the file whose collaborations you want to retrieve. You can find this ID in the file's URL in the Box web application."),
    limit: str | None = Field(None, description="The maximum number of collaboration records to return per page. Accepts values up to 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all pending and active collaborations for a specific file, including users who currently have access or have been invited to collaborate."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetFilesIdCollaborationsRequest(
            path=_models.GetFilesIdCollaborationsRequestPath(file_id=file_id),
            query=_models.GetFilesIdCollaborationsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_collaborations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/collaborations", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/collaborations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_collaborations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_collaborations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_collaborations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool(
    title="List File Comments",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_file_comments(
    file_id: str = Field(..., description="The unique identifier of the file whose comments you want to retrieve. Find this ID in the file's URL on the Box web application."),
    limit: str | None = Field(None, description="The maximum number of comments to return per page. Must be between 1 and 1000."),
    offset: str | None = Field(None, description="The zero-based index of the first item to include in the response, used for paginating through results. Offset values exceeding 10000 are not supported."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of comments posted on a specific file. Useful for reviewing user feedback or discussion threads associated with a file."""

    _limit = _parse_int(limit)
    _offset = _parse_int(offset)

    # Construct request model with validation
    try:
        _request = _models.GetFilesIdCommentsRequest(
            path=_models.GetFilesIdCommentsRequestPath(file_id=file_id),
            query=_models.GetFilesIdCommentsRequestQuery(limit=_limit, offset=_offset)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/comments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_comments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_comments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_comments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tasks
@mcp.tool(
    title="List File Tasks",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_file_tasks(file_id: str = Field(..., description="The unique identifier of the file whose tasks you want to retrieve. You can find this ID in the file's URL in the Box web application.")) -> dict[str, Any] | ToolResult:
    """Retrieves all tasks associated with a specific file, returning the complete list in a single response. Note that this endpoint does not support pagination."""

    # Construct request model with validation
    try:
        _request = _models.GetFilesIdTasksRequest(
            path=_models.GetFilesIdTasksRequestPath(file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/tasks"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_tasks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_tasks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Trashed files
@mcp.tool(
    title="Get Trashed File",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_trashed_file(file_id: str = Field(..., description="The unique identifier of the file to retrieve from the trash. The file ID appears in the Box web app URL when viewing the file.")) -> dict[str, Any] | ToolResult:
    """Retrieves metadata for a file that was directly moved to the trash. Note: if a parent folder was trashed instead, use the trashed folder endpoint to inspect it."""

    # Construct request model with validation
    try:
        _request = _models.GetFilesIdTrashRequest(
            path=_models.GetFilesIdTrashRequestPath(file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_trashed_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/trash", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/trash"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_trashed_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_trashed_file", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_trashed_file",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Trashed files
@mcp.tool(
    title="Permanently Delete Trashed File",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def permanently_delete_trashed_file(file_id: str = Field(..., description="The unique identifier of the trashed file to permanently delete. The file ID can be found in the URL when viewing the file in the Box web application.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a file that is currently in the trash, freeing storage and removing it from Box entirely. This action is irreversible and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFilesIdTrashRequest(
            path=_models.DeleteFilesIdTrashRequestPath(file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for permanently_delete_trashed_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/trash", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/trash"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("permanently_delete_trashed_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("permanently_delete_trashed_file", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="permanently_delete_trashed_file",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: File versions
@mcp.tool(
    title="List File Versions",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_file_versions(
    file_id: str = Field(..., description="The unique identifier of the file whose version history you want to retrieve. The file ID can be found in the URL when viewing the file in the Box web application."),
    limit: str | None = Field(None, description="The maximum number of file versions to return per page. Accepts values up to 1000."),
    offset: str | None = Field(None, description="The zero-based index of the item at which to start the response, used for paginating through results. Offset values exceeding 10000 will result in a 400 error."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the version history of a specific file, returning all past versions in paginated results. Version tracking is available only for Box premium accounts; use the get_file operation to retrieve the current version ID."""

    _limit = _parse_int(limit)
    _offset = _parse_int(offset)

    # Construct request model with validation
    try:
        _request = _models.GetFilesIdVersionsRequest(
            path=_models.GetFilesIdVersionsRequestPath(file_id=file_id),
            query=_models.GetFilesIdVersionsRequestQuery(limit=_limit, offset=_offset)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_versions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/versions", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/versions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_versions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_versions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_versions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: File versions
@mcp.tool(
    title="Get File Version",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_file_version(
    file_id: str = Field(..., description="The unique identifier of the file whose version you want to retrieve. Visible in the file's URL in the Box web application."),
    file_version_id: str = Field(..., description="The unique identifier of the specific file version to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves metadata for a specific version of a file by its version ID. Version history is only available for Box accounts with premium subscriptions."""

    # Construct request model with validation
    try:
        _request = _models.GetFilesIdVersionsIdRequest(
            path=_models.GetFilesIdVersionsIdRequestPath(file_id=file_id, file_version_id=file_version_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/versions/{file_version_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/versions/{file_version_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_version", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_version",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: File versions
@mcp.tool(
    title="Restore File Version",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def restore_file_version(
    file_id: str = Field(..., description="The unique identifier of the file whose version you want to restore. Visible in the file's URL in the Box web application."),
    file_version_id: str = Field(..., description="The unique identifier of the specific file version to restore."),
) -> dict[str, Any] | ToolResult:
    """Restores a previously deleted version of a file, making it the current version. Supports standard file formats such as PDF, DOC, and PPTX, but not Box Notes."""

    # Construct request model with validation
    try:
        _request = _models.PutFilesIdVersionsIdRequest(
            path=_models.PutFilesIdVersionsIdRequestPath(file_id=file_id, file_version_id=file_version_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for restore_file_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/versions/{file_version_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/versions/{file_version_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("restore_file_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("restore_file_version", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="restore_file_version",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: File versions
@mcp.tool(
    title="Delete File Version",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_file_version(
    file_id: str = Field(..., description="The unique identifier of the file whose version will be deleted. The file ID can be found in the URL when viewing the file in the Box web application."),
    file_version_id: str = Field(..., description="The unique identifier of the specific file version to delete. This targets a single version entry within the file's version history."),
) -> dict[str, Any] | ToolResult:
    """Moves a specific version of a file to the trash, effectively removing it from the version history. Version tracking is only available for Box accounts with premium subscriptions."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFilesIdVersionsIdRequest(
            path=_models.DeleteFilesIdVersionsIdRequestPath(file_id=file_id, file_version_id=file_version_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_file_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/versions/{file_version_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/versions/{file_version_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_file_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_file_version", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_file_version",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: File versions
@mcp.tool(
    title="Promote File Version",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def promote_file_version(
    file_id: str = Field(..., description="The unique identifier of the file whose version you want to promote. Visible in the file's URL in the Box web application."),
    id_: str | None = Field(None, alias="id", description="The unique identifier of the specific file version to promote to the top of the version history."),
    type_: Literal["file_version"] | None = Field(None, alias="type", description="The resource type being promoted. Must be set to 'file_version' to indicate a file version promotion."),
) -> dict[str, Any] | ToolResult:
    """Promotes an older version of a file to the top of its version history by creating a new copy with the same contents, hash, etag, and name. Suitable for file formats like PDF, DOC, and PPTX, but not for Box Notes."""

    # Construct request model with validation
    try:
        _request = _models.PostFilesIdVersionsCurrentRequest(
            path=_models.PostFilesIdVersionsCurrentRequestPath(file_id=file_id),
            body=_models.PostFilesIdVersionsCurrentRequestBody(id_=id_, type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for promote_file_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/versions/current", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/versions/current"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("promote_file_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("promote_file_version", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="promote_file_version",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata instances (Files)
@mcp.tool(
    title="List File Metadata",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_file_metadata(
    file_id: str = Field(..., description="The unique identifier of the file whose metadata instances will be retrieved. The file ID can be found in the URL when viewing the file in the Box web application."),
    view: str | None = Field(None, description="Controls how taxonomy field values are represented in the response. When set to 'hydrated', taxonomy values include full taxonomy node details rather than just node identifiers."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all metadata instances attached to a specific file. Optionally returns full taxonomy node details instead of node identifiers."""

    # Construct request model with validation
    try:
        _request = _models.GetFilesIdMetadataRequest(
            path=_models.GetFilesIdMetadataRequestPath(file_id=file_id),
            query=_models.GetFilesIdMetadataRequestQuery(view=view)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/metadata", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/metadata"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_metadata", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_metadata",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Classifications on files
@mcp.tool(
    title="Get File Classification",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_file_classification(file_id: str = Field(..., description="The unique identifier of the file whose security classification you want to retrieve. Visible in the file's Box web URL after '/files/'.")) -> dict[str, Any] | ToolResult:
    """Retrieves the security classification metadata applied to a specific file. Returns the classification instance associated with the file's enterprise security policy."""

    # Construct request model with validation
    try:
        _request = _models.GetFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest(
            path=_models.GetFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath(file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_classification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/metadata/enterprise/securityClassification-6VMVochwUWo", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/metadata/enterprise/securityClassification-6VMVochwUWo"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_classification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_classification", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_classification",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Classifications on files
@mcp.tool(
    title="Add File Classification",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def add_file_classification(
    file_id: str = Field(..., description="The unique identifier of the file to classify. The file ID can be found in the file's URL in the Box web application."),
    box__security__classification__key: str | None = Field(None, alias="Box__Security__Classification__Key", description="The classification label to apply to the file. Must match one of the available classification keys defined in the enterprise's classification template; retrieve valid keys from the classification template endpoint."),
) -> dict[str, Any] | ToolResult:
    """Adds a security classification label to a file in Box. Use this to apply an enterprise-defined classification (e.g., Confidential, Sensitive) to control how the file is handled and shared."""

    # Construct request model with validation
    try:
        _request = _models.PostFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest(
            path=_models.PostFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath(file_id=file_id),
            body=_models.PostFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestBody(box__security__classification__key=box__security__classification__key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_file_classification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/metadata/enterprise/securityClassification-6VMVochwUWo", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/metadata/enterprise/securityClassification-6VMVochwUWo"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_file_classification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_file_classification", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_file_classification",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Classifications on files
@mcp.tool(
    title="Update File Classification",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_file_classification(
    file_id: str = Field(..., description="The unique identifier of the file whose classification will be updated. The file ID can be found in the file's URL in the Box web application."),
    body: list[_models.PutFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoBodyItem] | None = Field(None, description="A list containing exactly one change operation object that specifies the update to apply to the classification label. Order is significant; only a single item describing the classification change should be included."),
) -> dict[str, Any] | ToolResult:
    """Updates the security classification label on a file that already has a classification applied. Only classification values defined for the enterprise are accepted."""

    # Construct request model with validation
    try:
        _request = _models.PutFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest(
            path=_models.PutFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath(file_id=file_id),
            body=_models.PutFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_file_classification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/metadata/enterprise/securityClassification-6VMVochwUWo", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/metadata/enterprise/securityClassification-6VMVochwUWo"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/json-patch+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_file_classification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_file_classification", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_file_classification",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json-patch+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Classifications on files
@mcp.tool(
    title="Remove File Classification",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_file_classification(file_id: str = Field(..., description="The unique identifier of the file from which the classification will be removed. The file ID can be found in the URL when viewing the file in the Box web application.")) -> dict[str, Any] | ToolResult:
    """Removes any existing security classification from a specified file. This permanently strips the classification metadata, and can also be called using an explicit enterprise ID in the endpoint path."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest(
            path=_models.DeleteFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath(file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_file_classification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/metadata/enterprise/securityClassification-6VMVochwUWo", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/metadata/enterprise/securityClassification-6VMVochwUWo"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_file_classification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_file_classification", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_file_classification",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata instances (Files)
@mcp.tool(
    title="Get File Metadata Instance",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_file_metadata_instance(
    file_id: str = Field(..., description="The unique identifier of the file whose metadata instance you want to retrieve. Find this ID in the file's URL in the Box web application."),
    scope: Literal["global", "enterprise"] = Field(..., description="The scope of the metadata template to retrieve, either globally available templates or templates specific to your enterprise."),
    template_key: str = Field(..., description="The unique key name of the metadata template whose instance you want to retrieve from the file."),
    view: str | None = Field(None, description="Controls how taxonomy field values are represented in the response. Set to 'hydrated' to receive full taxonomy node details instead of the default node identifiers."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific metadata template instance applied to a file, identified by its scope and template key. Optionally returns full taxonomy node details instead of raw node identifiers."""

    # Construct request model with validation
    try:
        _request = _models.GetFilesIdMetadataIdIdRequest(
            path=_models.GetFilesIdMetadataIdIdRequestPath(file_id=file_id, scope=scope, template_key=template_key),
            query=_models.GetFilesIdMetadataIdIdRequestQuery(view=view)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_metadata_instance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/metadata/{scope}/{template_key}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/metadata/{scope}/{template_key}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_metadata_instance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_metadata_instance", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_metadata_instance",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata instances (Files)
@mcp.tool(
    title="Create File Metadata",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_file_metadata(
    file_id: str = Field(..., description="The unique identifier of the file to which the metadata instance will be applied. Visible in the file's URL in the Box web application."),
    scope: Literal["global", "enterprise"] = Field(..., description="The scope of the metadata template to apply, either global (Box-provided templates) or enterprise (custom templates defined by your organization)."),
    template_key: str = Field(..., description="The unique key identifying the metadata template within the given scope, corresponding to the template's defined name."),
    body: dict[str, Any] | None = Field(None, description="A JSON object containing the metadata field key-value pairs to populate on the template instance. Keys must match those defined in the template, unless using the global.properties template."),
) -> dict[str, Any] | ToolResult:
    """Applies an instance of a metadata template to a file, associating structured key-value data with it. Only keys defined in the specified template are accepted, except for the global.properties template which allows arbitrary key-value pairs."""

    # Construct request model with validation
    try:
        _request = _models.PostFilesIdMetadataIdIdRequest(
            path=_models.PostFilesIdMetadataIdIdRequestPath(file_id=file_id, scope=scope, template_key=template_key),
            body=_models.PostFilesIdMetadataIdIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_file_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/metadata/{scope}/{template_key}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/metadata/{scope}/{template_key}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_file_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_file_metadata", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_file_metadata",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata instances (Files)
@mcp.tool(
    title="Update File Metadata",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_file_metadata(
    file_id: str = Field(..., description="The unique identifier of the file whose metadata instance will be updated. Visible in the file's URL in the Box web application."),
    scope: Literal["global", "enterprise"] = Field(..., description="The scope of the metadata template to update, either globally defined templates or enterprise-specific ones."),
    template_key: str = Field(..., description="The unique key identifying the metadata template whose instance will be updated on the file."),
    body: list[_models.PutFilesIdMetadataIdIdBodyItem] | None = Field(None, description="An ordered array of JSON Patch operation objects describing the changes to apply to the metadata instance. Operations are applied in sequence and must conform to RFC 6902 JSON Patch syntax."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing metadata instance on a file using JSON Patch operations. The metadata template must already be applied to the file, and all changes are applied atomically — if any operation fails, no changes are made."""

    # Construct request model with validation
    try:
        _request = _models.PutFilesIdMetadataIdIdRequest(
            path=_models.PutFilesIdMetadataIdIdRequestPath(file_id=file_id, scope=scope, template_key=template_key),
            body=_models.PutFilesIdMetadataIdIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_file_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/metadata/{scope}/{template_key}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/metadata/{scope}/{template_key}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/json-patch+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_file_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_file_metadata", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_file_metadata",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json-patch+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata instances (Files)
@mcp.tool(
    title="Delete File Metadata",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_file_metadata(
    file_id: str = Field(..., description="The unique identifier of the file from which metadata will be removed. The file ID can be found in the URL when viewing the file in the Box web application."),
    scope: Literal["global", "enterprise"] = Field(..., description="The scope of the metadata template to delete, either 'global' for Box-wide templates or 'enterprise' for templates specific to your organization."),
    template_key: str = Field(..., description="The unique key identifying the metadata template to remove from the file, corresponding to the template's defined key within the specified scope."),
) -> dict[str, Any] | ToolResult:
    """Removes a specific metadata instance from a file by deleting the metadata template applied under the given scope. This permanently detaches the metadata from the file without affecting the file itself."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFilesIdMetadataIdIdRequest(
            path=_models.DeleteFilesIdMetadataIdIdRequestPath(file_id=file_id, scope=scope, template_key=template_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_file_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/metadata/{scope}/{template_key}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/metadata/{scope}/{template_key}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_file_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_file_metadata", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_file_metadata",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Skills
@mcp.tool(
    title="List File Skills Cards",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_file_skills_cards(file_id: str = Field(..., description="The unique identifier of the file whose Box Skills cards you want to retrieve. Visible in the file's URL on the Box web application.")) -> dict[str, Any] | ToolResult:
    """Retrieves all Box Skills metadata cards attached to a specific file. Useful for inspecting AI-generated insights such as transcripts, topics, or keywords extracted by Box Skills."""

    # Construct request model with validation
    try:
        _request = _models.GetFilesIdMetadataGlobalBoxSkillsCardsRequest(
            path=_models.GetFilesIdMetadataGlobalBoxSkillsCardsRequestPath(file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_skills_cards: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/metadata/global/boxSkillsCards", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/metadata/global/boxSkillsCards"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_skills_cards")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_skills_cards", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_skills_cards",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Skills
@mcp.tool(
    title="Create Skill Cards",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_skill_cards(
    file_id: str = Field(..., description="The unique identifier of the file to which Box Skill cards will be applied. The file ID can be found in the URL when viewing the file in the Box web application."),
    cards: list[_models.SkillCard] | None = Field(None, description="An array of Box Skill card objects to attach to the file. Each item should represent a valid skill card type (e.g., keyword, transcript, timeline, or status card); order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Applies one or more Box Skills metadata cards to a specified file, enabling AI-generated insights such as transcripts, topics, or keywords to be attached as structured metadata."""

    # Construct request model with validation
    try:
        _request = _models.PostFilesIdMetadataGlobalBoxSkillsCardsRequest(
            path=_models.PostFilesIdMetadataGlobalBoxSkillsCardsRequestPath(file_id=file_id),
            body=_models.PostFilesIdMetadataGlobalBoxSkillsCardsRequestBody(cards=cards)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_skill_cards: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/metadata/global/boxSkillsCards", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/metadata/global/boxSkillsCards"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_skill_cards")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_skill_cards", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_skill_cards",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Skills
@mcp.tool(
    title="Update Skill Cards",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_skill_cards(
    file_id: str = Field(..., description="The unique identifier of the file whose Box Skills metadata cards will be updated. Visible in the file's URL on the Box web application."),
    body: list[_models.PutFilesIdMetadataGlobalBoxSkillsCardsBodyItem] | None = Field(None, description="An array of JSON-Patch operation objects describing the changes to apply to the Box Skills metadata cards. Each object follows the RFC 6902 JSON-Patch specification, with order of operations being significant."),
) -> dict[str, Any] | ToolResult:
    """Updates one or more Box Skills metadata cards on a specified file using JSON-Patch operations, allowing targeted modifications to existing skill card data."""

    # Construct request model with validation
    try:
        _request = _models.PutFilesIdMetadataGlobalBoxSkillsCardsRequest(
            path=_models.PutFilesIdMetadataGlobalBoxSkillsCardsRequestPath(file_id=file_id),
            body=_models.PutFilesIdMetadataGlobalBoxSkillsCardsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_skill_cards: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/metadata/global/boxSkillsCards", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/metadata/global/boxSkillsCards"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/json-patch+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_skill_cards")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_skill_cards", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_skill_cards",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json-patch+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Skills
@mcp.tool(
    title="Remove File Skills Cards",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_file_skills_cards(file_id: str = Field(..., description="The unique identifier of the file from which Box Skills cards will be removed. The file ID can be found in the file's URL in the Box web application.")) -> dict[str, Any] | ToolResult:
    """Removes all Box Skills cards metadata from a specified file. This clears any AI-generated skill annotations (such as transcripts, topics, or faces) associated with the file."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFilesIdMetadataGlobalBoxSkillsCardsRequest(
            path=_models.DeleteFilesIdMetadataGlobalBoxSkillsCardsRequestPath(file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_file_skills_cards: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/metadata/global/boxSkillsCards", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/metadata/global/boxSkillsCards"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_file_skills_cards")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_file_skills_cards", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_file_skills_cards",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Watermarks (Files)
@mcp.tool(
    title="Get File Watermark",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_file_watermark(file_id: str = Field(..., description="The unique identifier of the file whose watermark you want to retrieve. Visible in the file's URL on the Box web application.")) -> dict[str, Any] | ToolResult:
    """Retrieves the watermark applied to a specific file. Returns watermark details if one exists, or an error if no watermark has been applied."""

    # Construct request model with validation
    try:
        _request = _models.GetFilesIdWatermarkRequest(
            path=_models.GetFilesIdWatermarkRequestPath(file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_watermark: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/watermark", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/watermark"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_watermark")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_watermark", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_watermark",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Watermarks (Files)
@mcp.tool(
    title="Apply File Watermark",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def apply_file_watermark(
    file_id: str = Field(..., description="The unique identifier of the file to watermark. Found in the file's URL in the Box web application."),
    imprint: Literal["default"] | None = Field(None, description="The type of watermark to apply to the file. Currently only the default imprint style is supported."),
) -> dict[str, Any] | ToolResult:
    """Applies or updates a watermark on a specified file in Box. Use this to protect file content by overlaying a visible watermark when the file is viewed or downloaded."""

    # Construct request model with validation
    try:
        _request = _models.PutFilesIdWatermarkRequest(
            path=_models.PutFilesIdWatermarkRequestPath(file_id=file_id),
            body=_models.PutFilesIdWatermarkRequestBody(watermark=_models.PutFilesIdWatermarkRequestBodyWatermark(imprint=imprint) if any(v is not None for v in [imprint]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for apply_file_watermark: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/watermark", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/watermark"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("apply_file_watermark")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("apply_file_watermark", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="apply_file_watermark",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Watermarks (Files)
@mcp.tool(
    title="Remove File Watermark",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_file_watermark(file_id: str = Field(..., description="The unique identifier of the file from which the watermark will be removed. Found in the file's URL in the Box web application.")) -> dict[str, Any] | ToolResult:
    """Removes an existing watermark from a specified file in Box. Use this to revoke watermark protection previously applied to a file."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFilesIdWatermarkRequest(
            path=_models.DeleteFilesIdWatermarkRequestPath(file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_file_watermark: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/watermark", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/watermark"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_file_watermark")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_file_watermark", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_file_watermark",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: File requests
@mcp.tool(
    title="Get File Request",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_file_request(file_request_id: str = Field(..., description="The unique identifier of the file request to retrieve. This ID can be found in the URL of the file request builder in the Box web application.")) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific file request, including its configuration and status. Use this to inspect an existing file request created via the Box web application."""

    # Construct request model with validation
    try:
        _request = _models.GetFileRequestsIdRequest(
            path=_models.GetFileRequestsIdRequestPath(file_request_id=file_request_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/file_requests/{file_request_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/file_requests/{file_request_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_request", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_request",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: File requests
@mcp.tool(
    title="Update File Request",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_file_request(
    file_request_id: str = Field(..., description="The unique identifier of the file request to update. Find this ID in the URL of the file request builder in the Box web application."),
    title: str | None = Field(None, description="The new title for the file request. If omitted, the existing title is preserved."),
    description: str | None = Field(None, description="The new description for the file request, displayed to submitters on the form. If omitted, the existing description is preserved."),
    status: Literal["active", "inactive"] | None = Field(None, description="The new status of the file request. Setting to 'inactive' stops accepting submissions and returns HTTP 404 to visitors; 'active' resumes acceptance. If omitted, the existing status is preserved."),
    is_email_required: bool | None = Field(None, description="Whether submitters must provide their email address on the file request form. If omitted, the existing setting is preserved."),
    is_description_required: bool | None = Field(None, description="Whether submitters must provide a description of the files they are uploading on the file request form. If omitted, the existing setting is preserved."),
    expires_at: str | None = Field(None, description="The expiration date and time after which the file request will no longer accept submissions and its status will automatically become inactive. Provide as an ISO 8601 date-time string. If omitted, the existing expiration is preserved."),
) -> dict[str, Any] | ToolResult:
    """Updates the properties of an existing file request, such as its title, description, status, and submission requirements. Use this to activate or deactivate a file request or modify its configuration."""

    # Construct request model with validation
    try:
        _request = _models.PutFileRequestsIdRequest(
            path=_models.PutFileRequestsIdRequestPath(file_request_id=file_request_id),
            body=_models.PutFileRequestsIdRequestBody(title=title, description=description, status=status, is_email_required=is_email_required, is_description_required=is_description_required, expires_at=expires_at)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_file_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/file_requests/{file_request_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/file_requests/{file_request_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_file_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_file_request", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_file_request",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: File requests
@mcp.tool(
    title="Delete File Request",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_file_request(file_request_id: str = Field(..., description="The unique identifier of the file request to delete. This ID can be found in the URL of the file request builder in the Box web application.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specified file request from Box. This action is irreversible and removes the file request and its associated upload link."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFileRequestsIdRequest(
            path=_models.DeleteFileRequestsIdRequestPath(file_request_id=file_request_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_file_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/file_requests/{file_request_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/file_requests/{file_request_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_file_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_file_request", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_file_request",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: File requests
@mcp.tool(
    title="Copy File Request",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def copy_file_request(
    file_request_id: str = Field(..., description="The unique identifier of the file request to copy. Find this ID in the URL when viewing a file request in the Box web application's file request builder."),
    body: _models.FileRequestCopyRequest | None = Field(None, description="The request body specifying the destination folder and any overrides to apply to the copied file request, such as a new title or description."),
) -> dict[str, Any] | ToolResult:
    """Copies an existing file request from one folder and applies it to another folder, duplicating its settings and configuration. Useful for reusing file request templates across multiple folders without manual recreation."""

    # Construct request model with validation
    try:
        _request = _models.PostFileRequestsIdCopyRequest(
            path=_models.PostFileRequestsIdCopyRequestPath(file_request_id=file_request_id),
            body=_models.PostFileRequestsIdCopyRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for copy_file_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/file_requests/{file_request_id}/copy", _request.path.model_dump(by_alias=True)) if _request.path else "/file_requests/{file_request_id}/copy"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("copy_file_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("copy_file_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="copy_file_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Folders
@mcp.tool(
    title="Get Folder",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_folder(
    folder_id: str = Field(..., description="The unique identifier of the folder to retrieve. The root folder of any Box account is always ID '0'; other folder IDs can be found in the URL when viewing the folder in the Box web app."),
    sort: Literal["id", "name", "date", "size"] | None = Field(None, description="The secondary attribute by which folder items are sorted. Items are always grouped by type first (folders, then files, then web links); this parameter controls ordering within those groups. Not supported for marker-based pagination on the root folder."),
    direction: Literal["ASC", "DESC"] | None = Field(None, description="The sort order for returned items, either ascending (ASC) or descending (DESC) alphabetically."),
    offset: str | None = Field(None, description="The zero-based index of the first item to include in the response, used for offset-based pagination. Note that very high offset values may be unreliable for large folders; consider restructuring large folders if pagination fails."),
    limit: str | None = Field(None, description="The maximum number of folder items to return in a single response, up to a maximum of 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves metadata and the first 100 items for a specified folder. Use the sort, direction, offset, and limit parameters to control item ordering and pagination within the folder."""

    _offset = _parse_int(offset)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetFoldersIdRequest(
            path=_models.GetFoldersIdRequestPath(folder_id=folder_id),
            query=_models.GetFoldersIdRequestQuery(sort=sort, direction=direction, offset=_offset, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Trashed folders
@mcp.tool(
    title="Restore Folder",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def restore_folder(
    folder_id: str = Field(..., description="The unique identifier of the folder to restore from trash. The folder ID can be found in the Box web app URL when viewing the folder."),
    name: str | None = Field(None, description="An optional new name to assign to the folder upon restoration, useful if a naming conflict exists at the destination."),
    parent: _models.PostFoldersIdBodyParent | None = Field(None, description="An optional parent folder object specifying where the folder should be restored to, used when the original parent folder no longer exists."),
) -> dict[str, Any] | ToolResult:
    """Restores a folder from the trash to its original location or an optional new parent folder. During the operation, the source folder, its descendants, and the destination folder are locked to prevent concurrent move, copy, delete, or restore actions."""

    # Construct request model with validation
    try:
        _request = _models.PostFoldersIdRequest(
            path=_models.PostFoldersIdRequestPath(folder_id=folder_id),
            body=_models.PostFoldersIdRequestBody(name=name, parent=parent)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for restore_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("restore_folder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("restore_folder", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="restore_folder",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Folders
@mcp.tool(
    title="Update Folder",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_folder(
    folder_id: str = Field(..., description="The unique identifier of the folder to update. Find this ID in the Box web app URL when viewing the folder. The root folder of any Box account always has the ID `0`."),
    name: str | None = Field(None, description="The new name for the folder. Names must be unique within the parent folder (case-insensitive) and cannot contain non-printable ASCII characters, forward or backward slashes, trailing spaces, or be `.` or `..`."),
    description: str | None = Field(None, description="An optional human-readable description for the folder, up to 256 characters.", max_length=256),
    sync_state: Literal["synced", "not_synced", "partially_synced"] | None = Field(None, description="Controls whether the folder is synced to a user's device. Applicable only to Box Sync (discontinued); not used by Box Drive."),
    can_non_owners_invite: bool | None = Field(None, description="When set to `true`, users who are not the folder owner are allowed to invite new collaborators. When `false`, only the owner can invite collaborators."),
    parent: _models.PutFoldersIdBodyParent | None = Field(None, description="The parent folder to move this folder into. Provide an object with the `id` of the destination parent folder to relocate the folder."),
    shared_link: _models.PutFoldersIdBodySharedLink | None = Field(None, description="Shared link settings for the folder. Provide a shared link object to create or update the shared link, or set to `null` to remove it."),
    folder_upload_email: _models.PutFoldersIdBodyFolderUploadEmail | None = Field(None, description="The email address configuration that allows files to be uploaded to this folder by sending an email. Provide an object with the desired access level, or set to `null` to disable."),
    tags: list[str] | None = Field(None, description="A list of tags to associate with the folder, visible in the Box web and mobile apps. To modify tags, retrieve the current list, apply changes, and submit the full updated list. Maximum of 100 tags per item.", min_length=1, max_length=100),
    is_collaboration_restricted_to_enterprise: bool | None = Field(None, description="When set to `true`, new collaboration invitations for this folder are restricted to users within the same enterprise. Existing collaborations are not affected."),
    collections_: list[_models.PutFoldersIdBodyCollectionsItem] | None = Field(None, alias="collections", description="A list of collection objects to add this folder to. Currently only the `favorites` collection is supported. Pass an empty array or `null` to remove the folder from all collections. Retrieve collection IDs using the List all collections endpoint."),
    can_non_owners_view_collaborators: bool | None = Field(None, description="When set to `false`, non-owner collaborators are prevented from viewing other collaborators on the folder and from inviting new ones. If setting this to `false`, `can_non_owners_invite` must also be set to `false`."),
) -> dict[str, Any] | ToolResult:
    """Updates a folder's properties such as name, description, tags, and sharing settings. Can also be used to move the folder to a new parent, manage shared links, and control collaboration permissions."""

    # Construct request model with validation
    try:
        _request = _models.PutFoldersIdRequest(
            path=_models.PutFoldersIdRequestPath(folder_id=folder_id),
            body=_models.PutFoldersIdRequestBody(name=name, description=description, sync_state=sync_state, can_non_owners_invite=can_non_owners_invite, parent=parent, shared_link=shared_link, folder_upload_email=folder_upload_email, tags=tags, is_collaboration_restricted_to_enterprise=is_collaboration_restricted_to_enterprise, collections_=collections_, can_non_owners_view_collaborators=can_non_owners_view_collaborators)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_folder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_folder", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_folder",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Folders
@mcp.tool(
    title="Delete Folder",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_folder(
    folder_id: str = Field(..., description="The unique identifier of the folder to delete. The folder ID can be found in the URL when viewing the folder in the Box web app, and the root folder is always ID `0`."),
    recursive: bool | None = Field(None, description="When set to true, allows deletion of a non-empty folder by recursively deleting all of its contents along with the folder itself. If omitted or false, the request will fail if the folder contains any items."),
) -> dict[str, Any] | ToolResult:
    """Deletes a Box folder either permanently or by moving it to the trash. Supports recursive deletion to remove folders that contain content."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFoldersIdRequest(
            path=_models.DeleteFoldersIdRequestPath(folder_id=folder_id),
            query=_models.DeleteFoldersIdRequestQuery(recursive=recursive)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: App item associations
@mcp.tool(
    title="List Folder App Item Associations",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_folder_app_item_associations(
    folder_id: str = Field(..., description="The unique identifier of the folder whose app item associations you want to retrieve. The folder ID appears in the URL when viewing the folder in the Box web app. The root folder is always ID 0."),
    limit: str | None = Field(None, description="The maximum number of app item associations to return per page. Must be between 1 and 1000."),
    application_type: str | None = Field(None, description="Filters results to only include app items belonging to the specified application type. When omitted, associations for all application types are returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all app items associated with a folder, including associations inherited from ancestor folders. App item type and ID are visible to any user with folder access, regardless of View permission on the app item."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetFoldersIdAppItemAssociationsRequest(
            path=_models.GetFoldersIdAppItemAssociationsRequestPath(folder_id=folder_id),
            query=_models.GetFoldersIdAppItemAssociationsRequestQuery(limit=_limit, application_type=application_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_folder_app_item_associations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/app_item_associations", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/app_item_associations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_folder_app_item_associations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_folder_app_item_associations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_folder_app_item_associations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Folders
@mcp.tool(
    title="List Folder Items",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_folder_items(
    folder_id: str = Field(..., description="The unique identifier of the folder whose contents you want to list. The root folder of any Box account always uses the ID '0'; for other folders, find the ID in the URL when viewing the folder in the Box web app."),
    usemarker: bool | None = Field(None, description="Set to true to enable marker-based pagination, which returns a 'marker' token in the response to fetch the next page. Cannot be combined with offset-based pagination; use one method consistently throughout a paginated sequence."),
    offset: str | None = Field(None, description="The zero-based index of the first item to include in the response, used for offset-based pagination. Avoid high offset values on large datasets as reliability is not guaranteed; prefer marker-based pagination in those cases."),
    limit: str | None = Field(None, description="The maximum number of items to return in a single page of results. Accepted values range from 1 to 1000."),
    sort: Literal["id", "name", "date", "size"] | None = Field(None, description="The secondary attribute by which to sort items within their type grouping — items are always sorted by type first (folders, then files, then web links). Sorting by this field is not supported for marker-based pagination on the root folder (ID '0')."),
    direction: Literal["ASC", "DESC"] | None = Field(None, description="The sort direction for results, either ascending or descending alphabetical/numerical order."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of files, folders, and web links contained within a specified folder. Use the dedicated Get Folder endpoint if you need metadata about the folder itself, such as its size."""

    _offset = _parse_int(offset)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetFoldersIdItemsRequest(
            path=_models.GetFoldersIdItemsRequestPath(folder_id=folder_id),
            query=_models.GetFoldersIdItemsRequestQuery(usemarker=usemarker, offset=_offset, limit=_limit, sort=sort, direction=direction)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_folder_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/items", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_folder_items")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_folder_items", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_folder_items",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Folders
@mcp.tool(
    title="Create Folder",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_folder(
    name: str | None = Field(None, description="The display name for the new folder. Must be between 1 and 255 characters, must not contain non-printable ASCII characters, forward or backward slashes, or trailing spaces, and cannot be '.' or '..'. Names are checked case-insensitively for uniqueness within the parent folder.", min_length=1, max_length=255),
    id_: str | None = Field(None, alias="id", description="The unique ID of the parent folder in which the new folder will be created. Use '0' to create the folder at the root level of the user's account."),
    folder_upload_email: _models.PostFoldersBodyFolderUploadEmail | None = Field(None, description="Optional email upload configuration for the folder, allowing files to be uploaded by sending an email to a folder-specific address."),
    sync_state: Literal["synced", "not_synced", "partially_synced"] | None = Field(None, description="Specifies the sync state of the folder for Box Sync (discontinued). Accepted values are 'synced' (fully synced), 'not_synced' (not synced), or 'partially_synced' (some contents synced). Not applicable to Box Drive."),
) -> dict[str, Any] | ToolResult:
    """Creates a new empty folder inside a specified parent folder. The folder name must be unique within the parent (case-insensitive) and must not contain invalid characters or trailing spaces."""

    # Construct request model with validation
    try:
        _request = _models.PostFoldersRequest(
            body=_models.PostFoldersRequestBody(name=name, folder_upload_email=folder_upload_email, sync_state=sync_state,
                parent=_models.PostFoldersRequestBodyParent(id_=id_) if any(v is not None for v in [id_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/folders"
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
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Folders
@mcp.tool(
    title="Copy Folder",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def copy_folder(
    folder_id: str = Field(..., description="The unique identifier of the folder to copy. The folder ID can be found in the Box web app URL when viewing the folder. The root folder (ID '0') cannot be copied."),
    name: str | None = Field(None, description="An optional name for the copied folder. If omitted, the original folder name is used. Names must be between 1 and 255 characters, cannot contain non-printable ASCII characters, forward or backward slashes, trailing spaces, or be exactly '.' or '..'.", min_length=1, max_length=255),
    id_: str | None = Field(None, alias="id", description="The ID of the destination parent folder where the copied folder will be placed."),
) -> dict[str, Any] | ToolResult:
    """Creates a copy of an existing folder and places it inside a specified destination folder. The original folder and its contents remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.PostFoldersIdCopyRequest(
            path=_models.PostFoldersIdCopyRequestPath(folder_id=folder_id),
            body=_models.PostFoldersIdCopyRequestBody(name=name,
                parent=_models.PostFoldersIdCopyRequestBodyParent(id_=id_) if any(v is not None for v in [id_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for copy_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/copy", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/copy"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("copy_folder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("copy_folder", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="copy_folder",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Collaborations (List)
@mcp.tool(
    title="List Folder Collaborations",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_folder_collaborations(
    folder_id: str = Field(..., description="The unique identifier of the folder whose collaborations you want to retrieve. Find this ID in the Box web app by opening the folder and copying the numeric ID from the URL."),
    limit: str | None = Field(None, description="The maximum number of collaboration records to return in a single page of results. Accepts values up to 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all active and pending collaborations for a specified folder, returning details on users who currently have access or have been invited to collaborate."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetFoldersIdCollaborationsRequest(
            path=_models.GetFoldersIdCollaborationsRequestPath(folder_id=folder_id),
            query=_models.GetFoldersIdCollaborationsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_folder_collaborations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/collaborations", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/collaborations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_folder_collaborations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_folder_collaborations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_folder_collaborations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Trashed folders
@mcp.tool(
    title="Get Trashed Folder",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_trashed_folder(folder_id: str = Field(..., description="The unique identifier of the trashed folder to retrieve. Only folders directly moved to the trash are accessible; folders implicitly trashed via a parent cannot be retrieved by their own ID.")) -> dict[str, Any] | ToolResult:
    """Retrieves metadata for a specific folder that has been directly moved to the trash. Note: if a parent folder was trashed instead, only that parent folder can be retrieved via this endpoint."""

    # Construct request model with validation
    try:
        _request = _models.GetFoldersIdTrashRequest(
            path=_models.GetFoldersIdTrashRequestPath(folder_id=folder_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_trashed_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/trash", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/trash"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_trashed_folder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_trashed_folder", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_trashed_folder",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Trashed folders
@mcp.tool(
    title="Permanently Delete Trashed Folder",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def permanently_delete_trashed_folder(folder_id: str = Field(..., description="The unique identifier of the folder to permanently delete from trash. The folder ID can be found in the URL when viewing the folder in the Box web application.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a folder that is currently in the trash, freeing storage and removing it from Box entirely. This action is irreversible and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFoldersIdTrashRequest(
            path=_models.DeleteFoldersIdTrashRequestPath(folder_id=folder_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for permanently_delete_trashed_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/trash", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/trash"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("permanently_delete_trashed_folder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("permanently_delete_trashed_folder", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="permanently_delete_trashed_folder",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata instances (Folders)
@mcp.tool(
    title="List Folder Metadata",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_folder_metadata(
    folder_id: str = Field(..., description="The unique identifier of the folder whose metadata instances will be retrieved. Find this ID in the Box web app URL when viewing the folder."),
    view: str | None = Field(None, description="Controls how taxonomy field values are represented in the response. By default, taxonomy values are returned as node identifiers (API view); set to `hydrated` to return full taxonomy node details instead."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all metadata instances attached to a given folder. Cannot be used on the root folder (ID `0`)."""

    # Construct request model with validation
    try:
        _request = _models.GetFoldersIdMetadataRequest(
            path=_models.GetFoldersIdMetadataRequestPath(folder_id=folder_id),
            query=_models.GetFoldersIdMetadataRequestQuery(view=view)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_folder_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/metadata", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/metadata"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_folder_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_folder_metadata", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_folder_metadata",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Classifications on folders
@mcp.tool(
    title="Get Folder Classification",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_folder_classification(folder_id: str = Field(..., description="The unique identifier of the folder whose classification metadata you want to retrieve. The root folder of a Box account is always ID '0'; other folder IDs can be found in the URL when viewing the folder in the Box web application.")) -> dict[str, Any] | ToolResult:
    """Retrieves the security classification metadata applied to a specific folder. Returns the classification instance associated with the folder's enterprise security policy."""

    # Construct request model with validation
    try:
        _request = _models.GetFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest(
            path=_models.GetFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath(folder_id=folder_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_folder_classification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/metadata/enterprise/securityClassification-6VMVochwUWo", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/metadata/enterprise/securityClassification-6VMVochwUWo"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_folder_classification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_folder_classification", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_folder_classification",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Classifications on folders
@mcp.tool(
    title="Add Folder Classification",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def add_folder_classification(
    folder_id: str = Field(..., description="The unique identifier of the folder to classify. The ID can be found in the folder's URL in the Box web app; the root folder is always ID '0'."),
    box__security__classification__key: str | None = Field(None, alias="Box__Security__Classification__Key", description="The classification label to apply to the folder. Must match an existing classification key from the enterprise's security classification template."),
) -> dict[str, Any] | ToolResult:
    """Applies a security classification label to a specified folder. The classification must exist in the enterprise's classification template."""

    # Construct request model with validation
    try:
        _request = _models.PostFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest(
            path=_models.PostFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath(folder_id=folder_id),
            body=_models.PostFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestBody(box__security__classification__key=box__security__classification__key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_folder_classification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/metadata/enterprise/securityClassification-6VMVochwUWo", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/metadata/enterprise/securityClassification-6VMVochwUWo"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_folder_classification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_folder_classification", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_folder_classification",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Classifications on folders
@mcp.tool(
    title="Update Folder Classification",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_folder_classification(
    folder_id: str = Field(..., description="The unique identifier of the folder whose classification will be updated. The folder ID can be found in the URL when viewing the folder in the Box web app. The root folder is always ID '0'."),
    body: list[_models.PutFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoBodyItem] | None = Field(None, description="A list containing exactly one JSON Patch operation object describing the change to apply to the classification label. Only a single update operation is supported per request."),
) -> dict[str, Any] | ToolResult:
    """Updates the security classification label on a folder that already has a classification applied. Only classification values defined for the enterprise are accepted."""

    # Construct request model with validation
    try:
        _request = _models.PutFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest(
            path=_models.PutFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath(folder_id=folder_id),
            body=_models.PutFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_folder_classification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/metadata/enterprise/securityClassification-6VMVochwUWo", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/metadata/enterprise/securityClassification-6VMVochwUWo"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/json-patch+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_folder_classification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_folder_classification", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_folder_classification",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json-patch+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Classifications on folders
@mcp.tool(
    title="Remove Folder Classification",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_folder_classification(folder_id: str = Field(..., description="The unique identifier of the folder from which the classification will be removed. The root folder of a Box account is always represented by ID '0'.")) -> dict[str, Any] | ToolResult:
    """Removes any existing security classification from a specified folder. This operation clears all classification metadata applied via the enterprise security classification schema."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest(
            path=_models.DeleteFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath(folder_id=folder_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_folder_classification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/metadata/enterprise/securityClassification-6VMVochwUWo", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/metadata/enterprise/securityClassification-6VMVochwUWo"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_folder_classification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_folder_classification", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_folder_classification",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata instances (Folders)
@mcp.tool(
    title="Get Folder Metadata Instance",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_folder_metadata_instance(
    folder_id: str = Field(..., description="The unique identifier of the folder whose metadata instance you want to retrieve. Find this ID in the Box web app URL when viewing the folder. The root folder is always ID `0`, but is not supported by this operation."),
    scope: Literal["global", "enterprise"] = Field(..., description="The scope of the metadata template to retrieve, either `global` for Box-wide templates or `enterprise` for templates defined within your organization."),
    template_key: str = Field(..., description="The unique key name of the metadata template whose instance you want to retrieve from the folder."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific metadata template instance applied to a folder, returning its field values and associated metadata. Cannot be used on the root folder (ID `0`)."""

    # Construct request model with validation
    try:
        _request = _models.GetFoldersIdMetadataIdIdRequest(
            path=_models.GetFoldersIdMetadataIdIdRequestPath(folder_id=folder_id, scope=scope, template_key=template_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_folder_metadata_instance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/metadata/{scope}/{template_key}", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/metadata/{scope}/{template_key}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_folder_metadata_instance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_folder_metadata_instance", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_folder_metadata_instance",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata instances (Folders)
@mcp.tool(
    title="Create Folder Metadata",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_folder_metadata(
    folder_id: str = Field(..., description="The unique identifier of the folder to which the metadata instance will be applied. The root folder of a Box account always uses ID `0`; other folder IDs can be found in the URL when viewing the folder in the Box web app."),
    scope: Literal["global", "enterprise"] = Field(..., description="The scope of the metadata template to apply, either `global` for Box-wide templates or `enterprise` for templates defined within your enterprise."),
    template_key: str = Field(..., description="The unique key name of the metadata template to apply to the folder. Use `properties` for the global free-form key-value template, which accepts any key-value pair."),
    body: dict[str, Any] | None = Field(None, description="The metadata key-value pairs to store on the folder, conforming to the fields defined in the specified template. The `global.properties` template accepts any arbitrary key-value pairs."),
) -> dict[str, Any] | ToolResult:
    """Applies an instance of a metadata template to a folder, attaching structured key-value data based on the specified template. Note that the enterprise must have Cascading Folder Level Metadata enabled in the admin console for the metadata to appear in the Box web app."""

    # Construct request model with validation
    try:
        _request = _models.PostFoldersIdMetadataIdIdRequest(
            path=_models.PostFoldersIdMetadataIdIdRequestPath(folder_id=folder_id, scope=scope, template_key=template_key),
            body=_models.PostFoldersIdMetadataIdIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_folder_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/metadata/{scope}/{template_key}", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/metadata/{scope}/{template_key}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_folder_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_folder_metadata", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_folder_metadata",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata instances (Folders)
@mcp.tool(
    title="Update Folder Metadata",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_folder_metadata(
    folder_id: str = Field(..., description="The unique identifier of the folder to update metadata on. The ID appears in the folder's URL in the Box web app, and the root folder is always ID `0`."),
    scope: Literal["global", "enterprise"] = Field(..., description="The scope of the metadata template, either globally defined or specific to the enterprise account."),
    template_key: str = Field(..., description="The unique key name of the metadata template to update on the folder."),
    body: list[_models.PutFoldersIdMetadataIdIdBodyItem] | None = Field(None, description="A JSON Patch array of operation objects describing the changes to apply to the metadata instance. Operations are applied atomically — if any operation fails, no changes are made."),
) -> dict[str, Any] | ToolResult:
    """Updates a metadata instance on a folder using JSON Patch operations, applied atomically. The metadata template must already be applied to the folder, and all changes must conform to the template schema."""

    # Construct request model with validation
    try:
        _request = _models.PutFoldersIdMetadataIdIdRequest(
            path=_models.PutFoldersIdMetadataIdIdRequestPath(folder_id=folder_id, scope=scope, template_key=template_key),
            body=_models.PutFoldersIdMetadataIdIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_folder_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/metadata/{scope}/{template_key}", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/metadata/{scope}/{template_key}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/json-patch+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_folder_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_folder_metadata", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_folder_metadata",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json-patch+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata instances (Folders)
@mcp.tool(
    title="Delete Folder Metadata",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_folder_metadata(
    folder_id: str = Field(..., description="The unique identifier of the folder from which metadata will be removed. The root folder of a Box account is always represented by ID '0'; other folder IDs can be found in the URL when viewing the folder in the web application."),
    scope: Literal["global", "enterprise"] = Field(..., description="The scope of the metadata template, determining whether it is a globally available template or one specific to the enterprise account."),
    template_key: str = Field(..., description="The unique key name of the metadata template instance to remove from the folder, identifying which template's data should be deleted."),
) -> dict[str, Any] | ToolResult:
    """Removes a specific metadata instance from a folder by deleting the metadata template instance identified by its scope and template key. This action permanently detaches the metadata from the folder."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFoldersIdMetadataIdIdRequest(
            path=_models.DeleteFoldersIdMetadataIdIdRequestPath(folder_id=folder_id, scope=scope, template_key=template_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_folder_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/metadata/{scope}/{template_key}", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/metadata/{scope}/{template_key}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_folder_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_folder_metadata", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_folder_metadata",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Trashed items
@mcp.tool(
    title="List Trash Items",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_trash_items(
    limit: str | None = Field(None, description="The maximum number of items to return per page. Must be between 1 and 1000."),
    offset: str | None = Field(None, description="The zero-based index of the first item to include in the response, used for offset-based pagination. Offsets exceeding 10000 will result in a 400 error."),
    direction: Literal["ASC", "DESC"] | None = Field(None, description="The sort direction for results, either ascending or descending alphabetical order. Items are always grouped by type first (folders, then files, then web links) before this ordering is applied."),
    sort: Literal["name", "date", "size"] | None = Field(None, description="The secondary attribute by which to sort items within each type group. Items are always sorted by type first; this parameter is not supported when using marker-based pagination."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all files and folders currently in the trash. Supports offset-based and marker-based pagination, and allows sorting and filtering by specific attributes using the fields parameter."""

    _limit = _parse_int(limit)
    _offset = _parse_int(offset)

    # Construct request model with validation
    try:
        _request = _models.GetFoldersTrashItemsRequest(
            query=_models.GetFoldersTrashItemsRequestQuery(limit=_limit, offset=_offset, direction=direction, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_trash_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/folders/trash/items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_trash_items")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_trash_items", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_trash_items",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Watermarks (Folders)
@mcp.tool(
    title="Get Folder Watermark",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_folder_watermark(folder_id: str = Field(..., description="The unique identifier of the folder whose watermark you want to retrieve. The root folder of a Box account is always represented by the ID '0'; other folder IDs can be found in the URL when viewing the folder in the Box web application.")) -> dict[str, Any] | ToolResult:
    """Retrieves the watermark applied to a specific folder in Box. Returns watermark details if one exists, or a 404 if no watermark has been applied."""

    # Construct request model with validation
    try:
        _request = _models.GetFoldersIdWatermarkRequest(
            path=_models.GetFoldersIdWatermarkRequestPath(folder_id=folder_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_folder_watermark: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/watermark", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/watermark"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_folder_watermark")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_folder_watermark", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_folder_watermark",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Watermarks (Folders)
@mcp.tool(
    title="Apply Folder Watermark",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def apply_folder_watermark(
    folder_id: str = Field(..., description="The unique identifier of the folder to watermark. The folder ID can be found in the URL when viewing the folder in the Box web app. The root folder of any Box account is always ID `0`."),
    imprint: Literal["default"] | None = Field(None, description="The type of watermark imprint to apply to the folder. Currently only the default imprint style is supported."),
) -> dict[str, Any] | ToolResult:
    """Applies or updates a watermark on a specified folder in Box. Use this to protect folder contents by overlaying a visible watermark imprint."""

    # Construct request model with validation
    try:
        _request = _models.PutFoldersIdWatermarkRequest(
            path=_models.PutFoldersIdWatermarkRequestPath(folder_id=folder_id),
            body=_models.PutFoldersIdWatermarkRequestBody(watermark=_models.PutFoldersIdWatermarkRequestBodyWatermark(imprint=imprint) if any(v is not None for v in [imprint]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for apply_folder_watermark: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/watermark", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/watermark"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("apply_folder_watermark")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("apply_folder_watermark", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="apply_folder_watermark",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Watermarks (Folders)
@mcp.tool(
    title="Remove Folder Watermark",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_folder_watermark(folder_id: str = Field(..., description="The unique identifier of the folder from which the watermark will be removed. The root folder of a Box account is always represented by the ID '0'.")) -> dict[str, Any] | ToolResult:
    """Removes the watermark from a specified folder in Box. Once removed, the folder's content will no longer display watermark overlays."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFoldersIdWatermarkRequest(
            path=_models.DeleteFoldersIdWatermarkRequestPath(folder_id=folder_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_folder_watermark: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}/watermark", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}/watermark"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_folder_watermark")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_folder_watermark", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_folder_watermark",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Folder Locks
@mcp.tool(
    title="List Folder Locks",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_folder_locks(folder_id: str = Field(..., description="The unique identifier of the folder whose locks you want to retrieve. You can find this ID in the folder's URL in the Box web application; the root folder is always ID `0`.")) -> dict[str, Any] | ToolResult:
    """Retrieves all lock details for a specified folder, including lock type and restrictions. You must be authenticated as the owner or co-owner of the folder to use this endpoint."""

    # Construct request model with validation
    try:
        _request = _models.GetFolderLocksRequest(
            query=_models.GetFolderLocksRequestQuery(folder_id=folder_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_folder_locks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/folder_locks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_folder_locks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_folder_locks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_folder_locks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Folder Locks
@mcp.tool(
    title="Lock Folder",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def lock_folder(
    move: bool | None = Field(None, description="Whether to lock the folder against move operations, preventing it from being relocated within the file system."),
    delete: bool | None = Field(None, description="Whether to lock the folder against deletion, preventing it from being permanently removed."),
    id_: str | None = Field(None, alias="id", description="The unique identifier of the folder on which to apply the lock."),
) -> dict[str, Any] | ToolResult:
    """Creates a lock on a folder to prevent it from being moved and/or deleted. You must be the owner or co-owner of the folder to perform this action."""

    # Construct request model with validation
    try:
        _request = _models.PostFolderLocksRequest(
            body=_models.PostFolderLocksRequestBody(locked_operations=_models.PostFolderLocksRequestBodyLockedOperations(move=move, delete=delete) if any(v is not None for v in [move, delete]) else None,
                folder=_models.PostFolderLocksRequestBodyFolder(id_=id_) if any(v is not None for v in [id_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for lock_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/folder_locks"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("lock_folder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("lock_folder", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="lock_folder",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Folder Locks
@mcp.tool(
    title="Delete Folder Lock",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_folder_lock(folder_lock_id: str = Field(..., description="The unique identifier of the folder lock to delete.")) -> dict[str, Any] | ToolResult:
    """Deletes a specific folder lock, removing any restrictions it imposed on the folder. You must be authenticated as the owner or co-owner of the folder to perform this action."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFolderLocksIdRequest(
            path=_models.DeleteFolderLocksIdRequestPath(folder_lock_id=folder_lock_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_folder_lock: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folder_locks/{folder_lock_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/folder_locks/{folder_lock_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_folder_lock")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_folder_lock", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_folder_lock",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata templates
@mcp.tool(
    title="Find Metadata Template by Instance",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def find_metadata_template_by_instance(
    metadata_instance_id: str = Field(..., description="The unique UUID of a metadata template instance used to identify and retrieve the associated template definition."),
    limit: str | None = Field(None, description="The maximum number of metadata templates to return in a single page of results. Must be between 1 and 1000."),
) -> dict[str, Any] | ToolResult:
    """Finds a metadata template by looking up the ID of one of its existing instances. Useful when you have an instance ID and need to retrieve the template definition it was created from."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetMetadataTemplatesRequest(
            query=_models.GetMetadataTemplatesRequestQuery(metadata_instance_id=metadata_instance_id, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for find_metadata_template_by_instance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/metadata_templates"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("find_metadata_template_by_instance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("find_metadata_template_by_instance", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="find_metadata_template_by_instance",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Classifications
@mcp.tool(
    title="List Classifications",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_classifications() -> dict[str, Any] | ToolResult:
    """Retrieves the enterprise security classification metadata template and returns all classification labels available to the enterprise. Can also be accessed by specifying the enterprise ID explicitly in the URL."""

    # Extract parameters for API call
    _http_path = "/metadata_templates/enterprise/securityClassification-6VMVochwUWo/schema"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_classifications")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_classifications", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_classifications",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata templates
@mcp.tool(
    title="Get Metadata Template Schema",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_metadata_template(
    scope: Literal["global", "enterprise"] = Field(..., description="The scope of the metadata template, either 'global' for Box-wide templates or 'enterprise' for templates specific to your organization."),
    template_key: str = Field(..., description="The unique key identifying the metadata template within its scope. To discover available template keys, list all templates for an enterprise or globally, or list templates applied to a file or folder."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific metadata template by its scope and template key. Use this to fetch full template details including its fields and configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetMetadataTemplatesIdIdSchemaRequest(
            path=_models.GetMetadataTemplatesIdIdSchemaRequestPath(scope=scope, template_key=template_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metadata_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/metadata_templates/{scope}/{template_key}/schema", _request.path.model_dump(by_alias=True)) if _request.path else "/metadata_templates/{scope}/{template_key}/schema"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metadata_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metadata_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metadata_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata templates
@mcp.tool(
    title="Update Metadata Template",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_metadata_template(
    scope: Literal["global", "enterprise"] = Field(..., description="The scope of the metadata template, determining its visibility and ownership — either globally available or restricted to the enterprise."),
    template_key: str = Field(..., description="The unique key identifying the metadata template within the given scope."),
    body: list[_models.PutMetadataTemplatesIdIdSchemaBodyItem] | None = Field(None, description="An ordered array of JSON-Patch (RFC 6902) operation objects describing the changes to apply to the metadata template. Each item specifies an operation type, target path, and value as needed."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing metadata template by applying a series of JSON-Patch operations atomically. All changes succeed or fail together — no partial updates are applied if any operation encounters an error."""

    # Construct request model with validation
    try:
        _request = _models.PutMetadataTemplatesIdIdSchemaRequest(
            path=_models.PutMetadataTemplatesIdIdSchemaRequestPath(scope=scope, template_key=template_key),
            body=_models.PutMetadataTemplatesIdIdSchemaRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_metadata_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/metadata_templates/{scope}/{template_key}/schema", _request.path.model_dump(by_alias=True)) if _request.path else "/metadata_templates/{scope}/{template_key}/schema"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/json-patch+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_metadata_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_metadata_template", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_metadata_template",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json-patch+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata templates
@mcp.tool(
    title="Delete Metadata Template Schema",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_metadata_template(
    scope: Literal["global", "enterprise"] = Field(..., description="The scope of the metadata template, determining whether it applies globally across all enterprises or is specific to your enterprise."),
    template_key: str = Field(..., description="The unique key name identifying the metadata template within the specified scope."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a metadata template and all of its associated instances. This action is irreversible and removes the template across all content it was applied to."""

    # Construct request model with validation
    try:
        _request = _models.DeleteMetadataTemplatesIdIdSchemaRequest(
            path=_models.DeleteMetadataTemplatesIdIdSchemaRequestPath(scope=scope, template_key=template_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_metadata_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/metadata_templates/{scope}/{template_key}/schema", _request.path.model_dump(by_alias=True)) if _request.path else "/metadata_templates/{scope}/{template_key}/schema"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_metadata_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_metadata_template", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_metadata_template",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata templates
@mcp.tool(
    title="Get Metadata Template by ID",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_metadata_template_by_id(template_id: str = Field(..., description="The unique identifier of the metadata template to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific metadata template by its unique ID. Use this to inspect template structure, fields, and configuration for a known template."""

    # Construct request model with validation
    try:
        _request = _models.GetMetadataTemplatesIdRequest(
            path=_models.GetMetadataTemplatesIdRequestPath(template_id=template_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metadata_template_by_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/metadata_templates/{template_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/metadata_templates/{template_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metadata_template_by_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metadata_template_by_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metadata_template_by_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata templates
@mcp.tool(
    title="List Global Metadata Templates",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_global_metadata_templates(limit: str | None = Field(None, description="The maximum number of metadata templates to return per page. Accepts values up to 1000; omit to use the default page size.")) -> dict[str, Any] | ToolResult:
    """Retrieves all generic, global metadata templates available to every enterprise using Box. These templates are not organization-specific and can be applied universally across all Box accounts."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetMetadataTemplatesGlobalRequest(
            query=_models.GetMetadataTemplatesGlobalRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_global_metadata_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/metadata_templates/global"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_global_metadata_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_global_metadata_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_global_metadata_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata templates
@mcp.tool(
    title="List Enterprise Metadata Templates",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_enterprise_metadata_templates(limit: str | None = Field(None, description="Maximum number of metadata templates to return per page. Accepts values up to 1000.")) -> dict[str, Any] | ToolResult:
    """Retrieves all metadata templates created for use within the authenticated user's enterprise. Returns a paginated list of enterprise-scoped templates available for applying structured metadata to content."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetMetadataTemplatesEnterpriseRequest(
            query=_models.GetMetadataTemplatesEnterpriseRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_enterprise_metadata_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/metadata_templates/enterprise"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_enterprise_metadata_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_enterprise_metadata_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_enterprise_metadata_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata templates
@mcp.tool(
    title="Create Metadata Template",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_metadata_template(
    scope: str | None = Field(None, description="The scope under which the metadata template will be created. Must be set to 'enterprise', as global-scoped templates cannot be created via the API."),
    template_key: str | None = Field(None, alias="templateKey", description="A unique identifier for the template across the enterprise, used to reference it programmatically. Must start with a letter or underscore, followed by letters, digits, hyphens, or underscores, up to 64 characters. If omitted, the API auto-generates one from the display name.", max_length=64, pattern="^[a-zA-Z_][-a-zA-Z0-9_]*$"),
    display_name: str | None = Field(None, alias="displayName", description="The human-readable name of the template shown in the Box UI and API responses, up to 4096 characters.", max_length=4096),
    hidden: bool | None = Field(None, description="Controls whether the template is visible in the Box web app UI. Set to true to hide it and restrict usage to API access only."),
    fields: list[_models.PostMetadataTemplatesSchemaBodyFieldsItem] | None = Field(None, description="An ordered list of field definitions that make up the template. Each field can be of type text, date, number, single-select, or multi-select list, and the order provided determines display order."),
    copy_instance_on_item_copy: bool | None = Field(None, alias="copyInstanceOnItemCopy", description="Determines whether metadata instances attached to a file or folder are automatically copied when that item is copied. Defaults to false, meaning metadata is not copied."),
) -> dict[str, Any] | ToolResult:
    """Creates a new metadata template that can be applied to files and folders within an enterprise, defining custom fields for organizing and categorizing content."""

    # Construct request model with validation
    try:
        _request = _models.PostMetadataTemplatesSchemaRequest(
            body=_models.PostMetadataTemplatesSchemaRequestBody(scope=scope, template_key=template_key, display_name=display_name, hidden=hidden, fields=fields, copy_instance_on_item_copy=copy_instance_on_item_copy)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_metadata_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/metadata_templates/schema"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_metadata_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_metadata_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_metadata_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Classifications
@mcp.tool(
    title="Initialize Classifications",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def initialize_classifications(
    hidden: bool | None = Field(None, description="Controls whether the classification template is hidden from users on web and mobile devices. Set to true to restrict visibility, or false to make classifications available for selection."),
    copy_instance_on_item_copy: bool | None = Field(None, alias="copyInstanceOnItemCopy", description="Controls whether the assigned classification is automatically copied to a new item when a file or folder is copied. Set to true to propagate classifications on copy, or false to leave the copy unclassified."),
    fields: list[_models.PostMetadataTemplatesSchemaClassificationsBodyFieldsItem] | None = Field(None, description="Defines the classification values available in the template. Exactly one field object must be provided, containing all valid classification options as enumerated values within that field."),
) -> dict[str, Any] | ToolResult:
    """Initializes the classification metadata template for an enterprise with an initial set of classifications. Use this only when no classification template exists yet; if one already exists, use the add classifications endpoint instead."""

    # Construct request model with validation
    try:
        _request = _models.PostMetadataTemplatesSchemaClassificationsRequest(
            body=_models.PostMetadataTemplatesSchemaClassificationsRequestBody(hidden=hidden, copy_instance_on_item_copy=copy_instance_on_item_copy, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for initialize_classifications: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/metadata_templates/schema#classifications"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("initialize_classifications")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("initialize_classifications", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="initialize_classifications",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata cascade policies
@mcp.tool(
    title="List Metadata Cascade Policies",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_metadata_cascade_policies(
    folder_id: str = Field(..., description="The ID of the folder for which to retrieve metadata cascade policies. Must be a valid non-root folder; the root folder with ID `0` is not supported."),
    owner_enterprise_id: str | None = Field(None, description="The ID of the enterprise whose metadata cascade policies should be returned. Defaults to the currently authenticated enterprise if not provided."),
    offset: str | None = Field(None, description="The zero-based index of the first item to include in the response, used for paginating through results. Must not exceed 10000; requests with a higher offset will be rejected with a 400 error."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all metadata cascade policies applied to a specific folder, which automatically apply metadata templates to items within that folder. Cannot be used on the root folder (ID `0`)."""

    _offset = _parse_int(offset)

    # Construct request model with validation
    try:
        _request = _models.GetMetadataCascadePoliciesRequest(
            query=_models.GetMetadataCascadePoliciesRequestQuery(folder_id=folder_id, owner_enterprise_id=owner_enterprise_id, offset=_offset)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_metadata_cascade_policies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/metadata_cascade_policies"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_metadata_cascade_policies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_metadata_cascade_policies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_metadata_cascade_policies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata cascade policies
@mcp.tool(
    title="Create Metadata Cascade Policy",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_metadata_cascade_policy(
    folder_id: str | None = Field(None, description="The unique identifier of the folder to which the cascade policy will be applied. The folder must already have an instance of the target metadata template applied to it."),
    metadata_template: str | None = Field(None, description="The metadata template identifier in 'scope/templateKey' format (e.g., 'enterprise_12345/contractTemplate')"),
) -> dict[str, Any] | ToolResult:
    """Creates a metadata cascade policy that automatically applies a metadata template from a specified folder down to all files within it. The folder must already have an instance of the target metadata template applied before the policy can take effect."""

    # Call helper functions
    metadata_template_parsed = parse_metadata_template(metadata_template)

    # Construct request model with validation
    try:
        _request = _models.PostMetadataCascadePoliciesRequest(
            body=_models.PostMetadataCascadePoliciesRequestBody(folder_id=folder_id, scope=metadata_template_parsed.get('scope') if metadata_template_parsed else None, template_key=metadata_template_parsed.get('templateKey') if metadata_template_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_metadata_cascade_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/metadata_cascade_policies"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_metadata_cascade_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_metadata_cascade_policy", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_metadata_cascade_policy",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata cascade policies
@mcp.tool(
    title="Get Metadata Cascade Policy",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_metadata_cascade_policy(metadata_cascade_policy_id: str = Field(..., description="The unique identifier of the metadata cascade policy to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific metadata cascade policy assigned to a folder. Use this to inspect how metadata templates are being propagated from a folder to its contents."""

    # Construct request model with validation
    try:
        _request = _models.GetMetadataCascadePoliciesIdRequest(
            path=_models.GetMetadataCascadePoliciesIdRequestPath(metadata_cascade_policy_id=metadata_cascade_policy_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metadata_cascade_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/metadata_cascade_policies/{metadata_cascade_policy_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/metadata_cascade_policies/{metadata_cascade_policy_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metadata_cascade_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metadata_cascade_policy", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metadata_cascade_policy",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata cascade policies
@mcp.tool(
    title="Apply Metadata Cascade Policy",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def apply_metadata_cascade_policy(
    metadata_cascade_policy_id: str = Field(..., description="The unique identifier of the metadata cascade policy to force-apply to the folder's children."),
    conflict_resolution: Literal["none", "overwrite"] | None = Field(None, description="Determines how to handle conflicts when a child file already has an instance of the metadata template applied. Use 'none' to preserve existing values on the child, or 'overwrite' to replace them with the cascaded values from the folder."),
) -> dict[str, Any] | ToolResult:
    """Force-applies a metadata cascade policy to all existing children within a folder, ensuring inherited metadata values are propagated down. Useful after creating a new cascade policy to retroactively enforce metadata on files already present in the folder."""

    # Construct request model with validation
    try:
        _request = _models.PostMetadataCascadePoliciesIdApplyRequest(
            path=_models.PostMetadataCascadePoliciesIdApplyRequestPath(metadata_cascade_policy_id=metadata_cascade_policy_id),
            body=_models.PostMetadataCascadePoliciesIdApplyRequestBody(conflict_resolution=conflict_resolution)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for apply_metadata_cascade_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/metadata_cascade_policies/{metadata_cascade_policy_id}/apply", _request.path.model_dump(by_alias=True)) if _request.path else "/metadata_cascade_policies/{metadata_cascade_policy_id}/apply"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("apply_metadata_cascade_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("apply_metadata_cascade_policy", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="apply_metadata_cascade_policy",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Search
@mcp.tool(
    title="Query Items by Metadata",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def query_items_by_metadata(
    from_: str | None = Field(None, alias="from", description="The metadata template to query against, specified as `scope.templateKey`. Built-in Box-provided classification templates are not supported."),
    query: str | None = Field(None, description="A SQL-like logical expression used to filter items by their metadata field values. Use named placeholders (e.g., `:paramName`) to reference values defined in `query_params`."),
    query_params: dict[str, Any] | None = Field(None, description="A key-value map of named parameters referenced in the `query` expression. Each value's type must match the corresponding metadata template field type."),
    ancestor_folder_id: str | None = Field(None, description="The ID of the folder to scope the query to. Use `0` to search across all accessible folders, or provide a specific folder ID to restrict results to that folder and its subfolders."),
    order_by: list[_models.PostMetadataQueriesExecuteReadBodyOrderByItem] | None = Field(None, description="An ordered list of metadata template fields and sort directions to apply to the results. All items in the array must use the same sort direction."),
    limit: int | None = Field(None, description="The maximum number of results to return in a single request, between 0 and 100. This is an upper boundary and does not guarantee a minimum number of results.", ge=0, le=100),
) -> dict[str, Any] | ToolResult:
    """Search for files and folders using SQL-like syntax against a specific metadata template. Use the `fields` attribute to include additional metadata fields in the results."""

    # Construct request model with validation
    try:
        _request = _models.PostMetadataQueriesExecuteReadRequest(
            body=_models.PostMetadataQueriesExecuteReadRequestBody(from_=from_, query=query, query_params=query_params, ancestor_folder_id=ancestor_folder_id, order_by=order_by, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for query_items_by_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/metadata_queries/execute_read"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("query_items_by_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("query_items_by_metadata", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="query_items_by_metadata",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool(
    title="Get Comment",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_comment(comment_id: str = Field(..., description="The unique identifier of the comment to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the message, metadata, and author information for a specific comment. Use this to fetch the full details of a single comment by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetCommentsIdRequest(
            path=_models.GetCommentsIdRequestPath(comment_id=comment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/comments/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/comments/{comment_id}"
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
@mcp.tool(
    title="Update Comment",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_comment(
    comment_id: str = Field(..., description="The unique identifier of the comment to update."),
    message: str | None = Field(None, description="The new text content to replace the comment's existing message."),
) -> dict[str, Any] | ToolResult:
    """Updates the message text of an existing comment. Use this to edit or correct the content of a previously posted comment."""

    # Construct request model with validation
    try:
        _request = _models.PutCommentsIdRequest(
            path=_models.PutCommentsIdRequestPath(comment_id=comment_id),
            body=_models.PutCommentsIdRequestBody(message=message)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/comments/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/comments/{comment_id}"
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
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool(
    title="Delete Comment",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_comment(comment_id: str = Field(..., description="The unique identifier of the comment to permanently delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a comment by its unique identifier. This action is irreversible and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCommentsIdRequest(
            path=_models.DeleteCommentsIdRequestPath(comment_id=comment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/comments/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/comments/{comment_id}"
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
@mcp.tool(
    title="Create Comment",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_comment(
    tagged_message: str | None = Field(None, description="The text of the comment using mention syntax to tag another user, formatted as `@[user_id:display_name]` anywhere in the message. Use the plain `message` parameter instead if no user mentions are needed."),
    id_: str | None = Field(None, alias="id", description="The unique identifier of the file or comment this comment will be attached to."),
    type_: Literal["file", "comment"] | None = Field(None, alias="type", description="Specifies whether the comment is being placed on a file or as a reply to an existing comment."),
) -> dict[str, Any] | ToolResult:
    """Creates a new comment on a file or as a reply to an existing comment. Supports mentioning other users via a tagged message syntax to trigger email notifications."""

    # Construct request model with validation
    try:
        _request = _models.PostCommentsRequest(
            body=_models.PostCommentsRequestBody(tagged_message=tagged_message,
                item=_models.PostCommentsRequestBodyItem(id_=id_, type_=type_) if any(v is not None for v in [id_, type_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/comments"
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
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Collaborations
@mcp.tool(
    title="Get Collaboration",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_collaboration(collaboration_id: str = Field(..., description="The unique identifier of the collaboration to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a single collaboration by its unique identifier. Use this to inspect collaboration settings, permissions, and associated users or groups."""

    # Construct request model with validation
    try:
        _request = _models.GetCollaborationsIdRequest(
            path=_models.GetCollaborationsIdRequestPath(collaboration_id=collaboration_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_collaboration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/collaborations/{collaboration_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/collaborations/{collaboration_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_collaboration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_collaboration", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_collaboration",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collaborations
@mcp.tool(
    title="Update Collaboration",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_collaboration(
    collaboration_id: str = Field(..., description="The unique identifier of the collaboration to update."),
    role: Literal["editor", "viewer", "previewer", "uploader", "previewer uploader", "viewer uploader", "co-owner", "owner"] | None = Field(None, description="The permission level to grant the collaborator. Not required when accepting a collaboration invitation. Valid values range from read-only access (viewer, previewer) to full ownership (owner)."),
    status: Literal["pending", "accepted", "rejected"] | None = Field(None, description="Sets the status of a pending collaboration invitation to accept or reject it. Only applicable to collaborations currently in a pending state."),
    expires_at: str | None = Field(None, description="The date and time at which the collaboration will be automatically removed from the item, specified in ISO 8601 format. Requires the 'Automatically remove invited collaborators' setting to be enabled in the Admin Console, and the collaboration must have been created after that setting was enabled."),
    can_view_path: bool | None = Field(None, description="When true, allows the invited collaborator to see the full parent folder path to the collaborated item without gaining access to parent folder contents. Only applicable to folder collaborations; only an owner can update this setting on existing collaborations, and it is recommended to limit collaborations with this enabled to 1,000 per user."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing collaboration on a Box item, allowing you to change the collaborator's role, accept or reject a pending invitation, set an expiration date, or toggle parent path visibility."""

    # Construct request model with validation
    try:
        _request = _models.PutCollaborationsIdRequest(
            path=_models.PutCollaborationsIdRequestPath(collaboration_id=collaboration_id),
            body=_models.PutCollaborationsIdRequestBody(role=role, status=status, expires_at=expires_at, can_view_path=can_view_path)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_collaboration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/collaborations/{collaboration_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/collaborations/{collaboration_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_collaboration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_collaboration", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_collaboration",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Collaborations
@mcp.tool(
    title="Delete Collaboration",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_collaboration(collaboration_id: str = Field(..., description="The unique identifier of the collaboration to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently removes a collaboration by its unique identifier. This action cannot be undone and will revoke the associated access or shared relationship."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCollaborationsIdRequest(
            path=_models.DeleteCollaborationsIdRequestPath(collaboration_id=collaboration_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_collaboration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/collaborations/{collaboration_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/collaborations/{collaboration_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_collaboration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_collaboration", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_collaboration",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collaborations (List)
@mcp.tool(
    title="List Pending Collaborations",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_pending_collaborations(
    status: Literal["pending"] = Field(..., description="Filters collaborations by their current status. Only pending invites are supported by this endpoint."),
    offset: str | None = Field(None, description="Zero-based index of the first item to include in the response, used for paginating through results. Must not exceed 10,000; requests beyond this limit will return a 400 error."),
    limit: str | None = Field(None, description="Limits the number of collaboration records returned in a single page. Accepts values up to 1,000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all pending collaboration invites for the authenticated user. Returns a paginated list of collaborations awaiting the user's response."""

    _offset = _parse_int(offset)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetCollaborationsRequest(
            query=_models.GetCollaborationsRequestQuery(status=status, offset=_offset, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pending_collaborations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collaborations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pending_collaborations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pending_collaborations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pending_collaborations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collaborations
@mcp.tool(
    title="Create Collaboration",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_collaboration(
    notify: bool | None = Field(None, description="Whether to send an email notification to the invited collaborator when the collaboration is created."),
    item_type: Literal["file", "folder"] | None = Field(None, alias="itemType", description="The type of Box item the collaboration will be granted access to, either a file or a folder."),
    accessible_by_type: Literal["user", "group"] | None = Field(None, alias="accessible_byType", description="Specifies whether the collaborator being invited is an individual user or a group. Group invitations depend on the group's invite permissions."),
    item_id: str | None = Field(None, alias="itemId", description="The unique Box ID of the file or folder to which access is being granted."),
    accessible_by_id: str | None = Field(None, alias="accessible_byId", description="The unique Box ID of the user or group being invited. Use this or the email-based login field to identify a user, but not both."),
    login: str | None = Field(None, description="The email address of the user to invite as a collaborator. Use this or the user ID field to identify a user, but not both."),
    role: Literal["editor", "viewer", "previewer", "uploader", "previewer uploader", "viewer uploader", "co-owner"] | None = Field(None, description="The permission level granted to the collaborator, controlling what actions they can perform on the item."),
    is_access_only: bool | None = Field(None, description="When true, the collaborator can access the shared item but it will not appear in their All Files list and the root folder path will be hidden."),
    can_view_path: bool | None = Field(None, description="When true, allows the collaborator to see the full parent folder path to the shared folder without gaining access to parent folder contents. Only applicable to folder collaborations, and only owners or co-owners can set this. Limit use to 1,000 collaborations per user to avoid performance impact."),
    expires_at: str | None = Field(None, description="The date and time at which the collaboration will be automatically removed from the item, provided in ISO 8601 format. Requires the expiry extension setting to be enabled in the Admin Console Enterprise Settings."),
) -> dict[str, Any] | ToolResult:
    """Grants a single user or group access to a file or folder by creating a collaboration with a specified role. Collaborators can be identified by user ID, group ID, or email address."""

    # Construct request model with validation
    try:
        _request = _models.PostCollaborationsRequest(
            query=_models.PostCollaborationsRequestQuery(notify=notify),
            body=_models.PostCollaborationsRequestBody(role=role, is_access_only=is_access_only, can_view_path=can_view_path, expires_at=expires_at,
                item=_models.PostCollaborationsRequestBodyItem(type_=item_type, id_=item_id) if any(v is not None for v in [item_type, item_id]) else None,
                accessible_by=_models.PostCollaborationsRequestBodyAccessibleBy(type_=accessible_by_type, id_=accessible_by_id, login=login) if any(v is not None for v in [accessible_by_type, accessible_by_id, login]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_collaboration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collaborations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_collaboration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_collaboration", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_collaboration",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Search
@mcp.tool(
    title="Search Content",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_content(
    query: str | None = Field(None, description="The text to search for, matched against item names, descriptions, file content, and other fields. Supports boolean operators AND, OR, and NOT (uppercase only), and exact phrase matching using double quotes."),
    scope: Literal["user_content", "enterprise_content"] | None = Field(None, description="Restricts search results to content accessible by the current user (`user_content`) or all content across the entire enterprise (`enterprise_content`). Enterprise scope requires admin enablement via support."),
    file_extensions: list[str] | None = Field(None, description="Restricts results to files matching any of the specified file extensions. Provide extensions without leading dots as an array."),
    created_at_range: list[str] | None = Field(None, description="Restricts results to items created within a date range, provided as an array of two RFC3339 timestamp strings representing start and end dates. Either bound may be omitted to create an open-ended range."),
    updated_at_range: list[str] | None = Field(None, description="Restricts results to items last updated within a date range, provided as an array of two RFC3339 timestamp strings representing start and end dates. Either bound may be omitted to create an open-ended range."),
    size_range: list[int] | None = Field(None, description="Restricts results to items whose file size falls within a byte range, provided as an array of two integers representing the lower and upper bounds (inclusive). Either bound may be omitted to create an open-ended range."),
    owner_user_ids: list[str] | None = Field(None, description="Restricts results to items owned by the specified users, provided as an array of user ID strings. Items must still be accessible to the authenticated user; inaccessible owners yield empty results."),
    recent_updater_user_ids: list[str] | None = Field(None, description="Restricts results to items most recently updated by the specified users, provided as an array of user ID strings. Only the last 10 versions of each item are considered."),
    ancestor_folder_ids: list[str] | None = Field(None, description="Restricts results to items located within the specified folders or their subfolders, provided as an array of folder ID strings. Folders must be accessible to the authenticated user; inaccessible or nonexistent folders return HTTP 404."),
    content_types: list[Literal["name", "description", "file_content", "comments", "tag"]] | None = Field(None, description="Restricts the search to specific parts of an item, such as its name, description, file content, comments, or tags. Provide as an array of recognized content type strings."),
    type_: Literal["file", "folder", "web_link"] | None = Field(None, alias="type", description="Restricts results to a single item type: `file`, `folder`, or `web_link`. When omitted, all item types are returned."),
    trash_content: Literal["non_trashed_only", "trashed_only", "all_items"] | None = Field(None, description="Controls whether results include items in the trash, items not in the trash, or both. Defaults to returning only non-trashed items."),
    mdfilters: list[_models.MetadataFilter] | None = Field(None, description="Restricts results to items whose metadata matches a specific metadata template filter. Accepts exactly one metadata filter object; required when `query` is not provided.", min_length=1, max_length=1),
    sort: Literal["modified_at", "relevance"] | None = Field(None, description="Determines the ordering of search results. Use `relevance` to rank by match quality or `modified_at` to order by most recently modified first."),
    direction: Literal["DESC", "ASC"] | None = Field(None, description="Sets the sort direction for results as ascending (`ASC`) or descending (`DESC`). Ignored when `sort` is set to `relevance`, which always returns results in descending relevance order."),
    limit: str | None = Field(None, description="Maximum number of items to return per page of results. Must be between 1 and 200."),
    include_recent_shared_links: bool | None = Field(None, description="When set to true, includes items the user recently accessed via a shared link in the results. Enabling this changes the response format to include shared link metadata."),
    deleted_user_ids: list[str] | None = Field(None, description="Restricts results to items deleted by the specified users, provided as an array of user ID strings. Requires `trash_content` to be set to `trashed_only`. Only available for data from 2023-02-01 onwards."),
    deleted_at_range: list[str] | None = Field(None, description="Restricts results to items deleted within a date range, provided as an array of two RFC3339 timestamp strings representing start and end dates. Requires `trash_content` to be set to `trashed_only`. Only available for data from 2023-02-01 onwards."),
) -> dict[str, Any] | ToolResult:
    """Search for files, folders, web links, and shared files across the authenticated user's content or the entire enterprise, with support for rich filtering by metadata, date ranges, file type, ownership, and more."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetSearchRequest(
            query=_models.GetSearchRequestQuery(query=query, scope=scope, file_extensions=file_extensions, created_at_range=created_at_range, updated_at_range=updated_at_range, size_range=size_range, owner_user_ids=owner_user_ids, recent_updater_user_ids=recent_updater_user_ids, ancestor_folder_ids=ancestor_folder_ids, content_types=content_types, type_=type_, trash_content=trash_content, mdfilters=mdfilters, sort=sort, direction=direction, limit=_limit, include_recent_shared_links=include_recent_shared_links, deleted_user_ids=deleted_user_ids, deleted_at_range=deleted_at_range)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "file_extensions": ("form", False),
        "created_at_range": ("form", False),
        "updated_at_range": ("form", False),
        "size_range": ("form", False),
        "owner_user_ids": ("form", False),
        "recent_updater_user_ids": ("form", False),
        "ancestor_folder_ids": ("form", False),
        "content_types": ("form", False),
    })
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_content", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_content",
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
async def create_task(
    id_: str | None = Field(None, alias="id", description="The unique identifier of the file on which the task will be created."),
    type_: Literal["file"] | None = Field(None, alias="type", description="The type of item the task is being created on; must always be set to 'file'."),
    action: Literal["review", "complete"] | None = Field(None, description="The action assignees will be prompted to perform: 'review' creates an approval task that can be approved or rejected, while 'complete' creates a general task that can simply be marked as done."),
    message: str | None = Field(None, description="An optional message displayed to task assignees providing context or instructions for the task."),
    due_at: str | None = Field(None, description="The deadline by which the task should be completed, specified as an ISO 8601 date-time string. Defaults to null if omitted."),
    completion_rule: Literal["all_assignees", "any_assignee"] | None = Field(None, description="Determines how many assignees must act on the task before it is considered complete: 'all_assignees' requires every assignee to respond, while 'any_assignee' requires only one."),
) -> dict[str, Any] | ToolResult:
    """Creates a new task on a specified file, optionally configuring the action type, due date, message, and completion rules. The task must be assigned to users separately after creation."""

    # Construct request model with validation
    try:
        _request = _models.PostTasksRequest(
            body=_models.PostTasksRequestBody(action=action, message=message, due_at=due_at, completion_rule=completion_rule,
                item=_models.PostTasksRequestBodyItem(id_=id_, type_=type_) if any(v is not None for v in [id_, type_]) else None)
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
async def get_task(task_id: str = Field(..., description="The unique identifier of the task to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific task by its unique identifier. Use this to fetch the current state, metadata, and attributes of a single task."""

    # Construct request model with validation
    try:
        _request = _models.GetTasksIdRequest(
            path=_models.GetTasksIdRequestPath(task_id=task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_id}"
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
    task_id: str = Field(..., description="The unique identifier of the task to update."),
    action: Literal["review", "complete"] | None = Field(None, description="The type of action assignees are prompted to perform: 'review' creates an approval task that can be approved or rejected, while 'complete' creates a general task that can be marked done."),
    message: str | None = Field(None, description="The instructional message displayed to task assignees describing what they need to do."),
    due_at: str | None = Field(None, description="The deadline by which the task should be completed, specified as an ISO 8601 date-time string."),
    completion_rule: Literal["all_assignees", "any_assignee"] | None = Field(None, description="Determines how many assignees must complete the task before it is marked as completed: 'all_assignees' requires every assignee to act, while 'any_assignee' requires only one."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing task's configuration or completion state, including its action type, message, due date, and assignee completion rules."""

    # Construct request model with validation
    try:
        _request = _models.PutTasksIdRequest(
            path=_models.PutTasksIdRequestPath(task_id=task_id),
            body=_models.PutTasksIdRequestBody(action=action, message=message, due_at=due_at, completion_rule=completion_rule)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_id}"
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
async def delete_task(task_id: str = Field(..., description="The unique identifier of the task to be deleted.")) -> dict[str, Any] | ToolResult:
    """Permanently removes a task from its associated file. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTasksIdRequest(
            path=_models.DeleteTasksIdRequestPath(task_id=task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_id}"
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

# Tags: Task assignments
@mcp.tool(
    title="List Task Assignments",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_task_assignments(task_id: str = Field(..., description="The unique identifier of the task whose assignments you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves all assignments associated with a specific task, returning the list of users or groups assigned to it."""

    # Construct request model with validation
    try:
        _request = _models.GetTasksIdAssignmentsRequest(
            path=_models.GetTasksIdAssignmentsRequestPath(task_id=task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_task_assignments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/tasks/{task_id}/assignments", _request.path.model_dump(by_alias=True)) if _request.path else "/tasks/{task_id}/assignments"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_task_assignments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_task_assignments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_task_assignments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Task assignments
@mcp.tool(
    title="Assign Task",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def assign_task(
    task_id: str | None = Field(None, alias="taskId", description="The unique identifier of the task to be assigned."),
    assign_to_id: str | None = Field(None, alias="assign_toId", description="The unique identifier of the user to assign the task to. Use the `login` parameter instead to specify the user by email address."),
    type_: Literal["task"] | None = Field(None, alias="type", description="The type of the item being assigned. Must always be set to 'task'."),
    login: str | None = Field(None, description="The email address of the user to assign the task to. Use the `id` parameter instead to specify the user by their unique user ID."),
) -> dict[str, Any] | ToolResult:
    """Assigns a task to a specific user by user ID or email address. A task can be assigned to multiple users by creating separate assignments."""

    # Construct request model with validation
    try:
        _request = _models.PostTaskAssignmentsRequest(
            body=_models.PostTaskAssignmentsRequestBody(task=_models.PostTaskAssignmentsRequestBodyTask(id_=task_id, type_=type_) if any(v is not None for v in [task_id, type_]) else None,
                assign_to=_models.PostTaskAssignmentsRequestBodyAssignTo(id_=assign_to_id, login=login) if any(v is not None for v in [assign_to_id, login]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for assign_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/task_assignments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("assign_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("assign_task", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="assign_task",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Task assignments
@mcp.tool(
    title="Get Task Assignment",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_task_assignment(task_assignment_id: str = Field(..., description="The unique identifier of the task assignment to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific task assignment, including its status, assignee, and associated task. Use this to inspect the current state of a single task assignment by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetTaskAssignmentsIdRequest(
            path=_models.GetTaskAssignmentsIdRequestPath(task_assignment_id=task_assignment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task_assignment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/task_assignments/{task_assignment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/task_assignments/{task_assignment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_task_assignment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_task_assignment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_task_assignment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Task assignments
@mcp.tool(
    title="Update Task Assignment",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_task_assignment(
    task_assignment_id: str = Field(..., description="The unique identifier of the task assignment to update."),
    message: str | None = Field(None, description="An optional message from the assignee to accompany the task assignment update."),
    resolution_state: Literal["completed", "incomplete", "approved", "rejected"] | None = Field(None, description="The resolution state to set for the task assignment. For tasks with action type 'complete', valid values are 'incomplete' or 'completed'. For tasks with action type 'review', valid values are 'incomplete', 'approved', or 'rejected'."),
) -> dict[str, Any] | ToolResult:
    """Updates a task assignment for a specific user, allowing changes to the resolution state or an optional assignee message. Supported resolution states depend on the task's action type (complete or review)."""

    # Construct request model with validation
    try:
        _request = _models.PutTaskAssignmentsIdRequest(
            path=_models.PutTaskAssignmentsIdRequestPath(task_assignment_id=task_assignment_id),
            body=_models.PutTaskAssignmentsIdRequestBody(message=message, resolution_state=resolution_state)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_task_assignment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/task_assignments/{task_assignment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/task_assignments/{task_assignment_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_task_assignment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_task_assignment", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_task_assignment",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Task assignments
@mcp.tool(
    title="Delete Task Assignment",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_task_assignment(task_assignment_id: str = Field(..., description="The unique identifier of the task assignment to delete.")) -> dict[str, Any] | ToolResult:
    """Removes a specific task assignment, unassigning the user from the associated task. This action permanently deletes the assignment record."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTaskAssignmentsIdRequest(
            path=_models.DeleteTaskAssignmentsIdRequestPath(task_assignment_id=task_assignment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_task_assignment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/task_assignments/{task_assignment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/task_assignments/{task_assignment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_task_assignment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_task_assignment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_task_assignment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared links (Files)
@mcp.tool(
    title="Get Shared Link File",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_shared_link_file(boxapi: str = Field(..., description="Authorization header value containing the shared link URL and an optional password, formatted as a key-value pair string using the shared_link and shared_link_password keys.")) -> dict[str, Any] | ToolResult:
    """Retrieves file information for a given shared link, supporting links originating from within or outside the current enterprise. Optionally returns shared link permission options when requested via the fields query parameter."""

    # Construct request model with validation
    try:
        _request = _models.GetSharedItemsRequest(
            header=_models.GetSharedItemsRequestHeader(boxapi=boxapi)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_shared_link_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shared_items"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_shared_link_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_shared_link_file", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_shared_link_file",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared links (Files)
@mcp.tool(
    title="Get File Shared Link",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_file_shared_link(
    file_id: str = Field(..., description="The unique identifier of the file whose shared link information you want to retrieve. The file ID can be found in the file's URL in the Box web application."),
    fields: str = Field(..., description="Specifies which fields to include in the response; must be set to request shared link data to be returned for the file."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the shared link details for a specific file, including its URL, access level, and permissions. Use this to inspect or confirm the sharing configuration of a file."""

    # Construct request model with validation
    try:
        _request = _models.GetFilesIdGetSharedLinkRequest(
            path=_models.GetFilesIdGetSharedLinkRequestPath(file_id=file_id),
            query=_models.GetFilesIdGetSharedLinkRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_shared_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}#get_shared_link", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}#get_shared_link"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_shared_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_shared_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_shared_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared links (Files)
@mcp.tool(
    title="Add File Shared Link",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def add_file_shared_link(
    file_id: str = Field(..., description="The unique identifier of the file to add a shared link to. Visible in the file's URL in the Box web application."),
    fields: str = Field(..., description="A comma-separated list of fields to include in the response. Must include 'shared_link' to return shared link details in the response."),
    access: Literal["open", "company", "collaborators"] | None = Field(None, description="The visibility level of the shared link. Use 'open' for anyone with the link, 'company' for internal users only (paid accounts only), or 'collaborators' for explicitly invited users only. Defaults to the enterprise admin setting if omitted."),
    password: str | None = Field(None, description="An optional password required to access the shared link. Must be at least eight characters and include a number, uppercase letter, or non-alphanumeric character. Can only be set when access is 'open'. Set to null to remove an existing password."),
    vanity_name: str | None = Field(None, description="A custom vanity slug appended to the shared link URL (e.g., https://app.box.com/v/{vanity_name}). Must be at least 12 characters. Avoid using vanity names for sensitive content as they are easier to guess.", min_length=12),
    unshared_at: str | None = Field(None, description="The ISO 8601 datetime at which the shared link expires and becomes inaccessible. Must be a future datetime. Only available to paid account users."),
    can_download: bool | None = Field(None, description="Whether the shared link permits downloading the file. Can only be set when access is 'open' or 'company'."),
    can_preview: bool | None = Field(None, description="Whether the shared link permits previewing the file. This value is always true and applies to all items within a folder when set on a folder shared link."),
    can_edit: bool | None = Field(None, description="Whether the shared link permits editing the file. Can only be set when access is 'open' or 'company', and requires can_download to also be true."),
) -> dict[str, Any] | ToolResult:
    """Creates or updates a shared link on a file, controlling access level, permissions, expiration, and optional password protection. Returns the file with the shared link fields populated."""

    # Construct request model with validation
    try:
        _request = _models.PutFilesIdAddSharedLinkRequest(
            path=_models.PutFilesIdAddSharedLinkRequestPath(file_id=file_id),
            query=_models.PutFilesIdAddSharedLinkRequestQuery(fields=fields),
            body=_models.PutFilesIdAddSharedLinkRequestBody(shared_link=_models.PutFilesIdAddSharedLinkRequestBodySharedLink(access=access, password=password, vanity_name=vanity_name, unshared_at=unshared_at,
                    permissions=_models.PutFilesIdAddSharedLinkRequestBodySharedLinkPermissions(can_download=can_download, can_preview=can_preview, can_edit=can_edit) if any(v is not None for v in [can_download, can_preview, can_edit]) else None) if any(v is not None for v in [access, password, vanity_name, unshared_at, can_download, can_preview, can_edit]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_file_shared_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}#add_shared_link", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}#add_shared_link"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_file_shared_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_file_shared_link", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_file_shared_link",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared links (Files)
@mcp.tool(
    title="Update File Shared Link",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_file_shared_link(
    file_id: str = Field(..., description="The unique identifier of the file whose shared link will be updated. The file ID can be found in the URL when viewing the file in the Box web application."),
    fields: str = Field(..., description="A comma-separated list of fields to include in the response. Must include 'shared_link' to ensure the updated shared link details are returned."),
    access: Literal["open", "company", "collaborators"] | None = Field(None, description="The visibility level of the shared link. Use 'open' for anyone with the link, 'company' for internal users only (paid accounts only), or 'collaborators' for explicitly invited users only. Defaults to the enterprise admin setting if omitted."),
    password: str | None = Field(None, description="An optional password required to access the shared link. Set to null to remove an existing password. Passwords must be at least 8 characters and include a number, uppercase letter, or special character. Can only be set when access is 'open'."),
    vanity_name: str | None = Field(None, description="A custom vanity name to use in the shared link URL path. Must be at least 12 characters. Avoid using vanity names for sensitive content as they are easier to guess than standard shared links.", min_length=12),
    unshared_at: str | None = Field(None, description="The ISO 8601 datetime at which the shared link will expire and become inaccessible. Must be a future date and time. Only available to paid account users."),
    can_download: bool | None = Field(None, description="Whether the shared link permits downloading of the file. Can only be set when access is 'open' or 'company'."),
    can_preview: bool | None = Field(None, description="Whether the shared link permits previewing of the file. This value is always true and applies to all items within a folder when set on a folder shared link."),
    can_edit: bool | None = Field(None, description="Whether the shared link permits editing of the file. Can only be set when access is 'open' or 'company', and requires can_download to also be true."),
) -> dict[str, Any] | ToolResult:
    """Updates the shared link settings on a specific file, including access level, password protection, expiration, and permissions. Use this to modify an existing shared link or configure a new one on the file."""

    # Construct request model with validation
    try:
        _request = _models.PutFilesIdUpdateSharedLinkRequest(
            path=_models.PutFilesIdUpdateSharedLinkRequestPath(file_id=file_id),
            query=_models.PutFilesIdUpdateSharedLinkRequestQuery(fields=fields),
            body=_models.PutFilesIdUpdateSharedLinkRequestBody(shared_link=_models.PutFilesIdUpdateSharedLinkRequestBodySharedLink(access=access, password=password, vanity_name=vanity_name, unshared_at=unshared_at,
                    permissions=_models.PutFilesIdUpdateSharedLinkRequestBodySharedLinkPermissions(can_download=can_download, can_preview=can_preview, can_edit=can_edit) if any(v is not None for v in [can_download, can_preview, can_edit]) else None) if any(v is not None for v in [access, password, vanity_name, unshared_at, can_download, can_preview, can_edit]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_file_shared_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}#update_shared_link", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}#update_shared_link"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_file_shared_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_file_shared_link", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_file_shared_link",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared links (Files)
@mcp.tool(
    title="Remove File Shared Link",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_file_shared_link(
    file_id: str = Field(..., description="The unique identifier of the file from which the shared link will be removed. The file ID can be found in the URL when viewing the file in the Box web application."),
    fields: str = Field(..., description="A comma-separated list of fields to include in the response. Must include 'shared_link' to confirm the shared link has been removed and retrieve the updated link state."),
    shared_link: dict[str, Any] | None = Field(None, description="Set this field to null to remove the shared link from the file. Omitting this field or providing any non-null value will not remove the link."),
) -> dict[str, Any] | ToolResult:
    """Removes an existing shared link from a file, revoking any previously granted public or shared access. Returns the updated file metadata with the shared link field cleared."""

    # Construct request model with validation
    try:
        _request = _models.PutFilesIdRemoveSharedLinkRequest(
            path=_models.PutFilesIdRemoveSharedLinkRequestPath(file_id=file_id),
            query=_models.PutFilesIdRemoveSharedLinkRequestQuery(fields=fields),
            body=_models.PutFilesIdRemoveSharedLinkRequestBody(shared_link=shared_link)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_file_shared_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}#remove_shared_link", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}#remove_shared_link"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_file_shared_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_file_shared_link", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_file_shared_link",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared links (Folders)
@mcp.tool(
    title="Get Folder From Shared Link",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_folder_from_shared_link(boxapi: str = Field(..., description="Authorization header containing the shared link URL and an optional password, formatted as a key-value string using the pattern shared_link=[link]&shared_link_password=[password].")) -> dict[str, Any] | ToolResult:
    """Retrieves folder metadata using a shared link, supporting links from within the current enterprise or external ones. Useful when only a shared link is available and full folder details are needed."""

    # Construct request model with validation
    try:
        _request = _models.GetSharedItemsFoldersRequest(
            header=_models.GetSharedItemsFoldersRequestHeader(boxapi=boxapi)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_folder_from_shared_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shared_items#folders"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_folder_from_shared_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_folder_from_shared_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_folder_from_shared_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared links (Folders)
@mcp.tool(
    title="Get Folder Shared Link",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_folder_shared_link(
    folder_id: str = Field(..., description="The unique identifier of the folder whose shared link you want to retrieve. The root folder of a Box account is always ID '0'; other folder IDs can be found in the URL when viewing the folder in the Box web app."),
    fields: str = Field(..., description="Must be set to 'shared_link' to explicitly request that shared link fields are included in the response. This field is required by the API to return shared link data."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the shared link details for a specific folder, including its URL, access level, and permissions. Use this to inspect or verify the sharing configuration of a folder."""

    # Construct request model with validation
    try:
        _request = _models.GetFoldersIdGetSharedLinkRequest(
            path=_models.GetFoldersIdGetSharedLinkRequestPath(folder_id=folder_id),
            query=_models.GetFoldersIdGetSharedLinkRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_folder_shared_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}#get_shared_link", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}#get_shared_link"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_folder_shared_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_folder_shared_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_folder_shared_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared links (Folders)
@mcp.tool(
    title="Add Folder Shared Link",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def add_folder_shared_link(
    folder_id: str = Field(..., description="The unique identifier of the folder to add a shared link to. The ID appears in the folder's URL in the Box web app, and the root folder is always ID `0`."),
    fields: str = Field(..., description="A comma-separated list of fields to include in the response. Must include `shared_link` to return the shared link details in the response."),
    access: Literal["open", "company", "collaborators"] | None = Field(None, description="The visibility level of the shared link: `open` for anyone with the link, `company` for users within the enterprise (paid accounts only), or `collaborators` for only invited collaborators. Omitting this field uses the enterprise admin's default access setting."),
    password: str | None = Field(None, description="An optional password required to access the shared link. Must be at least 8 characters and include a number, uppercase letter, or non-alphanumeric character. Can only be set when access is `open`; set to `null` to remove an existing password."),
    vanity_name: str | None = Field(None, description="A custom vanity name to use in the shared link URL path. Must be at least 12 characters. Avoid using vanity names for sensitive content as they are easier to guess than standard shared links.", min_length=12),
    unshared_at: str | None = Field(None, description="The ISO 8601 datetime at which the shared link expires and becomes inaccessible. Must be a future date and time, and can only be set by users on paid accounts."),
    can_download: bool | None = Field(None, description="Whether recipients of the shared link are permitted to download files in the folder. Can only be set when access is `open` or `company`."),
    can_preview: bool | None = Field(None, description="Whether recipients of the shared link are permitted to preview files in the folder. This value is always `true` and applies to all items within the folder."),
    can_edit: bool | None = Field(None, description="Whether recipients of the shared link are permitted to edit items. For folders, this value can only be `false`."),
) -> dict[str, Any] | ToolResult:
    """Adds or updates a shared link on a folder, controlling access level, password protection, expiration, and permissions for viewing or downloading folder contents."""

    # Construct request model with validation
    try:
        _request = _models.PutFoldersIdAddSharedLinkRequest(
            path=_models.PutFoldersIdAddSharedLinkRequestPath(folder_id=folder_id),
            query=_models.PutFoldersIdAddSharedLinkRequestQuery(fields=fields),
            body=_models.PutFoldersIdAddSharedLinkRequestBody(shared_link=_models.PutFoldersIdAddSharedLinkRequestBodySharedLink(access=access, password=password, vanity_name=vanity_name, unshared_at=unshared_at,
                    permissions=_models.PutFoldersIdAddSharedLinkRequestBodySharedLinkPermissions(can_download=can_download, can_preview=can_preview, can_edit=can_edit) if any(v is not None for v in [can_download, can_preview, can_edit]) else None) if any(v is not None for v in [access, password, vanity_name, unshared_at, can_download, can_preview, can_edit]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_folder_shared_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}#add_shared_link", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}#add_shared_link"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_folder_shared_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_folder_shared_link", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_folder_shared_link",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared links (Folders)
@mcp.tool(
    title="Update Folder Shared Link",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_folder_shared_link(
    folder_id: str = Field(..., description="The unique identifier of the folder whose shared link will be updated. The ID can be found in the folder's URL in the Box web app. The root folder is always ID `0`."),
    fields: str = Field(..., description="A comma-separated list of fields to include in the response. Must include `shared_link` to return the updated shared link details."),
    access: Literal["open", "company", "collaborators"] | None = Field(None, description="The access level for the shared link. Use `open` for anyone with the link, `company` for users within the enterprise (paid accounts only), or `collaborators` for only invited users. Defaults to the enterprise admin setting if omitted."),
    password: str | None = Field(None, description="An optional password required to access the shared link. Must be at least 8 characters and include a number, uppercase letter, or special character. Can only be set when access is `open`. Set to `null` to remove an existing password."),
    vanity_name: str | None = Field(None, description="A custom vanity name to use in the shared link URL path. Must be at least 12 characters. Avoid using vanity names for sensitive content as they are easier to guess than standard shared links.", min_length=12),
    unshared_at: str | None = Field(None, description="The ISO 8601 datetime at which the shared link will expire and become inaccessible. Must be a future date and time. Only available to paid account users."),
    can_download: bool | None = Field(None, description="Whether the shared link permits downloading of files. Can only be enabled when access is set to `open` or `company`."),
    can_preview: bool | None = Field(None, description="Whether the shared link permits previewing of files. This value is always `true` for folders and applies to all items within the folder."),
    can_edit: bool | None = Field(None, description="Whether the shared link permits editing of items. For folders, this value can only be set to `false`."),
) -> dict[str, Any] | ToolResult:
    """Updates the shared link settings on a specific folder, allowing you to configure access level, password protection, expiration, and permissions for the link."""

    # Construct request model with validation
    try:
        _request = _models.PutFoldersIdUpdateSharedLinkRequest(
            path=_models.PutFoldersIdUpdateSharedLinkRequestPath(folder_id=folder_id),
            query=_models.PutFoldersIdUpdateSharedLinkRequestQuery(fields=fields),
            body=_models.PutFoldersIdUpdateSharedLinkRequestBody(shared_link=_models.PutFoldersIdUpdateSharedLinkRequestBodySharedLink(access=access, password=password, vanity_name=vanity_name, unshared_at=unshared_at,
                    permissions=_models.PutFoldersIdUpdateSharedLinkRequestBodySharedLinkPermissions(can_download=can_download, can_preview=can_preview, can_edit=can_edit) if any(v is not None for v in [can_download, can_preview, can_edit]) else None) if any(v is not None for v in [access, password, vanity_name, unshared_at, can_download, can_preview, can_edit]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_folder_shared_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}#update_shared_link", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}#update_shared_link"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_folder_shared_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_folder_shared_link", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_folder_shared_link",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared links (Folders)
@mcp.tool(
    title="Remove Folder Shared Link",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_folder_shared_link(
    folder_id: str = Field(..., description="The unique identifier of the folder from which the shared link will be removed. The root folder of a Box account is always represented by the ID '0'."),
    fields: str = Field(..., description="A comma-separated list of fields to include in the response. Must include 'shared_link' to confirm the shared link has been removed from the folder."),
    shared_link: dict[str, Any] | None = Field(None, description="The shared link configuration object. Set this to null to remove the shared link from the folder and revoke any previously granted access."),
) -> dict[str, Any] | ToolResult:
    """Removes an existing shared link from a folder, revoking public or shared access. The shared_link field must be set to null to complete the removal."""

    # Construct request model with validation
    try:
        _request = _models.PutFoldersIdRemoveSharedLinkRequest(
            path=_models.PutFoldersIdRemoveSharedLinkRequestPath(folder_id=folder_id),
            query=_models.PutFoldersIdRemoveSharedLinkRequestQuery(fields=fields),
            body=_models.PutFoldersIdRemoveSharedLinkRequestBody(shared_link=shared_link)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_folder_shared_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_id}#remove_shared_link", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_id}#remove_shared_link"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_folder_shared_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_folder_shared_link", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_folder_shared_link",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Web links
@mcp.tool(
    title="Create Web Link",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_web_link(
    url: str | None = Field(None, description="The full URL the web link points to. Must begin with 'http://' or 'https://'."),
    id_: str | None = Field(None, alias="id", description="The ID of the parent folder where the web link will be created. Use '0' to target the root folder."),
    name: str | None = Field(None, description="A display name for the web link as it appears in the folder. If omitted, the URL is used as the name."),
    description: str | None = Field(None, description="An optional human-readable description providing additional context about the web link's destination or purpose."),
) -> dict[str, Any] | ToolResult:
    """Creates a web link object inside a specified folder, storing a URL as a navigable item within Box. Useful for bookmarking external resources directly within a folder hierarchy."""

    # Construct request model with validation
    try:
        _request = _models.PostWebLinksRequest(
            body=_models.PostWebLinksRequestBody(url=url, name=name, description=description,
                parent=_models.PostWebLinksRequestBodyParent(id_=id_) if any(v is not None for v in [id_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_web_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/web_links"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_web_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_web_link", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_web_link",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Web links
@mcp.tool(
    title="Get Web Link",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_web_link(web_link_id: str = Field(..., description="The unique identifier of the web link to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific web link, including its URL, name, and associated metadata. Useful for inspecting or displaying a saved web link by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetWebLinksIdRequest(
            path=_models.GetWebLinksIdRequestPath(web_link_id=web_link_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_web_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/web_links/{web_link_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/web_links/{web_link_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_web_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_web_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_web_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Trashed web links
@mcp.tool(
    title="Restore Web Link",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def restore_web_link(
    web_link_id: str = Field(..., description="The unique identifier of the web link to restore from the trash."),
    name: str | None = Field(None, description="An optional new name to assign to the web link upon restoration, useful if a naming conflict exists in the destination folder."),
    parent: _models.PostWebLinksIdBodyParent | None = Field(None, description="An optional parent folder object specifying an alternative destination to restore the web link into, used when the original parent folder has been deleted."),
) -> dict[str, Any] | ToolResult:
    """Restores a web link from the trash back to its original location or an alternative parent folder. An optional new name and parent folder can be specified if the original folder no longer exists."""

    # Construct request model with validation
    try:
        _request = _models.PostWebLinksIdRequest(
            path=_models.PostWebLinksIdRequestPath(web_link_id=web_link_id),
            body=_models.PostWebLinksIdRequestBody(name=name, parent=parent)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for restore_web_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/web_links/{web_link_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/web_links/{web_link_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("restore_web_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("restore_web_link", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="restore_web_link",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Web links
@mcp.tool(
    title="Update Web Link",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_web_link(
    web_link_id: str = Field(..., description="The unique identifier of the web link to update."),
    url: str | None = Field(None, description="The new destination URL for the web link. Must begin with 'http://' or 'https://'."),
    parent: _models.PutWebLinksIdBodyParent | None = Field(None, description="The parent folder to move the web link into. Provide the target folder's identifier to relocate the web link."),
    name: str | None = Field(None, description="A new display name for the web link. If omitted, the name defaults to the URL."),
    description: str | None = Field(None, description="A new human-readable description for the web link to provide additional context about its destination."),
    access: Literal["open", "company", "collaborators"] | None = Field(None, description="The visibility level for the shared link. Use 'open' for anyone with the link, 'company' for internal users only (paid accounts), or 'collaborators' for invited users only. Omitting this field applies the enterprise default."),
    password: str | None = Field(None, description="A password required to access the shared link. Must be at least eight characters and include a number, uppercase letter, or non-alphanumeric character. Can only be set when access is 'open'; set to null to remove an existing password."),
    vanity_name: str | None = Field(None, description="A custom vanity slug appended to the shared link URL path. Must be at least 12 characters. Avoid using vanity names for sensitive content as they are easier to guess than standard shared links.", min_length=12),
    unshared_at: str | None = Field(None, description="The ISO 8601 datetime at which the shared link expires and becomes inaccessible. Must be a future datetime and can only be set by users on paid accounts."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing web link object, allowing changes to its URL, name, description, parent location, and shared link settings such as access level, password, vanity name, and expiration."""

    # Construct request model with validation
    try:
        _request = _models.PutWebLinksIdRequest(
            path=_models.PutWebLinksIdRequestPath(web_link_id=web_link_id),
            body=_models.PutWebLinksIdRequestBody(url=url, parent=parent, name=name, description=description,
                shared_link=_models.PutWebLinksIdRequestBodySharedLink(access=access, password=password, vanity_name=vanity_name, unshared_at=unshared_at) if any(v is not None for v in [access, password, vanity_name, unshared_at]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_web_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/web_links/{web_link_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/web_links/{web_link_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_web_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_web_link", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_web_link",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Web links
@mcp.tool(
    title="Delete Web Link",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_web_link(web_link_id: str = Field(..., description="The unique identifier of the web link to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a web link by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWebLinksIdRequest(
            path=_models.DeleteWebLinksIdRequestPath(web_link_id=web_link_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_web_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/web_links/{web_link_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/web_links/{web_link_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_web_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_web_link", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_web_link",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Trashed web links
@mcp.tool(
    title="Get Trashed Web Link",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_trashed_web_link(web_link_id: str = Field(..., description="The unique identifier of the web link to retrieve from the trash.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a web link that has been moved to the trash. Useful for inspecting or restoring a trashed web link before permanent deletion."""

    # Construct request model with validation
    try:
        _request = _models.GetWebLinksIdTrashRequest(
            path=_models.GetWebLinksIdTrashRequestPath(web_link_id=web_link_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_trashed_web_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/web_links/{web_link_id}/trash", _request.path.model_dump(by_alias=True)) if _request.path else "/web_links/{web_link_id}/trash"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_trashed_web_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_trashed_web_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_trashed_web_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Trashed web links
@mcp.tool(
    title="Permanently Delete Web Link",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def permanently_delete_web_link(web_link_id: str = Field(..., description="The unique identifier of the web link to permanently delete from the trash.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a web link that is currently in the trash, removing it from Box entirely. This action is irreversible and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWebLinksIdTrashRequest(
            path=_models.DeleteWebLinksIdTrashRequestPath(web_link_id=web_link_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for permanently_delete_web_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/web_links/{web_link_id}/trash", _request.path.model_dump(by_alias=True)) if _request.path else "/web_links/{web_link_id}/trash"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("permanently_delete_web_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("permanently_delete_web_link", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="permanently_delete_web_link",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared links (Web Links)
@mcp.tool(
    title="Get Web Link from Shared Link",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_web_link_from_shared_link(boxapi: str = Field(..., description="Authorization header containing the shared link URL and an optional password, formatted as a key-value string. Both the shared link and password fields must follow the prescribed header format.")) -> dict[str, Any] | ToolResult:
    """Retrieves web link details using only a shared link URL, supporting links originating from within or outside the current enterprise. Useful when the web link ID is unknown and only the shared link is available."""

    # Construct request model with validation
    try:
        _request = _models.GetSharedItemsWebLinksRequest(
            header=_models.GetSharedItemsWebLinksRequestHeader(boxapi=boxapi)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_web_link_from_shared_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shared_items#web_links"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_web_link_from_shared_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_web_link_from_shared_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_web_link_from_shared_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared links (Web Links)
@mcp.tool(
    title="Get Web Link Shared Link",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_web_link_shared_link(
    web_link_id: str = Field(..., description="The unique identifier of the web link whose shared link information you want to retrieve."),
    fields: str = Field(..., description="Specifies which fields to include in the response; must be set to request shared link data to be returned for the web link."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the shared link details for a specific web link item. Use this to inspect sharing settings, permissions, and access information for a web link."""

    # Construct request model with validation
    try:
        _request = _models.GetWebLinksIdGetSharedLinkRequest(
            path=_models.GetWebLinksIdGetSharedLinkRequestPath(web_link_id=web_link_id),
            query=_models.GetWebLinksIdGetSharedLinkRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_web_link_shared_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/web_links/{web_link_id}#get_shared_link", _request.path.model_dump(by_alias=True)) if _request.path else "/web_links/{web_link_id}#get_shared_link"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_web_link_shared_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_web_link_shared_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_web_link_shared_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared links (Web Links)
@mcp.tool(
    title="Add Web Link Shared Link",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_web_link_shared_link(
    web_link_id: str = Field(..., description="The unique identifier of the web link to which the shared link will be added."),
    fields: str = Field(..., description="A comma-separated list of fields to include in the response; must include 'shared_link' to return the shared link details."),
    access: Literal["open", "company", "collaborators"] | None = Field(None, description="The visibility level of the shared link: 'open' allows anyone with the link, 'company' restricts to users within the enterprise (paid accounts only), and 'collaborators' restricts to explicitly invited users. Defaults to the enterprise admin setting if omitted."),
    password: str | None = Field(None, description="An optional password required to access the shared link; set to null to remove an existing password. Must be at least eight characters and include a number, uppercase letter, or non-alphanumeric character. Can only be set when access is 'open'."),
    vanity_name: str | None = Field(None, description="A custom vanity name used in the shared link URL path, forming a human-readable URL. Must be at least 12 characters; avoid using vanity names for sensitive content as they are easier to guess.", min_length=12),
    unshared_at: str | None = Field(None, description="The ISO 8601 datetime at which the shared link will automatically expire and become inaccessible. Must be a future datetime and can only be set by users on paid accounts."),
    can_download: bool | None = Field(None, description="Whether recipients of the shared link are permitted to download the web link. Can only be set when access is 'open' or 'company'."),
    can_preview: bool | None = Field(None, description="Whether recipients of the shared link are permitted to preview the web link. This value is always true and also applies to items within a shared folder."),
    can_edit: bool | None = Field(None, description="Whether recipients of the shared link are permitted to edit the item. Can only be true when the item type is a file."),
) -> dict[str, Any] | ToolResult:
    """Adds or updates a shared link on a web link item, controlling access level, password protection, expiration, and permissions. Returns the web link with the shared link fields populated."""

    # Construct request model with validation
    try:
        _request = _models.PutWebLinksIdAddSharedLinkRequest(
            path=_models.PutWebLinksIdAddSharedLinkRequestPath(web_link_id=web_link_id),
            query=_models.PutWebLinksIdAddSharedLinkRequestQuery(fields=fields),
            body=_models.PutWebLinksIdAddSharedLinkRequestBody(shared_link=_models.PutWebLinksIdAddSharedLinkRequestBodySharedLink(access=access, password=password, vanity_name=vanity_name, unshared_at=unshared_at,
                    permissions=_models.PutWebLinksIdAddSharedLinkRequestBodySharedLinkPermissions(can_download=can_download, can_preview=can_preview, can_edit=can_edit) if any(v is not None for v in [can_download, can_preview, can_edit]) else None) if any(v is not None for v in [access, password, vanity_name, unshared_at, can_download, can_preview, can_edit]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_web_link_shared_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/web_links/{web_link_id}#add_shared_link", _request.path.model_dump(by_alias=True)) if _request.path else "/web_links/{web_link_id}#add_shared_link"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_web_link_shared_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_web_link_shared_link", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_web_link_shared_link",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared links (Web Links)
@mcp.tool(
    title="Update Web Link Shared Link",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_web_link_shared_link(
    web_link_id: str = Field(..., description="The unique identifier of the web link whose shared link settings will be updated."),
    fields: str = Field(..., description="A comma-separated list of fields to include in the response; must include 'shared_link' to return shared link details."),
    access: Literal["open", "company", "collaborators"] | None = Field(None, description="The visibility level of the shared link: 'open' allows anyone with the link, 'company' restricts to users within the enterprise (paid accounts only), and 'collaborators' restricts to invited collaborators only. Defaults to the enterprise admin setting if omitted."),
    password: str | None = Field(None, description="An optional password required to access the shared link; set to null to remove an existing password. Must be at least eight characters and include a number, uppercase letter, or non-alphanumeric character. Can only be set when access is 'open'."),
    vanity_name: str | None = Field(None, description="A custom vanity name to use in the shared link URL path; must be at least 12 characters. Avoid using vanity names for sensitive content as they are easier to guess than standard shared links.", min_length=12),
    unshared_at: str | None = Field(None, description="The ISO 8601 datetime at which the shared link will expire and become inaccessible; must be a future date and time. Only available to paid account users."),
    can_download: bool | None = Field(None, description="Whether the shared link permits downloading of the web link. Can only be set when access is 'open' or 'company'."),
    can_preview: bool | None = Field(None, description="Whether the shared link permits previewing of the web link; this value is always true and also applies to items within a shared folder."),
    can_edit: bool | None = Field(None, description="Whether the shared link permits editing; can only be true when the item type is a file."),
) -> dict[str, Any] | ToolResult:
    """Updates the shared link settings on an existing web link, allowing you to control access level, password protection, expiration, and permissions."""

    # Construct request model with validation
    try:
        _request = _models.PutWebLinksIdUpdateSharedLinkRequest(
            path=_models.PutWebLinksIdUpdateSharedLinkRequestPath(web_link_id=web_link_id),
            query=_models.PutWebLinksIdUpdateSharedLinkRequestQuery(fields=fields),
            body=_models.PutWebLinksIdUpdateSharedLinkRequestBody(shared_link=_models.PutWebLinksIdUpdateSharedLinkRequestBodySharedLink(access=access, password=password, vanity_name=vanity_name, unshared_at=unshared_at,
                    permissions=_models.PutWebLinksIdUpdateSharedLinkRequestBodySharedLinkPermissions(can_download=can_download, can_preview=can_preview, can_edit=can_edit) if any(v is not None for v in [can_download, can_preview, can_edit]) else None) if any(v is not None for v in [access, password, vanity_name, unshared_at, can_download, can_preview, can_edit]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_web_link_shared_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/web_links/{web_link_id}#update_shared_link", _request.path.model_dump(by_alias=True)) if _request.path else "/web_links/{web_link_id}#update_shared_link"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_web_link_shared_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_web_link_shared_link", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_web_link_shared_link",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared links (Web Links)
@mcp.tool(
    title="Remove Web Link Shared Link",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_web_link_shared_link(
    web_link_id: str = Field(..., description="The unique identifier of the web link from which the shared link will be removed."),
    fields: str = Field(..., description="A comma-separated list of fields to include in the response; must include 'shared_link' to confirm the shared link has been removed."),
    shared_link: dict[str, Any] | None = Field(None, description="Set this field to null to remove the shared link from the web link; omitting or providing any other value will not revoke the link."),
) -> dict[str, Any] | ToolResult:
    """Removes the shared link from a specified web link, revoking any previously granted public or shared access. The updated web link object is returned with the shared link field reflected."""

    # Construct request model with validation
    try:
        _request = _models.PutWebLinksIdRemoveSharedLinkRequest(
            path=_models.PutWebLinksIdRemoveSharedLinkRequestPath(web_link_id=web_link_id),
            query=_models.PutWebLinksIdRemoveSharedLinkRequestQuery(fields=fields),
            body=_models.PutWebLinksIdRemoveSharedLinkRequestBody(shared_link=shared_link)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_web_link_shared_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/web_links/{web_link_id}#remove_shared_link", _request.path.model_dump(by_alias=True)) if _request.path else "/web_links/{web_link_id}#remove_shared_link"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_web_link_shared_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_web_link_shared_link", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_web_link_shared_link",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Shared links (App Items)
@mcp.tool(
    title="Get App Item From Shared Link",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_app_item_from_shared_link(boxapi: str = Field(..., description="A header value containing the shared link URL and an optional password, formatted as a key-value pair string using the pattern `shared_link=[link]&shared_link_password=[password]`.")) -> dict[str, Any] | ToolResult:
    """Retrieves the app item associated with a given shared link, which may originate from the current enterprise or an external one. Requires the shared link URL and an optional password passed as a formatted header value."""

    # Construct request model with validation
    try:
        _request = _models.GetSharedItemsAppItemsRequest(
            header=_models.GetSharedItemsAppItemsRequestHeader(boxapi=boxapi)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_app_item_from_shared_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shared_items#app_items"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_app_item_from_shared_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_app_item_from_shared_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_app_item_from_shared_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
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
    filter_term: str | None = Field(None, description="Narrows results to users whose name or login starts with the given term. For externally managed users, the term must be an exact match and will return at most one result."),
    user_type: Literal["all", "managed", "external"] | None = Field(None, description="Filters results by user category: 'all' includes every user type with partial name/login matching (exact match required for external users), 'managed' returns only managed and app users with partial matching, and 'external' returns only external users whose login exactly matches the filter term."),
    external_app_user_id: str | None = Field(None, description="Restricts results to app users that were created with the specified external_app_user_id value, allowing lookup of app users by your own identifier assigned at creation time."),
    offset: str | None = Field(None, description="Zero-based index of the first item to include in the response, used for paginating through large result sets. Must not exceed 10000."),
    limit: str | None = Field(None, description="Maximum number of users to return in a single response page. Accepts values up to 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all enterprise users, including their user ID, public name, and login. Requires the authenticated user and application to have enterprise-wide user lookup permissions."""

    _offset = _parse_int(offset)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetUsersRequest(
            query=_models.GetUsersRequestQuery(filter_term=filter_term, user_type=user_type, external_app_user_id=external_app_user_id, offset=_offset, limit=_limit)
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
    title="Create User",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_user(
    is_platform_access_only: bool | None = Field(None, description="When set to true, designates this user as a platform (app) user rather than a standard managed enterprise user."),
    role: Literal["coadmin", "user"] | None = Field(None, description="The user's role within the enterprise, either a co-administrator with elevated privileges or a standard user."),
    language: str | None = Field(None, description="The display language for the user's Box interface, formatted as a modified ISO 639-1 language code."),
    is_sync_enabled: bool | None = Field(None, description="Whether the user is permitted to use Box Sync to synchronize files to their local device."),
    job_title: str | None = Field(None, description="The user's job title as displayed in their profile, limited to 100 characters.", max_length=100),
    phone: str | None = Field(None, description="The user's phone number as displayed in their profile, limited to 100 characters.", max_length=100),
    address: str | None = Field(None, description="The user's physical address as displayed in their profile, limited to 255 characters.", max_length=255),
    space_amount: str | None = Field(None, description="The total storage quota allocated to the user in bytes. Use -1 to grant unlimited storage."),
    tracking_codes: list[_models.TrackingCode] | None = Field(None, description="A list of tracking code objects (each with a name and value) used to categorize users for admin reporting. This feature must be enabled for the enterprise before use; order is not significant."),
    can_see_managed_users: bool | None = Field(None, description="Whether the user can view and search other managed users within the enterprise in their contact list."),
    timezone_: str | None = Field(None, alias="timezone", description="The user's local timezone, used for scheduling and display purposes, specified as a timezone identifier string."),
    is_external_collab_restricted: bool | None = Field(None, description="When set to true, restricts the user from collaborating on content with users outside the enterprise."),
    is_exempt_from_device_limits: bool | None = Field(None, description="When set to true, exempts the user from the enterprise-wide limit on the number of devices they can log in from."),
    is_exempt_from_login_verification: bool | None = Field(None, description="When set to true, exempts the user from the enterprise's two-factor authentication requirement at login."),
    status: Literal["active", "inactive", "cannot_delete_edit", "cannot_delete_edit_upload"] | None = Field(None, description="The initial account status for the user, controlling their ability to log in and interact with content."),
    external_app_user_id: str | None = Field(None, description="A custom identifier from an external identity provider that can be used to look up and map this Box user to an external system's user record."),
    name_and_login: str | None = Field(None, description="The user's display name and login email in RFC 5322 format: \"Display Name <user@example.com>\". The login email is required unless is_platform_access_only is true, in which case you may omit the angle-bracket portion and supply only the display name."),
) -> dict[str, Any] | ToolResult:
    """Creates a new managed or app user within a Box enterprise account. Requires admin-level permissions on the calling user or application."""

    # Call helper functions
    name_and_login_parsed = parse_name_and_login(name_and_login)

    _space_amount = _parse_int(space_amount)

    # Construct request model with validation
    try:
        _request = _models.PostUsersRequest(
            body=_models.PostUsersRequestBody(is_platform_access_only=is_platform_access_only, role=role, language=language, is_sync_enabled=is_sync_enabled, job_title=job_title, phone=phone, address=address, space_amount=_space_amount, tracking_codes=tracking_codes, can_see_managed_users=can_see_managed_users, timezone_=timezone_, is_external_collab_restricted=is_external_collab_restricted, is_exempt_from_device_limits=is_exempt_from_device_limits, is_exempt_from_login_verification=is_exempt_from_login_verification, status=status, external_app_user_id=external_app_user_id, name=name_and_login_parsed.get('name') if name_and_login_parsed else None, login=name_and_login_parsed.get('login') if name_and_login_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool(
    title="Get Current User",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_current_user() -> dict[str, Any] | ToolResult:
    """Retrieves profile and account information for the currently authenticated user, whether that is an OAuth 2.0 authorizing user, a JWT service account, or an impersonated user specified via the As-User header."""

    # Extract parameters for API call
    _http_path = "/users/me"
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

# Tags: Session termination
@mcp.tool(
    title="Terminate User Sessions",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def terminate_user_sessions(
    user_ids: list[str] | None = Field(None, description="A list of unique user IDs identifying the accounts whose sessions should be terminated. Order is not significant; each entry should be a valid numeric user ID string."),
    user_logins: list[str] | None = Field(None, description="A list of user login email addresses identifying the accounts whose sessions should be terminated. Order is not significant; each entry should be a valid email address associated with a user account."),
) -> dict[str, Any] | ToolResult:
    """Terminates active sessions for one or more users by dispatching asynchronous jobs, after validating the caller's roles and permissions. Accepts user IDs, user logins, or both to identify the target accounts."""

    # Construct request model with validation
    try:
        _request = _models.PostUsersTerminateSessionsRequest(
            body=_models.PostUsersTerminateSessionsRequestBody(user_ids=user_ids, user_logins=user_logins)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for terminate_user_sessions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users/terminate_sessions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("terminate_user_sessions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("terminate_user_sessions", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="terminate_user_sessions",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
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
async def get_user(user_id: str = Field(..., description="The unique identifier of the user whose information you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves profile and account information for a specific user within the enterprise. Also returns a limited set of fields for external collaborators, with restricted fields returning null."""

    # Construct request model with validation
    try:
        _request = _models.GetUsersIdRequest(
            path=_models.GetUsersIdRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}"
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
@mcp.tool(
    title="Update User",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_user(
    user_id: str = Field(..., description="The unique identifier of the user to update."),
    enterprise: str | None = Field(None, description="Set to null to remove the user from the enterprise and convert them to a free user."),
    notify: bool | None = Field(None, description="Whether the user should receive an email notification when they are rolled out of the enterprise."),
    name: str | None = Field(None, description="The display name of the user. Maximum 50 characters.", max_length=50),
    login: str | None = Field(None, description="The primary email address the user uses to log in. Cannot be changed if the target user's email address has not been confirmed."),
    role: Literal["coadmin", "user"] | None = Field(None, description="The user's role within the enterprise. Use 'coadmin' to grant co-administrator privileges or 'user' for a standard role."),
    language: str | None = Field(None, description="The user's preferred language, specified as a modified ISO 639-1 language code."),
    is_sync_enabled: bool | None = Field(None, description="Whether the user is permitted to use Box Sync to synchronize files to their local device."),
    job_title: str | None = Field(None, description="The user's job title as displayed on their profile. Maximum 100 characters.", max_length=100),
    phone: str | None = Field(None, description="The user's phone number. Maximum 100 characters.", max_length=100),
    address: str | None = Field(None, description="The user's physical address. Maximum 255 characters.", max_length=255),
    tracking_codes: list[_models.TrackingCode] | None = Field(None, description="A list of tracking code objects assigned to the user, used by admins to generate reports and group users by attributes. This feature must be enabled for the enterprise before use."),
    can_see_managed_users: bool | None = Field(None, description="Whether the user can see other enterprise users in their contact list."),
    timezone_: str | None = Field(None, alias="timezone", description="The user's timezone, specified as a valid IANA timezone identifier."),
    is_external_collab_restricted: bool | None = Field(None, description="Whether the user is restricted from collaborating with users outside the enterprise. Set to true to block external collaboration."),
    is_exempt_from_device_limits: bool | None = Field(None, description="Whether the user is exempt from the enterprise-wide limit on the number of devices they can log in from."),
    is_exempt_from_login_verification: bool | None = Field(None, description="Whether the user is exempt from two-factor authentication requirements. Set to true to bypass login verification."),
    is_password_reset_required: bool | None = Field(None, description="Whether the user will be required to reset their password on their next login."),
    status: Literal["active", "inactive", "cannot_delete_edit", "cannot_delete_edit_upload"] | None = Field(None, description="The user's account status. Use 'inactive' to deactivate the account, or 'cannot_delete_edit'/'cannot_delete_edit_upload' to apply restrictions."),
    space_amount: str | None = Field(None, description="The user's total available storage quota in bytes. Set to -1 to grant unlimited storage."),
    email: str | None = Field(None, description="The email address to which enterprise notifications for this user will be sent."),
    external_app_user_id: str | None = Field(None, description="An external identifier linking this Box app user to a user in an external identity provider. Can only be updated using a token from the application that originally created the app user."),
) -> dict[str, Any] | ToolResult:
    """Updates profile, permissions, and account settings for a managed or app user within an enterprise. Requires admin-level permissions to execute."""

    _space_amount = _parse_int(space_amount)

    # Construct request model with validation
    try:
        _request = _models.PutUsersIdRequest(
            path=_models.PutUsersIdRequestPath(user_id=user_id),
            body=_models.PutUsersIdRequestBody(enterprise=enterprise, notify=notify, name=name, login=login, role=role, language=language, is_sync_enabled=is_sync_enabled, job_title=job_title, phone=phone, address=address, tracking_codes=tracking_codes, can_see_managed_users=can_see_managed_users, timezone_=timezone_, is_external_collab_restricted=is_external_collab_restricted, is_exempt_from_device_limits=is_exempt_from_device_limits, is_exempt_from_login_verification=is_exempt_from_login_verification, is_password_reset_required=is_password_reset_required, status=status, space_amount=_space_amount, external_app_user_id=external_app_user_id,
                notification_email=_models.PutUsersIdRequestBodyNotificationEmail(email=email) if any(v is not None for v in [email]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}"
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
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool(
    title="Delete User",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_user(
    user_id: str = Field(..., description="The unique identifier of the user to delete."),
    notify: bool | None = Field(None, description="Whether to send the user an email notification informing them of their account deletion."),
    force: bool | None = Field(None, description="When set to true, bypasses deletion safeguards and removes the user even if they still own files, were recently active, or recently joined the enterprise from a free account; their owned files will also be deleted."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a user account from the enterprise. By default, deletion is blocked if the user owns content, was recently active, or recently joined from a free account; use the force parameter to override these safeguards or move owned content beforehand."""

    # Construct request model with validation
    try:
        _request = _models.DeleteUsersIdRequest(
            path=_models.DeleteUsersIdRequestPath(user_id=user_id),
            query=_models.DeleteUsersIdRequestQuery(notify=notify, force=force)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_user", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_user",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User avatars
@mcp.tool(
    title="Get User Avatar",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_user_avatar(user_id: str = Field(..., description="The unique identifier of the user whose avatar image should be retrieved.")) -> dict[str, Any] | ToolResult:
    """Retrieves the avatar image for a specified user. Returns the user's profile picture as an image resource."""

    # Construct request model with validation
    try:
        _request = _models.GetUsersIdAvatarRequest(
            path=_models.GetUsersIdAvatarRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_avatar: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/avatar", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/avatar"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_avatar")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_avatar", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_avatar",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User avatars
@mcp.tool(
    title="Upload User Avatar",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def upload_user_avatar(
    user_id: str = Field(..., description="The unique identifier of the user whose avatar is being added or updated."),
    pic: str | None = Field(None, description="Base64-encoded file content for upload. The image file to upload as the user's avatar. Must be a JPG or PNG file and cannot exceed 1MB in size.", json_schema_extra={'format': 'byte'}),
) -> dict[str, Any] | ToolResult:
    """Adds or replaces the avatar image for a specified user. Accepts JPG or PNG files up to 1MB in size."""

    # Construct request model with validation
    try:
        _request = _models.PostUsersIdAvatarRequest(
            path=_models.PostUsersIdAvatarRequestPath(user_id=user_id),
            body=_models.PostUsersIdAvatarRequestBody(pic=pic)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_user_avatar: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/avatar", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/avatar"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_user_avatar")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_user_avatar", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_user_avatar",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["pic"],
        headers=_http_headers,
    )

    return _response_data

# Tags: User avatars
@mcp.tool(
    title="Delete User Avatar",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_user_avatar(user_id: str = Field(..., description="The unique identifier of the user whose avatar will be permanently deleted.")) -> dict[str, Any] | ToolResult:
    """Permanently removes the avatar image for the specified user. This action is irreversible and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteUsersIdAvatarRequest(
            path=_models.DeleteUsersIdAvatarRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user_avatar: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/avatar", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/avatar"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_user_avatar")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_user_avatar", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_user_avatar",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Transfer folders
@mcp.tool(
    title="Transfer User Folders",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def transfer_user_folders(
    user_id: str = Field(..., description="The unique identifier of the user whose root folder and all owned content will be transferred."),
    notify: bool | None = Field(None, description="Whether to send email notifications to relevant users about the transfer action being performed."),
    id_: str | None = Field(None, alias="id", description="The unique identifier of the destination user who will receive ownership of the transferred folders and files."),
) -> dict[str, Any] | ToolResult:
    """Transfers all files, folders, and workflows owned by a specified user into another user's account by moving the root folder. Requires administrative permissions; large transfers run asynchronously, and admins receive an email upon completion."""

    # Construct request model with validation
    try:
        _request = _models.PutUsersIdFolders0Request(
            path=_models.PutUsersIdFolders0RequestPath(user_id=user_id),
            query=_models.PutUsersIdFolders0RequestQuery(notify=notify),
            body=_models.PutUsersIdFolders0RequestBody(owned_by=_models.PutUsersIdFolders0RequestBodyOwnedBy(id_=id_) if any(v is not None for v in [id_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for transfer_user_folders: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/folders/0", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/folders/0"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("transfer_user_folders")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("transfer_user_folders", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="transfer_user_folders",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Email aliases
@mcp.tool(
    title="List User Email Aliases",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_user_email_aliases(user_id: str = Field(..., description="The unique identifier of the user whose email aliases should be retrieved.")) -> dict[str, Any] | ToolResult:
    """Retrieves all secondary email aliases associated with a specific user account. Note that the user's primary login email is not included in the returned collection."""

    # Construct request model with validation
    try:
        _request = _models.GetUsersIdEmailAliasesRequest(
            path=_models.GetUsersIdEmailAliasesRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_email_aliases: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/email_aliases", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/email_aliases"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_email_aliases")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_email_aliases", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_email_aliases",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Email aliases
@mcp.tool(
    title="Create Email Alias",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_email_alias(
    user_id: str = Field(..., description="The unique identifier of the user account to which the email alias will be added."),
    email: str | None = Field(None, description="The email address to register as an alias on the user account. The domain portion must be verified and registered to your enterprise before use."),
) -> dict[str, Any] | ToolResult:
    """Adds a new email alias to an existing user account, allowing the user to send and receive email under an additional address. The alias domain must be registered and verified under your enterprise."""

    # Construct request model with validation
    try:
        _request = _models.PostUsersIdEmailAliasesRequest(
            path=_models.PostUsersIdEmailAliasesRequestPath(user_id=user_id),
            body=_models.PostUsersIdEmailAliasesRequestBody(email=email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_email_alias: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/email_aliases", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/email_aliases"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_email_alias")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_email_alias", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_email_alias",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Email aliases
@mcp.tool(
    title="Remove User Email Alias",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_user_email_alias(
    user_id: str = Field(..., description="The unique identifier of the user whose email alias will be removed."),
    email_alias_id: str = Field(..., description="The unique identifier of the email alias to remove from the user."),
) -> dict[str, Any] | ToolResult:
    """Removes a specific email alias from a user's account. Once removed, the alias can no longer be used to identify or contact the user."""

    # Construct request model with validation
    try:
        _request = _models.DeleteUsersIdEmailAliasesIdRequest(
            path=_models.DeleteUsersIdEmailAliasesIdRequestPath(user_id=user_id, email_alias_id=email_alias_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_user_email_alias: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/email_aliases/{email_alias_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/email_aliases/{email_alias_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_user_email_alias")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_user_email_alias", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_user_email_alias",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Group memberships
@mcp.tool(
    title="List User Memberships",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_user_memberships(
    user_id: str = Field(..., description="The unique identifier of the user whose group memberships are being retrieved."),
    limit: str | None = Field(None, description="The maximum number of group memberships to return per page. Accepts values up to 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all group memberships for a specified user. Accessible only to members of the same group or users with admin-level permissions."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetUsersIdMembershipsRequest(
            path=_models.GetUsersIdMembershipsRequestPath(user_id=user_id),
            query=_models.GetUsersIdMembershipsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_memberships: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/memberships", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/memberships"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_memberships")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_memberships", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_memberships",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Invites
@mcp.tool(
    title="Invite Enterprise User",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def invite_enterprise_user(
    id_: str | None = Field(None, alias="id", description="The unique identifier of the enterprise to which the user is being invited."),
    login: str | None = Field(None, description="The email address (login) of the existing Box user to invite to the enterprise."),
) -> dict[str, Any] | ToolResult:
    """Invites an existing Box user to join an enterprise by sending them an email prompt to accept within the Box web application. The user must already have a Box account and must not currently belong to another enterprise."""

    # Construct request model with validation
    try:
        _request = _models.PostInvitesRequest(
            body=_models.PostInvitesRequestBody(enterprise=_models.PostInvitesRequestBodyEnterprise(id_=id_) if any(v is not None for v in [id_]) else None,
                actionable_by=_models.PostInvitesRequestBodyActionableBy(login=login) if any(v is not None for v in [login]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for invite_enterprise_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/invites"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("invite_enterprise_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("invite_enterprise_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="invite_enterprise_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Invites
@mcp.tool(
    title="Get Invite",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_invite(invite_id: str = Field(..., description="The unique identifier of the invite whose status you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the current status of a specific user invite. Useful for checking whether an invite has been accepted, is pending, or has expired."""

    # Construct request model with validation
    try:
        _request = _models.GetInvitesIdRequest(
            path=_models.GetInvitesIdRequestPath(invite_id=invite_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_invite: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/invites/{invite_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/invites/{invite_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_invite")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_invite", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_invite",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool(
    title="List Groups",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_groups(
    filter_term: str | None = Field(None, description="Narrows results to only groups whose name begins with the specified search term. Omitting this parameter returns all groups."),
    limit: str | None = Field(None, description="Maximum number of groups to return in a single page of results. Accepts values between 1 and 1000."),
    offset: str | None = Field(None, description="Zero-based index of the first item to include in the response, used for paginating through results. Offsets greater than 10000 are not permitted and will return a 400 error."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all groups belonging to the enterprise, with optional filtering by name. Requires admin permissions to access enterprise group data."""

    _limit = _parse_int(limit)
    _offset = _parse_int(offset)

    # Construct request model with validation
    try:
        _request = _models.GetGroupsRequest(
            query=_models.GetGroupsRequestQuery(filter_term=filter_term, limit=_limit, offset=_offset)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/groups"
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
@mcp.tool(
    title="Create Group",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_group(
    name: str | None = Field(None, description="The display name for the new group, which must be unique across the entire enterprise."),
    provenance: str | None = Field(None, description="Identifies the external source system this group originates from (e.g., Active Directory or Okta). Setting this prevents Box admins from editing the group name or members via the Box web app, enabling one-way sync. Maximum 255 characters.", max_length=255),
    external_sync_identifier: str | None = Field(None, description="An arbitrary identifier used to link this Box group to a corresponding group in an external system, such as an Active Directory Object ID or Google Group ID. Using this field is recommended to prevent sync issues when group names change."),
    description: str | None = Field(None, description="A human-readable description providing additional context about the group's purpose or origin. Maximum 255 characters.", max_length=255),
    invitability_level: Literal["admins_only", "admins_and_members", "all_managed_users"] | None = Field(None, description="Controls who can invite this group to collaborate on folders. Use `admins_only` to restrict invitations to enterprise admins, co-admins, and the group's admin; `admins_and_members` to also allow group members; or `all_managed_users` to allow any managed user in the enterprise."),
    member_viewability_level: Literal["admins_only", "admins_and_members", "all_managed_users"] | None = Field(None, description="Controls who can view the membership list of this group. Use `admins_only` to restrict visibility to enterprise admins, co-admins, and the group's admin; `admins_and_members` to also allow group members; or `all_managed_users` to allow any managed user in the enterprise."),
) -> dict[str, Any] | ToolResult:
    """Creates a new user group within an enterprise account. Requires admin permissions; supports linking to external directory systems like Active Directory or Okta for one-way sync."""

    # Construct request model with validation
    try:
        _request = _models.PostGroupsRequest(
            body=_models.PostGroupsRequestBody(name=name, provenance=provenance, external_sync_identifier=external_sync_identifier, description=description, invitability_level=invitability_level, member_viewability_level=member_viewability_level)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/groups"
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

# Tags: Session termination
@mcp.tool(
    title="Terminate Group Sessions",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def terminate_group_sessions(group_ids: list[str] | None = Field(None, description="A list of group IDs whose sessions should be terminated. Order is not significant; each item should be a valid group ID string.")) -> dict[str, Any] | ToolResult:
    """Terminates all active sessions for one or more user groups by creating asynchronous jobs after validating group roles and permissions. Returns the status of the termination request."""

    # Construct request model with validation
    try:
        _request = _models.PostGroupsTerminateSessionsRequest(
            body=_models.PostGroupsTerminateSessionsRequestBody(group_ids=group_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for terminate_group_sessions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/groups/terminate_sessions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("terminate_group_sessions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("terminate_group_sessions", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="terminate_group_sessions",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool(
    title="Get Group",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_group(group_id: str = Field(..., description="The unique identifier of the group to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific group by its ID. Only group members or users with admin-level permissions can access this endpoint."""

    # Construct request model with validation
    try:
        _request = _models.GetGroupsIdRequest(
            path=_models.GetGroupsIdRequestPath(group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{group_id}"
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

# Tags: Groups
@mcp.tool(
    title="Update Group",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_group(
    group_id: str = Field(..., description="The unique identifier of the group to update."),
    name: str | None = Field(None, description="The updated display name for the group, which must remain unique across the enterprise."),
    provenance: str | None = Field(None, description="Identifies the external source system this group originates from (e.g., Active Directory or Okta). Setting this value prevents Box admins from editing the group name or members directly in the Box web application, enabling one-way sync behavior. Maximum 255 characters.", max_length=255),
    external_sync_identifier: str | None = Field(None, description="An arbitrary identifier used to link this Box group to a corresponding group in an external system, such as an Active Directory Object ID or Google Group ID. Using this field is recommended to prevent sync issues when group names change in either system."),
    description: str | None = Field(None, description="A human-readable description providing additional context about the group's purpose or origin. Maximum 255 characters.", max_length=255),
    invitability_level: Literal["admins_only", "admins_and_members", "all_managed_users"] | None = Field(None, description="Controls who can invite this group to collaborate on folders. Use `admins_only` to restrict invitations to enterprise and group admins, `admins_and_members` to also allow group members, or `all_managed_users` to allow any managed user in the enterprise."),
    member_viewability_level: Literal["admins_only", "admins_and_members", "all_managed_users"] | None = Field(None, description="Controls who can view the membership list of this group. Use `admins_only` to restrict visibility to enterprise and group admins, `admins_and_members` to also allow group members, or `all_managed_users` to allow any managed user in the enterprise."),
) -> dict[str, Any] | ToolResult:
    """Updates the properties of an existing group, such as its name, description, sync identifiers, and visibility settings. Only group admins or enterprise admins have permission to perform this operation."""

    # Construct request model with validation
    try:
        _request = _models.PutGroupsIdRequest(
            path=_models.PutGroupsIdRequestPath(group_id=group_id),
            body=_models.PutGroupsIdRequestBody(name=name, provenance=provenance, external_sync_identifier=external_sync_identifier, description=description, invitability_level=invitability_level, member_viewability_level=member_viewability_level)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{group_id}"
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

# Tags: Groups
@mcp.tool(
    title="Delete Group",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_group(group_id: str = Field(..., description="The unique identifier of the group to be permanently deleted.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a group and all associated data. Requires admin-level permissions to perform this action."""

    # Construct request model with validation
    try:
        _request = _models.DeleteGroupsIdRequest(
            path=_models.DeleteGroupsIdRequestPath(group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{group_id}"
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

# Tags: Group memberships
@mcp.tool(
    title="List Group Members",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_group_members(
    group_id: str = Field(..., description="The unique identifier of the group whose members you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of membership records to return per page. Accepts values up to 1000; omit to use the API default."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all membership records for a specified group, including details about each member. Accessible only to members of the group or users with admin-level permissions."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetGroupsIdMembershipsRequest(
            path=_models.GetGroupsIdMembershipsRequestPath(group_id=group_id),
            query=_models.GetGroupsIdMembershipsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_group_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{group_id}/memberships", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{group_id}/memberships"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_group_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_group_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_group_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collaborations (List)
@mcp.tool(
    title="List Group Collaborations",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_group_collaborations(
    group_id: str = Field(..., description="The unique identifier of the group whose collaborations you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of collaboration records to return per page. Accepts values up to 1000."),
    offset: str | None = Field(None, description="The zero-based index of the first item to include in the response, used for paginating through results. Offset values exceeding 10000 will result in a 400 error."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all collaborations for a specified group, showing which files or folders the group can access and with what role. Requires admin permissions to inspect enterprise groups."""

    _limit = _parse_int(limit)
    _offset = _parse_int(offset)

    # Construct request model with validation
    try:
        _request = _models.GetGroupsIdCollaborationsRequest(
            path=_models.GetGroupsIdCollaborationsRequestPath(group_id=group_id),
            query=_models.GetGroupsIdCollaborationsRequestQuery(limit=_limit, offset=_offset)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_group_collaborations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{group_id}/collaborations", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{group_id}/collaborations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_group_collaborations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_group_collaborations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_group_collaborations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Group memberships
@mcp.tool(
    title="Add User to Group",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_user_to_group(
    user_id: str | None = Field(None, alias="userId", description="The unique identifier of the user to be added to the group."),
    group_id: str | None = Field(None, alias="groupId", description="The unique identifier of the group the user will be added to."),
    role: Literal["member", "admin"] | None = Field(None, description="The role assigned to the user within the group. Use 'member' for standard access or 'admin' for elevated group management privileges."),
    configurable_permissions: dict[str, bool] | None = Field(None, description="Custom permission overrides for group admins only; has no effect on members with the 'member' role. Pass null to disable all configurable permissions, or specify individual permissions — any omitted permissions will default to enabled."),
) -> dict[str, Any] | ToolResult:
    """Adds a user to a group with a specified role and optional custom admin permissions. Requires admin-level permissions to perform this action."""

    # Construct request model with validation
    try:
        _request = _models.PostGroupMembershipsRequest(
            body=_models.PostGroupMembershipsRequestBody(role=role, configurable_permissions=configurable_permissions,
                user=_models.PostGroupMembershipsRequestBodyUser(id_=user_id) if any(v is not None for v in [user_id]) else None,
                group=_models.PostGroupMembershipsRequestBodyGroup(id_=group_id) if any(v is not None for v in [group_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_user_to_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/group_memberships"
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
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Group memberships
@mcp.tool(
    title="Get Group Membership",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_group_membership(group_membership_id: str = Field(..., description="The unique identifier of the group membership record to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves details of a specific group membership by its unique ID. Only group admins or users with admin-level permissions can access this endpoint."""

    # Construct request model with validation
    try:
        _request = _models.GetGroupMembershipsIdRequest(
            path=_models.GetGroupMembershipsIdRequestPath(group_membership_id=group_membership_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_group_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/group_memberships/{group_membership_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/group_memberships/{group_membership_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_group_membership")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_group_membership", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_group_membership",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Group memberships
@mcp.tool(
    title="Update Group Membership",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_group_membership(
    group_membership_id: str = Field(..., description="The unique identifier of the group membership record to update."),
    role: Literal["member", "admin"] | None = Field(None, description="The role to assign to the user within the group. Accepted values are 'member' for standard access or 'admin' for elevated group management privileges."),
    configurable_permissions: dict[str, bool] | None = Field(None, description="A map of specific permission overrides for a group admin, replacing their default access levels. Only applies to users with the 'admin' role; has no effect on members. Pass null to disable all configurable permissions; omitted permissions default to enabled."),
) -> dict[str, Any] | ToolResult:
    """Updates a user's role or permissions within a specific group membership. Only group admins or users with admin-level permissions can perform this action."""

    # Construct request model with validation
    try:
        _request = _models.PutGroupMembershipsIdRequest(
            path=_models.PutGroupMembershipsIdRequestPath(group_membership_id=group_membership_id),
            body=_models.PutGroupMembershipsIdRequestBody(role=role, configurable_permissions=configurable_permissions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_group_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/group_memberships/{group_membership_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/group_memberships/{group_membership_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_group_membership")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_group_membership", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_group_membership",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Group memberships
@mcp.tool(
    title="Remove Group Member",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_group_member(group_membership_id: str = Field(..., description="The unique identifier of the group membership record to delete, representing the association between a specific user and group.")) -> dict[str, Any] | ToolResult:
    """Removes a user from a group by deleting the specified group membership. Only group admins or users with admin-level permissions can perform this action."""

    # Construct request model with validation
    try:
        _request = _models.DeleteGroupMembershipsIdRequest(
            path=_models.DeleteGroupMembershipsIdRequestPath(group_membership_id=group_membership_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_group_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/group_memberships/{group_membership_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/group_memberships/{group_membership_id}"
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

# Tags: Webhooks
@mcp.tool(
    title="List Webhooks",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_webhooks(limit: str | None = Field(None, description="The maximum number of webhooks to return in a single page of results. Must be between 1 and 1000.")) -> dict[str, Any] | ToolResult:
    """Retrieves all webhooks defined for the authenticated application, scoped to files and folders owned by the requesting user. Note that admins cannot view webhooks created by service accounts unless they have explicit access to those folders, and vice versa."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetWebhooksRequest(
            query=_models.GetWebhooksRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/webhooks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
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
async def get_webhook(webhook_id: str = Field(..., description="The unique identifier of the webhook to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the configuration and details of a specific webhook by its unique identifier. Useful for inspecting webhook settings, target URLs, and event subscriptions."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhooksIdRequest(
            path=_models.GetWebhooksIdRequestPath(webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/webhooks/{webhook_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/webhooks/{webhook_id}"
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
async def delete_webhook(webhook_id: str = Field(..., description="The unique identifier of the webhook to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a webhook by its unique identifier, stopping all future event notifications associated with it."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWebhooksIdRequest(
            path=_models.DeleteWebhooksIdRequestPath(webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/webhooks/{webhook_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/webhooks/{webhook_id}"
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

# Tags: Skills
@mcp.tool(
    title="Update Skill Cards on File",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_skill_cards_on_file(
    skill_id: str = Field(..., description="The unique identifier of the Box Skill to apply metadata for. This determines which skill's cards are overwritten on the file."),
    status: Literal["invoked", "processing", "success", "transient_failure", "permanent_failure"] | None = Field(None, description="The current processing status of this skill invocation. Set to 'success' when providing completed Skill cards; use failure or processing states to reflect intermediate or error conditions. Accepted values are 'invoked', 'processing', 'success', 'transient_failure', or 'permanent_failure'."),
    cards: list[_models.SkillCard] | None = Field(None, description="An ordered list of Box Skill cards to apply to the file. Each item should be a valid Skill card object (e.g., keyword, timeline, transcript, or status card); order determines how cards are stored and displayed."),
    file_id: str | None = Field(None, alias="fileId", description="The unique identifier of the file on which the Skill cards will be applied."),
    file_version_id: str | None = Field(None, alias="file_versionId", description="The unique identifier of the specific file version to associate the Skill cards with. Use this to target a particular version rather than the current version of the file."),
    unit: str | None = Field(None, description="The type of resource unit being referenced. This value is always 'file' for file-level Skill card operations."),
    value: float | None = Field(None, description="The number of resources affected by this skill invocation. Typically reflects how many files or items the skill operation applies to."),
) -> dict[str, Any] | ToolResult:
    """Overwrites and updates all Box Skill metadata cards on a file for a given skill. Use this method to replace existing Skill cards with new ones in a single operation."""

    # Construct request model with validation
    try:
        _request = _models.PutSkillInvocationsIdRequest(
            path=_models.PutSkillInvocationsIdRequestPath(skill_id=skill_id),
            body=_models.PutSkillInvocationsIdRequestBody(status=status,
                metadata=_models.PutSkillInvocationsIdRequestBodyMetadata(cards=cards) if any(v is not None for v in [cards]) else None,
                file_=_models.PutSkillInvocationsIdRequestBodyFile(id_=file_id) if any(v is not None for v in [file_id]) else None,
                file_version=_models.PutSkillInvocationsIdRequestBodyFileVersion(id_=file_version_id) if any(v is not None for v in [file_version_id]) else None,
                usage=_models.PutSkillInvocationsIdRequestBodyUsage(unit=unit, value=value) if any(v is not None for v in [unit, value]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_skill_cards_on_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/skill_invocations/{skill_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/skill_invocations/{skill_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_skill_cards_on_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_skill_cards_on_file", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_skill_cards_on_file",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool(
    title="List Events",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_events(
    stream_type: Literal["all", "changes", "sync", "admin_logs", "admin_logs_streaming"] | None = Field(None, description="Controls the scope and type of events returned. Use 'all' for the authenticated user's full event history, 'changes' or 'sync' for file-tree-affecting events, 'admin_logs' for paginated historical enterprise-wide events within a date range, or 'admin_logs_streaming' for low-latency polling of recent enterprise-wide events. Admin privileges are required for the 'admin_logs' and 'admin_logs_streaming' types."),
    stream_position: str | None = Field(None, description="The cursor position in the event stream from which to begin returning events. Use 'now' to initialize a stream and receive only the latest position with no events, or '0' / null to retrieve all available events from the beginning."),
    limit: str | None = Field(None, description="Maximum number of events to return per request, up to 500. Fewer events than requested may be returned even when more exist, as the API may return already-retrieved events rather than waiting for additional results."),
    event_type: list[Literal["ACCESS_GRANTED", "ACCESS_REVOKED", "ADD_DEVICE_ASSOCIATION", "ADD_LOGIN_ACTIVITY_DEVICE", "ADMIN_LOGIN", "APPLICATION_CREATED", "APPLICATION_PUBLIC_KEY_ADDED", "APPLICATION_PUBLIC_KEY_DELETED", "CHANGE_ADMIN_ROLE", "CHANGE_FOLDER_PERMISSION", "COLLABORATION_ACCEPT", "COLLABORATION_EXPIRATION", "COLLABORATION_INVITE", "COLLABORATION_REMOVE", "COLLABORATION_ROLE_CHANGE", "COMMENT_CREATE", "COMMENT_DELETE", "CONTENT_WORKFLOW_ABNORMAL_DOWNLOAD_ACTIVITY", "CONTENT_WORKFLOW_AUTOMATION_ADD", "CONTENT_WORKFLOW_AUTOMATION_DELETE", "CONTENT_WORKFLOW_POLICY_ADD", "CONTENT_WORKFLOW_SHARING_POLICY_VIOLATION", "CONTENT_WORKFLOW_UPLOAD_POLICY_VIOLATION", "COPY", "DATA_RETENTION_CREATE_RETENTION", "DATA_RETENTION_REMOVE_RETENTION", "DELETE", "DELETE_USER", "DEVICE_TRUST_CHECK_FAILED", "DOWNLOAD", "EDIT", "EDIT_USER", "EMAIL_ALIAS_CONFIRM", "EMAIL_ALIAS_REMOVE", "ENTERPRISE_APP_AUTHORIZATION_UPDATE", "EXTERNAL_COLLAB_SECURITY_SETTINGS", "FAILED_LOGIN", "FILE_MARKED_MALICIOUS", "FILE_WATERMARKED_DOWNLOAD", "GROUP_ADD_ITEM", "GROUP_ADD_USER", "GROUP_CREATION", "GROUP_DELETION", "GROUP_EDITED", "GROUP_REMOVE_ITEM", "GROUP_REMOVE_USER", "ITEM_EMAIL_SEND", "ITEM_MODIFY", "ITEM_OPEN", "ITEM_SHARED_UPDATE", "ITEM_SYNC", "ITEM_UNSYNC", "LEGAL_HOLD_ASSIGNMENT_CREATE", "LEGAL_HOLD_ASSIGNMENT_DELETE", "LEGAL_HOLD_POLICY_CREATE", "LEGAL_HOLD_POLICY_DELETE", "LEGAL_HOLD_POLICY_UPDATE", "LOCK", "LOGIN", "METADATA_INSTANCE_CREATE", "METADATA_INSTANCE_DELETE", "METADATA_INSTANCE_UPDATE", "METADATA_TEMPLATE_CREATE", "METADATA_TEMPLATE_DELETE", "METADATA_TEMPLATE_UPDATE", "MOVE", "NEW_USER", "OAUTH2_ACCESS_TOKEN_REVOKE", "PREVIEW", "REMOVE_DEVICE_ASSOCIATION", "REMOVE_LOGIN_ACTIVITY_DEVICE", "RENAME", "RETENTION_POLICY_ASSIGNMENT_ADD", "SHARE", "SHARED_LINK_SEND", "SHARE_EXPIRATION", "SHIELD_ALERT", "SHIELD_EXTERNAL_COLLAB_ACCESS_BLOCKED", "SHIELD_EXTERNAL_COLLAB_ACCESS_BLOCKED_MISSING_JUSTIFICATION", "SHIELD_EXTERNAL_COLLAB_INVITE_BLOCKED", "SHIELD_EXTERNAL_COLLAB_INVITE_BLOCKED_MISSING_JUSTIFICATION", "SHIELD_JUSTIFICATION_APPROVAL", "SHIELD_SHARED_LINK_ACCESS_BLOCKED", "SHIELD_SHARED_LINK_STATUS_RESTRICTED_ON_CREATE", "SHIELD_SHARED_LINK_STATUS_RESTRICTED_ON_UPDATE", "SIGN_DOCUMENT_ASSIGNED", "SIGN_DOCUMENT_CANCELLED", "SIGN_DOCUMENT_COMPLETED", "SIGN_DOCUMENT_CONVERTED", "SIGN_DOCUMENT_CREATED", "SIGN_DOCUMENT_DECLINED", "SIGN_DOCUMENT_EXPIRED", "SIGN_DOCUMENT_SIGNED", "SIGN_DOCUMENT_VIEWED_BY_SIGNED", "SIGNER_DOWNLOADED", "SIGNER_FORWARDED", "STORAGE_EXPIRATION", "TASK_ASSIGNMENT_CREATE", "TASK_ASSIGNMENT_DELETE", "TASK_ASSIGNMENT_UPDATE", "TASK_CREATE", "TASK_UPDATE", "TERMS_OF_SERVICE_ACCEPT", "TERMS_OF_SERVICE_REJECT", "UNDELETE", "UNLOCK", "UNSHARE", "UPDATE_COLLABORATION_EXPIRATION", "UPDATE_SHARE_EXPIRATION", "UPLOAD", "USER_AUTHENTICATE_OAUTH2_ACCESS_TOKEN_CREATE", "WATERMARK_LABEL_CREATE", "WATERMARK_LABEL_DELETE"]] | None = Field(None, description="A list of specific event type strings to filter results by. Only applicable when 'stream_type' is 'admin_logs' or 'admin_logs_streaming'; ignored for all other stream types. Each item should be a valid Box event type identifier."),
    created_after: str | None = Field(None, description="The earliest date and time (inclusive) for which to return events, specified in ISO 8601 format. Only applicable when 'stream_type' is 'admin_logs'; ignored for all other stream types."),
    created_before: str | None = Field(None, description="The latest date and time (inclusive) for which to return events, specified in ISO 8601 format. Only applicable when 'stream_type' is 'admin_logs'; ignored for all other stream types."),
) -> dict[str, Any] | ToolResult:
    """Retrieves up to one year of past events for the authenticated user or, with admin privileges, for the entire enterprise. Supports both real-time polling and historical querying via configurable stream types."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetEventsRequest(
            query=_models.GetEventsRequestQuery(stream_type=stream_type, stream_position=stream_position, limit=_limit, event_type=event_type, created_after=created_after, created_before=created_before)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/events"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "event_type": ("form", False),
    })
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

# Tags: Collections
@mcp.tool(
    title="List Collections",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_collections(
    offset: str | None = Field(None, description="The zero-based index of the first item to include in the response, enabling pagination through large result sets. Offset values exceeding 10,000 will result in a 400 error."),
    limit: str | None = Field(None, description="The maximum number of collections to return in a single response page. Accepts values up to 1,000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all collections belonging to the authenticated user. Currently, only the favorites collection is supported."""

    _offset = _parse_int(offset)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetCollectionsRequest(
            query=_models.GetCollectionsRequestQuery(offset=_offset, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_collections: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_collections")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_collections", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_collections",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool(
    title="List Collection Items",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_collection_items(
    collection_id: str = Field(..., description="The unique identifier of the collection whose items you want to retrieve."),
    offset: str | None = Field(None, description="The zero-based index of the first item to return, enabling pagination through results. Must not exceed 10000; requests beyond this limit will be rejected with a 400 error."),
    limit: str | None = Field(None, description="The maximum number of items to return in a single response page. Accepts values up to 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the files and folders contained within a specified collection. Supports pagination to navigate large result sets."""

    _offset = _parse_int(offset)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetCollectionsIdItemsRequest(
            path=_models.GetCollectionsIdItemsRequestPath(collection_id=collection_id),
            query=_models.GetCollectionsIdItemsRequestQuery(offset=_offset, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_collection_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/collections/{collection_id}/items", _request.path.model_dump(by_alias=True)) if _request.path else "/collections/{collection_id}/items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_collection_items")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_collection_items", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_collection_items",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool(
    title="Get Collection",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_collection(collection_id: str = Field(..., description="The unique identifier of the collection to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific collection by its unique identifier. Use this to fetch metadata and contents associated with a single collection."""

    # Construct request model with validation
    try:
        _request = _models.GetCollectionsIdRequest(
            path=_models.GetCollectionsIdRequestPath(collection_id=collection_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/collections/{collection_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/collections/{collection_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_collection", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_collection",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Recent items
@mcp.tool(
    title="List Recent Items",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_recent_items(limit: str | None = Field(None, description="The maximum number of recently accessed items to return. Accepts values up to 1000.")) -> dict[str, Any] | ToolResult:
    """Retrieves a list of items recently accessed by the current user, covering activity from the last 90 days or up to the last 1000 items accessed, whichever limit is reached first."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetRecentItemsRequest(
            query=_models.GetRecentItemsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_recent_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/recent_items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_recent_items")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_recent_items", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_recent_items",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Retention policies
@mcp.tool(
    title="List Retention Policies",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_retention_policies(
    policy_name: str | None = Field(None, description="Filters results to only retention policies whose names begin with the specified string. The match is case-sensitive and prefix-based, so partial names from the start of the policy name are supported."),
    policy_type: Literal["finite", "indefinite"] | None = Field(None, description="Filters results by the retention policy type. Use 'finite' for policies with a defined expiration period, or 'indefinite' for policies that retain content without a set end date."),
    created_by_user_id: str | None = Field(None, description="Filters results to only policies created by the user with the specified user ID. Useful for auditing or managing policies owned by a particular administrator."),
    limit: str | None = Field(None, description="Limits the number of retention policies returned per page. Accepts values up to 1000; omitting this parameter returns the default page size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all retention policies configured for the enterprise, with optional filtering by name, type, or creator. Useful for auditing data governance rules or locating specific policies before applying or modifying them."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetRetentionPoliciesRequest(
            query=_models.GetRetentionPoliciesRequestQuery(policy_name=policy_name, policy_type=policy_type, created_by_user_id=created_by_user_id, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_retention_policies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/retention_policies"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_retention_policies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_retention_policies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_retention_policies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Retention policies
@mcp.tool(
    title="Get Retention Policy",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_retention_policy(retention_policy_id: str = Field(..., description="The unique identifier of the retention policy to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific retention policy by its unique identifier. Use this to inspect policy settings such as retention duration, disposition action, and assignment scope."""

    # Construct request model with validation
    try:
        _request = _models.GetRetentionPoliciesIdRequest(
            path=_models.GetRetentionPoliciesIdRequestPath(retention_policy_id=retention_policy_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_retention_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/retention_policies/{retention_policy_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/retention_policies/{retention_policy_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_retention_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_retention_policy", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_retention_policy",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Retention policies
@mcp.tool(
    title="Update Retention Policy",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_retention_policy(
    retention_policy_id: str = Field(..., description="The unique identifier of the retention policy to update."),
    policy_name: str | None = Field(None, description="The updated display name for the retention policy."),
    description: str | None = Field(None, description="An optional extended text description providing additional context or purpose for the retention policy."),
    disposition_action: Literal["permanently_delete", "remove_retention"] | str | None = Field(None, description="The action taken when the retention period expires. Use 'permanently_delete' to destroy retained content or 'remove_retention' to lift the policy and allow user-initiated deletion. Pass null to leave the current disposition action unchanged."),
    retention_type: str | None = Field(None, description="The modifiability type of the retention policy. Only 'non-modifiable' can be set when updating; you may convert a modifiable policy to non-modifiable, but not the reverse. Non-modifiable policies support only limited changes to ensure regulatory compliance."),
    retention_length: str | None | float | None = Field(None, description="The number of days the retention policy remains active after being assigned to content. For indefinite policies, this value should also be 'indefinite'."),
    status: str | None = Field(None, description="Set to 'retired' to retire the retention policy. Omit this parameter or pass null if you are not retiring the policy."),
    can_owner_extend_retention: bool | None = Field(None, description="Whether the owner of items under this policy is permitted to extend the retention period as it approaches expiration."),
    are_owners_notified: bool | None = Field(None, description="Whether owners and co-owners of items under this policy receive notifications as the retention period approaches its end."),
    custom_notification_recipients: list[_models.UserBase] | None = Field(None, description="An explicit list of additional users to notify when the retention duration is nearing expiration. Each item should represent a user recipient; order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing retention policy's settings, including its name, duration, disposition action, and notification preferences. You can also use this operation to retire a policy or convert it from modifiable to non-modifiable."""

    # Construct request model with validation
    try:
        _request = _models.PutRetentionPoliciesIdRequest(
            path=_models.PutRetentionPoliciesIdRequestPath(retention_policy_id=retention_policy_id),
            body=_models.PutRetentionPoliciesIdRequestBody(policy_name=policy_name, description=description, disposition_action=disposition_action, retention_type=retention_type, retention_length=retention_length, status=status, can_owner_extend_retention=can_owner_extend_retention, are_owners_notified=are_owners_notified, custom_notification_recipients=custom_notification_recipients)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_retention_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/retention_policies/{retention_policy_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/retention_policies/{retention_policy_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_retention_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_retention_policy", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_retention_policy",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Retention policies
@mcp.tool(
    title="Delete Retention Policy",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_retention_policy(retention_policy_id: str = Field(..., description="The unique identifier of the retention policy to permanently delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a retention policy by its unique identifier. This action is irreversible and removes the policy and its associated settings."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRetentionPoliciesIdRequest(
            path=_models.DeleteRetentionPoliciesIdRequestPath(retention_policy_id=retention_policy_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_retention_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/retention_policies/{retention_policy_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/retention_policies/{retention_policy_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_retention_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_retention_policy", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_retention_policy",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Retention policy assignments
@mcp.tool(
    title="List Retention Policy Assignments",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_retention_policy_assignments(
    retention_policy_id: str = Field(..., description="The unique identifier of the retention policy whose assignments you want to retrieve."),
    type_: Literal["folder", "enterprise", "metadata_template"] | None = Field(None, alias="type", description="Filters the results to only return assignments of a specific type. Accepted values are 'folder', 'enterprise', or 'metadata_template'."),
    limit: str | None = Field(None, description="The maximum number of assignments to return in a single page of results. Accepts values up to 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all assignments for a specified retention policy, showing which folders, enterprise, or metadata templates the policy is applied to. Optionally filter results by assignment type and control page size."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetRetentionPoliciesIdAssignmentsRequest(
            path=_models.GetRetentionPoliciesIdAssignmentsRequestPath(retention_policy_id=retention_policy_id),
            query=_models.GetRetentionPoliciesIdAssignmentsRequestQuery(type_=type_, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_retention_policy_assignments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/retention_policies/{retention_policy_id}/assignments", _request.path.model_dump(by_alias=True)) if _request.path else "/retention_policies/{retention_policy_id}/assignments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_retention_policy_assignments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_retention_policy_assignments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_retention_policy_assignments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Retention policy assignments
@mcp.tool(
    title="Assign Retention Policy",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def assign_retention_policy(
    policy_id: str | None = Field(None, description="The unique identifier of the retention policy to assign to the target item."),
    type_: Literal["enterprise", "folder", "metadata_template"] | None = Field(None, alias="type", description="The category of item the retention policy will be assigned to. Use 'enterprise' to apply policy-wide, 'folder' for a specific folder, or 'metadata_template' to target items matching a metadata template."),
    id_: str | None = Field(None, alias="id", description="The unique identifier of the specific folder or metadata template to assign the policy to. Omit or set to null when assigning to the entire enterprise."),
    filter_fields: list[_models.PostRetentionPolicyAssignmentsBodyFilterFieldsItem] | None = Field(None, description="An array of field-value filter objects used to narrow the assignment when the target type is 'metadata_template'. Each object must contain a 'field' key and a 'value' key; currently only one filter object is supported."),
    start_date_field: str | None = Field(None, description="The date from which the retention policy assignment takes effect. When the target type is 'metadata_template', this can reference a date-type metadata attribute key ID to dynamically determine the start date."),
) -> dict[str, Any] | ToolResult:
    """Assigns a retention policy to a specific target, such as a folder, enterprise, or metadata template. Use this to enforce data retention rules on content within Box."""

    # Construct request model with validation
    try:
        _request = _models.PostRetentionPolicyAssignmentsRequest(
            body=_models.PostRetentionPolicyAssignmentsRequestBody(policy_id=policy_id, filter_fields=filter_fields, start_date_field=start_date_field,
                assign_to=_models.PostRetentionPolicyAssignmentsRequestBodyAssignTo(type_=type_, id_=id_) if any(v is not None for v in [type_, id_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for assign_retention_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/retention_policy_assignments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("assign_retention_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("assign_retention_policy", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="assign_retention_policy",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Retention policy assignments
@mcp.tool(
    title="Get Retention Policy Assignment",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_retention_policy_assignment(retention_policy_assignment_id: str = Field(..., description="The unique identifier of the retention policy assignment to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific retention policy assignment by its unique ID. Use this to inspect how a retention policy has been applied to a particular content target."""

    # Construct request model with validation
    try:
        _request = _models.GetRetentionPolicyAssignmentsIdRequest(
            path=_models.GetRetentionPolicyAssignmentsIdRequestPath(retention_policy_assignment_id=retention_policy_assignment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_retention_policy_assignment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/retention_policy_assignments/{retention_policy_assignment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/retention_policy_assignments/{retention_policy_assignment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_retention_policy_assignment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_retention_policy_assignment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_retention_policy_assignment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Retention policy assignments
@mcp.tool(
    title="Delete Retention Policy Assignment",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_retention_policy_assignment(retention_policy_assignment_id: str = Field(..., description="The unique identifier of the retention policy assignment to remove.")) -> dict[str, Any] | ToolResult:
    """Removes a retention policy assignment, detaching the retention policy from the previously assigned content. This action stops the policy from being enforced on that content going forward."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRetentionPolicyAssignmentsIdRequest(
            path=_models.DeleteRetentionPolicyAssignmentsIdRequestPath(retention_policy_assignment_id=retention_policy_assignment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_retention_policy_assignment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/retention_policy_assignments/{retention_policy_assignment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/retention_policy_assignments/{retention_policy_assignment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_retention_policy_assignment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_retention_policy_assignment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_retention_policy_assignment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Retention policy assignments
@mcp.tool(
    title="List Files Under Retention",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_files_under_retention(
    retention_policy_assignment_id: str = Field(..., description="The unique identifier of the retention policy assignment whose retained files you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of files to return per page. Accepts values up to 1000; omit to use the API default."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of files currently under retention for a specific retention policy assignment. Useful for auditing which files are actively governed by a given retention rule."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetRetentionPolicyAssignmentsIdFilesUnderRetentionRequest(
            path=_models.GetRetentionPolicyAssignmentsIdFilesUnderRetentionRequestPath(retention_policy_assignment_id=retention_policy_assignment_id),
            query=_models.GetRetentionPolicyAssignmentsIdFilesUnderRetentionRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_files_under_retention: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/retention_policy_assignments/{retention_policy_assignment_id}/files_under_retention", _request.path.model_dump(by_alias=True)) if _request.path else "/retention_policy_assignments/{retention_policy_assignment_id}/files_under_retention"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_files_under_retention")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_files_under_retention", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_files_under_retention",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Retention policy assignments
@mcp.tool(
    title="List File Versions Under Retention",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_file_versions_under_retention(
    retention_policy_assignment_id: str = Field(..., description="The unique identifier of the retention policy assignment whose retained file versions you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of file version records to return per page. Accepts values up to 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of file versions currently under retention for a specific retention policy assignment. Useful for auditing which file versions are being preserved by a given policy."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetRetentionPolicyAssignmentsIdFileVersionsUnderRetentionRequest(
            path=_models.GetRetentionPolicyAssignmentsIdFileVersionsUnderRetentionRequestPath(retention_policy_assignment_id=retention_policy_assignment_id),
            query=_models.GetRetentionPolicyAssignmentsIdFileVersionsUnderRetentionRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_versions_under_retention: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/retention_policy_assignments/{retention_policy_assignment_id}/file_versions_under_retention", _request.path.model_dump(by_alias=True)) if _request.path else "/retention_policy_assignments/{retention_policy_assignment_id}/file_versions_under_retention"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_versions_under_retention")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_versions_under_retention", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_versions_under_retention",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal hold policies
@mcp.tool(
    title="List Legal Hold Policies",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_legal_hold_policies(
    policy_name: str | None = Field(None, description="Filters results to only include policies whose names begin with this search term. The match is case-insensitive."),
    limit: str | None = Field(None, description="The maximum number of legal hold policies to return in a single page of results. Accepts values up to 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all legal hold policies belonging to the enterprise. Supports filtering by policy name prefix to narrow results."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetLegalHoldPoliciesRequest(
            query=_models.GetLegalHoldPoliciesRequestQuery(policy_name=policy_name, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_legal_hold_policies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/legal_hold_policies"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_legal_hold_policies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_legal_hold_policies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_legal_hold_policies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal hold policies
@mcp.tool(
    title="Get Legal Hold Policy",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_legal_hold_policy(legal_hold_policy_id: str = Field(..., description="The unique identifier of the legal hold policy to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific legal hold policy by its unique identifier. Use this to inspect policy configuration, status, and associated metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetLegalHoldPoliciesIdRequest(
            path=_models.GetLegalHoldPoliciesIdRequestPath(legal_hold_policy_id=legal_hold_policy_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_legal_hold_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/legal_hold_policies/{legal_hold_policy_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/legal_hold_policies/{legal_hold_policy_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_legal_hold_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_legal_hold_policy", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_legal_hold_policy",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal hold policies
@mcp.tool(
    title="Update Legal Hold Policy",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_legal_hold_policy(
    legal_hold_policy_id: str = Field(..., description="The unique identifier of the legal hold policy to update."),
    policy_name: str | None = Field(None, description="The updated display name for the legal hold policy. Must not exceed 254 characters.", max_length=254),
    description: str | None = Field(None, description="An updated human-readable description of the legal hold policy's purpose or scope. Must not exceed 500 characters.", max_length=500),
    release_notes: str | None = Field(None, description="Notes explaining the reason or context for releasing this legal hold policy. Must not exceed 500 characters.", max_length=500),
) -> dict[str, Any] | ToolResult:
    """Updates the name, description, or release notes of an existing legal hold policy. Use this to modify policy details after creation without affecting associated holds."""

    # Construct request model with validation
    try:
        _request = _models.PutLegalHoldPoliciesIdRequest(
            path=_models.PutLegalHoldPoliciesIdRequestPath(legal_hold_policy_id=legal_hold_policy_id),
            body=_models.PutLegalHoldPoliciesIdRequestBody(policy_name=policy_name, description=description, release_notes=release_notes)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_legal_hold_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/legal_hold_policies/{legal_hold_policy_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/legal_hold_policies/{legal_hold_policy_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_legal_hold_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_legal_hold_policy", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_legal_hold_policy",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal hold policies
@mcp.tool(
    title="Delete Legal Hold Policy",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_legal_hold_policy(legal_hold_policy_id: str = Field(..., description="The unique identifier of the legal hold policy to delete.")) -> dict[str, Any] | ToolResult:
    """Deletes an existing legal hold policy by its ID. This is an asynchronous operation, so the policy may not be fully removed immediately when the response is returned."""

    # Construct request model with validation
    try:
        _request = _models.DeleteLegalHoldPoliciesIdRequest(
            path=_models.DeleteLegalHoldPoliciesIdRequestPath(legal_hold_policy_id=legal_hold_policy_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_legal_hold_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/legal_hold_policies/{legal_hold_policy_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/legal_hold_policies/{legal_hold_policy_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_legal_hold_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_legal_hold_policy", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_legal_hold_policy",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal hold policy assignments
@mcp.tool(
    title="List Legal Hold Policy Assignments",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_legal_hold_policy_assignments(
    policy_id: str = Field(..., description="The unique identifier of the legal hold policy whose assignments you want to retrieve."),
    assign_to_type: Literal["file", "file_version", "folder", "user", "ownership", "interactions"] | None = Field(None, description="Narrows results to only assignments targeting a specific item type. Accepted values are 'file', 'file_version', 'folder', 'user', 'ownership', or 'interactions'."),
    assign_to_id: str | None = Field(None, description="Narrows results to only assignments targeting a specific item by its unique ID. Best used in combination with assign_to_type for precise filtering."),
    limit: str | None = Field(None, description="The maximum number of assignments to return in a single page of results. Accepts values up to 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of all items (files, folders, users, etc.) that a specific legal hold policy has been assigned to. Supports filtering by item type and item ID for targeted lookups."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetLegalHoldPolicyAssignmentsRequest(
            query=_models.GetLegalHoldPolicyAssignmentsRequestQuery(policy_id=policy_id, assign_to_type=assign_to_type, assign_to_id=assign_to_id, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_legal_hold_policy_assignments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/legal_hold_policy_assignments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_legal_hold_policy_assignments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_legal_hold_policy_assignments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_legal_hold_policy_assignments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal hold policy assignments
@mcp.tool(
    title="Assign Legal Hold Policy",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def assign_legal_hold_policy(
    policy_id: str | None = Field(None, description="The unique identifier of the legal hold policy to assign to the target item."),
    type_: Literal["file", "file_version", "folder", "user", "ownership", "interactions"] | None = Field(None, alias="type", description="The category of item to which the legal hold policy will be applied. Must be one of: file, file_version, folder, user, ownership, or interactions."),
    id_: str | None = Field(None, alias="id", description="The unique identifier of the specific item (file, folder, user, etc.) to which the legal hold policy will be assigned."),
) -> dict[str, Any] | ToolResult:
    """Assigns a legal hold policy to a specific item, such as a file, file version, folder, user, ownership, or interactions. Use this to enforce legal holds across different content types within Box."""

    # Construct request model with validation
    try:
        _request = _models.PostLegalHoldPolicyAssignmentsRequest(
            body=_models.PostLegalHoldPolicyAssignmentsRequestBody(policy_id=policy_id,
                assign_to=_models.PostLegalHoldPolicyAssignmentsRequestBodyAssignTo(type_=type_, id_=id_) if any(v is not None for v in [type_, id_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for assign_legal_hold_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/legal_hold_policy_assignments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("assign_legal_hold_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("assign_legal_hold_policy", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="assign_legal_hold_policy",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal hold policy assignments
@mcp.tool(
    title="Get Legal Hold Policy Assignment",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_legal_hold_policy_assignment(legal_hold_policy_assignment_id: str = Field(..., description="The unique identifier of the legal hold policy assignment to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific legal hold policy assignment by its unique ID. Use this to inspect which users, folders, or files are bound to a particular legal hold policy."""

    # Construct request model with validation
    try:
        _request = _models.GetLegalHoldPolicyAssignmentsIdRequest(
            path=_models.GetLegalHoldPolicyAssignmentsIdRequestPath(legal_hold_policy_assignment_id=legal_hold_policy_assignment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_legal_hold_policy_assignment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/legal_hold_policy_assignments/{legal_hold_policy_assignment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/legal_hold_policy_assignments/{legal_hold_policy_assignment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_legal_hold_policy_assignment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_legal_hold_policy_assignment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_legal_hold_policy_assignment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal hold policy assignments
@mcp.tool(
    title="Remove Legal Hold Policy Assignment",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_legal_hold_policy_assignment(legal_hold_policy_assignment_id: str = Field(..., description="The unique identifier of the legal hold policy assignment to remove.")) -> dict[str, Any] | ToolResult:
    """Removes a legal hold policy assignment from an item, unlinking the policy from the associated content. This is an asynchronous operation; the hold may not be fully released by the time the response is returned."""

    # Construct request model with validation
    try:
        _request = _models.DeleteLegalHoldPolicyAssignmentsIdRequest(
            path=_models.DeleteLegalHoldPolicyAssignmentsIdRequestPath(legal_hold_policy_assignment_id=legal_hold_policy_assignment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_legal_hold_policy_assignment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/legal_hold_policy_assignments/{legal_hold_policy_assignment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/legal_hold_policy_assignments/{legal_hold_policy_assignment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_legal_hold_policy_assignment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_legal_hold_policy_assignment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_legal_hold_policy_assignment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal hold policy assignments
@mcp.tool(
    title="List Legal Hold Assignment Files",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_legal_hold_assignment_files(
    legal_hold_policy_assignment_id: str = Field(..., description="The unique identifier of the legal hold policy assignment whose held files you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of files to return per page, up to a maximum of 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of files with their current file versions held under a specific legal hold policy assignment. For previous file versions on hold, use the file versions on hold endpoint instead."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetLegalHoldPolicyAssignmentsIdFilesOnHoldRequest(
            path=_models.GetLegalHoldPolicyAssignmentsIdFilesOnHoldRequestPath(legal_hold_policy_assignment_id=legal_hold_policy_assignment_id),
            query=_models.GetLegalHoldPolicyAssignmentsIdFilesOnHoldRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_legal_hold_assignment_files: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/legal_hold_policy_assignments/{legal_hold_policy_assignment_id}/files_on_hold", _request.path.model_dump(by_alias=True)) if _request.path else "/legal_hold_policy_assignments/{legal_hold_policy_assignment_id}/files_on_hold"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_legal_hold_assignment_files")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_legal_hold_assignment_files", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_legal_hold_assignment_files",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal hold policy assignments
@mcp.tool(
    title="List Legal Hold Assignment File Versions",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_legal_hold_assignment_file_versions(
    legal_hold_policy_assignment_id: str = Field(..., description="The unique identifier of the legal hold policy assignment whose past file versions on hold should be retrieved."),
    limit: str | None = Field(None, description="The maximum number of file version records to return per page. Accepts values up to 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of previous (past) file versions placed on hold for a specific legal hold policy assignment. Use this endpoint for historical file versions; for current file versions on hold, use the files_on_hold endpoint instead."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetLegalHoldPolicyAssignmentsIdFileVersionsOnHoldRequest(
            path=_models.GetLegalHoldPolicyAssignmentsIdFileVersionsOnHoldRequestPath(legal_hold_policy_assignment_id=legal_hold_policy_assignment_id),
            query=_models.GetLegalHoldPolicyAssignmentsIdFileVersionsOnHoldRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_legal_hold_assignment_file_versions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/legal_hold_policy_assignments/{legal_hold_policy_assignment_id}/file_versions_on_hold", _request.path.model_dump(by_alias=True)) if _request.path else "/legal_hold_policy_assignments/{legal_hold_policy_assignment_id}/file_versions_on_hold"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_legal_hold_assignment_file_versions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_legal_hold_assignment_file_versions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_legal_hold_assignment_file_versions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: File version legal holds
@mcp.tool(
    title="Get File Version Legal Hold",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_file_version_legal_hold(file_version_legal_hold_id: str = Field(..., description="The unique identifier of the file version legal hold record to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves details about the legal hold policies assigned to a specific file version. Use this to inspect which legal holds are actively applied to a given file version."""

    # Construct request model with validation
    try:
        _request = _models.GetFileVersionLegalHoldsIdRequest(
            path=_models.GetFileVersionLegalHoldsIdRequestPath(file_version_legal_hold_id=file_version_legal_hold_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_version_legal_hold: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/file_version_legal_holds/{file_version_legal_hold_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/file_version_legal_holds/{file_version_legal_hold_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_version_legal_hold")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_version_legal_hold", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_version_legal_hold",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: File version legal holds
@mcp.tool(
    title="List File Version Legal Holds",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_file_version_legal_holds(
    policy_id: str = Field(..., description="The unique identifier of the legal hold policy whose file version holds you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of file version legal hold records to return in a single page of results; must be between 1 and 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves file versions currently held under a specific legal hold policy, covering legacy-architecture holds only. For holds in the new architecture, use the legal hold policy assignment endpoints instead."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetFileVersionLegalHoldsRequest(
            query=_models.GetFileVersionLegalHoldsRequestQuery(policy_id=policy_id, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_version_legal_holds: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/file_version_legal_holds"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_version_legal_holds")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_version_legal_holds", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_version_legal_holds",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barriers
@mcp.tool(
    title="Get Information Barrier",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_information_barrier(shield_information_barrier_id: str = Field(..., description="The unique identifier of the shield information barrier to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves details of a specific shield information barrier by its unique ID. Useful for inspecting the configuration and status of an existing barrier between user groups."""

    # Construct request model with validation
    try:
        _request = _models.GetShieldInformationBarriersIdRequest(
            path=_models.GetShieldInformationBarriersIdRequestPath(shield_information_barrier_id=shield_information_barrier_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_information_barrier: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/shield_information_barriers/{shield_information_barrier_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/shield_information_barriers/{shield_information_barrier_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_information_barrier")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_information_barrier", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_information_barrier",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barriers
@mcp.tool(
    title="Update Shield Barrier Status",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def update_shield_barrier_status(
    id_: str | None = Field(None, alias="id", description="The unique identifier of the shield information barrier whose status you want to change."),
    status: Literal["pending", "disabled"] | None = Field(None, description="The target status to apply to the shield information barrier. Accepted values are 'pending' (barrier is queued for activation) or 'disabled' (barrier is turned off)."),
) -> dict[str, Any] | ToolResult:
    """Changes the status of a shield information barrier to control its enforcement state. Use this to activate, suspend, or disable an existing barrier by its unique ID."""

    # Construct request model with validation
    try:
        _request = _models.PostShieldInformationBarriersChangeStatusRequest(
            body=_models.PostShieldInformationBarriersChangeStatusRequestBody(id_=id_, status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_shield_barrier_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shield_information_barriers/change_status"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_shield_barrier_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_shield_barrier_status", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_shield_barrier_status",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barriers
@mcp.tool(
    title="List Shield Information Barriers",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_shield_information_barriers(limit: str | None = Field(None, description="The maximum number of shield information barrier records to return in a single page of results. Must be between 1 and 1000.")) -> dict[str, Any] | ToolResult:
    """Retrieves all shield information barriers configured for the enterprise associated with the JWT token. Shield information barriers restrict communication and data access between internal groups."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetShieldInformationBarriersRequest(
            query=_models.GetShieldInformationBarriersRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_shield_information_barriers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shield_information_barriers"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_shield_information_barriers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_shield_information_barriers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_shield_information_barriers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barriers
@mcp.tool(
    title="Create Shield Information Barrier",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_shield_information_barrier(enterprise: _models.PostShieldInformationBarriersBodyEnterprise | None = Field(None, description="The type and ID of the enterprise under which this shield information barrier will be created.")) -> dict[str, Any] | ToolResult:
    """Creates a shield information barrier within an enterprise to separate individuals or groups and prevent confidential information from passing between them. Use this to enforce ethical walls or compliance boundaries within the same firm."""

    # Construct request model with validation
    try:
        _request = _models.PostShieldInformationBarriersRequest(
            body=_models.PostShieldInformationBarriersRequestBody(enterprise=enterprise)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_shield_information_barrier: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shield_information_barriers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_shield_information_barrier")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_shield_information_barrier", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_shield_information_barrier",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barrier reports
@mcp.tool(
    title="List Barrier Reports",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_barrier_reports(
    shield_information_barrier_id: str = Field(..., description="The unique identifier of the shield information barrier whose reports should be listed."),
    limit: str | None = Field(None, description="The maximum number of reports to return per page. Accepts values up to 1000; omit to use the server default."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of shield information barrier reports associated with a specific barrier. Use this to audit or review compliance reports generated for a given information barrier."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetShieldInformationBarrierReportsRequest(
            query=_models.GetShieldInformationBarrierReportsRequestQuery(shield_information_barrier_id=shield_information_barrier_id, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_barrier_reports: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shield_information_barrier_reports"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_barrier_reports")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_barrier_reports", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_barrier_reports",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barrier reports
@mcp.tool(
    title="Create Barrier Report",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_barrier_report(
    id_: str | None = Field(None, alias="id", description="The unique identifier of the shield information barrier for which the report will be generated."),
    type_: Literal["shield_information_barrier"] | None = Field(None, alias="type", description="The resource type of the shield information barrier being referenced. Must be set to the designated barrier type value."),
) -> dict[str, Any] | ToolResult:
    """Generates a compliance report for a specified shield information barrier, providing a snapshot of the barrier's configuration and activity. Useful for auditing and regulatory review of information separation policies."""

    # Construct request model with validation
    try:
        _request = _models.PostShieldInformationBarrierReportsRequest(
            body=_models.PostShieldInformationBarrierReportsRequestBody(shield_information_barrier=_models.PostShieldInformationBarrierReportsRequestBodyShieldInformationBarrier(id_=id_, type_=type_) if any(v is not None for v in [id_, type_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_barrier_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shield_information_barrier_reports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_barrier_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_barrier_report", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_barrier_report",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barrier reports
@mcp.tool(
    title="Get Barrier Report",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_barrier_report(shield_information_barrier_report_id: str = Field(..., description="The unique identifier of the shield information barrier report to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific shield information barrier report by its unique ID. Use this to fetch the status and details of a previously created compliance barrier report."""

    # Construct request model with validation
    try:
        _request = _models.GetShieldInformationBarrierReportsIdRequest(
            path=_models.GetShieldInformationBarrierReportsIdRequestPath(shield_information_barrier_report_id=shield_information_barrier_report_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_barrier_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/shield_information_barrier_reports/{shield_information_barrier_report_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/shield_information_barrier_reports/{shield_information_barrier_report_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_barrier_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_barrier_report", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_barrier_report",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barrier segments
@mcp.tool(
    title="Get Barrier Segment",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_barrier_segment(shield_information_barrier_segment_id: str = Field(..., description="The unique identifier of the shield information barrier segment to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific shield information barrier segment by its unique ID. Shield information barrier segments define the boundaries that restrict information flow between groups within an organization."""

    # Construct request model with validation
    try:
        _request = _models.GetShieldInformationBarrierSegmentsIdRequest(
            path=_models.GetShieldInformationBarrierSegmentsIdRequestPath(shield_information_barrier_segment_id=shield_information_barrier_segment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_barrier_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/shield_information_barrier_segments/{shield_information_barrier_segment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/shield_information_barrier_segments/{shield_information_barrier_segment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_barrier_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_barrier_segment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_barrier_segment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barrier segments
@mcp.tool(
    title="Update Barrier Segment",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_barrier_segment(
    shield_information_barrier_segment_id: str = Field(..., description="The unique identifier of the shield information barrier segment to update."),
    name: str | None = Field(None, description="The new name to assign to the barrier segment. Must contain at least one non-whitespace character.", pattern="\\S+"),
    description: str | None = Field(None, description="The new description to assign to the barrier segment, providing context about its purpose or the division it represents."),
) -> dict[str, Any] | ToolResult:
    """Updates the name and/or description of a specific shield information barrier segment by its ID. Use this to modify segment metadata without affecting its underlying barrier configuration."""

    # Construct request model with validation
    try:
        _request = _models.PutShieldInformationBarrierSegmentsIdRequest(
            path=_models.PutShieldInformationBarrierSegmentsIdRequestPath(shield_information_barrier_segment_id=shield_information_barrier_segment_id),
            body=_models.PutShieldInformationBarrierSegmentsIdRequestBody(name=name, description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_barrier_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/shield_information_barrier_segments/{shield_information_barrier_segment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/shield_information_barrier_segments/{shield_information_barrier_segment_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_barrier_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_barrier_segment", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_barrier_segment",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barrier segments
@mcp.tool(
    title="Delete Barrier Segment",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_barrier_segment(shield_information_barrier_segment_id: str = Field(..., description="The unique identifier of the shield information barrier segment to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a shield information barrier segment by its unique ID. This action removes the segment and its associated configurations from the information barrier."""

    # Construct request model with validation
    try:
        _request = _models.DeleteShieldInformationBarrierSegmentsIdRequest(
            path=_models.DeleteShieldInformationBarrierSegmentsIdRequestPath(shield_information_barrier_segment_id=shield_information_barrier_segment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_barrier_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/shield_information_barrier_segments/{shield_information_barrier_segment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/shield_information_barrier_segments/{shield_information_barrier_segment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_barrier_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_barrier_segment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_barrier_segment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barrier segments
@mcp.tool(
    title="List Barrier Segments",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_barrier_segments(
    shield_information_barrier_id: str = Field(..., description="The unique identifier of the shield information barrier whose segments you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of barrier segment objects to return in a single page of results. Accepts values up to 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all shield information barrier segments associated with a specified information barrier. Segments define the groups or users separated by the barrier."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetShieldInformationBarrierSegmentsRequest(
            query=_models.GetShieldInformationBarrierSegmentsRequestQuery(shield_information_barrier_id=shield_information_barrier_id, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_barrier_segments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shield_information_barrier_segments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_barrier_segments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_barrier_segments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_barrier_segments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barrier segments
@mcp.tool(
    title="Create Barrier Segment",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_barrier_segment(
    id_: str | None = Field(None, alias="id", description="The unique identifier of the parent shield information barrier under which this segment will be created."),
    type_: Literal["shield_information_barrier"] | None = Field(None, alias="type", description="The resource type of the associated shield information barrier; must be set to the designated barrier type value."),
    name: str | None = Field(None, description="A human-readable name for the barrier segment that identifies the division or group being isolated."),
    description: str | None = Field(None, description="An optional narrative description providing additional context about the barrier segment's purpose or the division it represents."),
) -> dict[str, Any] | ToolResult:
    """Creates a named segment within an existing shield information barrier, allowing organizations to define distinct groups or divisions for information separation and compliance purposes."""

    # Construct request model with validation
    try:
        _request = _models.PostShieldInformationBarrierSegmentsRequest(
            body=_models.PostShieldInformationBarrierSegmentsRequestBody(name=name, description=description,
                shield_information_barrier=_models.PostShieldInformationBarrierSegmentsRequestBodyShieldInformationBarrier(id_=id_, type_=type_) if any(v is not None for v in [id_, type_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_barrier_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shield_information_barrier_segments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_barrier_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_barrier_segment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_barrier_segment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barrier segment members
@mcp.tool(
    title="Get Barrier Segment Member",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_barrier_segment_member(shield_information_barrier_segment_member_id: str = Field(..., description="The unique identifier of the shield information barrier segment member to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific shield information barrier segment member by its unique ID. Useful for inspecting the details of an individual member assigned to a barrier segment."""

    # Construct request model with validation
    try:
        _request = _models.GetShieldInformationBarrierSegmentMembersIdRequest(
            path=_models.GetShieldInformationBarrierSegmentMembersIdRequestPath(shield_information_barrier_segment_member_id=shield_information_barrier_segment_member_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_barrier_segment_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/shield_information_barrier_segment_members/{shield_information_barrier_segment_member_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/shield_information_barrier_segment_members/{shield_information_barrier_segment_member_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_barrier_segment_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_barrier_segment_member", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_barrier_segment_member",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barrier segment members
@mcp.tool(
    title="Delete Barrier Segment Member",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_barrier_segment_member(shield_information_barrier_segment_member_id: str = Field(..., description="The unique identifier of the shield information barrier segment member to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently removes a specific member from a shield information barrier segment. Use this to revoke a user's association with a segment when access restrictions need to be updated."""

    # Construct request model with validation
    try:
        _request = _models.DeleteShieldInformationBarrierSegmentMembersIdRequest(
            path=_models.DeleteShieldInformationBarrierSegmentMembersIdRequestPath(shield_information_barrier_segment_member_id=shield_information_barrier_segment_member_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_barrier_segment_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/shield_information_barrier_segment_members/{shield_information_barrier_segment_member_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/shield_information_barrier_segment_members/{shield_information_barrier_segment_member_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_barrier_segment_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_barrier_segment_member", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_barrier_segment_member",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barrier segment members
@mcp.tool(
    title="List Barrier Segment Members",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_barrier_segment_members(
    shield_information_barrier_segment_id: str = Field(..., description="The unique identifier of the shield information barrier segment whose members you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of segment members to return in a single page of results. Must be between 1 and 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of members belonging to a specific shield information barrier segment. Use this to audit or review which users are assigned to a given segment."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetShieldInformationBarrierSegmentMembersRequest(
            query=_models.GetShieldInformationBarrierSegmentMembersRequestQuery(shield_information_barrier_segment_id=shield_information_barrier_segment_id, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_barrier_segment_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shield_information_barrier_segment_members"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_barrier_segment_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_barrier_segment_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_barrier_segment_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barrier segment members
@mcp.tool(
    title="Add Barrier Segment Member",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_barrier_segment_member(
    shield_information_barrier_id: str | None = Field(None, alias="shield_information_barrierId", description="The unique identifier of the shield information barrier that the target segment belongs to."),
    shield_information_barrier_segment_id: str | None = Field(None, alias="shield_information_barrier_segmentId", description="The unique identifier of the shield information barrier segment to which the user will be added as a member."),
    user: _models.PostShieldInformationBarrierSegmentMembersBodyUser | None = Field(None, description="The user object representing the individual to whom the segment's information barrier restrictions will be applied."),
) -> dict[str, Any] | ToolResult:
    """Adds a user as a member of a shield information barrier segment, applying the segment's information restrictions to that user."""

    # Construct request model with validation
    try:
        _request = _models.PostShieldInformationBarrierSegmentMembersRequest(
            body=_models.PostShieldInformationBarrierSegmentMembersRequestBody(user=user,
                shield_information_barrier=_models.PostShieldInformationBarrierSegmentMembersRequestBodyShieldInformationBarrier(id_=shield_information_barrier_id) if any(v is not None for v in [shield_information_barrier_id]) else None,
                shield_information_barrier_segment=_models.PostShieldInformationBarrierSegmentMembersRequestBodyShieldInformationBarrierSegment(id_=shield_information_barrier_segment_id) if any(v is not None for v in [shield_information_barrier_segment_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_barrier_segment_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shield_information_barrier_segment_members"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_barrier_segment_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_barrier_segment_member", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_barrier_segment_member",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barrier segment restrictions
@mcp.tool(
    title="Get Barrier Segment Restriction",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_barrier_segment_restriction(shield_information_barrier_segment_restriction_id: str = Field(..., description="The unique identifier of the shield information barrier segment restriction to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific shield information barrier segment restriction by its unique ID. Use this to inspect the details of an existing restriction between two information barrier segments."""

    # Construct request model with validation
    try:
        _request = _models.GetShieldInformationBarrierSegmentRestrictionsIdRequest(
            path=_models.GetShieldInformationBarrierSegmentRestrictionsIdRequestPath(shield_information_barrier_segment_restriction_id=shield_information_barrier_segment_restriction_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_barrier_segment_restriction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/shield_information_barrier_segment_restrictions/{shield_information_barrier_segment_restriction_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/shield_information_barrier_segment_restrictions/{shield_information_barrier_segment_restriction_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_barrier_segment_restriction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_barrier_segment_restriction", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_barrier_segment_restriction",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shield information barrier segment restrictions
@mcp.tool(
    title="List Barrier Segment Restrictions",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_barrier_segment_restrictions(
    shield_information_barrier_segment_id: str = Field(..., description="The unique identifier of the shield information barrier segment whose restrictions you want to list."),
    limit: str | None = Field(None, description="The maximum number of restriction records to return in a single page of results. Must be between 1 and 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all shield information barrier segment restrictions associated with a specific segment. Use this to audit or review access restrictions applied to a given barrier segment."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetShieldInformationBarrierSegmentRestrictionsRequest(
            query=_models.GetShieldInformationBarrierSegmentRestrictionsRequestQuery(shield_information_barrier_segment_id=shield_information_barrier_segment_id, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_barrier_segment_restrictions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/shield_information_barrier_segment_restrictions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_barrier_segment_restrictions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_barrier_segment_restrictions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_barrier_segment_restrictions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Device pinners
@mcp.tool(
    title="Get Device Pin",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_device_pin(device_pinner_id: str = Field(..., description="The unique identifier of the device pin to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific device pin by its unique identifier. Useful for inspecting the status and metadata of an individual device pinning record."""

    # Construct request model with validation
    try:
        _request = _models.GetDevicePinnersIdRequest(
            path=_models.GetDevicePinnersIdRequestPath(device_pinner_id=device_pinner_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_device_pin: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/device_pinners/{device_pinner_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/device_pinners/{device_pinner_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_device_pin")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_device_pin", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_device_pin",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Device pinners
@mcp.tool(
    title="Delete Device Pin",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_device_pin(device_pinner_id: str = Field(..., description="The unique identifier of the device pin to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently removes a specific device pin, revoking the trusted device association for the corresponding user. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDevicePinnersIdRequest(
            path=_models.DeleteDevicePinnersIdRequestPath(device_pinner_id=device_pinner_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_device_pin: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/device_pinners/{device_pinner_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/device_pinners/{device_pinner_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_device_pin")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_device_pin", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_device_pin",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Device pinners
@mcp.tool(
    title="List Enterprise Device Pins",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_enterprise_device_pins(
    enterprise_id: str = Field(..., description="The unique identifier of the enterprise whose device pins you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of device pins to return per page, up to a maximum of 1000."),
    direction: Literal["ASC", "DESC"] | None = Field(None, description="The sort order for the returned results, either ascending (ASC) or descending (DESC) alphabetical order."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all device pins registered within a specified enterprise. Requires admin privileges and the 'manage enterprise' application scope."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetEnterprisesIdDevicePinnersRequest(
            path=_models.GetEnterprisesIdDevicePinnersRequestPath(enterprise_id=enterprise_id),
            query=_models.GetEnterprisesIdDevicePinnersRequestQuery(limit=_limit, direction=direction)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_enterprise_device_pins: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/enterprises/{enterprise_id}/device_pinners", _request.path.model_dump(by_alias=True)) if _request.path else "/enterprises/{enterprise_id}/device_pinners"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_enterprise_device_pins")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_enterprise_device_pins", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_enterprise_device_pins",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Terms of service user statuses
@mcp.tool(
    title="List Terms of Service User Statuses",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_terms_of_service_user_statuses(
    tos_id: str = Field(..., description="The unique identifier of the terms of service whose user acceptance statuses should be retrieved."),
    user_id: str | None = Field(None, description="When provided, restricts the results to the acceptance status of a single user matching this ID."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the acceptance status of users for a specific terms of service, including whether each user has accepted the terms and the timestamp of their response. Optionally filter results to a single user."""

    # Construct request model with validation
    try:
        _request = _models.GetTermsOfServiceUserStatusesRequest(
            query=_models.GetTermsOfServiceUserStatusesRequestQuery(tos_id=tos_id, user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_terms_of_service_user_statuses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/terms_of_service_user_statuses"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_terms_of_service_user_statuses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_terms_of_service_user_statuses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_terms_of_service_user_statuses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Terms of service user statuses
@mcp.tool(
    title="Create Terms of Service User Status",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_terms_of_service_user_status(
    tos_id: str | None = Field(None, alias="tosId", description="The unique identifier of the terms of service document to associate with the user status."),
    user_id: str | None = Field(None, alias="userId", description="The unique identifier of the user whose terms of service acceptance status is being recorded."),
    is_accepted: bool | None = Field(None, description="Indicates whether the user has accepted the terms of service; set to true if accepted, false if declined."),
) -> dict[str, Any] | ToolResult:
    """Creates or sets the acceptance status of a terms of service agreement for a specific user. Use this to record whether a new user has accepted or declined a given terms of service."""

    # Construct request model with validation
    try:
        _request = _models.PostTermsOfServiceUserStatusesRequest(
            body=_models.PostTermsOfServiceUserStatusesRequestBody(is_accepted=is_accepted,
                tos=_models.PostTermsOfServiceUserStatusesRequestBodyTos(id_=tos_id) if any(v is not None for v in [tos_id]) else None,
                user=_models.PostTermsOfServiceUserStatusesRequestBodyUser(id_=user_id) if any(v is not None for v in [user_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_terms_of_service_user_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/terms_of_service_user_statuses"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_terms_of_service_user_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_terms_of_service_user_status", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_terms_of_service_user_status",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Terms of service user statuses
@mcp.tool(
    title="Update Terms of Service User Status",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_terms_of_service_user_status(
    terms_of_service_user_status_id: str = Field(..., description="The unique identifier of the terms of service user status record to update."),
    is_accepted: bool | None = Field(None, description="Indicates whether the user has accepted the terms of service; set to true to mark acceptance or false to mark rejection."),
) -> dict[str, Any] | ToolResult:
    """Updates the acceptance status of a terms of service agreement for a specific user. Use this to record whether a user has accepted or declined a terms of service."""

    # Construct request model with validation
    try:
        _request = _models.PutTermsOfServiceUserStatusesIdRequest(
            path=_models.PutTermsOfServiceUserStatusesIdRequestPath(terms_of_service_user_status_id=terms_of_service_user_status_id),
            body=_models.PutTermsOfServiceUserStatusesIdRequestBody(is_accepted=is_accepted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_terms_of_service_user_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/terms_of_service_user_statuses/{terms_of_service_user_status_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/terms_of_service_user_statuses/{terms_of_service_user_status_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_terms_of_service_user_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_terms_of_service_user_status", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_terms_of_service_user_status",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Domain restrictions for collaborations
@mcp.tool(
    title="Get Collaboration Whitelist Entry",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_collaboration_whitelist_entry(collaboration_whitelist_entry_id: str = Field(..., description="The unique identifier of the collaboration whitelist entry to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific domain that has been approved for external collaborations within the current enterprise. Use this to inspect the details of a single whitelisted domain entry by its unique ID."""

    # Construct request model with validation
    try:
        _request = _models.GetCollaborationWhitelistEntriesIdRequest(
            path=_models.GetCollaborationWhitelistEntriesIdRequestPath(collaboration_whitelist_entry_id=collaboration_whitelist_entry_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_collaboration_whitelist_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/collaboration_whitelist_entries/{collaboration_whitelist_entry_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/collaboration_whitelist_entries/{collaboration_whitelist_entry_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_collaboration_whitelist_entry")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_collaboration_whitelist_entry", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_collaboration_whitelist_entry",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Standard and Zones Storage Policy Assignments
@mcp.tool(
    title="List Storage Policy Assignments",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_storage_policy_assignments(
    resolved_for_type: Literal["user", "enterprise"] = Field(..., description="The type of entity to retrieve storage policy assignments for, either a specific user or an entire enterprise."),
    resolved_for_id: str = Field(..., description="The unique identifier of the user or enterprise whose storage policy assignments should be retrieved. Must correspond to the entity type specified in resolved_for_type."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all storage policy assignments for a specified enterprise or user. Returns the storage policies currently assigned to the given target."""

    # Construct request model with validation
    try:
        _request = _models.GetStoragePolicyAssignmentsRequest(
            query=_models.GetStoragePolicyAssignmentsRequestQuery(resolved_for_type=resolved_for_type, resolved_for_id=resolved_for_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_storage_policy_assignments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/storage_policy_assignments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_storage_policy_assignments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_storage_policy_assignments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_storage_policy_assignments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Standard and Zones Storage Policy Assignments
@mcp.tool(
    title="Assign Storage Policy",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def assign_storage_policy(
    storage_policy_type: Literal["storage_policy"] | None = Field(None, alias="storage_policyType", description="The resource type being assigned as the storage policy; must always be 'storage_policy'."),
    assigned_to_type: Literal["user", "enterprise"] | None = Field(None, alias="assigned_toType", description="The type of entity receiving the storage policy assignment, either an individual user or an entire enterprise."),
    storage_policy_id: str | None = Field(None, alias="storage_policyId", description="The unique identifier of the storage policy to assign to the target entity."),
    assigned_to_id: str | None = Field(None, alias="assigned_toId", description="The unique identifier of the user or enterprise to which the storage policy will be assigned."),
) -> dict[str, Any] | ToolResult:
    """Assigns a storage policy to a specific user or enterprise, controlling where their content is stored. Use this to enforce data residency or storage tier requirements."""

    # Construct request model with validation
    try:
        _request = _models.PostStoragePolicyAssignmentsRequest(
            body=_models.PostStoragePolicyAssignmentsRequestBody(storage_policy=_models.PostStoragePolicyAssignmentsRequestBodyStoragePolicy(type_=storage_policy_type, id_=storage_policy_id) if any(v is not None for v in [storage_policy_type, storage_policy_id]) else None,
                assigned_to=_models.PostStoragePolicyAssignmentsRequestBodyAssignedTo(type_=assigned_to_type, id_=assigned_to_id) if any(v is not None for v in [assigned_to_type, assigned_to_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for assign_storage_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/storage_policy_assignments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("assign_storage_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("assign_storage_policy", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="assign_storage_policy",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Standard and Zones Storage Policy Assignments
@mcp.tool(
    title="Get Storage Policy Assignment",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_storage_policy_assignment(storage_policy_assignment_id: str = Field(..., description="The unique identifier of the storage policy assignment to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific storage policy assignment by its unique identifier. Useful for inspecting which storage policy is applied to a particular user or enterprise."""

    # Construct request model with validation
    try:
        _request = _models.GetStoragePolicyAssignmentsIdRequest(
            path=_models.GetStoragePolicyAssignmentsIdRequestPath(storage_policy_assignment_id=storage_policy_assignment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_storage_policy_assignment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/storage_policy_assignments/{storage_policy_assignment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/storage_policy_assignments/{storage_policy_assignment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_storage_policy_assignment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_storage_policy_assignment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_storage_policy_assignment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Standard and Zones Storage Policy Assignments
@mcp.tool(
    title="Delete Storage Policy Assignment",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_storage_policy_assignment(storage_policy_assignment_id: str = Field(..., description="The unique identifier of the storage policy assignment to delete.")) -> dict[str, Any] | ToolResult:
    """Removes a storage policy assignment, causing the affected user to inherit the enterprise's default storage policy. Note: this endpoint is rate-limited to two calls per user within any 24-hour period."""

    # Construct request model with validation
    try:
        _request = _models.DeleteStoragePolicyAssignmentsIdRequest(
            path=_models.DeleteStoragePolicyAssignmentsIdRequestPath(storage_policy_assignment_id=storage_policy_assignment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_storage_policy_assignment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/storage_policy_assignments/{storage_policy_assignment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/storage_policy_assignments/{storage_policy_assignment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_storage_policy_assignment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_storage_policy_assignment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_storage_policy_assignment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Zip Downloads
@mcp.tool(
    title="Create Zip Download",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_zip_download(
    items: list[_models.PostZipDownloadsBodyItemsItem] | None = Field(None, description="A list of files and folders to include in the zip archive. Order is not significant; each item should specify its type and identifier."),
    download_file_name: str | None = Field(None, description="The base name for the generated zip archive file, without the file extension. The `.zip` extension will be appended automatically."),
) -> dict[str, Any] | ToolResult:
    """Initiates a zip archive download request for multiple files and folders, validating access permissions and returning a download URL and status URL. The archive is limited to 10,000 files or the account's upload limit, with a recommended maximum total size of 25GB."""

    # Construct request model with validation
    try:
        _request = _models.PostZipDownloadsRequest(
            body=_models.PostZipDownloadsRequestBody(items=items, download_file_name=download_file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_zip_download: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/zip_downloads"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_zip_download")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_zip_download", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_zip_download",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Zip Downloads
@mcp.tool(
    title="Download Zip Archive",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def download_zip_archive(zip_download_id: str = Field(..., description="The unique identifier for the zip archive, obtained from the `download_url` field returned by the Create Zip Download API.")) -> dict[str, Any] | ToolResult:
    """Downloads the binary contents of a previously created zip archive using the download URL provided when the archive was requested. This endpoint requires no authentication and is intended for direct browser-based downloads; the URL is time-limited and a new zip download request must be created if the session expires."""

    # Construct request model with validation
    try:
        _request = _models.GetZipDownloadsIdContentRequest(
            path=_models.GetZipDownloadsIdContentRequestPath(zip_download_id=zip_download_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for download_zip_archive: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/zip_downloads/{zip_download_id}/content", _request.path.model_dump(by_alias=True)) if _request.path else "/zip_downloads/{zip_download_id}/content"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("download_zip_archive")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("download_zip_archive", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="download_zip_archive",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Zip Downloads
@mcp.tool(
    title="Get Zip Download Status",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_zip_download_status(zip_download_id: str = Field(..., description="The unique identifier for the zip archive whose status is being checked, obtained from the response of the Create zip download API.")) -> dict[str, Any] | ToolResult:
    """Retrieves the current download progress and status of a zip archive, including any items that were skipped. This endpoint is accessible only after the download has started and remains valid for 12 hours from initiation."""

    # Construct request model with validation
    try:
        _request = _models.GetZipDownloadsIdStatusRequest(
            path=_models.GetZipDownloadsIdStatusRequestPath(zip_download_id=zip_download_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_zip_download_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/zip_downloads/{zip_download_id}/status", _request.path.model_dump(by_alias=True)) if _request.path else "/zip_downloads/{zip_download_id}/status"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_zip_download_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_zip_download_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_zip_download_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Box Sign requests
@mcp.tool(
    title="Cancel Sign Request",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def cancel_sign_request(
    sign_request_id: str = Field(..., description="The unique identifier of the sign request to cancel."),
    reason: str | None = Field(None, description="An optional explanation for why the sign request is being cancelled, useful for audit trails and notifying stakeholders."),
) -> dict[str, Any] | ToolResult:
    """Cancels an active Box Sign request, preventing further signing actions by any recipients. An optional reason can be provided to document why the request was cancelled."""

    # Construct request model with validation
    try:
        _request = _models.PostSignRequestsIdCancelRequest(
            path=_models.PostSignRequestsIdCancelRequestPath(sign_request_id=sign_request_id),
            body=_models.PostSignRequestsIdCancelRequestBody(reason=reason)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for cancel_sign_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sign_requests/{sign_request_id}/cancel", _request.path.model_dump(by_alias=True)) if _request.path else "/sign_requests/{sign_request_id}/cancel"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("cancel_sign_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("cancel_sign_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="cancel_sign_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Box Sign requests
@mcp.tool(
    title="Resend Sign Request",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def resend_sign_request(sign_request_id: str = Field(..., description="The unique identifier of the signature request to resend notifications for.")) -> dict[str, Any] | ToolResult:
    """Resends the signature request email to all outstanding signers who have not yet completed signing. Useful for following up on pending signatures without creating a new request."""

    # Construct request model with validation
    try:
        _request = _models.PostSignRequestsIdResendRequest(
            path=_models.PostSignRequestsIdResendRequestPath(sign_request_id=sign_request_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for resend_sign_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sign_requests/{sign_request_id}/resend", _request.path.model_dump(by_alias=True)) if _request.path else "/sign_requests/{sign_request_id}/resend"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("resend_sign_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("resend_sign_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="resend_sign_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Box Sign requests
@mcp.tool(
    title="Get Sign Request",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_sign_request(sign_request_id: str = Field(..., description="The unique identifier of the Box Sign request to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific Box Sign request by its unique ID. Use this to check the status, signers, and configuration of an existing signature request."""

    # Construct request model with validation
    try:
        _request = _models.GetSignRequestsIdRequest(
            path=_models.GetSignRequestsIdRequestPath(sign_request_id=sign_request_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sign_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sign_requests/{sign_request_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sign_requests/{sign_request_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sign_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sign_request", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sign_request",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Box Sign requests
@mcp.tool(
    title="List Sign Requests",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_sign_requests(
    limit: str | None = Field(None, description="Maximum number of signature requests to return per page. Accepts values up to 1000."),
    senders: list[str] | None = Field(None, description="Filters results to only include signature requests sent by the specified email addresses. Requires `shared_requests` to be set to `true` when used. Order is not significant; each item should be a valid email address."),
    shared_requests: bool | None = Field(None, description="When `true`, returns only signature requests where the authenticated user is a collaborator (not the owner); collaborator access is determined by the user's access level on the associated sign files. Must be `true` if `senders` is provided; defaults to `false`."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all Box Sign signature requests created by the authenticated user. Requests associated with deleted sign files or parent folders are excluded from results."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetSignRequestsRequest(
            query=_models.GetSignRequestsRequestQuery(limit=_limit, senders=senders, shared_requests=shared_requests)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sign_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/sign_requests"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sign_requests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sign_requests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sign_requests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Box Sign requests
@mcp.tool(
    title="Create Sign Request",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_sign_request(body: _models.SignRequestCreateRequest | None = Field(None, description="The request body containing all details needed to create the signature request, including the document to be signed, signer information, and any signing configuration options.")) -> dict[str, Any] | ToolResult:
    """Creates a Box Sign signature request by preparing a document for signing and dispatching it to one or more signers. Use this to initiate a new e-signature workflow on a document stored in Box."""

    # Construct request model with validation
    try:
        _request = _models.PostSignRequestsRequest(
            body=_models.PostSignRequestsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_sign_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/sign_requests"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_sign_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_sign_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_sign_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflows
@mcp.tool(
    title="List Workflows",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_workflows(
    folder_id: str = Field(..., description="The unique identifier of the folder whose associated workflows you want to retrieve. The root folder of a Box account is always ID 0; other folder IDs can be found in the URL when viewing the folder in the Box web app."),
    trigger_type: str | None = Field(None, description="Filters workflows by their trigger type, returning only workflows that match the specified trigger. Use to narrow results to a specific trigger category."),
    limit: str | None = Field(None, description="The maximum number of workflows to return in a single response, up to a limit of 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all workflows associated with a specific folder that have a manually triggerable flow. Requires the Manage Box Relay application scope to be enabled in the developer console."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetWorkflowsRequest(
            query=_models.GetWorkflowsRequestQuery(folder_id=folder_id, trigger_type=trigger_type, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/workflows"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflows", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflows",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflows
@mcp.tool(
    title="Start Workflow",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def start_workflow(
    workflow_id: str = Field(..., description="The unique identifier of the workflow to start."),
    type_: Literal["workflow_parameters"] | None = Field(None, alias="type", description="Identifies the type of the top-level parameters object being submitted; must be set to 'workflow_parameters'."),
    flow_type: str | None = Field(None, alias="flowType", description="Identifies the type of the flow object being referenced within the parameters."),
    folder_type: Literal["folder"] | None = Field(None, alias="folderType", description="Identifies the type of the folder object being referenced; must be set to 'folder'."),
    flow_id: str | None = Field(None, alias="flowId", description="The unique identifier of the specific flow within the workflow to trigger."),
    folder_id: str | None = Field(None, alias="folderId", description="The unique identifier of the folder configured for this workflow; all provided files must reside within this folder."),
    files: list[_models.PostWorkflowsIdStartBodyFilesItem] | None = Field(None, description="An array of file objects for which the workflow should be started; each file must already exist within the workflow's configured folder. Order is not significant."),
    outcomes: list[_models.Outcome] | None = Field(None, description="An array of configurable outcome objects that the workflow should complete as part of its execution. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Manually triggers a Box Relay workflow with a WORKFLOW_MANUAL_START trigger type for a specified folder and optional files. Requires the Manage Box Relay application scope to be authorized in the developer console."""

    # Construct request model with validation
    try:
        _request = _models.PostWorkflowsIdStartRequest(
            path=_models.PostWorkflowsIdStartRequestPath(workflow_id=workflow_id),
            body=_models.PostWorkflowsIdStartRequestBody(type_=type_, files=files, outcomes=outcomes,
                flow=_models.PostWorkflowsIdStartRequestBodyFlow(type_=flow_type, id_=flow_id) if any(v is not None for v in [flow_type, flow_id]) else None,
                folder=_models.PostWorkflowsIdStartRequestBodyFolder(type_=folder_type, id_=folder_id) if any(v is not None for v in [folder_type, folder_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for start_workflow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workflows/{workflow_id}/start", _request.path.model_dump(by_alias=True)) if _request.path else "/workflows/{workflow_id}/start"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("start_workflow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("start_workflow", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="start_workflow",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Box Sign templates
@mcp.tool(
    title="List Sign Templates",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_sign_templates(limit: str | None = Field(None, description="The maximum number of sign templates to return per page. Accepts values up to 1000.")) -> dict[str, Any] | ToolResult:
    """Retrieves all Box Sign templates created by the authenticated user. Returns a paginated list of templates available for use in signing workflows."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetSignTemplatesRequest(
            query=_models.GetSignTemplatesRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sign_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/sign_templates"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sign_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sign_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sign_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Box Sign templates
@mcp.tool(
    title="Get Sign Template",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_sign_template(template_id: str = Field(..., description="The unique identifier of the Box Sign template to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the full details of a specific Box Sign template by its unique ID. Use this to inspect template configuration, fields, and signers before initiating a signing request."""

    # Construct request model with validation
    try:
        _request = _models.GetSignTemplatesIdRequest(
            path=_models.GetSignTemplatesIdRequestPath(template_id=template_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sign_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sign_templates/{template_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sign_templates/{template_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sign_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sign_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sign_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration mappings
@mcp.tool(
    title="List Slack Integration Mappings",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_slack_integration_mappings(
    limit: str | None = Field(None, description="Maximum number of integration mappings to return per page. Accepts values up to 1000."),
    partner_item_type: Literal["channel"] | None = Field(None, description="Filters results to only return mappings for the specified Slack item type. Currently only 'channel' is supported."),
    partner_item_id: str | None = Field(None, description="Filters results to only return mappings associated with the specified Slack partner item ID, such as a specific Slack channel ID."),
    box_item_id: str | None = Field(None, description="Filters results to only return mappings associated with the specified Box item ID."),
    box_item_type: Literal["folder"] | None = Field(None, description="Filters results to only return mappings for the specified Box item type. Currently only 'folder' is supported."),
    is_manually_created: bool | None = Field(None, description="Filters results to only return mappings that were manually created (true) or automatically created (false)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all Slack integration mappings for the enterprise, showing how Box folders are linked to Slack channels. Requires Admin or Co-Admin role."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetIntegrationMappingsSlackRequest(
            query=_models.GetIntegrationMappingsSlackRequestQuery(limit=_limit, partner_item_type=partner_item_type, partner_item_id=partner_item_id, box_item_id=box_item_id, box_item_type=box_item_type, is_manually_created=is_manually_created)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_slack_integration_mappings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/integration_mappings/slack"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_slack_integration_mappings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_slack_integration_mappings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_slack_integration_mappings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration mappings
@mcp.tool(
    title="List Teams Integration Mappings",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_teams_integration_mappings(
    partner_item_type: Literal["channel", "team"] | None = Field(None, description="Filters results to only return mappings for the specified Microsoft Teams item type, either a channel or a team."),
    partner_item_id: str | None = Field(None, description="Filters results to only return mappings associated with the specified Microsoft Teams item ID."),
    box_item_id: str | None = Field(None, description="Filters results to only return mappings associated with the specified Box item ID."),
    box_item_type: Literal["folder"] | None = Field(None, description="Filters results to only return mappings for the specified Box item type. Currently only folder mappings are supported."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of Box for Teams integration mappings within an enterprise, showing how Box items are linked to Microsoft Teams channels or teams. Requires Admin or Co-Admin role."""

    # Construct request model with validation
    try:
        _request = _models.GetIntegrationMappingsTeamsRequest(
            query=_models.GetIntegrationMappingsTeamsRequestQuery(partner_item_type=partner_item_type, partner_item_id=partner_item_id, box_item_id=box_item_id, box_item_type=box_item_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_teams_integration_mappings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/integration_mappings/teams"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_teams_integration_mappings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_teams_integration_mappings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_teams_integration_mappings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration mappings
@mcp.tool(
    title="Create Teams Integration Mapping",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_teams_integration_mapping(
    partner_item: _models.PostIntegrationMappingsTeamsBodyPartnerItem | None = Field(None, description="The Microsoft Teams channel to map, identifying the partner-side resource in the integration."),
    box_item: _models.PostIntegrationMappingsTeamsBodyBoxItem | None = Field(None, description="The Box item (such as a folder) to map to the Teams channel, identifying the Box-side resource in the integration."),
) -> dict[str, Any] | ToolResult:
    """Creates a Teams integration mapping by linking a Microsoft Teams channel to a Box item. Requires Admin or Co-Admin role."""

    # Construct request model with validation
    try:
        _request = _models.PostIntegrationMappingsTeamsRequest(
            body=_models.PostIntegrationMappingsTeamsRequestBody(partner_item=partner_item, box_item=box_item)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_teams_integration_mapping: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/integration_mappings/teams"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_teams_integration_mapping")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_teams_integration_mapping", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_teams_integration_mapping",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: AI
@mcp.tool(
    title="Extract Metadata Freeform",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def extract_metadata_freeform(
    prompt: str | None = Field(None, description="The freeform prompt instructing the LLM on what metadata to extract and how. Supports XML or JSON schema format and can be up to 10,000 characters long."),
    items: Annotated[list[_models.AiItemBase], AfterValidator(_check_unique_items)] | None = Field(None, description="The list of files the LLM will process for metadata extraction. Order is not significant; each item must reference a valid file. Between 1 and 25 files may be included.", min_length=1, max_length=25),
    ai_agent: _models.AiAgentReference | _models.AiAgentExtract | None = Field(None, description="Optional AI agent configuration to override the default LLM settings used for this extraction request."),
) -> dict[str, Any] | ToolResult:
    """Sends a freeform prompt to an LLM to extract key-value metadata from one or more files, without requiring a predefined metadata template. Both the prompt structure and the output format are flexible, supporting XML or JSON schema prompts."""

    # Construct request model with validation
    try:
        _request = _models.PostAiExtractRequest(
            body=_models.PostAiExtractRequestBody(prompt=prompt, items=items, ai_agent=ai_agent)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for extract_metadata_freeform: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/ai/extract"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("extract_metadata_freeform")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("extract_metadata_freeform", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="extract_metadata_freeform",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: AI
@mcp.tool(
    title="Extract Structured Metadata",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def extract_structured_metadata(
    items: Annotated[list[_models.AiItemBase], AfterValidator(_check_unique_items)] | None = Field(None, description="The list of files to be processed by the LLM. Accepts between 1 and 25 file items; order does not affect extraction results.", min_length=1, max_length=25),
    template_key: str | None = Field(None, description="The unique key identifying the metadata template to use for extraction. Required when using a metadata template instead of a custom fields list."),
    type_: Literal["metadata_template"] | None = Field(None, alias="type", description="Specifies the extraction structure type. Must always be set to `metadata_template` when using a template-based extraction."),
    scope: str | None = Field(None, description="The scope of the metadata template, either global (available to all Box enterprises) or enterprise-scoped (prefixed with the enterprise ID). Maximum 40 characters.", max_length=40),
    fields: Annotated[list[_models.PostAiExtractStructuredBodyFieldsItem], AfterValidator(_check_unique_items)] | None = Field(None, description="A custom list of fields to extract from the provided files. Use this instead of a metadata template — exactly one of `fields` or a metadata template must be provided, not both. Requires at least one field.", min_length=1),
    include_confidence_score: bool | None = Field(None, description="When set to true, the response will include a confidence score for each extracted field, indicating the LLM's certainty about the extracted value."),
    include_reference: bool | None = Field(None, description="When set to true, the response will include source references for each extracted field, indicating where in the file the value was found."),
    ai_agent: _models.AiAgentReference | _models.AiAgentExtractStructured | None = Field(None, description="Optional AI agent configuration to override the default extraction agent settings, such as model selection or prompt behavior."),
) -> dict[str, Any] | ToolResult:
    """Sends files to a Box AI-supported LLM and returns extracted metadata as structured key-value pairs. Define the extraction structure using either a metadata template or a custom list of fields."""

    # Construct request model with validation
    try:
        _request = _models.PostAiExtractStructuredRequest(
            body=_models.PostAiExtractStructuredRequestBody(items=items, fields=fields, include_confidence_score=include_confidence_score, include_reference=include_reference, ai_agent=ai_agent,
                metadata_template=_models.PostAiExtractStructuredRequestBodyMetadataTemplate(template_key=template_key, type_=type_, scope=scope) if any(v is not None for v in [template_key, type_, scope]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for extract_structured_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/ai/extract_structured"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("extract_structured_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("extract_structured_metadata", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="extract_structured_metadata",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Studio
@mcp.tool(
    title="List AI Agents",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_ai_agents(
    mode: list[str] | None = Field(None, description="Filters results to only return agents configured for the specified modes. Accepts one or more of the following values: `ask`, `text_gen`, or `extract`. Order is not significant."),
    agent_state: list[str] | None = Field(None, description="Filters results to only return agents in the specified states. Accepts one or more of the following values: `enabled`, `disabled`, or `enabled_for_selected_users`. Order is not significant."),
    include_box_default: bool | None = Field(None, description="When set to true, includes Box-provided default agents in the response alongside any custom agents."),
    limit: str | None = Field(None, description="The maximum number of agents to return in a single response. Accepts a value between 1 and 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of AI agents configured in the account, with optional filtering by mode, state, and whether to include Box default agents."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetAiAgentsRequest(
            query=_models.GetAiAgentsRequestQuery(mode=mode, agent_state=agent_state, include_box_default=include_box_default, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_ai_agents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/ai_agents"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "mode": ("form", False),
        "agent_state": ("form", False),
    })
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_ai_agents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_ai_agents", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_ai_agents",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Studio
@mcp.tool(
    title="Create AI Agent",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_ai_agent(
    type_: Literal["ai_agent"] | None = Field(None, alias="type", description="Identifies this configuration as an AI agent resource."),
    ask_type: Literal["ai_agent_ask"] | None = Field(None, alias="askType", description="Identifies the ask capability block as an AI agent ask handler."),
    text_gen_type: Literal["ai_agent_text_gen"] | None = Field(None, alias="text_genType", description="Identifies the text generation capability block as an AI agent text generator."),
    extract_type: Literal["ai_agent_extract"] | None = Field(None, alias="extractType", description="Identifies the extract capability block as an AI agent metadata extractor."),
    name: str | None = Field(None, description="Human-readable display name for the AI agent, shown in the UI and used to identify the agent."),
    access_state: str | None = Field(None, description="Controls the overall availability of the AI agent. Use `enabled` to make it available to all, `disabled` to deactivate it, or `enabled_for_selected_users` to restrict access to specific users."),
    ask_access_state: str | None = Field(None, alias="askAccess_state", description="Controls whether the ask capability is active. Set to `enabled` to allow users to ask questions, or `disabled` to turn it off."),
    text_gen_access_state: str | None = Field(None, alias="text_genAccess_state", description="Controls whether the text generation capability is active. Set to `enabled` to allow text generation, or `disabled` to turn it off."),
    extract_access_state: str | None = Field(None, alias="extractAccess_state", description="Controls whether the metadata extraction capability is active. Set to `enabled` to allow extraction, or `disabled` to turn it off."),
    icon_reference: str | None = Field(None, description="URL pointing to the avatar icon displayed for this AI agent in the UI. Must be a valid Box CDN URL using one of the supported avatar filenames.", min_length=1),
    allowed_entities: list[_models.UserBase | _models.GroupBase] | None = Field(None, description="List of users or groups permitted to use this AI agent when access is restricted to selected entities. Each item should reference a valid user or group."),
    ask_description: str | None = Field(None, alias="askDescription", description="Human-readable description of the ask capability, explaining its purpose or behavior to users."),
    text_gen_description: str | None = Field(None, alias="text_genDescription", description="Human-readable description of the text generation capability, explaining its purpose or behavior to users."),
    extract_description: str | None = Field(None, alias="extractDescription", description="Human-readable description of the extract capability, explaining its purpose or behavior to users."),
    ask_custom_instructions: str | None = Field(None, alias="askCustom_instructions", description="Custom behavioral instructions that guide how the ask capability responds, allowing tailored tone, scope, or domain-specific rules."),
    text_gen_custom_instructions: str | None = Field(None, alias="text_genCustom_instructions", description="Custom behavioral instructions that guide how the text generation capability produces output, allowing tailored tone, scope, or domain-specific rules."),
    extract_custom_instructions: str | None = Field(None, alias="extractCustom_instructions", description="Custom behavioral instructions that guide how the extract capability identifies and pulls metadata, allowing tailored scope or domain-specific rules."),
    ask_suggested_questions: list[str] | None = Field(None, alias="askSuggested_questions", description="Up to 4 pre-defined questions surfaced to users when interacting with the ask capability. Pass null to auto-generate suggestions, or an empty array to show none.", max_length=4),
    text_gen_suggested_questions: list[str] | None = Field(None, alias="text_genSuggested_questions", description="Up to 4 pre-defined questions surfaced to users when interacting with the text generation capability. Pass null to auto-generate suggestions, or an empty array to show none.", max_length=4),
    ask_long_text: _models.PostAiAgentsBodyAskLongText | None = Field(None, alias="askLong_text", description="Configuration for the processor that handles long-form text content within the ask capability, such as chunking strategy and model settings."),
    extract_long_text: _models.PostAiAgentsBodyExtractLongText | None = Field(None, alias="extractLong_text", description="Configuration for the processor that handles long-form text content within the extract capability, such as chunking strategy and model settings."),
    ask_basic_text: _models.PostAiAgentsBodyAskBasicText | None = Field(None, alias="askBasic_text", description="Configuration for the processor that handles standard-length text content within the ask capability, including model and prompt settings."),
    extract_basic_text: _models.PostAiAgentsBodyExtractBasicText | None = Field(None, alias="extractBasic_text", description="Configuration for the processor that handles standard-length text content within the extract capability, including model and prompt settings."),
    ask_basic_image: _models.PostAiAgentsBodyAskBasicImage | None = Field(None, alias="askBasic_image", description="Configuration for the processor that handles image content within the ask capability, including model and prompt settings."),
    extract_basic_image: _models.PostAiAgentsBodyExtractBasicImage | None = Field(None, alias="extractBasic_image", description="Configuration for the processor that handles image content within the extract capability, including model and prompt settings."),
    spreadsheet: _models.PostAiAgentsBodyAskSpreadsheet | None = Field(None, description="Configuration for the tool that processes spreadsheet and tabular data, controlling how structured data is interpreted by the agent."),
    long_text_multi: _models.PostAiAgentsBodyAskLongTextMulti | None = Field(None, description="Configuration for the processor that handles long-form text across multiple documents or segments, used for multi-document ask scenarios."),
    basic_text_multi: _models.PostAiAgentsBodyAskBasicTextMulti | None = Field(None, description="Configuration for the processor that handles standard-length text across multiple documents or segments, used for multi-document ask scenarios."),
    basic_image_multi: _models.PostAiAgentsBodyAskBasicImageMulti | None = Field(None, description="Configuration for the processor that handles images across multiple documents or segments, used for multi-document ask scenarios."),
    basic_gen: _models.PostAiAgentsBodyTextGenBasicGen | None = Field(None, description="Configuration for the basic text generation tool used by the text_gen capability, controlling model behavior and prompt structure for content generation."),
) -> dict[str, Any] | ToolResult:
    """Creates a new AI agent with one or more capabilities (ask, text_gen, or extract). At least one capability must be configured when creating the agent."""

    # Construct request model with validation
    try:
        _request = _models.PostAiAgentsRequest(
            body=_models.PostAiAgentsRequestBody(type_=type_, name=name, access_state=access_state, icon_reference=icon_reference, allowed_entities=allowed_entities,
                ask=_models.PostAiAgentsRequestBodyAsk(type_=ask_type, access_state=ask_access_state, description=ask_description, custom_instructions=ask_custom_instructions, suggested_questions=ask_suggested_questions, long_text=ask_long_text, basic_text=ask_basic_text, basic_image=ask_basic_image, spreadsheet=spreadsheet, long_text_multi=long_text_multi, basic_text_multi=basic_text_multi, basic_image_multi=basic_image_multi) if any(v is not None for v in [ask_type, ask_access_state, ask_description, ask_custom_instructions, ask_suggested_questions, ask_long_text, ask_basic_text, ask_basic_image, spreadsheet, long_text_multi, basic_text_multi, basic_image_multi]) else None,
                text_gen=_models.PostAiAgentsRequestBodyTextGen(type_=text_gen_type, access_state=text_gen_access_state, description=text_gen_description, custom_instructions=text_gen_custom_instructions, suggested_questions=text_gen_suggested_questions, basic_gen=basic_gen) if any(v is not None for v in [text_gen_type, text_gen_access_state, text_gen_description, text_gen_custom_instructions, text_gen_suggested_questions, basic_gen]) else None,
                extract_=_models.PostAiAgentsRequestBodyExtract(type_=extract_type, access_state=extract_access_state, description=extract_description, custom_instructions=extract_custom_instructions, long_text=extract_long_text, basic_text=extract_basic_text, basic_image=extract_basic_image) if any(v is not None for v in [extract_type, extract_access_state, extract_description, extract_custom_instructions, extract_long_text, extract_basic_text, extract_basic_image]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_ai_agent: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/ai_agents"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_ai_agent")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_ai_agent", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_ai_agent",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: AI Studio
@mcp.tool(
    title="Get AI Agent",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_ai_agent(agent_id: str = Field(..., description="The unique identifier of the AI agent to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific AI agent by its unique identifier. Returns the full agent configuration and metadata for the specified agent."""

    # Construct request model with validation
    try:
        _request = _models.GetAiAgentsIdRequest(
            path=_models.GetAiAgentsIdRequestPath(agent_id=agent_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_ai_agent: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/ai_agents/{agent_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/ai_agents/{agent_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_ai_agent")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_ai_agent", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_ai_agent",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata taxonomies
@mcp.tool(
    title="List Metadata Taxonomies",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_metadata_taxonomies(
    namespace: str = Field(..., description="The namespace that scopes the metadata taxonomies to retrieve, typically representing an enterprise or organizational boundary."),
    limit: str | None = Field(None, description="The maximum number of taxonomy items to return in a single page of results, up to a maximum of 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all metadata taxonomies within a specified namespace, enabling discovery of available taxonomy structures for organizing and classifying content metadata."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetMetadataTaxonomiesIdRequest(
            path=_models.GetMetadataTaxonomiesIdRequestPath(namespace=namespace),
            query=_models.GetMetadataTaxonomiesIdRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_metadata_taxonomies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/metadata_taxonomies/{namespace}", _request.path.model_dump(by_alias=True)) if _request.path else "/metadata_taxonomies/{namespace}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_metadata_taxonomies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_metadata_taxonomies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_metadata_taxonomies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata taxonomies
@mcp.tool(
    title="Get Metadata Taxonomy",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_metadata_taxonomy(
    namespace: str = Field(..., description="The namespace that scopes the metadata taxonomy, typically representing an enterprise or organizational unit."),
    taxonomy_key: str = Field(..., description="The unique key identifying the metadata taxonomy to retrieve within the specified namespace."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific metadata taxonomy by its unique key within a given namespace. Use this to inspect the structure and configuration of a taxonomy for organizing and classifying metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetMetadataTaxonomiesIdIdRequest(
            path=_models.GetMetadataTaxonomiesIdIdRequestPath(namespace=namespace, taxonomy_key=taxonomy_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metadata_taxonomy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/metadata_taxonomies/{namespace}/{taxonomy_key}", _request.path.model_dump(by_alias=True)) if _request.path else "/metadata_taxonomies/{namespace}/{taxonomy_key}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metadata_taxonomy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metadata_taxonomy", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metadata_taxonomy",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata taxonomies
@mcp.tool(
    title="List Taxonomy Nodes",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_taxonomy_nodes(
    namespace: str = Field(..., description="The namespace that owns the metadata taxonomy, used to scope the taxonomy to a specific organization or enterprise."),
    taxonomy_key: str = Field(..., description="The unique key identifying the metadata taxonomy within the given namespace."),
    level: list[int] | None = Field(None, description="Filters nodes to only those at the specified depth level(s) within the taxonomy hierarchy. Multiple values may be provided; nodes matching any specified level are returned."),
    parent: list[str] | None = Field(None, description="Filters nodes to only those whose immediate parent matches the specified node identifier(s). Multiple values may be provided; nodes matching any specified parent are returned."),
    ancestor: list[str] | None = Field(None, description="Filters nodes to only those that are descendants of the specified ancestor node identifier(s) at any depth. Multiple values may be provided; nodes matching any specified ancestor are returned."),
    query: str | None = Field(None, description="Free-text search string to find matching taxonomy nodes by name or content. When provided, results are ranked by relevance rather than lexicographic order."),
    include_total_result_count: bool | None = Field(None, alias="include-total-result-count", description="When set to true, includes the total count of matching nodes in the response. Counts are computed for up to 10,000 matching elements; defaults to false."),
    limit: str | None = Field(None, description="The maximum number of taxonomy nodes to return in a single page of results. Must be between 1 and 1,000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves nodes within a specific metadata taxonomy, supporting filtering by level, parent, or ancestor relationships. Results are sorted lexicographically by default, or by relevance when a search query is provided."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetMetadataTaxonomiesIdIdNodesRequest(
            path=_models.GetMetadataTaxonomiesIdIdNodesRequestPath(namespace=namespace, taxonomy_key=taxonomy_key),
            query=_models.GetMetadataTaxonomiesIdIdNodesRequestQuery(level=level, parent=parent, ancestor=ancestor, query=query, include_total_result_count=include_total_result_count, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_taxonomy_nodes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/metadata_taxonomies/{namespace}/{taxonomy_key}/nodes", _request.path.model_dump(by_alias=True)) if _request.path else "/metadata_taxonomies/{namespace}/{taxonomy_key}/nodes"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_taxonomy_nodes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_taxonomy_nodes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_taxonomy_nodes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata taxonomies
@mcp.tool(
    title="Get Taxonomy Node",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_taxonomy_node(
    namespace: str = Field(..., description="The namespace that scopes the metadata taxonomy, typically representing an enterprise or organizational unit."),
    taxonomy_key: str = Field(..., description="The unique key identifying the metadata taxonomy within the namespace, representing a classification domain such as geography or department."),
    node_id: str = Field(..., description="The unique identifier of the taxonomy node to retrieve, formatted as a UUID."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single metadata taxonomy node by its unique identifier within a specified namespace and taxonomy. Useful for inspecting the details of a specific classification node in a hierarchical metadata structure."""

    # Construct request model with validation
    try:
        _request = _models.GetMetadataTaxonomiesIdIdNodesIdRequest(
            path=_models.GetMetadataTaxonomiesIdIdNodesIdRequestPath(namespace=namespace, taxonomy_key=taxonomy_key, node_id=node_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_taxonomy_node: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/metadata_taxonomies/{namespace}/{taxonomy_key}/nodes/{node_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/metadata_taxonomies/{namespace}/{taxonomy_key}/nodes/{node_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_taxonomy_node")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_taxonomy_node", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_taxonomy_node",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata taxonomies
@mcp.tool(
    title="Delete Taxonomy Node",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_taxonomy_node(
    namespace: str = Field(..., description="The namespace that scopes the metadata taxonomy, typically representing an organization or enterprise account."),
    taxonomy_key: str = Field(..., description="The unique key identifying the metadata taxonomy within the namespace."),
    node_id: str = Field(..., description="The unique identifier of the taxonomy node to delete. The node must have no children before it can be removed."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific node from a metadata taxonomy. Only leaf nodes (those without children) can be deleted, and this action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteMetadataTaxonomiesIdIdNodesIdRequest(
            path=_models.DeleteMetadataTaxonomiesIdIdNodesIdRequestPath(namespace=namespace, taxonomy_key=taxonomy_key, node_id=node_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_taxonomy_node: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/metadata_taxonomies/{namespace}/{taxonomy_key}/nodes/{node_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/metadata_taxonomies/{namespace}/{taxonomy_key}/nodes/{node_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_taxonomy_node")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_taxonomy_node", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_taxonomy_node",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Metadata taxonomies
@mcp.tool(
    title="List Taxonomy Field Options",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_taxonomy_field_options(
    namespace: str = Field(..., description="The namespace that scopes the metadata taxonomy, typically tied to an enterprise account."),
    template_key: str = Field(..., description="The unique key identifying the metadata template that contains the taxonomy field."),
    field_key: str = Field(..., description="The key identifying the specific taxonomy field within the metadata template whose options are being retrieved."),
    level: list[int] | None = Field(None, description="Filters results to taxonomy nodes at the specified depth levels. Multiple values may be provided; nodes matching any specified level are included."),
    parent: list[str] | None = Field(None, description="Filters results to nodes that are direct children of the specified parent node identifiers. Multiple values may be provided; nodes matching any specified parent are included."),
    ancestor: list[str] | None = Field(None, description="Filters results to nodes that are descendants of the specified ancestor node identifiers at any depth. Multiple values may be provided; nodes matching any specified ancestor are included."),
    query: str | None = Field(None, description="Free-text search string to find matching taxonomy nodes by name or label. When provided, results are ranked by relevance rather than lexicographic order."),
    include_total_result_count: bool | None = Field(None, alias="include-total-result-count", description="When set to true, the response includes the total count of nodes matching the query, computed for up to 10,000 results. Defaults to false."),
    only_selectable_options: bool | None = Field(None, alias="only-selectable-options", description="When set to true, restricts results to only those taxonomy nodes that are valid selectable options for this field. When false, all taxonomy nodes are returned regardless of selectability. Defaults to true."),
    limit: str | None = Field(None, description="The maximum number of taxonomy nodes to return in a single page of results. Must be between 1 and 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves available taxonomy nodes for a specific taxonomy field within a metadata template, filtered by level, parent, ancestor, or search query. Results are sorted lexicographically by default, or by relevance when a query is provided."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetMetadataTemplatesIdIdFieldsIdOptionsRequest(
            path=_models.GetMetadataTemplatesIdIdFieldsIdOptionsRequestPath(namespace=namespace, template_key=template_key, field_key=field_key),
            query=_models.GetMetadataTemplatesIdIdFieldsIdOptionsRequestQuery(level=level, parent=parent, ancestor=ancestor, query=query, include_total_result_count=include_total_result_count, only_selectable_options=only_selectable_options, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_taxonomy_field_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/metadata_templates/{namespace}/{template_key}/fields/{field_key}/options", _request.path.model_dump(by_alias=True)) if _request.path else "/metadata_templates/{namespace}/{template_key}/fields/{field_key}/options"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_taxonomy_field_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_taxonomy_field_options", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_taxonomy_field_options",
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
        print("  python box_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Box MCP Server")

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
    logger.info("Starting Box MCP Server")
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

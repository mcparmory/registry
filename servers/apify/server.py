#!/usr/bin/env python3
"""
Apify MCP Server

API Info:
- API License: Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0.html)

Generated: 2026-05-11 22:59:53 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://api.apify.com/v2")
SERVER_NAME = "Apify"
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

def build_webhooks(webhook_event_types: list[str] | None = None, webhook_request_url: str | None = None) -> str | None:
    """Helper function for parameter transformation"""
    try:
        if webhook_event_types is None and webhook_request_url is None:
            return None
        webhook = {}
        if webhook_event_types is not None:
            webhook['eventTypes'] = webhook_event_types
        if webhook_request_url is not None:
            webhook['requestUrl'] = webhook_request_url
        webhooks_array = [webhook]
        json_bytes = json.dumps(webhooks_array).encode('utf-8')
        return base64.b64encode(json_bytes).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Failed to build webhooks parameter: {e}")


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
    'httpBearer',
    'apiKey',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["httpBearer"] = _auth.BearerTokenAuth(env_var="BEARER_TOKEN", token_format="Bearer")
    logging.info("Authentication configured: httpBearer")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for httpBearer not configured: {error_msg}")
    _auth_handlers["httpBearer"] = None
try:
    _auth_handlers["apiKey"] = _auth.APIKeyAuth(env_var="API_KEY", location="query", param_name="token")
    logging.info("Authentication configured: apiKey")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for apiKey not configured: {error_msg}")
    _auth_handlers["apiKey"] = None

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

mcp = FastMCP("Apify", middleware=[_JsonCoercionMiddleware()])

# Tags: Actors
@mcp.tool(
    title="List Actors",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_actors(
    my: bool | None = Field(None, description="When set to true, restricts the results to only Actors owned by the authenticated user, excluding Actors they have used but not created."),
    offset: float | None = Field(None, description="Number of records to skip from the beginning of the result set, used for paginating through large lists. Defaults to 0."),
    limit: float | None = Field(None, description="Maximum number of Actors to return in a single response. Accepts values between 1 and 1000, with 1000 being both the default and the upper limit."),
    desc: bool | None = Field(None, description="When set to true, reverses the sort order so that the most recently created (or most recently run, if sorting by last run) Actors appear first."),
    sort_by: Literal["createdAt", "stats.lastRunStartedAt"] | None = Field(None, alias="sortBy", description="Determines the field used to order results. Use 'createdAt' to sort by when the Actor was created, or 'stats.lastRunStartedAt' to sort by the most recent run start time."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of Actors the user has created or used, with options to filter to owned Actors only and sort by creation date or last run time. Returns up to 1000 records per request."""

    # Construct request model with validation
    try:
        _request = _models.ActsGetRequest(
            query=_models.ActsGetRequestQuery(my=my, offset=offset, limit=limit, desc=desc, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_actors: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/acts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_actors")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_actors", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_actors",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors
@mcp.tool(
    title="Create Actor",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_actor(
    name: str | None = Field(None, description="Unique identifier name for the Actor, used in URLs and API references."),
    description: str | None = Field(None, description="Short human-readable description of what the Actor does, displayed in Apify Store and the Actor detail page."),
    title: str | None = Field(None, description="Display title for the Actor shown in Apify Store; required when making the Actor public."),
    is_public: bool | None = Field(None, alias="isPublic", description="Whether the Actor is publicly listed in Apify Store; requires title and categories to be set when true."),
    seo_title: str | None = Field(None, alias="seoTitle", description="SEO-optimized title for the Actor's store page, used for search engine indexing."),
    seo_description: str | None = Field(None, alias="seoDescription", description="SEO-optimized description for the Actor's store page, used for search engine indexing."),
    restart_on_error: bool | None = Field(None, alias="restartOnError", description="Whether the Actor run should automatically restart if it encounters an error during execution."),
    versions: list[_models.Version] | None = Field(None, description="List of source code version objects defining the Actor's versioned implementations; at least one version is required. Each item follows the Version object schema."),
    pricing_infos: list[_models.PayPerEventActorPricingInfo | _models.PricePerDatasetItemActorPricingInfo | _models.FlatPricePerMonthActorPricingInfo | _models.FreeActorPricingInfo] | None = Field(None, alias="pricingInfos", description="List of pricing information objects associated with the Actor, defining monetization tiers or pay-per-result configurations."),
    categories: list[str] | None = Field(None, description="List of Apify Store category identifiers under which the Actor is classified; required when isPublic is true. Use constants from the apify-shared-js package."),
    default_run_options_build: str | None = Field(None, alias="defaultRunOptionsBuild", description="The default build tag or version to use when starting a run, such as a semantic version tag or 'latest'."),
    actor_standby_build: str | None = Field(None, alias="actorStandbyBuild", description="The build tag or version to use when starting the Actor in Standby mode."),
    timeout_secs: int | None = Field(None, alias="timeoutSecs", description="Default maximum run duration in seconds; the run is terminated if it exceeds this limit."),
    default_run_options_memory_mbytes: int | None = Field(None, alias="defaultRunOptionsMemoryMbytes", description="Default memory allocation in megabytes for each Actor run; must be a power of 2."),
    actor_standby_memory_mbytes: int | None = Field(None, alias="actorStandbyMemoryMbytes", description="Memory allocation in megabytes for the Actor when running in Standby mode."),
    max_items: int | None = Field(None, alias="maxItems", description="Maximum number of output items the Actor is allowed to produce per run; used for pay-per-result pricing enforcement."),
    force_permission_level: Literal["LIMITED_PERMISSIONS", "FULL_PERMISSIONS"] | None = Field(None, alias="forcePermissionLevel", description="Specifies the permission level the Actor requires at runtime; use LIMITED_PERMISSIONS to restrict access or FULL_PERMISSIONS for unrestricted access. See Actor permissions documentation for details."),
    is_enabled: bool | None = Field(None, alias="isEnabled", description="Whether the Actor is enabled and available to be run; set to false to disable the Actor without deleting it."),
    desired_requests_per_actor_run: int | None = Field(None, alias="desiredRequestsPerActorRun", description="Target number of requests to be processed per Actor run in Standby mode, used for autoscaling decisions."),
    max_requests_per_actor_run: int | None = Field(None, alias="maxRequestsPerActorRun", description="Hard upper limit on the number of requests processed per Actor run in Standby mode."),
    idle_timeout_secs: int | None = Field(None, alias="idleTimeoutSecs", description="Duration in seconds after which an idle Standby Actor instance is terminated to free resources."),
    disable_standby_fields_override: bool | None = Field(None, alias="disableStandbyFieldsOverride", description="When true, prevents automatic overriding of Standby-related fields by the platform during Actor configuration updates."),
    should_pass_actor_input: bool | None = Field(None, alias="shouldPassActorInput", description="Whether the Actor's input should be forwarded to Standby mode instances when they are activated."),
    body: str | None = Field(None, description="Raw JSON string representing the default input body passed to the Actor run."),
    content_type: str | None = Field(None, alias="contentType", description="MIME content type of the input body, specifying encoding and format for correct parsing."),
) -> dict[str, Any] | ToolResult:
    """Creates a new Actor on the Apify platform with the specified configuration, including source code versions, run options, and publishing settings. At least one version of the source code must be defined; set isPublic to true along with a title and categories to list the Actor in Apify Store."""

    # Construct request model with validation
    try:
        _request = _models.ActsPostRequest(
            body=_models.ActsPostRequestBody(name=name, description=description, title=title, is_public=is_public, seo_title=seo_title, seo_description=seo_description, versions=versions, pricing_infos=pricing_infos, categories=categories,
                default_run_options=_models.ActsPostRequestBodyDefaultRunOptions(restart_on_error=restart_on_error, build=default_run_options_build, timeout_secs=timeout_secs, memory_mbytes=default_run_options_memory_mbytes, max_items=max_items, force_permission_level=force_permission_level) if any(v is not None for v in [restart_on_error, default_run_options_build, timeout_secs, default_run_options_memory_mbytes, max_items, force_permission_level]) else None,
                actor_standby=_models.ActsPostRequestBodyActorStandby(build=actor_standby_build, memory_mbytes=actor_standby_memory_mbytes, is_enabled=is_enabled, desired_requests_per_actor_run=desired_requests_per_actor_run, max_requests_per_actor_run=max_requests_per_actor_run, idle_timeout_secs=idle_timeout_secs, disable_standby_fields_override=disable_standby_fields_override, should_pass_actor_input=should_pass_actor_input) if any(v is not None for v in [actor_standby_build, actor_standby_memory_mbytes, is_enabled, desired_requests_per_actor_run, max_requests_per_actor_run, idle_timeout_secs, disable_standby_fields_override, should_pass_actor_input]) else None,
                example_run_input=_models.ActsPostRequestBodyExampleRunInput(body=body, content_type=content_type) if any(v is not None for v in [body, content_type]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_actor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/acts"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_actor")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_actor", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_actor",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors
@mcp.tool(
    title="Get Actor",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_actor(actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor to retrieve, either as an Actor ID or a tilde-separated combination of the owner's username and Actor name.")) -> dict[str, Any] | ToolResult:
    """Retrieves full details for a specific Actor, including its configuration, settings, and metadata. Use this to inspect an Actor before running it or to verify its current state."""

    # Construct request model with validation
    try:
        _request = _models.ActGetRequest(
            path=_models.ActGetRequestPath(actor_id=actor_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_actor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_actor")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_actor", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_actor",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors
@mcp.tool(
    title="Update Actor",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_actor(
    actor_id: str = Field(..., alias="actorId", description="The unique ID of the Actor, or a tilde-separated string combining the owner's username and Actor name."),
    name: str | None = Field(None, description="The internal name identifier for the Actor."),
    description: str | None = Field(None, description="A short human-readable description of what the Actor does."),
    is_public: bool | None = Field(None, alias="isPublic", description="Whether the Actor is publicly visible in Apify Store. Setting this to true also requires providing a title and categories."),
    actor_permission_level: Literal["LIMITED_PERMISSIONS", "FULL_PERMISSIONS"] | None = Field(None, alias="actorPermissionLevel", description="Specifies the permission level the Actor requires at runtime. Use LIMITED_PERMISSIONS for restricted access or FULL_PERMISSIONS for unrestricted platform access."),
    seo_title: str | None = Field(None, alias="seoTitle", description="The SEO-optimized title used for the Actor's page in Apify Store search results."),
    seo_description: str | None = Field(None, alias="seoDescription", description="The SEO-optimized description used for the Actor's page in Apify Store search results."),
    title: str | None = Field(None, description="The display title shown for the Actor in Apify Store. Required when making the Actor public."),
    restart_on_error: bool | None = Field(None, alias="restartOnError", description="Whether the Actor should automatically restart if it encounters an error during a run."),
    versions: list[_models.CreateOrUpdateVersionRequest] | None = Field(None, description="An array of version objects defining the Actor's available versions and their source configurations. Order is not significant."),
    pricing_infos: list[_models.PayPerEventActorPricingInfo | _models.PricePerDatasetItemActorPricingInfo | _models.FlatPricePerMonthActorPricingInfo | _models.FreeActorPricingInfo] | None = Field(None, alias="pricingInfos", description="An array of pricing information objects associated with the Actor. Order is not significant."),
    categories: list[str] | None = Field(None, description="An array of category identifiers under which the Actor is classified in Apify Store. Required when making the Actor public. Use constants from the apify-shared-js package."),
    default_run_options_build: str | None = Field(None, alias="defaultRunOptionsBuild", description="The default build tag or version to use when starting a run, such as a version tag."),
    actor_standby_build: str | None = Field(None, alias="actorStandbyBuild", description="The build tag or version to use when starting the Actor in Standby mode."),
    timeout_secs: int | None = Field(None, alias="timeoutSecs", description="The default maximum run duration in seconds before the run is forcefully stopped."),
    default_run_options_memory_mbytes: int | None = Field(None, alias="defaultRunOptionsMemoryMbytes", description="The default amount of memory in megabytes allocated to each Actor run."),
    actor_standby_memory_mbytes: int | None = Field(None, alias="actorStandbyMemoryMbytes", description="The amount of memory in megabytes allocated when the Actor runs in Standby mode."),
    max_items: int | None = Field(None, alias="maxItems", description="The maximum number of items the Actor is allowed to return in a single run."),
    force_permission_level: Literal["LIMITED_PERMISSIONS", "FULL_PERMISSIONS"] | None = Field(None, alias="forcePermissionLevel", description="Overrides the permission level the Actor is forced to run with, regardless of the actorPermissionLevel setting."),
    tagged_builds: dict[str, _models.BuildTag] | None = Field(None, alias="taggedBuilds", description="An object for managing build tags using a patch strategy — existing tags not included are preserved. Assign a tag by providing a buildId, or remove a tag by setting its value to null."),
    is_enabled: bool | None = Field(None, alias="isEnabled", description="Whether the Actor Standby mode is enabled, allowing the Actor to remain warm and handle requests without cold-start delays."),
    desired_requests_per_actor_run: int | None = Field(None, alias="desiredRequestsPerActorRun", description="The target number of concurrent requests the Actor Standby should aim to handle per active Actor run."),
    max_requests_per_actor_run: int | None = Field(None, alias="maxRequestsPerActorRun", description="The maximum number of concurrent requests allowed per Actor run when operating in Standby mode."),
    idle_timeout_secs: int | None = Field(None, alias="idleTimeoutSecs", description="The number of seconds a Standby Actor run may remain idle without receiving requests before it is shut down."),
    disable_standby_fields_override: bool | None = Field(None, alias="disableStandbyFieldsOverride", description="When true, prevents automatic overriding of Standby-related fields by the platform."),
    should_pass_actor_input: bool | None = Field(None, alias="shouldPassActorInput", description="Whether the Actor's input schema should be forwarded to the Standby Actor run when it is initialized."),
    body: str | None = Field(None, description="The raw JSON request body payload containing the Actor settings to update, serialized as a string."),
    content_type: str | None = Field(None, alias="contentType", description="The MIME content type of the request body, which must be set to application/json."),
    is_deprecated: bool | None = Field(None, alias="isDeprecated", description="Whether the Actor is marked as deprecated, signaling to users that it should no longer be used."),
) -> dict[str, Any] | ToolResult:
    """Updates the settings and configuration of an existing Actor by applying only the properties provided in the JSON request body. Returns the full updated Actor object after the changes are applied."""

    # Construct request model with validation
    try:
        _request = _models.ActPutRequest(
            path=_models.ActPutRequestPath(actor_id=actor_id),
            body=_models.ActPutRequestBody(name=name, description=description, is_public=is_public, actor_permission_level=actor_permission_level, seo_title=seo_title, seo_description=seo_description, title=title, versions=versions, pricing_infos=pricing_infos, categories=categories, tagged_builds=tagged_builds, is_deprecated=is_deprecated,
                default_run_options=_models.ActPutRequestBodyDefaultRunOptions(restart_on_error=restart_on_error, build=default_run_options_build, timeout_secs=timeout_secs, memory_mbytes=default_run_options_memory_mbytes, max_items=max_items, force_permission_level=force_permission_level) if any(v is not None for v in [restart_on_error, default_run_options_build, timeout_secs, default_run_options_memory_mbytes, max_items, force_permission_level]) else None,
                actor_standby=_models.ActPutRequestBodyActorStandby(build=actor_standby_build, memory_mbytes=actor_standby_memory_mbytes, is_enabled=is_enabled, desired_requests_per_actor_run=desired_requests_per_actor_run, max_requests_per_actor_run=max_requests_per_actor_run, idle_timeout_secs=idle_timeout_secs, disable_standby_fields_override=disable_standby_fields_override, should_pass_actor_input=should_pass_actor_input) if any(v is not None for v in [actor_standby_build, actor_standby_memory_mbytes, is_enabled, desired_requests_per_actor_run, max_requests_per_actor_run, idle_timeout_secs, disable_standby_fields_override, should_pass_actor_input]) else None,
                example_run_input=_models.ActPutRequestBodyExampleRunInput(body=body, content_type=content_type) if any(v is not None for v in [body, content_type]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_actor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_actor")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_actor", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_actor",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors
@mcp.tool(
    title="Delete Actor",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_actor(actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor to delete, either as a standalone Actor ID or as a tilde-separated combination of the owner's username and Actor name.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes the specified Actor and all associated data. This action is irreversible."""

    # Construct request model with validation
    try:
        _request = _models.ActDeleteRequest(
            path=_models.ActDeleteRequestPath(actor_id=actor_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_actor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_actor")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_actor", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_actor",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor versions
@mcp.tool(
    title="List Actor Versions",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_actor_versions(actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor, either as a standalone Actor ID or as a tilde-separated combination of the owner's username and Actor name.")) -> dict[str, Any] | ToolResult:
    """Retrieves all versions of a specific Actor, returning a list of Version objects with basic information about each version."""

    # Construct request model with validation
    try:
        _request = _models.ActVersionsGetRequest(
            path=_models.ActVersionsGetRequestPath(actor_id=actor_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_actor_versions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/versions", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/versions"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_actor_versions")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_actor_versions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_actor_versions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor versions
@mcp.tool(
    title="Create Actor Version",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_actor_version(
    actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor, either as an Actor ID or a tilde-separated combination of the owner's username and Actor name."),
    version_number: str | None = Field(None, alias="versionNumber", description="The semantic version number to assign to this Actor version, following a major.minor format."),
    source_type: Literal["SOURCE_FILES", "GIT_REPO", "TARBALL", "GITHUB_GIST"] | None = Field(None, alias="sourceType", description="Defines where the Actor's source code is hosted; must be one of the supported source types. Each value requires its own additional properties: SOURCE_FILES uses sourceFiles, GIT_REPO uses gitRepoUrl, TARBALL uses tarballUrl, and GITHUB_GIST uses gitHubGistUrl."),
    env_vars: list[_models.EnvVar] | None = Field(None, alias="envVars", description="A list of environment variables to make available to the Actor at runtime and optionally during builds. Each item should specify the variable name and value."),
    apply_env_vars_to_build: bool | None = Field(None, alias="applyEnvVarsToBuild", description="When set to true, the defined environment variables are also injected into the build process, not just runtime execution."),
    build_tag: str | None = Field(None, alias="buildTag", description="A tag label applied to builds created from this version, used to reference or promote specific builds (e.g., marking a build as the latest stable release)."),
    source_files: list[_models.SourceCodeFile | _models.SourceCodeFolder] | None = Field(None, alias="sourceFiles", description="An array of source file objects representing the Actor's code when sourceType is SOURCE_FILES. Each item defines a file's name, content, and format."),
    git_repo_url: str | None = Field(None, alias="gitRepoUrl", description="The URL of the Git repository containing the Actor's source code; required when sourceType is GIT_REPO."),
    tarball_url: str | None = Field(None, alias="tarballUrl", description="The URL of a tarball archive containing the Actor's source code; required when sourceType is TARBALL."),
    git_hub_gist_url: str | None = Field(None, alias="gitHubGistUrl", description="The URL of a GitHub Gist containing the Actor's source code; required when sourceType is GITHUB_GIST."),
) -> dict[str, Any] | ToolResult:
    """Creates a new version of an Actor by specifying a version number and source type along with the corresponding source details. The source type determines which additional properties are required (e.g., a Git repository URL for GIT_REPO, a tarball URL for TARBALL)."""

    # Construct request model with validation
    try:
        _request = _models.ActVersionsPostRequest(
            path=_models.ActVersionsPostRequestPath(actor_id=actor_id),
            body=_models.ActVersionsPostRequestBody(version_number=version_number, source_type=source_type, env_vars=env_vars, apply_env_vars_to_build=apply_env_vars_to_build, build_tag=build_tag, source_files=source_files, git_repo_url=git_repo_url, tarball_url=tarball_url, git_hub_gist_url=git_hub_gist_url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_actor_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/versions", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/versions"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_actor_version")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_actor_version", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_actor_version",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor versions
@mcp.tool(
    title="Get Actor Version",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_actor_version(
    actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor, either as a standalone Actor ID or as a tilde-separated combination of the owner's username and Actor name."),
    version_number: str = Field(..., alias="versionNumber", description="The version number of the Actor to retrieve, following a major.minor versioning format."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific version of an Actor, including its configuration and metadata. Useful for inspecting the exact state of a particular Actor version."""

    # Construct request model with validation
    try:
        _request = _models.ActVersionGetRequest(
            path=_models.ActVersionGetRequestPath(actor_id=actor_id, version_number=version_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_actor_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/versions/{versionNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/versions/{versionNumber}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_actor_version")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_actor_version", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_actor_version",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor versions
@mcp.tool(
    title="Update Actor Version",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_actor_version(
    actor_id: str = Field(..., alias="actorId", description="The Actor's unique ID or a tilde-separated combination of the owner's username and Actor name identifying which Actor to update."),
    version_number: str = Field(..., alias="versionNumber", description="The version number of the Actor to update, following major.minor versioning format."),
    source_type: Literal["SOURCE_FILES", "GIT_REPO", "TARBALL", "GITHUB_GIST"] | None = Field(None, alias="sourceType", description="Defines where the Actor's source code originates, which determines which of the source URL fields are required."),
    env_vars: list[_models.EnvVar] | None = Field(None, alias="envVars", description="List of environment variables to make available to the Actor during execution and optionally during builds."),
    apply_env_vars_to_build: bool | None = Field(None, alias="applyEnvVarsToBuild", description="When set to true, the defined environment variables are also injected into the build process, not just runtime execution."),
    build_tag: str | None = Field(None, alias="buildTag", description="Tag label assigned to builds created from this version, used to reference the build when running the Actor."),
    source_files: list[_models.SourceCodeFile | _models.SourceCodeFolder] | None = Field(None, alias="sourceFiles", description="Array of source file objects representing the Actor's code when sourceType is SOURCE_FILES; each item defines a file path and its content."),
    git_repo_url: str | None = Field(None, alias="gitRepoUrl", description="The URL of the Git repository containing the Actor's source code; required when sourceType is GIT_REPO."),
    tarball_url: str | None = Field(None, alias="tarballUrl", description="The URL of the tarball archive containing the Actor's source code; required when sourceType is TARBALL."),
    git_hub_gist_url: str | None = Field(None, alias="gitHubGistUrl", description="The URL of the GitHub Gist containing the Actor's source code; required when sourceType is GITHUB_GIST."),
) -> dict[str, Any] | ToolResult:
    """Updates a specific version of an Actor with the provided fields, leaving unspecified properties unchanged. Send a JSON payload with only the fields you want to modify."""

    # Construct request model with validation
    try:
        _request = _models.ActVersionPutRequest(
            path=_models.ActVersionPutRequestPath(actor_id=actor_id, version_number=version_number),
            body=_models.ActVersionPutRequestBody(source_type=source_type, env_vars=env_vars, apply_env_vars_to_build=apply_env_vars_to_build, build_tag=build_tag, source_files=source_files, git_repo_url=git_repo_url, tarball_url=tarball_url, git_hub_gist_url=git_hub_gist_url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_actor_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/versions/{versionNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/versions/{versionNumber}"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_actor_version")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_actor_version", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_actor_version",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor versions
@mcp.tool(
    title="Delete Actor Version",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_actor_version(
    actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor, either as a standalone Actor ID or as a tilde-separated combination of the owner's username and Actor name."),
    version_number: str = Field(..., alias="versionNumber", description="The version number of the Actor to delete, following major.minor versioning format."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific version of an Actor's source code. This action is irreversible and removes the version along with its associated configuration."""

    # Construct request model with validation
    try:
        _request = _models.ActVersionDeleteRequest(
            path=_models.ActVersionDeleteRequestPath(actor_id=actor_id, version_number=version_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_actor_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/versions/{versionNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/versions/{versionNumber}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_actor_version")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_actor_version", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_actor_version",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor versions
@mcp.tool(
    title="List Actor Version Environment Variables",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_actor_version_env_vars(
    actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor, either as an Actor ID or a tilde-separated combination of the owner's username and Actor name."),
    version_number: str = Field(..., alias="versionNumber", description="The version number of the Actor whose environment variables should be retrieved, following major.minor versioning format."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all environment variables configured for a specific version of an Actor. Returns a list of environment variable objects, each containing the variable's key, value, and related metadata."""

    # Construct request model with validation
    try:
        _request = _models.ActVersionEnvVarsGetRequest(
            path=_models.ActVersionEnvVarsGetRequestPath(actor_id=actor_id, version_number=version_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_actor_version_env_vars: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/versions/{versionNumber}/env-vars", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/versions/{versionNumber}/env-vars"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_actor_version_env_vars")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_actor_version_env_vars", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_actor_version_env_vars",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor versions
@mcp.tool(
    title="Create Actor Version Environment Variable",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_actor_env_var(
    actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor, either as an Actor ID or a tilde-separated combination of the owner's username and Actor name."),
    version_number: str = Field(..., alias="versionNumber", description="The version number of the Actor to which the environment variable will be added."),
    name: str = Field(..., description="The name of the environment variable, typically uppercase with underscores following standard environment variable naming conventions."),
    value: str = Field(..., description="The value assigned to the environment variable."),
    is_secret: bool | None = Field(None, alias="isSecret", description="Indicates whether the environment variable should be treated as a secret, hiding its value from logs and the UI."),
) -> dict[str, Any] | ToolResult:
    """Creates a new environment variable for a specific version of an Actor. Requires a name and value, with an optional flag to mark the variable as secret."""

    # Construct request model with validation
    try:
        _request = _models.ActVersionEnvVarsPostRequest(
            path=_models.ActVersionEnvVarsPostRequestPath(actor_id=actor_id, version_number=version_number),
            body=_models.ActVersionEnvVarsPostRequestBody(name=name, value=value, is_secret=is_secret)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_actor_env_var: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/versions/{versionNumber}/env-vars", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/versions/{versionNumber}/env-vars"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_actor_env_var")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_actor_env_var", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_actor_env_var",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor versions
@mcp.tool(
    title="Get Actor Version Environment Variable",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_actor_env_var(
    actor_id: str = Field(..., alias="actorId", description="The unique ID of the Actor, or a tilde-separated combination of the owner's username and Actor name."),
    version_number: str = Field(..., alias="versionNumber", description="The version number of the Actor to retrieve the environment variable from, following major.minor versioning format."),
    env_var_name: str = Field(..., alias="envVarName", description="The exact name of the environment variable to retrieve, typically uppercase with underscores."),
) -> dict[str, Any] | ToolResult:
    """Retrieves details of a specific environment variable for a given Actor version. If the variable is marked as secret, its value will be omitted from the response."""

    # Construct request model with validation
    try:
        _request = _models.ActVersionEnvVarGetRequest(
            path=_models.ActVersionEnvVarGetRequestPath(actor_id=actor_id, version_number=version_number, env_var_name=env_var_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_actor_env_var: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/versions/{versionNumber}/env-vars/{envVarName}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/versions/{versionNumber}/env-vars/{envVarName}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_actor_env_var")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_actor_env_var", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_actor_env_var",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor versions
@mcp.tool(
    title="Update Actor Environment Variable",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_actor_env_var(
    actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor, either as an Actor ID or a tilde-separated combination of the owner's username and Actor name."),
    version_number: str = Field(..., alias="versionNumber", description="The version number of the Actor whose environment variable you want to update, in major.minor format."),
    env_var_name: str = Field(..., alias="envVarName", description="The exact name of the environment variable to update, as it appears in the Actor version's configuration."),
    name: str = Field(..., description="The updated name for the environment variable, typically uppercase with underscores following standard environment variable naming conventions."),
    value: str = Field(..., description="The updated value to assign to the environment variable."),
    is_secret: bool | None = Field(None, alias="isSecret", description="Indicates whether the environment variable should be treated as a secret. Secret variables are encrypted at rest and masked in logs."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing environment variable for a specific Actor version. Only the properties included in the request body will be modified; omitted properties retain their current values."""

    # Construct request model with validation
    try:
        _request = _models.ActVersionEnvVarPutRequest(
            path=_models.ActVersionEnvVarPutRequestPath(actor_id=actor_id, version_number=version_number, env_var_name=env_var_name),
            body=_models.ActVersionEnvVarPutRequestBody(name=name, value=value, is_secret=is_secret)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_actor_env_var: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/versions/{versionNumber}/env-vars/{envVarName}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/versions/{versionNumber}/env-vars/{envVarName}"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_actor_env_var")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_actor_env_var", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_actor_env_var",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor versions
@mcp.tool(
    title="Delete Actor Version Environment Variable",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_actor_version_env_var(
    actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor, either as an Actor ID or a tilde-separated combination of the owner's username and Actor name."),
    version_number: str = Field(..., alias="versionNumber", description="The version number of the Actor from which the environment variable will be deleted, following major.minor versioning format."),
    env_var_name: str = Field(..., alias="envVarName", description="The exact name of the environment variable to delete, typically uppercase with underscores as separators."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific environment variable from a given Actor version. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.ActVersionEnvVarDeleteRequest(
            path=_models.ActVersionEnvVarDeleteRequestPath(actor_id=actor_id, version_number=version_number, env_var_name=env_var_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_actor_version_env_var: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/versions/{versionNumber}/env-vars/{envVarName}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/versions/{versionNumber}/env-vars/{envVarName}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_actor_version_env_var")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_actor_version_env_var", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_actor_version_env_var",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Webhook collection
@mcp.tool(
    title="List Actor Webhooks",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_actor_webhooks(
    actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor, either as a standalone Actor ID or as a tilde-separated combination of the owner's username and Actor name."),
    offset: float | None = Field(None, description="Number of webhooks to skip from the beginning of the result set, used for paginating through records. Defaults to 0."),
    limit: float | None = Field(None, description="Maximum number of webhooks to return in a single response. Accepts values between 1 and 1000, defaulting to 1000."),
    desc: bool | None = Field(None, description="When set to true, reverses the sort order so that the most recently created webhooks appear first instead of last."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of webhooks associated with a specific Actor, returning basic information about each webhook. Results are sorted by creation date ascending by default, with a maximum of 1000 records per request."""

    # Construct request model with validation
    try:
        _request = _models.ActWebhooksGetRequest(
            path=_models.ActWebhooksGetRequestPath(actor_id=actor_id),
            query=_models.ActWebhooksGetRequestQuery(offset=offset, limit=limit, desc=desc)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_actor_webhooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/webhooks", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/webhooks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_actor_webhooks")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_actor_webhooks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_actor_webhooks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor builds
@mcp.tool(
    title="List Actor Builds",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_actor_builds(
    actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor, either as a plain Actor ID or in tilde-separated format combining the owner's username and Actor name."),
    offset: float | None = Field(None, description="Number of build records to skip from the beginning of the result set, used for paginating through results. Defaults to 0."),
    limit: float | None = Field(None, description="Maximum number of build records to return in a single response. Accepts values up to 1000, which is also the default."),
    desc: bool | None = Field(None, description="When set to true, sorts the returned builds by their start time in descending order (newest first). Defaults to ascending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of builds for a specific Actor, with each record containing basic build information. Results are sorted by start time in ascending order by default, supporting incremental fetching as new builds are created."""

    # Construct request model with validation
    try:
        _request = _models.ActBuildsGetRequest(
            path=_models.ActBuildsGetRequestPath(actor_id=actor_id),
            query=_models.ActBuildsGetRequestQuery(offset=offset, limit=limit, desc=desc)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_actor_builds: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/builds", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/builds"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_actor_builds")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_actor_builds", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_actor_builds",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor builds
@mcp.tool(
    title="Build Actor",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def build_actor(
    actor_id: str = Field(..., alias="actorId", description="The unique ID of the Actor, or a tilde-separated string combining the owner's username and Actor name."),
    version: str = Field(..., description="The Actor version number to build, corresponding to a version defined in the Actor's configuration."),
    use_cache: bool | None = Field(None, alias="useCache", description="When enabled, the build system reuses cached layers to speed up the build process; cache is disabled by default."),
    beta_packages: bool | None = Field(None, alias="betaPackages", description="When enabled, the Actor is built using beta versions of Apify NPM packages instead of the default latest stable versions."),
    tag: str | None = Field(None, description="A label applied to the build upon successful completion; if omitted, the tag defaults to the value set in the Actor version's buildTag property."),
    wait_for_finish: float | None = Field(None, alias="waitForFinish", description="Number of seconds the server will wait for the build to complete before returning a response; must be between 0 and 60, where 0 returns immediately with a transitional status and higher values may return a terminal status if the build finishes in time."),
) -> dict[str, Any] | ToolResult:
    """Triggers a new build for a specified Actor version, compiling its source code and dependencies into a runnable image. Returns the resulting build object, which may reflect a terminal or transitional status depending on wait time."""

    # Construct request model with validation
    try:
        _request = _models.ActBuildsPostRequest(
            path=_models.ActBuildsPostRequestPath(actor_id=actor_id),
            query=_models.ActBuildsPostRequestQuery(version=version, use_cache=use_cache, beta_packages=beta_packages, tag=tag, wait_for_finish=wait_for_finish)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for build_actor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/builds", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/builds"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("build_actor")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("build_actor", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="build_actor",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor builds
@mcp.tool(
    title="Get Default Actor Build",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_default_actor_build(
    actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor, either as a standalone Actor ID or as a tilde-separated combination of the owner's username and Actor name."),
    wait_for_finish: float | None = Field(None, alias="waitForFinish", description="Maximum number of seconds the server will wait for the build to finish before returning; if the build completes within this window the response will reflect a terminal status (e.g. SUCCEEDED), otherwise a transitional status (e.g. RUNNING) is returned. Accepts values from 0 (default, no wait) up to 60."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the default build for a specified Actor, optionally waiting synchronously for the build to reach a terminal state. No authentication token is required, though unauthenticated requests will have certain usage cost fields omitted from the response."""

    # Construct request model with validation
    try:
        _request = _models.ActBuildDefaultGetRequest(
            path=_models.ActBuildDefaultGetRequestPath(actor_id=actor_id),
            query=_models.ActBuildDefaultGetRequestQuery(wait_for_finish=wait_for_finish)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_default_actor_build: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/builds/default", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/builds/default"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_default_actor_build")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_default_actor_build", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_default_actor_build",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor runs
@mcp.tool(
    title="List Actor Runs",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_actor_runs_by_actor(
    actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor, either as an Actor ID or a tilde-separated combination of the owner's username and Actor name."),
    offset: float | None = Field(None, description="Number of runs to skip from the beginning of the result set, used for paginating through results."),
    limit: float | None = Field(None, description="Maximum number of runs to return in a single response; cannot exceed 1000."),
    desc: bool | None = Field(None, description="When set to true, sorts runs by their start time in descending order (newest first); defaults to ascending order."),
    status: str | None = Field(None, description="Filters results to only include runs matching the specified status or comma-separated list of statuses (e.g., SUCCEEDED, FAILED, RUNNING)."),
    started_after: str | None = Field(None, alias="startedAfter", description="Filters results to only include runs that started at or after this point in time, specified as an ISO 8601 datetime string in UTC."),
    started_before: str | None = Field(None, alias="startedBefore", description="Filters results to only include runs that started at or before this point in time, specified as an ISO 8601 datetime string in UTC."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of runs for a specific Actor, with each item containing basic run metadata. Supports filtering by status and start time, and sorting in ascending or descending order."""

    # Construct request model with validation
    try:
        _request = _models.ActRunsGetRequest(
            path=_models.ActRunsGetRequestPath(actor_id=actor_id),
            query=_models.ActRunsGetRequestQuery(offset=offset, limit=limit, desc=desc, status=status, started_after=started_after, started_before=started_before)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_actor_runs_by_actor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/runs", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/runs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_actor_runs_by_actor")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_actor_runs_by_actor", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_actor_runs_by_actor",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor runs
@mcp.tool(
    title="Run Actor",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def run_actor(
    actor_id: str = Field(..., alias="actorId", description="The unique ID of the Actor, or a tilde-separated combination of the owner's username and Actor name."),
    timeout: float | None = Field(None, description="Maximum duration the run is allowed to execute before being stopped, in seconds. Overrides the timeout configured in the Actor's settings."),
    memory: float | None = Field(None, description="Maximum RAM allocated to the run, in megabytes. Must be a power of 2 and at least 128 MB. Overrides the memory limit configured in the Actor's settings."),
    max_items: float | None = Field(None, alias="maxItems", description="Maximum number of dataset items that will be billed for pay-per-result Actors. Does not cap the number of items returned — only limits charges. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable."),
    max_total_charge_usd: float | None = Field(None, alias="maxTotalChargeUsd", description="Maximum total cost in USD allowed for the run, intended for pay-per-event Actors to cap charges. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable."),
    restart_on_error: bool | None = Field(None, alias="restartOnError", description="Whether the run should automatically restart if it encounters a failure."),
    build: str | None = Field(None, description="The specific Actor build to execute, specified as either a build tag or a build number. Defaults to the build defined in the Actor's configuration, typically the latest tag."),
    wait_for_finish: float | None = Field(None, alias="waitForFinish", description="Number of seconds the server will wait for the run to finish before returning a response, between 0 and 60. If the run completes within this window, the response will reflect a terminal status such as SUCCEEDED; otherwise it will reflect a transitional status such as RUNNING."),
    force_permission_level: Literal["LIMITED_PERMISSIONS", "FULL_PERMISSIONS"] | None = Field(None, alias="forcePermissionLevel", description="Overrides the Actor's default permission level for this run only, useful for testing restricted or elevated access scenarios without permanently changing the Actor's configuration."),
    webhook_event_types: list[str] | None = Field(None, description="List of event types to trigger the webhook. Common values: 'ACTOR.RUN.SUCCEEDED', 'ACTOR.RUN.FAILED', 'ACTOR.RUN.ABORTED', 'ACTOR.RUN.TIMED_OUT'."),
    webhook_request_url: str | None = Field(None, description="URL that will receive the webhook POST request when the event fires."),
    body: dict[str, Any] | None = Field(None, description="The input payload passed to the Actor as INPUT, typically a JSON object. The Content-Type header of the request is forwarded alongside this body."),
) -> dict[str, Any] | ToolResult:
    """Starts an Actor run asynchronously and immediately returns a Run object without waiting for completion. Pass input data as the request body and use the returned run ID or defaultDatasetId to retrieve results later."""

    # Call helper functions
    webhooks = build_webhooks(webhook_event_types, webhook_request_url)

    # Construct request model with validation
    try:
        _request = _models.ActRunsPostRequest(
            path=_models.ActRunsPostRequestPath(actor_id=actor_id),
            query=_models.ActRunsPostRequestQuery(timeout=timeout, memory=memory, max_items=max_items, max_total_charge_usd=max_total_charge_usd, restart_on_error=restart_on_error, build=build, wait_for_finish=wait_for_finish, force_permission_level=force_permission_level, webhooks=webhooks),
            body=_models.ActRunsPostRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for run_actor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/runs", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/runs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("run_actor")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("run_actor", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="run_actor",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor runs
@mcp.tool(
    title="Run Actor Synchronously",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def run_actor_sync_no_input(
    actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor to run, either as an Actor ID or a tilde-separated combination of the owner's username and Actor name."),
    output_record_key: str | None = Field(None, alias="outputRecordKey", description="The key of the record from the run's default key-value store to return in the response. Defaults to OUTPUT if not specified."),
    timeout: float | None = Field(None, description="Maximum duration the run is allowed to execute, in seconds. If omitted, the timeout defined in the Actor's saved configuration is used."),
    memory: float | None = Field(None, description="Memory allocated for the run in megabytes; must be a power of 2 with a minimum of 128. If omitted, the memory limit from the Actor's saved configuration is used."),
    max_items: float | None = Field(None, alias="maxItems", description="Maximum number of dataset items that will be charged for pay-per-result Actors; does not cap the actual items returned, only the billing ceiling. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable."),
    max_total_charge_usd: float | None = Field(None, alias="maxTotalChargeUsd", description="Maximum total cost in USD allowed for the run, useful for capping charges on pay-per-event Actors. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable."),
    restart_on_error: bool | None = Field(None, alias="restartOnError", description="When set to true, the run will automatically restart if it encounters a failure. Defaults to false if not specified."),
    build: str | None = Field(None, description="Specifies which build of the Actor to execute, provided as either a build tag or a build number. Defaults to the build defined in the Actor's configuration, typically the latest tag."),
    webhook_event_types: list[str] | None = Field(None, description="List of event types to trigger the webhook. Common values: 'ACTOR.RUN.SUCCEEDED', 'ACTOR.RUN.FAILED', 'ACTOR.RUN.ABORTED', 'ACTOR.RUN.TIMED_OUT'."),
    webhook_request_url: str | None = Field(None, description="URL that will receive the webhook POST request when the event fires."),
) -> dict[str, Any] | ToolResult:
    """Runs a specific Actor synchronously without input and returns its output directly in the response. The run must complete within 300 seconds; if it exceeds this limit or the connection breaks, a timeout error is returned."""

    # Call helper functions
    webhooks = build_webhooks(webhook_event_types, webhook_request_url)

    # Construct request model with validation
    try:
        _request = _models.ActRunSyncGetRequest(
            path=_models.ActRunSyncGetRequestPath(actor_id=actor_id),
            query=_models.ActRunSyncGetRequestQuery(output_record_key=output_record_key, timeout=timeout, memory=memory, max_items=max_items, max_total_charge_usd=max_total_charge_usd, restart_on_error=restart_on_error, build=build, webhooks=webhooks)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for run_actor_sync_no_input: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/run-sync", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/run-sync"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("run_actor_sync_no_input")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("run_actor_sync_no_input", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="run_actor_sync_no_input",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor runs
@mcp.tool(
    title="Run Actor Synchronously",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def run_actor_sync(
    actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor to run, either as an Actor ID or a tilde-separated owner username and Actor name combination."),
    output_record_key: str | None = Field(None, alias="outputRecordKey", description="The key of the record from the run's default key-value store to return in the response. Defaults to OUTPUT if not specified."),
    timeout: float | None = Field(None, description="Maximum duration the Actor run is allowed to execute, in seconds. Overrides the timeout defined in the Actor's configuration."),
    memory: float | None = Field(None, description="Memory allocated for the Actor run, in megabytes. Must be a power of 2 with a minimum of 128 MB. Overrides the memory limit defined in the Actor's configuration."),
    max_items: float | None = Field(None, alias="maxItems", description="Maximum number of dataset items that will be charged for pay-per-result Actors. Does not cap the number of items returned, only the number billed. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable."),
    max_total_charge_usd: float | None = Field(None, alias="maxTotalChargeUsd", description="Maximum total cost in USD allowed for the run, useful for limiting charges on pay-per-event Actors. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable."),
    restart_on_error: bool | None = Field(None, alias="restartOnError", description="Whether the Actor run should automatically restart if it encounters a failure."),
    build: str | None = Field(None, description="The specific Actor build to execute, specified as either a build tag or build number. Defaults to the build defined in the Actor's configuration, typically the latest tag."),
    webhook_event_types: list[str] | None = Field(None, description="List of event types to trigger the webhook. Common values: 'ACTOR.RUN.SUCCEEDED', 'ACTOR.RUN.FAILED', 'ACTOR.RUN.ABORTED', 'ACTOR.RUN.TIMED_OUT'."),
    webhook_request_url: str | None = Field(None, description="URL that will receive the webhook POST request when the event fires."),
    body: dict[str, Any] | None = Field(None, description="The input payload passed to the Actor as its INPUT record. The Content-Type header of the request is forwarded alongside this body, typically as application/json."),
) -> dict[str, Any] | ToolResult:
    """Runs a specific Actor synchronously, passing the request body as INPUT, and returns the Actor's OUTPUT from its default key-value store. If the Actor run exceeds 300 seconds, the response will return a 408 timeout status."""

    # Call helper functions
    webhooks = build_webhooks(webhook_event_types, webhook_request_url)

    # Construct request model with validation
    try:
        _request = _models.ActRunSyncPostRequest(
            path=_models.ActRunSyncPostRequestPath(actor_id=actor_id),
            query=_models.ActRunSyncPostRequestQuery(output_record_key=output_record_key, timeout=timeout, memory=memory, max_items=max_items, max_total_charge_usd=max_total_charge_usd, restart_on_error=restart_on_error, build=build, webhooks=webhooks),
            body=_models.ActRunSyncPostRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for run_actor_sync: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/run-sync", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/run-sync"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("run_actor_sync")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("run_actor_sync", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="run_actor_sync",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor runs
@mcp.tool(
    title="Run Actor Synchronously and Get Dataset Items",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def run_actor_sync_get_dataset_items(
    actor_id: str = Field(..., alias="actorId", description="The unique identifier of the Actor to run, either as an internal Actor ID or as a tilde-separated combination of the owner's username and Actor name."),
    timeout: float | None = Field(None, description="Maximum duration the Actor run is allowed to execute before being forcibly stopped, in seconds. Overrides the timeout defined in the Actor's saved configuration."),
    memory: float | None = Field(None, description="Maximum RAM the Actor run may use, in megabytes. Must be a power of 2 and at least 128 MB. Overrides the memory limit defined in the Actor's saved configuration."),
    max_items: float | None = Field(None, alias="maxItems", description="Maximum number of dataset items that will be billed for pay-per-result Actors. Does not cap the number of items returned — only limits charges. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable."),
    max_total_charge_usd: float | None = Field(None, alias="maxTotalChargeUsd", description="Maximum total cost in USD that may be charged for this run, intended for pay-per-event Actors. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable."),
    restart_on_error: bool | None = Field(None, alias="restartOnError", description="When enabled, the Actor run will automatically restart if it encounters a failure, rather than terminating in an error state."),
    build: str | None = Field(None, description="Specifies which build of the Actor to execute, either by build tag or build number. Overrides the build defined in the Actor's saved configuration, which defaults to the latest tag."),
    format_: str | None = Field(None, alias="format", description="Output format for the returned dataset items. Supported values are json, jsonl, csv, html, xlsx, xml, and rss."),
    offset: float | None = Field(None, description="Number of dataset items to skip from the beginning of the result set before returning data. Useful for pagination."),
    limit: float | None = Field(None, description="Maximum number of dataset items to include in the response. When omitted, all available items are returned."),
    fields: str | None = Field(None, description="Comma-separated list of field names to include in each returned item, excluding all other fields. Output fields are ordered to match the order specified in this list."),
    omit: str | None = Field(None, description="Comma-separated list of field names to exclude from each returned item. All other fields are retained."),
    unwind: str | None = Field(None, description="Comma-separated list of fields to unwind, processed in the specified order. Array fields produce one record per element merged with the parent; object fields are merged directly into the parent. Items with missing or non-unwindable fields are preserved as-is. Unwound items are not affected by the desc parameter."),
    flatten: str | None = Field(None, description="Comma-separated list of fields whose nested object values should be flattened into dot-notation keys on the parent object. The original nested object is replaced by its flattened representation."),
    desc: bool | None = Field(None, description="When set to true, reverses the order of returned items so the most recently stored items appear first. By default, items are returned in insertion order."),
    attachment: bool | None = Field(None, description="When set to true, adds a Content-Disposition: attachment header to the response, prompting browsers to download the result as a file rather than render it inline."),
    delimiter: str | None = Field(None, description="Single character used as the field delimiter in CSV output. Only applies when format is csv. Special characters should be URL-encoded (e.g., %09 for tab, %3B for semicolon). Defaults to a comma."),
    bom: bool | None = Field(None, description="Controls whether a UTF-8 Byte Order Mark (BOM) is prepended to the response. By default, BOM is included for CSV and omitted for json, jsonl, xml, html, and rss. Set to true to force inclusion or false to force omission."),
    xml_root: str | None = Field(None, alias="xmlRoot", description="Overrides the name of the root XML element in xml-formatted output. Only applies when format is xml."),
    xml_row: str | None = Field(None, alias="xmlRow", description="Overrides the name of the element wrapping each individual record in xml-formatted output. Only applies when format is xml."),
    skip_header_row: bool | None = Field(None, alias="skipHeaderRow", description="When set to true, omits the header row from csv-formatted output. Only applies when format is csv."),
    skip_hidden: bool | None = Field(None, alias="skipHidden", description="When set to true, excludes fields whose names begin with the # character from the output."),
    skip_empty: bool | None = Field(None, alias="skipEmpty", description="When set to true, items with no fields or all-null values are excluded from the output. Note that the total number of returned items may be less than the specified limit when this is enabled."),
    simplified: bool | None = Field(None, description="When set to true, applies preset query parameters fields=url,pageFunctionResult,errorInfo and unwind=pageFunctionResult to emulate the simplified output format of the legacy Apify Crawler. Not recommended for new integrations."),
    skip_failed_pages: bool | None = Field(None, alias="skipFailedPages", description="When set to true, excludes all items that contain an errorInfo property from the output. Provided for compatibility with legacy Apify Crawler API v1 behavior. Not recommended for new integrations."),
    webhook_event_types: list[str] | None = Field(None, description="List of event types to trigger the webhook. Common values: 'ACTOR.RUN.SUCCEEDED', 'ACTOR.RUN.FAILED', 'ACTOR.RUN.ABORTED', 'ACTOR.RUN.TIMED_OUT'."),
    webhook_request_url: str | None = Field(None, description="URL that will receive the webhook POST request when the event fires."),
) -> dict[str, Any] | ToolResult:
    """Runs a specific Actor synchronously without input and returns its dataset items directly in the response. The Actor must complete within 300 seconds; if it exceeds this limit or the connection breaks, a timeout error is returned."""

    # Call helper functions
    webhooks = build_webhooks(webhook_event_types, webhook_request_url)

    # Construct request model with validation
    try:
        _request = _models.ActRunSyncGetDatasetItemsGetRequest(
            path=_models.ActRunSyncGetDatasetItemsGetRequestPath(actor_id=actor_id),
            query=_models.ActRunSyncGetDatasetItemsGetRequestQuery(timeout=timeout, memory=memory, max_items=max_items, max_total_charge_usd=max_total_charge_usd, restart_on_error=restart_on_error, build=build, format_=format_, offset=offset, limit=limit, fields=fields, omit=omit, unwind=unwind, flatten=flatten, desc=desc, attachment=attachment, delimiter=delimiter, bom=bom, xml_root=xml_root, xml_row=xml_row, skip_header_row=skip_header_row, skip_hidden=skip_hidden, skip_empty=skip_empty, simplified=simplified, skip_failed_pages=skip_failed_pages, webhooks=webhooks)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for run_actor_sync_get_dataset_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/run-sync-get-dataset-items", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/run-sync-get-dataset-items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("run_actor_sync_get_dataset_items")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("run_actor_sync_get_dataset_items", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="run_actor_sync_get_dataset_items",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor runs
@mcp.tool(
    title="Run Actor Synchronously and Get Dataset Items",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def run_actor_sync_get_dataset_items_with_input(
    actor_id: str = Field(..., alias="actorId", description="The unique ID of the Actor, or a tilde-separated combination of the owner's username and Actor name."),
    timeout: float | None = Field(None, description="Maximum duration the Actor run is allowed to execute before being terminated, in seconds. Defaults to the timeout configured on the Actor itself."),
    memory: float | None = Field(None, description="Memory allocated to the Actor run in megabytes. Must be a power of 2 with a minimum of 128 MB. Defaults to the memory limit configured on the Actor."),
    max_items: float | None = Field(None, alias="maxItems", description="Maximum number of dataset items that will be charged for pay-per-result Actors. Does not cap the number of items returned — only limits billing. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable."),
    max_total_charge_usd: float | None = Field(None, alias="maxTotalChargeUsd", description="Maximum total cost in USD allowed for the run, intended for pay-per-event Actors to cap charges. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable."),
    restart_on_error: bool | None = Field(None, alias="restartOnError", description="When set to true, the Actor run will automatically restart if it encounters a failure."),
    build: str | None = Field(None, description="The specific Actor build to execute, specified as either a build tag or a build number. Defaults to the build configured on the Actor, typically the latest tag."),
    format_: str | None = Field(None, alias="format", description="Output format for the returned dataset items. Accepted values are json, jsonl, csv, html, xlsx, xml, and rss. Defaults to json."),
    offset: float | None = Field(None, description="Number of dataset items to skip from the beginning of the result set before returning data. Defaults to 0."),
    limit: float | None = Field(None, description="Maximum number of dataset items to include in the response. When omitted, all available items are returned."),
    fields: str | None = Field(None, description="Comma-separated list of field names to include in each output record, excluding all other fields. Output fields are ordered according to the order specified in this list."),
    omit: str | None = Field(None, description="Comma-separated list of field names to exclude from each output record. All other fields are retained."),
    unwind: str | None = Field(None, description="Comma-separated list of fields to unwind, processed in the specified order. Array fields produce one record per element merged with the parent; object fields are merged directly into the parent. Items with missing or non-unwindable fields are preserved as-is."),
    flatten: str | None = Field(None, description="Comma-separated list of fields whose nested object values should be flattened into dot-notation keys on the parent object. The original nested object is replaced by its flattened representation."),
    desc: bool | None = Field(None, description="When set to true, reverses the order of returned items. By default, items are returned in the order they were stored."),
    delimiter: str | None = Field(None, description="Single character used as the field delimiter in CSV output; only applicable when format is csv. URL-encode special characters as needed. Defaults to a comma."),
    xml_root: str | None = Field(None, alias="xmlRoot", description="Overrides the name of the root XML element in xml-formatted output. Defaults to items."),
    xml_row: str | None = Field(None, alias="xmlRow", description="Overrides the name of the element wrapping each individual record in xml-formatted output. Defaults to item."),
    skip_header_row: bool | None = Field(None, alias="skipHeaderRow", description="When set to true, omits the header row from csv-formatted output."),
    skip_hidden: bool | None = Field(None, alias="skipHidden", description="When set to true, fields whose names begin with the # character are excluded from the output."),
    skip_empty: bool | None = Field(None, alias="skipEmpty", description="When set to true, items with no fields or all-null values are excluded from the output. Note that the total number of returned items may be less than the specified limit when this option is active."),
    webhook_event_types: list[str] | None = Field(None, description="List of event types to trigger the webhook. Common values: 'ACTOR.RUN.SUCCEEDED', 'ACTOR.RUN.FAILED', 'ACTOR.RUN.ABORTED', 'ACTOR.RUN.TIMED_OUT'."),
    webhook_request_url: str | None = Field(None, description="URL that will receive the webhook POST request when the event fires."),
    body: dict[str, Any] | None = Field(None, description="The input payload passed to the Actor as its INPUT, with the request's Content-Type header forwarded alongside it. Typically a JSON object."),
) -> dict[str, Any] | ToolResult:
    """Runs a specific Actor synchronously with the provided input payload and returns the resulting dataset items directly in the response. Supports the same output formatting and filtering options as the Get Dataset Items endpoint; times out with HTTP 408 if the Actor run exceeds 300 seconds."""

    # Call helper functions
    webhooks = build_webhooks(webhook_event_types, webhook_request_url)

    # Construct request model with validation
    try:
        _request = _models.ActRunSyncGetDatasetItemsPostRequest(
            path=_models.ActRunSyncGetDatasetItemsPostRequestPath(actor_id=actor_id),
            query=_models.ActRunSyncGetDatasetItemsPostRequestQuery(timeout=timeout, memory=memory, max_items=max_items, max_total_charge_usd=max_total_charge_usd, restart_on_error=restart_on_error, build=build, format_=format_, offset=offset, limit=limit, fields=fields, omit=omit, unwind=unwind, flatten=flatten, desc=desc, delimiter=delimiter, xml_root=xml_root, xml_row=xml_row, skip_header_row=skip_header_row, skip_hidden=skip_hidden, skip_empty=skip_empty, webhooks=webhooks),
            body=_models.ActRunSyncGetDatasetItemsPostRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for run_actor_sync_get_dataset_items_with_input: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/run-sync-get-dataset-items", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/run-sync-get-dataset-items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("run_actor_sync_get_dataset_items_with_input")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("run_actor_sync_get_dataset_items_with_input", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="run_actor_sync_get_dataset_items_with_input",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor runs
@mcp.tool(
    title="Resurrect Actor Run",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def resurrect_actor_run(
    actor_id: str = Field(..., alias="actorId", description="The Actor's unique ID or a tilde-separated combination of the owner's username and Actor name identifying which Actor the run belongs to."),
    run_id: str = Field(..., alias="runId", description="The unique ID of the finished Actor run to resurrect."),
    build: str | None = Field(None, description="The Actor build to use for the resurrected run, specified as a build tag or build number. Defaults to the exact build version used when the run originally started, not the current resolution of any tag."),
    timeout: float | None = Field(None, description="Maximum duration the resurrected run is allowed to execute, in seconds. Defaults to the timeout value from the original run."),
    memory: float | None = Field(None, description="Memory allocated to the resurrected run in megabytes; must be a power of 2 and at least 128 MB. Defaults to the memory limit from the original run."),
    restart_on_error: bool | None = Field(None, alias="restartOnError", description="Whether the resurrected run should automatically restart if it encounters a failure. Defaults to the same setting used in the original run."),
) -> dict[str, Any] | ToolResult:
    """Restarts a finished Actor run (with status FINISHED, FAILED, ABORTED, or TIMED-OUT), resuming execution with the same storages and updating its status back to RUNNING. Optionally override the build, timeout, memory, or error-restart behavior from the original run."""

    # Construct request model with validation
    try:
        _request = _models.ActRunResurrectPostRequest(
            path=_models.ActRunResurrectPostRequestPath(actor_id=actor_id, run_id=run_id),
            query=_models.ActRunResurrectPostRequestQuery(build=build, timeout=timeout, memory=memory, restart_on_error=restart_on_error)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for resurrect_actor_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/runs/{runId}/resurrect", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/runs/{runId}/resurrect"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("resurrect_actor_run")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("resurrect_actor_run", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="resurrect_actor_run",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actors/Actor runs
@mcp.tool(
    title="Get Last Actor Run",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_last_actor_run(
    actor_id: str = Field(..., alias="actorId", description="The unique ID of the Actor, or a tilde-separated combination of the owner's username and Actor name."),
    status: str | None = Field(None, description="Filters the result to only return the last run matching the specified status, ensuring you retrieve a run in a particular state (e.g. only succeeded runs)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the most recent run of a specified Actor, with optional filtering by run status. Also serves as the base path for accessing the last run's default storages (log, key-value store, dataset, and request queue) via sub-endpoints."""

    # Construct request model with validation
    try:
        _request = _models.ActRunsLastGetRequest(
            path=_models.ActRunsLastGetRequestPath(actor_id=actor_id),
            query=_models.ActRunsLastGetRequestQuery(status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_last_actor_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/acts/{actorId}/runs/last", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/acts/{actorId}/runs/last"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_last_actor_run")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_last_actor_run", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_last_actor_run",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor tasks
@mcp.tool(
    title="List Tasks",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_tasks(
    offset: float | None = Field(None, description="Number of tasks to skip from the beginning of the result set, used for paginating through large lists."),
    limit: float | None = Field(None, description="Maximum number of tasks to return in a single response, up to a maximum of 1000."),
    desc: bool | None = Field(None, description="When set to true, sorts tasks by creation date in descending order (newest first); defaults to ascending order (oldest first)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all actor tasks created or used by the authenticated user. Results are sorted by creation date and capped at 1000 records per request."""

    # Construct request model with validation
    try:
        _request = _models.ActorTasksGetRequest(
            query=_models.ActorTasksGetRequestQuery(offset=offset, limit=limit, desc=desc)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/actor-tasks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tasks")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

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

# Tags: Actor tasks
@mcp.tool(
    title="Create Task",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_task(body: _models.ActorTasksPostBody | None = Field(None, description="JSON object defining the new task's configuration, including the actor to run, the task name, and execution options such as build version, timeout, and memory allocation.")) -> dict[str, Any] | ToolResult:
    """Creates a new actor task with the specified configuration, including the target actor, build version, timeout, and memory settings. Returns the full task object upon successful creation."""

    # Construct request model with validation
    try:
        _request = _models.ActorTasksPostRequest(
            body=_models.ActorTasksPostRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/actor-tasks"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_task")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_task", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_task",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor tasks
@mcp.tool(
    title="Get Task",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_task(actor_task_id: str = Field(..., alias="actorTaskId", description="The unique identifier of the task to retrieve, either as a standalone task ID or as a tilde-separated combination of the owner's username and the task's name.")) -> dict[str, Any] | ToolResult:
    """Retrieve full details of a specific actor task, including its configuration, settings, and metadata. Use this to inspect an existing task before running or modifying it."""

    # Construct request model with validation
    try:
        _request = _models.ActorTaskGetRequest(
            path=_models.ActorTaskGetRequestPath(actor_task_id=actor_task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-tasks/{actorTaskId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-tasks/{actorTaskId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_task")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

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

# Tags: Actor tasks
@mcp.tool(
    title="Update Task",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_task(
    actor_task_id: str = Field(..., alias="actorTaskId", description="The unique identifier of the task to update, either as a task ID or a tilde-separated combination of the owner's username and task name."),
    name: str | None = Field(None, description="The URL-friendly name of the task, used to identify it within the owner's account."),
    options_build: str | None = Field(None, alias="optionsBuild", description="The Actor build tag or version to use when running the task, such as a version tag or 'latest'."),
    actor_standby_build: str | None = Field(None, alias="actorStandbyBuild", description="The Actor build tag or version to use when the task is running in Standby mode."),
    timeout_secs: int | None = Field(None, alias="timeoutSecs", description="Maximum duration in seconds the task run is allowed to execute before it is forcefully stopped."),
    options_memory_mbytes: int | None = Field(None, alias="optionsMemoryMbytes", description="Amount of memory in megabytes allocated to each task run; must be a power of 2."),
    actor_standby_memory_mbytes: int | None = Field(None, alias="actorStandbyMemoryMbytes", description="Amount of memory in megabytes allocated to each task run when operating in Standby mode; must be a power of 2."),
    restart_on_error: bool | None = Field(None, alias="restartOnError", description="Whether the task run should automatically restart if it encounters an error during execution."),
    max_items: int | None = Field(None, alias="maxItems", description="Maximum number of output dataset items the task is allowed to produce before the run is stopped."),
    input_: dict[str, Any] | None = Field(None, alias="input", description="The user-defined JSON input configuration passed to the Actor when the task is executed; structure depends on the specific Actor's input schema."),
    title: str | None = Field(None, description="A human-readable display title for the task, distinct from its URL-friendly name."),
    is_enabled: bool | None = Field(None, alias="isEnabled", description="Whether the task is enabled and available to be run; disabled tasks cannot be triggered."),
    desired_requests_per_actor_run: int | None = Field(None, alias="desiredRequestsPerActorRun", description="The target number of requests to process per Actor run when the task is operating in Standby mode."),
    max_requests_per_actor_run: int | None = Field(None, alias="maxRequestsPerActorRun", description="The upper limit on the number of requests that can be processed per Actor run in Standby mode."),
    idle_timeout_secs: int | None = Field(None, alias="idleTimeoutSecs", description="Duration in seconds the Standby Actor is allowed to remain idle before it is considered inactive and shut down."),
    disable_standby_fields_override: bool | None = Field(None, alias="disableStandbyFieldsOverride", description="When true, prevents task-level Standby field values from overriding the Actor's default Standby configuration."),
    should_pass_actor_input: bool | None = Field(None, alias="shouldPassActorInput", description="When true, the Actor's own input is passed through to the task run in addition to the task's configured input."),
) -> dict[str, Any] | ToolResult:
    """Update the settings, input configuration, and runtime options of an existing Actor task. Only properties included in the request body are modified; omitted properties retain their current values."""

    # Construct request model with validation
    try:
        _request = _models.ActorTaskPutRequest(
            path=_models.ActorTaskPutRequestPath(actor_task_id=actor_task_id),
            body=_models.ActorTaskPutRequestBody(name=name, input_=input_, title=title,
                options=_models.ActorTaskPutRequestBodyOptions(build=options_build, timeout_secs=timeout_secs, memory_mbytes=options_memory_mbytes, restart_on_error=restart_on_error, max_items=max_items) if any(v is not None for v in [options_build, timeout_secs, options_memory_mbytes, restart_on_error, max_items]) else None,
                actor_standby=_models.ActorTaskPutRequestBodyActorStandby(build=actor_standby_build, memory_mbytes=actor_standby_memory_mbytes, is_enabled=is_enabled, desired_requests_per_actor_run=desired_requests_per_actor_run, max_requests_per_actor_run=max_requests_per_actor_run, idle_timeout_secs=idle_timeout_secs, disable_standby_fields_override=disable_standby_fields_override, should_pass_actor_input=should_pass_actor_input) if any(v is not None for v in [actor_standby_build, actor_standby_memory_mbytes, is_enabled, desired_requests_per_actor_run, max_requests_per_actor_run, idle_timeout_secs, disable_standby_fields_override, should_pass_actor_input]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-tasks/{actorTaskId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-tasks/{actorTaskId}"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_task")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_task", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_task",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor tasks
@mcp.tool(
    title="Delete Task",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_task(actor_task_id: str = Field(..., alias="actorTaskId", description="The unique identifier of the task to delete, either as a standalone task ID or as a tilde-separated combination of the owner's username and task name.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes the specified actor task and all associated configuration. This action is irreversible and removes the task from the account."""

    # Construct request model with validation
    try:
        _request = _models.ActorTaskDeleteRequest(
            path=_models.ActorTaskDeleteRequestPath(actor_task_id=actor_task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-tasks/{actorTaskId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-tasks/{actorTaskId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_task")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

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

# Tags: Actor tasks
@mcp.tool(
    title="Get Task Input",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_task_input(actor_task_id: str = Field(..., alias="actorTaskId", description="The unique identifier of the actor task, either as a standalone task ID or as a tilde-separated combination of the owner's username and the task's name.")) -> dict[str, Any] | ToolResult:
    """Retrieves the input configuration for a specified actor task. Returns the input object that defines the parameters passed to the actor when the task runs."""

    # Construct request model with validation
    try:
        _request = _models.ActorTaskInputGetRequest(
            path=_models.ActorTaskInputGetRequestPath(actor_task_id=actor_task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_task_input: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-tasks/{actorTaskId}/input", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-tasks/{actorTaskId}/input"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_task_input")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_task_input", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_task_input",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor tasks
@mcp.tool(
    title="Update Task Input",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_task_input(
    actor_task_id: str = Field(..., alias="actorTaskId", description="The unique identifier of the actor task to update, either as a standalone task ID or as a tilde-separated combination of the owner's username and the task's name."),
    body: dict[str, Any] | None = Field(None, description="A JSON object containing the input fields to update on the task. Only the specified properties will be modified; any properties not included will remain unchanged."),
) -> dict[str, Any] | ToolResult:
    """Updates the input configuration of a specific actor task by merging the provided JSON object with the existing input. Only the properties included in the request body are updated; omitted properties retain their current values."""

    # Construct request model with validation
    try:
        _request = _models.ActorTaskInputPutRequest(
            path=_models.ActorTaskInputPutRequestPath(actor_task_id=actor_task_id),
            body=_models.ActorTaskInputPutRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_task_input: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-tasks/{actorTaskId}/input", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-tasks/{actorTaskId}/input"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_task_input")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_task_input", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_task_input",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor tasks
@mcp.tool(
    title="List Task Webhooks",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_task_webhooks(
    actor_task_id: str = Field(..., alias="actorTaskId", description="The unique identifier of the Actor task, either as a plain task ID or in tilde-separated format combining the owner's username and task name."),
    offset: float | None = Field(None, description="Number of webhooks to skip from the beginning of the result set, used for paginating through records. Defaults to 0."),
    limit: float | None = Field(None, description="Maximum number of webhooks to return in a single response. Accepts values between 1 and 1000, with 1000 as both the default and upper limit."),
    desc: bool | None = Field(None, description="When set to true, reverses the sort order so that the most recently created webhooks appear first. By default, results are sorted by creation date in ascending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of webhooks associated with a specific Actor task. Results are sorted by creation date and capped at 1000 records per request."""

    # Construct request model with validation
    try:
        _request = _models.ActorTaskWebhooksGetRequest(
            path=_models.ActorTaskWebhooksGetRequestPath(actor_task_id=actor_task_id),
            query=_models.ActorTaskWebhooksGetRequestQuery(offset=offset, limit=limit, desc=desc)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_task_webhooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-tasks/{actorTaskId}/webhooks", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-tasks/{actorTaskId}/webhooks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_task_webhooks")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_task_webhooks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_task_webhooks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor tasks
@mcp.tool(
    title="List Task Runs",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_task_runs(
    actor_task_id: str = Field(..., alias="actorTaskId", description="The unique identifier of the actor task, either as a task ID or a tilde-separated combination of the owner's username and task name."),
    offset: float | None = Field(None, description="Number of runs to skip from the beginning of the result set, used for paginating through results. Defaults to 0."),
    limit: float | None = Field(None, description="Maximum number of runs to return in a single response. Accepts values between 1 and 1000, defaulting to 1000."),
    desc: bool | None = Field(None, description="When set to true, sorts runs by their start time in descending order (newest first). By default, runs are returned in ascending order."),
    status: str | None = Field(None, description="Filters results to only runs matching the specified status or comma-separated list of statuses. Valid statuses follow the Apify actor run lifecycle (e.g., SUCCEEDED, FAILED, RUNNING)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of runs for a specific actor task, including essential metadata for each run. Results can be filtered by status and sorted ascending or descending by start time."""

    # Construct request model with validation
    try:
        _request = _models.ActorTaskRunsGetRequest(
            path=_models.ActorTaskRunsGetRequestPath(actor_task_id=actor_task_id),
            query=_models.ActorTaskRunsGetRequestQuery(offset=offset, limit=limit, desc=desc, status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_task_runs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-tasks/{actorTaskId}/runs", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-tasks/{actorTaskId}/runs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_task_runs")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_task_runs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_task_runs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor tasks
@mcp.tool(
    title="Run Task",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def run_task(
    actor_task_id: str = Field(..., alias="actorTaskId", description="The unique identifier of the task to run, either as a task ID or a tilde-separated string combining the owner's username and task name."),
    timeout: float | None = Field(None, description="Maximum duration the run is allowed to execute before being terminated, in seconds. Overrides the timeout defined in the task's configuration."),
    memory: float | None = Field(None, description="Maximum RAM allocated to the run, in megabytes. Must be a power of 2 with a minimum of 128. Overrides the memory limit defined in the task's configuration."),
    max_items: float | None = Field(None, alias="maxItems", description="Maximum number of dataset items that will be billed for pay-per-result Actors. Does not cap the number of items returned — only limits charges. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable."),
    max_total_charge_usd: float | None = Field(None, alias="maxTotalChargeUsd", description="Maximum total cost in USD allowed for the run, useful for capping charges on pay-per-event Actors. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable."),
    restart_on_error: bool | None = Field(None, alias="restartOnError", description="Whether the run should automatically restart if it encounters a failure. Defaults to false."),
    build: str | None = Field(None, description="The specific Actor build to execute, specified as either a build tag or a build number. Overrides the build defined in the task's configuration, which defaults to latest."),
    wait_for_finish: float | None = Field(None, alias="waitForFinish", description="Number of seconds the server will wait for the run to finish before returning a response. Accepts values from 0 to 60; if the run completes within this window the response will reflect a terminal status, otherwise a transitional status such as RUNNING is returned."),
    webhook_event_types: list[str] | None = Field(None, description="List of event types to trigger the webhook. Common values: 'ACTOR.RUN.SUCCEEDED', 'ACTOR.RUN.FAILED', 'ACTOR.RUN.ABORTED', 'ACTOR.RUN.TIMED_OUT'."),
    webhook_request_url: str | None = Field(None, description="URL that will receive the webhook POST request when the event fires."),
    body: dict[str, Any] | None = Field(None, description="JSON object containing input properties to override the task's default input configuration. Any properties not included here will fall back to the task's or Actor's default values."),
) -> dict[str, Any] | ToolResult:
    """Starts an Actor task run asynchronously and immediately returns a run object without waiting for completion. Optionally override the task's input configuration via the request body, and use the returned run ID to poll for results or fetch dataset output."""

    # Call helper functions
    webhooks = build_webhooks(webhook_event_types, webhook_request_url)

    # Construct request model with validation
    try:
        _request = _models.ActorTaskRunsPostRequest(
            path=_models.ActorTaskRunsPostRequestPath(actor_task_id=actor_task_id),
            query=_models.ActorTaskRunsPostRequestQuery(timeout=timeout, memory=memory, max_items=max_items, max_total_charge_usd=max_total_charge_usd, restart_on_error=restart_on_error, build=build, wait_for_finish=wait_for_finish, webhooks=webhooks),
            body=_models.ActorTaskRunsPostRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for run_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-tasks/{actorTaskId}/runs", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-tasks/{actorTaskId}/runs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("run_task")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("run_task", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="run_task",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor tasks
@mcp.tool(
    title="Run Task Synchronously",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def run_task_sync_get(
    actor_task_id: str = Field(..., alias="actorTaskId", description="The unique identifier of the task to run, either as a task ID or a tilde-separated combination of the owner's username and task name."),
    timeout: float | None = Field(None, description="Maximum duration in seconds the run is allowed to execute before being timed out. If omitted, the timeout defined in the task's saved configuration is used."),
    memory: float | None = Field(None, description="Memory allocated to the run in megabytes; must be a power of 2 and at least 128 MB. If omitted, the memory limit from the task's saved configuration is used."),
    max_items: float | None = Field(None, alias="maxItems", description="Maximum number of dataset items that will be billed for pay-per-result Actors; does not cap the actual items returned, only the charge. Applies exclusively to pay-per-result Actors and is exposed inside the run via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable."),
    build: str | None = Field(None, description="The Actor build to execute, specified as either a build tag or a build number. If omitted, the build defined in the task's saved configuration (typically 'latest') is used."),
    output_record_key: str | None = Field(None, alias="outputRecordKey", description="The key of the record in the run's default key-value store whose value will be returned as the response body. Defaults to 'OUTPUT' if not specified."),
    webhook_event_types: list[str] | None = Field(None, description="List of event types to trigger the webhook. Common values: 'ACTOR.RUN.SUCCEEDED', 'ACTOR.RUN.FAILED', 'ACTOR.RUN.ABORTED', 'ACTOR.RUN.TIMED_OUT'."),
    webhook_request_url: str | None = Field(None, description="URL that will receive the webhook POST request when the event fires."),
) -> dict[str, Any] | ToolResult:
    """Runs a specific actor task synchronously and returns its output directly in the response. The task must complete within 300 seconds; if it exceeds this limit or the connection drops, the request fails but the underlying run continues."""

    # Call helper functions
    webhooks = build_webhooks(webhook_event_types, webhook_request_url)

    # Construct request model with validation
    try:
        _request = _models.ActorTaskRunSyncGetRequest(
            path=_models.ActorTaskRunSyncGetRequestPath(actor_task_id=actor_task_id),
            query=_models.ActorTaskRunSyncGetRequestQuery(timeout=timeout, memory=memory, max_items=max_items, build=build, output_record_key=output_record_key, webhooks=webhooks)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for run_task_sync_get: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-tasks/{actorTaskId}/run-sync", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-tasks/{actorTaskId}/run-sync"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("run_task_sync_get")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("run_task_sync_get", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="run_task_sync_get",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor tasks
@mcp.tool(
    title="Run Task Synchronously",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def run_task_sync(
    actor_task_id: str = Field(..., alias="actorTaskId", description="The unique identifier of the Actor task to run, either as a task ID or a tilde-separated combination of the owner's username and task name."),
    timeout: float | None = Field(None, description="Maximum duration the run is allowed to execute before being timed out, in seconds. Overrides the timeout defined in the task's configuration."),
    memory: float | None = Field(None, description="Memory allocated to the run, in megabytes. Must be a power of 2 with a minimum of 128 MB. Overrides the memory limit defined in the task's configuration."),
    max_items: float | None = Field(None, alias="maxItems", description="Maximum number of dataset items that will be billed for pay-per-result Actors. Does not cap the number of items returned, only the number charged. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable."),
    max_total_charge_usd: float | None = Field(None, alias="maxTotalChargeUsd", description="Maximum total cost in USD allowed for the run, intended for pay-per-event Actors to cap charges. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable."),
    restart_on_error: bool | None = Field(None, alias="restartOnError", description="Whether the run should automatically restart if it encounters a failure. Defaults to false."),
    build: str | None = Field(None, description="The specific Actor build to execute, specified as either a build tag or a build number. Defaults to the build defined in the task's configuration, typically the latest tag."),
    output_record_key: str | None = Field(None, alias="outputRecordKey", description="The key of the record in the run's default key-value store to return in the response body. Defaults to OUTPUT if not specified."),
    webhook_event_types: list[str] | None = Field(None, description="List of event types to trigger the webhook. Common values: 'ACTOR.RUN.SUCCEEDED', 'ACTOR.RUN.FAILED', 'ACTOR.RUN.ABORTED', 'ACTOR.RUN.TIMED_OUT'."),
    webhook_request_url: str | None = Field(None, description="URL that will receive the webhook POST request when the event fires."),
    body: dict[str, Any] | None = Field(None, description="A JSON object used to override specific input fields defined in the Actor task configuration. Any fields not included here will fall back to the task's default values. Requires the Content-Type header to be set to application/json."),
) -> dict[str, Any] | ToolResult:
    """Runs an Actor task synchronously and returns its output directly in the response. The task must complete within 300 seconds; optionally, you can override the task's default input by providing a JSON payload."""

    # Call helper functions
    webhooks = build_webhooks(webhook_event_types, webhook_request_url)

    # Construct request model with validation
    try:
        _request = _models.ActorTaskRunSyncPostRequest(
            path=_models.ActorTaskRunSyncPostRequestPath(actor_task_id=actor_task_id),
            query=_models.ActorTaskRunSyncPostRequestQuery(timeout=timeout, memory=memory, max_items=max_items, max_total_charge_usd=max_total_charge_usd, restart_on_error=restart_on_error, build=build, output_record_key=output_record_key, webhooks=webhooks),
            body=_models.ActorTaskRunSyncPostRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for run_task_sync: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-tasks/{actorTaskId}/run-sync", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-tasks/{actorTaskId}/run-sync"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("run_task_sync")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("run_task_sync", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="run_task_sync",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor tasks
@mcp.tool(
    title="Run Task Synchronously and Get Dataset Items",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def run_task_sync_and_get_dataset_items(
    actor_task_id: str = Field(..., alias="actorTaskId", description="The unique identifier of the actor task to run, either as a task ID or a tilde-separated combination of the owner's username and task name."),
    timeout: float | None = Field(None, description="Maximum duration in seconds the run is allowed to execute before being timed out. If omitted, the timeout defined in the task's saved configuration is used."),
    memory: float | None = Field(None, description="Memory allocated to the run in megabytes. Must be a power of 2 and at least 128 MB. If omitted, the memory limit from the task's saved configuration is used."),
    max_items: float | None = Field(None, alias="maxItems", description="Maximum number of dataset items that will be charged for pay-per-result actors. Does not cap the number of items returned — only limits billing. Accessible inside the actor run via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable."),
    build: str | None = Field(None, description="The actor build to execute, specified as either a build tag or a build number. If omitted, the build defined in the task's saved configuration (typically 'latest') is used."),
    format_: str | None = Field(None, alias="format", description="Output format for the returned dataset items. Supported values are: json, jsonl, csv, html, xlsx, xml, and rss. Defaults to json if not specified."),
    offset: float | None = Field(None, description="Number of items to skip from the beginning of the dataset before returning results. Useful for pagination. Defaults to 0."),
    limit: float | None = Field(None, description="Maximum number of items to include in the response. When omitted, all available items are returned without a cap."),
    fields: str | None = Field(None, description="Comma-separated list of field names to include in each returned item, excluding all other fields. Output fields are ordered to match the order specified in this list."),
    omit: str | None = Field(None, description="Comma-separated list of field names to exclude from each returned item. All other fields are retained in the output."),
    unwind: str | None = Field(None, description="Comma-separated list of fields to unwind, processed in the order specified. Array fields produce one record per element merged with the parent; object fields are merged directly into the parent. Items with missing or non-unwindable fields are preserved as-is. Unwound items are not affected by the desc parameter."),
    flatten: str | None = Field(None, description="Comma-separated list of fields whose nested object values should be flattened into dot-notation keys on the parent object. The original nested object is replaced by its flattened representation."),
    desc: bool | None = Field(None, description="When set to true, reverses the order of returned items so the most recently stored items appear first. By default items are returned in insertion order."),
    attachment: bool | None = Field(None, description="When set to true, adds a Content-Disposition: attachment header to the response, prompting browsers to download the result as a file rather than render it inline."),
    delimiter: str | None = Field(None, description="Field delimiter character used when format is csv. Special characters should be URL-encoded (e.g., %09 for tab, %3B for semicolon). Defaults to a comma."),
    bom: bool | None = Field(None, description="Controls inclusion of the UTF-8 Byte Order Mark (BOM) in the response. CSV files include the BOM by default; json, jsonl, xml, html, and rss do not. Set to true to force inclusion or false to force exclusion regardless of format."),
    xml_root: str | None = Field(None, alias="xmlRoot", description="Overrides the name of the root XML element when format is xml. Defaults to 'items'."),
    xml_row: str | None = Field(None, alias="xmlRow", description="Overrides the name of the element wrapping each individual record when format is xml. Defaults to 'item'."),
    skip_header_row: bool | None = Field(None, alias="skipHeaderRow", description="When set to true, omits the header row from csv output. Only applies when format is csv."),
    skip_hidden: bool | None = Field(None, alias="skipHidden", description="When set to true, excludes fields whose names begin with the '#' character from the output."),
    skip_empty: bool | None = Field(None, alias="skipEmpty", description="When set to true, items with no fields or empty values are excluded from the output. Note that the total number of returned items may be less than the specified limit when this is enabled."),
    simplified: bool | None = Field(None, description="When set to true, automatically applies fields=url,pageFunctionResult,errorInfo and unwind=pageFunctionResult to emulate the legacy Apify Crawler simplified output format. Not recommended for new integrations."),
    skip_failed_pages: bool | None = Field(None, alias="skipFailedPages", description="When set to true, items containing an errorInfo property are excluded from the output. Provided for backward compatibility with legacy Apify Crawler integrations and not recommended for new integrations."),
    webhook_event_types: list[str] | None = Field(None, description="List of event types to trigger the webhook. Common values: 'ACTOR.RUN.SUCCEEDED', 'ACTOR.RUN.FAILED', 'ACTOR.RUN.ABORTED', 'ACTOR.RUN.TIMED_OUT'."),
    webhook_request_url: str | None = Field(None, description="URL that will receive the webhook POST request when the event fires."),
) -> dict[str, Any] | ToolResult:
    """Synchronously runs a specific actor task and returns its dataset items directly in the response. The task must complete within 300 seconds; if it exceeds this limit the request times out, though the underlying run continues executing."""

    # Call helper functions
    webhooks = build_webhooks(webhook_event_types, webhook_request_url)

    # Construct request model with validation
    try:
        _request = _models.ActorTaskRunSyncGetDatasetItemsGetRequest(
            path=_models.ActorTaskRunSyncGetDatasetItemsGetRequestPath(actor_task_id=actor_task_id),
            query=_models.ActorTaskRunSyncGetDatasetItemsGetRequestQuery(timeout=timeout, memory=memory, max_items=max_items, build=build, format_=format_, offset=offset, limit=limit, fields=fields, omit=omit, unwind=unwind, flatten=flatten, desc=desc, attachment=attachment, delimiter=delimiter, bom=bom, xml_root=xml_root, xml_row=xml_row, skip_header_row=skip_header_row, skip_hidden=skip_hidden, skip_empty=skip_empty, simplified=simplified, skip_failed_pages=skip_failed_pages, webhooks=webhooks)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for run_task_sync_and_get_dataset_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-tasks/{actorTaskId}/run-sync-get-dataset-items", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-tasks/{actorTaskId}/run-sync-get-dataset-items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("run_task_sync_and_get_dataset_items")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("run_task_sync_and_get_dataset_items", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="run_task_sync_and_get_dataset_items",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor tasks
@mcp.tool(
    title="Run Task Synchronously and Get Dataset Items",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def run_task_sync_get_dataset_items(
    actor_task_id: str = Field(..., alias="actorTaskId", description="The unique identifier of the Actor task to run, either as a task ID or a tilde-separated string combining the owner's username and task name."),
    timeout: float | None = Field(None, description="Maximum duration in seconds the run is allowed to execute before being timed out. If not provided, the timeout defined in the task configuration is used."),
    memory: float | None = Field(None, description="Memory allocated to the run in megabytes. Must be a power of 2 and at least 128 MB. Defaults to the memory limit set in the task configuration."),
    max_items: float | None = Field(None, alias="maxItems", description="Maximum number of dataset items that will be charged for pay-per-result Actors. Does not cap the number of items returned — only limits billing. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable."),
    max_total_charge_usd: float | None = Field(None, alias="maxTotalChargeUsd", description="Maximum total cost in USD allowed for the run, intended for pay-per-event Actors to cap charges. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable."),
    restart_on_error: bool | None = Field(None, alias="restartOnError", description="When set to true, the run will automatically restart if it encounters a failure."),
    build: str | None = Field(None, description="Specifies which Actor build version to execute, provided as a build tag or build number. Defaults to the build defined in the task configuration, typically the latest tag."),
    format_: str | None = Field(None, alias="format", description="Output format for the returned dataset items. Supported values are json, jsonl, csv, html, xlsx, xml, and rss. Defaults to json."),
    offset: float | None = Field(None, description="Number of items to skip from the beginning of the dataset before returning results. Useful for pagination. Defaults to 0."),
    limit: float | None = Field(None, description="Maximum number of items to include in the response. When omitted, all available items are returned."),
    fields: str | None = Field(None, description="Comma-separated list of field names to include in each returned item, excluding all other fields. Output fields are ordered according to the order specified in this list."),
    omit: str | None = Field(None, description="Comma-separated list of field names to exclude from each returned item. All other fields are retained."),
    unwind: str | None = Field(None, description="Comma-separated list of fields to unwind, processed in the specified order. Array fields produce one record per element merged with the parent; object fields are merged directly into the parent. Items with missing or non-unwindable fields are preserved as-is. Unwound items are not affected by the desc parameter."),
    flatten: str | None = Field(None, description="Comma-separated list of fields whose nested object values should be flattened into dot-notation keys on the parent object. The original nested object is replaced by the flattened representation."),
    desc: bool | None = Field(None, description="When set to true, results are returned in reverse order from how they were stored. Defaults to ascending (insertion) order."),
    delimiter: str | None = Field(None, description="Single character used as the field delimiter in CSV output. Only applicable when format is csv. URL-encode special characters as needed. Defaults to a comma."),
    xml_root: str | None = Field(None, alias="xmlRoot", description="Overrides the name of the root XML element in xml format output. Defaults to items."),
    xml_row: str | None = Field(None, alias="xmlRow", description="Overrides the name of the element wrapping each individual record in xml format output. Defaults to item."),
    skip_header_row: bool | None = Field(None, alias="skipHeaderRow", description="When set to true, omits the header row from csv format output."),
    skip_hidden: bool | None = Field(None, alias="skipHidden", description="When set to true, fields whose names begin with the # character are excluded from the output."),
    skip_empty: bool | None = Field(None, alias="skipEmpty", description="When set to true, items with no fields or all-null values are excluded from the output. Note that the total number of returned items may be less than the specified limit when this option is active."),
    body: dict[str, Any] | None = Field(None, description="Optional JSON object to override specific input fields defined in the Actor task configuration. Fields not included in this payload retain their default values from the task or Actor input schema. Must be sent with Content-Type: application/json."),
) -> dict[str, Any] | ToolResult:
    """Runs an Actor task synchronously and returns the resulting dataset items directly in the response. Optionally override task input via the POST body and control output format, pagination, and field selection through query parameters."""

    # Construct request model with validation
    try:
        _request = _models.ActorTaskRunSyncGetDatasetItemsPostRequest(
            path=_models.ActorTaskRunSyncGetDatasetItemsPostRequestPath(actor_task_id=actor_task_id),
            query=_models.ActorTaskRunSyncGetDatasetItemsPostRequestQuery(timeout=timeout, memory=memory, max_items=max_items, max_total_charge_usd=max_total_charge_usd, restart_on_error=restart_on_error, build=build, format_=format_, offset=offset, limit=limit, fields=fields, omit=omit, unwind=unwind, flatten=flatten, desc=desc, delimiter=delimiter, xml_root=xml_root, xml_row=xml_row, skip_header_row=skip_header_row, skip_hidden=skip_hidden, skip_empty=skip_empty),
            body=_models.ActorTaskRunSyncGetDatasetItemsPostRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for run_task_sync_get_dataset_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-tasks/{actorTaskId}/run-sync-get-dataset-items", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-tasks/{actorTaskId}/run-sync-get-dataset-items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("run_task_sync_get_dataset_items")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("run_task_sync_get_dataset_items", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="run_task_sync_get_dataset_items",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor tasks
@mcp.tool(
    title="Get Last Task Run",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_last_task_run(
    actor_task_id: str = Field(..., alias="actorTaskId", description="The unique identifier of the actor task, either as a task ID or a tilde-separated combination of the owner's username and task name."),
    status: str | None = Field(None, description="Restricts the result to the last run matching the specified status, ensuring runs in other states are ignored."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the most recent run of a specified actor task, with optional filtering by run status. Also serves as the base path for accessing the last run's default storages (log, key-value store, dataset, request queue) via sub-endpoints."""

    # Construct request model with validation
    try:
        _request = _models.ActorTaskRunsLastGetRequest(
            path=_models.ActorTaskRunsLastGetRequestPath(actor_task_id=actor_task_id),
            query=_models.ActorTaskRunsLastGetRequestQuery(status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_last_task_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-tasks/{actorTaskId}/runs/last", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-tasks/{actorTaskId}/runs/last"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_last_task_run")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_last_task_run", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_last_task_run",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor runs
@mcp.tool(
    title="List Actor Runs",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_actor_runs(
    offset: float | None = Field(None, description="Number of runs to skip from the beginning of the result set, used for pagination."),
    limit: float | None = Field(None, description="Maximum number of runs to return per request; cannot exceed 1000."),
    desc: bool | None = Field(None, description="When set to true, sorts runs by their start time in descending order (newest first); defaults to ascending order."),
    status: str | None = Field(None, description="Filters results to only runs matching the given status or statuses; accepts a single status value or a comma-separated list of status values (e.g., SUCCEEDED, FAILED, RUNNING)."),
    started_after: str | None = Field(None, alias="startedAfter", description="Filters results to only runs that started at or after this point in time; must be a valid ISO 8601 datetime string in UTC."),
    started_before: str | None = Field(None, alias="startedBefore", description="Filters results to only runs that started at or before this point in time; must be a valid ISO 8601 datetime string in UTC."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all Actor runs for the authenticated user, with each item containing basic run metadata. Supports filtering by status and start time, and sorting in ascending or descending order."""

    # Construct request model with validation
    try:
        _request = _models.ActorRunsGetRequest(
            query=_models.ActorRunsGetRequestQuery(offset=offset, limit=limit, desc=desc, status=status, started_after=started_after, started_before=started_before)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_actor_runs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/actor-runs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_actor_runs")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_actor_runs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_actor_runs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor runs
@mcp.tool(
    title="Get Actor Run",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_actor_run(
    run_id: str = Field(..., alias="runId", description="The unique identifier of the Actor run to retrieve."),
    wait_for_finish: float | None = Field(None, alias="waitForFinish", description="Maximum number of seconds the server will wait for the run to reach a terminal status before responding. Accepts values from 0 to 60; if the run finishes within the specified time the response will reflect its final status, otherwise it will reflect the current transitional status."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all details about a specific Actor run, including its status, timing, and usage statistics. Optionally waits synchronously for the run to finish, eliminating the need for repeated polling."""

    # Construct request model with validation
    try:
        _request = _models.ActorRunGetRequest(
            path=_models.ActorRunGetRequestPath(run_id=run_id),
            query=_models.ActorRunGetRequestQuery(wait_for_finish=wait_for_finish)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_actor_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-runs/{runId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-runs/{runId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_actor_run")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_actor_run", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_actor_run",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor runs
@mcp.tool(
    title="Update Actor Run",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_run(
    run_id: str = Field(..., alias="runId", description="The unique identifier of the Actor run to update."),
    body: _models.ActorRunPutBody | None = Field(None, description="Request body containing the fields to update on the run. Supports setting a status message (with an optional terminal flag indicating it is the final message) and/or the general resource access level, which controls anonymous or restricted visibility of the run and its default storages and logs. Allowed access values are: FOLLOW_USER_SETTING, ANYONE_WITH_ID_CAN_READ, or RESTRICTED."),
) -> dict[str, Any] | ToolResult:
    """Updates an Actor run's status message and/or general resource access level. Use this to communicate progress to users via the Apify Console UI or to control who can view the run and its associated storages and logs."""

    # Construct request model with validation
    try:
        _request = _models.ActorRunPutRequest(
            path=_models.ActorRunPutRequestPath(run_id=run_id),
            body=_models.ActorRunPutRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-runs/{runId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-runs/{runId}"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_run")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_run", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_run",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor runs
@mcp.tool(
    title="Delete Actor Run",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_actor_run(run_id: str = Field(..., alias="runId", description="The unique identifier of the actor run to delete. The run must be in a finished state before it can be deleted.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a finished actor run. Only completed runs can be deleted, and only by the user or organization that initiated the run."""

    # Construct request model with validation
    try:
        _request = _models.ActorRunDeleteRequest(
            path=_models.ActorRunDeleteRequestPath(run_id=run_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_actor_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-runs/{runId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-runs/{runId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_actor_run")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_actor_run", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_actor_run",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor runs
@mcp.tool(
    title="Abort Run",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def abort_run(
    run_id: str = Field(..., alias="runId", description="The unique identifier of the Actor run to abort."),
    gracefully: bool | None = Field(None, description="When true, the run is aborted gracefully by sending 'aborting' and 'persistState' events before force-stopping after 30 seconds, which is useful if you intend to resurrect the run later."),
) -> dict[str, Any] | ToolResult:
    """Aborts a currently starting or running Actor run, returning full run details. Runs already in a terminal state (FINISHED, FAILED, ABORTING, TIMED-OUT) are unaffected."""

    # Construct request model with validation
    try:
        _request = _models.ActorRunAbortPostRequest(
            path=_models.ActorRunAbortPostRequestPath(run_id=run_id),
            query=_models.ActorRunAbortPostRequestQuery(gracefully=gracefully)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for abort_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-runs/{runId}/abort", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-runs/{runId}/abort"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("abort_run")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("abort_run", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="abort_run",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor runs
@mcp.tool(
    title="Metamorph Actor Run",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def metamorph_run(
    run_id: str = Field(..., alias="runId", description="The unique identifier of the Actor run to be transformed."),
    target_actor_id: str = Field(..., alias="targetActorId", description="The unique identifier of the target Actor that this run should be transformed into."),
    build: str | None = Field(None, description="Specifies which build of the target Actor to use, either as a build tag or build number. Defaults to the build defined in the target Actor's default run configuration (typically `latest`)."),
) -> dict[str, Any] | ToolResult:
    """Transforms an active Actor run into a run of a different Actor with new input, seamlessly handing off work without creating a new run. The original run's default storages are preserved and the new input is stored in the same key-value store."""

    # Construct request model with validation
    try:
        _request = _models.ActorRunMetamorphPostRequest(
            path=_models.ActorRunMetamorphPostRequestPath(run_id=run_id),
            query=_models.ActorRunMetamorphPostRequestQuery(target_actor_id=target_actor_id, build=build)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for metamorph_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-runs/{runId}/metamorph", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-runs/{runId}/metamorph"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("metamorph_run")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("metamorph_run", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="metamorph_run",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor runs
@mcp.tool(
    title="Reboot Actor Run",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def reboot_actor_run(run_id: str = Field(..., alias="runId", description="The unique identifier of the Actor run to reboot. The run must currently have a RUNNING status.")) -> dict[str, Any] | ToolResult:
    """Reboots a currently running Actor run by restarting its container, returning the updated run details. Only runs with a RUNNING status can be rebooted; any data not persisted to a key-value store, dataset, or request queue will be lost."""

    # Construct request model with validation
    try:
        _request = _models.ActorRunRebootPostRequest(
            path=_models.ActorRunRebootPostRequestPath(run_id=run_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reboot_actor_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-runs/{runId}/reboot", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-runs/{runId}/reboot"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reboot_actor_run")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reboot_actor_run", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reboot_actor_run",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor runs
@mcp.tool(
    title="Resurrect Run",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def resurrect_run(
    run_id: str = Field(..., alias="runId", description="The unique identifier of the Actor run to resurrect."),
    build: str | None = Field(None, description="The Actor build to use for the resurrected run, specified as a build tag (e.g. 'latest') or a build number. If omitted, the run restarts with the exact build version it originally executed, even if a tag like 'latest' now points to a newer build."),
    timeout: float | None = Field(None, description="Maximum duration the resurrected run is allowed to execute, in seconds. If omitted, the timeout from the original run is used."),
    memory: float | None = Field(None, description="Memory allocated to the resurrected run in megabytes; must be a power of 2 and at least 128 MB. If omitted, the memory limit from the original run is used."),
    max_items: float | None = Field(None, alias="maxItems", description="Maximum number of dataset items that will be charged for pay-per-result Actors; does not cap the actual items returned, only the billable count. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable."),
    max_total_charge_usd: float | None = Field(None, alias="maxTotalChargeUsd", description="Maximum total cost in USD allowed for the resurrected run, intended for pay-per-event Actors to cap charges to your subscription. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable."),
    restart_on_error: bool | None = Field(None, alias="restartOnError", description="Whether the resurrected run should automatically restart if it encounters a failure. If omitted, the setting from the original run is preserved."),
) -> dict[str, Any] | ToolResult:
    """Restarts a finished Actor run (with status FINISHED, FAILED, ABORTED, or TIMED-OUT) by restarting its container with the same storages, updating its status back to RUNNING. Optionally override the build, timeout, memory, and cost limits used for the resurrected run."""

    # Construct request model with validation
    try:
        _request = _models.PostResurrectRunRequest(
            path=_models.PostResurrectRunRequestPath(run_id=run_id),
            query=_models.PostResurrectRunRequestQuery(build=build, timeout=timeout, memory=memory, max_items=max_items, max_total_charge_usd=max_total_charge_usd, restart_on_error=restart_on_error)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for resurrect_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-runs/{runId}/resurrect", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-runs/{runId}/resurrect"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("resurrect_run")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("resurrect_run", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="resurrect_run",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor runs
@mcp.tool(
    title="Charge Run Event",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def charge_run_event(
    run_id: str = Field(..., alias="runId", description="The unique identifier of the Actor run to charge events against."),
    event_name: str = Field(..., alias="eventName", description="The name of the billing event to charge for, which must exactly match one of the events configured in the Actor's pay-per-event settings."),
    count: int = Field(..., description="The number of event occurrences to charge for in this request; must be a positive integer."),
) -> dict[str, Any] | ToolResult:
    """Charge for one or more occurrences of a configured pay-per-event (PPE) billing event within a specific Actor run. Must be called from within the Actor run using the same API token that started the run."""

    # Construct request model with validation
    try:
        _request = _models.PostChargeRunRequest(
            path=_models.PostChargeRunRequestPath(run_id=run_id),
            body=_models.PostChargeRunRequestBody(event_name=event_name, count=count)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for charge_run_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-runs/{runId}/charge", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-runs/{runId}/charge"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("charge_run_event")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("charge_run_event", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="charge_run_event",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor builds
@mcp.tool(
    title="List Actor Builds",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_builds(
    offset: float | None = Field(None, description="Number of builds to skip from the beginning of the result set, used for paginating through large result sets."),
    limit: float | None = Field(None, description="Maximum number of builds to return in a single response, capped at 1000 records."),
    desc: bool | None = Field(None, description="When set to true, sorts builds by their start time in descending order (newest first); defaults to ascending order (oldest first)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all builds for the authenticated user, with each entry containing basic build information. Records are sorted by start time and the endpoint returns a maximum of 1000 records per request."""

    # Construct request model with validation
    try:
        _request = _models.ActorBuildsGetRequest(
            query=_models.ActorBuildsGetRequestQuery(offset=offset, limit=limit, desc=desc)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_builds: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/actor-builds"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_builds")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_builds", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_builds",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor builds
@mcp.tool(
    title="Get Actor Build",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_actor_build(
    build_id: str = Field(..., alias="buildId", description="The unique identifier of the Actor build to retrieve."),
    wait_for_finish: float | None = Field(None, alias="waitForFinish", description="Maximum number of seconds the server will wait for the build to reach a terminal status before responding. Accepts values from 0 (default, return immediately) to 60. If the build finishes within the timeout, the response will reflect a terminal status such as SUCCEEDED; otherwise a transitional status such as RUNNING is returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieves full details about a specific Actor build, including its status, timing, and resource usage. Supports synchronous waiting via an optional timeout parameter to avoid polling when monitoring build completion."""

    # Construct request model with validation
    try:
        _request = _models.ActorBuildGetRequest(
            path=_models.ActorBuildGetRequestPath(build_id=build_id),
            query=_models.ActorBuildGetRequestQuery(wait_for_finish=wait_for_finish)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_actor_build: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-builds/{buildId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-builds/{buildId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_actor_build")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_actor_build", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_actor_build",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor builds
@mcp.tool(
    title="Delete Build",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_build(build_id: str = Field(..., alias="buildId", description="The unique identifier of the Actor build to delete, found in the build's Info tab.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific Actor build by its ID. The current default build for an Actor cannot be deleted; only users with build permissions for the Actor may perform this action."""

    # Construct request model with validation
    try:
        _request = _models.ActorBuildDeleteRequest(
            path=_models.ActorBuildDeleteRequestPath(build_id=build_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_build: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-builds/{buildId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-builds/{buildId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_build")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_build", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_build",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor builds
@mcp.tool(
    title="Abort Build",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def abort_build(build_id: str = Field(..., alias="buildId", description="The unique identifier of the Actor build to abort, available in the build's Info tab.")) -> dict[str, Any] | ToolResult:
    """Aborts a running or starting Actor build, immediately halting execution and returning the build's full details. Builds already in a terminal state (FINISHED, FAILED, ABORTING, TIMED-OUT) are unaffected by this call."""

    # Construct request model with validation
    try:
        _request = _models.ActorBuildAbortPostRequest(
            path=_models.ActorBuildAbortPostRequestPath(build_id=build_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for abort_build: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-builds/{buildId}/abort", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-builds/{buildId}/abort"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("abort_build")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("abort_build", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="abort_build",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Actor builds
@mcp.tool(
    title="Get Build Log",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_build_log(
    build_id: str = Field(..., alias="buildId", description="The unique identifier of the actor build whose log you want to retrieve."),
    stream: bool | None = Field(None, description="When set to true, the response will stream log output continuously as long as the build is still running, rather than returning a static snapshot."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the log output for a specific actor build. Supports real-time log streaming while the build is in progress."""

    # Construct request model with validation
    try:
        _request = _models.ActorBuildLogGetRequest(
            path=_models.ActorBuildLogGetRequestPath(build_id=build_id),
            query=_models.ActorBuildLogGetRequestQuery(stream=stream)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_build_log: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/actor-builds/{buildId}/log", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/actor-builds/{buildId}/log"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_build_log")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_build_log", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_build_log",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Key-value stores
@mcp.tool(
    title="List Key-Value Stores",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_key_value_stores(
    offset: float | None = Field(None, description="Number of stores to skip from the beginning of the result set, used for paginating through results."),
    limit: float | None = Field(None, description="Maximum number of stores to return in a single response. Accepts values up to 1000."),
    desc: bool | None = Field(None, description="When set to true, reverses the sort order so that the most recently created stores appear first."),
    unnamed: bool | None = Field(None, description="When set to true, returns both named and unnamed stores. By default, only named stores are included in the response."),
    ownership: Literal["ownedByMe", "sharedWithMe"] | None = Field(None, description="Filters results by ownership relationship. Omitting this parameter returns all accessible stores regardless of ownership."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of key-value stores accessible to the user, including basic metadata for each store. Results are sorted by creation date ascending by default, supporting incremental pagination as new stores are created."""

    # Construct request model with validation
    try:
        _request = _models.KeyValueStoresGetRequest(
            query=_models.KeyValueStoresGetRequestQuery(offset=offset, limit=limit, desc=desc, unnamed=unnamed, ownership=ownership)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_key_value_stores: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/key-value-stores"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_key_value_stores")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_key_value_stores", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_key_value_stores",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Key-value stores
@mcp.tool(
    title="Create Key-Value Store",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_key_value_store(name: str | None = Field(None, description="Optional unique name for the store, making it easy to identify and retrieve later. If omitted, an unnamed store is created and subject to the platform's data retention policy.")) -> dict[str, Any] | ToolResult:
    """Creates a new key-value store and returns its store object. If a store with the specified name already exists, the existing store is returned instead of creating a duplicate."""

    # Construct request model with validation
    try:
        _request = _models.KeyValueStoresPostRequest(
            query=_models.KeyValueStoresPostRequestQuery(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_key_value_store: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/key-value-stores"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_key_value_store")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_key_value_store", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_key_value_store",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Key-value stores
@mcp.tool(
    title="Get Key-Value Store",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_key_value_store(store_id: str = Field(..., alias="storeId", description="The unique identifier of the key-value store to retrieve, either as a store ID or in the format username~store-name.")) -> dict[str, Any] | ToolResult:
    """Retrieves full details about a specific key-value store, including its configuration and metadata. Use this to inspect store properties before reading or writing data."""

    # Construct request model with validation
    try:
        _request = _models.KeyValueStoreGetRequest(
            path=_models.KeyValueStoreGetRequestPath(store_id=store_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_key_value_store: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/key-value-stores/{storeId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/key-value-stores/{storeId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_key_value_store")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_key_value_store", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_key_value_store",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Key-value stores
@mcp.tool(
    title="Update Key-Value Store",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_key_value_store(
    store_id: str = Field(..., alias="storeId", description="The unique identifier of the key-value store to update, either as a store ID or in the format username~store-name."),
    name: str | None = Field(None, description="The new name to assign to the key-value store."),
    general_access: Literal["ANYONE_WITH_ID_CAN_READ", "ANYONE_WITH_NAME_CAN_READ", "FOLLOW_USER_SETTING", "RESTRICTED"] | None = Field(None, alias="generalAccess", description="The general access level for the key-value store, controlling who can read or interact with it. Use RESTRICTED to limit access, ANYONE_WITH_ID_CAN_READ or ANYONE_WITH_NAME_CAN_READ for broader read access, or FOLLOW_USER_SETTING to inherit the owner's default setting."),
) -> dict[str, Any] | ToolResult:
    """Updates a key-value store's name and general access level using the provided JSON payload. Returns the updated store object reflecting the applied changes."""

    # Construct request model with validation
    try:
        _request = _models.KeyValueStorePutRequest(
            path=_models.KeyValueStorePutRequestPath(store_id=store_id),
            body=_models.KeyValueStorePutRequestBody(name=name, general_access=general_access)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_key_value_store: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/key-value-stores/{storeId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/key-value-stores/{storeId}"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_key_value_store")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_key_value_store", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_key_value_store",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Key-value stores
@mcp.tool(
    title="Delete Key-Value Store",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_key_value_store(store_id: str = Field(..., alias="storeId", description="The unique identifier of the key-value store to delete, either as a store ID or in the format username~store-name.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a key-value store and all of its contents. This action is irreversible and removes the store along with all stored key-value pairs."""

    # Construct request model with validation
    try:
        _request = _models.KeyValueStoreDeleteRequest(
            path=_models.KeyValueStoreDeleteRequestPath(store_id=store_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_key_value_store: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/key-value-stores/{storeId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/key-value-stores/{storeId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_key_value_store")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_key_value_store", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_key_value_store",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Key-value stores
@mcp.tool(
    title="List Key-Value Store Keys",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_key_value_store_keys(
    store_id: str = Field(..., alias="storeId", description="The unique identifier of the key-value store, either as a store ID or in the format username~store-name."),
    exclusive_start_key: str | None = Field(None, alias="exclusiveStartKey", description="Pagination cursor — all keys up to and including this key are excluded from the results, allowing you to retrieve the next page of keys."),
    limit: float | None = Field(None, description="Maximum number of keys to return in a single response. Must be between 1 and 1000."),
    collection: str | None = Field(None, description="Restricts results to keys belonging to a specific collection defined in the key-value store's schema. Requires the store to have a schema configured."),
    prefix: str | None = Field(None, description="Restricts results to keys that begin with the specified string prefix, useful for filtering logically grouped keys."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of keys from a specified key-value store, including metadata about each key's associated value such as size. Supports filtering by collection or key prefix."""

    # Construct request model with validation
    try:
        _request = _models.KeyValueStoreKeysGetRequest(
            path=_models.KeyValueStoreKeysGetRequestPath(store_id=store_id),
            query=_models.KeyValueStoreKeysGetRequestQuery(exclusive_start_key=exclusive_start_key, limit=limit, collection=collection, prefix=prefix)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_key_value_store_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/key-value-stores/{storeId}/keys", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/key-value-stores/{storeId}/keys"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_key_value_store_keys")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_key_value_store_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_key_value_store_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Key-value stores
@mcp.tool(
    title="Get Key-Value Store Record",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_key_value_store_record(
    store_id: str = Field(..., alias="storeId", description="The unique identifier of the key-value store, either as a store ID or in the format username~store-name."),
    record_key: str = Field(..., alias="recordKey", description="The key under which the record is stored in the key-value store."),
    attachment: bool | None = Field(None, description="When set to true, the response is served with a Content-Disposition: attachment header, prompting browsers to download the file rather than render it, and bypasses Apify's HTML security modifications to return raw content."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the value stored under a specific key in a key-value store, returning the record with its original content type and encoding. Use the attachment parameter to fetch raw HTML content without Apify's security modifications."""

    # Construct request model with validation
    try:
        _request = _models.KeyValueStoreRecordGetRequest(
            path=_models.KeyValueStoreRecordGetRequestPath(store_id=store_id, record_key=record_key),
            query=_models.KeyValueStoreRecordGetRequestQuery(attachment=attachment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_key_value_store_record: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/key-value-stores/{storeId}/records/{recordKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/key-value-stores/{storeId}/records/{recordKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_key_value_store_record")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_key_value_store_record", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_key_value_store_record",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Key-value stores
@mcp.tool(
    title="Put Store Record",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def put_store_record(
    store_id: str = Field(..., alias="storeId", description="The unique identifier of the key-value store, either as a store ID or in the format username~store-name."),
    record_key: str = Field(..., alias="recordKey", description="The key under which the value will be stored; must be unique within the store and is used to retrieve the record later."),
    body: dict[str, Any] | None = Field(None, description="The value to store in the record; any data type or structure is supported, with the content type specified via the Content-Type request header."),
) -> dict[str, Any] | ToolResult:
    """Stores a value under a specific key in a key-value store, with the content type defined by the Content-Type header. Supports Gzip, Deflate, and Brotli compression via the Content-Encoding header to reduce payload size and improve upload speed."""

    # Construct request model with validation
    try:
        _request = _models.KeyValueStoreRecordPutRequest(
            path=_models.KeyValueStoreRecordPutRequestPath(store_id=store_id, record_key=record_key),
            body=_models.KeyValueStoreRecordPutRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for put_store_record: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/key-value-stores/{storeId}/records/{recordKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/key-value-stores/{storeId}/records/{recordKey}"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("put_store_record")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("put_store_record", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="put_store_record",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Key-value stores
@mcp.tool(
    title="Delete Key-Value Store Record",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_key_value_store_record(
    store_id: str = Field(..., alias="storeId", description="The unique identifier of the key-value store, either as a store ID or in the format username~store-name."),
    record_key: str = Field(..., alias="recordKey", description="The key identifying the specific record to delete within the store."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a single record from a key-value store by its key. The store itself and all other records remain unaffected."""

    # Construct request model with validation
    try:
        _request = _models.KeyValueStoreRecordDeleteRequest(
            path=_models.KeyValueStoreRecordDeleteRequestPath(store_id=store_id, record_key=record_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_key_value_store_record: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/key-value-stores/{storeId}/records/{recordKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/key-value-stores/{storeId}/records/{recordKey}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_key_value_store_record")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_key_value_store_record", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_key_value_store_record",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Key-value stores
@mcp.tool(
    title="Check Key-Value Store Record Exists",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def check_key_value_store_record_exists(
    store_id: str = Field(..., alias="storeId", description="The unique identifier of the key-value store, either as a store ID or in the format username~store-name."),
    record_key: str = Field(..., alias="recordKey", description="The key identifying the record to check for existence within the key-value store."),
) -> dict[str, Any] | ToolResult:
    """Checks whether a record exists in a key-value store under a specific key without retrieving its value. Useful for lightweight existence checks before performing read or write operations."""

    # Construct request model with validation
    try:
        _request = _models.KeyValueStoreRecordHeadRequest(
            path=_models.KeyValueStoreRecordHeadRequestPath(store_id=store_id, record_key=record_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_key_value_store_record_exists: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/key-value-stores/{storeId}/records/{recordKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/key-value-stores/{storeId}/records/{recordKey}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_key_value_store_record_exists")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_key_value_store_record_exists", "HEAD", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_key_value_store_record_exists",
        method="HEAD",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Datasets
@mcp.tool(
    title="List Datasets",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_datasets(
    offset: float | None = Field(None, description="Number of datasets to skip from the beginning of the result set, used for pagination. Defaults to 0."),
    limit: float | None = Field(None, description="Maximum number of datasets to return in a single response. Accepts values up to 1000, which is also the default."),
    desc: bool | None = Field(None, description="When set to true, results are sorted by creation date in descending order (newest first). By default, results are sorted in ascending order."),
    unnamed: bool | None = Field(None, description="When set to true, both named and unnamed datasets are returned. By default, only named datasets are included in the response."),
    ownership: Literal["ownedByMe", "sharedWithMe"] | None = Field(None, description="Filters results by ownership relationship. Use 'ownedByMe' to return only datasets you own, or 'sharedWithMe' to return only datasets shared with you by others. Omit to return all accessible datasets."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of datasets accessible to the user, including basic metadata for each. Supports sorting, filtering by ownership, and optionally including unnamed datasets."""

    # Construct request model with validation
    try:
        _request = _models.DatasetsGetRequest(
            query=_models.DatasetsGetRequestQuery(offset=offset, limit=limit, desc=desc, unnamed=unnamed, ownership=ownership)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_datasets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/datasets"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_datasets")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_datasets", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_datasets",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Datasets
@mcp.tool(
    title="Create Dataset",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_dataset(name: str | None = Field(None, description="Optional unique human-readable name for the dataset, allowing easy identification and retrieval in the future. If omitted, the dataset is unnamed and subject to the platform's data retention policy.")) -> dict[str, Any] | ToolResult:
    """Creates a new dataset for storing structured data and returns its object. If a name is provided and a dataset with that name already exists, the existing dataset object is returned instead."""

    # Construct request model with validation
    try:
        _request = _models.DatasetsPostRequest(
            query=_models.DatasetsPostRequestQuery(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_dataset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/datasets"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_dataset")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_dataset", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_dataset",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Datasets
@mcp.tool(
    title="Get Dataset",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_dataset(dataset_id: str = Field(..., alias="datasetId", description="The unique identifier of the dataset, either as a standalone dataset ID or in the combined username~dataset-name format.")) -> dict[str, Any] | ToolResult:
    """Retrieves metadata and storage information for a specific dataset by its ID. Note that item count fields may lag up to 5 seconds behind actual data; use the list dataset items endpoint to retrieve the dataset's contents."""

    # Construct request model with validation
    try:
        _request = _models.DatasetGetRequest(
            path=_models.DatasetGetRequestPath(dataset_id=dataset_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_dataset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/datasets/{datasetId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/datasets/{datasetId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_dataset")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_dataset", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_dataset",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Datasets
@mcp.tool(
    title="Update Dataset",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_dataset(
    dataset_id: str = Field(..., alias="datasetId", description="The unique identifier of the dataset to update, either as a standalone dataset ID or in the format username~dataset-name."),
    name: str | None = Field(None, description="The new display name to assign to the dataset."),
    general_access: Literal["ANYONE_WITH_ID_CAN_READ", "ANYONE_WITH_NAME_CAN_READ", "FOLLOW_USER_SETTING", "RESTRICTED"] | None = Field(None, alias="generalAccess", description="Controls who can access the dataset: restrict to specific users, allow anyone with the ID or name to read, or inherit from the user's default sharing setting."),
) -> dict[str, Any] | ToolResult:
    """Updates a dataset's name and general access level by dataset ID or username-scoped name. Returns the full updated dataset object."""

    # Construct request model with validation
    try:
        _request = _models.DatasetPutRequest(
            path=_models.DatasetPutRequestPath(dataset_id=dataset_id),
            body=_models.DatasetPutRequestBody(name=name, general_access=general_access)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_dataset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/datasets/{datasetId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/datasets/{datasetId}"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_dataset")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_dataset", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_dataset",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Datasets
@mcp.tool(
    title="Delete Dataset",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_dataset(dataset_id: str = Field(..., alias="datasetId", description="The unique identifier of the dataset to delete, accepted either as a standalone dataset ID or as a combined username and dataset name in the format `username~dataset-name`.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific dataset and its associated data. This action is irreversible and removes the dataset from the account."""

    # Construct request model with validation
    try:
        _request = _models.DatasetDeleteRequest(
            path=_models.DatasetDeleteRequestPath(dataset_id=dataset_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_dataset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/datasets/{datasetId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/datasets/{datasetId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_dataset")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_dataset", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_dataset",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Datasets
@mcp.tool(
    title="List Dataset Items",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_dataset_items(
    dataset_id: str = Field(..., alias="datasetId", description="The unique identifier of the dataset, either as a dataset ID or in the format `username~dataset-name`."),
    format_: str | None = Field(None, alias="format", description="Output format for the response. Structured formats (`json`, `jsonl`, `xml`) return raw item objects; tabular formats (`html`, `csv`, `xlsx`) return rows and columns limited to 2000 columns with column names up to 200 characters; `rss` returns an RSS feed. Defaults to `json`."),
    offset: float | None = Field(None, description="Number of items to skip from the beginning of the result set, used for pagination. Defaults to `0`."),
    limit: float | None = Field(None, description="Maximum number of items to include in the response. When omitted, all available items are returned. Note that using `skipEmpty` may cause fewer items to be returned than this limit."),
    fields: str | None = Field(None, description="Comma-separated list of top-level field names to include in each output item; all other fields are dropped. The order of fields in the output matches the order specified here, which can be used to enforce a consistent output schema."),
    omit: str | None = Field(None, description="Comma-separated list of top-level field names to exclude from each output item; all other fields are retained."),
    unwind: str | None = Field(None, description="Comma-separated list of fields to unwind, processed in the specified order. Array fields are expanded so each element becomes a separate item merged with the parent object; object fields are merged directly into the parent. Items whose unwind field is missing or not an array/object are preserved unchanged. Unwound items are not affected by the `desc` ordering parameter."),
    flatten: str | None = Field(None, description="Comma-separated list of fields whose nested object values should be flattened into dot-notation keys on the parent object (e.g., `foo.bar`). The original nested object is replaced by the flattened representation."),
    desc: bool | None = Field(None, description="When set to `true` or `1`, reverses the sort order so items are returned from newest to oldest. By default items are returned in insertion order (oldest first). Note that this does not reverse the order of elements within unwound arrays."),
    delimiter: str | None = Field(None, description="Single character used as the field delimiter in CSV output; only applicable when `format=csv`. URL-encode special characters as needed (e.g., `%09` for tab, `%3B` for semicolon). Defaults to a comma."),
    xml_root: str | None = Field(None, alias="xmlRoot", description="Overrides the name of the root XML element wrapping all results in XML output. Only applicable when `format=xml`. Defaults to `items`."),
    xml_row: str | None = Field(None, alias="xmlRow", description="Overrides the name of the XML element wrapping each individual item in XML output. Only applicable when `format=xml`. Defaults to `item`."),
    skip_header_row: bool | None = Field(None, alias="skipHeaderRow", description="When set to `true` or `1`, omits the header row from CSV output. Only applicable when `format=csv`."),
    skip_hidden: bool | None = Field(None, alias="skipHidden", description="When set to `true` or `1`, excludes hidden fields (top-level fields whose names begin with `#`) from the output. Equivalent to enabling `clean`."),
    skip_empty: bool | None = Field(None, alias="skipEmpty", description="When set to `true` or `1`, excludes empty items from the output. Be aware that the number of returned items may be less than the specified `limit` when this option is active."),
    view: str | None = Field(None, description="Name of a predefined view configuration defined in the dataset's schema, which controls how items are filtered and presented. Refer to the dataset schema documentation for how views are defined."),
) -> dict[str, Any] | ToolResult:
    """Retrieves items stored in a dataset, supporting multiple output formats (JSON, JSONL, XML, HTML, CSV, XLSX, RSS) with options for pagination, field filtering, sorting, and data transformation. Use this to export or inspect dataset contents produced by an Actor run."""

    # Construct request model with validation
    try:
        _request = _models.DatasetItemsGetRequest(
            path=_models.DatasetItemsGetRequestPath(dataset_id=dataset_id),
            query=_models.DatasetItemsGetRequestQuery(format_=format_, offset=offset, limit=limit, fields=fields, omit=omit, unwind=unwind, flatten=flatten, desc=desc, delimiter=delimiter, xml_root=xml_root, xml_row=xml_row, skip_header_row=skip_header_row, skip_hidden=skip_hidden, skip_empty=skip_empty, view=view)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dataset_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/datasets/{datasetId}/items", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/datasets/{datasetId}/items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dataset_items")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dataset_items", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dataset_items",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Datasets
@mcp.tool(
    title="Append Dataset Items",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def append_dataset_items(
    dataset_id: str = Field(..., alias="datasetId", description="The unique identifier of the target dataset, either as a dataset ID or in the format username~dataset-name."),
    body: list[_models.PutItemsRequest] | None = Field(None, description="A single JSON object or an array of JSON objects to append to the dataset in order; total payload must not exceed 5 MB, so split larger arrays into smaller batches."),
) -> dict[str, Any] | ToolResult:
    """Appends one or more JSON objects to the end of the specified dataset. The entire request is rejected with a 400 error if any item fails schema validation; payloads must not exceed 5 MB."""

    # Construct request model with validation
    try:
        _request = _models.DatasetItemsPostRequest(
            path=_models.DatasetItemsPostRequestPath(dataset_id=dataset_id),
            body=_models.DatasetItemsPostRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for append_dataset_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/datasets/{datasetId}/items", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/datasets/{datasetId}/items"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("append_dataset_items")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("append_dataset_items", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="append_dataset_items",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Datasets
@mcp.tool(
    title="Get Dataset Statistics",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_dataset_statistics(dataset_id: str = Field(..., alias="datasetId", description="The unique identifier of the dataset, either as a dataset ID or in the format username~dataset-name.")) -> dict[str, Any] | ToolResult:
    """Retrieves field-level statistics for a specified dataset. Returns aggregated metrics such as value counts, null rates, and type distributions for each field in the dataset."""

    # Construct request model with validation
    try:
        _request = _models.DatasetStatisticsGetRequest(
            path=_models.DatasetStatisticsGetRequestPath(dataset_id=dataset_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_dataset_statistics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/datasets/{datasetId}/statistics", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/datasets/{datasetId}/statistics"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_dataset_statistics")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_dataset_statistics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_dataset_statistics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues
@mcp.tool(
    title="List Request Queues",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_request_queues(
    offset: float | None = Field(None, description="Number of queues to skip from the beginning of the result set, used for pagination. Defaults to 0."),
    limit: float | None = Field(None, description="Maximum number of queues to return in a single response. Accepts values up to 1000, which is also the default."),
    desc: bool | None = Field(None, description="When set to true, reverses the sort order so queues are returned with the most recently created first instead of oldest first."),
    unnamed: bool | None = Field(None, description="When set to true, returns both named and unnamed queues. By default, only named queues are included in the results."),
    ownership: Literal["ownedByMe", "sharedWithMe"] | None = Field(None, description="Filters results by ownership relationship. Omitting this parameter returns all accessible queues, while specifying a value limits results to queues owned by the user or shared with them by others."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of the user's request queues, returning basic metadata for each. Results are sorted by creation date ascending by default, supporting incremental fetching as new queues are created."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueuesGetRequest(
            query=_models.RequestQueuesGetRequestQuery(offset=offset, limit=limit, desc=desc, unnamed=unnamed, ownership=ownership)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_request_queues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/request-queues"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_request_queues")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_request_queues", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_request_queues",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues
@mcp.tool(
    title="Create Request Queue",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_request_queue(name: str | None = Field(None, description="Optional unique name for the request queue, allowing easy identification and retrieval in the future. If omitted, an unnamed queue is created and subject to data retention limits.")) -> dict[str, Any] | ToolResult:
    """Creates a new request queue and returns its object, or returns the existing queue object if a queue with the given name already exists. Unnamed queues are subject to the platform's data retention policy."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueuesPostRequest(
            query=_models.RequestQueuesPostRequestQuery(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_request_queue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/request-queues"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_request_queue")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_request_queue", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_request_queue",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues
@mcp.tool(
    title="Get Request Queue",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_request_queue(queue_id: str = Field(..., alias="queueId", description="The unique identifier of the request queue to retrieve. Accepts either the queue's ID or a combined username and queue name in the format username~queue-name.")) -> dict[str, Any] | ToolResult:
    """Retrieves metadata and configuration details for a specific request queue. Returns the full queue object including its properties and current state."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueueGetRequest(
            path=_models.RequestQueueGetRequestPath(queue_id=queue_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_request_queue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/request-queues/{queueId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/request-queues/{queueId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_request_queue")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_request_queue", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_request_queue",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues
@mcp.tool(
    title="Update Request Queue",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_request_queue(
    queue_id: str = Field(..., alias="queueId", description="The unique identifier of the request queue to update, either as a queue ID or in the format username~queue-name."),
    body: _models.RequestQueuePutBody | None = Field(None, description="JSON object containing the fields to update on the request queue, such as its name or general resource access level."),
) -> dict[str, Any] | ToolResult:
    """Updates a request queue's name and resource access level by submitting a JSON payload with the desired changes. Returns the full updated request queue object upon success."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueuePutRequest(
            path=_models.RequestQueuePutRequestPath(queue_id=queue_id),
            body=_models.RequestQueuePutRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_request_queue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/request-queues/{queueId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/request-queues/{queueId}"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_request_queue")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_request_queue", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_request_queue",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues
@mcp.tool(
    title="Delete Request Queue",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_request_queue(queue_id: str = Field(..., alias="queueId", description="The unique identifier of the request queue to delete, either as a queue ID or in the format username~queue-name.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a request queue and all its associated data. This action is irreversible and removes the queue identified by its ID or name."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueueDeleteRequest(
            path=_models.RequestQueueDeleteRequestPath(queue_id=queue_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_request_queue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/request-queues/{queueId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/request-queues/{queueId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_request_queue")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_request_queue", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_request_queue",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues
@mcp.tool(
    title="Batch Add Requests",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def batch_add_requests(
    queue_id: str = Field(..., alias="queueId", description="The unique identifier of the target request queue, either as a queue ID or in the format username~queue-name."),
    client_key: str | None = Field(None, alias="clientKey", description="A unique string identifier (1–32 characters) representing the calling client, used to detect whether the queue is being accessed by multiple clients simultaneously. Omitting this value causes the system to treat the call as originating from a new client."),
    forefront: str | None = Field(None, description="Controls whether each request in the batch is inserted at the front (head) or back (end) of the queue. Accepts a boolean string value; defaults to false, placing requests at the end."),
    body: list[_models.RequestDraft] | None = Field(None, description="An array of request objects to add to the queue, with a maximum of 25 items per batch. Each item should include the request details such as URL and uniqueKey; order within the array does not affect queue priority."),
) -> dict[str, Any] | ToolResult:
    """Adds up to 25 requests to a specified request queue in a single batch operation. Returns arrays of successfully processed and unprocessed requests, with unprocessed entries recommended for retry using exponential backoff."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueueRequestsBatchPostRequest(
            path=_models.RequestQueueRequestsBatchPostRequestPath(queue_id=queue_id),
            query=_models.RequestQueueRequestsBatchPostRequestQuery(client_key=client_key, forefront=forefront),
            body=_models.RequestQueueRequestsBatchPostRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for batch_add_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/request-queues/{queueId}/requests/batch", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/request-queues/{queueId}/requests/batch"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("batch_add_requests")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("batch_add_requests", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="batch_add_requests",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues
@mcp.tool(
    title="Batch Delete Queue Requests",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def batch_delete_queue_requests(
    queue_id: str = Field(..., alias="queueId", description="The unique identifier of the request queue, either as a queue ID or in the format username~queue-name."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request body, which must be set to application/json."),
    client_key: str | None = Field(None, alias="clientKey", description="A unique string identifier (1–32 characters) representing the client accessing the queue, used to detect whether the queue has been accessed by multiple clients. If omitted, the system treats this call as originating from a new client."),
    body: list[_models.RequestDraftDelete] | None = Field(None, description="An array of request objects to delete, each identified by either an ID or uniqueKey field. The batch is limited to 25 requests; order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Batch-deletes up to 25 requests from a specified request queue, identified by their ID or uniqueKey. Any requests that fail due to rate limiting or internal errors are returned in the response for retry, with exponential backoff recommended."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueueRequestsBatchDeleteRequest(
            path=_models.RequestQueueRequestsBatchDeleteRequestPath(queue_id=queue_id),
            query=_models.RequestQueueRequestsBatchDeleteRequestQuery(client_key=client_key),
            header=_models.RequestQueueRequestsBatchDeleteRequestHeader(content_type=content_type),
            body=_models.RequestQueueRequestsBatchDeleteRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for batch_delete_queue_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/request-queues/{queueId}/requests/batch", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/request-queues/{queueId}/requests/batch"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("batch_delete_queue_requests")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("batch_delete_queue_requests", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="batch_delete_queue_requests",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues/Requests locks
@mcp.tool(
    title="Unlock Queue Requests",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def unlock_queue_requests(
    queue_id: str = Field(..., alias="queueId", description="The unique identifier of the request queue, either as a queue ID or in the format username~queue-name."),
    client_key: str | None = Field(None, alias="clientKey", description="A unique string identifier (1–32 characters) representing the client accessing the queue, used to track whether multiple clients have accessed the same queue. If omitted, the system treats the request as originating from a new client."),
) -> dict[str, Any] | ToolResult:
    """Unlocks all currently locked requests in the specified request queue that are held by the calling client. Within an Actor run, this releases locks held by both the current run and the same clientKey; outside a run, it releases all locks associated with the provided clientKey."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueueRequestsUnlockPostRequest(
            path=_models.RequestQueueRequestsUnlockPostRequestPath(queue_id=queue_id),
            query=_models.RequestQueueRequestsUnlockPostRequestQuery(client_key=client_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unlock_queue_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/request-queues/{queueId}/requests/unlock", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/request-queues/{queueId}/requests/unlock"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unlock_queue_requests")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unlock_queue_requests", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unlock_queue_requests",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues/Requests
@mcp.tool(
    title="List Queue Requests",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_queue_requests(
    queue_id: str = Field(..., alias="queueId", description="The unique identifier of the request queue, either as a queue ID or in the format username~queue-name."),
    exclusive_start_id: str | None = Field(None, alias="exclusiveStartId", description="Cursor for pagination — all requests up to and including this request ID are excluded from the results, returning only subsequent requests."),
    limit: float | None = Field(None, description="Maximum number of requests to return in a single response. Must be between 1 and 10000."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of requests from a specified request queue. Use exclusiveStartId and limit to page through large queues efficiently."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueueRequestsGetRequest(
            path=_models.RequestQueueRequestsGetRequestPath(queue_id=queue_id),
            query=_models.RequestQueueRequestsGetRequestQuery(exclusive_start_id=exclusive_start_id, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_queue_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/request-queues/{queueId}/requests", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/request-queues/{queueId}/requests"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_queue_requests")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_queue_requests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_queue_requests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues/Requests
@mcp.tool(
    title="Add Queue Request",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_queue_request(
    queue_id: str = Field(..., alias="queueId", description="The ID of the target request queue, or a combined identifier in the format username~queue-name."),
    unique_key: str = Field(..., alias="uniqueKey", description="A unique key used to deduplicate requests — requests sharing the same uniqueKey are treated as identical and will not be added twice."),
    url: str = Field(..., description="The fully qualified URL to be fetched or processed by this request, must be a valid URI."),
    method: str = Field(..., description="The HTTP method to use when executing this request (e.g., GET, POST, PUT, DELETE)."),
    client_key: str | None = Field(None, alias="clientKey", description="A unique string identifier (1–32 characters) representing the client making this request, used to detect whether the queue has been accessed by multiple clients."),
    forefront: str | None = Field(None, description="Controls where the request is inserted in the queue. Set to true to add at the front (head) of the queue, or false to append at the end. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Adds a new URL request to a specified request queue for processing. If a request with the same uniqueKey already exists in the queue, returns the ID of the existing request instead of creating a duplicate."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueueRequestsPostRequest(
            path=_models.RequestQueueRequestsPostRequestPath(queue_id=queue_id),
            query=_models.RequestQueueRequestsPostRequestQuery(client_key=client_key, forefront=forefront),
            body=_models.RequestQueueRequestsPostRequestBody(unique_key=unique_key, url=url, method=method)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_queue_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/request-queues/{queueId}/requests", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/request-queues/{queueId}/requests"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_queue_request")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_queue_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_queue_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues/Requests
@mcp.tool(
    title="Get Queue Request",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_queue_request(
    queue_id: str = Field(..., alias="queueId", description="The unique identifier of the request queue, either as a queue ID or in the format username~queue-name."),
    request_id: str = Field(..., alias="requestId", description="The unique identifier of the request to retrieve from the specified queue."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific request from a request queue by its ID. Returns the full request details including URL, metadata, and processing status."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueueRequestGetRequest(
            path=_models.RequestQueueRequestGetRequestPath(queue_id=queue_id, request_id=request_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_queue_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/request-queues/{queueId}/requests/{requestId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/request-queues/{queueId}/requests/{requestId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_queue_request")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_queue_request", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_queue_request",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues/Requests
@mcp.tool(
    title="Update Queue Request",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_queue_request(
    queue_id: str = Field(..., alias="queueId", description="The ID of the request queue, either as a direct queue ID or in the format `username~queue-name`."),
    request_id: str = Field(..., alias="requestId", description="The unique ID of the request to update within the queue."),
    id_: str = Field(..., alias="id", description="The unique identifier assigned to this request object, used to reference it within the queue."),
    unique_key: str = Field(..., alias="uniqueKey", description="A unique key used to deduplicate requests; requests sharing the same key are treated as identical and will not be added more than once."),
    url: str = Field(..., description="The target URL for this request, must be a valid URI."),
    forefront: str | None = Field(None, description="Controls whether the updated request is repositioned to the front of the queue (`true`) or remains at the end (`false`). Defaults to `false`."),
    client_key: str | None = Field(None, alias="clientKey", description="A unique string identifier (1–32 characters) representing the client making this call, used to detect whether the queue is being accessed by multiple clients simultaneously."),
    method: str | None = Field(None, description="The HTTP method to use when executing this request (e.g., GET, POST, PUT, DELETE)."),
    payload: dict[str, Any] | None = Field(None, description="The body payload to send with the request, typically used for POST or PUT requests."),
    headers: dict[str, Any] | None = Field(None, description="A key-value map of HTTP headers to include when executing this request."),
    label: str | None = Field(None, description="An optional label for categorizing or routing the request during processing."),
    image: str | None = Field(None, description="An optional URI pointing to an image associated with this request, must be a valid URI."),
    no_retry: bool | None = Field(None, alias="noRetry", description="When set to `true`, prevents the request from being retried automatically if its processing fails."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing request in a queue, allowing you to modify its properties or mark it as handled. Setting `handledAt` to the current time removes the request from the head of the queue and releases any lock on it."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueueRequestPutRequest(
            path=_models.RequestQueueRequestPutRequestPath(queue_id=queue_id, request_id=request_id),
            query=_models.RequestQueueRequestPutRequestQuery(forefront=forefront, client_key=client_key),
            body=_models.RequestQueueRequestPutRequestBody(id_=id_, unique_key=unique_key, url=url, method=method, payload=payload, headers=headers, no_retry=no_retry,
                user_data=_models.RequestQueueRequestPutRequestBodyUserData(label=label, image=image) if any(v is not None for v in [label, image]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_queue_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/request-queues/{queueId}/requests/{requestId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/request-queues/{queueId}/requests/{requestId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_queue_request")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_queue_request", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_queue_request",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues/Requests
@mcp.tool(
    title="Delete Queue Request",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_queue_request(
    queue_id: str = Field(..., alias="queueId", description="The unique identifier of the request queue, either as a queue ID or in the format username~queue-name."),
    request_id: str = Field(..., alias="requestId", description="The unique identifier of the request to delete from the queue."),
    client_key: str | None = Field(None, alias="clientKey", description="A unique string (1–32 characters) identifying the client making this call, used to track whether the queue has been accessed by multiple clients. If omitted, the system treats this call as originating from a new client."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a specific request from a request queue by its ID. Use this to discard requests that are no longer needed for processing."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueueRequestDeleteRequest(
            path=_models.RequestQueueRequestDeleteRequestPath(queue_id=queue_id, request_id=request_id),
            query=_models.RequestQueueRequestDeleteRequestQuery(client_key=client_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_queue_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/request-queues/{queueId}/requests/{requestId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/request-queues/{queueId}/requests/{requestId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_queue_request")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_queue_request", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_queue_request",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues/Requests locks
@mcp.tool(
    title="Get Request Queue Head",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_request_queue_head(
    queue_id: str = Field(..., alias="queueId", description="The unique ID of the request queue, or a combined identifier in the format `username~queue-name`."),
    limit: float | None = Field(None, description="The maximum number of requests to return from the head of the queue. If omitted, a default limit is applied."),
    client_key: str | None = Field(None, alias="clientKey", description="A unique string identifier (1–32 characters) representing the calling client, used to track whether the queue is being accessed by multiple clients. Omitting this value causes the system to treat the call as originating from a new, distinct client."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the first N requests from the head of a request queue. Returns a `hadMultipleClients` flag indicating whether the queue has been accessed by more than one client, which helps SDKs determine local cache consistency."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueueHeadGetRequest(
            path=_models.RequestQueueHeadGetRequestPath(queue_id=queue_id),
            query=_models.RequestQueueHeadGetRequestQuery(limit=limit, client_key=client_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_request_queue_head: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/request-queues/{queueId}/head", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/request-queues/{queueId}/head"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_request_queue_head")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_request_queue_head", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_request_queue_head",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues/Requests locks
@mcp.tool(
    title="Lock Queue Head Requests",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def lock_queue_head_requests(
    queue_id: str = Field(..., alias="queueId", description="The unique identifier of the request queue, either as a queue ID or in the format username~queue-name."),
    lock_secs: float = Field(..., alias="lockSecs", description="The duration in seconds for which the retrieved requests will be locked and unavailable to other clients or runs."),
    limit: float | None = Field(None, description="The maximum number of requests to retrieve from the head of the queue, between 1 and 25.", le=25),
    client_key: str | None = Field(None, alias="clientKey", description="A unique string identifier (1–32 characters) representing the calling client, used to detect whether the queue is being accessed by multiple distinct clients. Omitting this value causes the system to treat the call as originating from a new client."),
) -> dict[str, Any] | ToolResult:
    """Retrieves and locks a specified number of requests from the head of a request queue, preventing other clients or runs from accessing them for the duration of the lock period. Returns a flag indicating whether the queue has been accessed by multiple clients."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueueHeadLockPostRequest(
            path=_models.RequestQueueHeadLockPostRequestPath(queue_id=queue_id),
            query=_models.RequestQueueHeadLockPostRequestQuery(lock_secs=lock_secs, limit=limit, client_key=client_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for lock_queue_head_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/request-queues/{queueId}/head/lock", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/request-queues/{queueId}/head/lock"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("lock_queue_head_requests")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("lock_queue_head_requests", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="lock_queue_head_requests",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues/Requests locks
@mcp.tool(
    title="Prolong Request Lock",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def prolong_request_lock(
    queue_id: str = Field(..., alias="queueId", description="The unique identifier of the request queue, either as a queue ID or in the format username~queue-name."),
    request_id: str = Field(..., alias="requestId", description="The unique identifier of the request whose lock you want to prolong."),
    lock_secs: float = Field(..., alias="lockSecs", description="The number of seconds to extend the lock duration from the current time. Must be a positive value."),
    client_key: str | None = Field(None, alias="clientKey", description="A unique string identifier (1–32 characters) representing the client accessing the queue. Must match the client key used when the request was originally locked in order to prolong or delete the lock."),
    forefront: str | None = Field(None, description="Controls where the request is placed in the queue after its lock expires — set to true to move it to the front of the queue, or false to place it at the end."),
) -> dict[str, Any] | ToolResult:
    """Extends the lock duration on a specific request in a queue, preventing other clients from acquiring it. Only the client that originally locked the request can prolong its lock."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueueRequestLockPutRequest(
            path=_models.RequestQueueRequestLockPutRequestPath(queue_id=queue_id, request_id=request_id),
            query=_models.RequestQueueRequestLockPutRequestQuery(lock_secs=lock_secs, client_key=client_key, forefront=forefront)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for prolong_request_lock: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/request-queues/{queueId}/requests/{requestId}/lock", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/request-queues/{queueId}/requests/{requestId}/lock"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("prolong_request_lock")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("prolong_request_lock", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="prolong_request_lock",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Storage/Request queues/Requests locks
@mcp.tool(
    title="Delete Request Lock",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_request_lock(
    queue_id: str = Field(..., alias="queueId", description="The unique identifier of the request queue, either as a queue ID or in the format username~queue-name."),
    request_id: str = Field(..., alias="requestId", description="The unique identifier of the request whose lock should be deleted."),
    content_type: Literal["application/json"] = Field(..., alias="Content-Type", description="The media type of the request body, which must be application/json."),
    client_key: str | None = Field(None, alias="clientKey", description="A unique string identifier (1–32 characters) representing the client releasing the lock. Must match the client key used when the lock was originally acquired."),
    forefront: str | None = Field(None, description="Controls where the request is re-inserted in the queue after the lock is removed — set to true to place it at the front of the queue, or false to append it to the end."),
) -> dict[str, Any] | ToolResult:
    """Releases a lock on a specific request in a queue, making it available for other clients to process. Only the client that originally locked the request (via the lock head operation) can delete its lock."""

    # Construct request model with validation
    try:
        _request = _models.RequestQueueRequestLockDeleteRequest(
            path=_models.RequestQueueRequestLockDeleteRequestPath(queue_id=queue_id, request_id=request_id),
            query=_models.RequestQueueRequestLockDeleteRequestQuery(client_key=client_key, forefront=forefront),
            header=_models.RequestQueueRequestLockDeleteRequestHeader(content_type=content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_request_lock: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/request-queues/{queueId}/requests/{requestId}/lock", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/request-queues/{queueId}/requests/{requestId}/lock"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_request_lock")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_request_lock", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_request_lock",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks/Webhooks
@mcp.tool(
    title="List Webhooks",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_webhooks(
    offset: float | None = Field(None, description="Number of records to skip from the beginning of the result set, used for paginating through results."),
    limit: float | None = Field(None, description="Maximum number of webhook records to return in a single request, with an upper bound of 1000."),
    desc: bool | None = Field(None, description="When set to true, results are sorted by creation date in descending order (newest first); defaults to ascending order (oldest first)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of webhooks created by the authenticated user. Results are sorted by creation date and capped at 1000 records per request."""

    # Construct request model with validation
    try:
        _request = _models.WebhooksGetRequest(
            query=_models.WebhooksGetRequestQuery(offset=offset, limit=limit, desc=desc)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/webhooks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_webhooks")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

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

# Tags: Webhooks/Webhooks
@mcp.tool(
    title="Create Webhook",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_webhook(
    event_types: list[Literal["ACTOR.BUILD.ABORTED", "ACTOR.BUILD.CREATED", "ACTOR.BUILD.FAILED", "ACTOR.BUILD.SUCCEEDED", "ACTOR.BUILD.TIMED_OUT", "ACTOR.RUN.ABORTED", "ACTOR.RUN.CREATED", "ACTOR.RUN.FAILED", "ACTOR.RUN.RESURRECTED", "ACTOR.RUN.SUCCEEDED", "ACTOR.RUN.TIMED_OUT", "TEST"]] = Field(..., alias="eventTypes", description="List of event types that will trigger this webhook. Each item must be a valid Apify event string (e.g., ACTOR.RUN.SUCCEEDED, ACTOR.RUN.FAILED, ACTOR.RUN.ABORTED). Order is not significant."),
    request_url: str = Field(..., alias="requestUrl", description="The target URL to which webhook event data is sent as an HTTP POST request with a JSON payload. Must be a valid absolute URI."),
    is_ad_hoc: bool | None = Field(None, alias="isAdHoc", description="When true, marks the webhook as ad-hoc (not permanently assigned to an Actor or task). Defaults to false for standard persistent webhooks."),
    actor_id: str | None = Field(None, alias="actorId", description="ID of the Actor to assign this webhook to. Provide inside the condition object along with optionally actorTaskId to scope the webhook to a specific Actor."),
    actor_task_id: str | None = Field(None, alias="actorTaskId", description="ID of the Actor task to assign this webhook to. Provide inside the condition object to scope the webhook to a specific task run."),
    actor_run_id: str | None = Field(None, alias="actorRunId", description="ID of a specific Actor run to associate with this webhook, used to scope the webhook to a particular run instance."),
    idempotency_key: str | None = Field(None, alias="idempotencyKey", description="Unique key used to prevent duplicate webhook creation. Multiple requests with the same key will only create the webhook once and return the existing webhook on subsequent calls. Use a UUID or sufficiently random string."),
    ignore_ssl_errors: bool | None = Field(None, alias="ignoreSslErrors", description="When true, SSL certificate errors on the target requestUrl will be ignored during webhook dispatch. Defaults to false."),
    do_not_retry: bool | None = Field(None, alias="doNotRetry", description="When true, failed webhook dispatch attempts will not be retried. Defaults to false, meaning Apify will retry on failure."),
    payload_template: str | None = Field(None, alias="payloadTemplate", description="A JSON-like template string defining the payload sent to the requestUrl. Supports Apify template variables (e.g., {{userId}}, {{resource}}). If shouldInterpolateStrings is true, variables inside string values are also interpolated."),
    headers_template: str | None = Field(None, alias="headersTemplate", description="A JSON-like template string defining custom HTTP headers sent with the webhook request. Supports Apify template variables. Note: host, Content-Type, X-Apify-Webhook, X-Apify-Webhook-Dispatch-Id, and X-Apify-Request-Origin are always overwritten with defaults."),
    description: str | None = Field(None, description="Optional human-readable label for the webhook to help identify its purpose."),
    should_interpolate_strings: bool | None = Field(None, alias="shouldInterpolateStrings", description="When true, Apify template variables found inside string values within the payloadTemplate are interpolated. When false, only top-level variable placeholders are replaced."),
) -> dict[str, Any] | ToolResult:
    """Creates a new webhook that triggers HTTP POST requests to a target URL when specified Actor or task events occur. Use an idempotency key to safely retry creation without duplicating webhooks."""

    # Construct request model with validation
    try:
        _request = _models.WebhooksPostRequest(
            body=_models.WebhooksPostRequestBody(is_ad_hoc=is_ad_hoc, event_types=event_types, idempotency_key=idempotency_key, ignore_ssl_errors=ignore_ssl_errors, do_not_retry=do_not_retry, request_url=request_url, payload_template=payload_template, headers_template=headers_template, description=description, should_interpolate_strings=should_interpolate_strings,
                condition=_models.WebhooksPostRequestBodyCondition(actor_id=actor_id, actor_task_id=actor_task_id, actor_run_id=actor_run_id) if any(v is not None for v in [actor_id, actor_task_id, actor_run_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/webhooks"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_webhook")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_webhook", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_webhook",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks/Webhooks
@mcp.tool(
    title="Get Webhook",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_webhook(webhook_id: str = Field(..., alias="webhookId", description="The unique identifier of the webhook to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves full details of a specific webhook by its unique identifier. Returns all webhook configuration and metadata."""

    # Construct request model with validation
    try:
        _request = _models.WebhookGetRequest(
            path=_models.WebhookGetRequestPath(webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/webhooks/{webhookId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/webhooks/{webhookId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_webhook")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

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

# Tags: Webhooks/Webhooks
@mcp.tool(
    title="Update Webhook",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_webhook(
    webhook_id: str = Field(..., alias="webhookId", description="The unique identifier of the webhook to update."),
    is_ad_hoc: bool | None = Field(None, alias="isAdHoc", description="Indicates whether the webhook is ad hoc (created for a single run) rather than a persistent webhook."),
    event_types: list[Literal["ACTOR.BUILD.ABORTED", "ACTOR.BUILD.CREATED", "ACTOR.BUILD.FAILED", "ACTOR.BUILD.SUCCEEDED", "ACTOR.BUILD.TIMED_OUT", "ACTOR.RUN.ABORTED", "ACTOR.RUN.CREATED", "ACTOR.RUN.FAILED", "ACTOR.RUN.RESURRECTED", "ACTOR.RUN.SUCCEEDED", "ACTOR.RUN.TIMED_OUT", "TEST"]] | None = Field(None, alias="eventTypes", description="List of event types that trigger this webhook, such as actor run lifecycle events. Order is not significant; each item must be a valid event type string."),
    actor_id: str | None = Field(None, alias="actorId", description="The ID of the Actor whose events should trigger this webhook. Scopes the webhook to a specific Actor."),
    actor_task_id: str | None = Field(None, alias="actorTaskId", description="The ID of the Actor task whose events should trigger this webhook. Scopes the webhook to a specific task."),
    actor_run_id: str | None = Field(None, alias="actorRunId", description="The ID of the Actor run whose events should trigger this webhook. Scopes the webhook to a specific run."),
    ignore_ssl_errors: bool | None = Field(None, alias="ignoreSslErrors", description="When true, SSL certificate errors on the target request URL are ignored. Use with caution in production environments."),
    do_not_retry: bool | None = Field(None, alias="doNotRetry", description="When true, failed webhook delivery attempts will not be retried automatically."),
    request_url: str | None = Field(None, alias="requestUrl", description="The destination URL to which the webhook will send HTTP POST requests when triggered. Must be a valid URI."),
    payload_template: str | None = Field(None, alias="payloadTemplate", description="A template string defining the JSON payload sent with each webhook request. Supports variable interpolation using double curly brace syntax."),
    headers_template: str | None = Field(None, alias="headersTemplate", description="A template string defining custom HTTP headers included with each webhook request. Supports variable interpolation using double curly brace syntax."),
    description: str | None = Field(None, description="A human-readable description of the webhook's purpose or configuration for identification."),
    should_interpolate_strings: bool | None = Field(None, alias="shouldInterpolateStrings", description="When true, string values within the payload and headers templates will have variable placeholders interpolated before the request is sent."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing webhook's configuration by its ID, applying only the properties provided in the JSON request body. Returns the full updated webhook object."""

    # Construct request model with validation
    try:
        _request = _models.WebhookPutRequest(
            path=_models.WebhookPutRequestPath(webhook_id=webhook_id),
            body=_models.WebhookPutRequestBody(is_ad_hoc=is_ad_hoc, event_types=event_types, ignore_ssl_errors=ignore_ssl_errors, do_not_retry=do_not_retry, request_url=request_url, payload_template=payload_template, headers_template=headers_template, description=description, should_interpolate_strings=should_interpolate_strings,
                condition=_models.WebhookPutRequestBodyCondition(actor_id=actor_id, actor_task_id=actor_task_id, actor_run_id=actor_run_id) if any(v is not None for v in [actor_id, actor_task_id, actor_run_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/webhooks/{webhookId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/webhooks/{webhookId}"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_webhook")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_webhook", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_webhook",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks/Webhooks
@mcp.tool(
    title="Delete Webhook",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_webhook(webhook_id: str = Field(..., alias="webhookId", description="The unique identifier of the webhook to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a webhook by its unique identifier. This action is irreversible and will stop all event notifications associated with the webhook."""

    # Construct request model with validation
    try:
        _request = _models.WebhookDeleteRequest(
            path=_models.WebhookDeleteRequestPath(webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/webhooks/{webhookId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/webhooks/{webhookId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_webhook")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_webhook", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_webhook",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks/Webhooks
@mcp.tool(
    title="Test Webhook",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def test_webhook(webhook_id: str = Field(..., alias="webhookId", description="The unique identifier of the webhook to test.")) -> dict[str, Any] | ToolResult:
    """Sends a test dispatch to the specified webhook using a dummy payload. Useful for verifying that the webhook endpoint is correctly configured and reachable."""

    # Construct request model with validation
    try:
        _request = _models.WebhookTestPostRequest(
            path=_models.WebhookTestPostRequestPath(webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for test_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/webhooks/{webhookId}/test", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/webhooks/{webhookId}/test"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("test_webhook")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("test_webhook", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="test_webhook",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks/Webhooks
@mcp.tool(
    title="List Webhook Dispatches",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_webhook_dispatches_by_webhook(webhook_id: str = Field(..., alias="webhookId", description="The unique identifier of the webhook whose dispatch history you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the list of dispatch records for a specific webhook, showing its delivery history and execution events."""

    # Construct request model with validation
    try:
        _request = _models.WebhookWebhookDispatchesGetRequest(
            path=_models.WebhookWebhookDispatchesGetRequestPath(webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhook_dispatches_by_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/webhooks/{webhookId}/dispatches", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/webhooks/{webhookId}/dispatches"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_webhook_dispatches_by_webhook")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_webhook_dispatches_by_webhook", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_webhook_dispatches_by_webhook",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks/Webhook dispatches
@mcp.tool(
    title="List Webhook Dispatches",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_webhook_dispatches(
    offset: float | None = Field(None, description="Number of records to skip from the beginning of the result set, used for paginating through results. Defaults to 0."),
    limit: float | None = Field(None, description="Maximum number of webhook dispatch records to return in a single response. Accepts values up to 1000, which is also the default."),
    desc: bool | None = Field(None, description="When set to true, sorts the returned records by the createdAt field in descending order (newest first). Defaults to ascending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of webhook dispatches associated with the authenticated user. Results are sorted by creation date and capped at 1000 records per request."""

    # Construct request model with validation
    try:
        _request = _models.WebhookDispatchesGetRequest(
            query=_models.WebhookDispatchesGetRequestQuery(offset=offset, limit=limit, desc=desc)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhook_dispatches: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/webhook-dispatches"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_webhook_dispatches")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_webhook_dispatches", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_webhook_dispatches",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks/Webhook dispatches
@mcp.tool(
    title="Get Webhook Dispatch",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_webhook_dispatch(dispatch_id: str = Field(..., alias="dispatchId", description="The unique identifier of the webhook dispatch record to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a webhook dispatch record by its unique ID, returning full details about the dispatch event, status, and payload."""

    # Construct request model with validation
    try:
        _request = _models.WebhookDispatchGetRequest(
            path=_models.WebhookDispatchGetRequestPath(dispatch_id=dispatch_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook_dispatch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/webhook-dispatches/{dispatchId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/webhook-dispatches/{dispatchId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_webhook_dispatch")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_webhook_dispatch", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_webhook_dispatch",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Schedules
@mcp.tool(
    title="List Schedules",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_schedules(
    offset: float | None = Field(None, description="Number of schedules to skip from the beginning of the result set, used for paginating through records."),
    limit: float | None = Field(None, description="Maximum number of schedules to return in a single request, capped at 1000."),
    desc: bool | None = Field(None, description="When set to true, sorts the returned schedules by creation date in descending order instead of the default ascending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of schedules created by the user. Results are sorted by creation date ascending by default, with a maximum of 1000 records per request."""

    # Construct request model with validation
    try:
        _request = _models.SchedulesGetRequest(
            query=_models.SchedulesGetRequestQuery(offset=offset, limit=limit, desc=desc)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_schedules: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/schedules"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_schedules")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_schedules", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_schedules",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Schedules
@mcp.tool(
    title="Create Schedule",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_schedule(
    name: str | None = Field(None, description="Unique identifier name for the schedule, used to reference it programmatically."),
    is_enabled: bool | None = Field(None, alias="isEnabled", description="Controls whether the schedule is active and will trigger at its configured times. Set to false to create the schedule in a paused state."),
    is_exclusive: bool | None = Field(None, alias="isExclusive", description="When true, ensures only one run of this schedule executes at a time, preventing overlapping executions if a previous run is still in progress."),
    cron_expression: str | None = Field(None, alias="cronExpression", description="Defines the schedule's timing using standard cron syntax (minute, hour, day-of-month, month, day-of-week)."),
    timezone_: str | None = Field(None, alias="timezone", description="IANA timezone name used to interpret the cron expression, ensuring the schedule fires at the correct local time."),
    description: str | None = Field(None, description="Human-readable explanation of the schedule's purpose, useful for documentation and identifying what the schedule does."),
    title: str | None = Field(None, description="Display-friendly label for the schedule shown in the UI, distinct from the programmatic name."),
    actions: list[_models.ScheduleCreateActions] | None = Field(None, description="List of actions to execute when the schedule triggers. Each item defines an action type and its configuration; order determines execution sequence."),
) -> dict[str, Any] | ToolResult:
    """Creates a new schedule with the specified configuration, including timing, timezone, and associated actions. Returns the fully created schedule object upon success."""

    # Construct request model with validation
    try:
        _request = _models.SchedulesPostRequest(
            body=_models.SchedulesPostRequestBody(name=name, is_enabled=is_enabled, is_exclusive=is_exclusive, cron_expression=cron_expression, timezone_=timezone_, description=description, title=title, actions=actions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_schedule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/schedules"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_schedule")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_schedule", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_schedule",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Schedules
@mcp.tool(
    title="Get Schedule",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_schedule(schedule_id: str = Field(..., alias="scheduleId", description="The unique identifier of the schedule to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a schedule object with all associated details by its unique identifier. Use this to inspect scheduling configuration, timing, and related metadata for a specific schedule."""

    # Construct request model with validation
    try:
        _request = _models.ScheduleGetRequest(
            path=_models.ScheduleGetRequestPath(schedule_id=schedule_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_schedule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/schedules/{scheduleId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/schedules/{scheduleId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_schedule")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_schedule", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_schedule",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Schedules
@mcp.tool(
    title="Update Schedule",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_schedule(
    schedule_id: str = Field(..., alias="scheduleId", description="The unique identifier of the schedule to update."),
    name: str | None = Field(None, description="A short machine-friendly identifier for the schedule, typically used for referencing it programmatically."),
    is_enabled: bool | None = Field(None, alias="isEnabled", description="Whether the schedule is active and will trigger its actions at the defined times. Set to false to pause the schedule without deleting it."),
    is_exclusive: bool | None = Field(None, alias="isExclusive", description="Whether the schedule runs exclusively, preventing overlapping executions if a previous run is still in progress when the next trigger fires."),
    cron_expression: str | None = Field(None, alias="cronExpression", description="The cron expression defining when the schedule triggers, using standard five-field cron syntax (minute, hour, day-of-month, month, day-of-week)."),
    timezone_: str | None = Field(None, alias="timezone", description="The IANA timezone name used to interpret the cron expression, ensuring triggers fire at the correct local time."),
    description: str | None = Field(None, description="A human-readable explanation of the schedule's purpose or context, useful for documentation and identification."),
    title: str | None = Field(None, description="A human-friendly display name for the schedule, intended for presentation in UIs or dashboards."),
    actions: list[_models.ScheduleCreateActions] | None = Field(None, description="An ordered list of action objects that the schedule will execute when triggered. Each item defines the type and configuration of an action to perform."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing schedule by its ID, applying only the properties provided in the request body while leaving unspecified properties unchanged. Returns the full updated schedule object."""

    # Construct request model with validation
    try:
        _request = _models.SchedulePutRequest(
            path=_models.SchedulePutRequestPath(schedule_id=schedule_id),
            body=_models.SchedulePutRequestBody(name=name, is_enabled=is_enabled, is_exclusive=is_exclusive, cron_expression=cron_expression, timezone_=timezone_, description=description, title=title, actions=actions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_schedule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/schedules/{scheduleId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/schedules/{scheduleId}"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_schedule")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_schedule", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_schedule",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Schedules
@mcp.tool(
    title="Delete Schedule",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_schedule(schedule_id: str = Field(..., alias="scheduleId", description="The unique identifier of the schedule to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a schedule by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.ScheduleDeleteRequest(
            path=_models.ScheduleDeleteRequestPath(schedule_id=schedule_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_schedule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/schedules/{scheduleId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/schedules/{scheduleId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_schedule")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_schedule", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_schedule",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Schedules
@mcp.tool(
    title="Get Schedule Log",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_schedule_log(schedule_id: str = Field(..., alias="scheduleId", description="The unique identifier of the schedule whose invocation log you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the execution log for a specific schedule, returning a JSON array of up to 1000 recent invocation records. Useful for auditing schedule activity and diagnosing execution history."""

    # Construct request model with validation
    try:
        _request = _models.ScheduleLogGetRequest(
            path=_models.ScheduleLogGetRequestPath(schedule_id=schedule_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_schedule_log: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/schedules/{scheduleId}/log", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/schedules/{scheduleId}/log"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_schedule_log")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_schedule_log", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_schedule_log",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Store
@mcp.tool(
    title="List Store Actors",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_store_actors(
    limit: float | None = Field(None, description="Maximum number of Actors to return in a single response. Accepts values up to 1,000."),
    offset: float | None = Field(None, description="Number of Actors to skip from the beginning of the result set, used for paginating through results."),
    search: str | None = Field(None, description="Keyword or phrase used to search Actors across their title, name, description, username, and readme fields."),
    sort_by: str | None = Field(None, alias="sortBy", description="Field by which to sort the returned Actors. Supported values are relevance (default), popularity, newest, and lastUpdate."),
    category: str | None = Field(None, description="Filters results to only include Actors belonging to the specified category."),
    username: str | None = Field(None, description="Filters results to only include Actors published by the specified username."),
    pricing_model: Literal["FREE", "FLAT_PRICE_PER_MONTH", "PRICE_PER_DATASET_ITEM", "PAY_PER_EVENT"] | None = Field(None, alias="pricingModel", description="Filters results to only include Actors with the specified pricing model. Must be one of the supported pricing model values."),
    allows_agentic_users: bool | None = Field(None, alias="allowsAgenticUsers", description="When true, restricts results to Actors that permit agentic users; when false, restricts results to Actors that do not permit agentic users."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of publicly available Actors from the Apify Store, with support for keyword search, filtering, and sorting. Returns up to 1,000 results and supports pagination."""

    # Construct request model with validation
    try:
        _request = _models.StoreGetRequest(
            query=_models.StoreGetRequestQuery(limit=limit, offset=offset, search=search, sort_by=sort_by, category=category, username=username, pricing_model=pricing_model, allows_agentic_users=allows_agentic_users)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_store_actors: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/store"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_store_actors")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_store_actors", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_store_actors",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Logs
@mcp.tool(
    title="Get Run Log",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_run_log(
    build_or_run_id: str = Field(..., alias="buildOrRunId", description="The unique identifier of the Actor build or run whose logs you want to retrieve."),
    stream: bool | None = Field(None, description="When set to true, the response streams log output continuously while the build or run is still active, rather than returning a static snapshot."),
    raw: bool | None = Field(None, description="When set to true, logs are returned verbatim including ANSI escape codes. By default, ANSI escape codes are stripped and only printable characters are returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the log output for a specific Actor build or run. Supports real-time streaming for active runs and optional preservation of raw ANSI escape codes."""

    # Construct request model with validation
    try:
        _request = _models.LogGetRequest(
            path=_models.LogGetRequestPath(build_or_run_id=build_or_run_id),
            query=_models.LogGetRequestQuery(stream=stream, raw=raw)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_run_log: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/logs/{buildOrRunId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/logs/{buildOrRunId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_run_log")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_run_log", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_run_log",
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
async def get_user(user_id: str = Field(..., alias="userId", description="The unique identifier or username of the user whose public profile data should be retrieved.")) -> dict[str, Any] | ToolResult:
    """Retrieves public profile information for a specific user account, equivalent to what is visible on their public profile page. No authentication is required to call this endpoint."""

    # Construct request model with validation
    try:
        _request = _models.UserGetRequest(
            path=_models.UserGetRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/users/{userId}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/users/{userId}"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

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
    title="Get Current User",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_current_user() -> dict[str, Any] | ToolResult:
    """Retrieves both public and private profile data for the authenticated user account identified by the provided token. Note that plan, email, and profile fields are excluded when accessed from within an Actor run."""

    # Extract parameters for API call
    _http_path = "/v2/users/me"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_current_user")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_current_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_current_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool(
    title="Get Monthly Usage",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_monthly_usage(date: str | None = Field(None, description="The date within the billing cycle you want to retrieve usage for, in YYYY-MM-DD format. If omitted, the current billing cycle is returned.")) -> dict[str, Any] | ToolResult:
    """Retrieves a complete summary of your usage for the current or a specified billing cycle, including storage, data transfer, and request queue usage with both an overall total and a daily breakdown."""

    # Construct request model with validation
    try:
        _request = _models.UsersMeUsageMonthlyGetRequest(
            query=_models.UsersMeUsageMonthlyGetRequestQuery(date=date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_monthly_usage: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/users/me/usage/monthly"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_monthly_usage")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_monthly_usage", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_monthly_usage",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool(
    title="Get Account Limits",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_account_limits() -> dict[str, Any] | ToolResult:
    """Retrieves a complete summary of the authenticated account's limits, current usage cycle, and usage statistics, equivalent to the Limits page in the Apify console."""

    # Extract parameters for API call
    _http_path = "/v2/users/me/limits"
    _http_query = {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_account_limits")
    _http_headers.update(_auth.get("headers", {}))
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_account_limits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_account_limits",
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
        print("  python apify_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Apify MCP Server")

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
    logger.info("Starting Apify MCP Server")
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

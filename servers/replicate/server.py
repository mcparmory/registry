#!/usr/bin/env python3
"""
Replicate MCP Server

API Info:
- Terms of Service: https://replicate.com/terms

Generated: 2026-05-12 12:24:35 UTC
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
from mcp.types import ToolAnnotations
from pydantic import Field

BASE_URL = os.getenv("BASE_URL", "https://api.replicate.com/v1")
SERVER_NAME = "Replicate"
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
    'bearerAuth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["bearerAuth"] = _auth.BearerTokenAuth(env_var="BEARER_TOKEN", token_format="Bearer")
    logging.info("Authentication configured: bearerAuth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for bearerAuth not configured: {error_msg}")
    _auth_handlers["bearerAuth"] = None

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

mcp = FastMCP("Replicate", middleware=[_JsonCoercionMiddleware()])


@mcp.tool(
    title="Get Account",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_account() -> dict[str, Any] | ToolResult:
    """Retrieve information about the authenticated account associated with the provided API token, including account type, username, display name, and GitHub URL."""

    # Extract parameters for API call
    _http_path = "/account"
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


@mcp.tool(
    title="List Collections",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_collections() -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of model collections available on Replicate, each containing curated groups of related models organized by use case or capability."""

    # Extract parameters for API call
    _http_path = "/collections"
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
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Collection",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_collection(collection_slug: str = Field(..., description="The unique identifier slug for the collection (e.g., 'super-resolution', 'image-restoration'). Find available collections at replicate.com/collections.")) -> dict[str, Any] | ToolResult:
    """Retrieve a collection of models by its slug, including the collection metadata and all models within it."""

    # Construct request model with validation
    try:
        _request = _models.CollectionsGetRequest(
            path=_models.CollectionsGetRequestPath(collection_slug=collection_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/collections/{collection_slug}", _request.path.model_dump(by_alias=True)) if _request.path else "/collections/{collection_slug}"
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


@mcp.tool(
    title="List Deployments",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_deployments() -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of all deployments associated with your account, sorted by most recent first. Each deployment includes its current release configuration with model, version, and hardware settings."""

    # Extract parameters for API call
    _http_path = "/deployments"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_deployments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_deployments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_deployments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Deployment",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_deployment(
    hardware: str = Field(..., description="The hardware SKU to run the model on. Available SKUs can be retrieved from the hardware list endpoint (e.g., gpu-t4, gpu-a40)."),
    max_instances: int = Field(..., description="The maximum number of instances for auto-scaling. Must be between 0 and 20, and should be greater than or equal to min_instances.", ge=0, le=20),
    min_instances: int = Field(..., description="The minimum number of instances to keep running. Must be between 0 and 5, and should be less than or equal to max_instances.", ge=0, le=5),
    model: str = Field(..., description="The full model identifier in the format owner/model-name (e.g., stability-ai/sdxl)."),
    name: str = Field(..., description="A unique name for this deployment within your organization. Used to identify and manage the deployment."),
    version: str = Field(..., description="The 64-character version ID of the model to deploy. This specifies the exact model version and weights to use."),
) -> dict[str, Any] | ToolResult:
    """Create a new deployment to run a specific model version on designated hardware with auto-scaling configuration. The deployment will be immediately available for inference requests."""

    # Construct request model with validation
    try:
        _request = _models.DeploymentsCreateRequest(
            body=_models.DeploymentsCreateRequestBody(hardware=hardware, max_instances=max_instances, min_instances=min_instances, model=model, name=name, version=version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_deployment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/deployments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_deployment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_deployment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_deployment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Deployment",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_deployment(
    deployment_owner: str = Field(..., description="The username or organization name that owns the deployment."),
    deployment_name: str = Field(..., description="The name of the deployment to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific deployment, including its current release configuration, hardware settings, and scaling parameters."""

    # Construct request model with validation
    try:
        _request = _models.DeploymentsGetRequest(
            path=_models.DeploymentsGetRequestPath(deployment_owner=deployment_owner, deployment_name=deployment_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_deployment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/deployments/{deployment_owner}/{deployment_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/deployments/{deployment_owner}/{deployment_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_deployment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_deployment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_deployment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Deployment",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_deployment(
    deployment_owner: str = Field(..., description="The username or organization name that owns the deployment."),
    deployment_name: str = Field(..., description="The name of the deployment to update."),
    hardware: str | None = Field(None, description="The hardware SKU to run the model on (e.g., gpu-t4). Available options can be retrieved from the hardware list endpoint."),
    max_instances: int | None = Field(None, description="The maximum number of instances for autoscaling, ranging from 0 to 20.", ge=0, le=20),
    min_instances: int | None = Field(None, description="The minimum number of instances to maintain, ranging from 0 to 5.", ge=0, le=5),
    version: str | None = Field(None, description="The model version ID to deploy. Use this to update the deployment to a different version of the model."),
) -> dict[str, Any] | ToolResult:
    """Modify an existing deployment's configuration, including hardware SKU, scaling limits, and model version. Each update increments the deployment's release number."""

    # Construct request model with validation
    try:
        _request = _models.DeploymentsUpdateRequest(
            path=_models.DeploymentsUpdateRequestPath(deployment_owner=deployment_owner, deployment_name=deployment_name),
            body=_models.DeploymentsUpdateRequestBody(hardware=hardware, max_instances=max_instances, min_instances=min_instances, version=version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_deployment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/deployments/{deployment_owner}/{deployment_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/deployments/{deployment_owner}/{deployment_name}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_deployment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_deployment", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_deployment",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Deployment",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_deployment(
    deployment_owner: str = Field(..., description="The username or organization name that owns the deployment being deleted."),
    deployment_name: str = Field(..., description="The name of the deployment to delete."),
) -> dict[str, Any] | ToolResult:
    """Delete a deployment that has been offline and unused for at least 15 minutes. The operation returns a 204 status code on successful deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeploymentsDeleteRequest(
            path=_models.DeploymentsDeleteRequestPath(deployment_owner=deployment_owner, deployment_name=deployment_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_deployment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/deployments/{deployment_owner}/{deployment_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/deployments/{deployment_owner}/{deployment_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_deployment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_deployment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_deployment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Deployment Prediction",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_deployment_prediction(
    deployment_owner: str = Field(..., description="The username or organization name that owns the deployment."),
    deployment_name: str = Field(..., description="The name of the deployment to run the prediction against."),
    input_: dict[str, Any] = Field(..., alias="input", description="A JSON object containing the model's input parameters. The required fields depend on the specific model running on the deployment. Files should be passed as HTTP URLs (for files >256KB or reusable files) or data URLs (for small files ≤256KB)."),
    prefer: str | None = Field(None, alias="Prefer", description="Set to `wait` or `wait=n` (where n is 1-60 seconds) to hold the request open and wait for the model to complete. Without this header, the prediction starts asynchronously and returns immediately.", pattern="^wait(=([1-9]|[1-9][0-9]|60))?$"),
    cancel_after: str | None = Field(None, alias="Cancel-After", description="Maximum duration the prediction can run before automatic cancellation, measured from creation time. Specify with optional unit suffix: `s` for seconds, `m` for minutes, `h` for hours (e.g., `5m`, `1h30m45s`). Minimum is 5 seconds; defaults to seconds if no unit is provided."),
    webhook: str | None = Field(None, description="An HTTPS URL that receives a POST webhook notification when the prediction updates or completes. The request body will contain the full prediction object. Replicate retries on network failures, so the endpoint must be idempotent."),
    webhook_events_filter: list[Literal["start", "output", "logs", "completed"]] | None = Field(None, description="An array of event types that trigger webhook requests: `start` (immediately), `output` (each new output), `logs` (each log line), or `completed` (terminal state). If omitted, defaults to sending on output and completion. Output and log events are throttled to at most once per 500ms."),
) -> dict[str, Any] | ToolResult:
    """Create a prediction by running a model on a deployment with specified inputs. The request can optionally wait synchronously for results (up to 60 seconds) or return immediately with a prediction ID for asynchronous polling."""

    # Construct request model with validation
    try:
        _request = _models.DeploymentsPredictionsCreateRequest(
            path=_models.DeploymentsPredictionsCreateRequestPath(deployment_owner=deployment_owner, deployment_name=deployment_name),
            header=_models.DeploymentsPredictionsCreateRequestHeader(prefer=prefer, cancel_after=cancel_after),
            body=_models.DeploymentsPredictionsCreateRequestBody(input_=input_, webhook=webhook, webhook_events_filter=webhook_events_filter)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_deployment_prediction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/deployments/{deployment_owner}/{deployment_name}/predictions", _request.path.model_dump(by_alias=True)) if _request.path else "/deployments/{deployment_owner}/{deployment_name}/predictions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_deployment_prediction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_deployment_prediction", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_deployment_prediction",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
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
    """Retrieve a paginated list of all files created by the user or organization associated with the API token, sorted with the most recent file first."""

    # Extract parameters for API call
    _http_path = "/files"
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
    title="Create File",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_file(
    content: str = Field(..., description="Base64-encoded file content for upload. The raw file content to upload. Provide the binary data of the file you want to store.", json_schema_extra={'format': 'byte'}),
    filename: str | None = Field(None, description="The name of the file being uploaded. Must be valid UTF-8 and not exceed 255 bytes in length.", max_length=255),
    metadata: dict[str, Any] | None = Field(None, description="Optional custom metadata to associate with the file as a JSON object. Defaults to an empty object if not provided."),
    type_: str | None = Field(None, alias="type", description="The MIME type of the file content (e.g., application/zip, application/json, image/png). Defaults to application/octet-stream if not specified."),
) -> dict[str, Any] | ToolResult:
    """Upload a file with its content and optional metadata. The file is stored and can be referenced by its returned ID for use in other operations."""

    # Construct request model with validation
    try:
        _request = _models.FilesCreateRequest(
            body=_models.FilesCreateRequestBody(content=content, filename=filename, metadata=metadata, type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/files"
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
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["content"],
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
async def get_file(file_id: str = Field(..., description="The unique identifier of the file to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed metadata and information about a specific file by its ID."""

    # Construct request model with validation
    try:
        _request = _models.FilesGetRequest(
            path=_models.FilesGetRequestPath(file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}"
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
    title="Delete File",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_file(file_id: str = Field(..., description="The unique identifier of the file to delete. This ID must correspond to an existing file in the system.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a file by its ID. Once deleted, the file resource will no longer be accessible and subsequent requests will return a 404 Not Found error."""

    # Construct request model with validation
    try:
        _request = _models.FilesDeleteRequest(
            path=_models.FilesDeleteRequestPath(file_id=file_id)
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


@mcp.tool(
    title="Get File Download",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_file_download(
    file_id: str = Field(..., description="The unique identifier of the file to download."),
    owner: str = Field(..., description="The username of the user or organization that owns and uploaded the file."),
    expiry: str = Field(..., description="Unix timestamp (seconds since epoch) indicating when this download URL expires and becomes invalid."),
    signature: str = Field(..., description="Base64-encoded HMAC-SHA256 signature authenticating the download request. Generated by hashing the string '{owner} {id} {expiry}' with your Files API signing secret."),
) -> dict[str, Any] | ToolResult:
    """Download a file using authenticated access credentials. Requires the file ID, owner information, and a cryptographically signed URL that includes an expiration timestamp."""

    _expiry = _parse_int(expiry)

    # Construct request model with validation
    try:
        _request = _models.FilesDownloadRequest(
            path=_models.FilesDownloadRequestPath(file_id=file_id),
            query=_models.FilesDownloadRequestQuery(owner=owner, expiry=_expiry, signature=signature)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_download: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{file_id}/download", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{file_id}/download"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_download")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_download", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_download",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Available Hardware",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_available_hardware() -> dict[str, Any] | ToolResult:
    """Retrieve a list of all available hardware accelerators and compute resources that can be used for running models on Replicate."""

    # Extract parameters for API call
    _http_path = "/hardware"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_available_hardware")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_available_hardware", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_available_hardware",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Models",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_models(
    sort_by: Literal["model_created_at", "latest_version_created_at"] | None = Field(None, description="Field to sort results by: either model creation date or the date of the model's latest version. Defaults to sorting by latest version creation date."),
    sort_direction: Literal["asc", "desc"] | None = Field(None, description="Sort direction for results: ascending (oldest first) or descending (newest first). Defaults to descending."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of publicly available models, optionally sorted by creation date or latest version update."""

    # Construct request model with validation
    try:
        _request = _models.ModelsListRequest(
            query=_models.ModelsListRequestQuery(sort_by=sort_by, sort_direction=sort_direction)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_models: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/models"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_models")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_models", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_models",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Model",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_model(
    hardware: str = Field(..., description="The hardware SKU required to run this model. Valid values can be retrieved from the hardware.list endpoint (e.g., 'cpu', 'gpu-t4')."),
    name: str = Field(..., description="The model's name, which must be unique within your user or organization account. Use lowercase alphanumeric characters and hyphens."),
    owner: str = Field(..., description="The username or organization name that will own this model. Must match the account associated with your API token."),
    visibility: Literal["public", "private"] = Field(..., description="Controls model visibility: 'public' allows anyone to view and run the model, while 'private' restricts access to account members only."),
    cover_image_url: str | None = Field(None, description="A URL pointing to an image file to use as the model's cover image on the Replicate platform."),
    description: str | None = Field(None, description="A brief description explaining what the model does and its primary use case."),
    github_url: str | None = Field(None, description="A URL to the model's source code repository on GitHub."),
    license_url: str | None = Field(None, description="A URL to the license governing the model's use and distribution."),
    paper_url: str | None = Field(None, description="A URL to the academic paper or research publication describing the model's methodology."),
) -> dict[str, Any] | ToolResult:
    """Create a new model in your account. Each account is limited to 1,000 models; for iterative improvements, create new versions of an existing model instead."""

    # Construct request model with validation
    try:
        _request = _models.ModelsCreateRequest(
            body=_models.ModelsCreateRequestBody(cover_image_url=cover_image_url, description=description, github_url=github_url, hardware=hardware, license_url=license_url, name=name, owner=owner, paper_url=paper_url, visibility=visibility)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_model: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/models"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_model")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_model", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_model",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Search Models",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def search_models(body: str = Field(..., description="The search query string to find matching models. Can include model names, descriptions, or keywords.")) -> dict[str, Any] | ToolResult:
    """Search for public models on Replicate using a text query. Returns a paginated list of models matching your search criteria."""

    # Construct request model with validation
    try:
        _request = _models.ModelsSearchRequest(
            body=_models.ModelsSearchRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_models: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/models"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "text/plain"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_models")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_models", "QUERY", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_models",
        method="QUERY",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="text/plain",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Model",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_model(
    model_owner: str = Field(..., description="The username or organization name that owns the model."),
    model_name: str = Field(..., description="The unique identifier of the model within the owner's namespace."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed metadata for a specific model, including its latest version, input/output schemas, and example prediction. Returns comprehensive information about the model's configuration, visibility, and usage statistics."""

    # Construct request model with validation
    try:
        _request = _models.ModelsGetRequest(
            path=_models.ModelsGetRequestPath(model_owner=model_owner, model_name=model_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_model: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/models/{model_owner}/{model_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/models/{model_owner}/{model_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_model")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_model", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_model",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Update Model Metadata",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_model_metadata(
    model_owner: str = Field(..., description="The username or organization name that owns the model."),
    model_name: str = Field(..., description="The name of the model to update."),
    description: str | None = Field(None, description="A brief description of the model's purpose and functionality."),
    github_url: str | None = Field(None, description="A URL pointing to the model's source code repository on GitHub."),
    license_url: str | None = Field(None, description="A URL pointing to the model's license document or license page."),
    paper_url: str | None = Field(None, description="A URL pointing to the research paper or academic publication associated with the model."),
    readme: str | None = Field(None, description="The README content in Markdown format, typically including usage instructions, examples, and documentation."),
    weights_url: str | None = Field(None, description="A URL pointing to the pre-trained model weights or model artifacts, such as on Hugging Face or similar hosting platforms."),
) -> dict[str, Any] | ToolResult:
    """Update metadata properties for an existing model, including description, documentation, and resource links. Only specified properties are updated; omitted properties remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.ModelsUpdateRequest(
            path=_models.ModelsUpdateRequestPath(model_owner=model_owner, model_name=model_name),
            body=_models.ModelsUpdateRequestBody(description=description, github_url=github_url, license_url=license_url, paper_url=paper_url, readme=readme, weights_url=weights_url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_model_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/models/{model_owner}/{model_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/models/{model_owner}/{model_name}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_model_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_model_metadata", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_model_metadata",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Model",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_model(
    model_owner: str = Field(..., description="The username or organization name that owns the model. You can only delete models you own."),
    model_name: str = Field(..., description="The name of the model to delete. The model must be private and have no versions remaining."),
) -> dict[str, Any] | ToolResult:
    """Permanently delete a private model you own. The model must have no versions associated with it—delete all versions before attempting to delete the model itself."""

    # Construct request model with validation
    try:
        _request = _models.ModelsDeleteRequest(
            path=_models.ModelsDeleteRequestPath(model_owner=model_owner, model_name=model_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_model: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/models/{model_owner}/{model_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/models/{model_owner}/{model_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_model")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_model", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_model",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Model Examples",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_model_examples(
    model_owner: str = Field(..., description="The username or organization name that owns the model."),
    model_name: str = Field(..., description="The name of the model."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all example predictions that were saved by the model author to demonstrate the model's capabilities. Use this to browse illustrative examples; for just the default example, use the get_model operation instead."""

    # Construct request model with validation
    try:
        _request = _models.ModelsExamplesListRequest(
            path=_models.ModelsExamplesListRequestPath(model_owner=model_owner, model_name=model_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_model_examples: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/models/{model_owner}/{model_name}/examples", _request.path.model_dump(by_alias=True)) if _request.path else "/models/{model_owner}/{model_name}/examples"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_model_examples")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_model_examples", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_model_examples",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Prediction for Official Model",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_prediction_for_official_model(
    model_owner: str = Field(..., description="The username or organization name that owns the official model."),
    model_name: str = Field(..., description="The name of the official model to run."),
    input_: dict[str, Any] = Field(..., alias="input", description="The model's input parameters as a JSON object. Structure depends on the specific model being run. Files should be passed as HTTP URLs (for files >256KB or reusable files) or data URLs (for files ≤256KB or one-time use)."),
    prefer: str | None = Field(None, alias="Prefer", description="Enable synchronous mode by setting to `wait` or `wait=n` where n is the number of seconds (1-60) to wait for the model to finish. If omitted, the request returns immediately.", pattern="^wait(=([1-9]|[1-9][0-9]|60))?$"),
    cancel_after: str | None = Field(None, alias="Cancel-After", description="Maximum duration the prediction can run before automatic cancellation, measured from creation time. Specify as a number with optional unit suffix: `s` for seconds, `m` for minutes, `h` for hours (e.g., `5m`, `1h30m45s`). Minimum is 5 seconds; defaults to seconds if no unit is provided."),
    webhook: str | None = Field(None, description="An HTTPS URL that receives a POST webhook notification when the prediction updates or completes. The request body matches the prediction's full state. Replicate retries on network failures, so the endpoint must be idempotent."),
    webhook_events_filter: list[Literal["start", "output", "logs", "completed"]] | None = Field(None, description="Filter which events trigger webhook requests: `start` (immediately), `output` (each generation), `logs` (each log line), or `completed` (terminal state). Output and logs events are throttled to at most once per 500ms; start and completed events are always sent."),
) -> dict[str, Any] | ToolResult:
    """Create a prediction by running an official model. The request can optionally wait synchronously for up to 60 seconds for the model to complete, or return immediately with a starting status for asynchronous polling."""

    # Construct request model with validation
    try:
        _request = _models.ModelsPredictionsCreateRequest(
            path=_models.ModelsPredictionsCreateRequestPath(model_owner=model_owner, model_name=model_name),
            header=_models.ModelsPredictionsCreateRequestHeader(prefer=prefer, cancel_after=cancel_after),
            body=_models.ModelsPredictionsCreateRequestBody(input_=input_, webhook=webhook, webhook_events_filter=webhook_events_filter)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_prediction_for_official_model: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/models/{model_owner}/{model_name}/predictions", _request.path.model_dump(by_alias=True)) if _request.path else "/models/{model_owner}/{model_name}/predictions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_prediction_for_official_model")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_prediction_for_official_model", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_prediction_for_official_model",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Model Readme",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_model_readme(
    model_owner: str = Field(..., description="The username or organization name that owns the model."),
    model_name: str = Field(..., description="The name of the model to retrieve documentation for."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the README documentation for a specific model. Returns the README content as plain text in Markdown format."""

    # Construct request model with validation
    try:
        _request = _models.ModelsReadmeGetRequest(
            path=_models.ModelsReadmeGetRequestPath(model_owner=model_owner, model_name=model_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_model_readme: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/models/{model_owner}/{model_name}/readme", _request.path.model_dump(by_alias=True)) if _request.path else "/models/{model_owner}/{model_name}/readme"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "text/plain"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_model_readme")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_model_readme", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_model_readme",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Model Versions",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_model_versions(
    model_owner: str = Field(..., description="The username or organization name that owns the model. This identifies the model's owner in the Replicate registry."),
    model_name: str = Field(..., description="The name of the model. Combined with the model owner, this uniquely identifies which model's versions to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all versions of a model owned by a specific user or organization, sorted with the most recent version first. Returns paginated results including version metadata and OpenAPI schemas."""

    # Construct request model with validation
    try:
        _request = _models.ModelsVersionsListRequest(
            path=_models.ModelsVersionsListRequestPath(model_owner=model_owner, model_name=model_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_model_versions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/models/{model_owner}/{model_name}/versions", _request.path.model_dump(by_alias=True)) if _request.path else "/models/{model_owner}/{model_name}/versions"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_model_versions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_model_versions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_model_versions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Model Version",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_model_version(
    model_owner: str = Field(..., description="The username or organization name that owns the model."),
    model_name: str = Field(..., description="The name of the model to retrieve version information for."),
    version_id: str = Field(..., description="The unique identifier of the specific model version to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed metadata and schema information for a specific version of a model, including its OpenAPI schema that describes the model's inputs and outputs."""

    # Construct request model with validation
    try:
        _request = _models.ModelsVersionsGetRequest(
            path=_models.ModelsVersionsGetRequestPath(model_owner=model_owner, model_name=model_name, version_id=version_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_model_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/models/{model_owner}/{model_name}/versions/{version_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/models/{model_owner}/{model_name}/versions/{version_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_model_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_model_version", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_model_version",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Delete Model Version",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_model_version(
    model_owner: str = Field(..., description="The username or organization name that owns the model. You must be the owner to delete versions."),
    model_name: str = Field(..., description="The name of the model containing the version to delete."),
    version_id: str = Field(..., description="The unique identifier of the model version to delete. The version cannot be deleted if it's in use by deployments, fine-tuning jobs, other model versions, or has predictions run by other users."),
) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific model version and all associated predictions and output files. Deletion is asynchronous and may take several minutes to complete."""

    # Construct request model with validation
    try:
        _request = _models.ModelsVersionsDeleteRequest(
            path=_models.ModelsVersionsDeleteRequestPath(model_owner=model_owner, model_name=model_name, version_id=version_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_model_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/models/{model_owner}/{model_name}/versions/{version_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/models/{model_owner}/{model_name}/versions/{version_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_model_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_model_version", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_model_version",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Training",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_training(
    model_owner: str = Field(..., description="The username or organization name that owns the model being trained."),
    model_name: str = Field(..., description="The name of the model to train."),
    version_id: str = Field(..., description="The unique identifier of the model version to use as the base for training."),
    destination: str = Field(..., description="The target model location in format `owner/name`. Must be an existing model owned by the requesting user or organization."),
    input_: dict[str, Any] = Field(..., alias="input", description="An object containing input parameters for the model's training function. Structure depends on the specific model's training requirements."),
    webhook: str | None = Field(None, description="An HTTPS URL that will receive a POST request when the training completes. The request body will contain the final training status. Replicate will retry on network failures, so the endpoint should be idempotent."),
    webhook_events_filter: list[Literal["start", "output", "logs", "completed"]] | None = Field(None, description="An array of event types that trigger webhook requests. Valid events are `start` (immediately when training begins), `output` (when training generates outputs), `logs` (when log output is generated), and `completed` (when training reaches a terminal state). If omitted, defaults to sending on outputs and completion."),
) -> dict[str, Any] | ToolResult:
    """Start a new training job for a model version. The training will create a new version of the model at the specified destination when complete. Since training can take several minutes or longer, use webhooks or polling to track completion."""

    # Construct request model with validation
    try:
        _request = _models.TrainingsCreateRequest(
            path=_models.TrainingsCreateRequestPath(model_owner=model_owner, model_name=model_name, version_id=version_id),
            body=_models.TrainingsCreateRequestBody(destination=destination, input_=input_, webhook=webhook, webhook_events_filter=webhook_events_filter)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_training: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/models/{model_owner}/{model_name}/versions/{version_id}/trainings", _request.path.model_dump(by_alias=True)) if _request.path else "/models/{model_owner}/{model_name}/versions/{version_id}/trainings"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_training")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_training", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_training",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Predictions",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_predictions(
    created_after: str | None = Field(None, description="Filter to include only predictions created at or after this date-time. Specify in ISO 8601 format (e.g., 2025-01-01T00:00:00Z)."),
    created_before: str | None = Field(None, description="Filter to include only predictions created before this date-time. Specify in ISO 8601 format (e.g., 2025-02-01T00:00:00Z)."),
    source: Literal["web"] | None = Field(None, description="Filter predictions by creation source. Use 'web' to show only web-created predictions (limited to the last 14 days). Omit this parameter to include predictions from both API and web sources."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of all predictions created by your user or organization, including those from both API and web sources. Results are sorted with the most recent prediction first, returning up to 100 records per page."""

    # Construct request model with validation
    try:
        _request = _models.PredictionsListRequest(
            query=_models.PredictionsListRequestQuery(created_after=created_after, created_before=created_before, source=source)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_predictions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/predictions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_predictions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_predictions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_predictions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Create Prediction",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_prediction(
    input_: dict[str, Any] = Field(..., alias="input", description="Required JSON object containing the model's input parameters. Structure depends on the specific model version being run. Files should be passed as HTTP URLs (for files >256KB or reusable files) or data URLs (for small files ≤256KB)."),
    version: str = Field(..., description="Required identifier for the model or version to execute. Accepts three formats: `owner/model` for official models, `owner/model:version_id` for specific versions, or just the 64-character `version_id` alone."),
    prefer: str | None = Field(None, alias="Prefer", description="Enable synchronous mode by setting to `wait` or `wait=n` where n is 1-60 seconds. When set, the request will block and wait for the model to complete within the specified timeout before returning results.", pattern="^wait(=([1-9]|[1-9][0-9]|60))?$"),
    cancel_after: str | None = Field(None, alias="Cancel-After", description="Set a maximum runtime duration for the prediction before automatic cancellation. Accepts durations with optional unit suffixes: seconds (s), minutes (m), or hours (h). Combine units for precision (e.g., `1h30m45s`). Minimum allowed duration is 5 seconds."),
    webhook: str | None = Field(None, description="HTTPS URL for receiving webhook notifications when the prediction updates or completes. Replicate will POST the prediction state to this URL and may retry on network failures, so the endpoint should be idempotent."),
    webhook_events_filter: list[Literal["start", "output", "logs", "completed"]] | None = Field(None, description="Array of event types that trigger webhook requests: `start` (immediately), `output` (each generation), `logs` (log output), or `completed` (terminal state). Omit to receive all events. Output and logs events are throttled to at most once per 500ms."),
) -> dict[str, Any] | ToolResult:
    """Submit a prediction request to run a model with specified inputs. The request can optionally wait synchronously for results (up to 60 seconds) or return immediately with a prediction ID for asynchronous polling."""

    # Construct request model with validation
    try:
        _request = _models.PredictionsCreateRequest(
            header=_models.PredictionsCreateRequestHeader(prefer=prefer, cancel_after=cancel_after),
            body=_models.PredictionsCreateRequestBody(input_=input_, version=version, webhook=webhook, webhook_events_filter=webhook_events_filter)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_prediction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/predictions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_prediction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_prediction", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_prediction",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Prediction",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_prediction(prediction_id: str = Field(..., description="The unique identifier of the prediction to retrieve. This ID is returned when a prediction is created and can be used to poll for results or access the prediction details.")) -> dict[str, Any] | ToolResult:
    """Retrieve the current state and results of a prediction, including its status, output, logs, and performance metrics."""

    # Construct request model with validation
    try:
        _request = _models.PredictionsGetRequest(
            path=_models.PredictionsGetRequestPath(prediction_id=prediction_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_prediction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/predictions/{prediction_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/predictions/{prediction_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_prediction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_prediction", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_prediction",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Cancel Prediction",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def cancel_prediction(prediction_id: str = Field(..., description="The unique identifier of the prediction to cancel. This must be a valid prediction ID that is currently in a running or queued state.")) -> dict[str, Any] | ToolResult:
    """Cancel an in-progress prediction. This stops the model execution and prevents further processing of the prediction."""

    # Construct request model with validation
    try:
        _request = _models.PredictionsCancelRequest(
            path=_models.PredictionsCancelRequestPath(prediction_id=prediction_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for cancel_prediction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/predictions/{prediction_id}/cancel", _request.path.model_dump(by_alias=True)) if _request.path else "/predictions/{prediction_id}/cancel"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("cancel_prediction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("cancel_prediction", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="cancel_prediction",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Search Models, Collections, and Docs",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_models_collections_and_docs(
    query: str = Field(..., description="The text query to search for models, collections, and docs. Use keywords or phrases relevant to your search intent (e.g., 'nano banana')."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Must be between 1 and 50; defaults to 20 if not specified.", ge=1, le=50),
) -> dict[str, Any] | ToolResult:
    """Search across public models, collections, and documentation using a text query. Results include detailed metadata such as AI-generated descriptions, tags, and relevance scores to help identify the most suitable resources."""

    # Construct request model with validation
    try:
        _request = _models.SearchRequest(
            query=_models.SearchRequestQuery(query=query, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_models_collections_and_docs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_models_collections_and_docs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_models_collections_and_docs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_models_collections_and_docs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="List Trainings",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_trainings() -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of all trainings created by your user account or organization. Results include trainings from both API and web sources, sorted by most recent first, with 100 records per page."""

    # Extract parameters for API call
    _http_path = "/trainings"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_trainings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_trainings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_trainings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Training",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_training(training_id: str = Field(..., description="The unique identifier of the training job to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve the current state and results of a training job, including status, metrics, logs, and output artifacts."""

    # Construct request model with validation
    try:
        _request = _models.TrainingsGetRequest(
            path=_models.TrainingsGetRequestPath(training_id=training_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_training: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/trainings/{training_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/trainings/{training_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_training")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_training", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_training",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Cancel Training",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def cancel_training(training_id: str = Field(..., description="The unique identifier of the training session to cancel.")) -> dict[str, Any] | ToolResult:
    """Cancel an active or scheduled training session. Once cancelled, the training will no longer be available and participants will be notified of the cancellation."""

    # Construct request model with validation
    try:
        _request = _models.TrainingsCancelRequest(
            path=_models.TrainingsCancelRequestPath(training_id=training_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for cancel_training: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/trainings/{training_id}/cancel", _request.path.model_dump(by_alias=True)) if _request.path else "/trainings/{training_id}/cancel"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("cancel_training")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("cancel_training", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="cancel_training",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool(
    title="Get Default Webhook Secret",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_default_webhook_secret() -> dict[str, Any] | ToolResult:
    """Retrieve the signing secret for the default webhook endpoint. Use this secret to verify that incoming webhook requests are authentically from Replicate."""

    # Extract parameters for API call
    _http_path = "/webhooks/default/secret"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_default_webhook_secret")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_default_webhook_secret", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_default_webhook_secret",
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
        print("  python replicate_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Replicate MCP Server")

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
    logger.info("Starting Replicate MCP Server")
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

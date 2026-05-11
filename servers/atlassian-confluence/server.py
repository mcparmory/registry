#!/usr/bin/env python3
"""
Atlassian Confluence MCP Server

API Info:
- Terms of Service: https://atlassian.com/terms/

Generated: 2026-05-11 23:06:48 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import collections
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

# Server variables (from OpenAPI spec, overridable via SERVER_* env vars)
_SERVER_VARS = {
    "your_domain": os.getenv("SERVER_YOUR_DOMAIN", ""),
}
BASE_URL = os.getenv("BASE_URL", "https://{your_domain}.atlassian.net/wiki".format_map(collections.defaultdict(str, _SERVER_VARS)))
SERVER_NAME = "Atlassian Confluence"
SERVER_VERSION = "1.0.8"

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

def build_cqlcontext(cqlcontext_space_key: str | None = None, cqlcontext_content_id: str | None = None, cqlcontext_content_statuses: list[str] | None = None) -> dict | None:
    """Helper function for parameter transformation"""
    if cqlcontext_space_key is None and cqlcontext_content_id is None and cqlcontext_content_statuses is None:
        return None

    context = {}
    if cqlcontext_space_key is not None:
        context['spaceKey'] = cqlcontext_space_key
    if cqlcontext_content_id is not None:
        context['contentId'] = cqlcontext_content_id
    if cqlcontext_content_statuses is not None:
        context['contentStatuses'] = cqlcontext_content_statuses

    return context if context else None

def build_cql_query(content_type: str | None = None, space_key: str | None = None, text_search: str | None = None, created_after: str | None = None, created_before: str | None = None, modified_after: str | None = None, modified_before: str | None = None, status: str | None = None, label: str | None = None, ancestor_id: str | None = None) -> str | None:
    """Helper function for parameter transformation"""
    if all(v is None for v in [content_type, space_key, text_search, created_after, created_before, modified_after, modified_before, status, label, ancestor_id]):
        return None

    clauses = []

    if content_type is not None:
        clauses.append(f'type={content_type}')

    if space_key is not None:
        clauses.append(f'space={space_key}')

    if text_search is not None:
        escaped_text = text_search.replace('"', '\\"')
        clauses.append(f'text ~ "{escaped_text}"')

    if created_after is not None:
        clauses.append(f'created >= "{created_after}"')

    if created_before is not None:
        clauses.append(f'created <= "{created_before}"')

    if modified_after is not None:
        clauses.append(f'lastModified >= "{modified_after}"')

    if modified_before is not None:
        clauses.append(f'lastModified <= "{modified_before}"')

    if status is not None:
        clauses.append(f'status={status}')

    if label is not None:
        escaped_label = label.replace('"', '\\"')
        clauses.append(f'label = "{escaped_label}"')

    if ancestor_id is not None:
        clauses.append(f'ancestor={ancestor_id}')

    return ' AND '.join(clauses)

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
    'oAuthDefinitions',
    'basicAuth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["oAuthDefinitions"] = _auth.OAuth2Auth()
    logging.info("Authentication configured: oAuthDefinitions")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for oAuthDefinitions not configured: {error_msg}")
    _auth_handlers["oAuthDefinitions"] = None
try:
    _auth_handlers["basicAuth"] = _auth.BasicAuth(env_var_username="BASIC_AUTH_USERNAME", env_var_password="BASIC_AUTH_PASSWORD")
    logging.info("Authentication configured: basicAuth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for basicAuth not configured: {error_msg}")
    _auth_handlers["basicAuth"] = None

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

mcp = FastMCP("Atlassian Confluence", middleware=[_JsonCoercionMiddleware()])

# Tags: Audit
@mcp.tool(
    title="List Audit Records",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_audit_records(
    start_date: str | None = Field(None, alias="startDate", description="Filter results to records on or after this date. Specify as epoch time in milliseconds."),
    end_date: str | None = Field(None, alias="endDate", description="Filter results to records on or before this date. Specify as epoch time in milliseconds."),
    search_string: str | None = Field(None, alias="searchString", description="Filter results to records with string property values matching this search term."),
    limit: str | None = Field(None, description="Maximum number of records to return per page. System limits may restrict the actual number returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieve audit log records for administrative events such as space exports, group membership changes, and app installations. Requires Confluence Administrator global permission."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetAuditRecordsRequest(
            query=_models.GetAuditRecordsRequestQuery(start_date=start_date, end_date=end_date, search_string=search_string, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_audit_records: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/audit"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_audit_records")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_audit_records", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_audit_records",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content
@mcp.tool(
    title="Archive Pages",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def archive_pages(pages: list[_models.ArchivePagesBodyPagesItem] | None = Field(None, description="List of content IDs identifying the pages to archive. Each ID must resolve to a page object that is not already archived. Pages can belong to different spaces. Requires 'Archive' permission in each page's corresponding space.")) -> dict[str, Any] | ToolResult:
    """Archives a list of pages by their content IDs. The archival process is asynchronous; use the /longtask/<taskId> endpoint to monitor progress."""

    # Construct request model with validation
    try:
        _request = _models.ArchivePagesRequest(
            body=_models.ArchivePagesRequestBody(pages=pages)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for archive_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/content/archive"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("archive_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("archive_pages", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="archive_pages",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Content
@mcp.tool(
    title="Publish Blueprint Draft",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def publish_blueprint_draft(
    draft_id: str = Field(..., alias="draftId", description="The unique identifier of the draft page created from a blueprint. This ID can be found in the page URL when viewing the draft in Confluence."),
    number: str = Field(..., description="The version number of the content being published. Set this to 1 for new drafts."),
    title: str = Field(..., description="The title of the published page. If you do not want to change the title, use the current draft title. Maximum length is 255 characters.", max_length=255),
    type_: Literal["page"] = Field(..., alias="type", description="The content type being published. Must be set to 'page' for blueprint drafts."),
    key: str = Field(..., description="The space key where the published page will be created. This identifies the target Confluence space."),
    status: str | None = Field(None, description="The current status of the draft being published. Defaults to 'draft' and typically does not need to be specified."),
    status2: Literal["current"] | None = Field(None, alias="status", description="The target status for the published content. Set to 'current' to publish the draft as a live page, or omit to use the default."),
) -> dict[str, Any] | ToolResult:
    """Publishes a legacy blueprint draft page to make it live in Confluence. Requires permission to view the draft and 'Add' permission for the target space."""

    _number = _parse_int(number)

    # Construct request model with validation
    try:
        _request = _models.PublishLegacyDraftRequest(
            path=_models.PublishLegacyDraftRequestPath(draft_id=draft_id),
            query=_models.PublishLegacyDraftRequestQuery(status=status),
            body=_models.PublishLegacyDraftRequestBody(status=status2, title=title, type_=type_,
                version=_models.PublishLegacyDraftRequestBodyVersion(number=_number),
                space=_models.PublishLegacyDraftRequestBodySpace(key=key))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for publish_blueprint_draft: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/blueprint/instance/{draftId}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/blueprint/instance/{draftId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("publish_blueprint_draft")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("publish_blueprint_draft", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="publish_blueprint_draft",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Content
@mcp.tool(
    title="Publish Blueprint Draft Shared",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def publish_blueprint_draft_shared(
    draft_id: str = Field(..., alias="draftId", description="The unique identifier of the draft page created from a blueprint. This ID can be found in the Confluence application by opening the draft page and checking its URL."),
    number: str = Field(..., description="The version number of the content being published. Set this to 1 for new draft publications."),
    title: str = Field(..., description="The title of the published page. If you do not want to change the title, use the current title of the draft.", max_length=255),
    type_: Literal["page"] = Field(..., alias="type", description="The content type being published. Must be set to 'page' for blueprint-based content."),
    key: str = Field(..., description="The key identifier of the space where the content will be published."),
    status: str | None = Field(None, description="The current status of the draft content. This should remain set to 'draft' and typically does not need to be modified."),
    status2: Literal["current"] | None = Field(None, alias="status", description="The target status for the published content. Set to 'current' to publish the draft as active content."),
) -> dict[str, Any] | ToolResult:
    """Publishes a shared draft page created from a blueprint template. Requires permission to view the draft and 'Add' permission for the target space."""

    _number = _parse_int(number)

    # Construct request model with validation
    try:
        _request = _models.PublishSharedDraftRequest(
            path=_models.PublishSharedDraftRequestPath(draft_id=draft_id),
            query=_models.PublishSharedDraftRequestQuery(status=status),
            body=_models.PublishSharedDraftRequestBody(status=status2, title=title, type_=type_,
                version=_models.PublishSharedDraftRequestBodyVersion(number=_number),
                space=_models.PublishSharedDraftRequestBodySpace(key=key))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for publish_blueprint_draft_shared: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/blueprint/instance/{draftId}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/blueprint/instance/{draftId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("publish_blueprint_draft_shared")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("publish_blueprint_draft_shared", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="publish_blueprint_draft_shared",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Content
@mcp.tool(
    title="Search Content",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_content(
    cql: str = Field(..., description="A CQL query string that specifies the search criteria. CQL supports filtering by content type, space, author, date, and other properties. Refer to Advanced searching using CQL documentation for syntax and available operators."),
    limit: str | None = Field(None, description="The maximum number of content items to return in a single response page. When using expand with body.export_view or body.styled_view, this is restricted to a maximum of 25."),
    cqlcontext_space_key: str | None = Field(None, description="Key of the space to search against. Optional."),
    cqlcontext_content_id: str | None = Field(None, description="ID of the content to search against. Optional. Must be in the space specified by cqlcontext_space_key."),
    cqlcontext_content_statuses: list[str] | None = Field(None, description="Content statuses to search against. Optional. Array of status strings (e.g., ['current', 'archived'])."),
) -> dict[str, Any] | ToolResult:
    """Search Confluence content using CQL (Confluence Query Language) to find pages, blog posts, and other content matching your query criteria. Results are paginated and support cursor-based navigation for retrieving additional pages."""

    # Call helper functions
    cqlcontext = build_cqlcontext(cqlcontext_space_key, cqlcontext_content_id, cqlcontext_content_statuses)

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.SearchContentByCqlRequest(
            query=_models.SearchContentByCqlRequestQuery(cql=cql, limit=_limit, cqlcontext=cqlcontext)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/content/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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

# Tags: Experimental
@mcp.tool(
    title="Delete Page Tree",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_page_tree(id_: str = Field(..., alias="id", description="The content ID of the root page whose entire tree (including all descendant pages) should be deleted.")) -> dict[str, Any] | ToolResult:
    """Asynchronously delete a page and all its descendants by moving them to the space's trash. Only supported for pages with current status. Returns a task ID to track the deletion progress."""

    # Construct request model with validation
    try:
        _request = _models.DeletePageTreeRequest(
            path=_models.DeletePageTreeRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_page_tree: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/pageTree", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/pageTree"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_page_tree")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_page_tree", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_page_tree",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content - children and descendants
@mcp.tool(
    title="Move Page",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def move_page(
    page_id: str = Field(..., alias="pageId", description="The ID of the page to be moved."),
    position: Literal["before", "after", "append"] = Field(..., description="The position to move the page relative to the target page. Use 'before' or 'after' to place the page as a sibling, or 'append' to make it a child of the target."),
    target_id: str = Field(..., alias="targetId", description="The ID of the target page that serves as the reference point for the move operation. Avoid using 'before' or 'after' positions when the target is a top-level page, as this can create pages that are difficult to locate in the UI."),
) -> dict[str, Any] | ToolResult:
    """Move a page to a new location in the wiki hierarchy relative to a target page. Supports positioning before, after, or as a child of the target page."""

    # Construct request model with validation
    try:
        _request = _models.MovePageRequest(
            path=_models.MovePageRequestPath(page_id=page_id, position=position, target_id=target_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for move_page: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{pageId}/move/{position}/{targetId}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{pageId}/move/{position}/{targetId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("move_page")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("move_page", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="move_page",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content - attachments
@mcp.tool(
    title="Add Attachment",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_attachment(
    id_: str = Field(..., alias="id", description="The ID of the content to which the attachment will be added."),
    file_: str = Field(..., alias="file", description="Base64-encoded file content for upload. The file to attach. The file will be uploaded as binary data.", json_schema_extra={'format': 'byte'}),
    minor_edit: str = Field(..., alias="minorEdit", description="Base64-encoded file content for upload. Set to 'true' to suppress notification emails and activity stream updates when the attachment is added. Set to 'false' or omit to generate notifications.", json_schema_extra={'format': 'byte'}),
) -> dict[str, Any] | ToolResult:
    """Adds a new attachment to a piece of content. To update an existing attachment instead, use the create or update attachments operation. Requires X-Atlassian-Token: nocheck header to prevent XSRF attacks."""

    # Construct request model with validation
    try:
        _request = _models.CreateAttachmentRequest(
            path=_models.CreateAttachmentRequestPath(id_=id_),
            body=_models.CreateAttachmentRequestBody(file_=file_, minor_edit=minor_edit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/child/attachment", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/child/attachment"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_attachment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_attachment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file", "minorEdit"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Content - attachments
@mcp.tool(
    title="Upload Attachment",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def upload_attachment(
    id_: str = Field(..., alias="id", description="The ID of the content to attach the file to."),
    file_: str = Field(..., alias="file", description="Base64-encoded file content for upload. The file to upload as an attachment. The file will be sent as binary data in the multipart request.", json_schema_extra={'format': 'byte'}),
    minor_edit: str = Field(..., alias="minorEdit", description="Base64-encoded file content for upload. Set to 'true' to suppress notification emails and activity stream updates when the attachment is added or updated.", json_schema_extra={'format': 'byte'}),
) -> dict[str, Any] | ToolResult:
    """Uploads a new attachment to content or creates a new version of an existing attachment. Supports optional minor edit mode to suppress notifications."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrUpdateAttachmentsRequest(
            path=_models.CreateOrUpdateAttachmentsRequestPath(id_=id_),
            body=_models.CreateOrUpdateAttachmentsRequestBody(file_=file_, minor_edit=minor_edit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/child/attachment", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/child/attachment"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_attachment", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_attachment",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file", "minorEdit"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Content - attachments
@mcp.tool(
    title="Replace Attachment Data",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def replace_attachment_data(
    id_: str = Field(..., alias="id", description="The ID of the content that contains the attachment to be updated."),
    attachment_id: str = Field(..., alias="attachmentId", description="The ID of the attachment whose data will be replaced."),
    file_: str = Field(..., alias="file", description="Base64-encoded file content for upload. The binary file data to upload as the new attachment content.", json_schema_extra={'format': 'byte'}),
    minor_edit: str = Field(..., alias="minorEdit", description="Base64-encoded file content for upload. Set to 'true' to suppress notification emails and activity stream updates when the attachment is updated.", json_schema_extra={'format': 'byte'}),
) -> dict[str, Any] | ToolResult:
    """Replace the binary data of an attachment by its ID. Optionally include a comment and mark as a minor edit to suppress notifications."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAttachmentDataRequest(
            path=_models.UpdateAttachmentDataRequestPath(id_=id_, attachment_id=attachment_id),
            body=_models.UpdateAttachmentDataRequestBody(file_=file_, minor_edit=minor_edit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for replace_attachment_data: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/child/attachment/{attachmentId}/data", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/child/attachment/{attachmentId}/data"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("replace_attachment_data")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("replace_attachment_data", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="replace_attachment_data",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file", "minorEdit"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Content - attachments
@mcp.tool(
    title="Download Attachment",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def download_attachment(
    id_: str = Field(..., alias="id", description="The unique identifier of the content object to which the attachment is associated."),
    attachment_id: str = Field(..., alias="attachmentId", description="The unique identifier of the attachment to download."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a download URI for an attachment associated with a piece of content. The client is redirected to a URL that serves the attachment's binary data."""

    # Construct request model with validation
    try:
        _request = _models.DownloadAttatchmentRequest(
            path=_models.DownloadAttatchmentRequestPath(id_=id_, attachment_id=attachment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for download_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/child/attachment/{attachmentId}/download", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/child/attachment/{attachmentId}/download"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("download_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("download_attachment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="download_attachment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content - macro body
@mcp.tool(
    title="Get Macro Body by ID",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_macro_body(
    id_: str = Field(..., alias="id", description="The ID of the content that contains the macro."),
    version: str = Field(..., description="The version of the content containing the macro. Use 0 to retrieve the macro body from the latest content version."),
    macro_id: str = Field(..., alias="macroId", description="The ID of the macro to retrieve. This is typically a UUID generated by Confluence (e.g., 50884bd9-0cb8-41d5-98be-f80943c14f96) or the local ID of a Forge macro node. Query the content with expanded storage format body to locate the macro ID if unknown."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the body of a macro in storage format, including macro name, body content, and parameters. Returns macro metadata for the specified macro ID within a particular content version."""

    _version = _parse_int(version)

    # Construct request model with validation
    try:
        _request = _models.GetMacroBodyByMacroIdRequest(
            path=_models.GetMacroBodyByMacroIdRequestPath(id_=id_, version=_version, macro_id=macro_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_macro_body: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/history/{version}/macro/id/{macroId}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/history/{version}/macro/id/{macroId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_macro_body")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_macro_body", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_macro_body",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content - macro body
@mcp.tool(
    title="Get and Convert Macro Body by ID",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_macro_body_converted(
    id_: str = Field(..., alias="id", description="The ID of the content that contains the macro."),
    version: str = Field(..., description="The version of the content containing the macro. Use 0 to retrieve the macro body from the latest content version."),
    macro_id: str = Field(..., alias="macroId", description="The ID of the macro to retrieve. For Forge macros, this is the local ID of the ADF node. For other macros, this is a UUID-format identifier generated by Confluence. Query the content with expanded body storage format to find the macro ID if needed."),
    to: str = Field(..., description="The content representation format to return the macro body in."),
    embedded_content_render: Literal["current", "version-at-save"] | None = Field(None, alias="embeddedContentRender", description="Controls how embedded content (such as attachments) is rendered. Use 'current' to render with the latest version, or 'version-at-save' to render with the version that existed at the time of save."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the body of a macro in a specified content representation format. Returns macro metadata including name, body, and parameters for a given macro ID and content version."""

    _version = _parse_int(version)

    # Construct request model with validation
    try:
        _request = _models.GetAndConvertMacroBodyByMacroIdRequest(
            path=_models.GetAndConvertMacroBodyByMacroIdRequestPath(id_=id_, version=_version, macro_id=macro_id, to=to),
            query=_models.GetAndConvertMacroBodyByMacroIdRequestQuery(embedded_content_render=embedded_content_render)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_macro_body_converted: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/history/{version}/macro/id/{macroId}/convert/{to}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/history/{version}/macro/id/{macroId}/convert/{to}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_macro_body_converted")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_macro_body_converted", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_macro_body_converted",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content - macro body
@mcp.tool(
    title="Convert Macro Body Asynchronously",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def convert_macro_body_async(
    id_: str = Field(..., alias="id", description="The ID of the content that contains the macro to be converted."),
    version: str = Field(..., description="The version of the content containing the macro. Use 0 to retrieve the macro from the latest content version."),
    macro_id: str = Field(..., alias="macroId", description="The ID of the macro to convert. For Forge macros, this is the local ID from the ADF node parameters. For other macros, this is the randomly generated ID persisted across versions (format: UUID-like string)."),
    to: Literal["export_view", "view", "styled_view"] = Field(..., description="The target content representation format for the macro conversion."),
    allow_cache: bool | None = Field(None, alias="allowCache", description="Whether to cache and reuse conversion results for identical requests. When enabled, identical requests return the same task ID and reuse cached results if available."),
    embedded_content_render: Literal["current", "version-at-save"] | None = Field(None, alias="embeddedContentRender", description="Determines which version of embedded content (such as attachments) to render: the current version or the version at the time of save."),
) -> dict[str, Any] | ToolResult:
    """Asynchronously converts a macro body to a specified content representation format. Returns a task ID that can be used to retrieve the conversion result, which remains available for 5 minutes after completion."""

    _version = _parse_int(version)

    # Construct request model with validation
    try:
        _request = _models.GetAndAsyncConvertMacroBodyByMacroIdRequest(
            path=_models.GetAndAsyncConvertMacroBodyByMacroIdRequestPath(id_=id_, version=_version, macro_id=macro_id, to=to),
            query=_models.GetAndAsyncConvertMacroBodyByMacroIdRequestQuery(allow_cache=allow_cache, embedded_content_render=embedded_content_render)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_macro_body_async: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/history/{version}/macro/id/{macroId}/convert/async/{to}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/history/{version}/macro/id/{macroId}/convert/async/{to}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_macro_body_async")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_macro_body_async", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_macro_body_async",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content labels
@mcp.tool(
    title="Add Labels to Content",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_labels_to_content(
    id_: str = Field(..., alias="id", description="The unique identifier of the content item to which labels will be added."),
    body: _models.LabelCreateArray | _models.LabelCreate = Field(..., description="A collection of labels to add to the content. Each label is a key-value pair where the key identifies the label namespace and the value specifies the label name."),
) -> dict[str, Any] | ToolResult:
    """Adds one or more labels to existing content without removing previously assigned labels. This operation is additive and preserves all existing labels on the content."""

    # Construct request model with validation
    try:
        _request = _models.AddLabelsToContentRequest(
            path=_models.AddLabelsToContentRequestPath(id_=id_),
            body=_models.AddLabelsToContentRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_labels_to_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/label", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/label"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_labels_to_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_labels_to_content", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_labels_to_content",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Content labels
@mcp.tool(
    title="Remove Label from Content",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_label_from_content(
    id_: str = Field(..., alias="id", description="The unique identifier of the content from which the label will be removed."),
    name: str = Field(..., description="The name of the label to remove from the content. This parameter supports label names containing forward slashes."),
) -> dict[str, Any] | ToolResult:
    """Remove a label from content by specifying the label name as a query parameter. Use this method when the label name contains forward slashes, which are not supported in the path-based removal endpoint."""

    # Construct request model with validation
    try:
        _request = _models.RemoveLabelFromContentUsingQueryParameterRequest(
            path=_models.RemoveLabelFromContentUsingQueryParameterRequestPath(id_=id_),
            query=_models.RemoveLabelFromContentUsingQueryParameterRequestQuery(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_label_from_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/label", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/label"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_label_from_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_label_from_content", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_label_from_content",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content labels
@mcp.tool(
    title="Remove Label from Content",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_label_from_content_by_path(
    id_: str = Field(..., alias="id", description="The unique identifier of the content item from which the label will be removed."),
    label: str = Field(..., description="The name of the label to remove from the content. This method does not support label names containing forward slashes due to path parameter security restrictions."),
) -> dict[str, Any] | ToolResult:
    """Removes a label from a piece of content by specifying the label name as a path parameter. Use this method when the label name contains no forward slashes; otherwise use the query parameter variant."""

    # Construct request model with validation
    try:
        _request = _models.RemoveLabelFromContentRequest(
            path=_models.RemoveLabelFromContentRequestPath(id_=id_, label=label)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_label_from_content_by_path: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/label/{label}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/label/{label}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_label_from_content_by_path")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_label_from_content_by_path", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_label_from_content_by_path",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content watches
@mcp.tool(
    title="List Page Watches",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_page_watches(
    id_: str = Field(..., alias="id", description="The unique identifier of the page whose watches you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of watch records to return in a single response. The system may apply additional limits regardless of this value."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all watches for a specific page. Users who watch a page receive notifications when the page is updated."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetWatchesForPageRequest(
            path=_models.GetWatchesForPageRequestPath(id_=id_),
            query=_models.GetWatchesForPageRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_page_watches: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/notification/child-created", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/notification/child-created"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_page_watches")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_page_watches", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_page_watches",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content watches
@mcp.tool(
    title="List Space Watches",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_space_watches(
    id_: str = Field(..., alias="id", description="The unique identifier of the content whose parent space watches should be retrieved."),
    limit: str | None = Field(None, description="The maximum number of watch records to return in a single response page. The system may enforce additional limits on this value."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all space watches for the space containing the specified content. Users who watch a space receive notifications when any content in that space is updated."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetWatchesForSpaceRequest(
            path=_models.GetWatchesForSpaceRequestPath(id_=id_),
            query=_models.GetWatchesForSpaceRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_space_watches: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/notification/created", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/notification/created"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_space_watches")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_space_watches", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_space_watches",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content - children and descendants
@mcp.tool(
    title="Copy Page Hierarchy",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def copy_page_hierarchy(
    id_: str = Field(..., alias="id", description="The content ID of the source page whose hierarchy will be copied."),
    destination_page_id: str = Field(..., alias="destinationPageId", description="The content ID of the destination page under which the copied page hierarchy will be placed as a child."),
    copy_attachments: bool | None = Field(None, alias="copyAttachments", description="Whether to copy all attachments from the source page and its descendants to the destination hierarchy."),
    copy_permissions: bool | None = Field(None, alias="copyPermissions", description="Whether to copy page-level permissions from the source page and its descendants to the destination hierarchy."),
    copy_properties: bool | None = Field(None, alias="copyProperties", description="Whether to copy content properties from the source page and its descendants to the destination hierarchy."),
    copy_labels: bool | None = Field(None, alias="copyLabels", description="Whether to copy labels from the source page and its descendants to the destination hierarchy."),
    copy_custom_contents: bool | None = Field(None, alias="copyCustomContents", description="Whether to copy custom contents from the source page and its descendants to the destination hierarchy."),
    copy_descendants: bool | None = Field(None, alias="copyDescendants", description="Whether to copy all descendant pages in the hierarchy. When false, only the source page is copied without its children."),
) -> dict[str, Any] | ToolResult:
    """Copy an entire page hierarchy including all descendant pages, with optional copying of attachments, permissions, properties, labels, and custom contents. Returns a long-running task ID to track the copy operation progress."""

    # Construct request model with validation
    try:
        _request = _models.CopyPageHierarchyRequest(
            path=_models.CopyPageHierarchyRequestPath(id_=id_),
            body=_models.CopyPageHierarchyRequestBody(copy_attachments=copy_attachments, copy_permissions=copy_permissions, copy_properties=copy_properties, copy_labels=copy_labels, copy_custom_contents=copy_custom_contents, copy_descendants=copy_descendants, destination_page_id=destination_page_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for copy_page_hierarchy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/pagehierarchy/copy", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/pagehierarchy/copy"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("copy_page_hierarchy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("copy_page_hierarchy", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="copy_page_hierarchy",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Content - children and descendants
@mcp.tool(
    title="Copy Page",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def copy_page(
    id_: str = Field(..., alias="id", description="The content ID of the page to copy."),
    type_: Literal["space", "existing_page", "parent_page", "parent_content"] = Field(..., alias="type", description="The destination type for the copied page: 'space' copies as a root page, 'parent_page' or 'parent_content' copies as a child, 'existing_page' replaces the target page."),
    destination_value: str = Field(..., alias="destinationValue", description="The destination identifier: space key for 'space' type, or content ID for 'parent_page', 'parent_content', and 'existing_page' types."),
    storage_value: str = Field(..., alias="storageValue", description="The page content body in storage format representation."),
    editor2_value: str = Field(..., alias="editor2Value", description="The page content body in editor2 format representation."),
    storage_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="storageRepresentation", description="The content format type for the storage body representation."),
    editor2_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="editor2Representation", description="The content format type for the editor2 body representation."),
    copy_attachments: bool | None = Field(None, alias="copyAttachments", description="Whether to copy attachments from the source page to the destination page."),
    copy_permissions: bool | None = Field(None, alias="copyPermissions", description="Whether to copy page permissions from the source page to the destination page."),
    copy_properties: bool | None = Field(None, alias="copyProperties", description="Whether to copy content properties from the source page to the destination page."),
    copy_labels: bool | None = Field(None, alias="copyLabels", description="Whether to copy labels from the source page to the destination page."),
    copy_custom_contents: bool | None = Field(None, alias="copyCustomContents", description="Whether to copy custom contents from the source page to the destination page."),
    page_title: str | None = Field(None, alias="pageTitle", description="Optional title to replace the source page title in the destination page."),
) -> dict[str, Any] | ToolResult:
    """Copies a single page with its associated properties, permissions, attachments, and custom contents to a specified destination (space, parent page, parent content, or existing page)."""

    # Construct request model with validation
    try:
        _request = _models.CopyPageRequest(
            path=_models.CopyPageRequestPath(id_=id_),
            body=_models.CopyPageRequestBody(copy_attachments=copy_attachments, copy_permissions=copy_permissions, copy_properties=copy_properties, copy_labels=copy_labels, copy_custom_contents=copy_custom_contents, page_title=page_title,
                destination=_models.CopyPageRequestBodyDestination(type_=type_, value=destination_value),
                body=_models.CopyPageRequestBodyBody(
                    storage=_models.CopyPageRequestBodyBodyStorage(value=storage_value, representation=storage_representation),
                    editor2=_models.CopyPageRequestBodyBodyEditor2(value=editor2_value, representation=editor2_representation)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for copy_page: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/copy", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/copy"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("copy_page")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("copy_page", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="copy_page",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Content permissions
@mcp.tool(
    title="Verify Content Permission",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def verify_content_permission(
    id_: str = Field(..., alias="id", description="The unique identifier of the content to check permissions against."),
    type_: Literal["user", "group"] = Field(..., alias="type", description="The subject type being checked: either a user or group."),
    identifier: str = Field(..., description="The subject identifier. For users, provide the account ID or 'anonymous' for unauthenticated users. For groups, provide the group ID."),
    operation: Literal["read", "update", "delete"] = Field(..., description="The content operation to verify permission for."),
) -> dict[str, Any] | ToolResult:
    """Verify if a user or group has permission to perform a specific operation on content. Checks site permissions, space permissions, and content restrictions to determine access."""

    # Construct request model with validation
    try:
        _request = _models.CheckContentPermissionRequest(
            path=_models.CheckContentPermissionRequestPath(id_=id_),
            body=_models.CheckContentPermissionRequestBody(operation=operation,
                subject=_models.CheckContentPermissionRequestBodySubject(type_=type_, identifier=identifier))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for verify_content_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/permission/check", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/permission/check"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("verify_content_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("verify_content_permission", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="verify_content_permission",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Content restrictions
@mcp.tool(
    title="List Content Restrictions",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_content_restrictions(
    id_: str = Field(..., alias="id", description="The unique identifier of the content whose restrictions you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of users and groups to return per page in the restrictions list. System limits may further restrict this value."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all access restrictions applied to a piece of content, including user and group-level permissions. Requires permission to view the content."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetRestrictionsRequest(
            path=_models.GetRestrictionsRequestPath(id_=id_),
            query=_models.GetRestrictionsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_content_restrictions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/restriction", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/restriction"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_content_restrictions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_content_restrictions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_content_restrictions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content restrictions
@mcp.tool(
    title="Add Content Restrictions",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_content_restrictions(
    id_: str = Field(..., alias="id", description="The unique identifier of the content to which restrictions will be added."),
    body: _models.AddRestrictionsBodyV0 | list[_models.ContentRestrictionUpdate] = Field(..., description="The restriction configuration object specifying the users or groups to restrict and the restriction type to apply."),
) -> dict[str, Any] | ToolResult:
    """Adds access restrictions to a piece of content. This operation appends new restrictions without modifying any existing ones. Requires permission to edit the target content."""

    # Construct request model with validation
    try:
        _request = _models.AddRestrictionsRequest(
            path=_models.AddRestrictionsRequestPath(id_=id_),
            body=_models.AddRestrictionsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_content_restrictions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/restriction", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/restriction"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_content_restrictions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_content_restrictions", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_content_restrictions",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Content restrictions
@mcp.tool(
    title="Replace Content Restrictions",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def replace_content_restrictions(
    id_: str = Field(..., alias="id", description="The unique identifier of the content whose restrictions should be updated."),
    body: _models.UpdateRestrictionsBodyV0 | list[_models.ContentRestrictionUpdate] = Field(..., description="The restriction configuration object containing the new restrictions to apply. This replaces all existing restrictions for the content."),
) -> dict[str, Any] | ToolResult:
    """Replace all existing restrictions for a piece of content with new restrictions. This operation removes current restrictions and applies the restrictions specified in the request body."""

    # Construct request model with validation
    try:
        _request = _models.UpdateRestrictionsRequest(
            path=_models.UpdateRestrictionsRequestPath(id_=id_),
            body=_models.UpdateRestrictionsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for replace_content_restrictions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/restriction", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/restriction"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("replace_content_restrictions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("replace_content_restrictions", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="replace_content_restrictions",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Content restrictions
@mcp.tool(
    title="Remove Content Restrictions",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_content_restrictions(id_: str = Field(..., alias="id", description="The unique identifier of the content whose restrictions should be removed.")) -> dict[str, Any] | ToolResult:
    """Removes all read and update restrictions from a piece of content, making it accessible according to default permissions. Requires permission to edit the content."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRestrictionsRequest(
            path=_models.DeleteRestrictionsRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_content_restrictions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/restriction", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/restriction"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_content_restrictions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_content_restrictions", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_content_restrictions",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content restrictions
@mcp.tool(
    title="List Content Restrictions by Operation",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_content_restrictions_by_operation(id_: str = Field(..., alias="id", description="The unique identifier of the content whose restrictions are being queried.")) -> dict[str, Any] | ToolResult:
    """Retrieves restrictions on content organized by operation type. Returns restriction details with operations as properties rather than array items, requiring permission to view the specified content."""

    # Construct request model with validation
    try:
        _request = _models.GetRestrictionsByOperationRequest(
            path=_models.GetRestrictionsByOperationRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_content_restrictions_by_operation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/restriction/byOperation", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/restriction/byOperation"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_content_restrictions_by_operation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_content_restrictions_by_operation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_content_restrictions_by_operation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content restrictions
@mcp.tool(
    title="Get Content Restriction for Operation",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_content_restriction_for_operation(
    id_: str = Field(..., alias="id", description="The unique identifier of the content item to query for restrictions."),
    operation_key: Literal["read", "update"] = Field(..., alias="operationKey", description="The type of operation for which to retrieve restrictions."),
    limit: str | None = Field(None, description="The maximum number of users and groups to return per page in the restrictions list. System limits may further restrict this value."),
) -> dict[str, Any] | ToolResult:
    """Retrieves access restrictions for a specific content item based on the operation type (read or update). Returns the users and groups with restrictions applied to that content."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetRestrictionsForOperationRequest(
            path=_models.GetRestrictionsForOperationRequestPath(id_=id_, operation_key=operation_key),
            query=_models.GetRestrictionsForOperationRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_content_restriction_for_operation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/restriction/byOperation/{operationKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/restriction/byOperation/{operationKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_content_restriction_for_operation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_content_restriction_for_operation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_content_restriction_for_operation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content restrictions
@mcp.tool(
    title="Check Group Content Restriction",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def check_group_content_restriction(
    id_: str = Field(..., alias="id", description="The unique identifier of the content item to check restrictions for."),
    operation_key: Literal["read", "update"] = Field(..., alias="operationKey", description="The type of operation the restriction applies to."),
    group_id: str = Field(..., alias="groupId", description="The unique identifier of the group to check for the content restriction."),
) -> dict[str, Any] | ToolResult:
    """Checks whether a content restriction applies to a specific group. Returns true if the group has the specified restriction (read or update) on the content, though this does not guarantee group access due to other permission factors."""

    # Construct request model with validation
    try:
        _request = _models.GetIndividualGroupRestrictionStatusByGroupIdRequest(
            path=_models.GetIndividualGroupRestrictionStatusByGroupIdRequestPath(id_=id_, operation_key=operation_key, group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_group_content_restriction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/restriction/byOperation/{operationKey}/byGroupId/{groupId}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/restriction/byOperation/{operationKey}/byGroupId/{groupId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_group_content_restriction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_group_content_restriction", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_group_content_restriction",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content restrictions
@mcp.tool(
    title="Grant Group Content Restriction",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def grant_group_content_restriction(
    id_: str = Field(..., alias="id", description="The ID of the content to which the restriction applies."),
    operation_key: Literal["read", "update"] = Field(..., alias="operationKey", description="The operation type that the restriction applies to, determining whether the group gains read or update access."),
    group_id: str = Field(..., alias="groupId", description="The ID of the group to add to the content restriction."),
) -> dict[str, Any] | ToolResult:
    """Grant read or update permission to a group for a piece of content by adding the group to the content restriction. Requires permission to edit the content."""

    # Construct request model with validation
    try:
        _request = _models.AddGroupToContentRestrictionByGroupIdRequest(
            path=_models.AddGroupToContentRestrictionByGroupIdRequestPath(id_=id_, operation_key=operation_key, group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for grant_group_content_restriction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/restriction/byOperation/{operationKey}/byGroupId/{groupId}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/restriction/byOperation/{operationKey}/byGroupId/{groupId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("grant_group_content_restriction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("grant_group_content_restriction", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="grant_group_content_restriction",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content restrictions
@mcp.tool(
    title="Revoke Group Content Restriction",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def revoke_group_content_restriction(
    id_: str = Field(..., alias="id", description="The unique identifier of the content to which the restriction applies."),
    operation_key: Literal["read", "update"] = Field(..., alias="operationKey", description="The type of operation for which the group restriction is being removed."),
    group_id: str = Field(..., alias="groupId", description="The unique identifier of the group to remove from the content restriction."),
) -> dict[str, Any] | ToolResult:
    """Revoke a group's access restriction for a piece of content by removing them from a specific operation restriction (read or update). Requires permission to edit the content."""

    # Construct request model with validation
    try:
        _request = _models.RemoveGroupFromContentRestrictionRequest(
            path=_models.RemoveGroupFromContentRestrictionRequestPath(id_=id_, operation_key=operation_key, group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_group_content_restriction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/restriction/byOperation/{operationKey}/byGroupId/{groupId}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/restriction/byOperation/{operationKey}/byGroupId/{groupId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_group_content_restriction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_group_content_restriction", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_group_content_restriction",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content restrictions
@mcp.tool(
    title="Check Content Restriction for User",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def check_content_restriction_for_user(
    id_: str = Field(..., alias="id", description="The unique identifier of the content (page, blog post, etc.) to check restrictions for."),
    operation_key: str = Field(..., alias="operationKey", description="The type of operation being restricted (e.g., 'read', 'update', 'delete'). Determines which restriction rule to evaluate."),
    account_id: str | None = Field(None, alias="accountId", description="The unique account ID of the user across all Atlassian products. Used to determine if the restriction applies to this specific user."),
) -> dict[str, Any] | ToolResult:
    """Checks whether a specific content restriction applies to a user. Returns true if the restriction is enforced for that user, though this does not guarantee access due to inherited restrictions, space permissions, or product access levels."""

    # Construct request model with validation
    try:
        _request = _models.GetContentRestrictionStatusForUserRequest(
            path=_models.GetContentRestrictionStatusForUserRequestPath(id_=id_, operation_key=operation_key),
            query=_models.GetContentRestrictionStatusForUserRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_content_restriction_for_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/restriction/byOperation/{operationKey}/user", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/restriction/byOperation/{operationKey}/user"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_content_restriction_for_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_content_restriction_for_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_content_restriction_for_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content restrictions
@mcp.tool(
    title="Grant User Content Restriction",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def grant_user_content_restriction(
    id_: str = Field(..., alias="id", description="The unique identifier of the content to which the restriction applies."),
    operation_key: str = Field(..., alias="operationKey", description="The operation type that the restriction applies to (e.g., read, update)."),
    account_id: str | None = Field(None, alias="accountId", description="The account ID of the user to grant permission to. This uniquely identifies the user across all Atlassian products."),
) -> dict[str, Any] | ToolResult:
    """Grant a user read or update permission for content by adding them to a content restriction. Requires permission to edit the content."""

    # Construct request model with validation
    try:
        _request = _models.AddUserToContentRestrictionRequest(
            path=_models.AddUserToContentRestrictionRequestPath(id_=id_, operation_key=operation_key),
            query=_models.AddUserToContentRestrictionRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for grant_user_content_restriction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/restriction/byOperation/{operationKey}/user", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/restriction/byOperation/{operationKey}/user"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("grant_user_content_restriction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("grant_user_content_restriction", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="grant_user_content_restriction",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content restrictions
@mcp.tool(
    title="Revoke User Content Restriction",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def revoke_user_content_restriction(
    id_: str = Field(..., alias="id", description="The unique identifier of the content item from which the user restriction will be removed."),
    operation_key: Literal["read", "update"] = Field(..., alias="operationKey", description="The type of permission restriction to remove from the user."),
    account_id: str | None = Field(None, alias="accountId", description="The account ID of the user whose restriction will be removed. This uniquely identifies the user across all Atlassian products."),
) -> dict[str, Any] | ToolResult:
    """Revoke a user's content restriction by removing their read or update permission for a specific piece of content. Requires permission to edit the content."""

    # Construct request model with validation
    try:
        _request = _models.RemoveUserFromContentRestrictionRequest(
            path=_models.RemoveUserFromContentRestrictionRequestPath(id_=id_, operation_key=operation_key),
            query=_models.RemoveUserFromContentRestrictionRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_user_content_restriction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/restriction/byOperation/{operationKey}/user", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/restriction/byOperation/{operationKey}/user"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_user_content_restriction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_user_content_restriction", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_user_content_restriction",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content states
@mcp.tool(
    title="Get Content State",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_content_state(id_: str = Field(..., alias="id", description="The unique identifier of the content item whose state you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the current state of a content item, supporting draft, current, or archived versions. Requires permission to view the specified content."""

    # Construct request model with validation
    try:
        _request = _models.GetContentStateRequest(
            path=_models.GetContentStateRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_content_state: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/state", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/state"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_content_state")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_content_state", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_content_state",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content states
@mcp.tool(
    title="Publish Content with State",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def publish_content_with_state(
    id_: str = Field(..., alias="id", description="The unique identifier of the content whose state will be updated."),
    status: Literal["current", "draft"] = Field(..., description="Whether the state should be applied to the draft version or published as a new current version. Draft applies the state to unpublished changes; current publishes a new version with the same body as the previous version."),
    id_2: str | None = Field(None, alias="id", description="The numeric identifier of the state to apply. Use 0, 1, or 2 for default space states, or provide the ID of a custom state. If provided along with name and color, this ID takes precedence."),
    name: str | None = Field(None, description="The display name for a custom state. If a custom state with this name and color already exists for the current user, that existing state will be reused. Maximum 20 characters."),
    color: str | None = Field(None, description="The color for a custom state in 6-digit hexadecimal format (e.g., #ff7452 for red). Must be paired with a name to create or reuse a custom state."),
) -> dict[str, Any] | ToolResult:
    """Set the content state for a piece of content and publish a new version with that state. This creates a new version without modifying the content body, allowing you to apply state changes (default or custom) to either draft or current versions."""

    _id_2 = _parse_int(id_2)

    # Construct request model with validation
    try:
        _request = _models.SetContentStateRequest(
            path=_models.SetContentStateRequestPath(id_=id_),
            query=_models.SetContentStateRequestQuery(status=status),
            body=_models.SetContentStateRequestBody(id_2=_id_2, name=name, color=color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for publish_content_with_state: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/state", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/state"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("publish_content_with_state")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("publish_content_with_state", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="publish_content_with_state",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Content states
@mcp.tool(
    title="Publish Content Without State",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def publish_content_without_state(id_: str = Field(..., alias="id", description="The unique identifier of the content whose state should be removed and republished.")) -> dict[str, Any] | ToolResult:
    """Removes the content state and publishes a new version of the content without modifying its body. This operation creates a new version with an updated status while preserving the existing content."""

    # Construct request model with validation
    try:
        _request = _models.RemoveContentStateRequest(
            path=_models.RemoveContentStateRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for publish_content_without_state: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/state", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/state"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("publish_content_without_state")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("publish_content_without_state", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="publish_content_without_state",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content states
@mcp.tool(
    title="List Available Content States",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_available_content_states(id_: str = Field(..., alias="id", description="The unique identifier of the content for which to retrieve available state transitions. Requires permission to edit the content.")) -> dict[str, Any] | ToolResult:
    """Retrieves the content states available for a specific piece of content to transition to. Returns all enabled space content states plus up to 3 most recently published custom content states; use the content-states endpoint to retrieve all custom states."""

    # Construct request model with validation
    try:
        _request = _models.GetAvailableContentStatesRequest(
            path=_models.GetAvailableContentStatesRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_available_content_states: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/state/available", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/state/available"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_available_content_states")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_available_content_states", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_available_content_states",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content versions
@mcp.tool(
    title="Restore Content Version",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def restore_content_version(
    id_: str = Field(..., alias="id", description="The unique identifier of the content whose version will be restored."),
    operation_key: Literal["restore"] = Field(..., alias="operationKey", description="Operation type identifier that must be set to 'restore' to indicate a version restoration action."),
    version_number: str = Field(..., alias="versionNumber", description="The version number to restore as the current version. Must be a positive integer representing a historical version."),
    message: str = Field(..., description="A descriptive message or changelog entry for the restored version."),
    restore_title: bool | None = Field(None, alias="restoreTitle", description="When true, the restored version's title will become the current content title. When false, only the content body is restored while preserving the current title."),
) -> dict[str, Any] | ToolResult:
    """Restores a historical version of content as the latest version by creating a new version with the content from the specified historical version. Requires permission to update the content."""

    _version_number = _parse_int(version_number)

    # Construct request model with validation
    try:
        _request = _models.RestoreContentVersionRequest(
            path=_models.RestoreContentVersionRequestPath(id_=id_),
            body=_models.RestoreContentVersionRequestBody(operation_key=operation_key,
                params=_models.RestoreContentVersionRequestBodyParams(version_number=_version_number, message=message, restore_title=restore_title))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for restore_content_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/version", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/version"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("restore_content_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("restore_content_version", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="restore_content_version",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Content versions
@mcp.tool(
    title="Delete Content Version",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_content_version(
    id_: str = Field(..., alias="id", description="The unique identifier of the content from which the version will be deleted."),
    version_number: str = Field(..., alias="versionNumber", description="The version number to delete, starting from 1 up to the current version number."),
) -> dict[str, Any] | ToolResult:
    """Delete a historical version of content. The changes from the deleted version are automatically rolled up into the next version. Note that the current version cannot be deleted."""

    _version_number = _parse_int(version_number)

    # Construct request model with validation
    try:
        _request = _models.DeleteContentVersionRequest(
            path=_models.DeleteContentVersionRequestPath(id_=id_, version_number=_version_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_content_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/content/{id}/version/{versionNumber}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/content/{id}/version/{versionNumber}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_content_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_content_version", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_content_version",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content states
@mcp.tool(
    title="List Custom Content States",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_custom_content_states() -> dict[str, Any] | ToolResult:
    """Retrieve all custom content states that have been created by the authenticated user. This operation requires user authentication to access personalized content state configurations."""

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/content-states"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_content_states")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_content_states", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_content_states",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content body
@mcp.tool(
    title="Convert Content Body Asynchronously",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def convert_content_body_async(
    to: Literal["export_view"] = Field(..., description="Target format for the converted content body."),
    value: str = Field(..., description="The content body in the source format specified by the representation parameter."),
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., description="Source content format type. Must match the format of the provided content body value."),
    content_id_context: str | None = Field(None, alias="contentIdContext", description="Content ID used to resolve embedded content (page includes, files, links) within the same space. When provided, takes precedence over spaceKeyContext for context resolution."),
    allow_cache: bool | None = Field(None, alias="allowCache", description="Enable caching to reuse conversion results for identical requests. When true, identical requests return the same task ID and reuse cached results; when false, each request creates a new conversion task."),
    embedded_content_render: Literal["current", "version-at-save"] | None = Field(None, alias="embeddedContentRender", description="Rendering mode for embedded content. Use 'current' for the latest version or 'version-at-save' for the version at the time of save."),
) -> dict[str, Any] | ToolResult:
    """Asynchronously convert content body between different formats (storage, editor, atlas_doc_format, view variants). Returns an asyncId to retrieve the conversion result, which remains available for 5 minutes after completion."""

    # Construct request model with validation
    try:
        _request = _models.AsyncConvertContentBodyRequest(
            path=_models.AsyncConvertContentBodyRequestPath(to=to),
            query=_models.AsyncConvertContentBodyRequestQuery(content_id_context=content_id_context, allow_cache=allow_cache, embedded_content_render=embedded_content_render),
            body=_models.AsyncConvertContentBodyRequestBody(value=value, representation=representation)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_content_body_async: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/contentbody/convert/async/{to}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/contentbody/convert/async/{to}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_content_body_async")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_content_body_async", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_content_body_async",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Content body
@mcp.tool(
    title="Get Async Content Conversion",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_async_content_conversion(id_: str = Field(..., alias="id", description="The unique identifier of the asynchronous conversion task whose result or status you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve the converted content body for a completed asynchronous conversion task, or check the current status if the task is still processing. Completed results are available for up to 5 minutes or until a new conversion request is made with caching disabled."""

    # Construct request model with validation
    try:
        _request = _models.AsyncConvertContentBodyResponseRequest(
            path=_models.AsyncConvertContentBodyResponseRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_async_content_conversion: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/contentbody/convert/async/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/contentbody/convert/async/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_async_content_conversion")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_async_content_conversion", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_async_content_conversion",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content body
@mcp.tool(
    title="Get Bulk Content Conversion Results",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_bulk_content_conversion_results(ids: list[str] = Field(..., description="List of asyncIds from conversion tasks to retrieve results for. Maximum 50 task IDs per request. Order is preserved in the response.")) -> dict[str, Any] | ToolResult:
    """Retrieve completed content body conversion results for multiple asynchronous tasks. Results are available for up to 5 minutes after task completion or until a new conversion request is made with caching disabled."""

    # Construct request model with validation
    try:
        _request = _models.BulkAsyncConvertContentBodyResponseRequest(
            query=_models.BulkAsyncConvertContentBodyResponseRequestQuery(ids=ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_content_conversion_results: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/contentbody/convert/async/bulk/tasks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_content_conversion_results")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_content_conversion_results", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_content_conversion_results",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content body
@mcp.tool(
    title="Convert Content Bodies Asynchronously in Bulk",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def convert_content_bodies_async_bulk(conversion_inputs: list[_models.ContentBodyConversionInput] | None = Field(None, alias="conversionInputs", description="Array of content body conversion specifications. Each item defines a source content body and target format. Order is preserved in the response. Maximum 10 items per request.")) -> dict[str, Any] | ToolResult:
    """Asynchronously converts multiple content bodies between supported formats in bulk, with a maximum of 10 conversions per request. Conversion tasks remain available for polling for up to 5 minutes after completion."""

    # Construct request model with validation
    try:
        _request = _models.BulkAsyncConvertContentBodyRequest(
            body=_models.BulkAsyncConvertContentBodyRequestBody(conversion_inputs=conversion_inputs)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_content_bodies_async_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/contentbody/convert/async/bulk/tasks"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_content_bodies_async_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_content_bodies_async_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_content_bodies_async_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Label info
@mcp.tool(
    title="List Label Contents",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_label_contents(
    name: str = Field(..., description="The name of the label to query for associated contents."),
    type_: Literal["page", "blogpost", "attachment", "page_template"] | None = Field(None, alias="type", description="Filter results to only include specific content types."),
    limit: str | None = Field(None, description="Maximum number of results to return in the response."),
) -> dict[str, Any] | ToolResult:
    """Retrieve label information and all contents associated with that label. Only contents the user has permission to view are returned."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetAllLabelContentRequest(
            query=_models.GetAllLabelContentRequestQuery(name=name, type_=type_, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_label_contents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/label"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_label_contents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_label_contents", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_label_contents",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Group
@mcp.tool(
    title="List Groups",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_groups(
    limit: str | None = Field(None, description="Maximum number of groups to return per page. The system may enforce fixed limits below the requested value."),
    access_type: Literal["user", "admin", "site-admin"] | None = Field(None, alias="accessType", description="Filter results by group permission level within the Confluence site."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all user groups from the Confluence site, ordered alphabetically by group name. Requires 'Can use' global permission to access the Confluence site."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetGroupsRequest(
            query=_models.GetGroupsRequestQuery(limit=_limit, access_type=access_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/group"
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

# Tags: Group
@mcp.tool(
    title="Create Group",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_group(name: str = Field(..., description="The name of the user group to create. Must be unique within the Confluence instance.")) -> dict[str, Any] | ToolResult:
    """Creates a new user group in Confluence. Requires site administrator permissions."""

    # Construct request model with validation
    try:
        _request = _models.CreateGroupRequest(
            body=_models.CreateGroupRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/group"
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

# Tags: Group
@mcp.tool(
    title="Get Group by ID",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_group(id_: str = Field(..., alias="id", description="The unique identifier of the group to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a user group by its unique identifier. Requires permission to access the Confluence site."""

    # Construct request model with validation
    try:
        _request = _models.GetGroupByGroupIdRequest(
            query=_models.GetGroupByGroupIdRequestQuery(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/group/by-id"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Group
@mcp.tool(
    title="Delete Group",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_group(id_: str = Field(..., alias="id", description="The unique identifier of the group to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a user group from the Confluence instance. Requires site administrator permissions."""

    # Construct request model with validation
    try:
        _request = _models.RemoveGroupByIdRequest(
            query=_models.RemoveGroupByIdRequestQuery(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/group/by-id"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Group
@mcp.tool(
    title="Search Groups",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_groups(
    query: str = Field(..., description="The search term used to find matching groups. Supports partial matching against group names and identifiers."),
    limit: str | None = Field(None, description="The maximum number of groups to return in the results. Limited to a maximum of 200 groups per request."),
) -> dict[str, Any] | ToolResult:
    """Search for groups using a partial query string. Returns matching groups up to the specified limit."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.SearchGroupsRequest(
            query=_models.SearchGroupsRequestQuery(query=query, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/group/picker"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Group
@mcp.tool(
    title="List Group Members",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_group_members(
    group_id: str = Field(..., alias="groupId", description="The unique identifier of the group whose members you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of users to return per page of results. The system may apply fixed limits that restrict this value."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all users that are members of a specified group. Requires permission to access the Confluence site."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetGroupMembersByGroupIdRequest(
            path=_models.GetGroupMembersByGroupIdRequestPath(group_id=group_id),
            query=_models.GetGroupMembersByGroupIdRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_group_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/group/{groupId}/membersByGroupId", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/group/{groupId}/membersByGroupId"
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

# Tags: Group
@mcp.tool(
    title="Add User to Group",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_user_to_group(
    group_id: str = Field(..., alias="groupId", description="The unique identifier of the group to which the user will be added."),
    account_id: str = Field(..., alias="accountId", description="The account ID of the user to be added to the group."),
) -> dict[str, Any] | ToolResult:
    """Adds a user as a member to a group by its groupId. Requires site admin permissions."""

    # Construct request model with validation
    try:
        _request = _models.AddUserToGroupByGroupIdRequest(
            query=_models.AddUserToGroupByGroupIdRequestQuery(group_id=group_id),
            body=_models.AddUserToGroupByGroupIdRequestBody(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_user_to_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/group/userByGroupId"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Group
@mcp.tool(
    title="Remove User from Group",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_user_from_group(
    group_id: str = Field(..., alias="groupId", description="The unique identifier of the group from which the user will be removed."),
    account_id: str = Field(..., alias="accountId", description="The account ID of the user to remove from the group. This uniquely identifies the user across all Atlassian products."),
) -> dict[str, Any] | ToolResult:
    """Remove a user from a group by group ID. Requires site admin permissions."""

    # Construct request model with validation
    try:
        _request = _models.RemoveMemberFromGroupByGroupIdRequest(
            query=_models.RemoveMemberFromGroupByGroupIdRequestQuery(group_id=group_id, account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_user_from_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/group/userByGroupId"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_user_from_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_user_from_group", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_user_from_group",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Long-running task
@mcp.tool(
    title="Get Long Task",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_longtask(id_: str = Field(..., alias="id", description="The unique identifier of the long-running task to retrieve status information for.")) -> dict[str, Any] | ToolResult:
    """Retrieve the status of an active long-running task such as a space export, including elapsed time and completion percentage. Requires 'Can use' global permission to access the Confluence site."""

    # Construct request model with validation
    try:
        _request = _models.GetTaskRequest(
            path=_models.GetTaskRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_longtask: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/longtask/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/longtask/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_longtask")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_longtask", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_longtask",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Relation
@mcp.tool(
    title="List Related Entities",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_related_entities(
    relation_name: str = Field(..., alias="relationName", description="The name of the relationship type to query. Custom relationship types are supported, but 'like' and 'favourite' relationships are not available through this operation."),
    source_type: Literal["user", "content", "space"] = Field(..., alias="sourceType", description="The type of the source entity in the relationship."),
    source_key: str = Field(..., alias="sourceKey", description="The identifier for the source entity. For users, use 'current' for the logged-in user, an account ID, or a deprecated user key. For content, use the content ID. For spaces, use the space key."),
    target_type: Literal["user", "content", "space"] = Field(..., alias="targetType", description="The type of the target entity in the relationship."),
    limit: str | None = Field(None, description="The maximum number of relationships to return per page. The system may enforce additional limits on this value."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all target entities that have a specific relationship type with a source entity. Relationships are directional, so results depend on the relationship direction defined."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.FindTargetFromSourceRequest(
            path=_models.FindTargetFromSourceRequestPath(relation_name=relation_name, source_type=source_type, source_key=source_key, target_type=target_type),
            query=_models.FindTargetFromSourceRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_related_entities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/relation/{relationName}/from/{sourceType}/{sourceKey}/to/{targetType}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/relation/{relationName}/from/{sourceType}/{sourceKey}/to/{targetType}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_related_entities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_related_entities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_related_entities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Relation
@mcp.tool(
    title="Check Relationship",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def check_relationship(
    relation_name: str = Field(..., alias="relationName", description="The name of the relationship type to check (e.g., 'favourite' for save-for-later, or custom relationship types)."),
    source_type: Literal["user", "content", "space"] = Field(..., alias="sourceType", description="The type of the source entity in the relationship. Must be 'user' if checking a 'favourite' relationship."),
    source_key: str = Field(..., alias="sourceKey", description="The identifier for the source entity. Use 'current' for the logged-in user, an account ID or user key for users, a content ID for content, or a space key for spaces."),
    target_type: Literal["user", "content", "space"] = Field(..., alias="targetType", description="The type of the target entity in the relationship. Must be 'space' or 'content' if checking a 'favourite' relationship."),
    target_key: str = Field(..., alias="targetKey", description="The identifier for the target entity. Use 'current' for the logged-in user, an account ID or user key for users, a content ID for content, or a space key for spaces."),
) -> dict[str, Any] | ToolResult:
    """Check whether a specific relationship exists between two entities. Relationships are directional, so the source and target entities matter. For example, you can check if a user has marked a page as a favorite."""

    # Construct request model with validation
    try:
        _request = _models.GetRelationshipRequest(
            path=_models.GetRelationshipRequestPath(relation_name=relation_name, source_type=source_type, source_key=source_key, target_type=target_type, target_key=target_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_relationship: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/relation/{relationName}/from/{sourceType}/{sourceKey}/to/{targetType}/{targetKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/relation/{relationName}/from/{sourceType}/{sourceKey}/to/{targetType}/{targetKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_relationship")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_relationship", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_relationship",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Relation
@mcp.tool(
    title="Create Relationship",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def create_relationship(
    relation_name: str = Field(..., alias="relationName", description="The name of the relationship to create. Use 'favourite' for the built-in save-for-later relationship, or specify any custom relationship type name."),
    source_type: Literal["user", "content", "space"] = Field(..., alias="sourceType", description="The type of the source entity in the relationship. Must be 'user' when creating a 'favourite' relationship."),
    source_key: str = Field(..., alias="sourceKey", description="The identifier for the source entity. For users, specify 'current' (logged-in user), account ID, or deprecated user key. For content, specify the content ID. For spaces, specify the space key."),
    target_type: Literal["user", "content", "space"] = Field(..., alias="targetType", description="The type of the target entity in the relationship. Must be 'space' or 'content' when creating a 'favourite' relationship."),
    target_key: str = Field(..., alias="targetKey", description="The identifier for the target entity. For users, specify 'current' (logged-in user), account ID, or deprecated user key. For content, specify the content ID. For spaces, specify the space key."),
) -> dict[str, Any] | ToolResult:
    """Creates a relationship between two Confluence entities (user, space, or content). Supports built-in relationships like 'favourite' (save for later) as well as custom relationship types."""

    # Construct request model with validation
    try:
        _request = _models.CreateRelationshipRequest(
            path=_models.CreateRelationshipRequestPath(relation_name=relation_name, source_type=source_type, source_key=source_key, target_type=target_type, target_key=target_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_relationship: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/relation/{relationName}/from/{sourceType}/{sourceKey}/to/{targetType}/{targetKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/relation/{relationName}/from/{sourceType}/{sourceKey}/to/{targetType}/{targetKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_relationship")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_relationship", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_relationship",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Relation
@mcp.tool(
    title="Delete Relationship",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_relationship(
    relation_name: str = Field(..., alias="relationName", description="The name of the relationship to delete (e.g., 'favourite', 'relates_to')."),
    source_type: Literal["user", "content", "space"] = Field(..., alias="sourceType", description="The type of the source entity in the relationship. Must be 'user' for favourite relationships."),
    source_key: str = Field(..., alias="sourceKey", description="The identifier for the source entity. Use 'current' for the logged-in user, account ID or user key for users, content ID for content, or space key for spaces."),
    target_type: Literal["user", "content", "space"] = Field(..., alias="targetType", description="The type of the target entity in the relationship. Must be 'space' or 'content' for favourite relationships."),
    target_key: str = Field(..., alias="targetKey", description="The identifier for the target entity. Use 'current' for the logged-in user, account ID or user key for users, content ID for content, or space key for spaces."),
) -> dict[str, Any] | ToolResult:
    """Removes a relationship between two Confluence entities (user, space, or content). For favourite relationships, users can only delete their own, while space administrators can delete any user's favourites."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRelationshipRequest(
            path=_models.DeleteRelationshipRequestPath(relation_name=relation_name, source_type=source_type, source_key=source_key, target_type=target_type, target_key=target_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_relationship: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/relation/{relationName}/from/{sourceType}/{sourceKey}/to/{targetType}/{targetKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/relation/{relationName}/from/{sourceType}/{sourceKey}/to/{targetType}/{targetKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_relationship")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_relationship", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_relationship",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Relation
@mcp.tool(
    title="List Related Sources",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_related_sources(
    relation_name: str = Field(..., alias="relationName", description="The name of the relationship type to query. Custom relationship types are supported, but 'like' and 'favourite' relationships are not available through this operation."),
    source_type: Literal["user", "content", "space"] = Field(..., alias="sourceType", description="The entity type of the sources to retrieve."),
    target_type: Literal["user", "content", "space"] = Field(..., alias="targetType", description="The entity type of the target entity."),
    target_key: str = Field(..., alias="targetKey", description="The identifier of the target entity. For users, provide 'current' for the logged-in user, a user key, or an account ID. For content, provide the content ID. For spaces, provide the space key."),
    limit: str | None = Field(None, description="The maximum number of relationships to return per page. The system may enforce additional limits on this value."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all source entities that have a specific relationship type to a target entity. Relationships are directional, so this finds sources pointing to the specified target."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.FindSourcesForTargetRequest(
            path=_models.FindSourcesForTargetRequestPath(relation_name=relation_name, source_type=source_type, target_type=target_type, target_key=target_key),
            query=_models.FindSourcesForTargetRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_related_sources: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/relation/{relationName}/to/{targetType}/{targetKey}/from/{sourceType}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/relation/{relationName}/to/{targetType}/{targetKey}/from/{sourceType}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_related_sources")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_related_sources", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_related_sources",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Search
@mcp.tool(
    title="Search Content Globally",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_content_global(
    cqlcontext: str | None = Field(None, description="CQL query string to filter search results. Specify the space key, content ID, and/or content statuses to narrow the search scope. Note: User-specific fields (user, user.fullname, user.accountid, user.userkey) are no longer supported."),
    limit: str | None = Field(None, description="Maximum number of content objects to return per page. System limits may further restrict this value. When using body.export_view or body.styled_view expansion, the maximum is 25."),
    include_archived_spaces: bool | None = Field(None, alias="includeArchivedSpaces", description="Include content from archived spaces in the search results."),
    exclude_current_spaces: bool | None = Field(None, alias="excludeCurrentSpaces", description="Exclude current spaces from results and only return content from archived spaces."),
    excerpt: Literal["highlight", "indexed", "none", "highlight_unescaped", "indexed_unescaped"] | None = Field(None, description="Strategy for generating text excerpts in search results. Highlight shows matched terms in context, indexed uses pre-computed excerpts, and none omits excerpts entirely. Unescaped variants return HTML without entity encoding."),
    site_permission_type_filter: Literal["all", "externalCollaborator", "none"] | None = Field(None, alias="sitePermissionTypeFilter", description="Filter results by user permission type. Use 'none' for licensed users only, 'externalCollaborator' for external/guest users, or 'all' to include all permission types."),
    content_type: str | None = Field(None, description="Content type filter (e.g., 'page', 'blogpost', 'attachment'). Optional."),
    space_key: str | None = Field(None, description="Space key to filter by. Optional."),
    text_search: str | None = Field(None, description="Free text search query. Optional."),
    created_after: str | None = Field(None, description="ISO 8601 date/time to filter content created after this date. Optional."),
    created_before: str | None = Field(None, description="ISO 8601 date/time to filter content created before this date. Optional."),
    modified_after: str | None = Field(None, description="ISO 8601 date/time to filter content modified after this date. Optional."),
    modified_before: str | None = Field(None, description="ISO 8601 date/time to filter content modified before this date. Optional."),
    status: str | None = Field(None, description="Content status filter (e.g., 'current', 'archived'). Optional."),
    label: str | None = Field(None, description="Label to filter by. Optional."),
    ancestor_id: str | None = Field(None, description="Content ID of ancestor to filter by. Optional."),
) -> dict[str, Any] | ToolResult:
    """Search Confluence content using Confluence Query Language (CQL). Returns matching pages, blog posts, and other content objects with support for pagination via cursor-based navigation."""

    # Call helper functions
    cql = build_cql_query(content_type, space_key, text_search, created_after, created_before, modified_after, modified_before, status, label, ancestor_id)

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.SearchByCqlRequest(
            query=_models.SearchByCqlRequestQuery(cqlcontext=cqlcontext, limit=_limit, include_archived_spaces=include_archived_spaces, exclude_current_spaces=exclude_current_spaces, excerpt=excerpt, site_permission_type_filter=site_permission_type_filter, cql=cql)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_content_global: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_content_global")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_content_global", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_content_global",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Search
@mcp.tool(
    title="Search Users",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def search_users(
    cql: str = Field(..., description="CQL query string to filter users. Supports user-specific fields including user, user.fullname, user.accountid, and user.userkey. Use operators like IN, NOT IN, and != for advanced filtering."),
    limit: str | None = Field(None, description="Maximum number of user objects to return per page. System limits may restrict the actual number returned."),
    site_permission_type_filter: Literal["all", "externalCollaborator", "none"] | None = Field(None, alias="sitePermissionTypeFilter", description="Filter users by permission type. Use 'none' for licensed users, 'externalCollaborator' for external/guest users, or 'all' to include all permission types."),
) -> dict[str, Any] | ToolResult:
    """Search for Confluence users using Confluence Query Language (CQL) with support for user-specific fields like account ID, full name, and user key. Some user fields may be null depending on privacy settings."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.SearchUserRequest(
            query=_models.SearchUserRequestQuery(cql=cql, limit=_limit, site_permission_type_filter=site_permission_type_filter)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/search/user"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_users")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_users", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_users",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Space
@mcp.tool(
    title="Create Space",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_space(
    name: str = Field(..., description="The name of the new space. Must be unique and descriptive for identifying the space.", max_length=200),
    key: str | None = Field(None, description="The key for the new space. Format: See [Space\nkeys](https://confluence.atlassian.com/x/lqNMMQ). If `alias` is not provided, this is required."),
    alias: str | None = Field(None, description="This field will be used as the new identifier for the space in confluence page URLs.\nIf the property is not provided the alias will be the provided key.\nThis property is experimental and may be changed or removed in the future."),
    value: str | None = Field(None, description="The space description."),
    permissions: list[_models.SpacePermissionCreate] | None = Field(None, description="The permissions for the new space. If no permissions are provided, the\n[Confluence default space permissions](https://confluence.atlassian.com/x/UAgzKw#CreateaSpace-Spacepermissions)\nare applied. Note that if permissions are provided, the space is\ncreated with only the provided set of permissions, not\nincluding the default space permissions. Space permissions\ncan be modified after creation using the space permissions\nendpoints, and a private space can be created using the\ncreate private space endpoint."),
) -> dict[str, Any] | ToolResult:
    """Creates a new space in Confluence. Requires 'Create Space(s)' global permission. Note that space labels cannot be set during creation."""

    # Construct request model with validation
    try:
        _request = _models.CreateSpaceRequest(
            body=_models.CreateSpaceRequestBody(name=name, key=key, alias=alias, permissions=permissions,
                description=_models.CreateSpaceRequestBodyDescription(plain=_models.CreateSpaceRequestBodyDescriptionPlain(value=value) if any(v is not None for v in [value]) else None) if any(v is not None for v in [value]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_space: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/space"
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
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Space
@mcp.tool(
    title="Create Private Space",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_private_space(
    name: str = Field(..., description="The name for the new private space. Must not exceed 200 characters.", max_length=200),
    key: str | None = Field(None, description="The key for the new space. Format: See [Space\nkeys](https://confluence.atlassian.com/x/lqNMMQ). If `alias` is not provided, this is required."),
    alias: str | None = Field(None, description="This field will be used as the new identifier for the space in confluence page URLs.\nIf the property is not provided the alias will be the provided key.\nThis property is experimental and may be changed or removed in the future."),
    value: str | None = Field(None, description="The space description."),
    permissions: list[_models.SpacePermissionCreate] | None = Field(None, description="The permissions for the new space. If no permissions are provided, the\n[Confluence default space permissions](https://confluence.atlassian.com/x/UAgzKw#CreateaSpace-Spacepermissions)\nare applied. Note that if permissions are provided, the space is\ncreated with only the provided set of permissions, not\nincluding the default space permissions. Space permissions\ncan be modified after creation using the space permissions\nendpoints, and a private space can be created using the\ncreate private space endpoint."),
) -> dict[str, Any] | ToolResult:
    """Creates a new private space visible only to the creator. Requires 'Create Space(s)' global permission."""

    # Construct request model with validation
    try:
        _request = _models.CreatePrivateSpaceRequest(
            body=_models.CreatePrivateSpaceRequestBody(name=name, key=key, alias=alias, permissions=permissions,
                description=_models.CreatePrivateSpaceRequestBodyDescription(plain=_models.CreatePrivateSpaceRequestBodyDescriptionPlain(value=value) if any(v is not None for v in [value]) else None) if any(v is not None for v in [value]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_private_space: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/space/_private"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_private_space")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_private_space", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_private_space",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Space
@mcp.tool(
    title="Update Space",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_space(
    space_key: str = Field(..., alias="spaceKey", description="The unique key identifier of the space to update."),
    name: str | None = Field(None, description="The new name for the space.", max_length=200),
    type_: str | None = Field(None, alias="type", description="The new type classification for the space."),
) -> dict[str, Any] | ToolResult:
    """Updates a space's name, description, or homepage. Requires 'Admin' permission for the space. Note that permissions and space labels cannot be modified through this API."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSpaceRequest(
            path=_models.UpdateSpaceRequestPath(space_key=space_key),
            body=_models.UpdateSpaceRequestBody(name=name, type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_space: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/space/{spaceKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/space/{spaceKey}"
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
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Space
@mcp.tool(
    title="Delete Space",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_space(space_key: str = Field(..., alias="spaceKey", description="The unique key identifier of the space to delete. This is the space's short name used in URLs and references.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a space without sending it to trash. The deletion occurs as a long-running task, so the space may not be immediately deleted when the response is returned. Poll the status link in the response to monitor task completion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpaceRequest(
            path=_models.DeleteSpaceRequestPath(space_key=space_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_space: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/space/{spaceKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/space/{spaceKey}"
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

# Tags: Space permissions
@mcp.tool(
    title="Grant Custom Content Permission",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def grant_custom_content_permission(
    space_key: str = Field(..., alias="spaceKey", description="The unique key identifier of the Confluence space where the permission will be granted."),
    type_: Literal["user", "group"] = Field(..., alias="type", description="The type of principal receiving the permission: either a user account or a group."),
    identifier: str = Field(..., description="The unique identifier of the principal. For users, provide the accountId or 'anonymous' for anonymous access. For groups, provide the groupId."),
    operations: list[_models.AddCustomContentPermissionsBodyOperationsItem] = Field(..., description="An array of permission operations to grant to the specified principal. Each operation defines what actions are permitted on custom content within the space."),
) -> dict[str, Any] | ToolResult:
    """Grants a new custom content permission to a user or group within a Confluence space. Only apps can modify app-specific permissions, and the requesting user must have Admin permission for the space."""

    # Construct request model with validation
    try:
        _request = _models.AddCustomContentPermissionsRequest(
            path=_models.AddCustomContentPermissionsRequestPath(space_key=space_key),
            body=_models.AddCustomContentPermissionsRequestBody(operations=operations,
                subject=_models.AddCustomContentPermissionsRequestBodySubject(type_=type_, identifier=identifier))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for grant_custom_content_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/space/{spaceKey}/permission/custom-content", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/space/{spaceKey}/permission/custom-content"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("grant_custom_content_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("grant_custom_content_permission", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="grant_custom_content_permission",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Space permissions
@mcp.tool(
    title="Delete Space Permission",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_space_permission(
    space_key: str = Field(..., alias="spaceKey", description="The unique key identifier of the space from which the permission will be removed."),
    id_: int = Field(..., alias="id", description="The unique identifier of the permission record to be deleted."),
) -> dict[str, Any] | ToolResult:
    """Removes a specific permission from a space. Deleting Read Space permission for a user or group will cascade and remove all other space permissions for that user or group."""

    # Construct request model with validation
    try:
        _request = _models.RemovePermissionRequest(
            path=_models.RemovePermissionRequestPath(space_key=space_key, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_space_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/space/{spaceKey}/permission/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/space/{spaceKey}/permission/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_space_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_space_permission", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_space_permission",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content states
@mcp.tool(
    title="List Space Content States",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_space_content_states(space_key: str = Field(..., alias="spaceKey", description="The unique identifier key of the space whose suggested content states should be retrieved.")) -> dict[str, Any] | ToolResult:
    """Retrieve the content states that are suggested for use within a specific Confluence space. Requires 'View' permission for the space."""

    # Construct request model with validation
    try:
        _request = _models.GetSpaceContentStatesRequest(
            path=_models.GetSpaceContentStatesRequestPath(space_key=space_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_space_content_states: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/space/{spaceKey}/state", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/space/{spaceKey}/state"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_space_content_states")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_space_content_states", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_space_content_states",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content states
@mcp.tool(
    title="List Space Content by State",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_space_content_by_state(
    space_key: str = Field(..., alias="spaceKey", description="The key identifier of the space to query for content with the specified state."),
    state_id: str = Field(..., alias="state-id", description="The numeric identifier of the content state to filter results by."),
    limit: str | None = Field(None, description="Maximum number of results to return in the response."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all content in a space filtered by a specific content state. Requires 'View' permission for the space. Note: When using expand parameter with body.export_view and/or body.styled_view, the limit is restricted to a maximum of 25."""

    _state_id = _parse_int(state_id)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetContentsWithStateRequest(
            path=_models.GetContentsWithStateRequestPath(space_key=space_key),
            query=_models.GetContentsWithStateRequestQuery(state_id=_state_id, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_space_content_by_state: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/space/{spaceKey}/state/content", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/space/{spaceKey}/state/content"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_space_content_by_state")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_space_content_by_state", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_space_content_by_state",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Themes
@mcp.tool(
    title="Get Space Theme",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_space_theme(space_key: str = Field(..., alias="spaceKey", description="The unique identifier key of the space whose theme should be retrieved.")) -> dict[str, Any] | ToolResult:
    """Retrieves the theme configuration for a space. If no custom theme is set, the space inherits the global look and feel settings."""

    # Construct request model with validation
    try:
        _request = _models.GetSpaceThemeRequest(
            path=_models.GetSpaceThemeRequestPath(space_key=space_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_space_theme: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/space/{spaceKey}/theme", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/space/{spaceKey}/theme"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_space_theme")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_space_theme", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_space_theme",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Themes
@mcp.tool(
    title="Apply Space Theme",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def apply_space_theme(
    space_key: str = Field(..., alias="spaceKey", description="The unique identifier key of the space where the theme will be applied."),
    theme_key: str = Field(..., alias="themeKey", description="The unique identifier key of the theme to apply to the space."),
) -> dict[str, Any] | ToolResult:
    """Apply a theme to a Confluence space. Requires 'Admin' permission for the space. To reset to the default theme, use the reset_space_theme operation instead."""

    # Construct request model with validation
    try:
        _request = _models.SetSpaceThemeRequest(
            path=_models.SetSpaceThemeRequestPath(space_key=space_key),
            body=_models.SetSpaceThemeRequestBody(theme_key=theme_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for apply_space_theme: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/space/{spaceKey}/theme", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/space/{spaceKey}/theme"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("apply_space_theme")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("apply_space_theme", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="apply_space_theme",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Content watches
@mcp.tool(
    title="List Space Watchers",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_space_watchers(
    space_key: str = Field(..., alias="spaceKey", description="The unique identifier key of the space for which to retrieve watchers."),
    limit: str | None = Field(None, description="The maximum number of watchers to return in the response. The actual limit may be restricted by system configuration."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of users watching a specific space. Use this to see who is monitoring updates to a space."""

    # Construct request model with validation
    try:
        _request = _models.GetWatchersForSpaceRequest(
            path=_models.GetWatchersForSpaceRequestPath(space_key=space_key),
            query=_models.GetWatchersForSpaceRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_space_watchers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/space/{spaceKey}/watch", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/space/{spaceKey}/watch"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_space_watchers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_space_watchers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_space_watchers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Experimental
@mcp.tool(
    title="List Space Labels",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_space_labels(
    space_key: str = Field(..., alias="spaceKey", description="The unique identifier key of the space from which to retrieve labels."),
    limit: str | None = Field(None, description="The maximum number of labels to return in a single page of results. The system may enforce additional limits on this value."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all labels associated with a Confluence space, with optional filtering and pagination support."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetLabelsForSpaceRequest(
            path=_models.GetLabelsForSpaceRequestPath(space_key=space_key),
            query=_models.GetLabelsForSpaceRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_space_labels: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/space/{spaceKey}/label", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/space/{spaceKey}/label"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_space_labels")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_space_labels", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_space_labels",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Experimental
@mcp.tool(
    title="Add Space Labels",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_space_labels(
    space_key: str = Field(..., alias="spaceKey", description="The unique key identifier of the space where labels will be added."),
    body: list[_models.LabelCreate] = Field(..., description="An array of label objects to add to the space. Each label in the array will be appended to the space's existing labels."),
) -> dict[str, Any] | ToolResult:
    """Adds one or more labels to a space without removing existing labels. This operation appends new labels to the space's current label set."""

    # Construct request model with validation
    try:
        _request = _models.AddLabelsToSpaceRequest(
            path=_models.AddLabelsToSpaceRequestPath(space_key=space_key),
            body=_models.AddLabelsToSpaceRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_space_labels: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/space/{spaceKey}/label", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/space/{spaceKey}/label"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_space_labels")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_space_labels", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_space_labels",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Experimental
@mcp.tool(
    title="Remove Label from Space",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_label_from_space(
    space_key: str = Field(..., alias="spaceKey", description="The unique identifier (key) of the space from which the label should be removed."),
    name: str = Field(..., description="The name of the label to remove from the space."),
) -> dict[str, Any] | ToolResult:
    """Remove a label from a space. This operation deletes the association between a specific label and the space identified by its key."""

    # Construct request model with validation
    try:
        _request = _models.DeleteLabelFromSpaceRequest(
            path=_models.DeleteLabelFromSpaceRequestPath(space_key=space_key),
            query=_models.DeleteLabelFromSpaceRequestQuery(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_label_from_space: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/space/{spaceKey}/label", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/space/{spaceKey}/label"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_label_from_space")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_label_from_space", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_label_from_space",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Template
@mcp.tool(
    title="Create Template",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_template(
    name: str = Field(..., description="The name of the template to create."),
    template_type: str = Field(..., alias="templateType", description="The type of template being created."),
    view_value: str = Field(..., alias="viewValue", description="The template body content in view format."),
    export_view_value: str = Field(..., alias="export_viewValue", description="The template body content in export_view format."),
    styled_view_value: str = Field(..., alias="styled_viewValue", description="The template body content in styled_view format."),
    storage_value: str = Field(..., alias="storageValue", description="The template body content in storage format."),
    editor_value: str = Field(..., alias="editorValue", description="The template body content in editor format."),
    editor2_value: str = Field(..., alias="editor2Value", description="The template body content in editor2 format."),
    wiki_value: str = Field(..., alias="wikiValue", description="The template body content in wiki format."),
    atlas_doc_format_value: str = Field(..., alias="atlas_doc_formatValue", description="The template body content in atlas_doc_format format."),
    anonymous_export_view_value: str = Field(..., alias="anonymous_export_viewValue", description="The template body content in anonymous_export_view format."),
    view_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="viewRepresentation", description="The content representation format for the view body."),
    export_view_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="export_viewRepresentation", description="The content representation format for the export_view body."),
    styled_view_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="styled_viewRepresentation", description="The content representation format for the styled_view body."),
    storage_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="storageRepresentation", description="The content representation format for the storage body."),
    editor_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="editorRepresentation", description="The content representation format for the editor body."),
    editor2_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="editor2Representation", description="The content representation format for the editor2 body."),
    wiki_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="wikiRepresentation", description="The content representation format for the wiki body."),
    atlas_doc_format_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="atlas_doc_formatRepresentation", description="The content representation format for the atlas_doc_format body."),
    anonymous_export_view_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="anonymous_export_viewRepresentation", description="The content representation format for the anonymous_export_view body."),
    key: str = Field(..., description="The unique key identifier for the template."),
) -> dict[str, Any] | ToolResult:
    """Creates a new content template for a space or globally. Requires 'Admin' permission for the space or 'Confluence Administrator' global permission. Note: blueprint templates cannot be created via this API."""

    # Construct request model with validation
    try:
        _request = _models.CreateContentTemplateRequest(
            body=_models.CreateContentTemplateRequestBody(name=name, template_type=template_type,
                body=_models.CreateContentTemplateRequestBodyBody(
                    view=_models.CreateContentTemplateRequestBodyBodyView(value=view_value, representation=view_representation),
                    export_view=_models.CreateContentTemplateRequestBodyBodyExportView(value=export_view_value, representation=export_view_representation),
                    styled_view=_models.CreateContentTemplateRequestBodyBodyStyledView(value=styled_view_value, representation=styled_view_representation),
                    storage=_models.CreateContentTemplateRequestBodyBodyStorage(value=storage_value, representation=storage_representation),
                    editor=_models.CreateContentTemplateRequestBodyBodyEditor(value=editor_value, representation=editor_representation),
                    editor2=_models.CreateContentTemplateRequestBodyBodyEditor2(value=editor2_value, representation=editor2_representation),
                    wiki=_models.CreateContentTemplateRequestBodyBodyWiki(value=wiki_value, representation=wiki_representation),
                    atlas_doc_format=_models.CreateContentTemplateRequestBodyBodyAtlasDocFormat(value=atlas_doc_format_value, representation=atlas_doc_format_representation),
                    anonymous_export_view=_models.CreateContentTemplateRequestBodyBodyAnonymousExportView(value=anonymous_export_view_value, representation=anonymous_export_view_representation)
                ),
                space=_models.CreateContentTemplateRequestBodySpace(key=key))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/template"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Template
@mcp.tool(
    title="Update Template",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_template(
    template_id: str = Field(..., alias="templateId", description="The unique identifier of the template to update."),
    name: str = Field(..., description="The display name of the template. Retain the current name if not being changed."),
    template_type: Literal["page"] = Field(..., alias="templateType", description="The template type. Must be set to 'page' for content templates."),
    view_value: str = Field(..., alias="viewValue", description="The template body content in view format."),
    export_view_value: str = Field(..., alias="export_viewValue", description="The template body content in export_view format."),
    styled_view_value: str = Field(..., alias="styled_viewValue", description="The template body content in styled_view format."),
    storage_value: str = Field(..., alias="storageValue", description="The template body content in storage format."),
    editor_value: str = Field(..., alias="editorValue", description="The template body content in editor format."),
    editor2_value: str = Field(..., alias="editor2Value", description="The template body content in editor2 format."),
    wiki_value: str = Field(..., alias="wikiValue", description="The template body content in wiki format."),
    atlas_doc_format_value: str = Field(..., alias="atlas_doc_formatValue", description="The template body content in atlas_doc_format."),
    anonymous_export_view_value: str = Field(..., alias="anonymous_export_viewValue", description="The template body content in anonymous_export_view format."),
    view_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="viewRepresentation", description="The content representation format for the view body."),
    export_view_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="export_viewRepresentation", description="The content representation format for the export_view body."),
    styled_view_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="styled_viewRepresentation", description="The content representation format for the styled_view body."),
    storage_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="storageRepresentation", description="The content representation format for the storage body."),
    editor_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="editorRepresentation", description="The content representation format for the editor body."),
    editor2_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="editor2Representation", description="The content representation format for the editor2 body."),
    wiki_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="wikiRepresentation", description="The content representation format for the wiki body."),
    atlas_doc_format_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="atlas_doc_formatRepresentation", description="The content representation format for the atlas_doc_format body."),
    anonymous_export_view_representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., alias="anonymous_export_viewRepresentation", description="The content representation format for the anonymous_export_view body."),
    key: str = Field(..., description="The template key identifier used for internal reference."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing content template with new content and metadata. Requires 'Admin' permission for space templates or 'Confluence Administrator' global permission for global templates. Blueprint templates cannot be updated via this API."""

    # Construct request model with validation
    try:
        _request = _models.UpdateContentTemplateRequest(
            body=_models.UpdateContentTemplateRequestBody(template_id=template_id, name=name, template_type=template_type,
                body=_models.UpdateContentTemplateRequestBodyBody(
                    view=_models.UpdateContentTemplateRequestBodyBodyView(value=view_value, representation=view_representation),
                    export_view=_models.UpdateContentTemplateRequestBodyBodyExportView(value=export_view_value, representation=export_view_representation),
                    styled_view=_models.UpdateContentTemplateRequestBodyBodyStyledView(value=styled_view_value, representation=styled_view_representation),
                    storage=_models.UpdateContentTemplateRequestBodyBodyStorage(value=storage_value, representation=storage_representation),
                    editor=_models.UpdateContentTemplateRequestBodyBodyEditor(value=editor_value, representation=editor_representation),
                    editor2=_models.UpdateContentTemplateRequestBodyBodyEditor2(value=editor2_value, representation=editor2_representation),
                    wiki=_models.UpdateContentTemplateRequestBodyBodyWiki(value=wiki_value, representation=wiki_representation),
                    atlas_doc_format=_models.UpdateContentTemplateRequestBodyBodyAtlasDocFormat(value=atlas_doc_format_value, representation=atlas_doc_format_representation),
                    anonymous_export_view=_models.UpdateContentTemplateRequestBodyBodyAnonymousExportView(value=anonymous_export_view_value, representation=anonymous_export_view_representation)
                ),
                space=_models.UpdateContentTemplateRequestBodySpace(key=key))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/template"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_template", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_template",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Template
@mcp.tool(
    title="List Blueprint Templates",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_blueprint_templates(
    space_key: str | None = Field(None, alias="spaceKey", description="The space key to query for templates. Omit this parameter to retrieve global blueprint templates instead of space-specific ones."),
    limit: str | None = Field(None, description="The maximum number of templates to return in a single response. The system may enforce additional limits on this value."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all blueprint templates available globally or within a specific space. Global templates are inherited by all spaces, while space-specific templates can be customized independently."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetBlueprintTemplatesRequest(
            query=_models.GetBlueprintTemplatesRequestQuery(space_key=space_key, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_blueprint_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/template/blueprint"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_blueprint_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_blueprint_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_blueprint_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Template
@mcp.tool(
    title="List Templates",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_templates(
    space_key: str | None = Field(None, alias="spaceKey", description="The space key to retrieve templates from. Omit this parameter to retrieve global templates instead of space-specific templates."),
    limit: str | None = Field(None, description="The maximum number of templates to return per page. The system may enforce lower limits than requested."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all content templates, either globally or within a specific space. Requires 'View' permission for space templates or 'Can use' global permission for global templates."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetContentTemplatesRequest(
            query=_models.GetContentTemplatesRequestQuery(space_key=space_key, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/template/page"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

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

# Tags: Template
@mcp.tool(
    title="Get Template",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_template(content_template_id: str = Field(..., alias="contentTemplateId", description="The unique identifier of the content template to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a content template with its metadata, including name, space or blueprint location, and template body. Requires 'View' permission for space templates or 'Can use' global permission for global templates."""

    # Construct request model with validation
    try:
        _request = _models.GetContentTemplateRequest(
            path=_models.GetContentTemplateRequestPath(content_template_id=content_template_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/template/{contentTemplateId}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/template/{contentTemplateId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Template
@mcp.tool(
    title="Delete Template",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_template(content_template_id: str = Field(..., alias="contentTemplateId", description="The unique identifier of the template to be deleted.")) -> dict[str, Any] | ToolResult:
    """Deletes a template, with behavior varying by template type: content templates are removed, modified space-level or global-level blueprint templates revert to their parent templates, and unmodified blueprint templates cannot be deleted. Requires 'Admin' permission for space templates or 'Confluence Administrator' global permission for global templates."""

    # Construct request model with validation
    try:
        _request = _models.RemoveTemplateRequest(
            path=_models.RemoveTemplateRequestPath(content_template_id=content_template_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/template/{contentTemplateId}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/template/{contentTemplateId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_template", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_template",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
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
async def get_user(account_id: str = Field(..., alias="accountId", description="The unique account ID that identifies the user across all Atlassian products. This is a required identifier to retrieve the specific user's information.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific user, including display name, account ID, profile picture, and other profile data. Information returned may be restricted based on the user's profile visibility settings."""

    # Construct request model with validation
    try:
        _request = _models.GetUserRequest(
            query=_models.GetUserRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/user"
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
    title="Get Anonymous User",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_anonymous_user() -> dict[str, Any] | ToolResult:
    """Retrieves information about how anonymous users are represented in Confluence, including their profile picture and display name. Requires 'Can use' global permission to access the Confluence site."""

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/user/anonymous"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_anonymous_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_anonymous_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_anonymous_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
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
    """Retrieves the currently authenticated user's profile information, including display name, user key, account ID, and profile picture. Requires 'Can use' global permission to access the Confluence site."""

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/user/current"
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

# Tags: Users
@mcp.tool(
    title="List User Groups",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_user_groups(
    account_id: str = Field(..., alias="accountId", description="The account ID that uniquely identifies the user across all Atlassian products."),
    limit: str | None = Field(None, description="The maximum number of groups to return per page. This value may be restricted by system limits."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all groups that a user is a member of. Requires permission to access the Confluence site."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetGroupMembershipsForUserRequest(
            query=_models.GetGroupMembershipsForUserRequestQuery(account_id=account_id, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/user/memberof"
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

# Tags: Users
@mcp.tool(
    title="List Users",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_users(account_id: str = Field(..., alias="accountId", description="Comma-separated list of account IDs identifying the users to retrieve. Maximum of 100 IDs per request; excess IDs are ignored.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information for multiple users by their account IDs. Returns up to 100 user records per request; additional IDs beyond the limit are ignored."""

    # Construct request model with validation
    try:
        _request = _models.GetBulkUserLookupRequest(
            query=_models.GetBulkUserLookupRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/user/bulk"
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

# Tags: Content watches
@mcp.tool(
    title="Check Content Watch Status",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def check_content_watch_status(
    content_id: str = Field(..., alias="contentId", description="The unique identifier of the content to check watch status for."),
    account_id: str | None = Field(None, alias="accountId", description="The account ID of the user whose watch status should be checked. If not provided, the currently authenticated user's status is returned. The accountId uniquely identifies the user across all Atlassian products."),
) -> dict[str, Any] | ToolResult:
    """Check whether a user is watching a specific piece of content. Requires 'Confluence Administrator' permission if checking another user's status, otherwise only 'Can use' permission is needed."""

    # Construct request model with validation
    try:
        _request = _models.GetContentWatchStatusRequest(
            path=_models.GetContentWatchStatusRequestPath(content_id=content_id),
            query=_models.GetContentWatchStatusRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_content_watch_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/user/watch/content/{contentId}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/user/watch/content/{contentId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_content_watch_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_content_watch_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_content_watch_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content watches
@mcp.tool(
    title="Watch Content",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def watch_content(
    content_id: str = Field(..., alias="contentId", description="The unique identifier of the content to add the watcher to."),
    account_id: str | None = Field(None, alias="accountId", description="The account ID of the user to add as a watcher. If not provided, the currently logged-in user will be used. Requires 'Confluence Administrator' global permission when specified."),
) -> dict[str, Any] | ToolResult:
    """Add a user as a watcher to a piece of content in Confluence. The watcher can be specified by account ID, or if not specified, the currently logged-in user will be added as a watcher."""

    # Construct request model with validation
    try:
        _request = _models.AddContentWatcherRequest(
            path=_models.AddContentWatcherRequestPath(content_id=content_id),
            query=_models.AddContentWatcherRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for watch_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/user/watch/content/{contentId}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/user/watch/content/{contentId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("watch_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("watch_content", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="watch_content",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content watches
@mcp.tool(
    title="Unwatch Content",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def unwatch_content(
    content_id: str = Field(..., alias="contentId", description="The unique identifier of the content from which to remove the watcher."),
    x_atlassian_token: str = Field(..., alias="X-Atlassian-Token", description="XSRF protection token required for this DELETE operation."),
    account_id: str | None = Field(None, alias="accountId", description="The account ID of the user to remove as a watcher. If not provided, the currently logged-in user is removed. The accountId uniquely identifies the user across all Atlassian products."),
) -> dict[str, Any] | ToolResult:
    """Remove a user as a watcher from content. Specify a user by accountId, or omit to remove the currently logged-in user. Requires 'Confluence Administrator' permission if specifying another user, otherwise standard site access permission."""

    # Construct request model with validation
    try:
        _request = _models.RemoveContentWatcherRequest(
            path=_models.RemoveContentWatcherRequestPath(content_id=content_id),
            query=_models.RemoveContentWatcherRequestQuery(account_id=account_id),
            header=_models.RemoveContentWatcherRequestHeader(x_atlassian_token=x_atlassian_token)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unwatch_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/user/watch/content/{contentId}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/user/watch/content/{contentId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unwatch_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unwatch_content", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unwatch_content",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content watches
@mcp.tool(
    title="Check Label Watch Status",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def check_label_watch_status(
    label_name: str = Field(..., alias="labelName", description="The name of the label to check watch status for."),
    account_id: str | None = Field(None, alias="accountId", description="The account ID of the user to check. If not provided, the currently logged-in user is used. Required if checking another user's watch status."),
) -> dict[str, Any] | ToolResult:
    """Check whether a user is watching a specific label in Confluence. If no user is specified, the currently logged-in user is checked."""

    # Construct request model with validation
    try:
        _request = _models.IsWatchingLabelRequest(
            path=_models.IsWatchingLabelRequestPath(label_name=label_name),
            query=_models.IsWatchingLabelRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_label_watch_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/user/watch/label/{labelName}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/user/watch/label/{labelName}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_label_watch_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_label_watch_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_label_watch_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content watches
@mcp.tool(
    title="Watch Label",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def watch_label(
    label_name: str = Field(..., alias="labelName", description="The name of the label to watch."),
    x_atlassian_token: str = Field(..., alias="X-Atlassian-Token", description="XSRF protection token. Must be set to 'no-check' for this operation."),
    account_id: str | None = Field(None, alias="accountId", description="The account ID of the user to add as a watcher. If not provided, the currently authenticated user is used. Required only if you have 'Confluence Administrator' permission; otherwise, the authenticated user is assumed."),
) -> dict[str, Any] | ToolResult:
    """Subscribe a user as a watcher to a label in Confluence. The watcher will receive notifications for changes to the label. If no user is specified, the currently authenticated user is subscribed."""

    # Construct request model with validation
    try:
        _request = _models.AddLabelWatcherRequest(
            path=_models.AddLabelWatcherRequestPath(label_name=label_name),
            query=_models.AddLabelWatcherRequestQuery(account_id=account_id),
            header=_models.AddLabelWatcherRequestHeader(x_atlassian_token=x_atlassian_token)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for watch_label: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/user/watch/label/{labelName}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/user/watch/label/{labelName}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("watch_label")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("watch_label", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="watch_label",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content watches
@mcp.tool(
    title="Unwatch Label",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def unwatch_label(
    label_name: str = Field(..., alias="labelName", description="The name of the label from which to remove the watcher."),
    account_id: str | None = Field(None, alias="accountId", description="The account ID of the user to remove as a watcher. If not specified, the currently logged-in user will be used. Required only if removing a different user (requires Confluence Administrator permission)."),
) -> dict[str, Any] | ToolResult:
    """Remove a user as a watcher from a label in Confluence. If no user is specified, the currently logged-in user will be removed as a watcher."""

    # Construct request model with validation
    try:
        _request = _models.RemoveLabelWatcherRequest(
            path=_models.RemoveLabelWatcherRequestPath(label_name=label_name),
            query=_models.RemoveLabelWatcherRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unwatch_label: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/user/watch/label/{labelName}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/user/watch/label/{labelName}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unwatch_label")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unwatch_label", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unwatch_label",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content watches
@mcp.tool(
    title="Check Space Watch Status",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def check_space_watch_status(
    space_key: str = Field(..., alias="spaceKey", description="The unique identifier key of the space to check watch status for."),
    account_id: str | None = Field(None, alias="accountId", description="The account ID of the user to check watch status for. If not provided, the currently logged-in user is used. Requires 'Confluence Administrator' permission when specified."),
) -> dict[str, Any] | ToolResult:
    """Check whether a user is watching a specific space. Identifies the user via account ID query parameter or uses the currently logged-in user if not specified."""

    # Construct request model with validation
    try:
        _request = _models.IsWatchingSpaceRequest(
            path=_models.IsWatchingSpaceRequestPath(space_key=space_key),
            query=_models.IsWatchingSpaceRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_space_watch_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/user/watch/space/{spaceKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/user/watch/space/{spaceKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_space_watch_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_space_watch_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_space_watch_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content watches
@mcp.tool(
    title="Watch Space",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def watch_space(
    space_key: str = Field(..., alias="spaceKey", description="The key identifier of the space to add the watcher to."),
    x_atlassian_token: str = Field(..., alias="X-Atlassian-Token", description="XSRF protection token. Must be set to 'no-check' for this operation."),
    account_id: str | None = Field(None, alias="accountId", description="The account ID of the user to add as a watcher. If not provided, the currently logged-in user will be used. Required only when adding a watcher other than yourself."),
) -> dict[str, Any] | ToolResult:
    """Adds a user as a watcher to a Confluence space. If no user is specified, the currently logged-in user will be added as a watcher."""

    # Construct request model with validation
    try:
        _request = _models.AddSpaceWatcherRequest(
            path=_models.AddSpaceWatcherRequestPath(space_key=space_key),
            query=_models.AddSpaceWatcherRequestQuery(account_id=account_id),
            header=_models.AddSpaceWatcherRequestHeader(x_atlassian_token=x_atlassian_token)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for watch_space: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/user/watch/space/{spaceKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/user/watch/space/{spaceKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("watch_space")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("watch_space", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="watch_space",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Content watches
@mcp.tool(
    title="Unwatch Space",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def unwatch_space(
    space_key: str = Field(..., alias="spaceKey", description="The key that uniquely identifies the space from which to remove the watcher."),
    account_id: str | None = Field(None, alias="accountId", description="The account ID of the user to remove as a watcher. If not provided, the currently logged-in user will be removed. The accountId uniquely identifies the user across all Atlassian products."),
) -> dict[str, Any] | ToolResult:
    """Remove a user as a watcher from a space. Specify a user by accountId, or omit to remove the currently logged-in user. Requires 'Confluence Administrator' permission if removing another user, otherwise requires site access permission."""

    # Construct request model with validation
    try:
        _request = _models.RemoveSpaceWatchRequest(
            path=_models.RemoveSpaceWatchRequestPath(space_key=space_key),
            query=_models.RemoveSpaceWatchRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unwatch_space: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/user/watch/space/{spaceKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/user/watch/space/{spaceKey}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unwatch_space")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unwatch_space", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unwatch_space",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool(
    title="Fetch User Emails in Bulk",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def fetch_user_emails_bulk(account_id: list[str] = Field(..., alias="accountId", description="An array of account IDs identifying the users whose email addresses should be retrieved. Users with unavailable accounts will be excluded from the results.")) -> dict[str, Any] | ToolResult:
    """Retrieve email addresses for multiple users in a single batch request, bypassing profile visibility restrictions. This operation requires appropriate permissions and is subject to app approval guidelines for Connect apps or asApp() context for Forge apps."""

    # Construct request model with validation
    try:
        _request = _models.GetPrivacyUnsafeUserEmailBulkRequest(
            query=_models.GetPrivacyUnsafeUserEmailBulkRequestQuery(account_id=account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for fetch_user_emails_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/wiki/rest/api/user/email/bulk"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "accountId": ("form", False),
    })
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("fetch_user_emails_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("fetch_user_emails_bulk", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="fetch_user_emails_bulk",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Analytics
@mcp.tool(
    title="Get Content Views",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_content_views(
    content_id: str = Field(..., alias="contentId", description="The unique identifier of the content whose view count should be retrieved."),
    from_date: str | None = Field(None, alias="fromDate", description="Filter results to include only views from this date forward. Specify in ISO 8601 format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the total number of views for a specific piece of content, optionally filtered from a given date onwards."""

    # Construct request model with validation
    try:
        _request = _models.GetViewsRequest(
            path=_models.GetViewsRequestPath(content_id=content_id),
            query=_models.GetViewsRequestQuery(from_date=from_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_content_views: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/analytics/content/{contentId}/views", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/analytics/content/{contentId}/views"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_content_views")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_content_views", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_content_views",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Analytics
@mcp.tool(
    title="Get Content Viewers",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_content_viewers(
    content_id: str = Field(..., alias="contentId", description="The unique identifier of the content to retrieve viewer analytics for."),
    from_date: str | None = Field(None, alias="fromDate", description="Filter results to include only views from this date forward. Use ISO 8601 format for the timestamp."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the total number of distinct viewers for a specific piece of content, optionally filtered by a start date."""

    # Construct request model with validation
    try:
        _request = _models.GetViewersRequest(
            path=_models.GetViewersRequestPath(content_id=content_id),
            query=_models.GetViewersRequestQuery(from_date=from_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_content_viewers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/analytics/content/{contentId}/viewers", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/analytics/content/{contentId}/viewers"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_content_viewers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_content_viewers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_content_viewers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User properties
@mcp.tool(
    title="List User Properties",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_user_properties(
    user_id: str = Field(..., alias="userId", description="The account ID of the user whose properties you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of properties to return in a single page of results. The system may enforce stricter limits than the specified maximum."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all properties associated with a user account on the Confluence site. User properties are stored at the site level and provide metadata about the user."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetUserPropertiesRequest(
            path=_models.GetUserPropertiesRequestPath(user_id=user_id),
            query=_models.GetUserPropertiesRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_properties: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/user/{userId}/property", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/user/{userId}/property"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_properties")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_properties", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_properties",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User properties
@mcp.tool(
    title="Get User Property",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_user_property(
    user_id: str = Field(..., alias="userId", description="The account ID of the user whose property you want to retrieve."),
    key: str = Field(..., description="The key identifying which user property to retrieve. Keys must contain only alphanumeric characters, hyphens, and underscores.", pattern="^[-_a-zA-Z0-9]+$"),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific property for a Confluence user by its key. User properties are stored at the site level and require 'Can use' global permission to access."""

    # Construct request model with validation
    try:
        _request = _models.GetUserPropertyRequest(
            path=_models.GetUserPropertyRequestPath(user_id=user_id, key=key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/user/{userId}/property/{key}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/user/{userId}/property/{key}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User properties
@mcp.tool(
    title="Set User Property",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def set_user_property(
    user_id: str = Field(..., alias="userId", description="The account ID of the user. This uniquely identifies the user across all Atlassian products."),
    key: str = Field(..., description="The key identifying this user property. Keys must contain only alphanumeric characters, hyphens, and underscores.", pattern="^[-_a-zA-Z0-9]+$"),
    value: dict[str, Any] = Field(..., description="The value to store for this user property. Can be any JSON-serializable object."),
) -> dict[str, Any] | ToolResult:
    """Set a custom property for a user at the Confluence site level. User properties enable storing arbitrary metadata associated with user accounts across the Confluence instance."""

    # Construct request model with validation
    try:
        _request = _models.CreateUserPropertyRequest(
            path=_models.CreateUserPropertyRequestPath(user_id=user_id, key=key),
            body=_models.CreateUserPropertyRequestBody(value=value)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_user_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/user/{userId}/property/{key}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/user/{userId}/property/{key}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_user_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_user_property", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_user_property",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: User properties
@mcp.tool(
    title="Set User Property Value",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def set_user_property_value(
    user_id: str = Field(..., alias="userId", description="The account ID of the user. This uniquely identifies the user across all Atlassian products."),
    key: str = Field(..., description="The key identifier for the user property. Must contain only alphanumeric characters, hyphens, and underscores.", pattern="^[-_a-zA-Z0-9]+$"),
    value: dict[str, Any] = Field(..., description="The new value to assign to the user property. Can be any JSON-serializable object."),
) -> dict[str, Any] | ToolResult:
    """Updates or sets a property value for a user on the Confluence site. The property key cannot be changed, only its value can be modified."""

    # Construct request model with validation
    try:
        _request = _models.UpdateUserPropertyRequest(
            path=_models.UpdateUserPropertyRequestPath(user_id=user_id, key=key),
            body=_models.UpdateUserPropertyRequestBody(value=value)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_user_property_value: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/user/{userId}/property/{key}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/user/{userId}/property/{key}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_user_property_value")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_user_property_value", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_user_property_value",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: User properties
@mcp.tool(
    title="Remove User Property",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def remove_user_property(
    user_id: str = Field(..., alias="userId", description="The account ID that uniquely identifies the user across all Atlassian products."),
    key: str = Field(..., description="The key identifying which user property to delete. Must contain only alphanumeric characters, hyphens, and underscores.", pattern="^[-_a-zA-Z0-9]+$"),
) -> dict[str, Any] | ToolResult:
    """Removes a custom property from a user account on the Confluence site. User properties are stored at the site level and are distinct from space or content-level properties."""

    # Construct request model with validation
    try:
        _request = _models.DeleteUserPropertyRequest(
            path=_models.DeleteUserPropertyRequestPath(user_id=user_id, key=key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_user_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/wiki/rest/api/user/{userId}/property/{key}", _request.path.model_dump(by_alias=True)) if _request.path else "/wiki/rest/api/user/{userId}/property/{key}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_user_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_user_property", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_user_property",
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
        print("  python atlassian_confluence_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Atlassian Confluence MCP Server")

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
    logger.info("Starting Atlassian Confluence MCP Server")
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

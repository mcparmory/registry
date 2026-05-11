#!/usr/bin/env python3
"""
BambooHR MCP Server
Generated: 2026-05-11 19:30:47 UTC
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

# Server variables (from OpenAPI spec, overridable via SERVER_* env vars)
_SERVER_VARS = {
    "companyDomain": os.getenv("SERVER_COMPANYDOMAIN", "companySubDomain"),
}
BASE_URL = os.getenv("BASE_URL", "https://{companyDomain}.bamboohr.com".format_map(collections.defaultdict(str, _SERVER_VARS)))
SERVER_NAME = "BambooHR"
SERVER_VERSION = "1.0.6"

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
    'oauth',
    'basic',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["oauth"] = _auth.OAuth2Auth()
    logging.info("Authentication configured: oauth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for oauth not configured: {error_msg}")
    _auth_handlers["oauth"] = None
try:
    _auth_handlers["basic"] = _auth.BasicAuth(env_var_username="BASIC_AUTH_USERNAME", env_var_password="BASIC_AUTH_PASSWORD")
    logging.info("Authentication configured: basic")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for basic not configured: {error_msg}")
    _auth_handlers["basic"] = None

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

mcp = FastMCP("BambooHR", middleware=[_JsonCoercionMiddleware()])

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Create Time Tracking Project",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_project(
    name: str = Field(..., description="Unique display name for the project, no more than 50 characters.", max_length=50),
    billable: bool | None = Field(None, description="Whether time logged to this project is billable. Defaults to true if omitted."),
    allow_all_employees: bool | None = Field(None, alias="allowAllEmployees", description="Whether all employees are permitted to log time to this project. Set to false and provide employeeIds to restrict access to specific employees. Defaults to true if omitted."),
    employee_ids: list[int] | None = Field(None, alias="employeeIds", description="List of employee IDs permitted to log time to this project. Only applied when allowAllEmployees is false; ignored otherwise."),
    has_tasks: bool | None = Field(None, alias="hasTasks", description="Whether the project supports task-level time tracking. When true, at least one task must be provided in the tasks array. Defaults to false if omitted."),
    tasks: list[_models.TaskCreateSchema] | None = Field(None, description="Tasks to create and associate with the project. Required when hasTasks is true; each task name must be unique within the project and no more than 50 characters. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Creates a new time tracking project with optional task-level tracking and employee access controls. Returns the created project including its ID, tasks, and employee access list when access is restricted."""

    # Construct request model with validation
    try:
        _request = _models.CreateTimeTrackingProjectRequest(
            body=_models.CreateTimeTrackingProjectRequestBody(name=name, billable=billable, allow_all_employees=allow_all_employees, employee_ids=employee_ids, has_tasks=has_tasks, tasks=tasks)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/time_tracking/projects"
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

# Tags: Time Tracking, Public API
@mcp.tool(
    title="List Break Assessments",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_break_assessments(
    offset: int | None = Field(None, description="Number of records to skip before returning results, used for paginating through large result sets. Must be zero or greater; defaults to 0.", ge=0),
    limit: int | None = Field(None, description="Maximum number of break assessment records to return in a single response. Accepts values from 0 to 500; defaults to 100.", ge=0, le=500),
    filter_: str | None = Field(None, alias="filter", description="OData v4 filter expression to narrow results by specific fields. Filterable fields include: `id`, `breakId`, `employeeId`, `employeeTimesheetId`, `date`, `result`, `availableYmdt`, `unavailableYmdt`, `createdAt`, `updatedAt`, `expectedDuration`, `recordedDuration`, and `durationDifference`."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of break assessments, each recording whether an employee complied with their assigned break policy for a given day along with any violations. Use the filter parameter to scope results by employee, date, compliance result, or other fields."""

    # Construct request model with validation
    try:
        _request = _models.ListBreakAssessmentsRequest(
            query=_models.ListBreakAssessmentsRequestQuery(offset=offset, limit=limit, filter_=filter_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_break_assessments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/time-tracking/break-assessments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_break_assessments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_break_assessments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_break_assessments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Get Break",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_break(id_: str = Field(..., alias="id", description="The unique identifier of the time tracking break to retrieve, provided as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieves the full details of a specific time tracking break by its unique identifier, including its name, duration, paid status, and availability configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetBreakRequest(
            path=_models.GetBreakRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_break: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time-tracking/breaks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time-tracking/breaks/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_break")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_break", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_break",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Update Break",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_break(
    id_: str = Field(..., alias="id", description="The unique identifier of the break to update."),
    name: str | None = Field(None, description="Human-readable label for the break, used to identify it in schedules and reports."),
    policy_id: str | None = Field(None, alias="policyId", description="The UUID of the break policy this break belongs to, linking it to a set of organizational rules."),
    paid: bool | None = Field(None, description="Indicates whether employees are compensated during this break; true means the break counts toward paid work time."),
    duration: int | None = Field(None, description="The length of the break in whole minutes."),
    availability_type: Literal["anytime", "hours_worked", "time_of_day"] | None = Field(None, alias="availabilityType", description="Determines when the break becomes available: 'anytime' imposes no restriction, 'hours_worked' gates availability on hours worked thresholds, and 'time_of_day' restricts the break to a specific time window."),
    availability_min_hours_worked: float | None = Field(None, alias="availabilityMinHoursWorked", description="The minimum number of hours an employee must have worked before this break becomes available; applicable when availabilityType is 'hours_worked'."),
    availability_max_hours_worked: float | None = Field(None, alias="availabilityMaxHoursWorked", description="The maximum number of hours an employee can work before this break must be taken; applicable when availabilityType is 'hours_worked'."),
    availability_start_time: str | None = Field(None, alias="availabilityStartTime", description="The earliest clock time at which the break may be started, in HH:MM 24-hour format; applicable when availabilityType is 'time_of_day'."),
    availability_end_time: str | None = Field(None, alias="availabilityEndTime", description="The latest clock time by which the break must be started, in HH:MM 24-hour format; applicable when availabilityType is 'time_of_day'."),
) -> dict[str, Any] | ToolResult:
    """Partially updates an existing time tracking break by its UUID, modifying only the fields provided in the request body. Returns the full updated break record on success."""

    # Construct request model with validation
    try:
        _request = _models.UpdateBreakRequest(
            path=_models.UpdateBreakRequestPath(id_=id_),
            body=_models.UpdateBreakRequestBody(name=name, policy_id=policy_id, paid=paid, duration=duration, availability_type=availability_type, availability_min_hours_worked=availability_min_hours_worked, availability_max_hours_worked=availability_max_hours_worked, availability_start_time=availability_start_time, availability_end_time=availability_end_time)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_break: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time-tracking/breaks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time-tracking/breaks/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_break")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_break", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_break",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Delete Break",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_break(id_: str = Field(..., alias="id", description="The unique identifier of the break to delete, provided as a UUID.")) -> dict[str, Any] | ToolResult:
    """Soft-deletes a time tracking break by its unique identifier, permanently removing it from any associated break policies."""

    # Construct request model with validation
    try:
        _request = _models.DeleteBreakRequest(
            path=_models.DeleteBreakRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_break: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time-tracking/breaks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time-tracking/breaks/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_break")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_break", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_break",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="List Break Policy Breaks",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_break_policy_breaks(
    id_: str = Field(..., alias="id", description="The unique identifier of the break policy whose breaks you want to retrieve."),
    offset: int | None = Field(None, description="The number of records to skip before returning results, used for paginating through large result sets."),
    limit: int | None = Field(None, description="The maximum number of breaks to return in a single response, up to a limit of 500.", le=500),
    filter_: str | None = Field(None, alias="filter", description="An OData v4 filter expression used to query breaks by specific field values or conditions."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of breaks associated with a specific break policy. Supports OData v4 filtering to narrow results by break attributes."""

    # Construct request model with validation
    try:
        _request = _models.ListBreakPolicyBreaksRequest(
            path=_models.ListBreakPolicyBreaksRequestPath(id_=id_),
            query=_models.ListBreakPolicyBreaksRequestQuery(offset=offset, limit=limit, filter_=filter_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_break_policy_breaks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time-tracking/break-policies/{id}/breaks", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time-tracking/break-policies/{id}/breaks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_break_policy_breaks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_break_policy_breaks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_break_policy_breaks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Create Break",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_break(
    id_: str = Field(..., alias="id", description="The unique identifier of the break policy to associate the new break with."),
    name: str | None = Field(None, description="A descriptive label for the break, used to identify it within the policy."),
    paid: bool | None = Field(None, description="Indicates whether employees are compensated during this break."),
    duration: int | None = Field(None, description="How long the break lasts, expressed in whole minutes."),
    availability_type: Literal["anytime", "hours_worked", "time_of_day"] | None = Field(None, alias="availabilityType", description="Controls when the break becomes available: 'anytime' allows it at any point, 'hours_worked' gates it on hours worked thresholds, and 'time_of_day' restricts it to a specific time window."),
    availability_min_hours_worked: float | None = Field(None, alias="availabilityMinHoursWorked", description="The minimum number of hours an employee must have worked before this break becomes available; applicable when availabilityType is 'hours_worked'."),
    availability_max_hours_worked: float | None = Field(None, alias="availabilityMaxHoursWorked", description="The maximum number of hours an employee can work before this break must be taken; applicable when availabilityType is 'hours_worked'."),
    availability_start_time: str | None = Field(None, alias="availabilityStartTime", description="The earliest clock time at which the break can be taken, in HH:MM 24-hour format; applicable when availabilityType is 'time_of_day'."),
    availability_end_time: str | None = Field(None, alias="availabilityEndTime", description="The latest clock time by which the break must be taken, in HH:MM 24-hour format; applicable when availabilityType is 'time_of_day'."),
) -> dict[str, Any] | ToolResult:
    """Creates a new break and associates it with the specified break policy. Configure the break's name, pay status, duration, and availability rules to control when employees can take it."""

    # Construct request model with validation
    try:
        _request = _models.CreateBreakRequest(
            path=_models.CreateBreakRequestPath(id_=id_),
            body=_models.CreateBreakRequestBody(name=name, paid=paid, duration=duration, availability_type=availability_type, availability_min_hours_worked=availability_min_hours_worked, availability_max_hours_worked=availability_max_hours_worked, availability_start_time=availability_start_time, availability_end_time=availability_end_time)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_break: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time-tracking/break-policies/{id}/breaks", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time-tracking/break-policies/{id}/breaks"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_break")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_break", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_break",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Replace Break Policy Breaks",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def replace_break_policy_breaks(
    id_: str = Field(..., alias="id", description="The unique identifier of the break policy whose breaks will be replaced."),
    body: list[_models.TimeTrackingCreateOrUpdateTimeTrackingBreakWithoutPolicyV1] | None = Field(None, description="The full desired collection of breaks for the policy. Each item with an ID will be updated, items without an ID will be created, and any existing breaks not included will be soft-deleted. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Replaces the complete set of breaks for a specified break policy. Breaks with an ID are updated, breaks without an ID are created, and any existing breaks omitted from the request are soft-deleted."""

    # Construct request model with validation
    try:
        _request = _models.ReplaceBreaksForBreakPolicyRequest(
            path=_models.ReplaceBreaksForBreakPolicyRequestPath(id_=id_),
            body=_models.ReplaceBreaksForBreakPolicyRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for replace_break_policy_breaks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time-tracking/break-policies/{id}/breaks", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time-tracking/break-policies/{id}/breaks"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("replace_break_policy_breaks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("replace_break_policy_breaks", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="replace_break_policy_breaks",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Assign Employees to Break Policy",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def assign_employees_to_break_policy(
    id_: str = Field(..., alias="id", description="The unique identifier of the break policy to which employees will be assigned."),
    employee_ids: list[int] = Field(..., alias="employeeIds", description="List of employee IDs to add to the break policy. Must contain at least one ID; order is not significant.", min_length=1),
) -> dict[str, Any] | ToolResult:
    """Assigns one or more employees to an existing break policy, adding them to the policy's membership without affecting any previously assigned employees."""

    # Construct request model with validation
    try:
        _request = _models.AssignEmployeesToBreakPolicyRequest(
            path=_models.AssignEmployeesToBreakPolicyRequestPath(id_=id_),
            body=_models.AssignEmployeesToBreakPolicyRequestBody(employee_ids=employee_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for assign_employees_to_break_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time-tracking/break-policies/{id}/assign", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time-tracking/break-policies/{id}/assign"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("assign_employees_to_break_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("assign_employees_to_break_policy", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="assign_employees_to_break_policy",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Assign Break Policy to Employees",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def assign_break_policy_employees(
    id_: str = Field(..., alias="id", description="The unique identifier of the break policy whose employee assignments will be replaced."),
    employee_ids: list[int] = Field(..., alias="employeeIds", description="Complete list of employee IDs to assign to the break policy. This fully replaces all current assignments — any employee not included will be unassigned. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Assigns a specific set of employees to a break policy, fully replacing all existing employee assignments with the provided list."""

    # Construct request model with validation
    try:
        _request = _models.SetBreakPolicyEmployeesRequest(
            path=_models.SetBreakPolicyEmployeesRequestPath(id_=id_),
            body=_models.SetBreakPolicyEmployeesRequestBody(employee_ids=employee_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for assign_break_policy_employees: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time-tracking/break-policies/{id}/assign", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time-tracking/break-policies/{id}/assign"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("assign_break_policy_employees")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("assign_break_policy_employees", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="assign_break_policy_employees",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Unassign Employees from Break Policy",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def unassign_employees_from_break_policy(
    id_: str = Field(..., alias="id", description="Unique identifier of the break policy from which employees will be unassigned."),
    employee_ids: list[int] = Field(..., alias="employeeIds", description="List of one or more employee IDs to remove from the break policy; order is not significant and each entry should be a valid employee identifier.", min_length=1),
) -> dict[str, Any] | ToolResult:
    """Removes specific employees from a break policy assignment without affecting the policy itself or other assigned employees. Only applicable to policies that are not configured to apply to all employees."""

    # Construct request model with validation
    try:
        _request = _models.UnassignEmployeesFromBreakPolicyRequest(
            path=_models.UnassignEmployeesFromBreakPolicyRequestPath(id_=id_),
            body=_models.UnassignEmployeesFromBreakPolicyRequestBody(employee_ids=employee_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unassign_employees_from_break_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time-tracking/break-policies/{id}/unassign", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time-tracking/break-policies/{id}/unassign"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unassign_employees_from_break_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unassign_employees_from_break_policy", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unassign_employees_from_break_policy",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Get Break Policy",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_break_policy(
    id_: str = Field(..., alias="id", description="The unique identifier of the break policy to retrieve."),
    include_counts: bool | None = Field(None, alias="includeCounts", description="When set to true, the response includes the total number of employees and breaks associated with this policy."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single break policy by its unique identifier. Optionally includes counts of associated employees and breaks for summary reporting."""

    # Construct request model with validation
    try:
        _request = _models.GetBreakPolicyRequest(
            path=_models.GetBreakPolicyRequestPath(id_=id_),
            query=_models.GetBreakPolicyRequestQuery(include_counts=include_counts)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_break_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time-tracking/break-policies/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time-tracking/break-policies/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_break_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_break_policy", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_break_policy",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Update Break Policy",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_break_policy(
    id_: str = Field(..., alias="id", description="The unique identifier of the break policy to update."),
    name: str | None = Field(None, description="The display name for the break policy, typically reflecting a geographic region or compliance context."),
    description: str | None = Field(None, description="An optional human-readable description providing additional context about the break policy's purpose or scope."),
    all_employees_assigned: bool | None = Field(None, alias="allEmployeesAssigned", description="When set to true, this break policy is automatically assigned to all employees rather than a specific subset."),
) -> dict[str, Any] | ToolResult:
    """Partially updates an existing break policy by its UUID, modifying only the fields provided in the request body. Returns the full updated break policy on success."""

    # Construct request model with validation
    try:
        _request = _models.UpdateBreakPolicyRequest(
            path=_models.UpdateBreakPolicyRequestPath(id_=id_),
            body=_models.UpdateBreakPolicyRequestBody(name=name, description=description, all_employees_assigned=all_employees_assigned)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_break_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time-tracking/break-policies/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time-tracking/break-policies/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_break_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_break_policy", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_break_policy",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Delete Break Policy",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_break_policy(id_: str = Field(..., alias="id", description="The unique identifier of the break policy to delete, provided as a UUID.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a break policy by its unique identifier. All associated breaks and employee assignments linked to the policy are also removed."""

    # Construct request model with validation
    try:
        _request = _models.DeleteBreakPolicyRequest(
            path=_models.DeleteBreakPolicyRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_break_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time-tracking/break-policies/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time-tracking/break-policies/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_break_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_break_policy", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_break_policy",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="List Break Policies",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_break_policies(
    offset: int | None = Field(None, description="Number of records to skip before returning results, used for paginating through large result sets."),
    limit: int | None = Field(None, description="Maximum number of break policies to return in a single response, up to 500 per request.", le=500),
    filter_: str | None = Field(None, alias="filter", description="OData v4 filter expression to narrow results by policy attributes such as name or status."),
    include_counts: bool | None = Field(None, alias="includeCounts", description="When enabled, each policy in the response will include the count of assigned employees and associated breaks."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all break policies configured in the time-tracking system. Optionally includes employee and break counts per policy for summary reporting."""

    # Construct request model with validation
    try:
        _request = _models.ListBreakPoliciesRequest(
            query=_models.ListBreakPoliciesRequestQuery(offset=offset, limit=limit, filter_=filter_, include_counts=include_counts)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_break_policies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/time-tracking/break-policies"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_break_policies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_break_policies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_break_policies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Create Break Policy",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_break_policy(
    name: str = Field(..., description="Display name for the break policy, typically reflecting the jurisdiction or compliance context it applies to."),
    description: str | None = Field(None, description="Optional human-readable description providing additional context about the policy's purpose or compliance requirements."),
    all_employees_assigned: bool | None = Field(None, alias="allEmployeesAssigned", description="When set to true, automatically assigns this break policy to all employees, superseding any individual employee assignments."),
    breaks: list[_models.TimeTrackingCreateOrUpdateTimeTrackingBreakWithoutPolicyV1] | None = Field(None, description="List of break definitions to create and associate with this policy simultaneously. Each item defines a break's rules and timing configuration."),
    employee_ids: list[int] | None = Field(None, alias="employeeIds", description="List of employee IDs to assign to this policy. Ignored if allEmployeesAssigned is true. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Creates a new break policy for time tracking compliance, optionally including break definitions and employee assignments in a single request."""

    # Construct request model with validation
    try:
        _request = _models.CreateBreakPolicyRequest(
            body=_models.CreateBreakPolicyRequestBody(name=name, description=description, all_employees_assigned=all_employees_assigned, breaks=breaks, employee_ids=employee_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_break_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/time-tracking/break-policies"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_break_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_break_policy", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_break_policy",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="List Employee Break Availabilities",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_employee_break_availabilities(
    id_: int = Field(..., alias="id", description="The unique identifier of the employee whose break availabilities are being retrieved."),
    effective: str | None = Field(None, description="The employee's local datetime used to calculate which breaks are currently available, defaulting to the current time if omitted. Must be provided in ISO 8601 local datetime format (no timezone offset).", pattern="^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}$"),
) -> dict[str, Any] | ToolResult:
    """Retrieves the available break options for a specific employee at a given point in time. Requires permission to view the target employee and time-tracking-break access."""

    # Construct request model with validation
    try:
        _request = _models.ListEmployeeBreakAvailabilitiesRequest(
            path=_models.ListEmployeeBreakAvailabilitiesRequestPath(id_=id_),
            query=_models.ListEmployeeBreakAvailabilitiesRequestQuery(effective=effective)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_employee_break_availabilities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time-tracking/employees/{id}/break-availabilities", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time-tracking/employees/{id}/break-availabilities"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_employee_break_availabilities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_employee_break_availabilities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_employee_break_availabilities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="List Employee Break Policies",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_employee_break_policies(
    id_: int = Field(..., alias="id", description="The unique identifier of the employee whose break policies are being retrieved."),
    offset: int | None = Field(None, description="The number of records to skip before returning results, used for paginating through large result sets. Must be 0 or greater.", ge=0),
    limit: int | None = Field(None, description="The maximum number of break policies to return in a single response. Accepts values between 0 and 500.", ge=0, le=500),
) -> dict[str, Any] | ToolResult:
    """Retrieves all break policies assigned to a specific employee. Requires permission to view the target employee's records."""

    # Construct request model with validation
    try:
        _request = _models.ListEmployeeBreakPoliciesRequest(
            path=_models.ListEmployeeBreakPoliciesRequestPath(id_=id_),
            query=_models.ListEmployeeBreakPoliciesRequestQuery(offset=offset, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_employee_break_policies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time-tracking/employees/{id}/break-policies", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time-tracking/employees/{id}/break-policies"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_employee_break_policies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_employee_break_policies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_employee_break_policies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="List Break Policy Employees",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_break_policy_employees(
    id_: str = Field(..., alias="id", description="The unique identifier of the break policy whose assigned employees you want to retrieve."),
    offset: int | None = Field(None, description="The number of records to skip before returning results, used for paginating through large result sets."),
    limit: int | None = Field(None, description="The maximum number of employee records to return in a single response, up to a limit of 500.", le=500),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of employees assigned to a specific break policy. Returns an empty list if no employees are currently assigned to the policy."""

    # Construct request model with validation
    try:
        _request = _models.ListBreakPolicyEmployeesRequest(
            path=_models.ListBreakPolicyEmployeesRequestPath(id_=id_),
            query=_models.ListBreakPolicyEmployeesRequestQuery(offset=offset, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_break_policy_employees: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time-tracking/break-policies/{id}/employees", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time-tracking/break-policies/{id}/employees"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_break_policy_employees")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_break_policy_employees", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_break_policy_employees",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Replace Break Policy",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def replace_break_policy(
    id_: str = Field(..., alias="id", description="Unique identifier of the break policy to fully replace."),
    name: str | None = Field(None, description="Display name for the break policy, typically reflecting the region or compliance context it applies to."),
    description: str | None = Field(None, description="Optional human-readable description providing additional context about the break policy's purpose or compliance scope."),
    all_employees_assigned: bool | None = Field(None, alias="allEmployeesAssigned", description="When set to true, this policy applies to all employees in the organization, superseding individual employee assignments."),
    breaks: list[_models.TimeTrackingCreateOrUpdateTimeTrackingBreakWithoutPolicyV1] | None = Field(None, description="Complete list of break definitions to associate with this policy; any breaks previously on the policy that are omitted here will be deleted. Each item should represent a full break configuration."),
    employee_ids: list[int] | None = Field(None, alias="employeeIds", description="Complete list of employee IDs to assign to this policy; any employees previously assigned who are omitted here will be unassigned. Ignored if allEmployeesAssigned is true."),
) -> dict[str, Any] | ToolResult:
    """Performs a full replacement of a break policy and all its associated data, including breaks and employee assignments. Any breaks or assignments not included in the request payload will be removed from the policy."""

    # Construct request model with validation
    try:
        _request = _models.SyncBreakPolicyRequest(
            path=_models.SyncBreakPolicyRequestPath(id_=id_),
            body=_models.SyncBreakPolicyRequestBody(name=name, description=description, all_employees_assigned=all_employees_assigned, breaks=breaks, employee_ids=employee_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for replace_break_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time-tracking/break-policies/{id}/sync", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time-tracking/break-policies/{id}/sync"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("replace_break_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("replace_break_policy", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="replace_break_policy",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Delete Clock Entries",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_clock_entries(clock_entry_ids: list[int] = Field(..., alias="clockEntryIds", description="List of one or more clock entry IDs to delete. At least one ID must be provided; order does not matter.", min_length=1)) -> dict[str, Any] | ToolResult:
    """Permanently deletes one or more timesheet clock entries by their unique IDs. This operation is idempotent, so submitting IDs for already-deleted entries will not cause errors or require retries."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTimesheetClockEntriesViaPostRequest(
            body=_models.DeleteTimesheetClockEntriesViaPostRequestBody(clock_entry_ids=clock_entry_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_clock_entries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/time_tracking/clock_entries/delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_clock_entries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_clock_entries", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_clock_entries",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Delete Hour Entries",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_hour_entries(hour_entry_ids: list[int] = Field(..., alias="hourEntryIds", description="List of one or more timesheet hour entry IDs to delete. At least one ID must be provided; order does not affect the outcome.", min_length=1)) -> dict[str, Any] | ToolResult:
    """Permanently deletes one or more timesheet hour entries by their unique IDs. This operation is idempotent, so submitting IDs for already-deleted entries will not cause errors or require retries."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTimesheetHourEntriesViaPostRequest(
            body=_models.DeleteTimesheetHourEntriesViaPostRequestBody(hour_entry_ids=hour_entry_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_hour_entries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/time_tracking/hour_entries/delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_hour_entries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_hour_entries", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_hour_entries",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="List Timesheet Entries",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_timesheet_entries(
    start: str = Field(..., description="The start of the date range to filter timesheet entries, inclusive. Must be a date within the last 365 days, in ISO 8601 date format."),
    end: str = Field(..., description="The end of the date range to filter timesheet entries, inclusive. Must be a date within the last 365 days, in ISO 8601 date format."),
    employee_ids: str | None = Field(None, alias="employeeIds", description="Comma-separated list of employee IDs used to restrict results to specific employees. When omitted, entries for all accessible employees are returned.", pattern="^\\d+(,\\d+)*$"),
) -> dict[str, Any] | ToolResult:
    """Retrieves timesheet entries (clock and hour types) for all employees or a filtered subset within a specified date range. Both dates must fall within the last 365 days and are interpreted in the company timezone."""

    # Construct request model with validation
    try:
        _request = _models.ListTimesheetEntriesRequest(
            query=_models.ListTimesheetEntriesRequestQuery(start=start, end=end, employee_ids=employee_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_timesheet_entries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/time_tracking/timesheet_entries"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_timesheet_entries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_timesheet_entries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_timesheet_entries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Clock In Employee",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def clock_in_employee(
    employee_id: int = Field(..., alias="employeeId", description="Unique identifier of the employee to clock in."),
    project_id: int | None = Field(None, alias="projectId", description="Associates the timesheet entry with a specific time tracking project. Required when specifying a task."),
    task_id: int | None = Field(None, alias="taskId", description="Associates the timesheet entry with a specific task within the given project. Requires projectId to be provided."),
    note: str | None = Field(None, description="Free-text note to attach to the timesheet entry for additional context."),
    date: str | None = Field(None, description="The calendar date of the clock-in entry for historical records. Must follow YYYY-MM-DD format."),
    start: str | None = Field(None, description="The clock-in time for historical entries in 24-hour HH:MM format, ranging from 00:00 to 23:59.", pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$"),
    timezone_: str | None = Field(None, alias="timezone", description="IANA timezone name used to interpret the date and start time for historical clock-in entries."),
    break_id: str | None = Field(None, alias="breakId", description="UUID of the break type to associate with this timesheet entry."),
    offline: bool | None = Field(None, description="Marks the entry as an offline punch, bypassing shift schedule restrictions. Intended for devices that buffer punches locally and sync them later."),
) -> dict[str, Any] | ToolResult:
    """Records a clock-in entry for an employee, defaulting to the current server time. To log a historical entry, supply a date, start time, and timezone, and optionally associate the entry with a project, task, break, or note."""

    # Construct request model with validation
    try:
        _request = _models.CreateTimesheetClockInEntryRequest(
            path=_models.CreateTimesheetClockInEntryRequestPath(employee_id=employee_id),
            body=_models.CreateTimesheetClockInEntryRequestBody(project_id=project_id, task_id=task_id, note=note, date=date, start=start, timezone_=timezone_, break_id=break_id, offline=offline)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for clock_in_employee: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time_tracking/employees/{employeeId}/clock_in", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time_tracking/employees/{employeeId}/clock_in"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("clock_in_employee")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("clock_in_employee", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="clock_in_employee",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Clock Out Employee",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def clock_out_employee(
    employee_id: int = Field(..., alias="employeeId", description="The unique identifier of the employee to clock out."),
    date: str | None = Field(None, description="The calendar date of the clock-out entry, required when recording a historical entry rather than clocking out at the current server time. Must follow YYYY-MM-DD format."),
    end: str | None = Field(None, description="The clock-out time for a historical entry, expressed in 24-hour HH:MM format where hours range from 00–23 and minutes from 00–59.", pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$"),
    timezone_: str | None = Field(None, alias="timezone", description="The IANA timezone name associated with the clock-out time, required when recording a historical entry to ensure the end time is interpreted correctly."),
) -> dict[str, Any] | ToolResult:
    """Records a clock-out entry for a currently clocked-in employee, defaulting to the current server time. To log a historical clock-out, supply a date, end time, and timezone."""

    # Construct request model with validation
    try:
        _request = _models.CreateTimesheetClockOutEntryRequest(
            path=_models.CreateTimesheetClockOutEntryRequestPath(employee_id=employee_id),
            body=_models.CreateTimesheetClockOutEntryRequestBody(date=date, end=end, timezone_=timezone_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for clock_out_employee: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time_tracking/employees/{employeeId}/clock_out", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time_tracking/employees/{employeeId}/clock_out"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("clock_out_employee")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("clock_out_employee", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="clock_out_employee",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Bulk Upsert Clock Entries",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def bulk_upsert_clock_entries(entries: list[_models.ClockEntrySchema] = Field(..., description="Array of one or more clock entry objects to create or update. Each entry without an ID will be created as a new record; each entry with an existing ID will update the matching record. Must contain at least one entry.", min_length=1)) -> dict[str, Any] | ToolResult:
    """Creates new timesheet clock entries or updates existing ones in a single bulk operation. Entries containing an existing ID are updated; entries without an ID are created as new records."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrUpdateTimesheetClockEntriesRequest(
            body=_models.CreateOrUpdateTimesheetClockEntriesRequestBody(entries=entries)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_upsert_clock_entries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/time_tracking/clock_entries/store"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_upsert_clock_entries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_upsert_clock_entries", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_upsert_clock_entries",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Tracking, Public API
@mcp.tool(
    title="Bulk Upsert Timesheet Entries",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def bulk_upsert_timesheet_entries(hours: list[_models.HourEntrySchema] = Field(..., description="Array of hour entry objects to create or update. Each entry without an ID will be created as a new record; each entry with an existing ID will update the matching record. Order is not significant.")) -> dict[str, Any] | ToolResult:
    """Creates new timesheet hour entries or updates existing ones in a single bulk operation. Entries containing an existing ID are updated; entries without an ID are created as new records."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrUpdateTimesheetHourEntriesRequest(
            body=_models.CreateOrUpdateTimesheetHourEntriesRequestBody(hours=hours)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_upsert_timesheet_entries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/time_tracking/hour_entries/store"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_upsert_timesheet_entries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_upsert_timesheet_entries", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_upsert_timesheet_entries",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks, Public API
@mcp.tool(
    title="List Webhooks",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_webhooks() -> dict[str, Any] | ToolResult:
    """Retrieves all webhooks associated with the authenticated API key, returning an empty array if none exist. Each result includes the webhook ID, name, URL, creation datetime, and last fired datetime; use get_webhook to fetch full configuration details for a specific webhook."""

    # Extract parameters for API call
    _http_path = "/api/v1/webhooks"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks, Public API
@mcp.tool(
    title="Get Webhook",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_webhook(id_: int = Field(..., alias="id", description="The unique numeric identifier of the webhook to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the full configuration of a single webhook owned by the authenticated user, including its name, URL, format, monitored fields, events, and activity timestamps. Returns 403 if the webhook belongs to a different user and 404 if it does not exist."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhookRequest(
            path=_models.GetWebhookRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/webhooks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/webhooks/{id}"
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

# Tags: Webhooks, Public API
@mcp.tool(
    title="Delete Webhook",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_webhook(id_: int = Field(..., alias="id", description="The unique numeric identifier of the webhook to delete. Must correspond to a webhook owned by the authenticated API key.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a webhook associated with the authenticated user's API key. Returns 403 if the webhook belongs to a different API key, or 404 if the webhook does not exist."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWebhookRequest(
            path=_models.DeleteWebhookRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/webhooks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/webhooks/{id}"
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

# Tags: Webhooks, Public API
@mcp.tool(
    title="List Webhook Logs",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_webhook_logs(id_: int = Field(..., alias="id", description="The unique numeric identifier of the webhook whose delivery logs should be retrieved.")) -> dict[str, Any] | ToolResult:
    """Retrieves recent delivery log entries for a specific webhook, covering the last 14 days and up to 200 entries. Each entry includes the webhook URL, last attempt and success timestamps (UTC datetime or status string), HTTP response code, payload format, and employee IDs in the payload. Note: when the rate limit is exceeded the server returns HTTP 200 with an error object instead of the log array — callers must check for an `error.code` of 429 in the response body before processing results."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhookLogsRequest(
            path=_models.GetWebhookLogsRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhook_logs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/webhooks/{id}/log", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/webhooks/{id}/log"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_webhook_logs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_webhook_logs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_webhook_logs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks, Public API
@mcp.tool(
    title="List Webhook Monitor Fields",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_webhook_monitor_fields() -> dict[str, Any] | ToolResult:
    """Retrieves all employee fields available for webhook monitoring, including each field's numeric ID, human-readable name, and alias. Use the returned field IDs or aliases when specifying the `monitorFields` array during webhook creation or updates."""

    # Extract parameters for API call
    _http_path = "/api/v1/webhooks/monitor_fields"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_webhook_monitor_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_webhook_monitor_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_webhook_monitor_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks, Public API
@mcp.tool(
    title="List Webhook Post Fields",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_webhook_post_fields() -> dict[str, Any] | ToolResult:
    """Retrieves all available employee fields that can be included in a webhook post body, along with their related table and page record references. Use the returned field IDs or aliases in the `postFields` map when creating or updating a webhook."""

    # Extract parameters for API call
    _http_path = "/api/v1/webhooks/post-fields"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_webhook_post_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_webhook_post_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_webhook_post_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Datasets, Public API
@mcp.tool(
    title="Query Dataset",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def query_dataset(
    dataset_name: str = Field(..., alias="datasetName", description="The unique name of the dataset to query. Use GET /api/v1/datasets to discover available dataset names."),
    fields: list[str] = Field(..., description="The list of field names to include in the response. Use GET /api/v1/datasets/{datasetName}/fields to discover valid field names for the target dataset."),
    page: int | None = Field(None, description="The page number to retrieve when paginating through results. Must be 1 or greater; defaults to 1.", ge=1),
    page_size: int | None = Field(None, description="The number of records to return per page. Must be between 1 and 1000; defaults to 500.", ge=1, le=1000),
    aggregations: list[_models.GetDataFromDatasetBodyAggregationsItem] | None = Field(None, description="One or more aggregation operations to apply to the result set, each specifying a field and an aggregation function. Supported functions vary by field type: text/bool/options/govIdText support count; date supports count, min, max; int supports count, min, max, sum, avg."),
    sort_by: list[_models.GetDataFromDatasetBodySortByItem] | None = Field(None, alias="sortBy", description="An ordered array of sort directives, each specifying a field name and direction. Sort priority follows the order of items in the array, with the first item having the highest priority."),
    match: str | None = Field(None, description="A full-text search string used to match records across the dataset."),
    filters: list[_models.GetDataFromDatasetBodyFiltersFiltersItem] | None = Field(None, description="An array of filter conditions to apply to the query. Each filter references a field, an operator, and a value; the filtered field does not need to be included in the fields list. Supported operators vary by field type — for example, options fields use includes or does_not_include with values enclosed in square brackets, and date fields support range and last/next with structured value objects. Use GET /api/v1/datasets/{datasetName}/field-options to retrieve valid filter values."),
    group_by: list[str] | None = Field(None, alias="groupBy", description="An array containing a single field name by which to group results. Only one field is supported for grouping at a time."),
    show_history: list[str] | None = Field(None, alias="showHistory", description="An array of entity names corresponding to historical table fields whose full history should be included in the response. Use the entity name values returned by GET /api/v1/datasets/{datasetName}/fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieve paginated records from a specified dataset by providing a list of fields to return, with optional filtering, sorting, grouping, and aggregation. Use GET /api/v1/datasets/{datasetName}/fields to discover available field names before calling this endpoint."""

    # Construct request model with validation
    try:
        _request = _models.GetDataFromDatasetRequest(
            path=_models.GetDataFromDatasetRequestPath(dataset_name=dataset_name),
            query=_models.GetDataFromDatasetRequestQuery(page=page, page_size=page_size),
            body=_models.GetDataFromDatasetRequestBody(fields=fields, aggregations=aggregations, sort_by=sort_by, group_by=group_by, show_history=show_history,
                filters=_models.GetDataFromDatasetRequestBodyFilters(match=match, filters=filters) if any(v is not None for v in [match, filters]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for query_dataset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/datasets/{datasetName}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/datasets/{datasetName}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("query_dataset")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("query_dataset", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="query_dataset",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Reports, Public API
@mcp.tool(
    title="Get Custom Report",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_custom_report(
    report_id: int = Field(..., alias="reportId", description="The unique identifier of the saved custom report to retrieve data for."),
    page: int | None = Field(None, description="The page number to retrieve when paginating through results. Must be 1 or greater.", ge=1),
    page_size: int | None = Field(None, description="The number of records to return per page. Must be between 1 and 1000 inclusive; defaults to 500.", ge=1, le=1000),
) -> dict[str, Any] | ToolResult:
    """Retrieve paginated data for a specific saved custom report by its ID, using the report's stored field list and filter configuration. Use list_custom_reports to discover available report IDs."""

    # Construct request model with validation
    try:
        _request = _models.GetByReportIdRequest(
            path=_models.GetByReportIdRequestPath(report_id=report_id),
            query=_models.GetByReportIdRequestQuery(page=page, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/custom-reports/{reportId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/custom-reports/{reportId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_report", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_report",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Datasets, Public API
@mcp.tool(
    title="List Datasets",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_datasets() -> dict[str, Any] | ToolResult:
    """Retrieves all available datasets, returning each dataset's machine-readable name and human-readable label. Use the returned names to query data via POST /api/v1/datasets/{datasetName} or discover fields via GET /api/v1/datasets/{datasetName}/fields. Note: this endpoint is deprecated — prefer GET /api/v1_2/datasets."""

    # Extract parameters for API call
    _http_path = "/api/v1/datasets"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_datasets")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_datasets", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_datasets",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Datasets, Public API
@mcp.tool(
    title="List Dataset Fields",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_dataset_fields(
    dataset_name: str = Field(..., alias="datasetName", description="The unique machine-readable name of the dataset whose fields you want to retrieve."),
    page: int | None = Field(None, description="The page number to retrieve when navigating paginated results; must be 1 or greater.", ge=1),
    page_size: int | None = Field(None, description="The number of field records to return per page; must be between 1 and 1000 inclusive.", ge=1, le=1000),
) -> dict[str, Any] | ToolResult:
    """Retrieves the available fields for a specified dataset, returning paginated field descriptors that include each field's machine-readable name, human-readable label, parent section type and name, and entity name. Use the returned field `name` values when constructing field selections in POST /api/v1/datasets/{datasetName} queries. Note: this endpoint is deprecated — prefer GET /api/v1_2/datasets/{datasetName}/fields."""

    # Construct request model with validation
    try:
        _request = _models.GetFieldsFromDatasetRequest(
            path=_models.GetFieldsFromDatasetRequestPath(dataset_name=dataset_name),
            query=_models.GetFieldsFromDatasetRequestQuery(page=page, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dataset_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/datasets/{datasetName}/fields", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/datasets/{datasetName}/fields"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dataset_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dataset_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dataset_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom Reports, Public API
@mcp.tool(
    title="List Custom Reports",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_custom_reports(
    page: int | None = Field(None, description="The page number to retrieve when paginating through results, starting at page 1.", ge=1),
    page_size: int | None = Field(None, description="The number of records to return per page, between 1 and 1000. Defaults to 500 if not specified.", ge=1, le=1000),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of saved custom reports available in the account, returning each report's ID and name. Use the returned report ID with the get_custom_report operation to fetch full report data."""

    # Construct request model with validation
    try:
        _request = _models.ListReportsRequest(
            query=_models.ListReportsRequestQuery(page=page, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_reports: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/custom-reports"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_reports")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_reports", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_reports",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Datasets, Public API
@mcp.tool(
    title="Get Field Options",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def get_field_options(
    dataset_name: str = Field(..., alias="datasetName", description="The name of the dataset whose field options you want to retrieve."),
    fields: list[str] = Field(..., description="One or more field names whose possible values should be returned; order is not significant and each entry should be a valid field name within the dataset."),
    dependent_fields: dict[str, list[_models.GetFieldOptionsBodyDependentFieldsValueItem]] | None = Field(None, alias="dependentFields", description="A map of field names to dependent field-value pairs that constrain the options returned for those fields, used when one field's valid options depend on the selected value of another field."),
    filters: dict[str, Any] | None = Field(None, description="An optional filter object that scopes the returned options to only those that exist for records matching the specified conditions, such as limiting options to those applicable to active employees."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the available filter values for one or more fields in a dataset, returning an object keyed by field name where each value is an array of id/value pairs. Use the returned id values when constructing filters for dataset queries."""

    # Construct request model with validation
    try:
        _request = _models.GetFieldOptionsRequest(
            path=_models.GetFieldOptionsRequestPath(dataset_name=dataset_name),
            body=_models.GetFieldOptionsRequestBody(fields=fields, dependent_fields=dependent_fields, filters=filters)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_field_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/datasets/{datasetName}/field-options", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/datasets/{datasetName}/field-options"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_field_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_field_options", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_field_options",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Datasets, Public API
@mcp.tool(
    title="List Datasets",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_datasets_v1_2() -> dict[str, Any] | ToolResult:
    """Retrieves all available datasets, returning each dataset's machine-readable name and human-readable label. Use the returned name values to query dataset records or discover available fields via related endpoints."""

    # Extract parameters for API call
    _http_path = "/api/v1_2/datasets"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_datasets_v1_2")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_datasets_v1_2", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_datasets_v1_2",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Datasets, Public API
@mcp.tool(
    title="List Dataset Fields",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_dataset_fields_v1_2(
    dataset_name: str = Field(..., alias="datasetName", description="The machine-readable name of the dataset whose fields you want to retrieve."),
    page: int | None = Field(None, description="The page number to retrieve for paginated results; must be 1 or greater.", ge=1),
    page_size: int | None = Field(None, description="The number of field records to return per page; must be between 1 and 1000 inclusive.", ge=1, le=1000),
) -> dict[str, Any] | ToolResult:
    """Retrieve the available fields for a specified dataset, returning paginated field descriptors that include each field's machine-readable name, human-readable label, parent section, and entity name. Use the returned field `name` values when constructing data queries against the dataset."""

    # Construct request model with validation
    try:
        _request = _models.GetFieldsFromDatasetV12Request(
            path=_models.GetFieldsFromDatasetV12RequestPath(dataset_name=dataset_name),
            query=_models.GetFieldsFromDatasetV12RequestQuery(page=page, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dataset_fields_v1_2: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1_2/datasets/{datasetName}/fields", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1_2/datasets/{datasetName}/fields"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dataset_fields_v1_2")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dataset_fields_v1_2", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dataset_fields_v1_2",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Datasets, Public API
@mcp.tool(
    title="Get Field Options",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def get_field_options_rfc7807(
    dataset_name: str = Field(..., alias="datasetName", description="The name of the dataset whose field options you want to retrieve."),
    fields: list[str] = Field(..., description="One or more field names whose possible values should be returned; order is not significant and each entry should be a valid field name within the dataset."),
    dependent_fields: dict[str, list[_models.GetFieldOptionsV12BodyDependentFieldsValueItem]] | None = Field(None, alias="dependentFields", description="A map of field names to dependent field/value pairs that constrain the options returned for those fields, used when one field's valid options depend on the selected value of another field."),
    filters: dict[str, Any] | None = Field(None, description="An optional filter object that scopes the returned options to only those consistent with the specified field conditions, using match mode and a list of field/operator/value filter rules."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the available filter values for one or more fields in a dataset, returning an object keyed by field name where each value is an array of id/value pairs. Use the returned id values when constructing filters for dataset queries."""

    # Construct request model with validation
    try:
        _request = _models.GetFieldOptionsV12Request(
            path=_models.GetFieldOptionsV12RequestPath(dataset_name=dataset_name),
            body=_models.GetFieldOptionsV12RequestBody(fields=fields, dependent_fields=dependent_fields, filters=filters)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_field_options_rfc7807: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1_2/datasets/{datasetName}/field-options", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1_2/datasets/{datasetName}/field-options"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_field_options_rfc7807")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_field_options_rfc7807", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_field_options_rfc7807",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Public API, Applicant Tracking
@mcp.tool(
    title="List Applications",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_applications(
    page: int | None = Field(None, description="The page number to retrieve for paginated results."),
    job_id: int | None = Field(None, alias="jobId", description="Filters results to only applications associated with the specified job ID."),
    application_status_id: str | None = Field(None, alias="applicationStatusId", description="Filters results to applications matching one or more specific application status IDs, provided as a comma-separated list of numeric IDs."),
    application_status: str | None = Field(None, alias="applicationStatus", description="Filters results by one or more high-level application status group codes, provided as a comma-separated list. Use ALL to return all statuses, ALL_ACTIVE for any active state, or specific codes such as NEW, ACTIVE, INACTIVE, or HIRED."),
    job_status_groups: str | None = Field(None, alias="jobStatusGroups", description="Filters results by one or more job position status groups, provided as a comma-separated list. Use ALL to include every status, or target specific states such as Open, Filled, Draft, Deleted, On Hold, or Canceled."),
    search_string: str | None = Field(None, alias="searchString", description="A general keyword or search string used to find matching applications across relevant fields such as applicant name or job title."),
    sort_by: Literal["first_name", "job_title", "rating", "phone", "status", "last_updated", "created_date"] | None = Field(None, alias="sortBy", description="The field by which to sort the returned applications."),
    sort_order: Literal["ASC", "DESC"] | None = Field(None, alias="sortOrder", description="The direction in which to sort results — ascending (ASC) or descending (DESC)."),
    new_since: str | None = Field(None, alias="newSince", description="Restricts results to applications submitted after the specified UTC timestamp. Must follow the format Y-m-d H:i:s."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of job applications from the Applicant Tracking System (ATS). Supports filtering by job, application status, position status, and submission date, with flexible sorting options."""

    # Construct request model with validation
    try:
        _request = _models.GetApplicationsRequest(
            query=_models.GetApplicationsRequestQuery(page=page, job_id=job_id, application_status_id=application_status_id, application_status=application_status, job_status_groups=job_status_groups, search_string=search_string, sort_by=sort_by, sort_order=sort_order, new_since=new_since)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_applications: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/applicant_tracking/applications"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_applications")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_applications", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_applications",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Public API, Applicant Tracking
@mcp.tool(
    title="List Applicant Statuses",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_applicant_statuses() -> dict[str, Any] | ToolResult:
    """Retrieves all applicant tracking statuses configured for the company, including both system-defined and custom statuses. Requires the API key owner to have access to ATS settings."""

    # Extract parameters for API call
    _http_path = "/api/v1/applicant_tracking/statuses"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_applicant_statuses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_applicant_statuses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_applicant_statuses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Public API, Applicant Tracking
@mcp.tool(
    title="List Job Locations",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_job_locations() -> dict[str, Any] | ToolResult:
    """Retrieves all company locations available for use when creating a job opening in the Applicant Tracking System. Requires ATS settings access; use the returned location IDs as the `jobLocation` field when creating a job opening."""

    # Extract parameters for API call
    _http_path = "/api/v1/applicant_tracking/locations"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_job_locations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_job_locations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_job_locations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Public API, Applicant Tracking
@mcp.tool(
    title="List Hiring Leads",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_hiring_leads() -> dict[str, Any] | ToolResult:
    """Retrieves the list of employees eligible to be assigned as a hiring lead on a job opening. Use the returned `employeeId` values as the `hiringLead` field when creating a new job opening via the Create Job Opening endpoint."""

    # Extract parameters for API call
    _http_path = "/api/v1/applicant_tracking/hiring_leads"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_hiring_leads")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_hiring_leads", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_hiring_leads",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Public API, Applicant Tracking
@mcp.tool(
    title="Create Candidate",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_candidate(
    first_name: str = Field(..., alias="firstName", description="The candidate's first name."),
    last_name: str = Field(..., alias="lastName", description="The candidate's last name."),
    job_id: int = Field(..., alias="jobId", description="The unique identifier of the job opening this application is being submitted for."),
    email: str | None = Field(None, description="The candidate's email address, used for communication and deduplication."),
    phone_number: str | None = Field(None, alias="phoneNumber", description="The candidate's phone number, including country code if applicable."),
    source: str | None = Field(None, description="The channel or platform through which the candidate was sourced, such as a job board or professional network."),
    address: str | None = Field(None, description="The candidate's street address."),
    city: str | None = Field(None, description="The city of the candidate's address."),
    state: str | None = Field(None, description="The state or province of the candidate's address; accepts full name, abbreviation, or ISO code."),
    zip_: str | None = Field(None, alias="zip", description="The zip or postal code of the candidate's address."),
    country: str | None = Field(None, description="The country of the candidate's address; accepts full country name or ISO country code."),
    linkedin_url: str | None = Field(None, alias="linkedinUrl", description="The candidate's LinkedIn profile URL; must be a valid LinkedIn URL matching the required domain pattern."),
    date_available: str | None = Field(None, alias="dateAvailable", description="The date the candidate is available to start, in ISO 8601 date format (YYYY-MM-DD)."),
    desired_salary: str | None = Field(None, alias="desiredSalary", description="The candidate's desired compensation or salary expectation."),
    referred_by: str | None = Field(None, alias="referredBy", description="The name of the person or organization that referred the candidate."),
    website_url: str | None = Field(None, alias="websiteUrl", description="The URL of the candidate's personal website, blog, or online portfolio; must be a valid URL."),
    highest_education: Literal["GED or Equivalent", "High School", "Some College", "College - Associates", "College - Bachelor of Arts", "College - Bachelor of Fine Arts", "College - Bachelor of Science", "College - Master of Arts", "College - Master of Fine Arts", "College - Master of Science", "College - Master of Business Administration", "College - Doctorate", "Medical Doctor", "Other"] | None = Field(None, alias="highestEducation", description="The highest level of education the candidate has completed; must match one of the predefined education level values."),
    college_name: str | None = Field(None, alias="collegeName", description="The name of the college or university the candidate attended."),
    references: str | None = Field(None, description="Professional or personal references provided by the candidate."),
    resume: str | None = Field(None, description="Base64-encoded file content for upload. The candidate's resume file; accepted formats include PDF, Word documents, plain text, RTF, and common image types.", json_schema_extra={'format': 'byte'}),
    cover_letter: str | None = Field(None, alias="coverLetter", description="Base64-encoded file content for upload. The candidate's cover letter file; accepted formats include PDF, Word documents, plain text, RTF, and common image types.", json_schema_extra={'format': 'byte'}),
) -> dict[str, Any] | ToolResult:
    """Submit a new candidate application for a specific job opening in the Applicant Tracking System. Requires ATS settings access; only fields mandated by the target job's standard questions need to be provided beyond the three required fields."""

    # Construct request model with validation
    try:
        _request = _models.CreateCandidateRequest(
            body=_models.CreateCandidateRequestBody(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number, source=source, job_id=job_id, address=address, city=city, state=state, zip_=zip_, country=country, linkedin_url=linkedin_url, date_available=date_available, desired_salary=desired_salary, referred_by=referred_by, website_url=website_url, highest_education=highest_education, college_name=college_name, references=references, resume=resume, cover_letter=cover_letter)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_candidate: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/applicant_tracking/application"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_candidate")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_candidate", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_candidate",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["resume", "coverLetter"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Public API, Applicant Tracking
@mcp.tool(
    title="Create Job Opening",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_job_opening(
    posting_title: str = Field(..., alias="postingTitle", description="The public-facing title of the job opening as it will appear in postings."),
    job_status: Literal["Draft", "Open", "On Hold", "Filled", "Canceled"] = Field(..., alias="jobStatus", description="The current workflow status of the job opening, controlling its visibility and availability in the hiring pipeline."),
    hiring_lead: int = Field(..., alias="hiringLead", description="The employee ID of the person responsible for leading the hiring process, obtained from the list_hiring_leads endpoint."),
    employment_type: str = Field(..., alias="employmentType", description="The employment arrangement type for the role, such as full-time, part-time, or contractor."),
    job_description: str = Field(..., alias="jobDescription", description="The full descriptive text of the job opening, including responsibilities, qualifications, and any other relevant details presented to applicants."),
    department: str | None = Field(None, description="The name of the department this job opening belongs to within the organization."),
    minimum_experience: Literal["Entry-level", "Mid-level", "Experienced", "Manager/Supervisor", "Senior Manager/Supervisor'", "Executive", "Senior Executive"] | None = Field(None, alias="minimumExperience", description="The minimum career experience level required for a candidate to qualify for this role."),
    compensation: str | None = Field(None, description="The pay rate or compensation package details for the job opening, such as salary range or hourly rate."),
    job_location: int | None = Field(None, alias="jobLocation", description="The location ID for the job's physical workplace, obtained from the list_company_locations endpoint. Omit for fully remote positions; required when locationType is 0 (on-site) or 2 (hybrid)."),
    application_question_resume: Literal["true", "false", "Required"] | None = Field(None, alias="applicationQuestionResume", description="Controls whether the resume upload field appears on the application form: hidden, optional, or mandatory."),
    application_question_address: Literal["true", "false", "Required"] | None = Field(None, alias="applicationQuestionAddress", description="Controls whether the address field appears on the application form: hidden, optional, or mandatory."),
    application_question_linkedin_url: Literal["true", "false", "Required"] | None = Field(None, alias="applicationQuestionLinkedinUrl", description="Controls whether the LinkedIn profile URL field appears on the application form: hidden, optional, or mandatory."),
    application_question_date_available: Literal["true", "false", "Required"] | None = Field(None, alias="applicationQuestionDateAvailable", description="Controls whether the availability start date field appears on the application form: hidden, optional, or mandatory."),
    application_question_desired_salary: Literal["true", "false", "Required"] | None = Field(None, alias="applicationQuestionDesiredSalary", description="Controls whether the desired salary field appears on the application form: hidden, optional, or mandatory."),
    application_question_cover_letter: Literal["true", "false", "Required"] | None = Field(None, alias="applicationQuestionCoverLetter", description="Controls whether the cover letter upload field appears on the application form: hidden, optional, or mandatory."),
    application_question_referred_by: Literal["true", "false", "Required"] | None = Field(None, alias="applicationQuestionReferredBy", description="Controls whether the referral source field appears on the application form: hidden, optional, or mandatory."),
    application_question_website_url: Literal["true", "false", "Required"] | None = Field(None, alias="applicationQuestionWebsiteUrl", description="Controls whether the personal or portfolio website URL field appears on the application form: hidden, optional, or mandatory."),
    application_question_highest_education: Literal["true", "false", "Required"] | None = Field(None, alias="applicationQuestionHighestEducation", description="Controls whether the highest education level field appears on the application form: hidden, optional, or mandatory."),
    application_question_college: Literal["true", "false", "Required"] | None = Field(None, alias="applicationQuestionCollege", description="Controls whether the college or university attended field appears on the application form: hidden, optional, or mandatory."),
    application_question_references: Literal["true", "false", "Required"] | None = Field(None, alias="applicationQuestionReferences", description="Controls whether the professional references field appears on the application form: hidden, optional, or mandatory."),
    internal_job_code: str | None = Field(None, alias="internalJobCode", description="An internal identifier or code used by your organization to track or categorize this job opening."),
    location_type: Literal[0, 1, 2] | None = Field(None, alias="locationType", description="Specifies the work arrangement type: 0 = on-site (requires jobLocation), 1 = fully remote (no jobLocation), 2 = hybrid (requires jobLocation). Defaults to 1 when no jobLocation is provided, or 0 when jobLocation is provided."),
) -> dict[str, Any] | ToolResult:
    """Creates a new job opening in the Applicant Tracking System (ATS). Requires ATS settings access; use the list_company_locations and list_hiring_leads endpoints to retrieve valid IDs for location and hiring lead fields. Returns the new job opening ID on success."""

    # Construct request model with validation
    try:
        _request = _models.CreateJobOpeningRequest(
            body=_models.CreateJobOpeningRequestBody(posting_title=posting_title, job_status=job_status, hiring_lead=hiring_lead, department=department, employment_type=employment_type, minimum_experience=minimum_experience, compensation=compensation, job_location=job_location, job_description=job_description, application_question_resume=application_question_resume, application_question_address=application_question_address, application_question_linkedin_url=application_question_linkedin_url, application_question_date_available=application_question_date_available, application_question_desired_salary=application_question_desired_salary, application_question_cover_letter=application_question_cover_letter, application_question_referred_by=application_question_referred_by, application_question_website_url=application_question_website_url, application_question_highest_education=application_question_highest_education, application_question_college=application_question_college, application_question_references=application_question_references, internal_job_code=internal_job_code, location_type=location_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_job_opening: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/applicant_tracking/job_opening"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_job_opening")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_job_opening", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_job_opening",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: Benefits, Public API
@mcp.tool(
    title="List Company Benefits",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_company_benefits() -> dict[str, Any] | ToolResult:
    """Retrieves all active (non-deleted) company benefit plans for the account, including summary-level details such as name, benefit category type, associated vendor and deduction IDs, effective date range, and catch-up eligibility flags. For full plan details including SSO URL, description, and ACA fields, use get_company_benefit with a specific plan ID."""

    # Extract parameters for API call
    _http_path = "/api/v1/benefit/company_benefit"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_company_benefits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_company_benefits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_company_benefits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Benefits, Public API
@mcp.tool(
    title="List Employee Benefits",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_employee_benefits(
    employee_id: int | None = Field(None, alias="employeeId", description="Filters results to benefit enrollments belonging to a specific employee, identified by their unique numeric ID."),
    company_benefit_id: int | None = Field(None, alias="companyBenefitId", description="Filters results to enrollments associated with a specific company benefit plan, identified by its unique numeric ID."),
    enrollment_status_effective_date: str | None = Field(None, alias="enrollmentStatusEffectiveDate", description="Filters results to enrollments whose status became effective on the specified date, provided in YYYY-MM-DD format."),
) -> dict[str, Any] | ToolResult:
    """Retrieves current and future benefit enrollment records for one or more employees, grouped by employee, including plan details, enrollment status, deduction amounts, and cost-sharing information. At least one filter — employee ID, company benefit plan ID, or enrollment status effective date — must be provided."""

    # Construct request model with validation
    try:
        _request = _models.ListEmployeeBenefitsRequest(
            body=_models.ListEmployeeBenefitsRequestBody(filters=_models.ListEmployeeBenefitsRequestBodyFilters(employee_id=employee_id, company_benefit_id=company_benefit_id, enrollment_status_effective_date=enrollment_status_effective_date) if any(v is not None for v in [employee_id, company_benefit_id, enrollment_status_effective_date]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_employee_benefits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/benefit/employee_benefit"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_employee_benefits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_employee_benefits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_employee_benefits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Benefits, Public API
@mcp.tool(
    title="List Member Benefit Events",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_member_benefit_events() -> dict[str, Any] | ToolResult:
    """Retrieves benefit enrollment events for all employees and their dependents over the past year, organized by member. Each entry identifies a member and lists their per-plan coverage events (eligibility granted, enrolled, or loss of coverage) in chronological order. Requires benefit settings access."""

    # Extract parameters for API call
    _http_path = "/api/v1/benefit/member_benefit"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_member_benefit_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_member_benefit_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_member_benefit_events",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Benefits, Public API
@mcp.tool(
    title="List Member Benefits",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_member_benefits(
    calendar_year: str = Field(..., alias="calendarYear", description="The four-digit calendar year for which to retrieve benefit enrollment data, in YYYY format.", pattern="^\\d{4}$"),
    page: str | None = Field(None, description="The 1-based page number to retrieve; values that resolve to zero or below are rejected with a 400. Defaults to 1."),
    page_size: str | None = Field(None, alias="pageSize", description="The number of benefit records to return per page; must resolve to an integer between 1 and 99 inclusive, otherwise a 400 is returned. Defaults to 25."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of benefit enrollment records for all members (employees and dependents) in the company for a specified calendar year, including each member's plans and enrollment status date ranges. Requires benefit admin privileges; non-admin callers receive a 403."""

    # Construct request model with validation
    try:
        _request = _models.GetMemberBenefitsRequest(
            query=_models.GetMemberBenefitsRequestQuery(calendar_year=calendar_year, page=page, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_member_benefits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/benefits/member-benefits"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_member_benefits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_member_benefits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_member_benefits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Benefits, Public API
@mcp.tool(
    title="List Benefit Deduction Types",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_benefit_deduction_types() -> dict[str, Any] | ToolResult:
    """Retrieves all benefit deduction types available in the system, including categories such as 401(k), HSA, and Section 125, along with their allowable plan types, default deduction codes, and any sub-types. Requires Benefits Administration permissions."""

    # Extract parameters for API call
    _http_path = "/api/v1/benefits/settings/deduction_types/all"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_benefit_deduction_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_benefit_deduction_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_benefit_deduction_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Employees, Public API
@mcp.tool(
    title="Get Company Profile",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_company_profile() -> dict[str, Any] | ToolResult:
    """Retrieves the company's basic profile information, including legal name, display name, primary address, and contact phone number. Data is sourced from active payroll client metadata for BambooHR Payroll companies, or from account settings for all others."""

    # Extract parameters for API call
    _http_path = "/api/v1/company_information"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_company_profile")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_company_profile", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_company_profile",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Company Profile, Public API
@mcp.tool(
    title="List Enabled Integrations",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_enabled_integrations() -> dict[str, Any] | ToolResult:
    """Retrieves the list of integration and feature identifiers currently enabled for the company. Each identifier is an uppercase string key representing an activated product feature or integration, reflecting the company's current subscription and configuration."""

    # Extract parameters for API call
    _http_path = "/api/v1/company-profile-integrations"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_enabled_integrations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_enabled_integrations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_enabled_integrations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Employees, Public API
@mcp.tool(
    title="List Employees",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_employees(
    filter_: _models.GetEmployeesFilterRequestObject | None = Field(None, alias="filter", description="Narrows results to employees matching the specified field criteria, encoded as a deepObject. Employees for which the caller lacks permission to view the filtered field are excluded entirely from results."),
    sort: str | None = Field(None, description="Comma-separated list of fields to sort by, where a leading hyphen indicates descending order; sortable fields are limited to the core default set. Employees for which the caller lacks permission to view the sort field are excluded from results, and nulls sort first ascending and last descending."),
    fields: str | None = Field(None, description="Comma-separated list of additional contact or social fields to include beyond the default set, up to 14 supported values. Unrecognized field names are silently ignored, and fields the caller lacks permission to view will be null or omitted with the field name listed in the record's `_restrictedFields` array."),
    page: _models.CursorPaginationQueryObject | None = Field(None, description="Cursor-based pagination control accepting `limit`, `after`, and `before` parameters to navigate through result pages."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of employees, each including core identity and job fields by default, with optional filtering, sorting, and additional contact or social fields. Use the Get Employee endpoint or Datasets API for more comprehensive field coverage."""

    # Construct request model with validation
    try:
        _request = _models.ListEmployeesRequest(
            query=_models.ListEmployeesRequestQuery(filter_=filter_, sort=sort, fields=fields, page=page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_employees: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/employees"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "filter": ("deepObject", True),
        "page": ("deepObject", True),
    })
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_employees")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_employees", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_employees",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Employees, Public API
@mcp.tool(
    title="Create Employee",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_employee(
    first_name: str = Field(..., alias="firstName", description="Employee's legal first name as it should appear on official records and payroll documents."),
    last_name: str = Field(..., alias="lastName", description="Employee's legal last name as it should appear on official records and payroll documents."),
    work_email: str | None = Field(None, alias="workEmail", description="Employee's work email address used for company communications and system access."),
    job_title: str | None = Field(None, alias="jobTitle", description="Employee's job title reflecting their role or position within the organization."),
    department: str | None = Field(None, description="Name of the department the employee belongs to; must match an existing department name in the system."),
    hire_date: str | None = Field(None, alias="hireDate", description="The date the employee was officially hired, formatted as a calendar date in YYYY-MM-DD format."),
) -> dict[str, Any] | ToolResult:
    """Creates a new employee record with at minimum a first and last name; additional fields such as payroll, contact, and job details can be included using any valid employee field name discoverable via the list-fields endpoint. Employees added to a Trax Payroll-synced pay schedule require a full set of payroll-related fields including SSN/EIN, compensation, and location details."""

    # Construct request model with validation
    try:
        _request = _models.CreateEmployeeRequest(
            body=_models.CreateEmployeeRequestBody(first_name=first_name, last_name=last_name, work_email=work_email, job_title=job_title, department=department, hire_date=hire_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_employee: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/employees"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_employee")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_employee", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_employee",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tabular Data, Public API
@mcp.tool(
    title="Update Employee Table Row",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def update_employee_table_row(
    id_: str = Field(..., alias="id", description="The unique identifier of the employee whose table row will be updated."),
    table: str = Field(..., description="The name of the employee table containing the row to update, such as job information or compensation tables."),
    row_id: str = Field(..., alias="rowId", description="The unique identifier of the specific row within the table to be updated."),
    date: str | None = Field(None, description="The effective date for the row update in YYYY-MM-DD format, determining when the change takes effect."),
    location: str | None = Field(None, description="The office or work location value to assign to this row."),
    division: str | None = Field(None, description="The organizational division value to assign to this row."),
    department: str | None = Field(None, description="The department value to assign to this row."),
    job_title: str | None = Field(None, alias="jobTitle", description="The job title value to assign to this row."),
    reports_to: str | None = Field(None, alias="reportsTo", description="The identifier of the manager or supervisor this employee reports to for this row."),
    teams: list[str] | None = Field(None, description="A list of team identifiers or names associated with this row; order is not significant and each item represents a single team assignment."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing row in a specified employee table by submitting one or more field name/value pairs to modify. Targets a specific row by ID within tables such as job information or compensation history."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTableRowRequest(
            path=_models.UpdateTableRowRequestPath(id_=id_, table=table, row_id=row_id),
            body=_models.UpdateTableRowRequestBody(date=date, location=location, division=division, department=department, job_title=job_title, reports_to=reports_to, teams=teams)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_employee_table_row: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{id}/tables/{table}/{rowId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{id}/tables/{table}/{rowId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_employee_table_row")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_employee_table_row", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_employee_table_row",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tabular Data, Public API
@mcp.tool(
    title="Delete Employee Table Row",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_employee_table_row(
    id_: str = Field(..., alias="id", description="The unique identifier of the employee whose tabular data is being modified."),
    table: str = Field(..., description="The name of the tabular dataset from which the row will be deleted, such as job history, compensation records, or a custom tabular field."),
    row_id: str = Field(..., alias="rowId", description="The unique identifier of the specific row to delete within the targeted table."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a specific row from a named tabular dataset associated with an employee. Deletion will fail if the row has pending approval changes (409) or is tied to an active pay schedule (412)."""

    # Construct request model with validation
    try:
        _request = _models.DeleteEmployeeTableRowRequest(
            path=_models.DeleteEmployeeTableRowRequestPath(id_=id_, table=table, row_id=row_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_employee_table_row: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{id}/tables/{table}/{rowId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{id}/tables/{table}/{rowId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_employee_table_row")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_employee_table_row", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_employee_table_row",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Company Files, Public API
@mcp.tool(
    title="Download Company File",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def download_company_file(file_id: int = Field(..., alias="fileId", description="The unique identifier of the company file to download.")) -> dict[str, Any] | ToolResult:
    """Downloads the raw content of a company file by its ID, with the response including the appropriate MIME type and original filename as an attachment. Access is granted if the file or its category is shared with employees, shared directly with the requesting user, or the user holds view permission on the file section."""

    # Construct request model with validation
    try:
        _request = _models.GetCompanyFileRequest(
            path=_models.GetCompanyFileRequestPath(file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for download_company_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/files/{fileId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/files/{fileId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("download_company_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("download_company_file", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="download_company_file",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Company Files, Public API
@mcp.tool(
    title="Update Company File",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def update_company_file(
    file_id: int = Field(..., alias="fileId", description="The unique identifier of the company file to update."),
    name: str | None = Field(None, description="The new display name to assign to the file."),
    category_id: str | None = Field(None, alias="categoryId", description="The identifier of the category (file section) to move the file into."),
    share_with_employee: Literal["yes", "no"] | None = Field(None, alias="shareWithEmployee", description="Controls whether the file is visible and accessible to employees; set to 'yes' to share or 'no' to restrict access."),
) -> dict[str, Any] | ToolResult:
    """Updates metadata for an existing company file, including its display name, category, and employee visibility. Only fields included in the request body are modified; omitted fields remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCompanyFileRequest(
            path=_models.UpdateCompanyFileRequestPath(file_id=file_id),
            body=_models.UpdateCompanyFileRequestBody(name=name, category_id=category_id, share_with_employee=share_with_employee)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_company_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/files/{fileId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/files/{fileId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_company_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_company_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_company_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Company Files, Public API
@mcp.tool(
    title="Delete Company File",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_company_file(file_id: int = Field(..., alias="fileId", description="The unique numeric identifier of the company file to delete. Must correspond to an existing file the caller has write access to.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a company file by its unique identifier. Requires write access to company files; returns 404 if the file is not found or 403 if the caller lacks sufficient permissions."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCompanyFileRequest(
            path=_models.DeleteCompanyFileRequestPath(file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_company_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/files/{fileId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/files/{fileId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_company_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_company_file", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_company_file",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Employee Files, Public API
@mcp.tool(
    title="Download Employee File",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def download_employee_file(
    id_: int = Field(..., alias="id", description="The numeric ID of the employee whose file is being downloaded. Pass 0 to automatically resolve to the employee associated with the API key."),
    file_id: int = Field(..., alias="fileId", description="The numeric ID of the specific file to download from the employee's record."),
) -> dict[str, Any] | ToolResult:
    """Downloads the binary content of a specific file attached to an employee record, returning it as an attachment with the appropriate MIME type. Returns 403 if access to the employee or file section is denied, and 404 if the file does not exist or is archived."""

    # Construct request model with validation
    try:
        _request = _models.GetEmployeeFileRequest(
            path=_models.GetEmployeeFileRequestPath(id_=id_, file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for download_employee_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{id}/files/{fileId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{id}/files/{fileId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("download_employee_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("download_employee_file", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="download_employee_file",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Employee Files, Public API
@mcp.tool(
    title="Update Employee File",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def update_employee_file(
    id_: int = Field(..., alias="id", description="The unique identifier of the employee whose file is being updated."),
    file_id: int = Field(..., alias="fileId", description="The unique identifier of the employee file to update."),
    name: str | None = Field(None, description="The new display name to assign to the file. Omit this field to leave the current name unchanged."),
    category_id: int | None = Field(None, alias="categoryId", description="The ID of the file category (section) to move the file into. Omit this field to leave the file in its current category."),
    share_with_employee: Literal["yes", "no"] | None = Field(None, alias="shareWithEmployee", description="Controls whether the file is visible to the employee. Accepts 'yes' to share or 'no' to hide; also accepted as 'shareWithEmployees'."),
) -> dict[str, Any] | ToolResult:
    """Updates metadata for an existing employee file, supporting renaming, category reassignment, and toggling employee visibility. Only fields included in the request body are modified; omitted fields remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.UpdateEmployeeFileRequest(
            path=_models.UpdateEmployeeFileRequestPath(id_=id_, file_id=file_id),
            body=_models.UpdateEmployeeFileRequestBody(name=name, category_id=category_id, share_with_employee=share_with_employee)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_employee_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{id}/files/{fileId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{id}/files/{fileId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_employee_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_employee_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_employee_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Employee Files, Public API
@mcp.tool(
    title="Delete Employee File",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_employee_file(
    id_: int = Field(..., alias="id", description="The numeric ID of the employee whose file will be deleted. Pass 0 to automatically resolve to the employee associated with the API key."),
    file_id: int = Field(..., alias="fileId", description="The numeric ID of the specific file to delete from the employee's record."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific file associated with an employee record. Returns 200 even if the file was already deleted (idempotent), 404 if the file is not linked to the specified employee, and 403 if the caller lacks permission or the file is managed by BambooPayroll."""

    # Construct request model with validation
    try:
        _request = _models.DeleteEmployeeFileRequest(
            path=_models.DeleteEmployeeFileRequestPath(id_=id_, file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_employee_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{id}/files/{fileId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{id}/files/{fileId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_employee_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_employee_file", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_employee_file",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="List Employee Goals",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_employee_goals(
    employee_id: str = Field(..., alias="employeeId", description="The unique identifier of the employee whose goals should be retrieved."),
    filter_: str | None = Field(None, alias="filter", description="Restricts results to goals matching the specified status. Accepted values are `status-inProgress`, `status-completed`, and `status-closed`; if omitted, all goals are returned regardless of status. Unrecognized values may be silently ignored."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of goals assigned to a specific employee, optionally filtered by goal status. Returns up to 50 goals in a `goals` array."""

    # Construct request model with validation
    try:
        _request = _models.ListGoalsRequest(
            path=_models.ListGoalsRequestPath(employee_id=employee_id),
            query=_models.ListGoalsRequestQuery(filter_=filter_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_employee_goals: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/performance/employees/{employeeId}/goals", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/performance/employees/{employeeId}/goals"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_employee_goals")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_employee_goals", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_employee_goals",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="Create Employee Goal",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_employee_goal(
    employee_id: str = Field(..., alias="employeeId", description="The unique identifier of the employee for whom the goal is being created."),
    title: str = Field(..., description="A short, descriptive title for the goal."),
    due_date: str = Field(..., alias="dueDate", description="The target completion date for the goal in YYYY-MM-DD format (ISO 8601)."),
    shared_with_employee_ids: list[int] = Field(..., alias="sharedWithEmployeeIds", description="An unordered list of employee IDs who can view this goal. Must include the goal owner's employee ID."),
    description: str | None = Field(None, description="A detailed explanation of the goal's purpose, expectations, or scope."),
    percent_complete: int | None = Field(None, alias="percentComplete", description="How far along the goal is, expressed as a whole number between 0 and 100. Defaults to 0 if not provided. A value of 100 indicates the goal is fully complete and requires a completionDate.", ge=0, le=100),
    completion_date: str | None = Field(None, alias="completionDate", description="The date the goal was completed in YYYY-MM-DD format (ISO 8601). Must be provided when percentComplete is set to 100."),
    aligns_with_option_id: int | None = Field(None, alias="alignsWithOptionId", description="The identifier of a predefined alignment option that this goal supports, used to link the goal to broader organizational objectives."),
    milestones: list[_models.CreateGoalBodyMilestonesItem] | None = Field(None, description="An ordered list of milestone objects that break the goal into smaller steps. Each milestone requires a title field and is tracked independently."),
) -> dict[str, Any] | ToolResult:
    """Creates a new performance goal for a specified employee, including due dates, completion tracking, milestones, and sharing with other employees."""

    # Construct request model with validation
    try:
        _request = _models.CreateGoalRequest(
            path=_models.CreateGoalRequestPath(employee_id=employee_id),
            body=_models.CreateGoalRequestBody(title=title, description=description, due_date=due_date, percent_complete=percent_complete, completion_date=completion_date, shared_with_employee_ids=shared_with_employee_ids, aligns_with_option_id=aligns_with_option_id, milestones=milestones)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_employee_goal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/performance/employees/{employeeId}/goals", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/performance/employees/{employeeId}/goals"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_employee_goal")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_employee_goal", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_employee_goal",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="Delete Employee Goal",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_employee_goal(
    employee_id: str = Field(..., alias="employeeId", description="The unique identifier of the employee whose goal is being deleted."),
    goal_id: str = Field(..., alias="goalId", description="The unique identifier of the goal to permanently delete, which must belong to the specified employee."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific goal associated with an employee. The goal must belong to the specified employee; returns 204 with no response body on success."""

    # Construct request model with validation
    try:
        _request = _models.DeleteGoalRequest(
            path=_models.DeleteGoalRequestPath(employee_id=employee_id, goal_id=goal_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_employee_goal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/performance/employees/{employeeId}/goals/{goalId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/performance/employees/{employeeId}/goals/{goalId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_employee_goal")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_employee_goal", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_employee_goal",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="Update Goal Progress",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_goal_progress(
    employee_id: int = Field(..., alias="employeeId", description="The unique identifier of the employee whose goal progress is being updated."),
    goal_id: int = Field(..., alias="goalId", description="The unique identifier of the goal to update for the specified employee."),
    percent_complete: int = Field(..., alias="percentComplete", description="The current completion percentage of the goal, expressed as a whole number between 0 (not started) and 100 (fully complete).", ge=0, le=100),
    completion_date: str | None = Field(None, alias="completionDate", description="The date the goal was completed in YYYY-MM-DD format. Must be provided when percentComplete is 100."),
) -> dict[str, Any] | ToolResult:
    """Updates the completion percentage of a specific employee goal, optionally recording the completion date when the goal is fully achieved."""

    # Construct request model with validation
    try:
        _request = _models.UpdateGoalProgressRequest(
            path=_models.UpdateGoalProgressRequestPath(employee_id=employee_id, goal_id=goal_id),
            body=_models.UpdateGoalProgressRequestBody(percent_complete=percent_complete, completion_date=completion_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_goal_progress: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/performance/employees/{employeeId}/goals/{goalId}/progress", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/performance/employees/{employeeId}/goals/{goalId}/progress"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_goal_progress")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_goal_progress", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_goal_progress",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="Update Milestone Progress",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_milestone_progress(
    employee_id: str = Field(..., alias="employeeId", description="The unique identifier of the employee whose goal milestone is being updated."),
    goal_id: str = Field(..., alias="goalId", description="The unique identifier of the goal that contains the milestone to be updated."),
    milestone_id: str = Field(..., alias="milestoneId", description="The unique identifier of the milestone whose progress is being updated."),
    complete: bool = Field(..., description="Indicates whether the milestone has been completed. Set to true to mark the milestone as complete, or false to mark it as incomplete."),
) -> dict[str, Any] | ToolResult:
    """Updates the completion status of a specific milestone within an employee's goal. Use this to mark a milestone as complete or incomplete as part of tracking goal progress."""

    # Construct request model with validation
    try:
        _request = _models.UpdateGoalMilestoneProgressRequest(
            path=_models.UpdateGoalMilestoneProgressRequestPath(employee_id=employee_id, goal_id=goal_id, milestone_id=milestone_id),
            body=_models.UpdateGoalMilestoneProgressRequestBody(complete=complete)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_milestone_progress: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/performance/employees/{employeeId}/goals/{goalId}/milestones/{milestoneId}/progress", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/performance/employees/{employeeId}/goals/{goalId}/milestones/{milestoneId}/progress"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_milestone_progress")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_milestone_progress", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_milestone_progress",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="Set Goal Sharing",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def set_goal_sharing(
    employee_id: str = Field(..., alias="employeeId", description="The unique identifier of the employee who owns the goal."),
    goal_id: str = Field(..., alias="goalId", description="The unique identifier of the goal whose sharing list will be replaced."),
    shared_with_employee_ids: list[int] | None = Field(None, alias="sharedWithEmployeeIds", description="The complete, replacement list of employee IDs with whom the goal should be shared. Must include the goal owner's employee ID; order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Replaces the complete list of employees a goal is shared with, overwriting any previous sharing configuration. The goal owner's employee ID must be included in the updated list."""

    # Construct request model with validation
    try:
        _request = _models.UpdateGoalSharingRequest(
            path=_models.UpdateGoalSharingRequestPath(employee_id=employee_id, goal_id=goal_id),
            body=_models.UpdateGoalSharingRequestBody(shared_with_employee_ids=shared_with_employee_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_goal_sharing: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/performance/employees/{employeeId}/goals/{goalId}/sharedWith", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/performance/employees/{employeeId}/goals/{goalId}/sharedWith"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_goal_sharing")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_goal_sharing", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_goal_sharing",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="List Goal Share Options",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_goal_share_options(
    employee_id: str = Field(..., alias="employeeId", description="The unique identifier of the employee whose goal sharing options are being retrieved."),
    search: str = Field(..., description="A search term to filter the returned employees by name, employee ID, or email address. Must be provided to return results."),
    limit: int | None = Field(None, description="Maximum number of employees to include in the response. Accepts values between 1 and 100, defaulting to 10 if not specified.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of employees with whom the specified employee's goals can be shared. Results are filtered by a search term matching name, employee ID, or email."""

    # Construct request model with validation
    try:
        _request = _models.ListGoalShareOptionsRequest(
            path=_models.ListGoalShareOptionsRequestPath(employee_id=employee_id),
            query=_models.ListGoalShareOptionsRequestQuery(search=search, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_goal_share_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/performance/employees/{employeeId}/goals/shareOptions", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/performance/employees/{employeeId}/goals/shareOptions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_goal_share_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_goal_share_options", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_goal_share_options",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="List Goal Comments",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_goal_comments(
    employee_id: str = Field(..., alias="employeeId", description="The unique identifier of the employee whose goal comments are being retrieved."),
    goal_id: str = Field(..., alias="goalId", description="The unique identifier of the goal for which comments are being listed, scoped to the specified employee."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all comments associated with a specific goal for a given employee. Useful for reviewing feedback, progress notes, and discussion threads tied to a performance goal."""

    # Construct request model with validation
    try:
        _request = _models.ListGoalCommentsRequest(
            path=_models.ListGoalCommentsRequestPath(employee_id=employee_id, goal_id=goal_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_goal_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/performance/employees/{employeeId}/goals/{goalId}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/performance/employees/{employeeId}/goals/{goalId}/comments"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_goal_comments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_goal_comments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_goal_comments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="Add Goal Comment",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_goal_comment(
    employee_id: str = Field(..., alias="employeeId", description="The unique identifier of the employee who owns the goal."),
    goal_id: str = Field(..., alias="goalId", description="The unique identifier of the goal on which the comment will be created."),
    text: str = Field(..., description="The text content of the comment to be added to the goal."),
) -> dict[str, Any] | ToolResult:
    """Adds a new comment to a specific goal belonging to the given employee. Returns the newly created comment object, including its assigned ID."""

    # Construct request model with validation
    try:
        _request = _models.CreateGoalCommentRequest(
            path=_models.CreateGoalCommentRequestPath(employee_id=employee_id, goal_id=goal_id),
            body=_models.CreateGoalCommentRequestBody(text=text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_goal_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/performance/employees/{employeeId}/goals/{goalId}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/performance/employees/{employeeId}/goals/{goalId}/comments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_goal_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_goal_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_goal_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="Update Goal Comment",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_goal_comment(
    employee_id: str = Field(..., alias="employeeId", description="Unique identifier of the employee whose goal contains the comment to be updated."),
    goal_id: str = Field(..., alias="goalId", description="Unique identifier of the goal associated with the specified employee that contains the comment."),
    comment_id: str = Field(..., alias="commentId", description="Unique identifier of the comment to be updated, which must belong to the specified goal."),
    text: str = Field(..., description="The new text content to replace the existing comment body."),
) -> dict[str, Any] | ToolResult:
    """Updates the text of an existing comment on a specific employee goal. The comment, goal, and employee must all be correctly associated for the update to succeed."""

    # Construct request model with validation
    try:
        _request = _models.UpdateGoalCommentRequest(
            path=_models.UpdateGoalCommentRequestPath(employee_id=employee_id, goal_id=goal_id, comment_id=comment_id),
            body=_models.UpdateGoalCommentRequestBody(text=text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_goal_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/performance/employees/{employeeId}/goals/{goalId}/comments/{commentId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/performance/employees/{employeeId}/goals/{goalId}/comments/{commentId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_goal_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_goal_comment", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_goal_comment",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="Delete Goal Comment",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_goal_comment(
    employee_id: str = Field(..., alias="employeeId", description="Unique identifier of the employee whose goal contains the comment to be deleted."),
    goal_id: str = Field(..., alias="goalId", description="Unique identifier of the goal associated with the specified employee that contains the target comment."),
    comment_id: str = Field(..., alias="commentId", description="Unique identifier of the comment to delete from the specified goal."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific comment from an employee's goal. The comment must belong to the specified goal, which must be associated with the specified employee. Returns 204 with no response body on success."""

    # Construct request model with validation
    try:
        _request = _models.DeleteGoalCommentRequest(
            path=_models.DeleteGoalCommentRequestPath(employee_id=employee_id, goal_id=goal_id, comment_id=comment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_goal_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/performance/employees/{employeeId}/goals/{goalId}/comments/{commentId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/performance/employees/{employeeId}/goals/{goalId}/comments/{commentId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_goal_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_goal_comment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_goal_comment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="Get Goal Aggregate",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_goal_aggregate(
    employee_id: str = Field(..., alias="employeeId", description="The unique identifier of the employee whose goal is being retrieved."),
    goal_id: str = Field(..., alias="goalId", description="The unique identifier of the goal for which aggregate information is being fetched."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a comprehensive goal detail view for a specific employee, including the goal's comments, alignment options, and a consolidated list of all persons who are shared on or have commented on the goal. Designed to populate a full goal detail view in a single request."""

    # Construct request model with validation
    try:
        _request = _models.GetGoalAggregateRequest(
            path=_models.GetGoalAggregateRequestPath(employee_id=employee_id, goal_id=goal_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_goal_aggregate: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/performance/employees/{employeeId}/goals/{goalId}/aggregate", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/performance/employees/{employeeId}/goals/{goalId}/aggregate"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_goal_aggregate")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_goal_aggregate", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_goal_aggregate",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="List Goal Alignment Options",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_goal_alignment_options(
    employee_id: str = Field(..., alias="employeeId", description="The unique identifier of the employee whose alignable goal options are being retrieved."),
    goal_id: int | None = Field(None, alias="goalId", description="The ID of the employee's existing goal for which alignment options are being explored. When provided, the goal currently aligned to this goal is included in the results; when omitted, alignment options are returned for the API user."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of goals that a specified employee's goal can be aligned with. When a goal ID is provided, the currently aligned goal is included in the results even if it would otherwise be filtered out."""

    # Construct request model with validation
    try:
        _request = _models.GetAlignableGoalOptionsRequest(
            path=_models.GetAlignableGoalOptionsRequestPath(employee_id=employee_id),
            query=_models.GetAlignableGoalOptionsRequestQuery(goal_id=goal_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_goal_alignment_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/performance/employees/{employeeId}/goals/alignmentOptions", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/performance/employees/{employeeId}/goals/alignmentOptions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_goal_alignment_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_goal_alignment_options", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_goal_alignment_options",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="Close Goal",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def close_goal(
    employee_id: str = Field(..., alias="employeeId", description="The unique identifier of the employee whose goal is being closed."),
    goal_id: str = Field(..., alias="goalId", description="The unique identifier of the goal to be closed, associated with the specified employee."),
    comment: str | None = Field(None, description="An optional note to record alongside the goal closure, useful for documenting the reason or context for closing."),
) -> dict[str, Any] | ToolResult:
    """Closes an employee's goal by transitioning it to closed status, optionally recording a comment at the time of closure. Note: cascading goals that have visible child goals cannot be closed."""

    # Construct request model with validation
    try:
        _request = _models.CloseGoalRequest(
            path=_models.CloseGoalRequestPath(employee_id=employee_id, goal_id=goal_id),
            body=_models.CloseGoalRequestBody(comment=comment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for close_goal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/performance/employees/{employeeId}/goals/{goalId}/close", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/performance/employees/{employeeId}/goals/{goalId}/close"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("close_goal")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("close_goal", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="close_goal",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="Reopen Goal",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def reopen_goal(
    employee_id: str = Field(..., alias="employeeId", description="The unique identifier of the employee whose goal is being reopened."),
    goal_id: str = Field(..., alias="goalId", description="The unique identifier of the closed goal to be reopened for the specified employee."),
) -> dict[str, Any] | ToolResult:
    """Reopens a previously closed goal for the specified employee, returning it to in-progress status. Returns the updated goal object reflecting the new status."""

    # Construct request model with validation
    try:
        _request = _models.ReopenGoalRequest(
            path=_models.ReopenGoalRequestPath(employee_id=employee_id, goal_id=goal_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reopen_goal: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/performance/employees/{employeeId}/goals/{goalId}/reopen", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/performance/employees/{employeeId}/goals/{goalId}/reopen"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reopen_goal")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reopen_goal", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reopen_goal",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="Update Goal with Milestones",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_goal_with_milestones(
    employee_id: int = Field(..., alias="employeeId", description="The unique identifier of the employee who owns the goal being updated."),
    goal_id: int = Field(..., alias="goalId", description="The unique identifier of the goal to update, scoped to the specified employee."),
    title: str = Field(..., description="The display title of the goal."),
    due_date: str = Field(..., alias="dueDate", description="The target completion date for the goal, provided in YYYY-MM-DD format (ISO 8601 date)."),
    shared_with_employee_ids: list[int] = Field(..., alias="sharedWithEmployeeIds", description="The list of employee IDs who have visibility into this goal. Must include the goal owner's employee ID; order is not significant."),
    description: str | None = Field(None, description="A detailed narrative description providing additional context or specifics about the goal."),
    percent_complete: int | None = Field(None, alias="percentComplete", description="The current completion percentage of the goal, expressed as a whole number between 0 and 100. Required when milestones are not enabled for this goal.", ge=0, le=100),
    completion_date: str | None = Field(None, alias="completionDate", description="The date the goal was fully completed, provided in YYYY-MM-DD format (ISO 8601 date). Required when percentComplete is set to 100."),
    aligns_with_option_id: int | None = Field(None, alias="alignsWithOptionId", description="The identifier of the strategic option or objective this goal is aligned with, linking it to a broader organizational priority."),
    milestones_enabled: bool | None = Field(None, alias="milestonesEnabled", description="When set to true, enables milestone tracking for this goal, allowing progress to be measured through individual milestones rather than a single percent-complete value."),
    deleted_milestone_ids: list[int] | None = Field(None, alias="deletedMilestoneIds", description="A list of milestone IDs to permanently remove from this goal. Order is not significant."),
    milestones: list[_models.UpdateGoalV11BodyMilestonesItem] | None = Field(None, description="A list of milestone objects to add to this goal. Each item should represent a discrete, trackable step toward goal completion."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing performance goal for a specified employee, including support for adding, modifying, or deleting milestones within the goal. Use this version (v1.1) instead of v1 when milestone management is required."""

    # Construct request model with validation
    try:
        _request = _models.UpdateGoalV11Request(
            path=_models.UpdateGoalV11RequestPath(employee_id=employee_id, goal_id=goal_id),
            body=_models.UpdateGoalV11RequestBody(title=title, description=description, due_date=due_date, percent_complete=percent_complete, completion_date=completion_date, shared_with_employee_ids=shared_with_employee_ids, aligns_with_option_id=aligns_with_option_id, milestones_enabled=milestones_enabled, deleted_milestone_ids=deleted_milestone_ids, milestones=milestones)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_goal_with_milestones: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1_1/performance/employees/{employeeId}/goals/{goalId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1_1/performance/employees/{employeeId}/goals/{goalId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_goal_with_milestones")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_goal_with_milestones", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_goal_with_milestones",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="Get Goal Filters",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_goal_filters(employee_id: int = Field(..., alias="employeeId", description="The unique identifier of the employee whose goal filter counts should be retrieved.")) -> dict[str, Any] | ToolResult:
    """Retrieves the count of goals grouped by status for a specific employee, including goals that contain milestones. Use this to understand an employee's goal distribution across statuses before fetching detailed goal data."""

    # Construct request model with validation
    try:
        _request = _models.GetGoalsFiltersV12Request(
            path=_models.GetGoalsFiltersV12RequestPath(employee_id=employee_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_goal_filters: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1_2/performance/employees/{employeeId}/goals/filters", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1_2/performance/employees/{employeeId}/goals/filters"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_goal_filters")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_goal_filters", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_goal_filters",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Goals, Public API
@mcp.tool(
    title="Get Employee Goals Aggregate",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_employee_goals_aggregate(
    employee_id: int = Field(..., alias="employeeId", description="The unique numeric identifier of the employee whose goals aggregate data should be retrieved."),
    filter_: str | None = Field(None, alias="filter", description="Filters the returned goals by status using a filter ID from the filters endpoint. If omitted or an unrecognized value is provided, the API defaults to the first available filter."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a comprehensive aggregate of all goals for a given employee, including milestone-containing goals, type counts, filter actions, comment counts, and shared employee details. This version extends v1.1 by including goals that contain milestones."""

    # Construct request model with validation
    try:
        _request = _models.GetGoalsAggregateV12Request(
            path=_models.GetGoalsAggregateV12RequestPath(employee_id=employee_id),
            query=_models.GetGoalsAggregateV12RequestQuery(filter_=filter_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_employee_goals_aggregate: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1_2/performance/employees/{employeeId}/goals/aggregate", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1_2/performance/employees/{employeeId}/goals/aggregate"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_employee_goals_aggregate")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_employee_goals_aggregate", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_employee_goals_aggregate",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Hours, Public API
@mcp.tool(
    title="Get Time Tracking Record",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_time_tracking_record(id_: str = Field(..., alias="id", description="The unique identifier of the time tracking record to retrieve, as assigned when the record was originally created.")) -> dict[str, Any] | ToolResult:
    """Retrieves a single time tracking record by its unique ID, returning full details including hours, date, employee, project, task, and shift differential information. Note that project and shiftDifferential fields may be null when not applicable, and missing records may return an empty or null payload rather than a not-found error."""

    # Construct request model with validation
    try:
        _request = _models.GetTimeTrackingRecordRequest(
            path=_models.GetTimeTrackingRecordRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_time_tracking_record: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/timetracking/record/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/timetracking/record/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_time_tracking_record")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_time_tracking_record", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_time_tracking_record",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Public API, Hours
@mcp.tool(
    title="Create Time Entry",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_time_entry(
    time_tracking_id: str = Field(..., alias="timeTrackingId", description="A caller-supplied unique identifier for this time entry, used to reference the record for future updates or deletions. Accepts any string up to 36 characters, such as a UUID."),
    employee_id: int = Field(..., alias="employeeId", description="The numeric ID of the employee for whom hours are being recorded."),
    date_hours_worked: str = Field(..., alias="dateHoursWorked", description="The calendar date on which the hours were worked, in ISO 8601 full-date format."),
    rate_type: str = Field(..., alias="rateType", description="Classifies the hours as regular, overtime, or double-time. Must be one of the accepted rate type codes."),
    hours_worked: float = Field(..., alias="hoursWorked", description="The total number of hours worked for this entry, expressed as a decimal number."),
    division_id: int | None = Field(None, alias="divisionId", description="The numeric ID of the division to associate with this time entry. Required only when your payroll configuration tracks hours at the division level."),
    department_id: int | None = Field(None, alias="departmentId", description="The numeric ID of the department to associate with this time entry. Required only when your payroll configuration tracks hours at the department level."),
    job_title_id: int | None = Field(None, alias="jobTitleId", description="The numeric ID of the job title to associate with this time entry. Required only when your payroll configuration tracks hours by job title."),
    pay_code: str | None = Field(None, alias="payCode", description="The payroll provider-specific pay code to classify this time entry. Required only when your payroll provider mandates a pay code."),
    pay_rate: float | None = Field(None, alias="payRate", description="The hourly rate of pay for this entry, expressed as a decimal number. Required only when your payroll provider mandates a pay rate."),
    job_code: int | None = Field(None, alias="jobCode", description="An optional numeric job code to associate with this time entry for payroll or reporting purposes."),
    job_data: str | None = Field(None, alias="jobData", description="An ordered, comma-delimited list of up to four job numbers (each up to 20 characters, no spaces) to associate with this time entry."),
) -> dict[str, Any] | ToolResult:
    """Creates a single time tracking hour record for an employee. Use this endpoint for one-off entries; for bulk imports use the batch upsert endpoint."""

    # Construct request model with validation
    try:
        _request = _models.CreateTimeTrackingHourRecordRequest(
            body=_models.CreateTimeTrackingHourRecordRequestBody(time_tracking_id=time_tracking_id, employee_id=employee_id, division_id=division_id, department_id=department_id, job_title_id=job_title_id, pay_code=pay_code, date_hours_worked=date_hours_worked, pay_rate=pay_rate, rate_type=rate_type, hours_worked=hours_worked, job_code=job_code, job_data=job_data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_time_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/timetracking/add"
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

# Tags: Public API, Hours
@mcp.tool(
    title="Upsert Hour Records",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def upsert_hour_records(body: list[_models.TimeTrackingRecord] | None = Field(None, description="Array of hour record objects to create or update; each item should include the relevant time tracking fields. Order is not significant, but each item's result is returned individually so partial failures can be identified per record.")) -> dict[str, Any] | ToolResult:
    """Bulk create or update time tracking hour records in a single request. Note that HTTP 201 may be returned even when individual records fail validation — always inspect each item's `success` flag and `response.message` for partial failures."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrUpdateTimeTrackingHourRecordsRequest(
            body=_models.CreateOrUpdateTimeTrackingHourRecordsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upsert_hour_records: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/timetracking/record"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upsert_hour_records")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upsert_hour_records", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upsert_hour_records",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Public API, Hours
@mcp.tool(
    title="Update Time Entry",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_time_entry(
    time_tracking_id: str = Field(..., alias="timeTrackingId", description="The unique identifier of the time tracking entry to update, up to 36 characters in length (e.g., a UUID)."),
    hours_worked: float = Field(..., alias="hoursWorked", description="The corrected total number of hours worked for this entry. Always provide the full intended value, not a delta — for example, if correcting from 8.0 to 6.0 hours, send 6.0."),
    project_id: int | None = Field(None, alias="projectId", description="The ID of the project to associate with this time entry. Omit if the project association should remain unchanged or is not applicable."),
    task_id: int | None = Field(None, alias="taskId", description="The ID of the task to associate with this time entry. Omit if the task association should remain unchanged or is not applicable."),
    shift_differential_id: int | None = Field(None, alias="shiftDifferentialId", description="The ID of the shift differential to associate with this time entry, used when the entry qualifies for differential pay. Omit if not applicable."),
    holiday_id: int | None = Field(None, alias="holidayId", description="The ID of the holiday to associate with this time entry, used when the hours were worked on a recognized holiday. Omit if not applicable."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing time tracking entry identified by its unique ID. Use this to correct hours worked or reassign the entry to a different project, task, shift differential, or holiday."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTimeTrackingRecordRequest(
            body=_models.UpdateTimeTrackingRecordRequestBody(time_tracking_id=time_tracking_id, hours_worked=hours_worked, project_id=project_id, task_id=task_id, shift_differential_id=shift_differential_id, holiday_id=holiday_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_time_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/timetracking/adjust"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_time_entry")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_time_entry", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_time_entry",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Public API, Hours
@mcp.tool(
    title="Delete Time Tracking Record",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_time_tracking_record(id_: str = Field(..., alias="id", description="The unique identifier of the time tracking record to delete, up to 36 characters in length (e.g., a UUID). Both not-found and malformed ID values will return a 400 error.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a time tracking record and all of its associated revisions by ID. Note that both not-found and invalid ID cases return a 400 invalid-argument response for backward compatibility."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTimeTrackingHourRecordRequest(
            path=_models.DeleteTimeTrackingHourRecordRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_time_tracking_record: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/timetracking/delete/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/timetracking/delete/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_time_tracking_record")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_time_tracking_record", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_time_tracking_record",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Account Information, Public API
@mcp.tool(
    title="List Country States",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_country_states(country_id: int = Field(..., alias="countryId", description="The numeric ID of the country whose states or provinces to retrieve. Obtain valid country IDs from the list_countries operation.")) -> dict[str, Any] | ToolResult:
    """Retrieves the list of states or provinces for a given country, sorted alphabetically by abbreviation. Each result includes a numeric ID, abbreviation label, ISO 3166-2 code, and full name."""

    # Construct request model with validation
    try:
        _request = _models.GetStatesByCountryIdRequest(
            path=_models.GetStatesByCountryIdRequestPath(country_id=country_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_country_states: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/meta/provinces/{countryId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/meta/provinces/{countryId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_country_states")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_country_states", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_country_states",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Account Information, Public API
@mcp.tool(
    title="List Countries",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_countries() -> dict[str, Any] | ToolResult:
    """Retrieves the full list of countries supported by BambooHR, each including a numeric string ID, full name, and ISO 3166-1 alpha-2 code. The returned country IDs can be used with the Get States by Country ID endpoint to fetch corresponding states or provinces."""

    # Extract parameters for API call
    _http_path = "/api/v1/meta/countries/options"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_countries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_countries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_countries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Account Information, Public API
@mcp.tool(
    title="List Timezones",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_timezones(
    page_size: int | None = Field(None, alias="pageSize", description="The number of timezone records to return per page. Controls the size of each paginated response."),
    page: int | None = Field(None, description="The page number to retrieve within the paginated result set, starting at page 1."),
    sort: str | None = Field(None, description="Specifies the sort order of results using OData v4 syntax, allowing ordering by one or more timezone fields in ascending or descending direction."),
    filter_: str | None = Field(None, alias="filter", description="Filters the timezone list using OData v4 filter syntax, enabling conditional expressions on timezone fields to narrow results."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of available timezones. Supports pagination, filtering, sorting, and field projection via OData v4 query parameters."""

    # Construct request model with validation
    try:
        _request = _models.Op5c5fb0f1211ae1c9451753f92f1053b6Request(
            query=_models.Op5c5fb0f1211ae1c9451753f92f1053b6RequestQuery(page_size=page_size, page=page, sort=sort, filter_=filter_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_timezones: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/meta/timezones"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_timezones")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_timezones", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_timezones",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Account Information, Public API
@mcp.tool(
    title="List Employee Fields",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_employee_fields() -> dict[str, Any] | ToolResult:
    """Retrieves all available employee fields for the account, including field ID, display name, data type, and deprecation status. Use this to discover valid field names before querying employee data via the Get Employee, Datasets, or other field-based endpoints."""

    # Extract parameters for API call
    _http_path = "/api/v1/meta/fields"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_employee_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_employee_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_employee_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Account Information, Public API
@mcp.tool(
    title="List Users",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_users(status: str | None = Field(None, description="Comma-separated list of account statuses to filter results by; only users matching at least one of the provided statuses are returned. Omitting this parameter or providing no recognized values returns users of all statuses.")) -> dict[str, Any] | ToolResult:
    """Retrieves all users for the company, with each record including user ID, employee ID, name, email, account status, and last login time. Support admin accounts are always excluded; results can be filtered by status and returned as JSON or XML based on the Accept header."""

    # Construct request model with validation
    try:
        _request = _models.ListUsersRequest(
            query=_models.ListUsersRequestQuery(status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/meta/users"
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

# Tags: Employees, Public API
@mcp.tool(
    title="Get Employee",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_employee(
    id_: str = Field(..., alias="id", description="The unique identifier of the employee to retrieve. Use the special value 0 to automatically resolve to the employee associated with the current API key."),
    fields: str | None = Field(None, description="Comma-separated list of field names specifying which employee fields to include in the response. Use the List Fields endpoint (list-fields) to discover all valid field names. Maximum of 400 fields per request."),
    only_current: bool | None = Field(None, alias="onlyCurrent", description="Controls whether historical table fields (such as job title or compensation) return only the current value or also include future-dated entries. Set to false to include future-dated values."),
) -> dict[str, Any] | ToolResult:
    """Retrieves profile and field data for a specific employee by ID. Supports selective field retrieval and optionally includes future-dated values from historical tables such as job title or compensation."""

    # Construct request model with validation
    try:
        _request = _models.GetEmployeeRequest(
            path=_models.GetEmployeeRequestPath(id_=id_),
            query=_models.GetEmployeeRequestQuery(fields=fields, only_current=only_current)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_employee: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_employee")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_employee", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_employee",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Employees, Public API
@mcp.tool(
    title="Update Employee",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def update_employee(
    id_: str = Field(..., alias="id", description="Unique identifier of the employee record to update."),
    first_name: str | None = Field(None, alias="firstName", description="Employee's legal first name."),
    last_name: str | None = Field(None, alias="lastName", description="Employee's legal last name."),
    work_email: str | None = Field(None, alias="workEmail", description="Employee's work email address."),
    job_title: str | None = Field(None, alias="jobTitle", description="Employee's job title."),
    department: str | None = Field(None, description="Name of the department the employee belongs to."),
    division: str | None = Field(None, description="Name of the division the employee belongs to."),
    location: str | None = Field(None, description="Name of the work location assigned to the employee."),
    hire_date: str | None = Field(None, alias="hireDate", description="Date the employee was hired, in YYYY-MM-DD format (ISO 8601 full date)."),
    mobile_phone: str | None = Field(None, alias="mobilePhone", description="Employee's mobile phone number."),
    home_phone: str | None = Field(None, alias="homePhone", description="Employee's home phone number."),
    work_phone: str | None = Field(None, alias="workPhone", description="Employee's work phone number."),
    address1: str | None = Field(None, description="First line of the employee's street address."),
    city: str | None = Field(None, description="City component of the employee's address."),
    state: str | None = Field(None, description="State or province component of the employee's address; values are normalized to standard abbreviations (e.g., full state names are converted to their two-letter code)."),
    zipcode: str | None = Field(None, description="ZIP or postal code component of the employee's address."),
    country: str | None = Field(None, description="Country component of the employee's address."),
) -> dict[str, Any] | ToolResult:
    """Update one or more fields for an existing employee by submitting a JSON object or XML document with field name/value pairs. To discover all available field names beyond those listed here, call the list_fields operation (GET /api/v1/meta/fields). Note: if the employee is on a Trax Payroll pay schedule, a comprehensive set of required payroll fields must be included in the request."""

    # Construct request model with validation
    try:
        _request = _models.UpdateEmployeeRequest(
            path=_models.UpdateEmployeeRequestPath(id_=id_),
            body=_models.UpdateEmployeeRequestBody(first_name=first_name, last_name=last_name, work_email=work_email, job_title=job_title, department=department, division=division, location=location, hire_date=hire_date, mobile_phone=mobile_phone, home_phone=home_phone, work_phone=work_phone, address1=address1, city=city, state=state, zipcode=zipcode, country=country)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_employee: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_employee")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_employee", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_employee",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tabular Data, Public API
@mcp.tool(
    title="List Changed Employee Table Rows",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_changed_employee_table_rows(
    table: str = Field(..., description="The name of the employee data table to retrieve changed rows for, such as job information or compensation details."),
    since: str = Field(..., description="An ISO 8601 datetime timestamp indicating the cutoff point; only rows belonging to employees whose records were modified after this timestamp will be returned. Must be URL-encoded when included in the request."),
) -> dict[str, Any] | ToolResult:
    """Retrieves table rows for all employees whose records have changed since a specified timestamp, grouped by employee ID. Any change to an employee record causes all of that employee's rows in the specified table to be returned, making this an efficient alternative to fetching full table data for all employees."""

    # Construct request model with validation
    try:
        _request = _models.GetChangedEmployeeTableDataRequest(
            path=_models.GetChangedEmployeeTableDataRequestPath(table=table),
            query=_models.GetChangedEmployeeTableDataRequestQuery(since=since)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_changed_employee_table_rows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/changed/tables/{table}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/changed/tables/{table}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_changed_employee_table_rows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_changed_employee_table_rows", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_changed_employee_table_rows",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tabular Data, Public API
@mcp.tool(
    title="List Employee Table Rows",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_employee_table_rows(
    id_: str = Field(..., alias="id", description="The unique identifier of the employee whose table data should be retrieved. Use the special value \"all\" to retrieve table data across all employees the API user has access to."),
    table: str = Field(..., description="The name of the table to retrieve rows from, such as job information, compensation, or employment status tables."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all rows from a specified table for one or all employees, returning only the fields the caller has permission to access. Results are unordered and field visibility is subject to field-level permission checks."""

    # Construct request model with validation
    try:
        _request = _models.GetEmployeeTableDataRequest(
            path=_models.GetEmployeeTableDataRequestPath(id_=id_, table=table)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_employee_table_rows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{id}/tables/{table}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{id}/tables/{table}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_employee_table_rows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_employee_table_rows", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_employee_table_rows",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Tabular Data, Public API
@mcp.tool(
    title="Create Employee Table Row",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_employee_table_row(
    id_: str = Field(..., alias="id", description="The unique identifier of the employee whose table will receive the new row."),
    table: str = Field(..., description="The name of the employee table to append a row to, such as job information or compensation history."),
    date: str | None = Field(None, description="The effective date for the new row, indicating when the record becomes active. Must follow YYYY-MM-DD format."),
    location: str | None = Field(None, description="The office or work location associated with this row entry."),
    division: str | None = Field(None, description="The organizational division associated with this row entry."),
    department: str | None = Field(None, description="The department associated with this row entry."),
    job_title: str | None = Field(None, alias="jobTitle", description="The job title assigned to the employee for this row entry."),
    reports_to: str | None = Field(None, alias="reportsTo", description="The identifier of the manager or supervisor this employee reports to for this row entry."),
    teams: list[str] | None = Field(None, description="A list of team identifiers or names associated with this row entry. Order is not significant; each item represents a single team affiliation."),
) -> dict[str, Any] | ToolResult:
    """Appends a new row to a specified tabular data section of an employee record, such as job information or compensation history. Submit field name/value pairs in JSON or XML to record a new entry with an effective date and relevant attributes."""

    # Construct request model with validation
    try:
        _request = _models.CreateTableRowRequest(
            path=_models.CreateTableRowRequestPath(id_=id_, table=table),
            body=_models.CreateTableRowRequestBody(date=date, location=location, division=division, department=department, job_title=job_title, reports_to=reports_to, teams=teams)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_employee_table_row: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{id}/tables/{table}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{id}/tables/{table}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_employee_table_row")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_employee_table_row", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_employee_table_row",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tabular Data, Public API
@mcp.tool(
    title="Update Employee Table Row",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def update_employee_table_row_v1_1(
    id_: str = Field(..., alias="id", description="The unique identifier of the employee whose table row is being updated."),
    table: str = Field(..., description="The name of the employee table containing the row to update, such as job information or compensation tables."),
    row_id: str = Field(..., alias="rowId", description="The unique identifier of the specific row within the table to update."),
    date: str | None = Field(None, description="The effective date for the row update in ISO 8601 full-date format (YYYY-MM-DD), determining when the change takes effect."),
    location: str | None = Field(None, description="The physical or organizational location value to assign to the employee for this row."),
    division: str | None = Field(None, description="The division value to assign to the employee for this row, representing a high-level organizational grouping."),
    department: str | None = Field(None, description="The department value to assign to the employee for this row, representing the employee's organizational unit."),
    job_title: str | None = Field(None, alias="jobTitle", description="The job title value to assign to the employee for this row, reflecting their role or position."),
    reports_to: str | None = Field(None, alias="reportsTo", description="The identifier of the manager or supervisor this employee reports to for this row."),
    teams: list[str] | None = Field(None, description="A list of team identifiers or names associated with the employee for this row; order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing row in a specified employee table, such as job information or compensation history. Submit field changes to modify the row's effective date, location, department, job title, reporting structure, or team assignments."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTableRowV11Request(
            path=_models.UpdateTableRowV11RequestPath(id_=id_, table=table, row_id=row_id),
            body=_models.UpdateTableRowV11RequestBody(date=date, location=location, division=division, department=department, job_title=job_title, reports_to=reports_to, teams=teams)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_employee_table_row_v1_1: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1_1/employees/{id}/tables/{table}/{rowId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1_1/employees/{id}/tables/{table}/{rowId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_employee_table_row_v1_1")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_employee_table_row_v1_1", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_employee_table_row_v1_1",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Tabular Data, Public API
@mcp.tool(
    title="Create Employee Table Row",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_employee_table_row_v1_1(
    id_: str = Field(..., alias="id", description="The unique identifier of the employee whose table will receive the new row."),
    table: str = Field(..., description="The name of the employee table to add a row to, such as job information or compensation tables."),
    date: str | None = Field(None, description="The date on which the new row becomes effective, in YYYY-MM-DD format following ISO 8601."),
    location: str | None = Field(None, description="The office or work location associated with this row entry."),
    division: str | None = Field(None, description="The organizational division associated with this row entry."),
    department: str | None = Field(None, description="The department associated with this row entry."),
    job_title: str | None = Field(None, alias="jobTitle", description="The job title associated with this row entry."),
    reports_to: str | None = Field(None, alias="reportsTo", description="The identifier of the manager or supervisor this employee reports to for this row entry."),
    teams: list[str] | None = Field(None, description="A list of team identifiers associated with this row entry; order is not significant and each item represents a single team value."),
) -> dict[str, Any] | ToolResult:
    """Adds a new row to a specified table in an employee's record, such as job information or compensation history. Accepts row data in JSON or XML format with an optional effective date and relevant field values."""

    # Construct request model with validation
    try:
        _request = _models.CreateTableRowV11Request(
            path=_models.CreateTableRowV11RequestPath(id_=id_, table=table),
            body=_models.CreateTableRowV11RequestBody(date=date, location=location, division=division, department=department, job_title=job_title, reports_to=reports_to, teams=teams)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_employee_table_row_v1_1: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1_1/employees/{id}/tables/{table}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1_1/employees/{id}/tables/{table}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_employee_table_row_v1_1")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_employee_table_row_v1_1", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_employee_table_row_v1_1",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Last Change Information, Public API
@mcp.tool(
    title="List Changed Employees",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_changed_employees(
    since: str = Field(..., description="The cutoff timestamp in ISO 8601 format; only employees whose records changed after this point will be returned. Must be URL-encoded when included in the request."),
    type_: Literal["inserted", "updated", "deleted", "all"] | None = Field(None, alias="type", description="Filters results to a specific type of change; when omitted, employees of all change types are returned. Accepted values are 'inserted', 'updated', 'deleted', or 'all'."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of employee IDs that have changed since a specified timestamp, enabling efficient incremental sync without downloading all employee records. Each result includes the employee ID, change type (inserted, updated, or deleted), and the timestamp of the last change."""

    # Construct request model with validation
    try:
        _request = _models.GetChangedEmployeeIdsRequest(
            query=_models.GetChangedEmployeeIdsRequestQuery(since=since, type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_changed_employees: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/employees/changed"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_changed_employees")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_changed_employees", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_changed_employees",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Photos, Public API
@mcp.tool(
    title="Get Employee Photo",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_employee_photo(
    employee_id: int = Field(..., alias="employeeId", description="The unique numeric identifier of the employee whose photo is being requested."),
    size: Literal["original", "large", "medium", "small", "xs", "tiny"] = Field(..., description="The predefined size tier for the returned photo. Available options are: original (full resolution), large (340×340), medium (170×170), small (150×150), xs (50×50), and tiny (20×20)."),
    width: int | None = Field(None, description="Scales the returned image to this pixel width, capped at the natural width of the requested size tier. Only applies when size is small or tiny."),
    height: int | None = Field(None, description="Scales the returned image to this pixel height, capped at the natural height of the requested size tier. Only applies when size is small or tiny."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a JPEG photo of the specified employee at a predefined size. The response Content-Type is always image/jpeg, though the underlying byte payload may reflect the original upload format."""

    # Construct request model with validation
    try:
        _request = _models.GetEmployeePhotoRequest(
            path=_models.GetEmployeePhotoRequestPath(employee_id=employee_id, size=size),
            query=_models.GetEmployeePhotoRequestQuery(width=width, height=height)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_employee_photo: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{employeeId}/photo/{size}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{employeeId}/photo/{size}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_employee_photo")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_employee_photo", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_employee_photo",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Employee Files, Public API
@mcp.tool(
    title="Create Employee File Categories",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_employee_file_categories(body: list[str] | None = Field(None, description="A list of category name strings to create. Each name must be non-empty and must not already exist. Order is not significant.")) -> dict[str, Any] | ToolResult:
    """Creates one or more employee file categories by accepting a list of category names. An empty payload succeeds without creating anything; duplicate or empty names return an error."""

    # Construct request model with validation
    try:
        _request = _models.AddEmployeeFileCategoryRequest(
            body=_models.AddEmployeeFileCategoryRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_employee_file_categories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/employees/files/categories"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_employee_file_categories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_employee_file_categories", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_employee_file_categories",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Company Files, Public API
@mcp.tool(
    title="Create File Categories",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_file_categories(body: list[str] | None = Field(None, description="An array of category name strings to create. Each entry must be a non-empty, unique name that is not reserved. Order is not significant.")) -> dict[str, Any] | ToolResult:
    """Creates one or more company file categories in a single request. Returns 400 if any name is empty or already exists, 403 if the caller lacks permission or a name is reserved, and 200 with no changes if the payload is empty."""

    # Construct request model with validation
    try:
        _request = _models.AddCompanyFileCategoryRequest(
            body=_models.AddCompanyFileCategoryRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_file_categories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/files/categories"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_file_categories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_file_categories", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_file_categories",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Employee Files, Public API
@mcp.tool(
    title="Upload Employee File",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def upload_employee_file(
    id_: str = Field(..., alias="id", description="The ID of the employee whose file folder will receive the upload. Pass 0 to target the employee associated with the API key."),
    file_name: str = Field(..., alias="fileName", description="The display name assigned to the uploaded file as it will appear in the employee's document folder."),
    category: int = Field(..., description="The numeric ID of the employee file section (category) into which the file will be uploaded."),
    file_: str = Field(..., alias="file", description="Base64-encoded file content for upload. The binary file content to upload, submitted as part of the multipart/form-data request body.", json_schema_extra={'format': 'byte'}),
    share: Literal["yes", "no"] | None = Field(None, description="Controls whether the uploaded file is shared with the employee and made visible to them. Defaults to no if omitted."),
) -> dict[str, Any] | ToolResult:
    """Uploads a file to a specific section of an employee's document folder via multipart/form-data. Files must be under 20MB and use a supported extension; on success, the response includes a Location header pointing to the newly created file resource."""

    # Construct request model with validation
    try:
        _request = _models.UploadEmployeeFileRequest(
            path=_models.UploadEmployeeFileRequestPath(id_=id_),
            body=_models.UploadEmployeeFileRequestBody(file_name=file_name, category=category, share=share, file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_employee_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{id}/files", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{id}/files"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_employee_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_employee_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_employee_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Company Files, Public API
@mcp.tool(
    title="Upload File",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def upload_file(
    file_name: str = Field(..., alias="fileName", description="The display name for the file as it will appear in the company file system."),
    category: int = Field(..., description="The numeric ID of the file category (section) into which the file will be uploaded. Read-only categories and implementation categories (for completed implementations) are not permitted."),
    file_: str = Field(..., alias="file", description="Base64-encoded file content for upload. The binary file content to upload. Must be under 20MB and use a supported file extension.", json_schema_extra={'format': 'byte'}),
    share: Literal["yes", "no"] | None = Field(None, description="Controls whether the uploaded file is shared with all employees. Accepts 'yes' to share or 'no' to keep private; defaults to 'no' if omitted."),
) -> dict[str, Any] | ToolResult:
    """Uploads a file to a specified company file category using a multipart/form-data request. Files must be under 20MB, use a supported extension, and cannot be uploaded to read-only categories or implementation categories on companies that have completed implementation."""

    # Construct request model with validation
    try:
        _request = _models.UploadCompanyFileRequest(
            body=_models.UploadCompanyFileRequestBody(file_name=file_name, category=category, share=share, file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/files"
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

# Tags: Time Off, Public API
@mcp.tool(
    title="List Employee Time Off Policies",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_employee_time_off_policies(employee_id: int = Field(..., alias="employeeId", description="The unique identifier of the employee whose assigned time off policies should be retrieved.")) -> dict[str, Any] | ToolResult:
    """Retrieves all time off policies currently assigned to a specified employee, including each policy's ID, time off type, and accrual start date."""

    # Construct request model with validation
    try:
        _request = _models.ListEmployeeTimeOffPoliciesRequest(
            path=_models.ListEmployeeTimeOffPoliciesRequestPath(employee_id=employee_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_employee_time_off_policies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{employeeId}/time_off/policies", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{employeeId}/time_off/policies"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_employee_time_off_policies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_employee_time_off_policies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_employee_time_off_policies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Off, Public API
@mcp.tool(
    title="Assign Employee Time Off Policies",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def assign_employee_time_off_policies(
    employee_id: int = Field(..., alias="employeeId", description="The unique identifier of the employee to whom time off policies will be assigned."),
    body: list[_models.AssignTimeOffPoliciesBodyItem] | None = Field(None, description="List of policy assignment objects, each specifying a time off policy and the date on which accruals should begin for that policy. Order is not significant. Set accrualStartDate to null to remove an existing policy assignment rather than add or update one."),
) -> dict[str, Any] | ToolResult:
    """Assigns one or more time off policies to an employee, with accruals beginning on the specified start date for each policy. Passing a null accrual start date for a policy removes that existing assignment; returns the full updated list of assigned policies on success."""

    # Construct request model with validation
    try:
        _request = _models.AssignTimeOffPoliciesRequest(
            path=_models.AssignTimeOffPoliciesRequestPath(employee_id=employee_id),
            body=_models.AssignTimeOffPoliciesRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for assign_employee_time_off_policies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{employeeId}/time_off/policies", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{employeeId}/time_off/policies"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("assign_employee_time_off_policies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("assign_employee_time_off_policies", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="assign_employee_time_off_policies",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Off, Public API
@mcp.tool(
    title="List Employee Time Off Policies",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_employee_time_off_policies_extended(employee_id: int = Field(..., alias="employeeId", description="The unique identifier of the employee whose time off policies should be retrieved.")) -> dict[str, Any] | ToolResult:
    """Retrieves all time off policies currently assigned to a specified employee, including manual and unlimited policy types not available in the v1 endpoint."""

    # Construct request model with validation
    try:
        _request = _models.ListEmployeeTimeOffPoliciesV11Request(
            path=_models.ListEmployeeTimeOffPoliciesV11RequestPath(employee_id=employee_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_employee_time_off_policies_extended: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1_1/employees/{employeeId}/time_off/policies", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1_1/employees/{employeeId}/time_off/policies"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_employee_time_off_policies_extended")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_employee_time_off_policies_extended", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_employee_time_off_policies_extended",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Off, Public API
@mcp.tool(
    title="Assign Time Off Policies",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def assign_time_off_policies(
    employee_id: int = Field(..., alias="employeeId", description="The unique identifier of the employee to whom the time off policies will be assigned."),
    body: list[_models.AssignTimeOffPoliciesV11BodyItem] | None = Field(None, description="A list of policy assignment objects, each specifying a time off policy and the date on which accruals should begin for that policy. Order is not significant. Set accrual start date to null for policies that do not use accrual-based tracking."),
) -> dict[str, Any] | ToolResult:
    """Assigns one or more time off policies to an employee, with accruals beginning on the specified start date for each policy. Returns the employee's full current list of assigned policies, including manual and unlimited policy types."""

    # Construct request model with validation
    try:
        _request = _models.AssignTimeOffPoliciesV11Request(
            path=_models.AssignTimeOffPoliciesV11RequestPath(employee_id=employee_id),
            body=_models.AssignTimeOffPoliciesV11RequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for assign_time_off_policies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1_1/employees/{employeeId}/time_off/policies", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1_1/employees/{employeeId}/time_off/policies"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("assign_time_off_policies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("assign_time_off_policies", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="assign_time_off_policies",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Public API, Applicant Tracking
@mcp.tool(
    title="Get Application",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_application(application_id: int = Field(..., alias="applicationId", description="The unique identifier of the job application to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves full details for a single job application, including applicant information, job details, screening questions and answers, and status history. Requires the API key owner to have access to ATS settings."""

    # Construct request model with validation
    try:
        _request = _models.GetApplicationDetailsRequest(
            path=_models.GetApplicationDetailsRequestPath(application_id=application_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_application: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/applicant_tracking/applications/{applicationId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/applicant_tracking/applications/{applicationId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_application")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_application", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_application",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Public API, Applicant Tracking
@mcp.tool(
    title="Add Application Comment",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def add_application_comment(
    application_id: int = Field(..., alias="applicationId", description="The unique identifier of the job application to which the comment will be added."),
    comment: str = Field(..., description="The text content of the comment to post on the application."),
    type_: str | None = Field(None, alias="type", description="The category of the comment being posted. Accepts predefined comment type values; defaults to 'comment' if not provided."),
) -> dict[str, Any] | ToolResult:
    """Adds a comment to a specific job application in the Applicant Tracking System. Requires the API key owner to have access to ATS settings."""

    # Construct request model with validation
    try:
        _request = _models.CreateApplicationCommentRequest(
            path=_models.CreateApplicationCommentRequestPath(application_id=application_id),
            body=_models.CreateApplicationCommentRequestBody(type_=type_, comment=comment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_application_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/applicant_tracking/applications/{applicationId}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/applicant_tracking/applications/{applicationId}/comments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_application_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_application_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_application_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Public API, Applicant Tracking
@mcp.tool(
    title="List Jobs",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_jobs(
    status_groups: str | None = Field(None, alias="statusGroups", description="One or more status group names to filter job openings by, provided as a comma-separated string. Defaults to all non-deleted positions when omitted."),
    status_ids: str | None = Field(None, description="One or more specific job opening status IDs to filter by, provided as a comma-separated string of integers. When combined with statusGroups, both filters are applied together."),
    sort_by: Literal["count", "title", "lead", "created", "status"] | None = Field(None, alias="sortBy", description="The field by which to sort the returned job openings. Applies to the full result set before pagination."),
    sort_order: Literal["ASC", "DESC"] | None = Field(None, alias="sortOrder", description="The direction in which to sort results, either ascending or descending."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of job opening summaries from the Applicant Tracking System. Supports filtering by status group or specific status IDs, with configurable sorting. Requires ATS settings access."""

    # Construct request model with validation
    try:
        _request = _models.GetJobSummariesRequest(
            query=_models.GetJobSummariesRequestQuery(status_groups=status_groups, status_ids=status_ids, sort_by=sort_by, sort_order=sort_order)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/applicant_tracking/jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Public API, Applicant Tracking
@mcp.tool(
    title="Update Application Status",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def update_application_status(
    application_id: int = Field(..., alias="applicationId", description="The unique identifier of the application whose status will be updated."),
    status: int = Field(..., description="The unique identifier of the status to assign to the application. Retrieve valid status IDs using the Get Applicant Statuses endpoint."),
) -> dict[str, Any] | ToolResult:
    """Updates the status of a specific applicant tracking application. The API key owner must have ATS settings access, and valid status IDs can be retrieved via the Get Applicant Statuses endpoint."""

    # Construct request model with validation
    try:
        _request = _models.UpdateApplicantStatusRequest(
            path=_models.UpdateApplicantStatusRequestPath(application_id=application_id),
            body=_models.UpdateApplicantStatusRequestBody(status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_application_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/applicant_tracking/applications/{applicationId}/status", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/applicant_tracking/applications/{applicationId}/status"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_application_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_application_status", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_application_status",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Benefits, Public API
@mcp.tool(
    title="List Benefit Coverages",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_benefit_coverages() -> dict[str, Any] | ToolResult:
    """Retrieves all benefit coverage levels configured for the company, such as Employee Only, Employee + Spouse, or Employee + Family enrollment tiers. Returns each coverage level's ID, short name, description, sort order, and associated benefit plan ID (null for company-wide levels)."""

    # Extract parameters for API call
    _http_path = "/api/v1/benefitcoverages"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_benefit_coverages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_benefit_coverages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_benefit_coverages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Benefits, Public API
@mcp.tool(
    title="Get Employee Dependent",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_employee_dependent(id_: int = Field(..., alias="id", description="The unique numeric identifier of the employee dependent record to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the full details of a single employee dependent by their unique dependent ID, including masked SSN/SIN values and full state and country names. Requires Benefits Administration permissions and returns data as a JSON or XML object containing a single-element array under the 'Employee Dependents' key."""

    # Construct request model with validation
    try:
        _request = _models.GetEmployeeDependentRequest(
            path=_models.GetEmployeeDependentRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_employee_dependent: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employeedependents/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employeedependents/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_employee_dependent")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_employee_dependent", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_employee_dependent",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Benefits, Public API
@mcp.tool(
    title="Update Dependent",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_dependent(
    id_: int = Field(..., alias="id", description="The numeric ID of the employee dependent record to update."),
    employee_id: str = Field(..., alias="employeeId", description="The ID of the employee this dependent is associated with. Must reference an existing, valid employee."),
    first_name: str | None = Field(None, alias="firstName", description="The dependent's first name."),
    middle_name: str | None = Field(None, alias="middleName", description="The dependent's middle name."),
    last_name: str | None = Field(None, alias="lastName", description="The dependent's last name."),
    relationship: str | None = Field(None, description="The dependent's relationship to the employee. Must be a valid relationship type recognized by the system."),
    gender: str | None = Field(None, description="The dependent's gender. Must be a valid gender value recognized by the system."),
    ssn: str | None = Field(None, description="The dependent's Social Security Number, submitted as plain text and stored encrypted. Read responses return a masked value."),
    sin: str | None = Field(None, description="The dependent's Social Insurance Number (Canadian equivalent of SSN), submitted as plain text and stored encrypted. Read responses return a masked value."),
    date_of_birth: str | None = Field(None, alias="dateOfBirth", description="The dependent's date of birth. Must be provided in YYYY-MM-DD format."),
    address_line1: str | None = Field(None, alias="addressLine1", description="The first line of the dependent's street address."),
    address_line2: str | None = Field(None, alias="addressLine2", description="The second line of the dependent's street address, such as an apartment or suite number."),
    city: str | None = Field(None, description="The city component of the dependent's address."),
    state: str | None = Field(None, description="The dependent's state, provided as a two-letter state code. Read responses return the full state name."),
    zip_code: str | None = Field(None, alias="zipCode", description="The dependent's ZIP or postal code."),
    home_phone: str | None = Field(None, alias="homePhone", description="The dependent's home phone number."),
    country: str | None = Field(None, description="The dependent's country, provided as an ISO 3166-1 alpha-2 two-letter country code. Read responses return the full country name."),
    is_us_citizen: Literal["yes", "no"] | None = Field(None, alias="isUsCitizen", description="Indicates whether the dependent is a US citizen. Accepted values are \"yes\" or \"no\"."),
    is_student: Literal["yes", "no"] | None = Field(None, alias="isStudent", description="Indicates whether the dependent is currently enrolled as a student. Accepted values are \"yes\" or \"no\"."),
) -> dict[str, Any] | ToolResult:
    """Fully replaces an existing employee dependent record with the provided data. This is a full-replacement operation — all fields must be supplied, as omitted fields will be cleared rather than preserved."""

    # Construct request model with validation
    try:
        _request = _models.UpdateEmployeeDependentRequest(
            path=_models.UpdateEmployeeDependentRequestPath(id_=id_),
            body=_models.UpdateEmployeeDependentRequestBody(employee_id=employee_id, first_name=first_name, middle_name=middle_name, last_name=last_name, relationship=relationship, gender=gender, ssn=ssn, sin=sin, date_of_birth=date_of_birth, address_line1=address_line1, address_line2=address_line2, city=city, state=state, zip_code=zip_code, home_phone=home_phone, country=country, is_us_citizen=is_us_citizen, is_student=is_student)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_dependent: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employeedependents/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employeedependents/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_dependent")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_dependent", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_dependent",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Benefits, Public API
@mcp.tool(
    title="List Employee Dependents",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_employee_dependents(employeeid: int | None = Field(None, description="Filters the results to dependents belonging to a specific employee. When omitted, dependents for all employees in the company are returned.")) -> dict[str, Any] | ToolResult:
    """Retrieves dependent records for one or all employees in the company, requiring Benefits Administration permissions. When an employee ID is provided the response is scoped to that employee; otherwise all dependents across the company are returned, with SSN/SIN values masked and state/country fields returned as full names."""

    # Construct request model with validation
    try:
        _request = _models.ListEmployeeDependentsRequest(
            query=_models.ListEmployeeDependentsRequestQuery(employeeid=employeeid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_employee_dependents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/employeedependents"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_employee_dependents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_employee_dependents", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_employee_dependents",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Benefits, Public API
@mcp.tool(
    title="Create Employee Dependent",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_employee_dependent(
    employee_id: str = Field(..., alias="employeeId", description="The unique identifier of the employee to whom this dependent belongs. Must reference an existing employee record."),
    first_name: str | None = Field(None, alias="firstName", description="The dependent's first name."),
    middle_name: str | None = Field(None, alias="middleName", description="The dependent's middle name."),
    last_name: str | None = Field(None, alias="lastName", description="The dependent's last name."),
    relationship: str | None = Field(None, description="The dependent's relationship to the employee. Must be a valid relationship type such as spouse, child, or domestic partner."),
    gender: str | None = Field(None, description="The dependent's gender. Must be a valid gender value as recognized by the API."),
    ssn: str | None = Field(None, description="The dependent's Social Security Number, submitted as plain text and stored encrypted. When retrieved, the value is returned in masked form showing only the last four digits."),
    sin: str | None = Field(None, description="The dependent's Social Insurance Number (Canadian equivalent of SSN), submitted as plain text and stored encrypted. When retrieved, the value is returned in masked form."),
    date_of_birth: str | None = Field(None, alias="dateOfBirth", description="The dependent's date of birth, formatted as a calendar date in YYYY-MM-DD format."),
    address_line1: str | None = Field(None, alias="addressLine1", description="The first line of the dependent's street address, typically including street number and name."),
    address_line2: str | None = Field(None, alias="addressLine2", description="The second line of the dependent's address, used for suite, apartment, or unit information."),
    city: str | None = Field(None, description="The city portion of the dependent's address."),
    state: str | None = Field(None, description="The dependent's state, provided as a two-letter state code. When retrieved, the API returns the full state name."),
    zip_code: str | None = Field(None, alias="zipCode", description="The dependent's ZIP or postal code corresponding to their address."),
    home_phone: str | None = Field(None, alias="homePhone", description="The dependent's home phone number."),
    country: str | None = Field(None, description="The dependent's country, provided as an ISO 3166-1 alpha-2 two-letter country code. When retrieved, the API returns the full country name."),
    is_us_citizen: Literal["yes", "no"] | None = Field(None, alias="isUsCitizen", description="Indicates whether the dependent is a US citizen. Accepted values are yes or no."),
    is_student: Literal["yes", "no"] | None = Field(None, alias="isStudent", description="Indicates whether the dependent is currently enrolled as a student. Accepted values are yes or no."),
) -> dict[str, Any] | ToolResult:
    """Creates a new dependent record associated with a specific employee, capturing personal, demographic, and address details. The employee must exist, and sensitive fields like SSN and SIN are accepted as plain text and stored encrypted."""

    # Construct request model with validation
    try:
        _request = _models.CreateEmployeeDependentRequest(
            body=_models.CreateEmployeeDependentRequestBody(employee_id=employee_id, first_name=first_name, middle_name=middle_name, last_name=last_name, relationship=relationship, gender=gender, ssn=ssn, sin=sin, date_of_birth=date_of_birth, address_line1=address_line1, address_line2=address_line2, city=city, state=state, zip_code=zip_code, home_phone=home_phone, country=country, is_us_citizen=is_us_citizen, is_student=is_student)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_employee_dependent: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/employeedependents"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_employee_dependent")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_employee_dependent", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_employee_dependent",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Employees, Public API
@mcp.tool(
    title="Get Employee Directory",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_employee_directory(only_current: bool | None = Field(None, alias="onlyCurrent", description="Controls whether only active employees are returned. Set to false to include terminated employees alongside active ones.")) -> dict[str, Any] | ToolResult:
    """Retrieves the company employee directory, including a fieldset definition and employee records. Access level determines the returned fieldset; directory sharing or org-chart access must be enabled for the company."""

    # Construct request model with validation
    try:
        _request = _models.GetEmployeesDirectoryRequest(
            query=_models.GetEmployeesDirectoryRequestQuery(only_current=only_current)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_employee_directory: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/employees/directory"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_employee_directory")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_employee_directory", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_employee_directory",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Company Files, Public API
@mcp.tool(
    title="List Company Files",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_company_files() -> dict[str, Any] | ToolResult:
    """Retrieves all company file categories and the files within each category that the requesting user has permission to view. Response format is controlled via the Accept header: use application/json for JSON or application/xml (or omit) for XML."""

    # Extract parameters for API call
    _http_path = "/api/v1/files/view"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_company_files")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_company_files", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_company_files",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Employee Files, Public API
@mcp.tool(
    title="List Employee Files",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_employee_files(id_: int = Field(..., alias="id", description="The unique identifier of the employee whose files are being listed. Only files and categories the caller is permitted to view will be returned.")) -> dict[str, Any] | ToolResult:
    """Retrieves the file categories and associated files visible to the caller for a specified employee. Results are permission-filtered; employees viewing their own profile also see files shared with them. Response format is determined by the Accept header (application/json for JSON, XML otherwise)."""

    # Construct request model with validation
    try:
        _request = _models.ListEmployeeFilesRequest(
            path=_models.ListEmployeeFilesRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_employee_files: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{id}/files/view", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{id}/files/view"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_employee_files")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_employee_files", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_employee_files",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Account Information, Public API
@mcp.tool(
    title="List List Fields",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_list_fields(format_: Literal["json"] | None = Field(None, alias="format", description="Specifies the response format as JSON, serving as an alternative to setting the Accept header on the request.")) -> dict[str, Any] | ToolResult:
    """Retrieves all list fields defined in the account, including each field's ID, alias, options, manageability, and multi-value support. Archived options are included in responses to support historical data references but should not be presented as active selections."""

    # Construct request model with validation
    try:
        _request = _models.ListListFieldsRequest(
            query=_models.ListListFieldsRequestQuery(format_=format_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_list_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/meta/lists"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_list_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_list_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_list_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Account Information, Public API
@mcp.tool(
    title="Update List Field Options",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_list_field_options(
    list_field_id: str = Field(..., alias="listFieldId", description="The unique identifier of the list field whose options are being managed."),
    options: list[_models.UpdateListFieldValuesBodyOptionsItem] | None = Field(None, description="Array of option objects to create, update, or archive on the list field. To create a new option omit its ID, to update an existing option include its ID, and to archive an option include its ID with the archived attribute set to yes. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Create, update, or archive options for a specific list field by its ID. Omit an option's ID to create it, include an ID to update it, or set archived to yes to hide it from future use while preserving historical data."""

    # Construct request model with validation
    try:
        _request = _models.UpdateListFieldValuesRequest(
            path=_models.UpdateListFieldValuesRequestPath(list_field_id=list_field_id),
            body=_models.UpdateListFieldValuesRequestBody(options=options)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_list_field_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/meta/lists/{listFieldId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/meta/lists/{listFieldId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_list_field_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_list_field_options", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_list_field_options",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Account Information, Public API
@mcp.tool(
    title="List Tabular Fields",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_tabular_fields() -> dict[str, Any] | ToolResult:
    """Retrieves all tabular (table-based) fields available in the account, including each table's alias and its fields with their IDs, names, and types. Use this to discover valid table names and field metadata required for table row endpoints such as jobInfo, compensation, and employmentStatus."""

    # Extract parameters for API call
    _http_path = "/api/v1/meta/tables"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tabular_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tabular_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tabular_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Off, Public API
@mcp.tool(
    title="Get Employee Time Off Balance",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_employee_time_off_balance(
    employee_id: int = Field(..., alias="employeeId", description="The unique identifier of the employee whose time off balances should be retrieved."),
    end: str | None = Field(None, description="The date through which time off balances are calculated, in YYYY-MM-DD format. Defaults to the company's current date if omitted; supply a future date to project balances."),
    precision: int | None = Field(None, description="Number of decimal places applied to balance and year-to-date usage values. Accepts values from 0 (whole numbers) to 4 (four decimal places), defaulting to 2.", ge=0, le=4),
) -> dict[str, Any] | ToolResult:
    """Retrieves time off balances for an employee across all assigned categories as of a specified date, incorporating accruals, adjustments, usage, and carry-over events. Pass today's date for current balances or a future date to project balances forward."""

    # Construct request model with validation
    try:
        _request = _models.GetTimeOffBalanceRequest(
            path=_models.GetTimeOffBalanceRequestPath(employee_id=employee_id),
            query=_models.GetTimeOffBalanceRequestQuery(end=end, precision=precision)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_employee_time_off_balance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{employeeId}/time_off/calculator", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{employeeId}/time_off/calculator"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_employee_time_off_balance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_employee_time_off_balance", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_employee_time_off_balance",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Off, Public API
@mcp.tool(
    title="Create Time Off History Entry",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_time_off_history_entry(
    employee_id: int = Field(..., alias="employeeId", description="The unique identifier of the employee for whom the time off history entry is being created."),
    date: str = Field(..., description="The calendar date the history entry applies to, provided in YYYY-MM-DD format."),
    event_type: Literal["used", "override"] | None = Field(None, alias="eventType", description="Specifies whether the entry records actual time off usage against an approved request or a manual balance override adjustment. Defaults to 'used' when omitted on this endpoint."),
    time_off_request_id: int | None = Field(None, alias="timeOffRequestId", description="The unique identifier of the approved time off request this entry is linked to. Must be provided when eventType is 'used'."),
    time_off_type_id: int | None = Field(None, alias="timeOffTypeId", description="The unique identifier of the time off type (e.g., vacation, sick leave) to apply the balance adjustment to. Must be provided when eventType is 'override'."),
    amount: float | None = Field(None, description="The quantity of hours or days to record for this history entry. Must be provided when eventType is 'override'; positive values increase the balance and negative values decrease it."),
    note: str | None = Field(None, description="An optional free-text note that will be displayed alongside this entry in the employee's time off history."),
) -> dict[str, Any] | ToolResult:
    """Records a time off history entry for an employee, either logging usage against an approved time off request or applying a manual balance adjustment. The entry type determines which additional fields are required."""

    # Construct request model with validation
    try:
        _request = _models.CreateTimeOffHistoryRequest(
            path=_models.CreateTimeOffHistoryRequestPath(employee_id=employee_id),
            body=_models.CreateTimeOffHistoryRequestBody(date=date, event_type=event_type, time_off_request_id=time_off_request_id, time_off_type_id=time_off_type_id, amount=amount, note=note)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_time_off_history_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{employeeId}/time_off/history", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{employeeId}/time_off/history"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_time_off_history_entry")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_time_off_history_entry", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_time_off_history_entry",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Off, Public API
@mcp.tool(
    title="Adjust Time Off Balance",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def adjust_time_off_balance(
    employee_id: int = Field(..., alias="employeeId", description="Unique identifier of the employee whose time off balance is being adjusted."),
    date: str = Field(..., description="The effective date of the balance adjustment as it will appear in history, in ISO 8601 format (YYYY-MM-DD)."),
    time_off_type_id: int = Field(..., alias="timeOffTypeId", description="Unique identifier of the time off type to adjust; must be a non-discretionary (limited) time off type."),
    amount: float = Field(..., description="The number of hours or days to adjust the balance by; use a positive value to add time or a negative value to deduct time."),
    note: str | None = Field(None, description="Optional note providing context or reason for the adjustment, visible in the employee's time off history."),
) -> dict[str, Any] | ToolResult:
    """Creates a balance adjustment for a specific time off type on an employee's account, recorded as an override history entry. Not applicable to discretionary (unlimited) time off types."""

    # Construct request model with validation
    try:
        _request = _models.AdjustTimeOffBalanceRequest(
            path=_models.AdjustTimeOffBalanceRequestPath(employee_id=employee_id),
            body=_models.AdjustTimeOffBalanceRequestBody(date=date, time_off_type_id=time_off_type_id, amount=amount, note=note)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for adjust_time_off_balance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{employeeId}/time_off/balance_adjustment", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{employeeId}/time_off/balance_adjustment"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("adjust_time_off_balance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("adjust_time_off_balance", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="adjust_time_off_balance",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Off, Public API
@mcp.tool(
    title="List Time Off Policies",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_time_off_policies() -> dict[str, Any] | ToolResult:
    """Retrieves all active time off policies for the company, sorted alphabetically by name. Excludes deleted policies and any policies whose associated time off type has been deleted."""

    # Extract parameters for API call
    _http_path = "/api/v1/meta/time_off/policies"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_time_off_policies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_time_off_policies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_time_off_policies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Off, Public API
@mcp.tool(
    title="Create Time Off Request",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_time_off_request(
    employee_id: int = Field(..., alias="employeeId", description="The unique identifier of the employee for whom the time off request is being created."),
    status: Literal["approved", "denied", "declined", "requested"] = Field(..., description="The initial status of the time off request. Use 'requested' to submit for approval; use 'approved' or 'denied' to record a decision directly without triggering approval notifications; 'declined' indicates the employee withdrew the request."),
    start: str = Field(..., description="The first day of the time off period in YYYY-MM-DD format."),
    end: str = Field(..., description="The last day of the time off period in YYYY-MM-DD format. Must be the same as or later than the start date."),
    time_off_type_id: int = Field(..., alias="timeOffTypeId", description="The unique identifier of the time off type (e.g., vacation, sick leave) to apply to this request."),
    amount: float | None = Field(None, description="The total number of hours or days being requested. This value is ignored when a dates array is provided, in which case the sum of the daily amounts is used instead."),
    previous_request: int | None = Field(None, alias="previousRequest", description="The unique identifier of an existing time off request that this request supersedes. The referenced request will be cancelled and replaced by this new request."),
    notes: list[_models.CreateTimeOffRequestBodyNotesItem] | None = Field(None, description="An optional list of notes from the employee or manager providing context or comments about the time off request. Order is not significant."),
    dates: list[_models.CreateTimeOffRequestBodyDatesItem] | None = Field(None, description="An optional per-day breakdown of the time off request, where each item specifies the date and amount for that day. When provided, the top-level amount field is ignored and the sum of daily amounts is used as the total."),
) -> dict[str, Any] | ToolResult:
    """Creates a time off request for an employee with an initial status of approved, denied, or requested. Approved and denied requests are recorded directly without triggering approval notifications; supplying a previousRequest ID cancels the original request and replaces it with this one."""

    # Construct request model with validation
    try:
        _request = _models.CreateTimeOffRequest(
            path=_models.CreateTimeOffRequestPath(employee_id=employee_id),
            body=_models.CreateTimeOffRequestBody(status=status, start=start, end=end, time_off_type_id=time_off_type_id, amount=amount, previous_request=previous_request, notes=notes, dates=dates)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_time_off_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{employeeId}/time_off/request", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{employeeId}/time_off/request"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_time_off_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_time_off_request", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_time_off_request",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Off, Public API
@mcp.tool(
    title="Update Time Off Request Status",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def update_time_off_request_status(
    request_id: int = Field(..., alias="requestId", description="The unique identifier of the time off request whose status is being updated."),
    status: Literal["approved", "denied", "declined", "canceled", "cancelled"] = Field(..., description="The new status to apply to the time off request. Use 'approved' to grant the request, 'denied' or 'declined' to reject it, and 'canceled' or 'cancelled' to withdraw it."),
    note: str | None = Field(None, description="An optional note to attach to the status change, such as a reason for denial or approval context."),
) -> dict[str, Any] | ToolResult:
    """Approves, denies, or cancels an existing time off request by updating its status. Owners and admins can complete all workflow approval steps at once, while standard approvers advance only their current step."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTimeOffRequestStatusRequest(
            path=_models.UpdateTimeOffRequestStatusRequestPath(request_id=request_id),
            body=_models.UpdateTimeOffRequestStatusRequestBody(status=status, note=note)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_time_off_request_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/time_off/requests/{requestId}/status", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/time_off/requests/{requestId}/status"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_time_off_request_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_time_off_request_status", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_time_off_request_status",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Off, Public API
@mcp.tool(
    title="List Time Off Requests",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_time_off_requests(
    start: str = Field(..., description="The beginning of the query window in YYYY-MM-DD format; requests that end on or after this date are included. Must be provided alongside the end parameter."),
    end: str = Field(..., description="The end of the query window in YYYY-MM-DD format; requests that start on or before this date are included. Must be provided alongside the start parameter."),
    id_: int | None = Field(None, alias="id", description="Filters the response to a single time off request matching this ID."),
    action: Literal["view", "approve", "myRequests"] | None = Field(None, description="Scopes the response based on the caller's relationship to the requests: all viewable requests, only those the caller can approve, or only the caller's own requests. Defaults to view if omitted."),
    employee_id: int | None = Field(None, alias="employeeId", description="Filters the response to requests belonging to a single employee matching this ID."),
    type_: str | None = Field(None, alias="type", description="Comma-separated list of time off type IDs to filter results by. When omitted, requests of all time off types are returned."),
    status: str | None = Field(None, description="Comma-separated list of statuses to filter results by; accepted values are approved, denied, superceded, requested, and canceled. When omitted, requests of all statuses are returned."),
    exclude_note: str | None = Field(None, alias="excludeNote", description="When set to a truthy value, the notes object is omitted from each request in the response, reducing payload size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves time off requests that overlap a specified date range, requiring both a start and end date. Results can be filtered by request ID, employee, time off type, status, or scoped to requests the caller is authorized to approve."""

    # Construct request model with validation
    try:
        _request = _models.ListTimeOffRequestsRequest(
            query=_models.ListTimeOffRequestsRequestQuery(id_=id_, action=action, employee_id=employee_id, start=start, end=end, type_=type_, status=status, exclude_note=exclude_note)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_time_off_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/time_off/requests"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_time_off_requests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_time_off_requests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_time_off_requests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Off, Public API
@mcp.tool(
    title="List Time Off Types",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_time_off_types(mode: Literal["request"] | None = Field(None, description="Controls filtering of returned time off types. When set to 'request', results are limited to only the types the authenticated employee has permission to request.")) -> dict[str, Any] | ToolResult:
    """Retrieves all active time off types for the company, along with the company's default hours-per-day schedule. Optionally filter to only the types the authenticated employee has permission to request."""

    # Construct request model with validation
    try:
        _request = _models.ListTimeOffTypesRequest(
            query=_models.ListTimeOffTypesRequestQuery(mode=mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_time_off_types: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/meta/time_off/types"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_time_off_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_time_off_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_time_off_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Training, Public API
@mcp.tool(
    title="List Training Types",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_training_types() -> dict[str, Any] | ToolResult:
    """Retrieves all training types configured for the company, returned as an object keyed by training type ID. Each entry includes the training name, renewable status, renewal frequency, required status, new hire due-date window, category, link URL, description, and self-completion permission. Requires the API key owner to have access to training settings."""

    # Extract parameters for API call
    _http_path = "/api/v1/training/type"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_training_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_training_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_training_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Training, Public API
@mcp.tool(
    title="Create Training Type",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_training_type(
    name: str = Field(..., description="The display name for the new training type."),
    category_name: str | None = Field(None, alias="categoryName", description="The name of the category to associate with this training type, used to group related trainings together."),
    frequency: int | None = Field(None, description="The number of months between required renewals for this training type. Must be provided when renewable is true; ignored otherwise."),
    renewable: bool | None = Field(None, description="Indicates whether this training type must be periodically renewed. When set to true, frequency must also be provided to define the renewal interval in months."),
    id_: int | None = Field(None, alias="id", description="The unique identifier of an existing category to associate with this training type."),
    required: bool | None = Field(None, description="Indicates whether this training type is mandatory for employees. When true, dueFromHireDate may also be specified."),
    due_from_hire_date: int | None = Field(None, alias="dueFromHireDate", description="The number of days after an employee's hire date by which this training must be completed. Only valid when required is true."),
    link_url: str | None = Field(None, alias="linkUrl", description="An optional URL to attach to this training type, such as a link to course materials or an external training resource."),
    description: str | None = Field(None, description="A detailed description of the training type, providing employees and administrators with context about its purpose or content."),
    allow_employees_to_mark_complete: bool | None = Field(None, alias="allowEmployeesToMarkComplete", description="When true, any employee who can view this training type is also permitted to mark it as complete on their own record."),
) -> dict[str, Any] | ToolResult:
    """Creates a new training type with the specified configuration, including optional renewal schedules, hiring requirements, and completion permissions. Requires training settings access; when renewable is true, frequency must be provided, and dueFromHireDate is only applicable when required is true."""

    # Construct request model with validation
    try:
        _request = _models.CreateTrainingTypeRequest(
            body=_models.CreateTrainingTypeRequestBody(name=name, frequency=frequency, renewable=renewable, required=required, due_from_hire_date=due_from_hire_date, link_url=link_url, description=description, allow_employees_to_mark_complete=allow_employees_to_mark_complete,
                category=_models.CreateTrainingTypeRequestBodyCategory(name=category_name, id_=id_) if any(v is not None for v in [category_name, id_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_training_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/training/type"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_training_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_training_type", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_training_type",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Training, Public API
@mcp.tool(
    title="Update Training Type",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_training_type(
    training_type_id: int = Field(..., alias="trainingTypeId", description="The unique identifier of the training type to update."),
    name: str | None = Field(None, description="The display name of the training type."),
    category_name: str | None = Field(None, alias="categoryName", description="The name of the category to assign to this training type. Pass an empty string or null to remove the existing category."),
    frequency: int | None = Field(None, description="The interval in months at which this training must be renewed. Only applicable when the training type is set to renewable."),
    renewable: bool | None = Field(None, description="Indicates whether this training type can be renewed on a recurring basis. If set to true, a frequency value must also be provided."),
    id_: int | None = Field(None, alias="id", description="The unique identifier of the category to assign to this training type."),
    required: bool | None = Field(None, description="Indicates whether completion of this training type is mandatory for employees."),
    due_from_hire_date: int | None = Field(None, alias="dueFromHireDate", description="The number of days after an employee's hire date by which this training must be completed. Only applicable when the training type is marked as required."),
    link_url: str | None = Field(None, alias="linkUrl", description="An optional URL to associate with this training type, such as a link to training materials or an external resource."),
    description: str | None = Field(None, description="A detailed description of the training type, providing context or instructions for employees."),
    allow_employees_to_mark_complete: bool | None = Field(None, alias="allowEmployeesToMarkComplete", description="When enabled, allows any employee who can view this training type to mark it as complete without manager or admin intervention."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing training type by modifying only the fields provided in the request. Requires training settings access; pass an empty string or null for the category field to remove a category assignment."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTrainingTypeRequest(
            path=_models.UpdateTrainingTypeRequestPath(training_type_id=training_type_id),
            body=_models.UpdateTrainingTypeRequestBody(name=name, frequency=frequency, renewable=renewable, required=required, due_from_hire_date=due_from_hire_date, link_url=link_url, description=description, allow_employees_to_mark_complete=allow_employees_to_mark_complete,
                category=_models.UpdateTrainingTypeRequestBodyCategory(name=category_name, id_=id_) if any(v is not None for v in [category_name, id_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_training_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/training/type/{trainingTypeId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/training/type/{trainingTypeId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_training_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_training_type", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_training_type",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Training, Public API
@mcp.tool(
    title="Delete Training Type",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_training_type(training_type_id: int = Field(..., alias="trainingTypeId", description="The unique numeric identifier of the training type to delete. All associated employee trainings must be removed before this operation can succeed.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an existing training type by its ID, requiring training settings access. All employee trainings associated with this type must be removed before this deletion will succeed."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTrainingTypeRequest(
            path=_models.DeleteTrainingTypeRequestPath(training_type_id=training_type_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_training_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/training/type/{trainingTypeId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/training/type/{trainingTypeId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_training_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_training_type", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_training_type",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Training, Public API
@mcp.tool(
    title="List Training Categories",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_training_categories() -> dict[str, Any] | ToolResult:
    """Retrieves all training categories defined for the company, returned as an object keyed by category ID with each entry containing the category ID and name. Requires the API key owner to have access to training settings."""

    # Extract parameters for API call
    _http_path = "/api/v1/training/category"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_training_categories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_training_categories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_training_categories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Training, Public API
@mcp.tool(
    title="Create Training Category",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_training_category(name: str = Field(..., description="The display name for the new training category, used to identify and organize training content.")) -> dict[str, Any] | ToolResult:
    """Creates a new training category to organize training content. Requires training settings access and returns the newly created TrainingCategory on success."""

    # Construct request model with validation
    try:
        _request = _models.CreateTrainingCategoryRequest(
            body=_models.CreateTrainingCategoryRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_training_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/training/category"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_training_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_training_category", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_training_category",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Training, Public API
@mcp.tool(
    title="Update Training Category",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_training_category(
    training_category_id: int = Field(..., alias="trainingCategoryId", description="The unique numeric identifier of the training category to update."),
    name: str = Field(..., description="The new name to assign to the training category; must be unique across all existing training categories."),
) -> dict[str, Any] | ToolResult:
    """Updates the name of an existing training category identified by its ID. Requires training settings access; returns a 409 conflict if a category with the new name already exists."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTrainingCategoryRequest(
            path=_models.UpdateTrainingCategoryRequestPath(training_category_id=training_category_id),
            body=_models.UpdateTrainingCategoryRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_training_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/training/category/{trainingCategoryId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/training/category/{trainingCategoryId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_training_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_training_category", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_training_category",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Training, Public API
@mcp.tool(
    title="Delete Training Category",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_training_category(training_category_id: int = Field(..., alias="trainingCategoryId", description="The unique identifier of the training category to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an existing training category by its unique identifier. The API key owner must have access to training settings to perform this action."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTrainingCategoryRequest(
            path=_models.DeleteTrainingCategoryRequestPath(training_category_id=training_category_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_training_category: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/training/category/{trainingCategoryId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/training/category/{trainingCategoryId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_training_category")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_training_category", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_training_category",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Training, Public API
@mcp.tool(
    title="List Employee Training Records",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_employee_training_records(
    employee_id: int = Field(..., alias="employeeId", description="The unique identifier of the employee whose training records should be retrieved. The API key owner must have permission to view this employee."),
    type_: int | None = Field(None, alias="type", description="The unique identifier of a training type used to filter results to only records of that type. Omit this parameter to return all training records regardless of type."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all training records for a specified employee, returned as an object keyed by training record ID. Optionally filter by training type; note that fields like instructor, credits, hours, and cost are only present when enabled in the company's training settings."""

    # Construct request model with validation
    try:
        _request = _models.ListEmployeeTrainingsRequest(
            path=_models.ListEmployeeTrainingsRequestPath(employee_id=employee_id),
            query=_models.ListEmployeeTrainingsRequestQuery(type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_employee_training_records: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/training/record/employee/{employeeId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/training/record/employee/{employeeId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_employee_training_records")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_employee_training_records", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_employee_training_records",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Training, Public API
@mcp.tool(
    title="Create Employee Training Record",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_employee_training_record(
    employee_id: int = Field(..., alias="employeeId", description="The unique identifier of the employee for whom the training record is being created."),
    completed: str = Field(..., description="The date the training was completed, formatted as ISO 8601 calendar date (yyyy-mm-dd)."),
    type_: int = Field(..., alias="type", description="The identifier of the training type to categorize this record; must correspond to an existing training type ID in the system."),
    currency: str | None = Field(None, description="The currency associated with the training cost, specified as an ISO 4217 three-letter currency code."),
    amount: str | None = Field(None, description="The monetary cost of the training expressed as a decimal string, used alongside the currency field."),
    instructor: str | None = Field(None, description="The full name of the instructor who delivered the training."),
    hours: float | None = Field(None, description="The total duration of the training expressed in hours."),
    credits_: float | None = Field(None, alias="credits", description="The number of credits the employee earned upon completing the training."),
    notes: str | None = Field(None, description="Free-text notes providing additional context or details about the training record."),
) -> dict[str, Any] | ToolResult:
    """Creates a new training record for a specified employee, logging completion date, training type, and optional details such as instructor, hours, credits, cost, and notes. The API key owner must have permission to add training records for the target employee."""

    # Construct request model with validation
    try:
        _request = _models.CreateEmployeeTrainingRecordRequest(
            path=_models.CreateEmployeeTrainingRecordRequestPath(employee_id=employee_id),
            body=_models.CreateEmployeeTrainingRecordRequestBody(completed=completed, instructor=instructor, hours=hours, credits_=credits_, notes=notes, type_=type_,
                cost=_models.CreateEmployeeTrainingRecordRequestBodyCost(currency=currency, amount=amount) if any(v is not None for v in [currency, amount]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_employee_training_record: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/training/record/employee/{employeeId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/training/record/employee/{employeeId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_employee_training_record")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_employee_training_record", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_employee_training_record",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Training, Public API
@mcp.tool(
    title="Update Training Record",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_training_record(
    employee_training_record_id: int = Field(..., alias="employeeTrainingRecordId", description="The unique identifier of the employee training record to update."),
    completed: str = Field(..., description="The date the training was completed, required for every update. Must follow the yyyy-mm-dd format."),
    currency: str | None = Field(None, description="The ISO 4217 three-letter currency code representing the currency of the training cost."),
    amount: str | None = Field(None, description="The monetary cost of the training expressed as a decimal string, corresponding to the specified currency."),
    instructor: str | None = Field(None, description="The full name of the person who delivered or facilitated the training."),
    hours: float | None = Field(None, description="The total duration of the training expressed in hours."),
    credits_: float | None = Field(None, alias="credits", description="The number of credits the employee earned upon completing the training."),
    notes: str | None = Field(None, description="Free-text notes providing any additional context or details about the training record."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing employee training record by its ID. The completion date is required; all other fields such as cost, instructor, hours, credits, and notes are optional."""

    # Construct request model with validation
    try:
        _request = _models.UpdateEmployeeTrainingRecordRequest(
            path=_models.UpdateEmployeeTrainingRecordRequestPath(employee_training_record_id=employee_training_record_id),
            body=_models.UpdateEmployeeTrainingRecordRequestBody(completed=completed, instructor=instructor, hours=hours, credits_=credits_, notes=notes,
                cost=_models.UpdateEmployeeTrainingRecordRequestBodyCost(currency=currency, amount=amount) if any(v is not None for v in [currency, amount]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_training_record: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/training/record/{employeeTrainingRecordId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/training/record/{employeeTrainingRecordId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_training_record")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_training_record", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_training_record",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Training, Public API
@mcp.tool(
    title="Delete Training Record",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_training_record(employee_training_record_id: int = Field(..., alias="employeeTrainingRecordId", description="The unique identifier of the employee training record to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an existing employee training record by its unique ID. The API key owner must have view and edit permissions for both the associated employee and training type."""

    # Construct request model with validation
    try:
        _request = _models.DeleteEmployeeTrainingRecordRequest(
            path=_models.DeleteEmployeeTrainingRecordRequestPath(employee_training_record_id=employee_training_record_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_training_record: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/training/record/{employeeTrainingRecordId}", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/training/record/{employeeTrainingRecordId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_training_record")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_training_record", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_training_record",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Photos, Public API
@mcp.tool(
    title="Upload Employee Photo",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def upload_employee_photo(
    employee_id: int = Field(..., alias="employeeId", description="The unique numeric identifier of the employee whose photo is being uploaded."),
    file_: str = Field(..., alias="file", description="Base64-encoded file content for upload. The image file to set as the employee's photo. Must be a square image (width and height within one pixel of each other), at least 150×150 pixels, no larger than 20MB, and in JPEG, PNG, or BMP format; other formats such as HEIC, SVG, AVIF, and TIFF are not reliably supported.", json_schema_extra={'format': 'byte'}),
) -> dict[str, Any] | ToolResult:
    """Uploads and replaces the photo for a specified employee, updating all size variants. The image must be a square JPEG, PNG, or BMP file of at least 150×150 pixels and no larger than 20MB; employees may upload their own photo if the company has self-photo uploads enabled."""

    # Construct request model with validation
    try:
        _request = _models.UploadEmployeePhotoRequest(
            path=_models.UploadEmployeePhotoRequestPath(employee_id=employee_id),
            body=_models.UploadEmployeePhotoRequestBody(file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_employee_photo: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/v1/employees/{employeeId}/photo", _request.path.model_dump(by_alias=True)) if _request.path else "/api/v1/employees/{employeeId}/photo"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_employee_photo")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_employee_photo", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_employee_photo",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Time Off, Public API
@mcp.tool(
    title="List Who's Out",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_whos_out(
    start: str | None = Field(None, description="The first day of the date range to query, in YYYY-MM-DD format. Defaults to today when omitted."),
    end: str | None = Field(None, description="The last day of the date range to query, in YYYY-MM-DD format. Defaults to 14 days after the start date when omitted."),
    filter_: Literal["off"] | None = Field(None, alias="filter", description="Controls visibility filtering on the results. Set to 'off' to bypass the Who's Out visibility filter and return the full unfiltered feed; omitting this parameter leaves filtering enabled."),
) -> dict[str, Any] | ToolResult:
    """Returns a date-sorted list of employees who are out and company holidays for a specified date range. Includes both time off entries and holidays, each identified by type, defaulting to today through the next 14 days when no dates are provided."""

    # Construct request model with validation
    try:
        _request = _models.ListWhosOutRequest(
            query=_models.ListWhosOutRequestQuery(start=start, end=end, filter_=filter_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_whos_out: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/v1/time_off/whos_out"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_whos_out")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_whos_out", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_whos_out",
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
        print("  python bamboo_hr_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="BambooHR MCP Server")

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
    logger.info("Starting BambooHR MCP Server")
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

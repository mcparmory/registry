#!/usr/bin/env python3
"""
Slack MCP Server

API Info:
- Contact: Slack developer relations (https://api.slack.com/support)

Generated: 2026-05-08 19:05:30 UTC
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
from typing import Any, cast

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

BASE_URL = os.getenv("BASE_URL", "https://slack.com/api")
SERVER_NAME = "Slack"
SERVER_VERSION = "1.0.0"

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
    'slackAuth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["slackAuth"] = _auth.OAuth2Auth()
    logging.info("Authentication configured: slackAuth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for slackAuth not configured: {error_msg}")
    _auth_handlers["slackAuth"] = None

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

mcp = FastMCP("Slack", middleware=[_JsonCoercionMiddleware()])

# Tags: auth
@mcp.tool()
async def verify_authentication() -> dict[str, Any] | ToolResult:
    """Verifies that the provided authentication token is valid and returns information about the authenticated user or application."""

    # Extract parameters for API call
    _http_path = "/auth.test"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("verify_authentication")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("verify_authentication", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="verify_authentication",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: bots
@mcp.tool()
async def get_bot_info(bot: str | None = Field(None, description="The bot user identifier to retrieve information for. If not provided, returns information about the authenticated bot making the request.")) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific bot user. Requires authentication with users:read scope."""

    # Construct request model with validation
    try:
        _request = _models.BotsInfoRequest(
            query=_models.BotsInfoRequestQuery(bot=bot)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bot_info: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bots.info"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bot_info")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bot_info", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bot_info",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: calls
@mcp.tool()
async def update_call(
    id_: str = Field(..., alias="id", description="The unique identifier of the Call to update, as returned by the calls.add method."),
    join_url: str | None = Field(None, description="The URL that clients use to join the Call. This is the primary join link for the call."),
    desktop_app_join_url: str | None = Field(None, description="A direct launch URL for the 3rd-party Call application on desktop clients. When provided, Slack clients will attempt to open the call directly using this URL instead of the standard join_url."),
) -> dict[str, Any] | ToolResult:
    """Updates the join URLs and other metadata for an existing Call, allowing you to modify how clients access the call."""

    # Construct request model with validation
    try:
        _request = _models.CallsUpdateRequest(
            body=_models.CallsUpdateRequestBody(id_=id_, join_url=join_url, desktop_app_join_url=desktop_app_join_url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_call: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/calls.update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_call")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_call", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_call",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: chat
@mcp.tool()
async def delete_message(
    ts: float | None = Field(None, description="The timestamp of the message to delete. This uniquely identifies the message within its channel."),
    as_user: bool | None = Field(None, description="When true, deletes the message as the authenticated user using the `chat:write:user` scope (applies to bot users as well). When false or omitted, deletes the message using the `chat:write:bot` scope."),
    channel: str | None = Field(None, description="Channel containing the message to be deleted."),
) -> dict[str, Any] | ToolResult:
    """Deletes a message from a channel. The message is identified by its timestamp, and deletion can be performed either as the authenticated user or as a bot, depending on the scope and parameters provided."""

    # Construct request model with validation
    try:
        _request = _models.ChatDeleteRequest(
            body=_models.ChatDeleteRequestBody(ts=ts, as_user=as_user, channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/chat.delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_message", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_message",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: chat
@mcp.tool()
async def delete_scheduled_message(
    channel: str = Field(..., description="The channel ID where the scheduled message is queued to be posted."),
    scheduled_message_id: str = Field(..., description="The unique identifier of the scheduled message to delete, as returned from the chat.scheduleMessage operation."),
    as_user: bool | None = Field(None, description="When true, deletes the message as the authenticated user with `chat:write:user` scope (applies to bot users as well). When false or omitted, uses `chat:write:bot` scope instead."),
) -> dict[str, Any] | ToolResult:
    """Removes a pending scheduled message from the queue before it is posted to a channel."""

    # Construct request model with validation
    try:
        _request = _models.ChatDeleteScheduledMessageRequest(
            body=_models.ChatDeleteScheduledMessageRequestBody(as_user=as_user, channel=channel, scheduled_message_id=scheduled_message_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_scheduled_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/chat.deleteScheduledMessage"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_scheduled_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_scheduled_message", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_scheduled_message",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: chat
@mcp.tool()
async def get_message_permalink(
    channel: str = Field(..., description="The unique identifier of the channel or conversation containing the target message."),
    message_ts: str = Field(..., description="The timestamp value (`ts`) of the message, which uniquely identifies it within the channel."),
) -> dict[str, Any] | ToolResult:
    """Generate a shareable permalink URL for a specific message in a channel or conversation. This allows you to create direct links to individual messages that persist even if the original message is edited."""

    # Construct request model with validation
    try:
        _request = _models.ChatGetPermalinkRequest(
            query=_models.ChatGetPermalinkRequestQuery(channel=channel, message_ts=message_ts)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_message_permalink: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/chat.getPermalink"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_message_permalink")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_message_permalink", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_message_permalink",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: chat
@mcp.tool()
async def send_me_message(
    text: str | None = Field(None, description="The text content of the me message to send to the channel."),
    channel: str | None = Field(None, description="Channel to send message to. Can be a public channel, private group or IM channel. Can be an encoded ID, or a name."),
) -> dict[str, Any] | ToolResult:
    """Send a me message (action message) to a channel. Me messages are typically used to share actions or emotes in a conversational context."""

    # Construct request model with validation
    try:
        _request = _models.ChatMeMessageRequest(
            body=_models.ChatMeMessageRequestBody(text=text, channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_me_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/chat.meMessage"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_me_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_me_message", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_me_message",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: chat
@mcp.tool()
async def send_ephemeral_message(
    channel: str = Field(..., description="Target channel, private group, or direct message channel. Accepts encoded channel ID or channel name."),
    user: str = Field(..., description="User ID of the recipient. The user must be a member of the specified channel to receive the ephemeral message."),
    as_user: bool | None = Field(None, description="When true, posts the message as the authenticated user; when false, posts as the bot. Defaults based on available scopes."),
    parse: str | None = Field(None, description="Controls message formatting interpretation. Set to `none` by default to treat text literally, or use other values to enable special formatting."),
    text: str | None = Field(None, description="Message content. Required unless using block-based formatting. Supports text, mentions, and links depending on the `parse` setting."),
    thread_ts: str | None = Field(None, description="Parent message timestamp to post this message as a reply in a thread. Use the parent message's `ts` value, not a reply's timestamp. Only visible if the thread is already active."),
    username: str | None = Field(None, description="Custom display name for the bot. Only applies when `as_user` is false; ignored otherwise."),
) -> dict[str, Any] | ToolResult:
    """Sends an ephemeral message visible only to a specific user in a channel. Ephemeral messages disappear after the user refreshes and are useful for temporary notifications or interactive responses."""

    # Construct request model with validation
    try:
        _request = _models.ChatPostEphemeralRequest(
            body=_models.ChatPostEphemeralRequestBody(as_user=as_user, channel=channel, parse=parse, text=text, thread_ts=thread_ts, user=user, username=username)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_ephemeral_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/chat.postEphemeral"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_ephemeral_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_ephemeral_message", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_ephemeral_message",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: chat
@mcp.tool()
async def send_message_to_channel(
    channel: str = Field(..., description="Target destination for the message: a channel name, private group name, or encoded channel/user ID."),
    as_user: str | None = Field(None, description="When true, posts the message as the authenticated user instead of as a bot. Defaults to false."),
    mrkdwn: bool | None = Field(None, description="When false, disables Slack markup parsing. Enabled by default to allow formatting."),
    parse: str | None = Field(None, description="Controls message formatting behavior. Defaults to `none`; see API documentation for available options."),
    reply_broadcast: bool | None = Field(None, description="When true and used with `thread_ts`, makes the threaded reply visible to all channel members instead of just the thread participants."),
    text: str | None = Field(None, description="Message content. Required unless using blocks or other content fields. Supports text and Slack markup when `mrkdwn` is enabled."),
    thread_ts: str | None = Field(None, description="Timestamp of the parent message to create a threaded reply. Use the parent message's timestamp, not a reply's timestamp."),
    unfurl_links: bool | None = Field(None, description="When true, enables automatic unfurling of text-based content links in the message."),
    unfurl_media: bool | None = Field(None, description="When false, prevents automatic unfurling of media content (images, videos, etc.) in the message."),
    username: str | None = Field(None, description="Custom display name for the bot. Only used when `as_user` is false; ignored otherwise."),
) -> dict[str, Any] | ToolResult:
    """Sends a message to a Slack channel, private group, or direct message. Supports threaded replies, formatting options, and customizable authorship."""

    # Construct request model with validation
    try:
        _request = _models.ChatPostMessageRequest(
            body=_models.ChatPostMessageRequestBody(as_user=as_user, channel=channel, mrkdwn=mrkdwn, parse=parse, reply_broadcast=reply_broadcast, text=text, thread_ts=thread_ts, unfurl_links=unfurl_links, unfurl_media=unfurl_media, username=username)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_message_to_channel: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/chat.postMessage"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_message_to_channel")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_message_to_channel", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_message_to_channel",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: chat
@mcp.tool()
async def schedule_message(
    text: str | None = Field(None, description="The message content to send. Required unless using blocks or other content structures. See formatting documentation for supported syntax options."),
    post_at: str | None = Field(None, description="Unix EPOCH timestamp indicating when the message should be sent. Must be a future time."),
    parse: str | None = Field(None, description="Controls how the message text is processed. Defaults to 'none'. Options include 'full' for markdown-style formatting and 'mrkdwn' for Slack's markup syntax."),
    as_user: bool | None = Field(None, description="When true, posts the message as the authenticated user instead of as a bot. Defaults to false."),
    unfurl_links: bool | None = Field(None, description="When true, enables automatic expansion of text-based links (URLs, articles, etc.) into rich previews."),
    unfurl_media: bool | None = Field(None, description="When false, prevents automatic expansion of media content (images, videos, etc.) in the message."),
    thread_ts: float | None = Field(None, description="The timestamp of a parent message to make this message a threaded reply. Use the parent message's timestamp, not a reply's timestamp."),
    reply_broadcast: bool | None = Field(None, description="When true, makes a threaded reply visible to all channel members. Only applies when thread_ts is provided. Defaults to false."),
    channel: str | None = Field(None, description="Channel, private group, or DM channel to send message to. Can be an encoded ID, or a name. See [below](#channels) for more details."),
) -> dict[str, Any] | ToolResult:
    """Schedules a message to be delivered to a channel at a specified future time. The message content and formatting can be customized with optional parameters for parsing, unfurling, and threading."""

    # Construct request model with validation
    try:
        _request = _models.ChatScheduleMessageRequest(
            body=_models.ChatScheduleMessageRequestBody(text=text, post_at=post_at, parse=parse, as_user=as_user, unfurl_links=unfurl_links, unfurl_media=unfurl_media, thread_ts=thread_ts, reply_broadcast=reply_broadcast, channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for schedule_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/chat.scheduleMessage"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("schedule_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("schedule_message", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="schedule_message",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: chat.scheduledMessages, chat
@mcp.tool()
async def list_scheduled_messages(
    latest: float | None = Field(None, description="A UNIX timestamp marking the most recent message to include in the results. Messages scheduled at or before this time will be returned."),
    oldest: float | None = Field(None, description="A UNIX timestamp marking the oldest message to include in the results. Messages scheduled at or after this time will be returned."),
    limit: int | None = Field(None, description="The maximum number of scheduled messages to return in a single response. Useful for pagination and controlling response size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of scheduled messages, optionally filtered by a time range. Use the oldest and latest parameters to narrow results to a specific period."""

    # Construct request model with validation
    try:
        _request = _models.ChatScheduledMessagesListRequest(
            query=_models.ChatScheduledMessagesListRequestQuery(latest=latest, oldest=oldest, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_scheduled_messages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/chat.scheduledMessages.list"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_scheduled_messages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_scheduled_messages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_scheduled_messages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: chat
@mcp.tool()
async def update_message(
    channel: str = Field(..., description="The channel ID containing the message to be updated."),
    ts: str = Field(..., description="The timestamp (ts) of the message to be updated, used to uniquely identify the message within the channel."),
    as_user: str | None = Field(None, description="Set to `true` to update the message as the authenticated user (applies to bot users as well). Defaults to `false` if not specified."),
    parse: str | None = Field(None, description="Controls how the message content is parsed. Use `none` to disable formatting or `full` to enable all formatting rules. Defaults to `client` if not specified; omitting this parameter will reset to the default value."),
    text: str | None = Field(None, description="The new message text using standard formatting rules. Not required if `blocks` or `attachments` are being provided instead."),
) -> dict[str, Any] | ToolResult:
    """Updates the text and formatting of an existing message in a channel. Requires the message timestamp and channel ID to identify which message to update."""

    # Construct request model with validation
    try:
        _request = _models.ChatUpdateRequest(
            body=_models.ChatUpdateRequestBody(as_user=as_user, channel=channel, parse=parse, text=text, ts=ts)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/chat.update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_message", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_message",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def archive_conversation(channel: str | None = Field(None, description="ID of conversation to archive")) -> dict[str, Any] | ToolResult:
    """Archives a conversation, removing it from the active conversation list while preserving its history for future reference."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsArchiveRequest(
            body=_models.ConversationsArchiveRequestBody(channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for archive_conversation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.archive"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("archive_conversation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("archive_conversation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="archive_conversation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def close_conversation(channel: str | None = Field(None, description="Conversation to close.")) -> dict[str, Any] | ToolResult:
    """Closes an active direct message conversation, either between two users or among multiple participants. This action archives the conversation and prevents further messages in that thread."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsCloseRequest(
            body=_models.ConversationsCloseRequestBody(channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for close_conversation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.close"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("close_conversation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("close_conversation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="close_conversation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def create_conversation(
    is_private: bool | None = Field(None, description="Set to true to create a private channel with restricted access, or false (default) to create a public channel visible to all users."),
    name: str | None = Field(None, description="Name of the public or private channel to create"),
) -> dict[str, Any] | ToolResult:
    """Creates a new conversation channel that can be either public or private. Public channels are visible to all users, while private channels restrict access to invited members only."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsCreateRequest(
            body=_models.ConversationsCreateRequestBody(is_private=is_private, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_conversation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.create"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_conversation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_conversation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_conversation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def get_conversation_history(
    latest: float | None = Field(None, description="Unix timestamp marking the end of the time range; only messages up to this point are included in results."),
    oldest: float | None = Field(None, description="Unix timestamp marking the start of the time range; only messages from this point forward are included in results."),
    inclusive: bool | None = Field(None, description="When true, includes messages with timestamps exactly matching the latest or oldest values; when false, excludes them. Only applies when at least one timestamp boundary is specified."),
    limit: int | None = Field(None, description="Maximum number of messages to return per request. The actual number returned may be less than requested, even if additional messages exist."),
    channel: str | None = Field(None, description="Conversation ID to fetch history for."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the message and event history for a conversation within an optional time range. Results can be paginated and filtered by timestamp boundaries."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsHistoryRequest(
            query=_models.ConversationsHistoryRequestQuery(latest=latest, oldest=oldest, inclusive=inclusive, limit=limit, channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_conversation_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_conversation_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_conversation_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_conversation_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def get_conversation_info(
    include_locale: bool | None = Field(None, description="Include the locale language and region information for the conversation in the response."),
    include_num_members: bool | None = Field(None, description="Include the total number of members in the conversation in the response."),
    channel: str | None = Field(None, description="Conversation ID to learn more about"),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific conversation, optionally including locale and member count metadata."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsInfoRequest(
            query=_models.ConversationsInfoRequestQuery(include_locale=include_locale, include_num_members=include_num_members, channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_conversation_info: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.info"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_conversation_info")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_conversation_info", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_conversation_info",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def add_users_to_conversation(
    users: str | None = Field(None, description="A comma-separated list of user IDs to invite to the conversation. Up to 1000 users can be added in a single request."),
    channel: str | None = Field(None, description="The ID of the public or private channel to invite user(s) to."),
) -> dict[str, Any] | ToolResult:
    """Adds one or more users to a conversation channel. Specify users by their IDs in a comma-separated list."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsInviteRequest(
            body=_models.ConversationsInviteRequestBody(users=users, channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_users_to_conversation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.invite"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_users_to_conversation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_users_to_conversation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_users_to_conversation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def join_conversation(channel: str | None = Field(None, description="ID of conversation to join")) -> dict[str, Any] | ToolResult:
    """Joins the authenticated user to an existing conversation, enabling participation in the conversation's messages and interactions."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsJoinRequest(
            body=_models.ConversationsJoinRequestBody(channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for join_conversation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.join"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("join_conversation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("join_conversation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="join_conversation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def remove_user_from_conversation(
    user: str | None = Field(None, description="The unique identifier of the user to be removed from the conversation."),
    channel: str | None = Field(None, description="ID of conversation to remove user from."),
) -> dict[str, Any] | ToolResult:
    """Removes a specified user from a conversation, effectively ending their participation in that conversation thread."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsKickRequest(
            body=_models.ConversationsKickRequestBody(user=user, channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_user_from_conversation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.kick"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_user_from_conversation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_user_from_conversation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_user_from_conversation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def leave_conversation(channel: str | None = Field(None, description="Conversation to leave")) -> dict[str, Any] | ToolResult:
    """Removes the authenticated user from a conversation, ending their participation and access to that conversation."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsLeaveRequest(
            body=_models.ConversationsLeaveRequestBody(channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for leave_conversation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.leave"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("leave_conversation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("leave_conversation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="leave_conversation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def list_conversations(
    exclude_archived: bool | None = Field(None, description="When set to true, archived channels are excluded from the results. Useful for focusing on active conversations only."),
    types: str | None = Field(None, description="Filters conversations by type using a comma-separated list. Supported types are public_channel, private_channel, mpim (multi-person direct messages), and im (direct messages). Omit to include all types."),
    limit: int | None = Field(None, description="Maximum number of conversations to return per request, up to 1000. The API may return fewer items than requested even if more results are available."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of all conversations (channels and direct messages) in a Slack workspace, with options to filter by type and archive status."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsListRequest(
            query=_models.ConversationsListRequestQuery(exclude_archived=exclude_archived, types=types, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_conversations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.list"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_conversations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_conversations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_conversations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def mark_conversation_read(
    ts: float = Field(..., description="The message timestamp to mark as read. If provided, sets your read cursor to this message; if omitted, marks the entire conversation as read up to the current time."),
    channel: str | None = Field(None, description="Channel or conversation to set the read cursor for."),
) -> dict[str, Any] | ToolResult:
    """Mark a conversation as read by setting the read cursor to a specific message timestamp. This updates your read position in the channel."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsMarkRequest(
            body=_models.ConversationsMarkRequestBody(ts=ts, channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for mark_conversation_read: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.mark"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("mark_conversation_read")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("mark_conversation_read", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="mark_conversation_read",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def list_conversation_members(
    limit: int | None = Field(None, description="Maximum number of members to return in a single request. The API may return fewer members than requested if the end of the list is reached."),
    channel: str | None = Field(None, description="ID of the conversation to retrieve members for"),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of members in a conversation. Use the limit parameter to control the number of results returned per request."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsMembersRequest(
            query=_models.ConversationsMembersRequestQuery(limit=limit, channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_conversation_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.members"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_conversation_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_conversation_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_conversation_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def open_direct_message(
    users: str | None = Field(None, description="Comma-separated list of user identifiers to include in the direct message. Provide a single user for a 1:1 DM, or multiple users for a group DM. The order of users is preserved in the returned conversation. Either this parameter or a channel must be supplied."),
    return_im: bool | None = Field(None, description="When true, returns the complete direct message channel definition in the response, including all channel metadata and settings."),
) -> dict[str, Any] | ToolResult:
    """Opens or resumes a direct message conversation, either a 1:1 DM with a single user or a multi-person DM with multiple users. The conversation is created if it doesn't exist, or resumed if it already does."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsOpenRequest(
            body=_models.ConversationsOpenRequestBody(users=users, return_im=return_im)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for open_direct_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.open"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("open_direct_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("open_direct_message", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="open_direct_message",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def update_conversation(
    channel: str | None = Field(None, description="ID of conversation to rename"),
    name: str | None = Field(None, description="New name for conversation."),
) -> dict[str, Any] | ToolResult:
    """Updates the name of an existing conversation. This operation allows you to rename a conversation to better organize or identify it."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsRenameRequest(
            body=_models.ConversationsRenameRequestBody(channel=channel, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_conversation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.rename"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_conversation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_conversation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_conversation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def get_conversation_thread(
    ts: float | None = Field(None, description="The timestamp of the parent message whose thread you want to retrieve. This message must exist and can have zero or more replies; if there are no replies, only the parent message itself is returned."),
    latest: float | None = Field(None, description="The end of the time range for filtering messages, specified as a Unix timestamp. Only messages up to this time will be included in results."),
    oldest: float | None = Field(None, description="The start of the time range for filtering messages, specified as a Unix timestamp. Only messages from this time onward will be included in results."),
    inclusive: bool | None = Field(None, description="When true, includes messages that match the exact latest or oldest timestamp in results. Only applies when at least one of those timestamps is specified."),
    limit: int | None = Field(None, description="The maximum number of messages to return in a single response. The actual number returned may be less if the thread contains fewer messages than requested."),
    channel: str | None = Field(None, description="Conversation ID to fetch thread from."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a thread of messages from a conversation, including a parent message and all its replies within an optional time range."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsRepliesRequest(
            query=_models.ConversationsRepliesRequestQuery(ts=ts, latest=latest, oldest=oldest, inclusive=inclusive, limit=limit, channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_conversation_thread: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.replies"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_conversation_thread")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_conversation_thread", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_conversation_thread",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def update_conversation_purpose(
    purpose: str | None = Field(None, description="The new purpose or topic description for the conversation. Provide a clear, concise statement that describes the conversation's intent or focus."),
    channel: str | None = Field(None, description="Conversation to set the purpose of"),
) -> dict[str, Any] | ToolResult:
    """Updates the purpose or topic description for a conversation. This helps organize and clarify the conversation's intent."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsSetPurposeRequest(
            body=_models.ConversationsSetPurposeRequestBody(purpose=purpose, channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_conversation_purpose: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.setPurpose"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_conversation_purpose")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_conversation_purpose", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_conversation_purpose",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def update_conversation_topic(
    topic: str | None = Field(None, description="The new topic string for the conversation. Plain text only; formatting and linkification are not supported."),
    channel: str | None = Field(None, description="Conversation to set the topic of"),
) -> dict[str, Any] | ToolResult:
    """Updates the topic for a conversation. The topic is a plain text string used to label or describe the conversation's subject matter."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsSetTopicRequest(
            body=_models.ConversationsSetTopicRequestBody(topic=topic, channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_conversation_topic: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.setTopic"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_conversation_topic")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_conversation_topic", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_conversation_topic",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: conversations
@mcp.tool()
async def unarchive_conversation(channel: str | None = Field(None, description="ID of conversation to unarchive")) -> dict[str, Any] | ToolResult:
    """Restores an archived conversation to active status, reversing the archival action and making it accessible again."""

    # Construct request model with validation
    try:
        _request = _models.ConversationsUnarchiveRequest(
            body=_models.ConversationsUnarchiveRequestBody(channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unarchive_conversation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/conversations.unarchive"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unarchive_conversation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unarchive_conversation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unarchive_conversation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: dnd
@mcp.tool()
async def disable_dnd() -> dict[str, Any] | ToolResult:
    """Immediately deactivates the current user's Do Not Disturb mode, restoring normal notification delivery."""

    # Extract parameters for API call
    _http_path = "/dnd.endDnd"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("disable_dnd")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("disable_dnd", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="disable_dnd",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dnd
@mcp.tool()
async def end_dnd_snooze() -> dict[str, Any] | ToolResult:
    """Immediately ends the current user's do-not-disturb snooze mode, restoring normal notification delivery."""

    # Extract parameters for API call
    _http_path = "/dnd.endSnooze"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("end_dnd_snooze")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("end_dnd_snooze", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="end_dnd_snooze",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dnd
@mcp.tool()
async def get_dnd_status(user: str | None = Field(None, description="The user ID or username to fetch the Do Not Disturb status for. If not provided, returns the status for the authenticated user making the request.")) -> dict[str, Any] | ToolResult:
    """Retrieves the current Do Not Disturb status for a user, indicating whether they have notifications muted or disabled."""

    # Construct request model with validation
    try:
        _request = _models.DndInfoRequest(
            query=_models.DndInfoRequestQuery(user=user)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_dnd_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/dnd.info"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_dnd_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_dnd_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_dnd_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: dnd
@mcp.tool()
async def enable_do_not_disturb(num_minutes: str = Field(..., description="Duration in minutes from the current time until Do Not Disturb mode should automatically turn off. Must be a positive integer.")) -> dict[str, Any] | ToolResult:
    """Activates Do Not Disturb mode for the current user with a specified duration. If Do Not Disturb is already active, this updates the snooze duration."""

    # Construct request model with validation
    try:
        _request = _models.DndSetSnoozeRequest(
            body=_models.DndSetSnoozeRequestBody(num_minutes=num_minutes)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for enable_do_not_disturb: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/dnd.setSnooze"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("enable_do_not_disturb")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("enable_do_not_disturb", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="enable_do_not_disturb",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: dnd
@mcp.tool()
async def get_team_dnd_status(users: str = Field(..., description="Comma-separated list of user identifiers to retrieve Do Not Disturb status for. Supports up to 50 users per request.")) -> dict[str, Any] | ToolResult:
    """Retrieves the Do Not Disturb status for specified users on a team, allowing you to check up to 50 users at once."""

    # Construct request model with validation
    try:
        _request = _models.DndTeamInfoRequest(
            query=_models.DndTeamInfoRequestQuery(users=users)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team_dnd_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/dnd.teamInfo"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_team_dnd_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_team_dnd_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_team_dnd_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: emoji
@mcp.tool()
async def list_emoji() -> dict[str, Any] | ToolResult:
    """Retrieves all custom emoji configured for the workspace. This includes emoji names, URLs, and metadata for all custom emoji available to team members."""

    # Extract parameters for API call
    _http_path = "/emoji.list"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_emoji")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_emoji", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_emoji",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: files.comments, files
@mcp.tool()
async def delete_file_comment(
    id_: str | None = Field(None, alias="id", description="The unique identifier of the comment to delete."),
    file_: str | None = Field(None, alias="file", description="File to delete a comment from."),
) -> dict[str, Any] | ToolResult:
    """Deletes an existing comment on a file. Requires the comment ID to identify which comment to remove."""

    # Construct request model with validation
    try:
        _request = _models.FilesCommentsDeleteRequest(
            body=_models.FilesCommentsDeleteRequestBody(id_=id_, file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_file_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/files.comments.delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_file_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_file_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_file_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def delete_file(file_: str | None = Field(None, alias="file", description="ID of file to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a file from the system. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.FilesDeleteRequest(
            body=_models.FilesDeleteRequestBody(file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/files.delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def get_file_info(
    limit: int | None = Field(None, description="The maximum number of file records to return in the response. The API may return fewer items than requested if the end of the list is reached."),
    file_: str | None = Field(None, alias="file", description="Specify a file by providing its ID."),
) -> dict[str, Any] | ToolResult:
    """Retrieves metadata and information about a specific file, including details such as size, type, timestamps, and other file attributes."""

    # Construct request model with validation
    try:
        _request = _models.FilesInfoRequest(
            query=_models.FilesInfoRequestQuery(limit=limit, file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_info: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/files.info"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_info")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_info", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_info",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def list_files(
    user: str | None = Field(None, description="Filter results to files created by a specific user. Provide the user identifier."),
    ts_from: float | None = Field(None, description="Filter results to files created on or after this timestamp (inclusive). Use Unix timestamp format."),
    ts_to: float | None = Field(None, description="Filter results to files created on or before this timestamp (inclusive). Use Unix timestamp format."),
    types: str | None = Field(None, description="Filter results by file type. Accepts multiple comma-separated values (e.g., spaces,snippets). Defaults to all types if not specified."),
    show_files_hidden_by_limit: bool | None = Field(None, description="When enabled, includes truncated file information for files hidden due to age or the team exceeding file storage limits. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of files with optional filtering by user, date range, file type, and visibility. Supports showing truncated information for files hidden due to age or team file limits."""

    # Construct request model with validation
    try:
        _request = _models.FilesListRequest(
            query=_models.FilesListRequestQuery(user=user, ts_from=ts_from, ts_to=ts_to, types=types, show_files_hidden_by_limit=show_files_hidden_by_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_files: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/files.list"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def revoke_file_public_url(file_: str | None = Field(None, alias="file", description="File to revoke")) -> dict[str, Any] | ToolResult:
    """Revokes public and external sharing access for a file, preventing further access via public URLs."""

    # Construct request model with validation
    try:
        _request = _models.FilesRevokePublicUrlRequest(
            body=_models.FilesRevokePublicUrlRequestBody(file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_file_public_url: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/files.revokePublicURL"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_file_public_url")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_file_public_url", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_file_public_url",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def enable_file_public_sharing(file_: str | None = Field(None, alias="file", description="File to share")) -> dict[str, Any] | ToolResult:
    """Enables public sharing for a file by generating a shareable public URL that allows external users to access the file without authentication."""

    # Construct request model with validation
    try:
        _request = _models.FilesSharedPublicUrlRequest(
            body=_models.FilesSharedPublicUrlRequestBody(file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for enable_file_public_sharing: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/files.sharedPublicURL"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("enable_file_public_sharing")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("enable_file_public_sharing", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="enable_file_public_sharing",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: pins
@mcp.tool()
async def add_pin_to_channel(
    channel: str = Field(..., description="The channel where the item will be pinned. Specify the channel ID or name."),
    timestamp: str | None = Field(None, description="The timestamp of the message to pin. Use the message's timestamp identifier to specify which message should be pinned."),
) -> dict[str, Any] | ToolResult:
    """Pins a message to a channel, making it easily accessible to channel members. Requires authentication with pins:write scope."""

    # Construct request model with validation
    try:
        _request = _models.PinsAddRequest(
            body=_models.PinsAddRequestBody(channel=channel, timestamp=timestamp)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_pin_to_channel: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/pins.add"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_pin_to_channel")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_pin_to_channel", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_pin_to_channel",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: pins
@mcp.tool()
async def list_channel_pins(channel: str = Field(..., description="The channel ID or name to retrieve pinned items from.")) -> dict[str, Any] | ToolResult:
    """Retrieves all items pinned to a specified channel. Pinned items are messages or files that have been marked for easy reference within the channel."""

    # Construct request model with validation
    try:
        _request = _models.PinsListRequest(
            query=_models.PinsListRequestQuery(channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_channel_pins: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/pins.list"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_channel_pins")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_channel_pins", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_channel_pins",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: pins
@mcp.tool()
async def remove_pin_from_channel(
    channel: str = Field(..., description="The channel ID or name where the pinned item is located."),
    timestamp: str | None = Field(None, description="The timestamp of the specific message to un-pin. If omitted, the most recently pinned message in the channel will be removed."),
) -> dict[str, Any] | ToolResult:
    """Removes a pinned message from a channel. Specify the channel and optionally the message timestamp to un-pin."""

    # Construct request model with validation
    try:
        _request = _models.PinsRemoveRequest(
            body=_models.PinsRemoveRequestBody(channel=channel, timestamp=timestamp)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_pin_from_channel: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/pins.remove"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_pin_from_channel")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_pin_from_channel", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_pin_from_channel",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: reactions
@mcp.tool()
async def add_reaction_to_message(
    channel: str = Field(..., description="The channel ID where the message to react to is located."),
    name: str = Field(..., description="The emoji name to add as a reaction (e.g., 'thumbsup', 'heart'). Use the emoji name without colons or special characters."),
    timestamp: str = Field(..., description="The message timestamp (in seconds or milliseconds since epoch) identifying which message to add the reaction to."),
) -> dict[str, Any] | ToolResult:
    """Adds an emoji reaction to a message in a channel. Requires authentication with reactions:write scope."""

    # Construct request model with validation
    try:
        _request = _models.ReactionsAddRequest(
            body=_models.ReactionsAddRequestBody(channel=channel, name=name, timestamp=timestamp)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_reaction_to_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/reactions.add"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_reaction_to_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_reaction_to_message", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_reaction_to_message",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: reactions
@mcp.tool()
async def get_reactions(
    file_comment: str | None = Field(None, description="The file comment to retrieve reactions for. Specify either this parameter, timestamp, or neither to get reactions for the item context."),
    full: bool | None = Field(None, description="When true, returns the complete list of all reactions. When false or omitted, may return a truncated list."),
    timestamp: str | None = Field(None, description="The timestamp of the message to retrieve reactions for, typically in Unix epoch format. Specify either this parameter, file_comment, or neither to get reactions for the item context."),
    channel: str | None = Field(None, description="Channel where the message to get reactions for was posted."),
    file_: str | None = Field(None, alias="file", description="File to get reactions for."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all reactions added to a specific message, file comment, or other item. Use this to see what emoji reactions users have added to content."""

    # Construct request model with validation
    try:
        _request = _models.ReactionsGetRequest(
            query=_models.ReactionsGetRequestQuery(file_comment=file_comment, full=full, timestamp=timestamp, channel=channel, file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_reactions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/reactions.get"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_reactions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_reactions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_reactions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reactions
@mcp.tool()
async def list_user_reactions(
    user: str | None = Field(None, description="The user whose reactions to retrieve. If not specified, defaults to the authenticated user."),
    full: bool | None = Field(None, description="When enabled, returns the complete list of all reactions without pagination limits."),
    limit: int | None = Field(None, description="Maximum number of reactions to return per request. The actual number returned may be less than requested if fewer items remain."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of emoji reactions made by a user. By default, returns reactions from the authenticated user, but can be filtered to show reactions from a specific user."""

    # Construct request model with validation
    try:
        _request = _models.ReactionsListRequest(
            query=_models.ReactionsListRequestQuery(user=user, full=full, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_reactions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/reactions.list"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_reactions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_reactions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_reactions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reactions
@mcp.tool()
async def remove_reaction(
    name: str = Field(..., description="The emoji name of the reaction to remove (e.g., 'thumbsup', 'heart'). Must match the exact reaction name."),
    file_comment: str | None = Field(None, description="The file comment ID from which to remove the reaction. Use this when removing a reaction from a file comment instead of a message."),
    timestamp: str | None = Field(None, description="The message timestamp identifying which message to remove the reaction from. Use this when removing a reaction from a message instead of a file comment."),
    channel: str | None = Field(None, description="Channel where the message to remove reaction from was posted."),
    file_: str | None = Field(None, alias="file", description="File to remove reaction from."),
) -> dict[str, Any] | ToolResult:
    """Removes an emoji reaction from a message or file comment. Specify either a message timestamp or file comment ID to identify the target item."""

    # Construct request model with validation
    try:
        _request = _models.ReactionsRemoveRequest(
            body=_models.ReactionsRemoveRequestBody(name=name, file_comment=file_comment, timestamp=timestamp, channel=channel, file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_reaction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/reactions.remove"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_reaction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_reaction", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_reaction",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: reminders
@mcp.tool()
async def create_reminder(
    text: str = Field(..., description="The reminder message content that will be displayed to the recipient."),
    time_: str = Field(..., alias="time", description="When the reminder should trigger: a Unix timestamp (up to five years in the future), seconds from now (for reminders within 24 hours), or natural language phrasing like 'in 15 minutes' or 'every Thursday'."),
    user: str | None = Field(None, description="The user who will receive the reminder. If omitted, the reminder is assigned to the user who created it."),
) -> dict[str, Any] | ToolResult:
    """Creates a reminder that will be delivered at a specified time. The reminder can be scheduled for a specific Unix timestamp, a relative time within 24 hours, or using natural language descriptions."""

    # Construct request model with validation
    try:
        _request = _models.RemindersAddRequest(
            body=_models.RemindersAddRequestBody(text=text, time_=time_, user=user)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_reminder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/reminders.add"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_reminder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_reminder", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_reminder",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: search
@mcp.tool()
async def search_messages(
    query: str = Field(..., description="Search query string to match against message content. Supports the platform's standard search syntax."),
    highlight: bool | None = Field(None, description="Enable query highlight markers in results to visually distinguish matched terms within message content."),
    sort: str | None = Field(None, description="Sort results by relevance score or message timestamp. Defaults to score-based sorting if not specified."),
    sort_dir: str | None = Field(None, description="Sort direction for results: ascending (`asc`) for oldest/lowest first, or descending (`desc`) for newest/highest first."),
) -> dict[str, Any] | ToolResult:
    """Searches for messages matching a query string, with optional result highlighting and sorting capabilities. Returns matching messages from the workspace."""

    # Construct request model with validation
    try:
        _request = _models.SearchMessagesRequest(
            query=_models.SearchMessagesRequestQuery(highlight=highlight, query=query, sort=sort, sort_dir=sort_dir)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_messages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/search.messages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_messages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_messages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_messages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: stars
@mcp.tool()
async def add_star(
    file_comment: str | None = Field(None, description="The file comment identifier to star. Specify either this or timestamp, but not both."),
    timestamp: str | None = Field(None, description="The timestamp of the message to star. Specify either this or file_comment, but not both."),
    channel: str | None = Field(None, description="Channel to add star to, or channel where the message to add star to was posted (used with `timestamp`)."),
) -> dict[str, Any] | ToolResult:
    """Adds a star to a specific item, such as a file comment or message. Requires authentication with stars:write scope."""

    # Construct request model with validation
    try:
        _request = _models.StarsAddRequest(
            body=_models.StarsAddRequestBody(file_comment=file_comment, timestamp=timestamp, channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_star: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stars.add"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_star")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_star", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_star",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: stars
@mcp.tool()
async def list_stars(limit: int | None = Field(None, description="Maximum number of items to return per request. The API may return fewer items than requested if the end of the list is reached.")) -> dict[str, Any] | ToolResult:
    """Retrieves a list of stars for the authenticated user, with optional pagination control."""

    # Construct request model with validation
    try:
        _request = _models.StarsListRequest(
            query=_models.StarsListRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_stars: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stars.list"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_stars")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_stars", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_stars",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: stars
@mcp.tool()
async def remove_star(
    file_comment: str | None = Field(None, description="The file comment to remove the star from. Either this or timestamp must be provided."),
    timestamp: str | None = Field(None, description="The timestamp of the message to remove the star from. Either this or file_comment must be provided."),
    channel: str | None = Field(None, description="Channel to remove star from, or channel where the message to remove star from was posted (used with `timestamp`)."),
) -> dict[str, Any] | ToolResult:
    """Removes a star from a specific item, such as a file comment or message. Requires authentication with stars:write scope."""

    # Construct request model with validation
    try:
        _request = _models.StarsRemoveRequest(
            body=_models.StarsRemoveRequestBody(file_comment=file_comment, timestamp=timestamp, channel=channel)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_star: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/stars.remove"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_star")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_star", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_star",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: team
@mcp.tool()
async def get_team_info(team: str | None = Field(None, description="Optional team identifier to retrieve information for a specific team. If omitted, returns the current team. Only returns teams accessible to the authenticated token through external shared channels.")) -> dict[str, Any] | ToolResult:
    """Retrieves information about a team. If no team is specified, returns information about the authenticated user's current team. The authenticated token must have the `team:read` scope."""

    # Construct request model with validation
    try:
        _request = _models.TeamInfoRequest(
            query=_models.TeamInfoRequestQuery(team=team)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team_info: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/team.info"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_team_info")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_team_info", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_team_info",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: team.profile, team
@mcp.tool()
async def get_team_profile(visibility: str | None = Field(None, description="Optional filter to retrieve only team profiles matching a specific visibility level.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed profile information for a team, with optional filtering by visibility settings."""

    # Construct request model with validation
    try:
        _request = _models.TeamProfileGetRequest(
            query=_models.TeamProfileGetRequestQuery(visibility=visibility)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team_profile: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/team.profile.get"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_team_profile")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_team_profile", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_team_profile",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: usergroups
@mcp.tool()
async def create_usergroup(
    name: str = Field(..., description="A unique name for the User Group. Must not duplicate any existing User Group names."),
    channels: str | None = Field(None, description="Comma-separated list of encoded channel IDs to set as defaults for this User Group."),
    description: str | None = Field(None, description="A brief description of the User Group's purpose or membership."),
    handle: str | None = Field(None, description="A unique mention handle for the User Group. Must not conflict with existing channel names, user handles, or other User Group handles."),
    include_count: bool | None = Field(None, description="When enabled, the response will include the count of users currently in the User Group."),
) -> dict[str, Any] | ToolResult:
    """Create a new User Group with a unique name and optional configuration for channels, description, and mention handle."""

    # Construct request model with validation
    try:
        _request = _models.UsergroupsCreateRequest(
            body=_models.UsergroupsCreateRequestBody(channels=channels, description=description, handle=handle, include_count=include_count, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_usergroup: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/usergroups.create"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_usergroup")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_usergroup", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_usergroup",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: usergroups
@mcp.tool()
async def disable_usergroup(
    usergroup: str = Field(..., description="The encoded ID of the User Group to disable. This identifier uniquely identifies the target group."),
    include_count: bool | None = Field(None, description="When enabled, the response will include a count of users currently in the User Group."),
) -> dict[str, Any] | ToolResult:
    """Disable an existing User Group, preventing its use while preserving its configuration and membership data."""

    # Construct request model with validation
    try:
        _request = _models.UsergroupsDisableRequest(
            body=_models.UsergroupsDisableRequestBody(include_count=include_count, usergroup=usergroup)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for disable_usergroup: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/usergroups.disable"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("disable_usergroup")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("disable_usergroup", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="disable_usergroup",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: usergroups
@mcp.tool()
async def enable_usergroup(
    usergroup: str = Field(..., description="The encoded ID of the User Group to enable. This identifier uniquely identifies the target User Group."),
    include_count: bool | None = Field(None, description="When true, the response includes the total number of users currently in the User Group."),
) -> dict[str, Any] | ToolResult:
    """Activate a disabled User Group, making it available for use. Optionally retrieve the current member count."""

    # Construct request model with validation
    try:
        _request = _models.UsergroupsEnableRequest(
            body=_models.UsergroupsEnableRequestBody(include_count=include_count, usergroup=usergroup)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for enable_usergroup: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/usergroups.enable"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("enable_usergroup")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("enable_usergroup", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="enable_usergroup",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: usergroups
@mcp.tool()
async def list_usergroups(
    include_users: bool | None = Field(None, description="Include the complete list of users belonging to each User Group in the response."),
    include_count: bool | None = Field(None, description="Include the total count of users in each User Group without listing individual members."),
    include_disabled: bool | None = Field(None, description="Include User Groups that have been disabled in addition to active groups."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all User Groups configured for a team, with optional details about group membership and status."""

    # Construct request model with validation
    try:
        _request = _models.UsergroupsListRequest(
            query=_models.UsergroupsListRequestQuery(include_users=include_users, include_count=include_count, include_disabled=include_disabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_usergroups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/usergroups.list"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_usergroups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_usergroups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_usergroups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: usergroups
@mcp.tool()
async def update_usergroup(
    usergroup: str = Field(..., description="The encoded ID of the User Group to update. This identifier is required to target the correct group."),
    handle: str | None = Field(None, description="A unique mention handle for the User Group. Must be distinct across all channels, users, and other User Groups in the workspace."),
    description: str | None = Field(None, description="A brief description of the User Group's purpose or membership."),
    channels: str | None = Field(None, description="A comma-separated list of encoded channel IDs to set as defaults for this User Group."),
    include_count: bool | None = Field(None, description="When enabled, the response will include the total count of users currently in the User Group."),
) -> dict[str, Any] | ToolResult:
    """Update an existing User Group's properties such as handle, description, and associated channels. Requires usergroups:write scope."""

    # Construct request model with validation
    try:
        _request = _models.UsergroupsUpdateRequest(
            body=_models.UsergroupsUpdateRequestBody(handle=handle, description=description, channels=channels, include_count=include_count, usergroup=usergroup)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_usergroup: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/usergroups.update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_usergroup")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_usergroup", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_usergroup",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: usergroups.users, usergroups
@mcp.tool()
async def list_usergroup_members(
    usergroup: str = Field(..., description="The encoded ID of the User Group whose members you want to list."),
    include_disabled: bool | None = Field(None, description="When enabled, includes results from User Groups that are currently disabled. By default, only active User Groups are included."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all users who are members of a specified User Group. Optionally include users from disabled User Groups in the results."""

    # Construct request model with validation
    try:
        _request = _models.UsergroupsUsersListRequest(
            query=_models.UsergroupsUsersListRequestQuery(include_disabled=include_disabled, usergroup=usergroup)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_usergroup_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/usergroups.users.list"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_usergroup_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_usergroup_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_usergroup_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: usergroups.users, usergroups
@mcp.tool()
async def update_usergroup_users(
    usergroup: str = Field(..., description="The encoded ID of the User Group to update. This identifies which group's membership will be replaced."),
    users: str = Field(..., description="A comma-separated list of encoded user IDs that defines the complete new membership for the User Group. All previous members not in this list will be removed."),
    include_count: bool | None = Field(None, description="When true, the response will include a count of the total number of users in the User Group."),
) -> dict[str, Any] | ToolResult:
    """Update the complete membership of a User Group by replacing all users with a new list of user IDs."""

    # Construct request model with validation
    try:
        _request = _models.UsergroupsUsersUpdateRequest(
            body=_models.UsergroupsUsersUpdateRequestBody(include_count=include_count, usergroup=usergroup, users=users)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_usergroup_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/usergroups.users.update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_usergroup_users")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_usergroup_users", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_usergroup_users",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_user_conversations(
    user: str | None = Field(None, description="Filter conversations to only those where a specific user is a member. Non-public channels are only included if the calling user shares membership in them."),
    types: str | None = Field(None, description="Filter by conversation type using a comma-separated list. Supported types are: public_channel, private_channel, mpim (multi-person direct message), and im (direct message)."),
    exclude_archived: bool | None = Field(None, description="Set to true to exclude archived conversations from the results."),
    limit: int | None = Field(None, description="Maximum number of conversations to return per request. Must be between 1 and 1000; the API may return fewer items than requested even if more results are available."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of conversations (channels and direct messages) that the calling user has access to, with optional filtering by user membership, conversation type, and archive status."""

    # Construct request model with validation
    try:
        _request = _models.UsersConversationsRequest(
            query=_models.UsersConversationsRequestQuery(user=user, types=types, exclude_archived=exclude_archived, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_conversations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users.conversations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_conversations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_conversations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_conversations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def delete_user_photo() -> dict[str, Any] | ToolResult:
    """Remove the user's profile photo. Requires authentication with users.profile:write scope."""

    # Extract parameters for API call
    _http_path = "/users.deletePhoto"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_user_photo")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_user_photo", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_user_photo",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_user_presence(user: str | None = Field(None, description="The user whose presence information should be retrieved. If omitted, defaults to the authenticated user making the request.")) -> dict[str, Any] | ToolResult:
    """Retrieves the presence status of a user. If no user is specified, returns the presence information for the authenticated user."""

    # Construct request model with validation
    try:
        _request = _models.UsersGetPresenceRequest(
            query=_models.UsersGetPresenceRequestQuery(user=user)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_presence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users.getPresence"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_presence")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_presence", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_presence",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_user_info(
    include_locale: bool | None = Field(None, description="Set to `true` to include the user's locale in the response; defaults to `false` if omitted."),
    user: str | None = Field(None, description="The user identifier to retrieve information for. If omitted, returns information for the authenticated user."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific user, optionally including their locale preference."""

    # Construct request model with validation
    try:
        _request = _models.UsersInfoRequest(
            query=_models.UsersInfoRequestQuery(include_locale=include_locale, user=user)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_info: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users.info"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_info")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_info", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_info",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_users(
    limit: int | None = Field(None, description="Maximum number of users to return per request. Omitting this parameter attempts to return the entire user list, which may fail if the workspace is large; include a limit to ensure reliable pagination."),
    include_locale: bool | None = Field(None, description="Include the locale setting for each user in the response. Defaults to false; set to true only if locale information is needed, as it may increase response size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all users in a Slack workspace. Results can be paginated and optionally include user locale information."""

    # Construct request model with validation
    try:
        _request = _models.UsersListRequest(
            query=_models.UsersListRequestQuery(limit=limit, include_locale=include_locale)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users.list"
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

# Tags: users
@mcp.tool()
async def get_user_by_email(email: str = Field(..., description="The email address of the user to look up. Must be a valid email address associated with a user in the workspace.")) -> dict[str, Any] | ToolResult:
    """Retrieve a user account by their email address. Returns the user object if found in the workspace."""

    # Construct request model with validation
    try:
        _request = _models.UsersLookupByEmailRequest(
            query=_models.UsersLookupByEmailRequestQuery(email=email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_by_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users.lookupByEmail"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_by_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_by_email", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_by_email",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users.profile, users
@mcp.tool()
async def get_user_profile(
    include_labels: bool | None = Field(None, description="When enabled, includes human-readable labels for each identifier in custom profile fields, making the response more interpretable."),
    user: str | None = Field(None, description="The user identifier to retrieve profile information for. If omitted, returns the profile of the authenticated user making the request."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed profile information for a specified user or the authenticated user. Requires authentication with users.profile:read scope."""

    # Construct request model with validation
    try:
        _request = _models.UsersProfileGetRequest(
            query=_models.UsersProfileGetRequestQuery(include_labels=include_labels, user=user)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_profile: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users.profile.get"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_profile")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_profile", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_profile",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def update_user_presence(presence: str = Field(..., description="Presence status to set for the user. Must be either 'auto' for active presence or 'away' for away status.")) -> dict[str, Any] | ToolResult:
    """Manually set a user's presence status to either active (auto) or away. Requires authentication with users:write scope."""

    # Construct request model with validation
    try:
        _request = _models.UsersSetPresenceRequest(
            body=_models.UsersSetPresenceRequestBody(presence=presence)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user_presence: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users.setPresence"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user_presence")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user_presence", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user_presence",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def users_set_photo(
    crop_w: str | None = Field(None, description="Width/height of crop box (always square)"),
    crop_x: str | None = Field(None, description="X coordinate of top-left corner of crop box"),
    crop_y: str | None = Field(None, description="Y coordinate of top-left corner of crop box"),
    image: str | None = Field(None, description="Base64-encoded file content for upload. File contents via `multipart/form-data`.", json_schema_extra={'format': 'byte'}),
) -> dict[str, Any] | ToolResult:
    """Set the user profile photo"""

    # Construct request model with validation
    try:
        _request = _models.UsersSetPhotoRequest(
            body=_models.UsersSetPhotoRequestBody(crop_w=crop_w, crop_x=crop_x, crop_y=crop_y, image=image)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for users_set_photo: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users.setPhoto"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("users_set_photo")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("users_set_photo", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="users_set_photo",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["image"],
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
        print("  python slack_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Slack MCP Server")

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
    logger.info("Starting Slack MCP Server")
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

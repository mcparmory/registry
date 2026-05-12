#!/usr/bin/env python3
"""
Runpod MCP Server

API Info:
- Contact: help <help@runpod.io> (https://contact.runpod.io/hc/requests/new)

Generated: 2026-05-12 12:32:34 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://rest.runpod.io/v1")
SERVER_NAME = "Runpod"
SERVER_VERSION = "1.0.1"

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
    'ApiKey',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["ApiKey"] = _auth.BearerTokenAuth(env_var="BEARER_TOKEN", token_format="Bearer")
    logging.info("Authentication configured: ApiKey")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for ApiKey not configured: {error_msg}")
    _auth_handlers["ApiKey"] = None

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

mcp = FastMCP("Runpod", middleware=[_JsonCoercionMiddleware()])

# Tags: pods
@mcp.tool(
    title="List Pods",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_pods(
    compute_type: Literal["GPU", "CPU"] | None = Field(None, alias="computeType", description="Filter results to only GPU-based or CPU-based Pods."),
    cpu_flavor_id: list[str] | None = Field(None, alias="cpuFlavorId", description="Filter to CPU Pods matching any of the specified CPU flavor identifiers (e.g., cpu3c, cpu5g)."),
    data_center_id: list[str] | None = Field(None, alias="dataCenterId", description="Filter to Pods located in any of the specified RunPod data center regions (e.g., EU-RO-1)."),
    desired_status: Literal["RUNNING", "EXITED", "TERMINATED"] | None = Field(None, alias="desiredStatus", description="Filter to Pods currently in a specific operational state: RUNNING, EXITED, or TERMINATED."),
    endpoint_id: str | None = Field(None, alias="endpointId", description="Filter to worker Pods associated with a specific Serverless endpoint ID. Worker Pods are excluded from results by default unless includeWorkers is enabled.", max_length=191),
    gpu_type_id: list[str] | None = Field(None, alias="gpuTypeId", description="Filter to Pods with any of the specified GPU types attached (e.g., NVIDIA GeForce RTX 4090, NVIDIA RTX A5000)."),
    id_: str | None = Field(None, alias="id", description="Filter to a specific Pod by its unique identifier."),
    image_name: str | None = Field(None, alias="imageName", description="Filter to Pods created with a specific container image."),
    include_machine: bool | None = Field(None, alias="includeMachine", description="Include detailed information about the physical machine or node the Pod is running on."),
    include_network_volume: bool | None = Field(None, alias="includeNetworkVolume", description="Include detailed information about any network volume attached to the Pod."),
    include_savings_plans: bool | None = Field(None, alias="includeSavingsPlans", description="Include information about active savings plans or discounts applied to the Pod."),
    include_template: bool | None = Field(None, alias="includeTemplate", description="Include information about the Pod template used during creation, if applicable."),
    include_workers: bool | None = Field(None, alias="includeWorkers", description="Include Serverless worker Pods in the results. By default, only standard Pods are returned."),
    name: str | None = Field(None, description="Filter to Pods with a specific name.", max_length=191),
    template_id: str | None = Field(None, alias="templateId", description="Filter to Pods created from a specific template ID."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of Pods with optional filtering by compute type, hardware specifications, location, status, and other attributes. Supports inclusion of related metadata such as machine details, network volumes, savings plans, and templates."""

    # Construct request model with validation
    try:
        _request = _models.ListPodsRequest(
            query=_models.ListPodsRequestQuery(compute_type=compute_type, cpu_flavor_id=cpu_flavor_id, data_center_id=data_center_id, desired_status=desired_status, endpoint_id=endpoint_id, gpu_type_id=gpu_type_id, id_=id_, image_name=image_name, include_machine=include_machine, include_network_volume=include_network_volume, include_savings_plans=include_savings_plans, include_template=include_template, include_workers=include_workers, name=name, template_id=template_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pods: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/pods"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pods")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pods", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pods",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: pods
@mcp.tool(
    title="Create Pod",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_pod(
    cloud_type: Literal["SECURE", "COMMUNITY"] | None = Field(None, alias="cloudType", description="Cloud environment for the Pod. SECURE provides dedicated infrastructure with guaranteed availability; COMMUNITY offers lower-cost shared resources. Defaults to SECURE."),
    compute_type: Literal["GPU", "CPU"] | None = Field(None, alias="computeType", description="Compute type for the Pod. GPU Pods include graphics processors and ignore CPU-related settings; CPU Pods are GPU-less and ignore GPU-related settings. Defaults to GPU."),
    country_codes: list[str] | None = Field(None, alias="countryCodes", description="List of ISO 3166-1 alpha-2 country codes where the Pod can be located. If omitted, the Pod can be placed in any country."),
    cpu_flavor_ids: list[Literal["cpu3c", "cpu3g", "cpu3m", "cpu5c", "cpu5g", "cpu5m"]] | None = Field(None, alias="cpuFlavorIds", description="Ordered list of CPU flavor IDs for CPU Pods. The order determines rental priority; earlier entries are attempted first. Ignored for GPU Pods."),
    data_center_ids: list[Literal["EU-RO-1", "CA-MTL-1", "EU-SE-1", "US-IL-1", "EUR-IS-1", "EU-CZ-1", "US-TX-3", "EUR-IS-2", "US-KS-2", "US-GA-2", "US-WA-1", "US-TX-1", "CA-MTL-3", "EU-NL-1", "US-TX-4", "US-CA-2", "US-NC-1", "OC-AU-1", "US-DE-1", "EUR-IS-3", "CA-MTL-2", "AP-JP-1", "EUR-NO-1", "EU-FR-1", "US-KS-3", "US-GA-1"]] | None = Field(None, alias="dataCenterIds", description="Ordered list of data center IDs where the Pod can be located. The order determines rental priority; earlier entries are attempted first. Defaults to a global list of 26 data centers."),
    docker_entrypoint: list[str] | None = Field(None, alias="dockerEntrypoint", description="Docker ENTRYPOINT override for the container. Pass an empty array to use the image's default ENTRYPOINT. Defaults to empty array."),
    docker_start_cmd: list[str] | None = Field(None, alias="dockerStartCmd", description="Docker CMD override for the container startup. Pass an empty array to use the image's default CMD. Defaults to empty array."),
    env: dict[str, Any] | None = Field(None, description="Environment variables to inject into the Pod container as key-value pairs. Defaults to empty object."),
    global_networking: bool | None = Field(None, alias="globalNetworking", description="Enable global networking for the Pod. Currently available only for On-Demand GPU Pods on select Secure Cloud data centers. Defaults to false."),
    gpu_count: int | None = Field(None, alias="gpuCount", description="Number of GPUs to attach to the Pod. Only applies to GPU Pods. Must be at least 1. Defaults to 1.", ge=1),
    gpu_type_ids: list[Literal["NVIDIA GeForce RTX 4090", "NVIDIA A40", "NVIDIA RTX A5000", "NVIDIA GeForce RTX 5090", "NVIDIA H100 80GB HBM3", "NVIDIA GeForce RTX 3090", "NVIDIA RTX A4500", "NVIDIA L40S", "NVIDIA H200", "NVIDIA L4", "NVIDIA RTX 6000 Ada Generation", "NVIDIA A100-SXM4-80GB", "NVIDIA RTX 4000 Ada Generation", "NVIDIA RTX A6000", "NVIDIA A100 80GB PCIe", "NVIDIA RTX 2000 Ada Generation", "NVIDIA RTX A4000", "NVIDIA RTX PRO 6000 Blackwell Server Edition", "NVIDIA H100 PCIe", "NVIDIA H100 NVL", "NVIDIA L40", "NVIDIA B200", "NVIDIA GeForce RTX 3080 Ti", "NVIDIA RTX PRO 6000 Blackwell Workstation Edition", "NVIDIA GeForce RTX 3080", "NVIDIA GeForce RTX 3070", "AMD Instinct MI300X OAM", "NVIDIA GeForce RTX 4080 SUPER", "Tesla V100-PCIE-16GB", "Tesla V100-SXM2-32GB", "NVIDIA RTX 5000 Ada Generation", "NVIDIA GeForce RTX 4070 Ti", "NVIDIA RTX 4000 SFF Ada Generation", "NVIDIA GeForce RTX 3090 Ti", "NVIDIA RTX A2000", "NVIDIA GeForce RTX 4080", "NVIDIA A30", "NVIDIA GeForce RTX 5080", "Tesla V100-FHHL-16GB", "NVIDIA H200 NVL", "Tesla V100-SXM2-16GB", "NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition", "NVIDIA A5000 Ada", "Tesla V100-PCIE-32GB", "NVIDIA  RTX A4500", "NVIDIA  A30", "NVIDIA GeForce RTX 3080TI", "Tesla T4", "NVIDIA RTX A30"]] | None = Field(None, alias="gpuTypeIds", description="Ordered list of GPU type IDs for GPU Pods. The order determines rental priority; earlier entries are attempted first. Ignored for CPU Pods."),
    image_name: str | None = Field(None, alias="imageName", description="Container image tag to run on the Pod (e.g., runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04)."),
    interruptible: bool | None = Field(None, description="Create an interruptible (spot) Pod instead of reserved. Interruptible Pods cost less but can be stopped anytime to free resources. Defaults to false (reserved)."),
    locked: bool | None = Field(None, description="Lock the Pod to prevent stopping or resetting. Defaults to false (unlocked)."),
    min_disk_bandwidth_m_bps: float | None = Field(None, alias="minDiskBandwidthMBps", description="Minimum disk bandwidth in megabytes per second (MBps) required for the Pod."),
    min_download_mbps: float | None = Field(None, alias="minDownloadMbps", description="Minimum download speed in megabits per second (Mbps) required for the Pod."),
    min_ram_per_gpu: int | None = Field(None, alias="minRAMPerGPU", description="Minimum RAM in gigabytes (GB) per GPU for GPU Pods. Defaults to 8 GB per GPU."),
    min_upload_mbps: float | None = Field(None, alias="minUploadMbps", description="Minimum upload speed in megabits per second (Mbps) required for the Pod."),
    min_vcpu_per_gpu: int | None = Field(None, alias="minVCPUPerGPU", description="Minimum virtual CPUs per GPU for GPU Pods. Defaults to 2 vCPUs per GPU."),
    name: str | None = Field(None, description="User-defined name for the Pod. Does not need to be unique. Maximum 191 characters. Defaults to 'my pod'.", max_length=191),
    ports: list[str] | None = Field(None, description="List of exposed ports in format [port_number]/[protocol], where protocol is either 'http' or 'tcp' (e.g., ['8888/http', '22/tcp'])."),
    support_public_ip: bool | None = Field(None, alias="supportPublicIp", description="For Community Cloud Pods, set to true to request a public IP address. On Secure Cloud, Pods always have public IPs. Defaults to null (may not have public IP on Community Cloud)."),
    template_id: str | None = Field(None, alias="templateId", description="Unique identifier of a Pod template to use for creation. If provided, the Pod is created from this template."),
    vcpu_count: int | None = Field(None, alias="vcpuCount", description="Number of virtual CPUs to allocate to the Pod. Only applies to CPU Pods. Defaults to 2 vCPUs."),
) -> dict[str, Any] | ToolResult:
    """Create and optionally deploy a new Pod with configurable compute resources, networking, and deployment settings. Supports both GPU and CPU Pods across Secure Cloud and Community Cloud environments."""

    # Construct request model with validation
    try:
        _request = _models.CreatePodRequest(
            body=_models.CreatePodRequestBody(cloud_type=cloud_type, compute_type=compute_type, country_codes=country_codes, cpu_flavor_ids=cpu_flavor_ids, data_center_ids=data_center_ids, docker_entrypoint=docker_entrypoint, docker_start_cmd=docker_start_cmd, env=env, global_networking=global_networking, gpu_count=gpu_count, gpu_type_ids=gpu_type_ids, image_name=image_name, interruptible=interruptible, locked=locked, min_disk_bandwidth_m_bps=min_disk_bandwidth_m_bps, min_download_mbps=min_download_mbps, min_ram_per_gpu=min_ram_per_gpu, min_upload_mbps=min_upload_mbps, min_vcpu_per_gpu=min_vcpu_per_gpu, name=name, ports=ports, support_public_ip=support_public_ip, template_id=template_id, vcpu_count=vcpu_count)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_pod: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/pods"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_pod")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_pod", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_pod",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: pods
@mcp.tool(
    title="Get Pod",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_pod(
    pod_id: str = Field(..., alias="podId", description="The unique identifier of the Pod to retrieve."),
    include_machine: bool | None = Field(None, alias="includeMachine", description="When enabled, includes details about the machine the Pod is running on. Defaults to false."),
    include_network_volume: bool | None = Field(None, alias="includeNetworkVolume", description="When enabled, includes information about any network volume attached to the Pod. Defaults to false."),
    include_savings_plans: bool | None = Field(None, alias="includeSavingsPlans", description="When enabled, includes details about savings plans applied to the Pod. Defaults to false."),
    include_template: bool | None = Field(None, alias="includeTemplate", description="When enabled, includes information about the template used by the Pod, if one exists. Defaults to false."),
    include_workers: bool | None = Field(None, alias="includeWorkers", description="When enabled, includes Pods that are Serverless workers in the results. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a single Pod by its ID with optional related resource information. Use include parameters to expand the response with machine, network volume, savings plans, template, or worker details."""

    # Construct request model with validation
    try:
        _request = _models.GetPodRequest(
            path=_models.GetPodRequestPath(pod_id=pod_id),
            query=_models.GetPodRequestQuery(include_machine=include_machine, include_network_volume=include_network_volume, include_savings_plans=include_savings_plans, include_template=include_template, include_workers=include_workers)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pod: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/pods/{podId}", _request.path.model_dump(by_alias=True)) if _request.path else "/pods/{podId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pod")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pod", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pod",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: pods
@mcp.tool(
    title="Update Pod",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_pod(
    pod_id: str = Field(..., alias="podId", description="The unique identifier of the Pod to update."),
    docker_entrypoint: list[str] | None = Field(None, alias="dockerEntrypoint", description="Override the Docker image's ENTRYPOINT instruction. Provide as an array of command segments (e.g., ['python', '-m', 'server']). An empty array uses the image's default ENTRYPOINT."),
    docker_start_cmd: list[str] | None = Field(None, alias="dockerStartCmd", description="Override the Docker image's CMD instruction. Provide as an array of command segments (e.g., ['--port', '8080']). An empty array uses the image's default CMD."),
    env: dict[str, Any] | None = Field(None, description="Environment variables to set in the Pod runtime, provided as key-value pairs (e.g., {'ENV_VAR': 'value'})."),
    global_networking: bool | None = Field(None, alias="globalNetworking", description="Enable global networking for the Pod. Currently available only for On-Demand GPU Pods on select Secure Cloud data centers."),
    image_name: str | None = Field(None, alias="imageName", description="The container image tag to run on the Pod (e.g., 'runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04')."),
    locked: bool | None = Field(None, description="Lock the Pod to prevent stopping or resetting. Useful for protecting long-running workloads from accidental interruption."),
    name: str | None = Field(None, description="A user-defined name for the Pod. Names do not need to be unique and are limited to 191 characters.", max_length=191),
    ports: list[str] | None = Field(None, description="List of ports to expose on the Pod. Each port is specified as 'port_number/protocol' where protocol is either 'http' or 'tcp' (e.g., ['8888/http', '22/tcp'])."),
) -> dict[str, Any] | ToolResult:
    """Update Pod configuration settings such as Docker image, environment variables, networking, and port mappings. Changes may trigger a Pod reset depending on the parameters modified."""

    # Construct request model with validation
    try:
        _request = _models.UpdatePodRequest(
            path=_models.UpdatePodRequestPath(pod_id=pod_id),
            body=_models.UpdatePodRequestBody(docker_entrypoint=docker_entrypoint, docker_start_cmd=docker_start_cmd, env=env, global_networking=global_networking, image_name=image_name, locked=locked, name=name, ports=ports)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_pod: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/pods/{podId}", _request.path.model_dump(by_alias=True)) if _request.path else "/pods/{podId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_pod")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_pod", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_pod",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: pods
@mcp.tool(
    title="Delete Pod",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_pod(pod_id: str = Field(..., alias="podId", description="The unique identifier of the Pod to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a Pod by its ID. This operation removes the Pod and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeletePodRequest(
            path=_models.DeletePodRequestPath(pod_id=pod_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_pod: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/pods/{podId}", _request.path.model_dump(by_alias=True)) if _request.path else "/pods/{podId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_pod")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_pod", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_pod",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: pods
@mcp.tool(
    title="Update Pod",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_pod_request(
    pod_id: str = Field(..., alias="podId", description="The unique identifier of the Pod to update."),
    docker_entrypoint: list[str] | None = Field(None, alias="dockerEntrypoint", description="Override the Docker image's ENTRYPOINT instruction. Provide as an array of command arguments, or use an empty array to use the image's default ENTRYPOINT."),
    docker_start_cmd: list[str] | None = Field(None, alias="dockerStartCmd", description="Override the Docker image's CMD instruction. Provide as an array of command arguments, or use an empty array to use the image's default CMD."),
    env: dict[str, Any] | None = Field(None, description="Environment variables to set in the Pod container, provided as key-value pairs (e.g., {'ENV_VAR': 'value'})."),
    global_networking: bool | None = Field(None, alias="globalNetworking", description="Enable global networking for the Pod. Currently supported only for On-Demand GPU Pods on select Secure Cloud data centers."),
    image_name: str | None = Field(None, alias="imageName", description="The container image tag to run on the Pod (e.g., 'runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04')."),
    locked: bool | None = Field(None, description="Lock the Pod to prevent stopping or resetting. Useful for protecting long-running workloads from accidental interruption."),
    name: str | None = Field(None, description="A user-defined name for the Pod. Names do not need to be unique and are limited to 191 characters.", max_length=191),
    ports: list[str] | None = Field(None, description="List of ports to expose on the Pod. Each port is specified as 'port_number/protocol' where protocol is either 'http' or 'tcp' (e.g., ['8888/http', '22/tcp'])."),
) -> dict[str, Any] | ToolResult:
    """Update configuration settings for an existing Pod, including container image, environment variables, networking, and exposed ports."""

    # Construct request model with validation
    try:
        _request = _models.UpdatePod2Request(
            path=_models.UpdatePod2RequestPath(pod_id=pod_id),
            body=_models.UpdatePod2RequestBody(docker_entrypoint=docker_entrypoint, docker_start_cmd=docker_start_cmd, env=env, global_networking=global_networking, image_name=image_name, locked=locked, name=name, ports=ports)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_pod_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/pods/{podId}/update", _request.path.model_dump(by_alias=True)) if _request.path else "/pods/{podId}/update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_pod_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_pod_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_pod_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: pods
@mcp.tool(
    title="Start Pod",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def start_pod(pod_id: str = Field(..., alias="podId", description="The unique identifier of the Pod to start or resume.")) -> dict[str, Any] | ToolResult:
    """Start or resume a Pod that is currently stopped or paused. This operation transitions the Pod to a running state."""

    # Construct request model with validation
    try:
        _request = _models.StartPodRequest(
            path=_models.StartPodRequestPath(pod_id=pod_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for start_pod: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/pods/{podId}/start", _request.path.model_dump(by_alias=True)) if _request.path else "/pods/{podId}/start"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("start_pod")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("start_pod", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="start_pod",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: pods
@mcp.tool(
    title="Stop Pod",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def stop_pod(pod_id: str = Field(..., alias="podId", description="The unique identifier of the Pod to stop.")) -> dict[str, Any] | ToolResult:
    """Stop a running Pod, halting its execution and resources. This operation gracefully terminates the Pod identified by the provided ID."""

    # Construct request model with validation
    try:
        _request = _models.StopPodRequest(
            path=_models.StopPodRequestPath(pod_id=pod_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for stop_pod: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/pods/{podId}/stop", _request.path.model_dump(by_alias=True)) if _request.path else "/pods/{podId}/stop"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("stop_pod")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("stop_pod", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="stop_pod",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: pods
@mcp.tool(
    title="Reset Pod",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def reset_pod(pod_id: str = Field(..., alias="podId", description="The unique identifier of the Pod to reset.")) -> dict[str, Any] | ToolResult:
    """Reset a Pod to its initial state, clearing any runtime state or configuration changes. This operation restarts the Pod and restores it to a clean state."""

    # Construct request model with validation
    try:
        _request = _models.ResetPodRequest(
            path=_models.ResetPodRequestPath(pod_id=pod_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reset_pod: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/pods/{podId}/reset", _request.path.model_dump(by_alias=True)) if _request.path else "/pods/{podId}/reset"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reset_pod")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reset_pod", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reset_pod",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: pods
@mcp.tool(
    title="Restart Pod",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def restart_pod(pod_id: str = Field(..., alias="podId", description="The unique identifier of the Pod to restart.")) -> dict[str, Any] | ToolResult:
    """Restart a running Pod, causing it to stop and start again. This operation is useful for refreshing a Pod's state or recovering from transient issues."""

    # Construct request model with validation
    try:
        _request = _models.RestartPodRequest(
            path=_models.RestartPodRequestPath(pod_id=pod_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for restart_pod: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/pods/{podId}/restart", _request.path.model_dump(by_alias=True)) if _request.path else "/pods/{podId}/restart"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("restart_pod")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("restart_pod", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="restart_pod",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: endpoints
@mcp.tool(
    title="List Endpoints",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_endpoints(
    include_template: bool | None = Field(None, alias="includeTemplate", description="When enabled, includes template information for each endpoint. Defaults to false."),
    include_workers: bool | None = Field(None, alias="includeWorkers", description="When enabled, includes details about workers currently running on each endpoint. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of all available endpoints. Optionally include details about the templates used to create endpoints and the workers currently running on them."""

    # Construct request model with validation
    try:
        _request = _models.ListEndpointsRequest(
            query=_models.ListEndpointsRequestQuery(include_template=include_template, include_workers=include_workers)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_endpoints: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/endpoints"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_endpoints")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_endpoints", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_endpoints",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: endpoints
@mcp.tool(
    title="Create Serverless Endpoint",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_serverless_endpoint(
    template_id: str = Field(..., alias="templateId", description="Unique identifier of the template defining the container image and runtime configuration for workers."),
    compute_type: Literal["GPU", "CPU"] | None = Field(None, alias="computeType", description="Compute resource type for workers: GPU for GPU-accelerated inference, or CPU for CPU-only workloads. GPU-related properties are ignored for CPU endpoints and vice versa. Defaults to GPU."),
    cpu_flavor_ids: list[Literal["cpu3c", "cpu3g", "cpu5c", "cpu5g"]] | None = Field(None, alias="cpuFlavorIds", description="List of RunPod CPU flavor IDs available for CPU endpoints. Order determines rental preference priority when scaling workers."),
    data_center_ids: list[Literal["EU-RO-1", "CA-MTL-1", "EU-SE-1", "US-IL-1", "EUR-IS-1", "EU-CZ-1", "US-TX-3", "EUR-IS-2", "US-KS-2", "US-GA-2", "US-WA-1", "US-TX-1", "CA-MTL-3", "EU-NL-1", "US-TX-4", "US-CA-2", "US-NC-1", "OC-AU-1", "US-DE-1", "EUR-IS-3", "CA-MTL-2", "AP-JP-1", "EUR-NO-1", "EU-FR-1", "US-KS-3", "US-GA-1"]] | None = Field(None, alias="dataCenterIds", description="List of RunPod data center IDs where workers can be deployed. Order determines preference priority. Defaults to all available global data centers."),
    gpu_count: int | None = Field(None, alias="gpuCount", description="Number of GPUs per worker for GPU endpoints. Must be at least 1. Defaults to 1.", ge=1),
    gpu_type_ids: list[Literal["NVIDIA GeForce RTX 4090", "NVIDIA A40", "NVIDIA RTX A5000", "NVIDIA GeForce RTX 5090", "NVIDIA H100 80GB HBM3", "NVIDIA GeForce RTX 3090", "NVIDIA RTX A4500", "NVIDIA L40S", "NVIDIA H200", "NVIDIA L4", "NVIDIA RTX 6000 Ada Generation", "NVIDIA A100-SXM4-80GB", "NVIDIA RTX 4000 Ada Generation", "NVIDIA RTX A6000", "NVIDIA A100 80GB PCIe", "NVIDIA RTX 2000 Ada Generation", "NVIDIA RTX A4000", "NVIDIA RTX PRO 6000 Blackwell Server Edition", "NVIDIA H100 PCIe", "NVIDIA H100 NVL", "NVIDIA L40", "NVIDIA B200", "NVIDIA GeForce RTX 3080 Ti", "NVIDIA RTX PRO 6000 Blackwell Workstation Edition", "NVIDIA GeForce RTX 3080", "NVIDIA GeForce RTX 3070", "AMD Instinct MI300X OAM", "NVIDIA GeForce RTX 4080 SUPER", "Tesla V100-PCIE-16GB", "Tesla V100-SXM2-32GB", "NVIDIA RTX 5000 Ada Generation", "NVIDIA GeForce RTX 4070 Ti", "NVIDIA RTX 4000 SFF Ada Generation", "NVIDIA GeForce RTX 3090 Ti", "NVIDIA RTX A2000", "NVIDIA GeForce RTX 4080", "NVIDIA A30", "NVIDIA GeForce RTX 5080", "Tesla V100-FHHL-16GB", "NVIDIA H200 NVL", "Tesla V100-SXM2-16GB", "NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition", "NVIDIA A5000 Ada", "Tesla V100-PCIE-32GB", "NVIDIA  RTX A4500", "NVIDIA  A30", "NVIDIA GeForce RTX 3080TI", "Tesla T4", "NVIDIA RTX A30"]] | None = Field(None, alias="gpuTypeIds", description="List of RunPod GPU type IDs available for GPU endpoints. Order determines rental preference priority when scaling workers."),
    name: str | None = Field(None, description="User-defined name for the endpoint. Does not need to be unique. Maximum 191 characters.", max_length=191),
    network_volume_ids: list[str] | None = Field(None, alias="networkVolumeIds", description="List of network volume IDs to attach to the endpoint. Enables multi-region endpoints to access shared storage across data centers."),
    scaler_type: Literal["QUEUE_DELAY", "REQUEST_COUNT"] | None = Field(None, alias="scalerType", description="Scaling strategy: QUEUE_DELAY scales workers when requests exceed maximum latency tolerance, REQUEST_COUNT scales based on request queue depth. Defaults to QUEUE_DELAY."),
    scaler_value: int | None = Field(None, alias="scalerValue", description="Scaling threshold: for QUEUE_DELAY, maximum seconds a request waits before scaling up; for REQUEST_COUNT, requests per worker ratio. Must be at least 1. Defaults to 4.", ge=1),
    vcpu_count: int | None = Field(None, alias="vcpuCount", description="Number of vCPUs allocated per worker for CPU endpoints. Defaults to 2."),
    workers_max: int | None = Field(None, alias="workersMax", description="Maximum number of concurrent workers. Must be 0 or greater. Set to 0 for unlimited scaling.", ge=0),
    workers_min: int | None = Field(None, alias="workersMin", description="Minimum number of always-running workers. Must be 0 or greater. These workers run continuously at reduced cost even with no active requests.", ge=0),
) -> dict[str, Any] | ToolResult:
    """Create a new Serverless endpoint for running containerized workloads. Configure compute resources (GPU or CPU), scaling behavior, worker limits, and data center preferences to match your inference workload requirements."""

    # Construct request model with validation
    try:
        _request = _models.CreateEndpointRequest(
            body=_models.CreateEndpointRequestBody(compute_type=compute_type, cpu_flavor_ids=cpu_flavor_ids, data_center_ids=data_center_ids, gpu_count=gpu_count, gpu_type_ids=gpu_type_ids, name=name, network_volume_ids=network_volume_ids, scaler_type=scaler_type, scaler_value=scaler_value, template_id=template_id, vcpu_count=vcpu_count, workers_max=workers_max, workers_min=workers_min)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_serverless_endpoint: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/endpoints"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_serverless_endpoint")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_serverless_endpoint", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_serverless_endpoint",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: endpoints
@mcp.tool(
    title="Get Endpoint",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_endpoint(
    endpoint_id: str = Field(..., alias="endpointId", description="The unique identifier of the endpoint to retrieve."),
    include_template: bool | None = Field(None, alias="includeTemplate", description="When enabled, includes detailed information about the template that was used to create this endpoint. Defaults to false."),
    include_workers: bool | None = Field(None, alias="includeWorkers", description="When enabled, includes information about all workers currently running on this endpoint. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a single endpoint by its ID. Optionally include details about the template used to create it and the workers currently running on it."""

    # Construct request model with validation
    try:
        _request = _models.GetEndpointRequest(
            path=_models.GetEndpointRequestPath(endpoint_id=endpoint_id),
            query=_models.GetEndpointRequestQuery(include_template=include_template, include_workers=include_workers)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_endpoint: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/endpoints/{endpointId}", _request.path.model_dump(by_alias=True)) if _request.path else "/endpoints/{endpointId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_endpoint")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_endpoint", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_endpoint",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: endpoints
@mcp.tool(
    title="Update Endpoint",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_endpoint(
    endpoint_id: str = Field(..., alias="endpointId", description="The unique identifier of the endpoint to update."),
    cpu_flavor_ids: list[Literal["cpu3c", "cpu3g", "cpu5c", "cpu5g"]] | None = Field(None, alias="cpuFlavorIds", description="For CPU endpoints, an ordered list of RunPod CPU flavor IDs to attach to workers. The list order determines rental priority."),
    data_center_ids: list[Literal["EU-RO-1", "CA-MTL-1", "EU-SE-1", "US-IL-1", "EUR-IS-1", "EU-CZ-1", "US-TX-3", "EUR-IS-2", "US-KS-2", "US-GA-2", "US-WA-1", "US-TX-1", "CA-MTL-3", "EU-NL-1", "US-TX-4", "US-CA-2", "US-NC-1", "OC-AU-1", "US-DE-1", "EUR-IS-3", "CA-MTL-2", "AP-JP-1", "EUR-NO-1", "EU-FR-1", "US-KS-3", "US-GA-1"]] | None = Field(None, alias="dataCenterIds", description="An ordered list of RunPod data center IDs where workers can be deployed. Defaults to all available global data centers if not specified."),
    gpu_count: int | None = Field(None, alias="gpuCount", description="For GPU endpoints, the number of GPUs to attach to each worker. Must be at least 1.", ge=1),
    gpu_type_ids: list[Literal["NVIDIA GeForce RTX 4090", "NVIDIA A40", "NVIDIA RTX A5000", "NVIDIA GeForce RTX 5090", "NVIDIA H100 80GB HBM3", "NVIDIA GeForce RTX 3090", "NVIDIA RTX A4500", "NVIDIA L40S", "NVIDIA H200", "NVIDIA L4", "NVIDIA RTX 6000 Ada Generation", "NVIDIA A100-SXM4-80GB", "NVIDIA RTX 4000 Ada Generation", "NVIDIA RTX A6000", "NVIDIA A100 80GB PCIe", "NVIDIA RTX 2000 Ada Generation", "NVIDIA RTX A4000", "NVIDIA RTX PRO 6000 Blackwell Server Edition", "NVIDIA H100 PCIe", "NVIDIA H100 NVL", "NVIDIA L40", "NVIDIA B200", "NVIDIA GeForce RTX 3080 Ti", "NVIDIA RTX PRO 6000 Blackwell Workstation Edition", "NVIDIA GeForce RTX 3080", "NVIDIA GeForce RTX 3070", "AMD Instinct MI300X OAM", "NVIDIA GeForce RTX 4080 SUPER", "Tesla V100-PCIE-16GB", "Tesla V100-SXM2-32GB", "NVIDIA RTX 5000 Ada Generation", "NVIDIA GeForce RTX 4070 Ti", "NVIDIA RTX 4000 SFF Ada Generation", "NVIDIA GeForce RTX 3090 Ti", "NVIDIA RTX A2000", "NVIDIA GeForce RTX 4080", "NVIDIA A30", "NVIDIA GeForce RTX 5080", "Tesla V100-FHHL-16GB", "NVIDIA H200 NVL", "Tesla V100-SXM2-16GB", "NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition", "NVIDIA A5000 Ada", "Tesla V100-PCIE-32GB", "NVIDIA  RTX A4500", "NVIDIA  A30", "NVIDIA GeForce RTX 3080TI", "Tesla T4", "NVIDIA RTX A30"]] | None = Field(None, alias="gpuTypeIds", description="For GPU endpoints, an ordered list of RunPod GPU type IDs to attach to workers. The list order determines rental priority."),
    name: str | None = Field(None, description="A user-friendly name for the endpoint. Names do not need to be unique and can be up to 191 characters.", max_length=191),
    network_volume_ids: list[str] | None = Field(None, alias="networkVolumeIds", description="A list of network volume IDs to attach to the endpoint, enabling multi-region storage access."),
    scaler_type: Literal["QUEUE_DELAY", "REQUEST_COUNT"] | None = Field(None, alias="scalerType", description="The autoscaling strategy: QUEUE_DELAY scales workers when requests exceed a latency threshold, while REQUEST_COUNT scales based on queue depth divided by a target ratio."),
    scaler_value: int | None = Field(None, alias="scalerValue", description="For QUEUE_DELAY scaling, the maximum seconds a request can wait before triggering a new worker. For REQUEST_COUNT scaling, the target number of requests per worker. Must be at least 1.", ge=1),
    template_id: str | None = Field(None, alias="templateId", description="The template ID used to configure the endpoint's runtime environment and dependencies."),
    vcpu_count: int | None = Field(None, alias="vcpuCount", description="For CPU endpoints, the number of vCPUs allocated to each worker. Defaults to 2."),
    workers_max: int | None = Field(None, alias="workersMax", description="The maximum number of workers that can run simultaneously. Must be 0 or greater.", ge=0),
    workers_min: int | None = Field(None, alias="workersMin", description="The minimum number of workers that always run, even with no active requests. These are charged at a lower rate. Must be 0 or greater.", ge=0),
) -> dict[str, Any] | ToolResult:
    """Modify configuration settings for a Serverless endpoint, including scaling behavior, resource allocation, worker limits, and attached volumes."""

    # Construct request model with validation
    try:
        _request = _models.UpdateEndpointRequest(
            path=_models.UpdateEndpointRequestPath(endpoint_id=endpoint_id),
            body=_models.UpdateEndpointRequestBody(cpu_flavor_ids=cpu_flavor_ids, data_center_ids=data_center_ids, gpu_count=gpu_count, gpu_type_ids=gpu_type_ids, name=name, network_volume_ids=network_volume_ids, scaler_type=scaler_type, scaler_value=scaler_value, template_id=template_id, vcpu_count=vcpu_count, workers_max=workers_max, workers_min=workers_min)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_endpoint: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/endpoints/{endpointId}", _request.path.model_dump(by_alias=True)) if _request.path else "/endpoints/{endpointId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_endpoint")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_endpoint", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_endpoint",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: endpoints
@mcp.tool(
    title="Delete Endpoint",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_endpoint(endpoint_id: str = Field(..., alias="endpointId", description="The unique identifier of the endpoint to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete an endpoint by its ID. This action cannot be undone and will remove the endpoint from the system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteEndpointRequest(
            path=_models.DeleteEndpointRequestPath(endpoint_id=endpoint_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_endpoint: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/endpoints/{endpointId}", _request.path.model_dump(by_alias=True)) if _request.path else "/endpoints/{endpointId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_endpoint")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_endpoint", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_endpoint",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: endpoints
@mcp.tool(
    title="Update Endpoint",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_endpoint_async(
    endpoint_id: str = Field(..., alias="endpointId", description="The unique identifier of the endpoint to update."),
    cpu_flavor_ids: list[Literal["cpu3c", "cpu3g", "cpu5c", "cpu5g"]] | None = Field(None, alias="cpuFlavorIds", description="For CPU endpoints, an ordered list of RunPod CPU flavor IDs available for worker allocation. Earlier flavors in the list are prioritized for rental."),
    data_center_ids: list[Literal["EU-RO-1", "CA-MTL-1", "EU-SE-1", "US-IL-1", "EUR-IS-1", "EU-CZ-1", "US-TX-3", "EUR-IS-2", "US-KS-2", "US-GA-2", "US-WA-1", "US-TX-1", "CA-MTL-3", "EU-NL-1", "US-TX-4", "US-CA-2", "US-NC-1", "OC-AU-1", "US-DE-1", "EUR-IS-3", "CA-MTL-2", "AP-JP-1", "EUR-NO-1", "EU-FR-1", "US-KS-3", "US-GA-1"]] | None = Field(None, alias="dataCenterIds", description="An ordered list of RunPod data center IDs where workers can be deployed. Earlier data centers are prioritized. Defaults to a global set of 26 data centers across multiple regions."),
    gpu_count: int | None = Field(None, alias="gpuCount", description="For GPU endpoints, the number of GPUs to attach to each worker. Must be at least 1. Defaults to 1 GPU per worker.", ge=1),
    gpu_type_ids: list[Literal["NVIDIA GeForce RTX 4090", "NVIDIA A40", "NVIDIA RTX A5000", "NVIDIA GeForce RTX 5090", "NVIDIA H100 80GB HBM3", "NVIDIA GeForce RTX 3090", "NVIDIA RTX A4500", "NVIDIA L40S", "NVIDIA H200", "NVIDIA L4", "NVIDIA RTX 6000 Ada Generation", "NVIDIA A100-SXM4-80GB", "NVIDIA RTX 4000 Ada Generation", "NVIDIA RTX A6000", "NVIDIA A100 80GB PCIe", "NVIDIA RTX 2000 Ada Generation", "NVIDIA RTX A4000", "NVIDIA RTX PRO 6000 Blackwell Server Edition", "NVIDIA H100 PCIe", "NVIDIA H100 NVL", "NVIDIA L40", "NVIDIA B200", "NVIDIA GeForce RTX 3080 Ti", "NVIDIA RTX PRO 6000 Blackwell Workstation Edition", "NVIDIA GeForce RTX 3080", "NVIDIA GeForce RTX 3070", "AMD Instinct MI300X OAM", "NVIDIA GeForce RTX 4080 SUPER", "Tesla V100-PCIE-16GB", "Tesla V100-SXM2-32GB", "NVIDIA RTX 5000 Ada Generation", "NVIDIA GeForce RTX 4070 Ti", "NVIDIA RTX 4000 SFF Ada Generation", "NVIDIA GeForce RTX 3090 Ti", "NVIDIA RTX A2000", "NVIDIA GeForce RTX 4080", "NVIDIA A30", "NVIDIA GeForce RTX 5080", "Tesla V100-FHHL-16GB", "NVIDIA H200 NVL", "Tesla V100-SXM2-16GB", "NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition", "NVIDIA A5000 Ada", "Tesla V100-PCIE-32GB", "NVIDIA  RTX A4500", "NVIDIA  A30", "NVIDIA GeForce RTX 3080TI", "Tesla T4", "NVIDIA RTX A30"]] | None = Field(None, alias="gpuTypeIds", description="For GPU endpoints, an ordered list of RunPod GPU type IDs available for worker allocation. Earlier types in the list are prioritized for rental."),
    name: str | None = Field(None, description="A user-friendly name for the endpoint. Names do not need to be unique and can be up to 191 characters.", max_length=191),
    network_volume_ids: list[str] | None = Field(None, alias="networkVolumeIds", description="A list of network volume IDs to attach to the endpoint. Supports multiple volumes for multi-region deployments."),
    scaler_type: Literal["QUEUE_DELAY", "REQUEST_COUNT"] | None = Field(None, alias="scalerType", description="The autoscaling strategy: QUEUE_DELAY scales workers when requests exceed a latency threshold, while REQUEST_COUNT scales based on queue depth divided by a target ratio. Defaults to QUEUE_DELAY."),
    scaler_value: int | None = Field(None, alias="scalerValue", description="For QUEUE_DELAY scaling, the maximum seconds a request can wait before triggering a new worker. For REQUEST_COUNT scaling, the target number of requests per worker. Must be at least 1. Defaults to 4.", ge=1),
    template_id: str | None = Field(None, alias="templateId", description="The template ID used to configure the endpoint's runtime environment and dependencies."),
    vcpu_count: int | None = Field(None, alias="vcpuCount", description="For CPU endpoints, the number of vCPUs allocated to each worker. Defaults to 2 vCPUs per worker."),
    workers_max: int | None = Field(None, alias="workersMax", description="The maximum number of workers that can run simultaneously. Must be 0 or greater. Set to 0 for unlimited scaling.", ge=0),
    workers_min: int | None = Field(None, alias="workersMin", description="The minimum number of workers that always run, even with no active requests. These workers are charged at a lower rate. Must be 0 or greater.", ge=0),
) -> dict[str, Any] | ToolResult:
    """Update configuration for a Serverless endpoint, including scaling behavior, resource allocation, and deployment settings. Changes apply to all future workers spawned on this endpoint."""

    # Construct request model with validation
    try:
        _request = _models.UpdateEndpoint2Request(
            path=_models.UpdateEndpoint2RequestPath(endpoint_id=endpoint_id),
            body=_models.UpdateEndpoint2RequestBody(cpu_flavor_ids=cpu_flavor_ids, data_center_ids=data_center_ids, gpu_count=gpu_count, gpu_type_ids=gpu_type_ids, name=name, network_volume_ids=network_volume_ids, scaler_type=scaler_type, scaler_value=scaler_value, template_id=template_id, vcpu_count=vcpu_count, workers_max=workers_max, workers_min=workers_min)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_endpoint_async: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/endpoints/{endpointId}/update", _request.path.model_dump(by_alias=True)) if _request.path else "/endpoints/{endpointId}/update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_endpoint_async")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_endpoint_async", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_endpoint_async",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: templates
@mcp.tool(
    title="List Templates",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_templates(
    include_endpoint_bound_templates: bool | None = Field(None, alias="includeEndpointBoundTemplates", description="Include templates that are bound to Serverless endpoints in the response. Disabled by default."),
    include_public_templates: bool | None = Field(None, alias="includePublicTemplates", description="Include community-made public templates in the response. Disabled by default."),
    include_runpod_templates: bool | None = Field(None, alias="includeRunpodTemplates", description="Include official Runpod templates in the response. Disabled by default."),
) -> dict[str, Any] | ToolResult:
    """Retrieve available templates with optional filtering to include endpoint-bound, community, and official Runpod templates. By default, returns only your personal templates."""

    # Construct request model with validation
    try:
        _request = _models.ListTemplatesRequest(
            query=_models.ListTemplatesRequestQuery(include_endpoint_bound_templates=include_endpoint_bound_templates, include_public_templates=include_public_templates, include_runpod_templates=include_runpod_templates)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/templates"
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

# Tags: templates
@mcp.tool(
    title="Create Template",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_template(
    image_name: str = Field(..., alias="imageName", description="The Docker image to use for this template, specified as a registry path (e.g., 'nvidia/cuda:12.0' or 'myregistry.com/myimage:latest'). Required."),
    name: str = Field(..., description="A human-readable name for this template. Used for identification in the RunPod UI and API. Required."),
    category: Literal["NVIDIA", "AMD", "CPU"] | None = Field(None, description="The compute hardware category for this template. Choose NVIDIA for GPU acceleration, AMD for AMD GPUs, or CPU for CPU-only workloads. Defaults to NVIDIA."),
    docker_entrypoint: list[str] | None = Field(None, alias="dockerEntrypoint", description="Override the Docker image's ENTRYPOINT instruction. Provide as an array of command segments (e.g., ['/bin/bash', '-c']). Leave empty to use the image's default ENTRYPOINT."),
    docker_start_cmd: list[str] | None = Field(None, alias="dockerStartCmd", description="Override the Docker image's CMD instruction. Provide as an array of command segments. Leave empty to use the image's default CMD."),
    env: dict[str, Any] | None = Field(None, description="Environment variables to inject into the container at runtime. Provide as key-value pairs (e.g., {'ENV_VAR': 'value'})."),
    is_public: bool | None = Field(None, alias="isPublic", description="Make this template visible to other RunPod users. Only applies to Pod templates. Defaults to private (false)."),
    is_serverless: bool | None = Field(None, alias="isServerless", description="Specify whether this template is for a Serverless worker (true) or a standard Pod (false). Defaults to Pod (false)."),
    ports: list[str] | None = Field(None, description="List of network ports to expose on the Pod. Each port is specified as 'port_number/protocol' where protocol is either 'http' or 'tcp' (e.g., ['8888/http', '22/tcp'])."),
    readme: str | None = Field(None, description="Documentation for this template in Markdown format. Displayed to users who select this template. Defaults to empty."),
) -> dict[str, Any] | ToolResult:
    """Create a new Docker-based template for RunPod Pods or Serverless workers. Templates define the compute environment, Docker image, runtime configuration, and exposed ports for containerized workloads."""

    # Construct request model with validation
    try:
        _request = _models.CreateTemplateRequest(
            body=_models.CreateTemplateRequestBody(category=category, docker_entrypoint=docker_entrypoint, docker_start_cmd=docker_start_cmd, env=env, image_name=image_name, is_public=is_public, is_serverless=is_serverless, name=name, ports=ports, readme=readme)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/templates"
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

# Tags: templates
@mcp.tool(
    title="Get Template",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_template(
    template_id: str = Field(..., alias="templateId", description="The unique identifier of the template to retrieve."),
    include_endpoint_bound_templates: bool | None = Field(None, alias="includeEndpointBoundTemplates", description="Whether to include templates that are bound to Serverless endpoints in the response. Defaults to false."),
    include_public_templates: bool | None = Field(None, alias="includePublicTemplates", description="Whether to include community-made public templates in the response. Defaults to false."),
    include_runpod_templates: bool | None = Field(None, alias="includeRunpodTemplates", description="Whether to include official Runpod templates in the response. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a single template by its ID. Optionally include templates from Serverless endpoints, community-made public templates, or official Runpod templates in the response."""

    # Construct request model with validation
    try:
        _request = _models.GetTemplateRequest(
            path=_models.GetTemplateRequestPath(template_id=template_id),
            query=_models.GetTemplateRequestQuery(include_endpoint_bound_templates=include_endpoint_bound_templates, include_public_templates=include_public_templates, include_runpod_templates=include_runpod_templates)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/templates/{templateId}", _request.path.model_dump(by_alias=True)) if _request.path else "/templates/{templateId}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: templates
@mcp.tool(
    title="Update Template",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_template(
    template_id: str = Field(..., alias="templateId", description="The unique identifier of the template to update."),
    docker_entrypoint: list[str] | None = Field(None, alias="dockerEntrypoint", description="Override the Docker image's ENTRYPOINT instruction. Provide as an array of command segments (e.g., ['python', '-m', 'server']). Leave empty to use the ENTRYPOINT defined in the Dockerfile."),
    docker_start_cmd: list[str] | None = Field(None, alias="dockerStartCmd", description="Override the Docker image's start command (CMD instruction). Provide as an array of command segments. Leave empty to use the CMD defined in the Dockerfile."),
    env: dict[str, Any] | None = Field(None, description="Environment variables to inject into Pods created from this template, specified as key-value pairs (e.g., ENV_VAR: value)."),
    image_name: str | None = Field(None, alias="imageName", description="The Docker image name and optional tag to use for Pods created from this template (e.g., 'myregistry/myimage:latest')."),
    is_public: bool | None = Field(None, alias="isPublic", description="If true, makes this Pod template visible to other Runpod users. If false, the template is private to your account."),
    name: str | None = Field(None, description="A human-readable name for the template."),
    ports: list[str] | None = Field(None, description="List of network ports to expose on Pods created from this template. Each port is specified as 'port_number/protocol' where protocol is either 'http' or 'tcp' (e.g., '8888/http', '22/tcp')."),
    readme: str | None = Field(None, description="Template documentation in Markdown format, displayed to users when viewing or selecting this template."),
) -> dict[str, Any] | ToolResult:
    """Update an existing template's configuration, including Docker image settings, environment variables, exposed ports, and metadata. Changes apply to all Pods created from this template going forward."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTemplateRequest(
            path=_models.UpdateTemplateRequestPath(template_id=template_id),
            body=_models.UpdateTemplateRequestBody(docker_entrypoint=docker_entrypoint, docker_start_cmd=docker_start_cmd, env=env, image_name=image_name, is_public=is_public, name=name, ports=ports, readme=readme)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/templates/{templateId}", _request.path.model_dump(by_alias=True)) if _request.path else "/templates/{templateId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_template", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_template",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: templates
@mcp.tool(
    title="Delete Template",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_template(template_id: str = Field(..., alias="templateId", description="The unique identifier of the template to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a template by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTemplateRequest(
            path=_models.DeleteTemplateRequestPath(template_id=template_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/templates/{templateId}", _request.path.model_dump(by_alias=True)) if _request.path else "/templates/{templateId}"
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

# Tags: templates
@mcp.tool(
    title="Update Template Alternate",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_template_alternate(
    template_id: str = Field(..., alias="templateId", description="The unique identifier of the template to update."),
    docker_entrypoint: list[str] | None = Field(None, alias="dockerEntrypoint", description="Docker ENTRYPOINT override for Pods using this template. Provide as an array of command segments; pass an empty array to use the ENTRYPOINT defined in the Dockerfile."),
    docker_start_cmd: list[str] | None = Field(None, alias="dockerStartCmd", description="Docker CMD override for Pods using this template. Provide as an array of command segments; pass an empty array to use the CMD defined in the Dockerfile."),
    env: dict[str, Any] | None = Field(None, description="Environment variables to inject into Pods using this template, specified as key-value pairs (e.g., ENV_VAR: value)."),
    image_name: str | None = Field(None, alias="imageName", description="The Docker image name and tag to use for Pods created from this template."),
    is_public: bool | None = Field(None, alias="isPublic", description="Whether this Pod template is visible to other Runpod users. Defaults to private (not visible)."),
    name: str | None = Field(None, description="A human-readable name for the template."),
    ports: list[str] | None = Field(None, description="Network ports exposed by Pods using this template. Each port is specified as [port_number]/[protocol], where protocol is either 'http' or 'tcp'."),
    readme: str | None = Field(None, description="Template documentation in Markdown format, displayed to users viewing or using this template."),
) -> dict[str, Any] | ToolResult:
    """Update an existing Pod template's configuration, including Docker image settings, environment variables, exposed ports, and metadata. Changes apply to all Pods created from this template going forward."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTemplate2Request(
            path=_models.UpdateTemplate2RequestPath(template_id=template_id),
            body=_models.UpdateTemplate2RequestBody(docker_entrypoint=docker_entrypoint, docker_start_cmd=docker_start_cmd, env=env, image_name=image_name, is_public=is_public, name=name, ports=ports, readme=readme)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_template_alternate: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/templates/{templateId}/update", _request.path.model_dump(by_alias=True)) if _request.path else "/templates/{templateId}/update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_template_alternate")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_template_alternate", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_template_alternate",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: network volumes
@mcp.tool(
    title="List Network Volumes",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_network_volumes() -> dict[str, Any] | ToolResult:
    """Retrieves a list of all network volumes available in the system. Use this operation to discover and enumerate network storage resources."""

    # Extract parameters for API call
    _http_path = "/networkvolumes"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_network_volumes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_network_volumes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_network_volumes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: network volumes
@mcp.tool(
    title="Create Network Volume",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_network_volume(
    data_center_id: str = Field(..., alias="dataCenterId", description="The Runpod data center where the network volume will be created (e.g., EU-RO-1)."),
    name: str = Field(..., description="A user-defined name for the network volume. Names do not need to be unique and can be any descriptive label."),
    size: int = Field(..., description="The storage capacity to allocate for the network volume, specified in gigabytes. Must be between 0 and 4000 GB.", ge=0, le=4000),
) -> dict[str, Any] | ToolResult:
    """Create a new network volume in a specified Runpod data center. The volume will be allocated with the specified storage capacity and can be referenced by its user-defined name."""

    # Construct request model with validation
    try:
        _request = _models.CreateNetworkVolumeRequest(
            body=_models.CreateNetworkVolumeRequestBody(data_center_id=data_center_id, name=name, size=size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_network_volume: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/networkvolumes"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_network_volume")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_network_volume", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_network_volume",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: network volumes
@mcp.tool(
    title="Get Network Volume",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_network_volume(network_volume_id: str = Field(..., alias="networkVolumeId", description="The unique identifier of the network volume to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific network volume by its unique identifier. Returns detailed information about the requested network volume."""

    # Construct request model with validation
    try:
        _request = _models.GetNetworkVolumeRequest(
            path=_models.GetNetworkVolumeRequestPath(network_volume_id=network_volume_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_network_volume: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/networkvolumes/{networkVolumeId}", _request.path.model_dump(by_alias=True)) if _request.path else "/networkvolumes/{networkVolumeId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_network_volume")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_network_volume", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_network_volume",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: network volumes
@mcp.tool(
    title="Update Network Volume",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_network_volume(
    network_volume_id: str = Field(..., alias="networkVolumeId", description="The unique identifier of the network volume to be updated."),
    name: str | None = Field(None, description="A user-defined name for the network volume. Names do not need to be unique and can be changed at any time."),
    size: int | None = Field(None, description="The new disk space allocation in gigabytes (GB) for the network volume. Must be greater than the current size and cannot exceed 4000 GB.", ge=0, le=4000),
) -> dict[str, Any] | ToolResult:
    """Update the name and/or storage capacity of an existing network volume. Changes take effect immediately after the update is processed."""

    # Construct request model with validation
    try:
        _request = _models.UpdateNetworkVolumeRequest(
            path=_models.UpdateNetworkVolumeRequestPath(network_volume_id=network_volume_id),
            body=_models.UpdateNetworkVolumeRequestBody(name=name, size=size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_network_volume: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/networkvolumes/{networkVolumeId}", _request.path.model_dump(by_alias=True)) if _request.path else "/networkvolumes/{networkVolumeId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_network_volume")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_network_volume", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_network_volume",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: network volumes
@mcp.tool(
    title="Delete Network Volume",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_network_volume(network_volume_id: str = Field(..., alias="networkVolumeId", description="The unique identifier of the network volume to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a network volume by its ID. This operation removes the network volume and its associated resources from the system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteNetworkVolumeRequest(
            path=_models.DeleteNetworkVolumeRequestPath(network_volume_id=network_volume_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_network_volume: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/networkvolumes/{networkVolumeId}", _request.path.model_dump(by_alias=True)) if _request.path else "/networkvolumes/{networkVolumeId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_network_volume")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_network_volume", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_network_volume",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: network volumes
@mcp.tool(
    title="Update Network Volume",
    annotations=ToolAnnotations(
        idempotentHint=True,
        openWorldHint=True
    ),
)
async def update_network_volume_action(
    network_volume_id: str = Field(..., alias="networkVolumeId", description="The unique identifier of the network volume to update."),
    name: str | None = Field(None, description="A user-defined name for the network volume. Names do not need to be unique across volumes."),
    size: int | None = Field(None, description="The new disk space allocation in gigabytes. Must be between 0 and 4000 GB, and must exceed the current volume size.", ge=0, le=4000),
) -> dict[str, Any] | ToolResult:
    """Update the name and/or storage capacity of an existing network volume. The new size must be larger than the current allocated size."""

    # Construct request model with validation
    try:
        _request = _models.UpdateNetworkVolume2Request(
            path=_models.UpdateNetworkVolume2RequestPath(network_volume_id=network_volume_id),
            body=_models.UpdateNetworkVolume2RequestBody(name=name, size=size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_network_volume_action: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/networkvolumes/{networkVolumeId}/update", _request.path.model_dump(by_alias=True)) if _request.path else "/networkvolumes/{networkVolumeId}/update"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_network_volume_action")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_network_volume_action", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_network_volume_action",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: container registry auths
@mcp.tool(
    title="List Container Registry Auths",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_container_registry_auths() -> dict[str, Any] | ToolResult:
    """Retrieves a list of all container registry authentication configurations. Use this to view available registry credentials and their settings."""

    # Extract parameters for API call
    _http_path = "/containerregistryauth"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_container_registry_auths")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_container_registry_auths", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_container_registry_auths",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: container registry auths
@mcp.tool(
    title="Create Container Registry Auth",
    annotations=ToolAnnotations(
        openWorldHint=True
    ),
)
async def create_container_registry_auth(
    name: str = Field(..., description="A unique identifier for this container registry credential. Choose a descriptive name that helps you identify which registry or account this credential is for."),
    password: str = Field(..., description="The password or authentication token for accessing the container registry. This is stored securely and used when authenticating registry operations."),
    username: str = Field(..., description="The username or account identifier for accessing the container registry. This is paired with the password to authenticate registry operations."),
) -> dict[str, Any] | ToolResult:
    """Create a new container registry authentication credential with a unique name. This stores the username and password needed to authenticate with a container registry."""

    # Construct request model with validation
    try:
        _request = _models.CreateContainerRegistryAuthRequest(
            body=_models.CreateContainerRegistryAuthRequestBody(name=name, password=password, username=username)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_container_registry_auth: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/containerregistryauth"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_container_registry_auth")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_container_registry_auth", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_container_registry_auth",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/json",
        headers=_http_headers,
    )

    return _response_data

# Tags: container registry auths
@mcp.tool(
    title="Get Container Registry Auth",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def get_container_registry_auth(container_registry_auth_id: str = Field(..., alias="containerRegistryAuthId", description="The unique identifier of the container registry authentication configuration to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific container registry authentication configuration by its unique identifier. Returns the complete details of the requested registry auth."""

    # Construct request model with validation
    try:
        _request = _models.GetContainerRegistryAuthRequest(
            path=_models.GetContainerRegistryAuthRequestPath(container_registry_auth_id=container_registry_auth_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_container_registry_auth: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/containerregistryauth/{containerRegistryAuthId}", _request.path.model_dump(by_alias=True)) if _request.path else "/containerregistryauth/{containerRegistryAuthId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_container_registry_auth")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_container_registry_auth", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_container_registry_auth",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: container registry auths
@mcp.tool(
    title="Delete Container Registry Auth",
    annotations=ToolAnnotations(
        destructiveHint=True,
        openWorldHint=True
    ),
)
async def delete_container_registry_auth(container_registry_auth_id: str = Field(..., alias="containerRegistryAuthId", description="The unique identifier of the container registry authentication configuration to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a container registry authentication configuration. This removes the stored credentials and access settings for the specified registry."""

    # Construct request model with validation
    try:
        _request = _models.DeleteContainerRegistryAuthRequest(
            path=_models.DeleteContainerRegistryAuthRequestPath(container_registry_auth_id=container_registry_auth_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_container_registry_auth: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/containerregistryauth/{containerRegistryAuthId}", _request.path.model_dump(by_alias=True)) if _request.path else "/containerregistryauth/{containerRegistryAuthId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_container_registry_auth")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_container_registry_auth", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_container_registry_auth",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: billing
@mcp.tool(
    title="List Pod Billing History",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_pod_billing_history(
    bucket_size: Literal["hour", "day", "week", "month", "year"] | None = Field(None, alias="bucketSize", description="Time granularity for aggregating billing records. Choose from hourly, daily, weekly, monthly, or yearly buckets. Defaults to daily aggregation."),
    end_time: str | None = Field(None, alias="endTime", description="End of the billing period to retrieve, specified as an ISO 8601 datetime (e.g., 2023-01-31T23:59:59Z). If omitted, defaults to the current time."),
    gpu_type_id: Literal["NVIDIA GeForce RTX 4090", "NVIDIA A40", "NVIDIA RTX A5000", "NVIDIA GeForce RTX 5090", "NVIDIA H100 80GB HBM3", "NVIDIA GeForce RTX 3090", "NVIDIA RTX A4500", "NVIDIA L40S", "NVIDIA H200", "NVIDIA L4", "NVIDIA RTX 6000 Ada Generation", "NVIDIA A100-SXM4-80GB", "NVIDIA RTX 4000 Ada Generation", "NVIDIA RTX A6000", "NVIDIA A100 80GB PCIe", "NVIDIA RTX 2000 Ada Generation", "NVIDIA RTX A4000", "NVIDIA RTX PRO 6000 Blackwell Server Edition", "NVIDIA H100 PCIe", "NVIDIA H100 NVL", "NVIDIA L40", "NVIDIA B200", "NVIDIA GeForce RTX 3080 Ti", "NVIDIA RTX PRO 6000 Blackwell Workstation Edition", "NVIDIA GeForce RTX 3080", "NVIDIA GeForce RTX 3070", "AMD Instinct MI300X OAM", "NVIDIA GeForce RTX 4080 SUPER", "Tesla V100-PCIE-16GB", "Tesla V100-SXM2-32GB", "NVIDIA RTX 5000 Ada Generation", "NVIDIA GeForce RTX 4070 Ti", "NVIDIA RTX 4000 SFF Ada Generation", "NVIDIA GeForce RTX 3090 Ti", "NVIDIA RTX A2000", "NVIDIA GeForce RTX 4080", "NVIDIA A30", "NVIDIA GeForce RTX 5080", "Tesla V100-FHHL-16GB", "NVIDIA H200 NVL", "Tesla V100-SXM2-16GB", "NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition", "NVIDIA A5000 Ada", "Tesla V100-PCIE-32GB", "NVIDIA  RTX A4500", "NVIDIA  A30", "NVIDIA GeForce RTX 3080TI", "Tesla T4", "NVIDIA RTX A30"] | None = Field(None, alias="gpuTypeId", description="Filter results to Pods equipped with a specific GPU type. Accepts the full GPU model name (e.g., 'NVIDIA GeForce RTX 4090'). Omit to include all GPU types."),
    grouping: Literal["podId", "gpuTypeId"] | None = Field(None, description="Organize billing records by Pod ID or GPU type. Defaults to grouping by GPU type. Use 'podId' to see per-Pod breakdowns."),
    pod_id: str | None = Field(None, alias="podId", description="Filter results to a single Pod by its ID. Omit to include all Pods."),
    start_time: str | None = Field(None, alias="startTime", description="Start of the billing period to retrieve, specified as an ISO 8601 datetime (e.g., 2023-01-01T00:00:00Z). If omitted, defaults to 30 days before the end time."),
) -> dict[str, Any] | ToolResult:
    """Retrieve aggregated billing records for your Pods over a specified time period. Results can be grouped by individual Pod or GPU type, with flexible time bucket granularity."""

    # Construct request model with validation
    try:
        _request = _models.PodBillingRequest(
            query=_models.PodBillingRequestQuery(bucket_size=bucket_size, end_time=end_time, gpu_type_id=gpu_type_id, grouping=grouping, pod_id=pod_id, start_time=start_time)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pod_billing_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/billing/pods"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pod_billing_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pod_billing_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pod_billing_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: billing
@mcp.tool(
    title="List Endpoint Billing History",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_endpoint_billing_history(
    bucket_size: Literal["hour", "day", "week", "month", "year"] | None = Field(None, alias="bucketSize", description="Time bucket size for aggregating billing records. Choose from hourly, daily, weekly, monthly, or yearly aggregation. Defaults to daily."),
    data_center_id: list[Literal["EU-RO-1", "CA-MTL-1", "EU-SE-1", "US-IL-1", "EUR-IS-1", "EU-CZ-1", "US-TX-3", "EUR-IS-2", "US-KS-2", "US-GA-2", "US-WA-1", "US-TX-1", "CA-MTL-3", "EU-NL-1", "US-TX-4", "US-CA-2", "US-NC-1", "OC-AU-1", "US-DE-1", "EUR-IS-3", "CA-MTL-2", "AP-JP-1", "EUR-NO-1", "EU-FR-1", "US-KS-3", "US-GA-1"]] | None = Field(None, alias="dataCenterId", description="Filter results to endpoints in specific Runpod data centers. Provide an array of data center IDs (e.g., EU-RO-1, US-TX-3). Defaults to all available data centers."),
    endpoint_id: str | None = Field(None, alias="endpointId", description="Filter results to a single endpoint by its ID."),
    end_time: str | None = Field(None, alias="endTime", description="End date for the billing period in ISO 8601 format (e.g., 2023-01-31T23:59:59Z)."),
    gpu_type_id: list[Literal["NVIDIA GeForce RTX 4090", "NVIDIA A40", "NVIDIA RTX A5000", "NVIDIA GeForce RTX 5090", "NVIDIA H100 80GB HBM3", "NVIDIA GeForce RTX 3090", "NVIDIA RTX A4500", "NVIDIA L40S", "NVIDIA H200", "NVIDIA L4", "NVIDIA RTX 6000 Ada Generation", "NVIDIA A100-SXM4-80GB", "NVIDIA RTX 4000 Ada Generation", "NVIDIA RTX A6000", "NVIDIA A100 80GB PCIe", "NVIDIA RTX 2000 Ada Generation", "NVIDIA RTX A4000", "NVIDIA RTX PRO 6000 Blackwell Server Edition", "NVIDIA H100 PCIe", "NVIDIA H100 NVL", "NVIDIA L40", "NVIDIA B200", "NVIDIA GeForce RTX 3080 Ti", "NVIDIA RTX PRO 6000 Blackwell Workstation Edition", "NVIDIA GeForce RTX 3080", "NVIDIA GeForce RTX 3070", "AMD Instinct MI300X OAM", "NVIDIA GeForce RTX 4080 SUPER", "Tesla V100-PCIE-16GB", "Tesla V100-SXM2-32GB", "NVIDIA RTX 5000 Ada Generation", "NVIDIA GeForce RTX 4070 Ti", "NVIDIA RTX 4000 SFF Ada Generation", "NVIDIA GeForce RTX 3090 Ti", "NVIDIA RTX A2000", "NVIDIA GeForce RTX 4080", "NVIDIA A30", "NVIDIA GeForce RTX 5080", "Tesla V100-FHHL-16GB", "NVIDIA H200 NVL", "Tesla V100-SXM2-16GB", "NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition", "NVIDIA A5000 Ada", "Tesla V100-PCIE-32GB", "NVIDIA  RTX A4500", "NVIDIA  A30", "NVIDIA GeForce RTX 3080TI", "Tesla T4", "NVIDIA RTX A30"]] | None = Field(None, alias="gpuTypeId", description="Filter results to endpoints with specific GPU types attached. Provide an array of GPU type names (e.g., NVIDIA GeForce RTX 4090)."),
    grouping: Literal["endpointId", "podId", "gpuTypeId"] | None = Field(None, description="Group billing records by endpoint ID, pod ID, or GPU type. Defaults to grouping by endpoint ID."),
    image_name: str | None = Field(None, alias="imageName", description="Filter results to endpoints created with a specific container image."),
    start_time: str | None = Field(None, alias="startTime", description="Start date for the billing period in ISO 8601 format (e.g., 2023-01-01T00:00:00Z)."),
    template_id: str | None = Field(None, alias="templateId", description="Filter results to endpoints created from a specific template by its ID."),
) -> dict[str, Any] | ToolResult:
    """Retrieve aggregated billing records for your Serverless endpoints, with flexible filtering by location, GPU type, endpoint, and time range. Results can be grouped by endpoint, pod, or GPU type."""

    # Construct request model with validation
    try:
        _request = _models.EndpointBillingRequest(
            query=_models.EndpointBillingRequestQuery(bucket_size=bucket_size, data_center_id=data_center_id, endpoint_id=endpoint_id, end_time=end_time, gpu_type_id=gpu_type_id, grouping=grouping, image_name=image_name, start_time=start_time, template_id=template_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_endpoint_billing_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/billing/endpoints"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_endpoint_billing_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_endpoint_billing_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_endpoint_billing_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: billing
@mcp.tool(
    title="List Network Volume Billing",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=True
    ),
)
async def list_network_volume_billing(
    bucket_size: Literal["hour", "day", "week", "month", "year"] | None = Field(None, alias="bucketSize", description="The time granularity for aggregating billing data. Defaults to daily buckets if not specified. Valid options are hour, day, week, month, or year."),
    end_time: str | None = Field(None, alias="endTime", description="The end of the billing period to retrieve, specified as an ISO 8601 datetime string (e.g., 2023-01-31T23:59:59Z). If omitted, defaults to the current time."),
    start_time: str | None = Field(None, alias="startTime", description="The start of the billing period to retrieve, specified as an ISO 8601 datetime string (e.g., 2023-01-01T00:00:00Z). If omitted, defaults to a reasonable historical starting point."),
) -> dict[str, Any] | ToolResult:
    """Retrieve aggregated billing records for your network volumes over a specified time period. Results can be grouped by hour, day, week, month, or year."""

    # Construct request model with validation
    try:
        _request = _models.NetworkVolumeBillingRequest(
            query=_models.NetworkVolumeBillingRequestQuery(bucket_size=bucket_size, end_time=end_time, start_time=start_time)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_network_volume_billing: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/billing/networkvolumes"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_network_volume_billing")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_network_volume_billing", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_network_volume_billing",
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
        print("  python runpod_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Runpod MCP Server")

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
    logger.info("Starting Runpod MCP Server")
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

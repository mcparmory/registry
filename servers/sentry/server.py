#!/usr/bin/env python3
"""
API Reference MCP Server

API Info:
- API License: Apache 2.0 (http://www.apache.org/licenses/LICENSE-2.0.html)
- Terms of Service: http://sentry.io/terms/

Generated: 2026-05-05 16:19:13 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

import argparse
import asyncio
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
from pydantic import Field

# Server variables (from OpenAPI spec, overridable via SERVER_* env vars)
_SERVER_VARS = {
    "region": os.getenv("SERVER_REGION", "us"),
}
BASE_URL = os.getenv("BASE_URL", "https://{region}.sentry.io".format_map(collections.defaultdict(str, _SERVER_VARS)))
OPERATION_URL_MAP: dict[str, str] = {
    "upload_dsym_file": os.getenv("SERVER_URL_UPLOAD_DSYM_FILE", "https://{region}.sentry.io".format_map(collections.defaultdict(str, _SERVER_VARS))),
    "upload_release_file": os.getenv("SERVER_URL_UPLOAD_RELEASE_FILE", "https://{region}.sentry.io".format_map(collections.defaultdict(str, _SERVER_VARS))),
    "upload_release_file_project": os.getenv("SERVER_URL_UPLOAD_RELEASE_FILE_PROJECT", "https://{region}.sentry.io".format_map(collections.defaultdict(str, _SERVER_VARS))),
}
SERVER_NAME = "API Reference"
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


async def _make_request(
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    body: Any = None,
    body_content_type: str | None = None,
    multipart_file_fields: list[str] | None = None,
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
                if isinstance(body, dict):
                    for _key, _value in body.items():
                        if _value is None:
                            continue
                        if _key in _file_fields:
                            _file_values = _value if isinstance(_value, (list, tuple)) else [_value]
                            for _file_item in _file_values:
                                if _file_item is None:
                                    continue
                                if isinstance(_file_item, str):
                                    _file_content = _file_item.encode("utf-8")
                                elif isinstance(_file_item, (bytes, bytearray)):
                                    _file_content = bytes(_file_item)
                                else:
                                    raise ValueError(
                                        f"Unsupported multipart file field '{_key}': "
                                        "expected str, bytes, or list of str/bytes, got "
                                        f"{type(_file_item).__name__}"
                                    )
                                _multipart_parts.append(
                                    (_key, (f"{_key}.bin", _file_content, "application/octet-stream"))
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
                    if isinstance(body, str):
                        _file_content = body.encode("utf-8")
                    elif isinstance(body, (bytes, bytearray)):
                        _file_content = bytes(body)
                    else:
                        raise ValueError(
                            "Unsupported multipart file body: expected str or bytes "
                            f"for file part, got {type(body).__name__}"
                        )
                    _field_name = next(iter(_file_fields), "file")
                    _multipart_parts.append(
                        (_field_name, (f"{_field_name}.bin", _file_content, "application/octet-stream"))
                    )
                _files = _multipart_parts
            _content: bytes | str | None = None
            if body_content_type is not None and body_content_type not in ("application/json", "application/x-www-form-urlencoded", "multipart/form-data"):
                _raw = body
                if isinstance(_raw, (dict, list)):
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
    'auth_token',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["auth_token"] = _auth.BearerTokenAuth(env_var="BEARER_TOKEN", token_format="Bearer")
    logging.info("Authentication configured: auth_token")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for auth_token not configured: {error_msg}")
    _auth_handlers["auth_token"] = None

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

mcp = FastMCP("API Reference", middleware=[_JsonCoercionMiddleware()])

# Tags: Users
@mcp.tool()
async def list_organizations(
    owner: bool | None = Field(None, description="Set to `true` to filter results to only organizations where you have owner-level permissions."),
    query: str | None = Field(None, description="Filter organizations using query syntax supporting multiple fields: `id`, `slug`, `status` (active, pending_deletion, or deletion_in_progress), `email` or `member_id` for specific members, `platform` for projects using a given platform, and `query` for substring matching against name, slug, and member information. Supports boolean operators (AND, OR) and complex expressions."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of organizations accessible to the authenticated session. For user-bound contexts, returns all member organizations; for API key requests, returns only the organization associated with that key."""

    # Construct request model with validation
    try:
        _request = _models.ListYourOrganizationsRequest(
            query=_models.ListYourOrganizationsRequestQuery(owner=owner, query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organizations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api/0/organizations/"
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

# Tags: Organizations
@mcp.tool()
async def get_organization(
    organization_id_or_slug: str = Field(..., description="The unique identifier or slug of the organization. Use either the numeric ID or the URL-friendly slug name."),
    detailed: str | None = Field(None, description="Set to `\"0\"` to retrieve only basic organization details while excluding projects and teams from the response. Omit to include full details."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific organization, including membership access levels and associated teams."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAnOrganizationRequest(
            path=_models.RetrieveAnOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.RetrieveAnOrganizationRequestQuery(detailed=detailed)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def update_organization(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    slug: str | None = Field(None, description="New organization slug for URLs; must be unique across the instance and not exceed 50 characters.", max_length=50),
    name: str | None = Field(None, description="New display name for the organization; limited to 64 characters.", max_length=64),
    is_early_adopter: bool | None = Field(None, alias="isEarlyAdopter", description="Enable early access to unreleased features and experimental functionality."),
    hide_ai_features: bool | None = Field(None, alias="hideAiFeatures", description="Hide AI-powered features and recommendations from the organization's interface."),
    codecov_access: bool | None = Field(None, alias="codecovAccess", description="Enable Code Coverage Insights for tracking test coverage trends; available only on Team plan and above."),
    default_role: Literal["member", "admin", "manager", "owner"] | None = Field(None, alias="defaultRole", description="Default role assigned to newly invited members: member, admin, manager, or owner."),
    open_membership: bool | None = Field(None, alias="openMembership", description="Allow organization members to join any team without explicit invitation."),
    events_member_admin: bool | None = Field(None, alias="eventsMemberAdmin", description="Grant all members the ability to delete events and use the delete & discard action."),
    alerts_member_write: bool | None = Field(None, alias="alertsMemberWrite", description="Grant all members the ability to create, edit, and delete alert rules."),
    attachments_role: Literal["member", "admin", "manager", "owner"] | None = Field(None, alias="attachmentsRole", description="Minimum role required to download event attachments such as crash reports and log files: member, admin, manager, or owner."),
    debug_files_role: Literal["member", "admin", "manager", "owner"] | None = Field(None, alias="debugFilesRole", description="Minimum role required to download debug files, ProGuard mappings, and source maps: member, admin, manager, or owner."),
    has_granular_replay_permissions: bool | None = Field(None, alias="hasGranularReplayPermissions", description="Enable per-member access control for session replay data instead of role-based access."),
    replay_access_members: list[int] | None = Field(None, alias="replayAccessMembers", description="List of user IDs granted access to replay data; only enforced when granular replay permissions are enabled."),
    avatar: str | None = Field(None, description="Organization avatar image encoded as base64; required when avatarType is set to upload."),
    require2fa: bool | None = Field(None, alias="require2FA", description="Require and enforce two-factor authentication for all organization members."),
    allow_shared_issues: bool | None = Field(None, alias="allowSharedIssues", description="Allow sharing of limited issue details with anonymous users via public links."),
    enhanced_privacy: bool | None = Field(None, alias="enhancedPrivacy", description="Enable enhanced privacy mode to minimize personally identifiable information and source code in notifications and exports."),
    scrape_java_script: bool | None = Field(None, alias="scrapeJavaScript", description="Allow Sentry to automatically fetch missing JavaScript source context from public CDNs when available."),
    store_crash_reports: Literal[0, 1, 5, 10, 20, 50, 100, -1] | None = Field(None, alias="storeCrashReports", description="Number of native crash reports (minidumps, etc.) to retain per issue: 0 (disabled), 1, 5, 10, 20, 50, 100, or -1 (unlimited)."),
    allow_join_requests: bool | None = Field(None, alias="allowJoinRequests", description="Allow users to submit requests to join the organization without requiring an explicit invitation."),
    data_scrubber_defaults: bool | None = Field(None, alias="dataScrubberDefaults", description="Apply default data scrubbers organization-wide to prevent sensitive data like passwords and credit card numbers from being stored."),
    sensitive_fields: list[str] | None = Field(None, alias="sensitiveFields", description="List of additional field names to scrub across all projects; matched against event data during processing."),
    safe_fields: list[str] | None = Field(None, alias="safeFields", description="List of field names that data scrubbers should explicitly ignore and not redact."),
    scrub_ip_addresses: bool | None = Field(None, alias="scrubIPAddresses", description="Prevent IP addresses from being stored in new events across all projects."),
    relay_pii_config: str | None = Field(None, alias="relayPiiConfig", description="Advanced data scrubbing rules as a JSON string for masking or removing sensitive data patterns; overwrites existing rules and applies only to new events. See documentation for rule syntax and examples."),
    trusted_relays: list[dict[str, Any]] | None = Field(None, alias="trustedRelays", description="List of local Relay instances registered for the organization, each containing name, public key, and description; available only on Business and Enterprise plans."),
    github_pr_bot: bool | None = Field(None, alias="githubPRBot", description="Enable Sentry to post comments on recent GitHub pull requests suspected of introducing issues; requires GitHub integration."),
    github_nudge_invite: bool | None = Field(None, alias="githubNudgeInvite", description="Enable Sentry to detect GitHub repository committers not yet in the organization and suggest invitations; requires GitHub integration."),
    gitlab_pr_bot: bool | None = Field(None, alias="gitlabPRBot", description="Enable Sentry to post comments on recent GitLab merge requests suspected of introducing issues; requires GitLab integration."),
    issue_alerts_thread_flag: bool | None = Field(None, alias="issueAlertsThreadFlag", description="Allow Sentry Slack integration to post Issue Alert notifications as threaded replies instead of standalone messages; requires Slack integration."),
    metric_alerts_thread_flag: bool | None = Field(None, alias="metricAlertsThreadFlag", description="Allow Sentry Slack integration to post Metric Alert notifications as threaded replies instead of standalone messages; requires Slack integration."),
    cancel_deletion: bool | None = Field(None, alias="cancelDeletion", description="Restore an organization that is currently scheduled for deletion, canceling the deletion process."),
) -> dict[str, Any] | ToolResult:
    """Update organization settings, membership policies, security configurations, data privacy controls, and integration permissions. Changes apply to all projects within the organization."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAnOrganizationRequest(
            path=_models.UpdateAnOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug),
            body=_models.UpdateAnOrganizationRequestBody(slug=slug, name=name, is_early_adopter=is_early_adopter, hide_ai_features=hide_ai_features, codecov_access=codecov_access, default_role=default_role, open_membership=open_membership, events_member_admin=events_member_admin, alerts_member_write=alerts_member_write, attachments_role=attachments_role, debug_files_role=debug_files_role, has_granular_replay_permissions=has_granular_replay_permissions, replay_access_members=replay_access_members, avatar=avatar, require2fa=require2fa, allow_shared_issues=allow_shared_issues, enhanced_privacy=enhanced_privacy, scrape_java_script=scrape_java_script, store_crash_reports=store_crash_reports, allow_join_requests=allow_join_requests, data_scrubber_defaults=data_scrubber_defaults, sensitive_fields=sensitive_fields, safe_fields=safe_fields, scrub_ip_addresses=scrub_ip_addresses, relay_pii_config=relay_pii_config, trusted_relays=trusted_relays, github_pr_bot=github_pr_bot, github_nudge_invite=github_nudge_invite, gitlab_pr_bot=gitlab_pr_bot, issue_alerts_thread_flag=issue_alerts_thread_flag, metric_alerts_thread_flag=metric_alerts_thread_flag, cancel_deletion=cancel_deletion)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_organization", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_organization",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Alerts
@mcp.tool()
async def update_metric_alert_rule(
    organization_id_or_slug: str = Field(..., description="The ID or slug of the organization that owns the alert rule."),
    alert_rule_id: int = Field(..., description="The numeric ID of the alert rule to update."),
    name: str = Field(..., description="A descriptive name for the alert rule, up to 256 characters.", max_length=256),
    aggregate: str = Field(..., description="The aggregate function to apply to the metric. Valid options are: count, count_unique, percentage, avg, apdex, failure_rate, p50, p75, p95, p99, p100, or percentile."),
    time_window: Literal[1, 5, 10, 15, 30, 60, 120, 240, 1440] = Field(..., alias="timeWindow", description="The time window over which to aggregate the metric. Valid options are: 1 minute, 5 minutes, 10 minutes, 15 minutes, 30 minutes, 1 hour, 2 hours, 4 hours, or 24 hours."),
    projects: list[str] = Field(..., description="A list of project names to monitor. The alert will only apply to events from these projects."),
    query: str = Field(..., description="An event search query to filter which events trigger the alert (e.g., 'http.status_code:400'). Use an empty string to monitor all events without filtering."),
    threshold_type: Literal[0, 1] = Field(..., alias="thresholdType", description="The comparison operator for thresholds: 0 for 'Above' or 1 for 'Below'. The resolved threshold operator is automatically set to the opposite."),
    triggers: list[Any] = Field(..., description="A list of trigger objects, each with a label (critical or warning), alertThreshold value, and actions array. At least one critical trigger is required. Actions specify how to notify (email, Slack, PagerDuty, etc.) and to whom."),
    environment: str | None = Field(None, description="Optional environment name to filter events by (e.g., 'production', 'staging'). Defaults to all environments if not specified."),
    dataset: str | None = Field(None, description="The dataset to query: events, transactions, metrics, sessions, or generic-metrics. Defaults to events."),
    query_type: Literal[0, 1, 2] | None = Field(None, alias="queryType", description="The query type: 0 for error events, 1 for transactions, or 2 for none. Defaults based on the specified dataset if not provided."),
    event_types: list[str] | None = Field(None, alias="eventTypes", description="Optional list of event types to monitor: default (Capture Message events), error, or transaction."),
    comparison_delta: int | None = Field(None, alias="comparisonDelta", description="Optional time delta in minutes for percentage change comparisons. Required when using a percentage change threshold (e.g., 'x% higher than 60 minutes ago'). Not supported for Crash Free Session/User Rate alerts."),
    resolve_threshold: float | None = Field(None, alias="resolveThreshold", description="Optional threshold value at which the alert resolves. If not provided, it is automatically set based on the lowest severity trigger's threshold. Must be greater than the critical threshold when thresholdType is 0, or less than the critical threshold when thresholdType is 1."),
    owner: str | None = Field(None, description="Optional ID of the team or user that owns this alert rule."),
) -> dict[str, Any] | ToolResult:
    """Update a metric alert rule configuration that defines conditions for triggering alerts based on metrics like error count, latency, or failure rate. Warning: This operation fully overwrites the specified metric alert rule. (Deprecated: use Update a Monitor by ID or Update an Alert by ID instead)"""

    # Construct request model with validation
    try:
        _request = _models.DeprecatedUpdateAMetricAlertRuleRequest(
            path=_models.DeprecatedUpdateAMetricAlertRuleRequestPath(organization_id_or_slug=organization_id_or_slug, alert_rule_id=alert_rule_id),
            body=_models.DeprecatedUpdateAMetricAlertRuleRequestBody(name=name, aggregate=aggregate, time_window=time_window, projects=projects, query=query, threshold_type=threshold_type, triggers=triggers, environment=environment, dataset=dataset, query_type=query_type, event_types=event_types, comparison_delta=comparison_delta, resolve_threshold=resolve_threshold, owner=owner)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_metric_alert_rule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/alert-rules/{alert_rule_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/alert-rules/{alert_rule_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_metric_alert_rule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_metric_alert_rule", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_metric_alert_rule",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integrations
@mcp.tool()
async def list_integration_providers(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    provider_key: str | None = Field(None, alias="providerKey", description="Optional filter to retrieve details for a single integration provider (e.g., 'slack'). When omitted, information for all available providers is returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieve information about all available integration providers for an organization, with optional filtering by a specific provider type."""

    # Construct request model with validation
    try:
        _request = _models.GetIntegrationProviderInformationRequest(
            path=_models.GetIntegrationProviderInformationRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.GetIntegrationProviderInformationRequestQuery(provider_key=provider_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_integration_providers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/config/integrations/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/config/integrations/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_integration_providers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_integration_providers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_integration_providers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def list_organization_dashboards(
    organization_id_or_slug: str = Field(..., description="The unique identifier or slug of the organization. Use either the numeric ID or the organization's URL-friendly slug."),
    per_page: int | None = Field(None, description="Maximum number of dashboards to return in a single response. Defaults to 100 if not specified; cannot exceed 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all custom dashboards associated with an organization. Results can be paginated to control the number of dashboards returned per request."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSCustomDashboardsRequest(
            path=_models.ListAnOrganizationSCustomDashboardsRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.ListAnOrganizationSCustomDashboardsRequestQuery(per_page=per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_dashboards: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/dashboards/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/dashboards/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_dashboards")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_dashboards", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_dashboards",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def create_dashboard(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    title: str = Field(..., description="A human-readable name for the dashboard. Limited to 255 characters.", max_length=255),
    widgets: list[_models.CreateANewDashboardForAnOrganizationBodyWidgetsItem] | None = Field(None, description="An ordered list of widget objects that define the visualizations and data displayed on the dashboard."),
    projects: list[int] | None = Field(None, description="A list of project identifiers to filter dashboard data to specific projects."),
    environment: list[str] | None = Field(None, description="A list of environment names to filter dashboard data to specific environments."),
    filters: dict[str, Any] | None = Field(None, description="A structured object containing saved search filters and query parameters applied to the dashboard."),
    utc: bool | None = Field(None, description="When enabled, displays all time ranges and timestamps on the dashboard in UTC timezone instead of the user's local timezone."),
    permissions: _models.CreateANewDashboardForAnOrganizationBodyPermissions | None = Field(None, description="Access control settings that determine which users can view and edit this dashboard."),
    is_favorited: bool | None = Field(None, description="When set to true, automatically adds this dashboard to the requesting user's favorites list."),
) -> dict[str, Any] | ToolResult:
    """Create a new dashboard for an organization to visualize and monitor project metrics, events, and custom data. Dashboards can include widgets, project filters, environment filters, and saved search criteria."""

    # Construct request model with validation
    try:
        _request = _models.CreateANewDashboardForAnOrganizationRequest(
            path=_models.CreateANewDashboardForAnOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug),
            body=_models.CreateANewDashboardForAnOrganizationRequestBody(title=title, widgets=widgets, projects=projects, environment=environment, filters=filters, utc=utc, permissions=permissions, is_favorited=is_favorited)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/dashboards/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/dashboards/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_dashboard", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_dashboard",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def get_organization_dashboard(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    dashboard_id: int = Field(..., description="The numeric ID of the dashboard to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific custom dashboard within an organization, including its configuration and contents."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAnOrganizationSCustomDashboardRequest(
            path=_models.RetrieveAnOrganizationSCustomDashboardRequestPath(organization_id_or_slug=organization_id_or_slug, dashboard_id=dashboard_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/dashboards/{dashboard_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/dashboards/{dashboard_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_organization_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_organization_dashboard", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_organization_dashboard",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def update_organization_dashboard(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    dashboard_id: int = Field(..., description="The numeric ID of the dashboard to update."),
    title: str | None = Field(None, description="The dashboard's display name. Must not exceed 255 characters.", max_length=255),
    widgets: list[_models.EditAnOrganizationSCustomDashboardBodyWidgetsItem] | None = Field(None, description="An ordered array of widget objects representing the dashboard's visualizations. Each widget can include query definitions, field selections, and display type configurations."),
    projects: list[int] | None = Field(None, description="An array of project identifiers to filter the dashboard's data scope. Only events from these projects will be displayed."),
    environment: list[str] | None = Field(None, description="An array of environment names to filter the dashboard's data scope. Only events from these environments will be displayed."),
    filters: dict[str, Any] | None = Field(None, description="An object containing saved filter criteria applied across the dashboard. Filters are applied to all widgets unless overridden at the widget level."),
    utc: bool | None = Field(None, description="When enabled, displays all saved time ranges and timestamps in UTC timezone instead of the user's local timezone."),
    permissions: _models.EditAnOrganizationSCustomDashboardBodyPermissions | None = Field(None, description="Access control settings that define which users can view or edit this dashboard."),
) -> dict[str, Any] | ToolResult:
    """Update an organization's custom dashboard configuration, including its title, widgets, filters, and display settings. Supports bulk edits to widget arrangements, queries, fields, and display types."""

    # Construct request model with validation
    try:
        _request = _models.EditAnOrganizationSCustomDashboardRequest(
            path=_models.EditAnOrganizationSCustomDashboardRequestPath(organization_id_or_slug=organization_id_or_slug, dashboard_id=dashboard_id),
            body=_models.EditAnOrganizationSCustomDashboardRequestBody(title=title, widgets=widgets, projects=projects, environment=environment, filters=filters, utc=utc, permissions=permissions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_organization_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/dashboards/{dashboard_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/dashboards/{dashboard_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_organization_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_organization_dashboard", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_organization_dashboard",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def delete_organization_dashboard(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    dashboard_id: int = Field(..., description="The numeric ID of the dashboard to delete."),
) -> dict[str, Any] | ToolResult:
    """Delete an organization's custom dashboard or tombstone a pre-built dashboard to effectively remove it from the organization."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnOrganizationSCustomDashboardRequest(
            path=_models.DeleteAnOrganizationSCustomDashboardRequestPath(organization_id_or_slug=organization_id_or_slug, dashboard_id=dashboard_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_organization_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/dashboards/{dashboard_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/dashboards/{dashboard_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_organization_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_organization_dashboard", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_organization_dashboard",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def list_organization_monitors(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug. This determines which organization's monitors are returned."),
    query: str | None = Field(None, description="Optional search query to filter monitors by name, type (e.g., error, metric_issue, issue_stream), or assignee (email, username, team reference with # prefix, 'me', or 'none')."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all monitors configured for an organization. This endpoint supports the new monitoring and alerting system and allows filtering by monitor properties such as name, type, and assignee."""

    # Construct request model with validation
    try:
        _request = _models.FetchAnOrganizationSMonitorsRequest(
            path=_models.FetchAnOrganizationSMonitorsRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.FetchAnOrganizationSMonitorsRequestQuery(query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_monitors: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/detectors/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/detectors/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_monitors")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_monitors", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_monitors",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def update_organization_monitors_enabled_state(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the organization slug."),
    enabled: bool = Field(..., description="Set to true to enable the selected monitors or false to disable them."),
    query: str | None = Field(None, description="Optional search query to filter which monitors are affected. Supports filtering by monitor name, type (such as error, metric_issue, or issue_stream), or assignee (email, username, team reference with # prefix, 'me', or 'none')."),
) -> dict[str, Any] | ToolResult:
    """Bulk enable or disable monitors across an organization, optionally filtered by search criteria. This beta endpoint supports the New Monitors and Alerts system."""

    # Construct request model with validation
    try:
        _request = _models.MutateAnOrganizationSMonitorsRequest(
            path=_models.MutateAnOrganizationSMonitorsRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.MutateAnOrganizationSMonitorsRequestQuery(query=query),
            body=_models.MutateAnOrganizationSMonitorsRequestBody(enabled=enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_organization_monitors_enabled_state: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/detectors/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/detectors/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_organization_monitors_enabled_state")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_organization_monitors_enabled_state", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_organization_monitors_enabled_state",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def delete_monitors_bulk(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the organization slug."),
    query: str | None = Field(None, description="Optional search query to filter which monitors to delete. Supports filtering by name, type (error, metric_issue, issue_stream), or assignee (email, username, #team, me, none)."),
) -> dict[str, Any] | ToolResult:
    """Bulk delete monitors for an organization, optionally filtered by search criteria. This beta endpoint supports the New Monitors and Alerts system."""

    # Construct request model with validation
    try:
        _request = _models.BulkDeleteMonitorsRequest(
            path=_models.BulkDeleteMonitorsRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.BulkDeleteMonitorsRequestQuery(query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_monitors_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/detectors/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/detectors/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_monitors_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_monitors_bulk", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_monitors_bulk",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def get_monitor_detector(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL slug of the organization."),
    detector_id: int = Field(..., description="The numeric ID of the monitor to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific monitor (detector). This endpoint is part of the New Monitors and Alerts system and is currently in beta."""

    # Construct request model with validation
    try:
        _request = _models.FetchAMonitorRequest(
            path=_models.FetchAMonitorRequestPath(organization_id_or_slug=organization_id_or_slug, detector_id=detector_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_monitor_detector: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/detectors/{detector_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/detectors/{detector_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_monitor_detector")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_monitor_detector", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_monitor_detector",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def update_monitor_detector(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or URL-friendly slug."),
    detector_id: int = Field(..., description="The numeric ID of the monitor to update."),
    name: str = Field(..., description="Display name for the monitor. Maximum 200 characters.", max_length=200),
    type_: str = Field(..., alias="type", description="The monitor classification type. Currently supports `metric_issue` for metric-based monitoring."),
    workflow_ids: list[int] | None = Field(None, description="Array of alert workflow IDs to connect this monitor to. Use the Fetch Alerts endpoint to discover available workflow IDs."),
    data_sources: list[Any] | None = Field(None, description="Array of data source configurations defining what metric to measure. Each source specifies the aggregate function (e.g., count(), p95(span.duration)), dataset (events, events_analytics_platform, or generic_metrics), environment, event types to include, query filters, query type, and time window in seconds. Refer to monitor type examples for valid aggregate and dataset combinations."),
    config: dict[str, Any] | None = Field(None, description="Detection algorithm configuration. Choose `static` for threshold-based alerts, `percent` for change-based detection (requires comparisonDelta in minutes), or `dynamic` for anomaly detection."),
    condition_group: _models.UpdateAMonitorByIdBodyConditionGroup | None = Field(None, description="Condition group defining alert triggers and priority levels. Specify logic type, conditions with comparison operators (gt, lte, anomaly_detection), threshold values, and resulting issue states (75=high priority, 50=low priority, 0=resolved). For dynamic monitors, configure seasonality, sensitivity (low/medium/high), and threshold direction."),
    owner: str | None = Field(None, description="Owner assignment as either a user ID (prefixed with 'user:') or team ID (prefixed with 'team:'). Example: 'user:123456' or 'team:456789'."),
    description: str | None = Field(None, description="Detailed description of the monitor's purpose and scope. Will be included in generated issues."),
    enabled: bool | None = Field(None, description="Boolean flag to enable or disable the monitor. Set to false to deactivate without deleting."),
) -> dict[str, Any] | ToolResult:
    """Update an existing metric monitor with new configuration, data sources, detection rules, and alert connections. This beta endpoint supports threshold-based, change-based, and dynamic anomaly detection monitors."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAMonitorByIdRequest(
            path=_models.UpdateAMonitorByIdRequestPath(organization_id_or_slug=organization_id_or_slug, detector_id=detector_id),
            body=_models.UpdateAMonitorByIdRequestBody(name=name, type_=type_, workflow_ids=workflow_ids, data_sources=data_sources, config=config, condition_group=condition_group, owner=owner, description=description, enabled=enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_monitor_detector: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/detectors/{detector_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/detectors/{detector_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_monitor_detector")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_monitor_detector", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_monitor_detector",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def delete_monitor(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug of the organization that owns the monitor."),
    detector_id: int = Field(..., description="The numeric ID of the monitor to delete."),
) -> dict[str, Any] | ToolResult:
    """Permanently delete a monitor (detector) from an organization. This beta endpoint is part of the New Monitors and Alerts system and may not yet be visible in the UI."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAMonitorRequest(
            path=_models.DeleteAMonitorRequestPath(organization_id_or_slug=organization_id_or_slug, detector_id=detector_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_monitor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/detectors/{detector_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/detectors/{detector_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_monitor")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_monitor", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_monitor",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Discover
@mcp.tool()
async def list_organization_discover_saved_queries(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either its numeric ID or URL-friendly slug."),
    per_page: int | None = Field(None, description="Maximum number of results to return per page, up to 100 (default is 100)."),
    query: str | None = Field(None, description="Filter results by the exact or partial name of the saved Discover query."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all saved Discover queries associated with an organization, with optional filtering by query name and pagination support."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSDiscoverSavedQueriesRequest(
            path=_models.ListAnOrganizationSDiscoverSavedQueriesRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.ListAnOrganizationSDiscoverSavedQueriesRequestQuery(per_page=per_page, query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_discover_saved_queries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/discover/saved/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/discover/saved/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_discover_saved_queries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_discover_saved_queries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_discover_saved_queries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Discover
@mcp.tool()
async def create_saved_query(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug."),
    name: str = Field(..., description="A descriptive name for the saved query, up to 255 characters.", max_length=255),
    projects: list[int] | None = Field(None, description="An array of project IDs to filter the query results by. If omitted, the query applies to all projects in the organization."),
    range_: str | None = Field(None, alias="range", description="A time range period for the query (e.g., '24h', '7d', '30d'). Defines the default time window when the saved query is loaded."),
    fields: list[str] | None = Field(None, description="An array of up to 20 fields, functions, or equations to retrieve. Fields can be event properties (e.g., 'transaction'), tags (e.g., 'tag[isEnterprise]'), functions (e.g., 'count_if(transaction.duration,greater,300)'), or equations prefixed with 'equation|'."),
    orderby: str | None = Field(None, description="The field or function to sort results by. Must be one of the fields specified in the fields array, and cannot be an equation."),
    environment: list[str] | None = Field(None, description="An array of environment names to filter the query by (e.g., 'production', 'staging'). If omitted, all environments are included."),
    query: str | None = Field(None, description="A search query using Sentry's query syntax to filter results further. Supports boolean operators and field-specific filters."),
    y_axis: list[str] | None = Field(None, alias="yAxis", description="An array of aggregate functions to plot on the chart (e.g., 'count()', 'avg(transaction.duration)'). Used for time-series visualization."),
    display: str | None = Field(None, description="The chart visualization type: 'default' (line chart), 'previous' (comparison), 'top5' (top 5 series), 'daily' (daily breakdown), 'dailytop5' (daily top 5), or 'bar' (bar chart)."),
    top_events: int | None = Field(None, alias="topEvents", description="The number of top events' time-series to display on the chart, between 1 and 10. Only applies when using top-events visualization modes.", ge=1, le=10),
) -> dict[str, Any] | ToolResult:
    """Create a new saved query for an organization to store custom Discover search configurations, including filters, fields, aggregations, and visualization settings."""

    # Construct request model with validation
    try:
        _request = _models.CreateANewSavedQueryRequest(
            path=_models.CreateANewSavedQueryRequestPath(organization_id_or_slug=organization_id_or_slug),
            body=_models.CreateANewSavedQueryRequestBody(name=name, projects=projects, range_=range_, fields=fields, orderby=orderby, environment=environment, query=query, y_axis=y_axis, display=display, top_events=top_events)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_saved_query: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/discover/saved/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/discover/saved/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_saved_query")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_saved_query", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_saved_query",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Discover
@mcp.tool()
async def get_discover_saved_query(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL slug of the organization."),
    query_id: int = Field(..., description="The numeric ID of the saved Discover query to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a saved Discover query by its ID within a specific organization. This returns the full configuration and metadata of the saved query."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAnOrganizationSDiscoverSavedQueryRequest(
            path=_models.RetrieveAnOrganizationSDiscoverSavedQueryRequestPath(organization_id_or_slug=organization_id_or_slug, query_id=query_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_discover_saved_query: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/discover/saved/{query_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/discover/saved/{query_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_discover_saved_query")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_discover_saved_query", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_discover_saved_query",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Discover
@mcp.tool()
async def update_discover_saved_query(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug."),
    query_id: int = Field(..., description="The numeric ID of the saved Discover query to modify."),
    name: str = Field(..., description="A user-defined name for the saved query. Maximum 255 characters.", max_length=255),
    projects: list[int] | None = Field(None, description="Array of project IDs to filter the query results by. Order is not significant."),
    range_: str | None = Field(None, alias="range", description="A time range period for the query (e.g., '24h', '7d', '30d'). Determines the lookback window for events."),
    fields: list[str] | None = Field(None, description="Array of fields, functions, or equations to retrieve in query results. Maximum 20 items per request. Supports built-in event properties, tags (prefixed with 'tag['), aggregate functions, and equations (prefixed with 'equation|'). When functions are included, results are automatically grouped by tags and fields."),
    orderby: str | None = Field(None, description="Field or function name to sort results by. Must be a value from the fields array, excluding equations."),
    environment: list[str] | None = Field(None, description="Array of environment names to filter results by (e.g., 'production', 'staging'). Order is not significant."),
    query: str | None = Field(None, description="Query filter expression using Sentry's search syntax to narrow results by event properties and tags."),
    y_axis: list[str] | None = Field(None, alias="yAxis", description="Array of aggregate functions to plot on the chart (e.g., 'count()', 'avg(transaction.duration)'). Order determines axis positioning."),
    display: str | None = Field(None, description="Chart visualization type. Choose from: default, previous, top5, daily, dailytop5, or bar."),
    top_events: int | None = Field(None, alias="topEvents", description="Number of top events' timeseries to display on the chart. Must be between 1 and 10.", ge=1, le=10),
) -> dict[str, Any] | ToolResult:
    """Modify an existing saved Discover query, including its name, filters, fields, visualization settings, and aggregations."""

    # Construct request model with validation
    try:
        _request = _models.EditAnOrganizationSDiscoverSavedQueryRequest(
            path=_models.EditAnOrganizationSDiscoverSavedQueryRequestPath(organization_id_or_slug=organization_id_or_slug, query_id=query_id),
            body=_models.EditAnOrganizationSDiscoverSavedQueryRequestBody(name=name, projects=projects, range_=range_, fields=fields, orderby=orderby, environment=environment, query=query, y_axis=y_axis, display=display, top_events=top_events)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_discover_saved_query: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/discover/saved/{query_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/discover/saved/{query_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_discover_saved_query")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_discover_saved_query", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_discover_saved_query",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Discover
@mcp.tool()
async def delete_discover_saved_query(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    query_id: int = Field(..., description="The numeric ID of the saved Discover query to delete."),
) -> dict[str, Any] | ToolResult:
    """Permanently delete a saved Discover query from an organization. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnOrganizationSDiscoverSavedQueryRequest(
            path=_models.DeleteAnOrganizationSDiscoverSavedQueryRequestPath(organization_id_or_slug=organization_id_or_slug, query_id=query_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_discover_saved_query: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/discover/saved/{query_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/discover/saved/{query_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_discover_saved_query")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_discover_saved_query", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_discover_saved_query",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def list_organization_environments(
    organization_id_or_slug: str = Field(..., description="The unique identifier or slug of the organization. You can use either the numeric ID or the organization's URL-friendly slug."),
    visibility: Literal["all", "hidden", "visible"] | None = Field(None, description="Filter environments by their visibility status. Choose 'visible' to show only active environments, 'hidden' to show only inactive ones, or 'all' to retrieve both. Defaults to 'visible' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all environments for a specified organization, with optional filtering by visibility status. Use this to discover available deployment environments and their configurations."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSEnvironmentsRequest(
            path=_models.ListAnOrganizationSEnvironmentsRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.ListAnOrganizationSEnvironmentsRequestQuery(visibility=visibility)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_environments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/environments/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/environments/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_environments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_environments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_environments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def resolve_event_id(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    event_id: str = Field(..., description="The event ID to resolve. This is the unique identifier for the event you want to look up."),
) -> dict[str, Any] | ToolResult:
    """Resolves an event ID to retrieve the associated project slug, internal issue ID, and internal event ID for a given organization."""

    # Construct request model with validation
    try:
        _request = _models.ResolveAnEventIdRequest(
            path=_models.ResolveAnEventIdRequestPath(organization_id_or_slug=organization_id_or_slug, event_id=event_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for resolve_event_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/eventids/{event_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/eventids/{event_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("resolve_event_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("resolve_event_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="resolve_event_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Explore
@mcp.tool()
async def search_events_in_table_format(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either its numeric ID or URL-friendly slug."),
    field: list[str] = Field(..., description="The columns to include in results. Select up to 20 fields, which can be built-in properties (e.g., transaction, environment), tags in tag[name, type] format, functions like count() or count_if(), or equations prefixed with equation|. See searchable properties documentation for available fields per dataset."),
    dataset: Literal["logs", "profile_functions", "spans", "uptime_results"] = Field(..., description="The data source to query. Choose from logs, profile_functions, spans, or uptime_results; available fields vary by dataset."),
    environment: list[str] | None = Field(None, description="Filter results to specific environment names. Provide as a comma-separated list or multiple array values."),
    per_page: int | None = Field(None, description="Maximum number of result rows to return, up to 100 (default is 100)."),
    query: str | None = Field(None, description="Filter events using Sentry query syntax with logical operators (AND, OR) and field conditions. Example: (transaction:foo AND release:abc) OR (transaction:[bar,baz])."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a table of events from a specified organization matching your query criteria. Use this to explore event data with selected fields and optional filtering; not intended for full data exports."""

    # Construct request model with validation
    try:
        _request = _models.QueryExploreEventsInTableFormatRequest(
            path=_models.QueryExploreEventsInTableFormatRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.QueryExploreEventsInTableFormatRequestQuery(field=field, dataset=dataset, environment=environment, per_page=per_page, query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_events_in_table_format: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/events/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/events/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_events_in_table_format")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_events_in_table_format", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_events_in_table_format",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Explore
@mcp.tool()
async def get_events_timeseries(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or URL slug."),
    dataset: Literal["logs", "profile_functions", "spans", "uptime_results"] = Field(..., description="The dataset to query. Different datasets provide different available fields: logs, profile_functions, spans, or uptime_results."),
    environment: list[str] | None = Field(None, description="Filter results to specific environments by name. Accepts multiple environment names as an array."),
    top_events: int | None = Field(None, alias="topEvents", description="Return the top N events by the sort criteria. Must be between 1 and 10. When specified, both groupBy and sort parameters become required."),
    comparison_delta: int | None = Field(None, alias="comparisonDelta", description="Return an additional offset timeseries shifted by this many seconds for comparison purposes."),
    group_by: list[str] | None = Field(None, alias="groupBy", description="Fields to group results by, determining which events are considered 'top' when used with topEvents. Required when topEvents is specified. Accepts multiple field names as an array."),
    y_axis: str | None = Field(None, alias="yAxis", description="The aggregate function to compute for the timeseries (e.g., count(), sum(), avg()). Defaults to count() if not provided."),
    query: str | None = Field(None, description="Filter results using Sentry query syntax. Supports boolean operators (AND, OR) and field matching with ranges or multiple values."),
) -> dict[str, Any] | ToolResult:
    """Retrieves event data for an organization as a timeseries, supporting single or multiple axes with optional grouping by top events. Results can be filtered by environment, time range, and custom query syntax."""

    # Construct request model with validation
    try:
        _request = _models.QueryExploreEventsInTimeseriesFormatRequest(
            path=_models.QueryExploreEventsInTimeseriesFormatRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.QueryExploreEventsInTimeseriesFormatRequestQuery(dataset=dataset, environment=environment, top_events=top_events, comparison_delta=comparison_delta, group_by=group_by, y_axis=y_axis, query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_events_timeseries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/events-timeseries/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/events-timeseries/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_events_timeseries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_events_timeseries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_events_timeseries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integrations
@mcp.tool()
async def link_external_user(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug of the organization."),
    user_id: int = Field(..., description="The numeric ID of the Sentry user to link to the external provider."),
    external_name: str = Field(..., description="The display name or username associated with the user in the external provider system."),
    provider: Literal["github", "github_enterprise", "jira_server", "slack", "slack_staging", "perforce", "gitlab", "msteams", "custom_scm"] = Field(..., description="The external provider platform. Supported providers include GitHub, GitHub Enterprise, Jira Server, Slack, Slack Staging, Perforce, GitLab, Microsoft Teams, and custom SCM systems."),
    integration_id: int = Field(..., description="The numeric ID of the integration configuration that connects Sentry to the external provider."),
    external_id: str | None = Field(None, description="The unique user identifier or account ID assigned by the external provider. This is optional if the external name is sufficient for identification."),
) -> dict[str, Any] | ToolResult:
    """Link a user from an external provider (such as GitHub, Slack, Jira, or GitLab) to a Sentry user account, enabling cross-platform identity mapping and integration."""

    # Construct request model with validation
    try:
        _request = _models.CreateAnExternalUserRequest(
            path=_models.CreateAnExternalUserRequestPath(organization_id_or_slug=organization_id_or_slug),
            body=_models.CreateAnExternalUserRequestBody(user_id=user_id, external_name=external_name, provider=provider, integration_id=integration_id, external_id=external_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for link_external_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/external-users/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/external-users/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("link_external_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("link_external_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="link_external_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integrations
@mcp.tool()
async def update_external_user(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    external_user_id: int = Field(..., description="The unique identifier of the external user object to update, returned when the external user was initially created."),
    user_id: int = Field(..., description="The numeric ID of the Sentry user account that this external user is linked to."),
    external_name: str = Field(..., description="The display name or username for this user in the external provider's system."),
    provider: Literal["github", "github_enterprise", "jira_server", "slack", "slack_staging", "perforce", "gitlab", "msteams", "custom_scm"] = Field(..., description="The external provider platform. Supported providers include GitHub, GitHub Enterprise, Jira Server, Slack, Slack Staging, Perforce, GitLab, Microsoft Teams, and custom SCM systems."),
    integration_id: int = Field(..., description="The numeric ID of the integration configuration that connects Sentry to the external provider."),
    external_id: str | None = Field(None, description="The user's unique identifier within the external provider system (e.g., user ID, handle, or account number). Optional if already set."),
) -> dict[str, Any] | ToolResult:
    """Update the details of an external user account linked to a Sentry user. This synchronizes user information across integrated external providers like GitHub, Slack, Jira, or GitLab."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAnExternalUserRequest(
            path=_models.UpdateAnExternalUserRequestPath(organization_id_or_slug=organization_id_or_slug, external_user_id=external_user_id),
            body=_models.UpdateAnExternalUserRequestBody(user_id=user_id, external_name=external_name, provider=provider, integration_id=integration_id, external_id=external_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_external_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/external-users/{external_user_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/external-users/{external_user_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_external_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_external_user", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_external_user",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integrations
@mcp.tool()
async def delete_external_user(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    external_user_id: int = Field(..., description="The unique identifier of the external user object to delete. This ID is provided when the external user is initially created."),
) -> dict[str, Any] | ToolResult:
    """Remove the link between an external provider user and a Sentry user account, effectively disconnecting the external identity from the organization."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnExternalUserRequest(
            path=_models.DeleteAnExternalUserRequestPath(organization_id_or_slug=organization_id_or_slug, external_user_id=external_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_external_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/external-users/{external_user_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/external-users/{external_user_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_external_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_external_user", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_external_user",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integrations
@mcp.tool()
async def list_data_forwarders_for_organization(organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")) -> dict[str, Any] | ToolResult:
    """Retrieves all data forwarders configured for a specific organization. Data forwarders enable automatic forwarding of events and data to external destinations."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveDataForwardersForAnOrganizationRequest(
            path=_models.RetrieveDataForwardersForAnOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_data_forwarders_for_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/forwarding/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/forwarding/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_data_forwarders_for_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_data_forwarders_for_organization", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_data_forwarders_for_organization",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integrations
@mcp.tool()
async def create_data_forwarder_for_organization(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the organization slug."),
    organization_id: int = Field(..., description="The numeric ID of the organization that will own this data forwarder."),
    provider: Literal["segment", "sqs", "splunk"] = Field(..., description="The data destination provider: Segment, Amazon SQS, or Splunk. Each provider requires specific configuration keys."),
    is_enabled: bool | None = Field(None, description="Whether the data forwarder is active and forwarding data. Defaults to enabled."),
    enroll_new_projects: bool | None = Field(None, description="Whether newly created projects are automatically enrolled with this data forwarder. Defaults to disabled."),
    config: dict[str, str] | None = Field(None, description="Provider-specific configuration object. For SQS: queue_url, region, access_key, secret_key (required), plus optional message_group_id for FIFO queues and optional s3_bucket. For Segment: write_key (required). For Splunk: instance_url, index, source, token (all required)."),
    project_ids: list[int] | None = Field(None, description="List of project IDs to enroll with this data forwarder. Projects not included will be unenrolled if they were previously connected."),
) -> dict[str, Any] | ToolResult:
    """Creates a new data forwarder for an organization to forward data to external providers like Segment, Amazon SQS, or Splunk. Only one data forwarder per provider is allowed per organization."""

    # Construct request model with validation
    try:
        _request = _models.CreateADataForwarderForAnOrganizationRequest(
            path=_models.CreateADataForwarderForAnOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug),
            body=_models.CreateADataForwarderForAnOrganizationRequestBody(organization_id=organization_id, provider=provider, is_enabled=is_enabled, enroll_new_projects=enroll_new_projects, config=config, project_ids=project_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_data_forwarder_for_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/forwarding/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/forwarding/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_data_forwarder_for_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_data_forwarder_for_organization", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_data_forwarder_for_organization",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integrations
@mcp.tool()
async def update_data_forwarder(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the organization slug."),
    data_forwarder_id: int = Field(..., description="The numeric ID of the data forwarder to update."),
    organization_id: int = Field(..., description="The numeric ID of the organization that owns the data forwarder."),
    provider: Literal["segment", "sqs", "splunk"] = Field(..., description="The data forwarding provider: Segment, Amazon SQS, or Splunk. Each provider requires specific configuration fields."),
    is_enabled: bool | None = Field(None, description="Whether the data forwarder is active. Defaults to true if not specified."),
    enroll_new_projects: bool | None = Field(None, description="Whether newly created projects should automatically be enrolled with this forwarder. Defaults to false if not specified."),
    config: dict[str, str] | None = Field(None, description="Provider-specific configuration object. For SQS: requires queue_url, region, access_key, secret_key (and message_group_id for FIFO queues; s3_bucket is optional). For Segment: requires write_key. For Splunk: requires instance_url, index, source, and token. When updating organization-level configuration, provide the complete config; for project overrides, only include fields to override."),
    project_ids: list[int] | None = Field(None, description="Array of project numeric IDs to connect to this forwarder. Projects not included will be unenrolled if previously connected. Required when updating organization-level configuration."),
) -> dict[str, Any] | ToolResult:
    """Updates a data forwarder configuration for an organization, or creates/modifies project-specific overrides. Organization-level updates require the full configuration including project IDs, while project-level overrides only need the project ID, overrides object, and enabled status."""

    # Construct request model with validation
    try:
        _request = _models.UpdateADataForwarderForAnOrganizationRequest(
            path=_models.UpdateADataForwarderForAnOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug, data_forwarder_id=data_forwarder_id),
            body=_models.UpdateADataForwarderForAnOrganizationRequestBody(organization_id=organization_id, provider=provider, is_enabled=is_enabled, enroll_new_projects=enroll_new_projects, config=config, project_ids=project_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_data_forwarder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/forwarding/{data_forwarder_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/forwarding/{data_forwarder_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_data_forwarder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_data_forwarder", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_data_forwarder",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integrations
@mcp.tool()
async def delete_data_forwarder_for_organization(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    data_forwarder_id: int = Field(..., description="The numeric ID of the data forwarder to delete."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a data forwarder from an organization, including all associated project-specific overrides."""

    # Construct request model with validation
    try:
        _request = _models.DeleteADataForwarderForAnOrganizationRequest(
            path=_models.DeleteADataForwarderForAnOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug, data_forwarder_id=data_forwarder_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_data_forwarder_for_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/forwarding/{data_forwarder_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/forwarding/{data_forwarder_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_data_forwarder_for_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_data_forwarder_for_organization", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_data_forwarder_for_organization",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integrations
@mcp.tool()
async def list_organization_integrations(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    provider_key: str | None = Field(None, alias="providerKey", description="Filter results to a specific integration provider (e.g., slack, github, jira). Omit to return all providers."),
    features: list[str] | None = Field(None, description="Filter integrations by one or more capabilities they support, such as alert-rule, incident-management, or issue-sync. Items are matched inclusively (any matching feature will be included)."),
    include_config: bool | None = Field(None, alias="includeConfig", description="Set to true to include third-party integration configurations in the response. Note: enabling this may significantly increase response time."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all available integrations for an organization, with optional filtering by provider and features. Use includeConfig to fetch third-party configuration details if needed."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSAvailableIntegrationsRequest(
            path=_models.ListAnOrganizationSAvailableIntegrationsRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.ListAnOrganizationSAvailableIntegrationsRequestQuery(provider_key=provider_key, features=features, include_config=include_config)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_integrations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/integrations/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/integrations/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_integrations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_integrations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_integrations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integrations
@mcp.tool()
async def get_organization_integration(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    integration_id: str = Field(..., description="The unique identifier of the integration installed on the organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific integration installed on an organization. Both the integration and its organization-specific configuration must exist."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAnIntegrationForAnOrganizationRequest(
            path=_models.RetrieveAnIntegrationForAnOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug, integration_id=integration_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization_integration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/integrations/{integration_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/integrations/{integration_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_organization_integration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_organization_integration", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_organization_integration",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integrations
@mcp.tool()
async def delete_organization_integration(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    integration_id: str = Field(..., description="The unique identifier of the integration that is installed on the organization."),
) -> dict[str, Any] | ToolResult:
    """Remove an integration from an organization. This operation requires both the Integration and OrganizationIntegration database entries to exist for the specified organization and integration."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnIntegrationForAnOrganizationRequest(
            path=_models.DeleteAnIntegrationForAnOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug, integration_id=integration_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_organization_integration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/integrations/{integration_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/integrations/{integration_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_organization_integration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_organization_integration", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_organization_integration",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def list_organization_issues(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    environment: list[str] | None = Field(None, description="Filter issues by one or more environment names. Provide as a list of environment identifiers."),
    group_stats_period: Literal["", "14d", "24h", "auto"] | None = Field(None, alias="groupStatsPeriod", description="The time period for which to calculate group statistics. Choose from: empty string (no stats), '24h' (last 24 hours), '14d' (last 14 days), or 'auto' (automatic period selection)."),
    query: str | None = Field(None, description="Search query to filter issues using Sentry's query syntax (e.g., 'is:unresolved', 'error.type:ValueError'). Leave empty to retrieve all issues; if omitted, defaults to 'is:unresolved'."),
    limit: int | None = Field(None, description="Maximum number of issues to return in the response. Must be between 1 and 100; defaults to 100."),
    expand: list[Literal["inbox", "integrationIssues", "latestEventHasAttachments", "owners", "pluginActions", "pluginIssues", "sentryAppIssues", "sessions"]] | None = Field(None, description="Specify additional data fields to include in the response for each issue (e.g., 'sessions', 'latestEventHasUrl'). Provide as a list of field names."),
    collapse: list[Literal["base", "filtered", "lifetime", "stats", "unhandled"]] | None = Field(None, description="Specify fields to exclude from the response to reduce payload size and improve performance. Provide as a list of field names to omit."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of issues for an organization with optional filtering, search, and pagination. By default, only unresolved issues are returned unless a custom query is provided."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSIssuesRequest(
            path=_models.ListAnOrganizationSIssuesRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.ListAnOrganizationSIssuesRequestQuery(environment=environment, group_stats_period=group_stats_period, query=query, limit=limit, expand=expand, collapse=collapse)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/issues/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/issues/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_issues", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_issues",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def bulk_update_issues(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either its numeric ID or URL slug."),
    inbox: bool = Field(..., description="Mark the issue as reviewed by the requesting user when set to true."),
    status: Literal["resolved", "unresolved", "ignored", "resolvedInNextRelease", "muted"] = Field(..., description="Limit mutations to issues with this status: `resolved`, `unresolved`, `ignored`, `resolvedInNextRelease`, or `muted`."),
    status_details: _models.BulkMutateAnOrganizationSIssuesBodyStatusDetails = Field(..., alias="statusDetails", description="Additional context for the status change, such as release information for resolution details. Release-based updates are restricted to issues within a single project."),
    substatus: Literal["archived_until_escalating", "archived_until_condition_met", "archived_forever", "escalating", "ongoing", "regressed", "new"] | None = Field(..., description="Set the issue substatus to one of: `archived_until_escalating`, `archived_until_condition_met`, `archived_forever`, `escalating`, `ongoing`, `regressed`, or `new`. Omit or set to null to leave unchanged."),
    has_seen: bool = Field(..., alias="hasSeen", description="Mark the issue as seen by the requesting user when set to true."),
    is_bookmarked: bool = Field(..., alias="isBookmarked", description="Bookmark the issue for the requesting user when set to true."),
    is_public: bool = Field(..., alias="isPublic", description="Publish the issue to make it publicly visible when set to true."),
    is_subscribed: bool = Field(..., alias="isSubscribed", description="Subscribe the requesting user to the issue when set to true."),
    merge: bool = Field(..., description="Merge the selected issues together when set to true."),
    discard: bool = Field(..., description="Discard the selected issues instead of updating them when set to true."),
    assigned_to: str = Field(..., alias="assignedTo", description="Assign the issues to a user or team. Specify as `<user_id>`, `user:<user_id>`, `<username>`, `<user_primary_email>`, or `team:<team_id>`."),
    priority: Literal["low", "medium", "high"] = Field(..., description="Set the priority level for the issues: `low`, `medium`, or `high`."),
    environment: list[str] | None = Field(None, description="Filter issues by one or more environment names. Specify as an array of environment identifiers."),
    query: str | None = Field(None, description="Search query to filter issues (e.g., `is:unresolved`). Defaults to `is:unresolved` if not provided; use an empty string to include all results."),
    limit: int | None = Field(None, description="Maximum number of issues to update, up to 100. Defaults to 100."),
) -> dict[str, Any] | ToolResult:
    """Bulk update attributes on up to 1000 issues in an organization. Use the `id` query parameter for non-status updates, or omit it for status updates to match issues by filter criteria. Issues out of scope are silently skipped; returns HTTP 204 if no issues match."""

    # Construct request model with validation
    try:
        _request = _models.BulkMutateAnOrganizationSIssuesRequest(
            path=_models.BulkMutateAnOrganizationSIssuesRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.BulkMutateAnOrganizationSIssuesRequestQuery(environment=environment, query=query, limit=limit),
            body=_models.BulkMutateAnOrganizationSIssuesRequestBody(inbox=inbox, status=status, status_details=status_details, substatus=substatus, has_seen=has_seen, is_bookmarked=is_bookmarked, is_public=is_public, is_subscribed=is_subscribed, merge=merge, discard=discard, assigned_to=assigned_to, priority=priority)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_update_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/issues/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/issues/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_update_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_update_issues", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_update_issues",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def delete_organization_issues(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either its numeric ID or URL slug."),
    environment: list[str] | None = Field(None, description="Filter issues by one or more environment names. Only issues matching all specified environments will be affected."),
    query: str | None = Field(None, description="Search query to filter issues by status, assignee, or other criteria. Defaults to unresolved issues only. Use an empty string to match all issues regardless of status."),
    limit: int | None = Field(None, description="Maximum number of issues to delete in this operation. Capped at 100 issues per request."),
) -> dict[str, Any] | ToolResult:
    """Permanently remove issues from an organization. Specify issues by ID for precise deletion, or use query filters to target multiple issues. Returns success even if no matching issues are found."""

    # Construct request model with validation
    try:
        _request = _models.BulkRemoveAnOrganizationSIssuesRequest(
            path=_models.BulkRemoveAnOrganizationSIssuesRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.BulkRemoveAnOrganizationSIssuesRequestQuery(environment=environment, query=query, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_organization_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/issues/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/issues/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_organization_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_organization_issues", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_organization_issues",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def list_organization_members(organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or a URL-friendly slug.")) -> dict[str, Any] | ToolResult:
    """Retrieve all members of an organization, including pending invitations that have been approved by owners or managers but not yet accepted by invitees."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSMembersRequest(
            path=_models.ListAnOrganizationSMembersRequestPath(organization_id_or_slug=organization_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/members/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/members/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def add_member_to_organization(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or URL-friendly slug."),
    email: str = Field(..., description="Email address of the member to invite. Must be a valid email format with a maximum length of 75 characters.", max_length=75),
    org_role: Literal["billing", "member", "manager", "owner", "admin"] | None = Field(None, alias="orgRole", description="Organization-level role for the new member. Options range from `member` (view and act on events) to `owner` (unrestricted access). Defaults to `member`. Note: `admin` role is deprecated for Business and Enterprise plans."),
    team_roles: list[dict[str, Any]] | None = Field(None, alias="teamRoles", description="Array of team assignments with associated roles. Each entry assigns the member to a team with either `contributor` (view and act on issues) or `admin` (full team management) permissions."),
    send_invite: bool | None = Field(None, alias="sendInvite", description="Whether to send an email invitation notification to the member. Defaults to true."),
    reinvite: bool | None = Field(None, description="Whether to re-invite a member who has already received an invitation to the organization. Defaults to true."),
) -> dict[str, Any] | ToolResult:
    """Add or invite a member to an organization with optional role assignment and team membership. Sends an email invitation by default unless disabled."""

    # Construct request model with validation
    try:
        _request = _models.AddAMemberToAnOrganizationRequest(
            path=_models.AddAMemberToAnOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug),
            body=_models.AddAMemberToAnOrganizationRequestBody(email=email, org_role=org_role, team_roles=team_roles, send_invite=send_invite, reinvite=reinvite)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_member_to_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/members/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/members/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_member_to_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_member_to_organization", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_member_to_organization",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def get_organization_member(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    member_id: str = Field(..., description="The unique identifier of the organization member to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve details for a specific organization member, including pending invite status if the member has been approved by owners or managers but hasn't yet accepted the invitation."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAnOrganizationMemberRequest(
            path=_models.RetrieveAnOrganizationMemberRequestPath(organization_id_or_slug=organization_id_or_slug, member_id=member_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/members/{member_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/members/{member_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_organization_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_organization_member", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_organization_member",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def update_organization_member_roles(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either its numeric ID or URL slug."),
    member_id: str = Field(..., description="The numeric ID of the member whose roles should be updated."),
    org_role: Literal["billing", "member", "manager", "owner", "admin"] | None = Field(None, alias="orgRole", description="The organization-level role to assign. Options range from billing (payment/compliance only) through member, manager, and owner (unrestricted access). The admin role is deprecated for Business and Enterprise plans. You can only assign roles at or below your own permission level."),
    team_roles: list[dict[str, Any]] | None = Field(None, alias="teamRoles", description="Array of team-level role assignments. Each entry specifies a team (by slug) and assigns either contributor (view and act on issues) or admin (full team management) role. Order is not significant. Omit to leave team roles unchanged."),
) -> dict[str, Any] | ToolResult:
    """Update an organization member's roles at both the organization and team levels. Requires user auth tokens and enforces permission hierarchy—you can only assign roles with equal or lower permissions than your own."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAnOrganizationMemberSRolesRequest(
            path=_models.UpdateAnOrganizationMemberSRolesRequestPath(organization_id_or_slug=organization_id_or_slug, member_id=member_id),
            body=_models.UpdateAnOrganizationMemberSRolesRequestBody(org_role=org_role, team_roles=team_roles)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_organization_member_roles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/members/{member_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/members/{member_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_organization_member_roles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_organization_member_roles", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_organization_member_roles",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def delete_organization_member(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    member_id: str = Field(..., description="The unique identifier of the organization member to remove."),
) -> dict[str, Any] | ToolResult:
    """Remove a member from an organization. This operation permanently deletes the member's association with the organization."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnOrganizationMemberRequest(
            path=_models.DeleteAnOrganizationMemberRequestPath(organization_id_or_slug=organization_id_or_slug, member_id=member_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_organization_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/members/{member_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/members/{member_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_organization_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_organization_member", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_organization_member",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def add_member_to_team(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug. Used to scope the operation to a specific organization."),
    member_id: str = Field(..., description="The numeric ID of the organization member to add to the team."),
    team_id_or_slug: str = Field(..., description="The team identifier, either the numeric ID or the URL slug. Identifies which team the member should be added to."),
) -> dict[str, Any] | ToolResult:
    """Add an organization member to a team. The operation returns different success codes based on context: 201 if successfully added, 202 if an access request is generated (pending approval), or 204 if the member is already on the team. Permission requirements vary based on the organization's 'Open Membership' setting and token type."""

    # Construct request model with validation
    try:
        _request = _models.AddAnOrganizationMemberToATeamRequest(
            path=_models.AddAnOrganizationMemberToATeamRequestPath(organization_id_or_slug=organization_id_or_slug, member_id=member_id, team_id_or_slug=team_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_member_to_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/members/{member_id}/teams/{team_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/members/{member_id}/teams/{team_id_or_slug}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_member_to_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_member_to_team", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_member_to_team",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def update_organization_member_team_role(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug."),
    member_id: str = Field(..., description="The numeric ID of the organization member whose team role should be updated."),
    team_id_or_slug: str = Field(..., description="The team identifier, either the numeric ID or the URL slug."),
    team_role: Literal["contributor", "admin"] | None = Field(None, alias="teamRole", description="The team-level role to assign. Choose 'contributor' for view and event action permissions, or 'admin' for full team management including project and membership control. Defaults to 'contributor' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Update an organization member's role within a specific team. The member must already be part of the team. Note that organization admins, managers, and owners automatically receive a minimum team role of admin on all their teams."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAnOrganizationMemberSTeamRoleRequest(
            path=_models.UpdateAnOrganizationMemberSTeamRoleRequestPath(organization_id_or_slug=organization_id_or_slug, member_id=member_id, team_id_or_slug=team_id_or_slug),
            body=_models.UpdateAnOrganizationMemberSTeamRoleRequestBody(team_role=team_role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_organization_member_team_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/members/{member_id}/teams/{team_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/members/{member_id}/teams/{team_id_or_slug}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_organization_member_team_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_organization_member_team_role", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_organization_member_team_role",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def remove_member_from_team(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug of the organization."),
    member_id: str = Field(..., description="The numeric ID of the organization member to remove from the team."),
    team_id_or_slug: str = Field(..., description="The team identifier, either the numeric ID or the URL slug of the team."),
) -> dict[str, Any] | ToolResult:
    """Remove an organization member from a specific team. Requires appropriate authorization scopes; org:read scope can only remove yourself from teams you belong to."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnOrganizationMemberFromATeamRequest(
            path=_models.DeleteAnOrganizationMemberFromATeamRequestPath(organization_id_or_slug=organization_id_or_slug, member_id=member_id, team_id_or_slug=team_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_member_from_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/members/{member_id}/teams/{team_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/members/{member_id}/teams/{team_id_or_slug}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_member_from_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_member_from_team", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_member_from_team",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Crons
@mcp.tool()
async def list_monitors_for_organization(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    environment: list[str] | None = Field(None, description="Filter results to include only monitors from specified environments. Accepts multiple environment names; monitors matching any of the provided environments will be included."),
    owner: str | None = Field(None, description="Filter results to monitors owned by a specific user or team. Use the format `user:id` for individual users or `team:id` for teams. Can be specified multiple times to include monitors from multiple owners."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all monitors for an organization, including their nested environments. Results can be filtered by specific projects or environments, and optionally filtered by monitor owner."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveMonitorsForAnOrganizationRequest(
            path=_models.RetrieveMonitorsForAnOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.RetrieveMonitorsForAnOrganizationRequestQuery(environment=environment, owner=owner)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_monitors_for_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/monitors/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/monitors/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_monitors_for_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_monitors_for_organization", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_monitors_for_organization",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Crons
@mcp.tool()
async def create_monitor(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    project: str = Field(..., description="The project slug that this monitor will be associated with."),
    name: str = Field(..., description="A human-readable name for the monitor (up to 128 characters) used in notifications. If no slug is provided, it will be automatically derived from this name.", max_length=128),
    config: _models.CreateAMonitorBodyConfig = Field(..., description="The monitor configuration object that defines check-in rules, thresholds, and behavior."),
    slug: str | None = Field(None, description="A unique identifier for the monitor within the organization (up to 50 characters). Must start with a letter or underscore and contain only lowercase letters, numbers, hyphens, and underscores. Required for check-in API calls, so changing it later requires updating instrumented code.", max_length=50),
    status: Literal["active", "disabled"] | None = Field(None, description="The operational status of the monitor. Active monitors accept events and count toward quota; disabled monitors do not. Defaults to active."),
    owner: str | None = Field(None, description="The team or user responsible for the monitor, specified as 'user:{user_id}' or 'team:{team_id}'."),
    is_muted: bool | None = Field(None, description="When enabled, prevents the creation of monitor incidents even when check-in failures occur."),
) -> dict[str, Any] | ToolResult:
    """Create a new monitor for uptime or performance tracking within an organization. The monitor will be associated with a specific project and can be configured with custom check-in rules and notification settings."""

    # Construct request model with validation
    try:
        _request = _models.CreateAMonitorRequest(
            path=_models.CreateAMonitorRequestPath(organization_id_or_slug=organization_id_or_slug),
            body=_models.CreateAMonitorRequestBody(project=project, name=name, config=config, slug=slug, status=status, owner=owner, is_muted=is_muted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_monitor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/monitors/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/monitors/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_monitor")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_monitor", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_monitor",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Crons
@mcp.tool()
async def get_monitor(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    monitor_id_or_slug: str = Field(..., description="The monitor identifier, which can be either the numeric ID or the URL-friendly slug of the monitor."),
    environment: list[str] | None = Field(None, description="Optional list of environment names to filter the monitor data by. Specify multiple environments as separate array items."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific monitor, including its configuration, status, and settings."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAMonitorRequest(
            path=_models.RetrieveAMonitorRequestPath(organization_id_or_slug=organization_id_or_slug, monitor_id_or_slug=monitor_id_or_slug),
            query=_models.RetrieveAMonitorRequestQuery(environment=environment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_monitor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/monitors/{monitor_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/monitors/{monitor_id_or_slug}/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_monitor")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_monitor", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_monitor",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Crons
@mcp.tool()
async def update_monitor(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the organization slug."),
    monitor_id_or_slug: str = Field(..., description="The monitor identifier, either the numeric ID or the monitor slug."),
    project: str = Field(..., description="The slug of the project to associate with this monitor."),
    name: str = Field(..., description="A descriptive name for the monitor used in notifications and UI display. Maximum 128 characters. If not provided, the slug will be derived from this name.", max_length=128),
    config: _models.UpdateAMonitorBodyConfig = Field(..., description="The monitor's configuration object defining its behavior, check intervals, and alert thresholds."),
    slug: str | None = Field(None, description="A unique identifier for the monitor within the organization. Must contain only lowercase letters, numbers, hyphens, and underscores, and cannot be purely numeric. Maximum 50 characters. Changing this requires updating any check-in calls that reference it.", max_length=50),
    status: Literal["active", "disabled"] | None = Field(None, description="The operational status of the monitor. Disabled monitors will not process events and do not count toward your monitor quota. Defaults to active."),
    owner: str | None = Field(None, description="The team or user responsible for the monitor, specified as 'user:{user_id}' or 'team:{team_id}'."),
    is_muted: bool | None = Field(None, description="When enabled, prevents the creation of new monitor incidents while keeping the monitor active for check-ins."),
) -> dict[str, Any] | ToolResult:
    """Update an existing monitor's configuration, status, ownership, and notification settings. Changes to the slug will require updates to any instrumented check-in calls referencing the monitor."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAMonitorRequest(
            path=_models.UpdateAMonitorRequestPath(organization_id_or_slug=organization_id_or_slug, monitor_id_or_slug=monitor_id_or_slug),
            body=_models.UpdateAMonitorRequestBody(project=project, name=name, config=config, slug=slug, status=status, owner=owner, is_muted=is_muted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_monitor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/monitors/{monitor_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/monitors/{monitor_id_or_slug}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_monitor")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_monitor", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_monitor",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Crons
@mcp.tool()
async def delete_monitor_or_monitor_environments(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug of the organization."),
    monitor_id_or_slug: str = Field(..., description="The monitor identifier, either the numeric ID or the URL slug of the monitor."),
    environment: list[str] | None = Field(None, description="Optional list of environment names to delete. When specified, only these environments are removed from the monitor rather than deleting the entire monitor. Omit to delete the monitor entirely."),
) -> dict[str, Any] | ToolResult:
    """Delete a monitor or specific monitor environments. If environment names are provided, only those environments are deleted; otherwise, the entire monitor is deleted."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAMonitorOrMonitorEnvironmentsRequest(
            path=_models.DeleteAMonitorOrMonitorEnvironmentsRequestPath(organization_id_or_slug=organization_id_or_slug, monitor_id_or_slug=monitor_id_or_slug),
            query=_models.DeleteAMonitorOrMonitorEnvironmentsRequestQuery(environment=environment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_monitor_or_monitor_environments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/monitors/{monitor_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/monitors/{monitor_id_or_slug}/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_monitor_or_monitor_environments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_monitor_or_monitor_environments", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_monitor_or_monitor_environments",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Crons
@mcp.tool()
async def list_checkins_for_monitor(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    monitor_id_or_slug: str = Field(..., description="The monitor identifier, which can be either the numeric ID or the URL-friendly slug of the monitor within the organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all check-ins recorded for a specific monitor, showing the history of uptime verification events."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveCheckInsForAMonitorRequest(
            path=_models.RetrieveCheckInsForAMonitorRequestPath(organization_id_or_slug=organization_id_or_slug, monitor_id_or_slug=monitor_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_checkins_for_monitor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/monitors/{monitor_id_or_slug}/checkins/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/monitors/{monitor_id_or_slug}/checkins/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_checkins_for_monitor")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_checkins_for_monitor", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_checkins_for_monitor",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Alerts
@mcp.tool()
async def list_spike_protection_notifications(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug."),
    trigger_type: str | None = Field(None, alias="triggerType", description="Filter notifications by trigger type. Currently, only `spike-protection` is supported."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all Spike Protection Notification Actions configured for an organization. These actions notify designated members via services like Slack or email when spike protection is triggered."""

    # Construct request model with validation
    try:
        _request = _models.ListSpikeProtectionNotificationsRequest(
            path=_models.ListSpikeProtectionNotificationsRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.ListSpikeProtectionNotificationsRequestQuery(trigger_type=trigger_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_spike_protection_notifications: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/notifications/actions/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/notifications/actions/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_spike_protection_notifications")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_spike_protection_notifications", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_spike_protection_notifications",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Alerts
@mcp.tool()
async def get_spike_protection_notification_action(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug. Use whichever format you have available."),
    action_id: int = Field(..., description="The numeric identifier of the notification action to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific Spike Protection Notification Action that notifies organization members when spike detection is triggered. This action defines how and which members are alerted through services like Slack or email."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveASpikeProtectionNotificationActionRequest(
            path=_models.RetrieveASpikeProtectionNotificationActionRequestPath(organization_id_or_slug=organization_id_or_slug, action_id=action_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_spike_protection_notification_action: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/notifications/actions/{action_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/notifications/actions/{action_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_spike_protection_notification_action")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_spike_protection_notification_action", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_spike_protection_notification_action",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Mobile Builds
@mcp.tool()
async def get_artifact_install_details(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    artifact_id: str = Field(..., description="The unique identifier of the build artifact for which to retrieve installation details."),
) -> dict[str, Any] | ToolResult:
    """Retrieve installation and distribution details for a preprod artifact, including installability status, install URL, download metrics, and iOS code signing information."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveInstallInfoForAGivenArtifactRequest(
            path=_models.RetrieveInstallInfoForAGivenArtifactRequestPath(organization_id_or_slug=organization_id_or_slug, artifact_id=artifact_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_artifact_install_details: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/preprodartifacts/{artifact_id}/install-details/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/preprodartifacts/{artifact_id}/install-details/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_artifact_install_details")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_artifact_install_details", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_artifact_install_details",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Mobile Builds
@mcp.tool()
async def get_artifact_size_analysis(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    artifact_id: str = Field(..., description="The unique identifier of the build artifact to analyze."),
    base_artifact_id: str | None = Field(None, alias="baseArtifactId", description="Optional artifact ID to use as a baseline for size comparison. If omitted, the system uses the default base artifact from commit comparison."),
) -> dict[str, Any] | ToolResult:
    """Retrieve size analysis results for a build artifact, including download and install size metrics. Optionally compare against a base artifact to see size differences."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveSizeAnalysisResultsForAGivenArtifactRequest(
            path=_models.RetrieveSizeAnalysisResultsForAGivenArtifactRequestPath(organization_id_or_slug=organization_id_or_slug, artifact_id=artifact_id),
            query=_models.RetrieveSizeAnalysisResultsForAGivenArtifactRequestQuery(base_artifact_id=base_artifact_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_artifact_size_analysis: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/preprodartifacts/{artifact_id}/size-analysis/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/preprodartifacts/{artifact_id}/size-analysis/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_artifact_size_analysis")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_artifact_size_analysis", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_artifact_size_analysis",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Prevent
@mcp.tool()
async def list_repositories_for_owner(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL slug. This determines which organization's repositories to query."),
    owner: str = Field(..., description="The owner identifier whose repositories should be retrieved."),
    limit: int | None = Field(None, description="Maximum number of repositories to return per request. Defaults to 20 if not specified."),
    term: str | None = Field(None, description="Optional substring filter to match against repository names using case-sensitive containment matching."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of repositories owned by a specified owner within an organization. Results can be filtered by name substring."""

    # Construct request model with validation
    try:
        _request = _models.RetrievesListOfRepositoriesForAGivenOwnerRequest(
            path=_models.RetrievesListOfRepositoriesForAGivenOwnerRequestPath(organization_id_or_slug=organization_id_or_slug, owner=owner),
            query=_models.RetrievesListOfRepositoriesForAGivenOwnerRequestQuery(limit=limit, term=term)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repositories_for_owner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repositories/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repositories/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repositories_for_owner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repositories_for_owner", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repositories_for_owner",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Prevent
@mcp.tool()
async def get_repository_sync_status(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    owner: str = Field(..., description="The repository owner identifier, typically a username or organization name that owns the repositories being queried."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the synchronization status of repositories for an integrated organization, showing which repositories are currently syncing and their progress."""

    # Construct request model with validation
    try:
        _request = _models.GetsSyncingStatusForRepositoriesForAnIntegratedOrgRequest(
            path=_models.GetsSyncingStatusForRepositoriesForAnIntegratedOrgRequestPath(organization_id_or_slug=organization_id_or_slug, owner=owner)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_sync_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repositories/sync/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repositories/sync/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_sync_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_sync_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_sync_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Prevent
@mcp.tool()
async def sync_repositories_for_owner(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug. This determines which organization's GitHub integration will be used for the sync operation."),
    owner: str = Field(..., description="The GitHub username or organization name that owns the repositories to be synchronized. Only repositories owned by this entity will be synced."),
) -> dict[str, Any] | ToolResult:
    """Synchronizes repositories from a specified owner with an integrated GitHub organization, ensuring the local repository list matches the current state in GitHub."""

    # Construct request model with validation
    try:
        _request = _models.SyncsRepositoriesFromAnIntegratedOrgWithGitHubRequest(
            path=_models.SyncsRepositoriesFromAnIntegratedOrgWithGitHubRequestPath(organization_id_or_slug=organization_id_or_slug, owner=owner)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for sync_repositories_for_owner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repositories/sync/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repositories/sync/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("sync_repositories_for_owner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("sync_repositories_for_owner", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="sync_repositories_for_owner",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Prevent
@mcp.tool()
async def list_repository_tokens_for_owner(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL slug. This determines which organization's tokens to retrieve."),
    owner: str = Field(..., description="The repository owner whose tokens should be listed. Filters results to tokens belonging to this specific owner."),
    limit: int | None = Field(None, description="The maximum number of tokens to return per request. Defaults to 20 if not specified. Use this to control pagination size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of repository tokens for a specified owner within an organization. Use this to view all tokens associated with a particular repository owner."""

    # Construct request model with validation
    try:
        _request = _models.RetrievesAPaginatedListOfRepositoryTokensForAGivenOwnerRequest(
            path=_models.RetrievesAPaginatedListOfRepositoryTokensForAGivenOwnerRequestPath(organization_id_or_slug=organization_id_or_slug, owner=owner),
            query=_models.RetrievesAPaginatedListOfRepositoryTokensForAGivenOwnerRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_tokens_for_owner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repositories/tokens/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repositories/tokens/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_tokens_for_owner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_tokens_for_owner", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_tokens_for_owner",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Prevent
@mcp.tool()
async def get_repository(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    owner: str = Field(..., description="The owner identifier of the repository, typically a user or team name within the organization."),
    repository: str = Field(..., description="The name of the repository to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed metadata for a single repository within an organization, identified by its owner and repository name."""

    # Construct request model with validation
    try:
        _request = _models.RetrievesASingleRepositoryForAGivenOwnerRequest(
            path=_models.RetrievesASingleRepositoryForAGivenOwnerRequestPath(organization_id_or_slug=organization_id_or_slug, owner=owner, repository=repository)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repository/{repository}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repository/{repository}/"
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

# Tags: Prevent
@mcp.tool()
async def list_repository_branches(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    owner: str = Field(..., description="The repository owner's username or identifier."),
    repository: str = Field(..., description="The name of the repository to retrieve branches from."),
    limit: int | None = Field(None, description="Maximum number of branches to return per request; defaults to 20 if not specified."),
    term: str | None = Field(None, description="Optional substring to filter branches by name using case-sensitive contains matching."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of branches for a specified repository, with optional filtering by branch name substring."""

    # Construct request model with validation
    try:
        _request = _models.RetrievesListOfBranchesForAGivenOwnerAndRepositoryRequest(
            path=_models.RetrievesListOfBranchesForAGivenOwnerAndRepositoryRequestPath(organization_id_or_slug=organization_id_or_slug, owner=owner, repository=repository),
            query=_models.RetrievesListOfBranchesForAGivenOwnerAndRepositoryRequestQuery(limit=limit, term=term)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_branches: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repository/{repository}/branches/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repository/{repository}/branches/"
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

# Tags: Prevent
@mcp.tool()
async def list_test_results_for_repository(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    owner: str = Field(..., description="The repository owner or account name."),
    repository: str = Field(..., description="The repository name."),
    filter_by: str | None = Field(None, alias="filterBy", description="Filter results by test category: flaky tests, failed tests, slowest tests, or skipped tests. If omitted, all test results are returned."),
    branch: str | None = Field(None, description="Limit results to a specific branch. If omitted, results from all branches are included."),
    limit: int | None = Field(None, description="Maximum number of results to return per page. Defaults to 20 if not specified."),
    term: str | None = Field(None, description="Filter test results by name substring using case-sensitive contains matching."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of test results for a specific repository, with optional filtering by test status, branch, and name substring matching."""

    # Construct request model with validation
    try:
        _request = _models.RetrievePaginatedListOfTestResultsForRepositoryOwnerAndOrganizationRequest(
            path=_models.RetrievePaginatedListOfTestResultsForRepositoryOwnerAndOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug, owner=owner, repository=repository),
            query=_models.RetrievePaginatedListOfTestResultsForRepositoryOwnerAndOrganizationRequestQuery(filter_by=filter_by, branch=branch, limit=limit, term=term)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_test_results_for_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repository/{repository}/test-results/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repository/{repository}/test-results/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_test_results_for_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_test_results_for_repository", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_test_results_for_repository",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Prevent
@mcp.tool()
async def get_test_results_aggregates_for_repository(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug. This determines which organization's data is accessed."),
    owner: str = Field(..., description="The owner or account name that owns the repository. Used to scope the repository lookup within the organization."),
    repository: str = Field(..., description="The name of the repository for which to retrieve test result metrics."),
    branch: str | None = Field(None, description="Optional branch name to filter results. When omitted, metrics are aggregated across all branches of the repository."),
) -> dict[str, Any] | ToolResult:
    """Retrieves aggregated test result metrics for a specific repository within an organization, with optional filtering by branch. Metrics can be scoped to a particular time period via query parameters."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAggregatedTestResultMetricsForRepositoryOwnerAndOrganizationRequest(
            path=_models.RetrieveAggregatedTestResultMetricsForRepositoryOwnerAndOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug, owner=owner, repository=repository),
            query=_models.RetrieveAggregatedTestResultMetricsForRepositoryOwnerAndOrganizationRequestQuery(branch=branch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_test_results_aggregates_for_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repository/{repository}/test-results-aggregates/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repository/{repository}/test-results-aggregates/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_test_results_aggregates_for_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_test_results_aggregates_for_repository", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_test_results_aggregates_for_repository",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Prevent
@mcp.tool()
async def list_test_suites_for_repository(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    owner: str = Field(..., description="The owner or account name that owns the repository."),
    repository: str = Field(..., description="The name of the repository to retrieve test suites from."),
    term: str | None = Field(None, description="Optional substring to filter test suites by name using case-sensitive contains matching."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all test suites associated with a repository's test results, with optional filtering by name substring."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveTestSuitesBelongingToARepositorySTestResultsRequest(
            path=_models.RetrieveTestSuitesBelongingToARepositorySTestResultsRequestPath(organization_id_or_slug=organization_id_or_slug, owner=owner, repository=repository),
            query=_models.RetrieveTestSuitesBelongingToARepositorySTestResultsRequestQuery(term=term)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_test_suites_for_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repository/{repository}/test-suites/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repository/{repository}/test-suites/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_test_suites_for_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_test_suites_for_repository", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_test_suites_for_repository",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Prevent
@mcp.tool()
async def regenerate_repository_upload_token(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    owner: str = Field(..., description="The owner identifier of the repository, typically a user or organization name."),
    repository: str = Field(..., description="The name of the repository for which to regenerate the upload token."),
) -> dict[str, Any] | ToolResult:
    """Regenerates an existing repository upload token, invalidating the previous token and returning a new one for repository uploads."""

    # Construct request model with validation
    try:
        _request = _models.RegeneratesARepositoryUploadTokenAndReturnsTheNewTokenRequest(
            path=_models.RegeneratesARepositoryUploadTokenAndReturnsTheNewTokenRequestPath(organization_id_or_slug=organization_id_or_slug, owner=owner, repository=repository)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for regenerate_repository_upload_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repository/{repository}/token/regenerate/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/prevent/owner/{owner}/repository/{repository}/token/regenerate/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("regenerate_repository_upload_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("regenerate_repository_upload_token", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="regenerate_repository_upload_token",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def list_organization_client_keys(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either its unique ID or human-readable slug."),
    team: str | None = Field(None, description="Optional filter to retrieve keys only for projects belonging to a specific team, identified by team slug or ID.", min_length=1),
    status: Literal["active", "inactive"] | None = Field(None, description="Optional filter to retrieve keys by their operational status: 'active' for enabled keys or 'inactive' for disabled keys.", min_length=1),
) -> dict[str, Any] | ToolResult:
    """Retrieve all client keys (DSNs) across projects in an organization, with optional filtering by team and key status. Results are paginated for efficient retrieval of large key sets."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSClientKeysRequest(
            path=_models.ListAnOrganizationSClientKeysRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.ListAnOrganizationSClientKeysRequestQuery(team=team, status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_client_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/project-keys/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/project-keys/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_client_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_client_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_client_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def list_organization_projects(organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")) -> dict[str, Any] | ToolResult:
    """Retrieve all projects associated with a specific organization. Returns a list of projects bound to the organization identified by ID or slug."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSProjectsRequest(
            path=_models.ListAnOrganizationSProjectsRequestPath(organization_id_or_slug=organization_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/projects/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/projects/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def create_metric_monitor_for_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or URL slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or URL slug."),
    name: str = Field(..., description="A descriptive name for the monitor. Maximum 200 characters.", max_length=200),
    type_: str = Field(..., alias="type", description="The monitor classification type. Currently supports `metric_issue` for metric-based monitoring."),
    workflow_ids: list[int] | None = Field(None, description="Optional array of alert workflow IDs to automatically connect this monitor to existing alerts. Use the Fetch Alerts endpoint to discover available workflow IDs."),
    data_sources: list[Any] | None = Field(None, description="Array of data source configurations defining what metric to measure. Each source specifies the aggregate function (e.g., count(), p95(span.duration)), dataset (events, events_analytics_platform, or generic_metrics), environment, event types to include, query filters, and time window in seconds. Refer to documentation for metric-specific configurations like error counts, throughput, duration, failure rate, or custom measurements."),
    config: dict[str, Any] | None = Field(None, description="Detection algorithm configuration. Choose `static` for threshold-based alerts, `percent` for change-based detection (requires comparisonDelta in minutes: 300, 900, 3600, 86400, 604800, or 2592000), or `dynamic` for anomaly detection."),
    condition_group: _models.CreateAMonitorForAProjectBodyConditionGroup | None = Field(None, description="Condition group defining when to trigger issue creation and priority assignment. Specify logic type, comparison operators (gt, lte, anomaly_detection), thresholds, and result states (75=high priority, 50=low priority, 0=resolved). For dynamic monitors, configure seasonality, sensitivity (low/medium/high), and threshold direction."),
    owner: str | None = Field(None, description="The owner of this monitor, specified as either a user ID (format: `user:123456`) or team ID (format: `team:456789`)."),
    description: str | None = Field(None, description="Optional descriptive text about the monitor's purpose. This text will be included in any resulting issues created by the monitor."),
    enabled: bool | None = Field(None, description="Set to `false` to create the monitor in a disabled state. Defaults to `true` (enabled)."),
) -> dict[str, Any] | ToolResult:
    """Create a metric-based monitor for a project to detect issues based on error counts, performance metrics, or custom measurements. This beta endpoint supports multiple monitor types including threshold-based, change-based, and dynamic anomaly detection."""

    # Construct request model with validation
    try:
        _request = _models.CreateAMonitorForAProjectRequest(
            path=_models.CreateAMonitorForAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            body=_models.CreateAMonitorForAProjectRequestBody(name=name, type_=type_, workflow_ids=workflow_ids, data_sources=data_sources, config=config, condition_group=condition_group, owner=owner, description=description, enabled=enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_metric_monitor_for_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/projects/{project_id_or_slug}/detectors/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/projects/{project_id_or_slug}/detectors/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_metric_monitor_for_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_metric_monitor_for_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_metric_monitor_for_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def list_organization_trusted_relays(organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")) -> dict[str, Any] | ToolResult:
    """Retrieve a list of all trusted relays configured for an organization. Relays are used to forward events and requests securely within the organization's infrastructure."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSTrustedRelaysRequest(
            path=_models.ListAnOrganizationSTrustedRelaysRequestPath(organization_id_or_slug=organization_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_trusted_relays: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/relay_usage/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/relay_usage/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_trusted_relays")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_trusted_relays", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_trusted_relays",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def list_release_threshold_statuses(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    start: str = Field(..., description="The start of the time range as a UTC datetime in ISO 8601 format or Unix epoch seconds (inclusive)."),
    end: str = Field(..., description="The end of the time range as a UTC datetime in ISO 8601 format or Unix epoch seconds (inclusive). Must be used with `start`."),
    environment: list[str] | None = Field(None, description="Optional list of environment names to filter results. Specify multiple environments as separate array items."),
    release: list[str] | None = Field(None, description="Optional list of release versions to filter results. Specify multiple releases as separate array items."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the health statuses of release thresholds within a specified time range. Returns threshold statuses keyed by release version and project, including full threshold details and derived health indicators. **Note: This is an experimental Alpha API subject to change.**"""

    # Construct request model with validation
    try:
        _request = _models.RetrieveStatusesOfReleaseThresholdsAlphaRequest(
            path=_models.RetrieveStatusesOfReleaseThresholdsAlphaRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.RetrieveStatusesOfReleaseThresholdsAlphaRequestQuery(start=start, end=end, environment=environment, release=release)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_release_threshold_statuses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/release-threshold-statuses/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/release-threshold-statuses/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_release_threshold_statuses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_release_threshold_statuses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_release_threshold_statuses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def get_organization_release(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    version: str = Field(..., description="The version identifier that uniquely identifies the release within the organization."),
    project_id: str | None = Field(None, description="Filter release data to a specific project within the organization."),
    health: bool | None = Field(None, description="Include health metrics and crash data with the release details. Disabled by default."),
    adoption_stages: bool | None = Field(None, alias="adoptionStages", description="Include adoption stage information showing how the release is being adopted across your user base. Disabled by default."),
    summary_stats_period: Literal["14d", "1d", "1h", "24h", "2d", "30d", "48h", "7d", "90d"] | None = Field(None, alias="summaryStatsPeriod", description="Time period for aggregating summary statistics. Defaults to 14 days. Valid periods range from 1 hour to 90 days."),
    health_stats_period: Literal["14d", "1d", "1h", "24h", "2d", "30d", "48h", "7d", "90d"] | None = Field(None, alias="healthStatsPeriod", description="Time period for aggregating health statistics when health data is enabled. Defaults to 24 hours if health is enabled. Valid periods range from 1 hour to 90 days."),
    status: Literal["archived", "open"] | None = Field(None, description="Filter results by release status: archived releases or actively open releases."),
    query: str | None = Field(None, description="Apply advanced filters using query syntax to narrow results by transaction, release, and other attributes. Supports boolean operators (AND, OR) and comma-separated value lists."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific release within an organization, including optional health metrics, adoption stages, and summary statistics."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAnOrganizationSReleaseRequest(
            path=_models.RetrieveAnOrganizationSReleaseRequestPath(organization_id_or_slug=organization_id_or_slug, version=version),
            query=_models.RetrieveAnOrganizationSReleaseRequestQuery(project_id=project_id, health=health, adoption_stages=adoption_stages, summary_stats_period=summary_stats_period, health_stats_period=health_stats_period, status=status, query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization_release: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/releases/{version}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/releases/{version}/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_organization_release")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_organization_release", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_organization_release",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def update_organization_release(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    version: str = Field(..., description="The semantic version string that uniquely identifies the release within the organization."),
    url: str | None = Field(None, description="A URI pointing to the release, such as a GitHub repository URL or deployment interface. Must be a valid URI format."),
    date_released: str | None = Field(None, alias="dateReleased", description="An ISO 8601 formatted date-time indicating when the release was deployed to production. If omitted, the current server time is used."),
    refs: list[_models.UpdateAnOrganizationSReleaseBodyRefsItem] | None = Field(None, description="An array of commit references for each repository in the release. Each entry must include the repository identifier and commit SHA (HEAD). Optionally include the previous commit SHA if this is the first time sending commit data for this repository. Order reflects the sequence of repositories in the release."),
) -> dict[str, Any] | ToolResult:
    """Update release metadata including repository references, deployment URL, and release date. Allows modification of commit information, external links, and timing details for an existing release."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAnOrganizationSReleaseRequest(
            path=_models.UpdateAnOrganizationSReleaseRequestPath(organization_id_or_slug=organization_id_or_slug, version=version),
            body=_models.UpdateAnOrganizationSReleaseRequestBody(url=url, date_released=date_released, refs=refs)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_organization_release: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/releases/{version}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/releases/{version}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_organization_release")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_organization_release", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_organization_release",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def delete_organization_release(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    version: str = Field(..., description="The version string that uniquely identifies the release within the organization."),
) -> dict[str, Any] | ToolResult:
    """Permanently delete a release from an organization, including all associated files and artifacts. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnOrganizationSReleaseRequest(
            path=_models.DeleteAnOrganizationSReleaseRequestPath(organization_id_or_slug=organization_id_or_slug, version=version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_organization_release: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/releases/{version}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/releases/{version}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_organization_release")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_organization_release", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_organization_release",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def list_release_deploys(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    version: str = Field(..., description="The version string that uniquely identifies the release for which to retrieve deployments."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all deployments for a specific release version within an organization. Returns deployment history and status information for the given release."""

    # Construct request model with validation
    try:
        _request = _models.ListAReleaseSDeploysRequest(
            path=_models.ListAReleaseSDeploysRequestPath(organization_id_or_slug=organization_id_or_slug, version=version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_release_deploys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/releases/{version}/deploys/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/releases/{version}/deploys/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_release_deploys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_release_deploys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_release_deploys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def create_deploy_for_release(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    version: str = Field(..., description="The release version identifier to deploy."),
    environment: str = Field(..., description="The target environment for this deployment (e.g., production, staging, development). Limited to 64 characters.", max_length=64),
    name: str | None = Field(None, description="A human-readable name for this deployment. Limited to 64 characters.", max_length=64),
    url: str | None = Field(None, description="A URL pointing to deployment details, logs, or related resources. Must be a valid URI."),
    date_started: str | None = Field(None, alias="dateStarted", description="The timestamp when the deployment began, in ISO 8601 format."),
    date_finished: str | None = Field(None, alias="dateFinished", description="The timestamp when the deployment completed, in ISO 8601 format. Defaults to the current time if not provided."),
    projects: list[str] | None = Field(None, description="A list of project slugs to associate with this deployment. If omitted, the deployment applies to all projects in the release."),
) -> dict[str, Any] | ToolResult:
    """Create a deployment record for a specific release version to a target environment. This tracks when and where a release was deployed, optionally linking it to specific projects."""

    # Construct request model with validation
    try:
        _request = _models.CreateADeployRequest(
            path=_models.CreateADeployRequestPath(organization_id_or_slug=organization_id_or_slug, version=version),
            body=_models.CreateADeployRequestBody(environment=environment, name=name, url=url, date_started=date_started, date_finished=date_finished, projects=projects)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_deploy_for_release: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/releases/{version}/deploys/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/releases/{version}/deploys/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_deploy_for_release")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_deploy_for_release", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_deploy_for_release",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Replays
@mcp.tool()
async def get_replay_count_for_issues_or_transactions(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug of the organization."),
    environment: list[str] | None = Field(None, description="Optional list of environment names to narrow results to specific deployment environments."),
    query: str | None = Field(None, description="Required search query using Sentry query syntax to specify which replays to count. Must include exactly one of: issue.id (for issues), transaction (for transactions), or replay_id (for specific replays). Supports boolean operators and multiple values in bracket notation."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the count of replays associated with specified issues, transactions, or replay IDs within an organization. Use the query parameter to filter by issue ID, transaction name, or replay ID."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveACountOfReplaysForAGivenIssueOrTransactionRequest(
            path=_models.RetrieveACountOfReplaysForAGivenIssueOrTransactionRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.RetrieveACountOfReplaysForAGivenIssueOrTransactionRequestQuery(environment=environment, query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_replay_count_for_issues_or_transactions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/replay-count/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/replay-count/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_replay_count_for_issues_or_transactions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_replay_count_for_issues_or_transactions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_replay_count_for_issues_or_transactions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Replays
@mcp.tool()
async def list_organization_replay_selectors(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    environment: list[str] | None = Field(None, description="Filter selectors by one or more environments. Specify as an array of environment names."),
    per_page: int | None = Field(None, description="Maximum number of results to return per page, up to 100. Defaults to 100 if not specified."),
    query: str | None = Field(None, description="Filter selectors using Sentry's query syntax, supporting logical operators (AND, OR) and field-based conditions like transaction names and release versions."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of replay selectors configured for an organization, with optional filtering by environment, query criteria, and pagination controls."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSSelectorsRequest(
            path=_models.ListAnOrganizationSSelectorsRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.ListAnOrganizationSSelectorsRequestQuery(environment=environment, per_page=per_page, query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_replay_selectors: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/replay-selectors/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/replay-selectors/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_replay_selectors")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_replay_selectors", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_replay_selectors",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Replays
@mcp.tool()
async def list_organization_replays(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    field: list[Literal["activity", "browser", "count_dead_clicks", "count_errors", "count_rage_clicks", "count_segments", "count_urls", "device", "dist", "duration", "environment", "error_ids", "finished_at", "id", "is_archived", "os", "platform", "project_id", "releases", "sdk", "started_at", "tags", "trace_ids", "urls", "user", "clicks", "info_ids", "warning_ids", "count_warnings", "count_infos", "has_viewed"]] | None = Field(None, description="Comma-separated list of specific fields to include in the response. Only valid field names are accepted; invalid fields will cause an error."),
    environment: str | None = Field(None, description="Filter replays by environment name (e.g., production, staging, development). Must be at least 1 character.", min_length=1),
    query: str | None = Field(None, description="A structured query string to filter results (e.g., by user, duration, or other replay attributes). Must be at least 1 character.", min_length=1),
    per_page: int | None = Field(None, description="Maximum number of replays to return per page for pagination."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of session replays for an organization, with optional filtering by environment and structured query parameters."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSReplaysRequest(
            path=_models.ListAnOrganizationSReplaysRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.ListAnOrganizationSReplaysRequestQuery(field=field, environment=environment, query=query, per_page=per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_replays: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/replays/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/replays/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_replays")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_replays", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_replays",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Replays
@mcp.tool()
async def get_replay_instance(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug. Required to scope the replay to the correct organization."),
    replay_id: str = Field(..., description="The unique identifier of the replay to retrieve, formatted as a UUID. This must be a valid UUID string."),
    field: list[Literal["activity", "browser", "count_dead_clicks", "count_errors", "count_rage_clicks", "count_segments", "count_urls", "device", "dist", "duration", "environment", "error_ids", "finished_at", "id", "is_archived", "os", "platform", "project_id", "releases", "sdk", "started_at", "tags", "trace_ids", "urls", "user", "clicks", "info_ids", "warning_ids", "count_warnings", "count_infos", "has_viewed"]] | None = Field(None, description="Optional list of specific fields to include in the response. Only the specified fields will be marshaled in the output; invalid field names will be rejected."),
    environment: str | None = Field(None, description="Optional environment name to filter the replay data. Must be a non-empty string if provided.", min_length=1),
    query: str | None = Field(None, description="Optional structured query string to filter the replay output. Must be a non-empty string if provided and should follow the API's query syntax.", min_length=1),
    per_page: int | None = Field(None, description="Optional limit on the number of rows to return in the result set. Useful for paginating large replay datasets."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific replay session by its ID. Returns comprehensive replay data including metadata, events, and user interactions."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAReplayInstanceRequest(
            path=_models.RetrieveAReplayInstanceRequestPath(organization_id_or_slug=organization_id_or_slug, replay_id=replay_id),
            query=_models.RetrieveAReplayInstanceRequestQuery(field=field, environment=environment, query=query, per_page=per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_replay_instance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/replays/{replay_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/replays/{replay_id}/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_replay_instance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_replay_instance", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_replay_instance",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def list_repository_commits(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL slug of the organization."),
    repo_id: str = Field(..., description="The unique identifier of the repository within the organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of commits for a specific repository within an organization. Use this to view the commit history and details for a given repository."""

    # Construct request model with validation
    try:
        _request = _models.ListARepositorySCommitsRequest(
            path=_models.ListARepositorySCommitsRequestPath(organization_id_or_slug=organization_id_or_slug, repo_id=repo_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_commits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/repos/{repo_id}/commits/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/repos/{repo_id}/commits/"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: SCIM
@mcp.tool()
async def list_organization_teams_scim(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either its numeric ID or URL slug."),
    start_index: int | None = Field(None, alias="startIndex", description="The starting position for pagination using 1-based indexing. Defaults to 1 if not specified.", ge=1),
    filter_: str | None = Field(None, alias="filter", description="A SCIM filter expression to narrow results. Currently supports only equality (`eq`) comparisons.", min_length=1),
    excluded_attributes: list[str] | None = Field(None, alias="excludedAttributes", description="Array of field names to exclude from the response. Currently only `members` is supported for exclusion."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of teams in an organization using SCIM Groups protocol. Note that the members field is capped at 10,000 members per team."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSPaginatedTeamsRequest(
            path=_models.ListAnOrganizationSPaginatedTeamsRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.ListAnOrganizationSPaginatedTeamsRequestQuery(start_index=start_index, filter_=filter_, excluded_attributes=excluded_attributes)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_teams_scim: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/scim/v2/Groups", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/scim/v2/Groups"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_teams_scim")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_teams_scim", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_teams_scim",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: SCIM
@mcp.tool()
async def create_team_in_organization(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    display_name: str = Field(..., alias="displayName", description="The display name for the team as shown in the UI. This will be normalized to a URL-friendly slug format (lowercase, spaces converted to dashes)."),
) -> dict[str, Any] | ToolResult:
    """Create a new team within an organization using SCIM Groups protocol. The team is initialized with an empty member set, and the display name is normalized to lowercase with spaces converted to dashes."""

    # Construct request model with validation
    try:
        _request = _models.ProvisionANewTeamRequest(
            path=_models.ProvisionANewTeamRequestPath(organization_id_or_slug=organization_id_or_slug),
            body=_models.ProvisionANewTeamRequestBody(display_name=display_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_team_in_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/scim/v2/Groups", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/scim/v2/Groups"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_team_in_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_team_in_organization", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_team_in_organization",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: SCIM
@mcp.tool()
async def list_organization_scim_members(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either its numeric ID or URL slug."),
    start_index: int | None = Field(None, alias="startIndex", description="The starting position for pagination using 1-based indexing (defaults to 1 if not specified).", ge=1),
    filter_: str | None = Field(None, alias="filter", description="A SCIM filter expression to refine results; currently supports only equality (`eq`) comparisons.", min_length=1),
    excluded_attributes: list[str] | None = Field(None, alias="excludedAttributes", description="Array of field names to exclude from the response. Currently only `members` is supported for exclusion."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of SCIM-provisioned members in an organization. Use SCIM filter expressions to narrow results or exclude specific attributes from the response."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSScimMembersRequest(
            path=_models.ListAnOrganizationSScimMembersRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.ListAnOrganizationSScimMembersRequestQuery(start_index=start_index, filter_=filter_, excluded_attributes=excluded_attributes)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_scim_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/scim/v2/Users", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/scim/v2/Users"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_scim_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_scim_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_scim_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: SCIM
@mcp.tool()
async def create_organization_member(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or URL-friendly slug."),
    user_name: str = Field(..., alias="userName", description="The email address for the new member, used as the SAML identifier. Must be a valid email format."),
    sentry_org_role: Literal["billing", "member", "manager", "admin"] | None = Field(None, alias="sentryOrgRole", description="The organization role to assign the member. Determines permissions for billing management, event handling, team/project administration, and global integrations. Defaults to the organization's default role if not specified. Options are: billing (payment and compliance), member (events and data viewing), manager (full team and project management), or admin (global integrations and project management)."),
) -> dict[str, Any] | ToolResult:
    """Provision a new organization member via SCIM protocol. The member will be assigned the organization's default role unless a specific role is provided."""

    # Construct request model with validation
    try:
        _request = _models.ProvisionANewOrganizationMemberRequest(
            path=_models.ProvisionANewOrganizationMemberRequestPath(organization_id_or_slug=organization_id_or_slug),
            body=_models.ProvisionANewOrganizationMemberRequestBody(user_name=user_name, sentry_org_role=sentry_org_role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_organization_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/scim/v2/Users", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/scim/v2/Users"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_organization_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_organization_member", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_organization_member",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration
@mcp.tool()
async def list_sentry_apps(organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug. Use the slug for human-readable requests or the ID for programmatic access.")) -> dict[str, Any] | ToolResult:
    """Retrieve all custom integrations (Sentry Apps) created by an organization. This returns the organization's internal integrations that extend Sentry's functionality."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveTheCustomIntegrationsCreatedByAnOrganizationRequest(
            path=_models.RetrieveTheCustomIntegrationsCreatedByAnOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sentry_apps: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/sentry-apps/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/sentry-apps/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sentry_apps")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sentry_apps", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sentry_apps",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def list_release_health_session_statistics(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    field: list[str] = Field(..., description="One or more metrics to retrieve, such as session counts, unique user counts, crash rates, or session duration percentiles. Multiple fields can be requested in a single query."),
    environment: list[str] | None = Field(None, description="Optional list of environment names to filter results by (e.g., production, staging, development). If omitted, all environments are included."),
    per_page: int | None = Field(None, description="Maximum number of result groups to return per request. Useful for pagination when results are large."),
    group_by: list[str] | None = Field(None, alias="groupBy", description="One or more dimensions to group results by, such as project, release, environment, or session status. Grouping affects the maximum number of data points returned (capped at 10,000 total)."),
    include_totals: int | None = Field(None, alias="includeTotals", description="Set to 0 to exclude aggregate totals from the response; defaults to 1 (include totals)."),
    include_series: int | None = Field(None, alias="includeSeries", description="Set to 0 to exclude time series data from the response; defaults to 1 (include series)."),
    query: str | None = Field(None, description="Filter results using Sentry's query syntax to match specific conditions on transactions, releases, and other attributes. Multiple conditions can be combined with AND/OR operators."),
) -> dict[str, Any] | ToolResult:
    """Retrieves time series data for release health session statistics across projects in an organization. Results are aggregated by specified intervals and grouped by optional dimensions, with automatic rounding to align with the selected time interval."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveReleaseHealthSessionStatisticsRequest(
            path=_models.RetrieveReleaseHealthSessionStatisticsRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.RetrieveReleaseHealthSessionStatisticsRequestQuery(field=field, environment=environment, per_page=per_page, group_by=group_by, include_totals=include_totals, include_series=include_series, query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_release_health_session_statistics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/sessions/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/sessions/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_release_health_session_statistics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_release_health_session_statistics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_release_health_session_statistics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def resolve_short_id(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug. This determines which organization's namespace to search within."),
    issue_id: str = Field(..., description="The short ID of the issue to resolve. This is a condensed identifier that maps to a specific issue within the organization."),
) -> dict[str, Any] | ToolResult:
    """Resolve a short issue ID to retrieve the associated project slug and group (issue) details. This allows you to look up full issue information using a condensed identifier."""

    # Construct request model with validation
    try:
        _request = _models.ResolveAShortIdRequest(
            path=_models.ResolveAShortIdRequestPath(organization_id_or_slug=organization_id_or_slug, issue_id=issue_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for resolve_short_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/shortids/{issue_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/shortids/{issue_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("resolve_short_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("resolve_short_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="resolve_short_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def get_organization_events_count_by_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    field: Literal["sum(quantity)", "sum(times_seen)"] = Field(..., description="The aggregation metric to retrieve: `sum(quantity)` returns event counts (or total bytes for attachments), while `sum(times_seen)` returns the number of times events were observed (or unique session counts for sessions, total attachments for attachments).", min_length=1),
    category: Literal["error", "transaction", "attachment", "replays", "profiles"] | None = Field(None, description="Filter results by event category. Note: attachments cannot be combined with other categories as quantity values differ (bytes vs. event counts). Filtering by `error` automatically includes `default` and `security` categories.", min_length=1),
    outcome: Literal["accepted", "filtered", "rate_limited", "invalid", "abuse", "client_discard", "cardinality_limited"] | None = Field(None, description="Filter results by event outcome status, indicating whether events were accepted, filtered, rate-limited, invalid, abused, client-discarded, or cardinality-limited. See Sentry's stats documentation for detailed outcome definitions.", min_length=1),
    reason: str | None = Field(None, description="Filter results by the specific reason an event was filtered or dropped. Provide the reason as a string value.", min_length=1),
    download: bool | None = Field(None, description="If true, download the response as a CSV file instead of JSON."),
) -> dict[str, Any] | ToolResult:
    """Retrieve summarized event counts aggregated by project for an organization. Use this to analyze event volume, filtering by category (errors, transactions, attachments, replays, profiles), outcome status, and other dimensions."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAnOrganizationSEventsCountByProjectRequest(
            path=_models.RetrieveAnOrganizationSEventsCountByProjectRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.RetrieveAnOrganizationSEventsCountByProjectRequestQuery(field=field, category=category, outcome=outcome, reason=reason, download=download)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization_events_count_by_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/stats-summary/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/stats-summary/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_organization_events_count_by_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_organization_events_count_by_project", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_organization_events_count_by_project",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def get_event_counts_for_organization(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    group_by: list[Literal["outcome", "category", "reason", "project"]] = Field(..., alias="groupBy", description="One or more dimensions to group results by (e.g., project, outcome, category). Multiple groupBy parameters can be passed to create multi-dimensional breakdowns. Note: grouping by project may omit rows if the project/interval combination is very large; for large project counts, filter and query individually. Project grouping does not support timeseries intervals and returns aggregated sums instead."),
    field: Literal["sum(quantity)", "sum(times_seen)"] = Field(..., description="The metric to aggregate: `sum(quantity)` counts events (or bytes for attachments), while `sum(times_seen)` counts unique occurrences (sessions for replay data, or attachment count for attachments).", min_length=1),
    category: Literal["error", "transaction", "attachment", "replay", "profile", "profile_duration", "profile_duration_ui", "profile_chunk", "profile_chunk_ui", "monitor"] | None = Field(None, description="Filter results to a specific data category. Each category represents a distinct data type: errors, transactions, file attachments, session replays, performance profiles, profile duration metrics, or cron monitors. Attachment and profile_duration categories cannot be combined with others due to their unique quantity units (bytes and milliseconds respectively).", min_length=1),
    outcome: Literal["accepted", "filtered", "rate_limited", "invalid", "abuse", "client_discard", "cardinality_limited"] | None = Field(None, description="Filter results by event outcome status, indicating whether an event was accepted, rate-limited, filtered, invalid, abused, discarded by client, or subject to cardinality limits. See Sentry documentation for detailed outcome definitions.", min_length=1),
    reason: str | None = Field(None, description="Filter results by the specific reason an event was filtered or dropped. Provide the reason string to narrow results to events rejected for a particular cause.", min_length=1),
    stats_period: str | None = Field(None, alias="statsPeriod", description="This defines the range of the time series, relative to now. The range is given in a `<number><unit>` format. For example `1d` for a one day range. Possible units are `m` for minutes, `h` for hours, `d` for days and `w` for weeks.You must either provide a `statsPeriod`, or a `start` and `end`.", min_length=1),
    interval: str | None = Field(None, description="This is the resolution of the time series, given in the same format as `statsPeriod`. The default resolution is `1h` and the minimum resolution is currently restricted to `1h` as well. Intervals larger than `1d` are not supported, and the interval has to cleanly divide one day.", min_length=1),
    start: str | None = Field(None, description="This defines the start of the time series range as an explicit datetime, either in UTC ISO8601 or epoch seconds.Use along with `end` instead of `statsPeriod`."),
    end: str | None = Field(None, description="This defines the inclusive end of the time series range as an explicit datetime, either in UTC ISO8601 or epoch seconds.Use along with `start` instead of `statsPeriod`."),
    project: list[Any] | None = Field(None, description="The ID of the projects to filter by.\n\nUse `-1` to include all accessible projects."),
) -> dict[str, Any] | ToolResult:
    """Retrieve aggregated event counts for an organization over a specified time period. Query by event type, outcome, and other dimensions using flexible grouping and filtering options."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveEventCountsForAnOrganizationV2Request(
            path=_models.RetrieveEventCountsForAnOrganizationV2RequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.RetrieveEventCountsForAnOrganizationV2RequestQuery(group_by=group_by, field=field, category=category, outcome=outcome, reason=reason, stats_period=stats_period, interval=interval, start=start, end=end, project=project)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_event_counts_for_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/stats_v2/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/stats_v2/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_event_counts_for_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_event_counts_for_organization", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_event_counts_for_organization",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def list_organization_teams(
    organization_id_or_slug: str = Field(..., description="The unique identifier or slug of the organization. Use either the numeric ID or the organization's URL-friendly slug."),
    detailed: str | None = Field(None, description="Set to \"0\" to return team information without including associated project details, reducing response size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of all teams associated with a specific organization. Optionally filter the response to exclude project details for a lighter payload."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSTeamsRequest(
            path=_models.ListAnOrganizationSTeamsRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.ListAnOrganizationSTeamsRequestQuery(detailed=detailed)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_teams: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/teams/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/teams/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_teams")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_teams", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_teams",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def create_team(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either its numeric ID or URL-friendly slug."),
    slug: str | None = Field(None, description="A URL-friendly identifier for the team (lowercase alphanumeric characters, hyphens, and underscores; cannot be purely numeric). Maximum 50 characters. If omitted, it will be automatically generated from the team name.", max_length=50),
) -> dict[str, Any] | ToolResult:
    """Create a new team within an organization. At least one of `name` or `slug` must be provided in the request body."""

    # Construct request model with validation
    try:
        _request = _models.CreateANewTeamRequest(
            path=_models.CreateANewTeamRequestPath(organization_id_or_slug=organization_id_or_slug),
            body=_models.CreateANewTeamRequestBody(slug=slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/teams/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/teams/"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def list_user_teams_in_organization(organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization.")) -> dict[str, Any] | ToolResult:
    """Retrieve all teams within an organization that the authenticated user has access to. This endpoint requires user authentication tokens and is useful for discovering team membership and permissions."""

    # Construct request model with validation
    try:
        _request = _models.ListAUserSTeamsForAnOrganizationRequest(
            path=_models.ListAUserSTeamsForAnOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_teams_in_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/user-teams/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/user-teams/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_teams_in_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_teams_in_organization", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_teams_in_organization",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def list_alerts(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug of the organization."),
    query: str | None = Field(None, description="Optional search query to filter alerts by name, status, or other alert properties."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of alerts for an organization. This endpoint is currently in beta and supports the New Monitors and Alerts feature."""

    # Construct request model with validation
    try:
        _request = _models.FetchAlertsRequest(
            path=_models.FetchAlertsRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.FetchAlertsRequestQuery(query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_alerts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/workflows/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/workflows/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_alerts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_alerts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_alerts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def create_alert_for_organization(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug of the organization."),
    name: str = Field(..., description="A descriptive name for the alert, up to 256 characters in length.", max_length=256),
    enabled: bool | None = Field(None, description="Whether the alert is active and will evaluate conditions. Defaults to enabled if not specified."),
    detector_ids: list[int] | None = Field(None, description="Array of monitor IDs to associate with this alert. Use the Fetch Organization Monitors endpoint to retrieve available monitor IDs."),
    config: dict[str, Any] | None = Field(None, description="Configuration object specifying the evaluation frequency in minutes. Supported values are 0, 5, 10, 30, 60, 180, 720, or 1440 minutes (up to 24 hours)."),
    environment: str | None = Field(None, description="The environment name where the alert will evaluate conditions, such as 'production' or 'staging'."),
    triggers: _models.CreateAnAlertForAnOrganizationBodyTriggers | None = Field(None, description="Trigger conditions that determine when the alert fires. Includes organization ID, logic type (any-short, all, or none), an array of condition objects (first_seen_event, issue_resolved_trigger, reappeared_event, regression_event), and associated actions."),
    action_filters: list[Any] | None = Field(None, description="Array of action filter groups that define conditions and corresponding actions to execute. Each filter group contains a logic type, conditions array (supporting age, assignment, category, frequency, priority, user impact, event count, and attribute matching), and actions array (email, Slack, PagerDuty, Discord, MSTeams, OpsGenie, Azure DevOps, Jira, or GitHub)."),
    owner: str | None = Field(None, description="The user or team who owns this alert, specified as 'user:USER_ID' or 'team:TEAM_ID'."),
) -> dict[str, Any] | ToolResult:
    """Creates a new alert for an organization to monitor issues and trigger notifications based on specified conditions. This endpoint is currently in beta and supports the New Monitors and Alerts system."""

    # Construct request model with validation
    try:
        _request = _models.CreateAnAlertForAnOrganizationRequest(
            path=_models.CreateAnAlertForAnOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug),
            body=_models.CreateAnAlertForAnOrganizationRequestBody(name=name, enabled=enabled, detector_ids=detector_ids, config=config, environment=environment, triggers=triggers, action_filters=action_filters, owner=owner)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_alert_for_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/workflows/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/workflows/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_alert_for_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_alert_for_organization", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_alert_for_organization",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def update_organization_alerts_bulk(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    enabled: bool = Field(..., description="Set to true to enable the selected alerts, or false to disable them."),
    query: str | None = Field(None, description="Optional search query to filter which alerts are affected by this operation. If omitted, the operation applies to all alerts in the organization."),
) -> dict[str, Any] | ToolResult:
    """Bulk enable or disable alerts across an organization, optionally filtered by search query. This beta endpoint supports the New Monitors and Alerts system."""

    # Construct request model with validation
    try:
        _request = _models.MutateAnOrganizationSAlertsRequest(
            path=_models.MutateAnOrganizationSAlertsRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.MutateAnOrganizationSAlertsRequestQuery(query=query),
            body=_models.MutateAnOrganizationSAlertsRequestBody(enabled=enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_organization_alerts_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/workflows/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/workflows/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_organization_alerts_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_organization_alerts_bulk", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_organization_alerts_bulk",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def delete_alerts_bulk(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    query: str | None = Field(None, description="An optional search query to filter which alerts should be deleted. If omitted, the operation applies to all alerts in the organization."),
) -> dict[str, Any] | ToolResult:
    """Bulk delete alerts for an organization, optionally filtered by a search query. This endpoint is currently in beta and supported by New Monitors and Alerts."""

    # Construct request model with validation
    try:
        _request = _models.BulkDeleteAlertsRequest(
            path=_models.BulkDeleteAlertsRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.BulkDeleteAlertsRequestQuery(query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_alerts_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/workflows/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/workflows/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_alerts_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_alerts_bulk", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_alerts_bulk",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def get_alert(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug. This determines which organization's alert you're accessing."),
    workflow_id: int = Field(..., description="The numeric ID of the alert (workflow) to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific alert (workflow) by its ID. This endpoint is part of the New Monitors and Alerts system and is currently in beta."""

    # Construct request model with validation
    try:
        _request = _models.FetchAnAlertRequest(
            path=_models.FetchAnAlertRequestPath(organization_id_or_slug=organization_id_or_slug, workflow_id=workflow_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_alert: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/workflows/{workflow_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/workflows/{workflow_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_alert")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_alert", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_alert",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def update_alert(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    workflow_id: int = Field(..., description="The numeric ID of the alert to update."),
    name: str = Field(..., description="The display name for the alert. Must not exceed 256 characters.", max_length=256),
    enabled: bool | None = Field(None, description="Whether the alert is active and will evaluate conditions. Defaults to true if not specified."),
    detector_ids: list[int] | None = Field(None, description="Array of monitor IDs to associate with this alert. Use the organization monitors endpoint to retrieve available monitor IDs."),
    config: dict[str, Any] | None = Field(None, description="Configuration object specifying the evaluation frequency in minutes. Supported values are 0, 5, 10, 30, 60, 180, 720, or 1440 minutes."),
    environment: str | None = Field(None, description="The environment name where this alert will evaluate conditions. Filters alert evaluation to a specific environment."),
    triggers: _models.UpdateAnAlertByIdBodyTriggers | None = Field(None, description="Trigger conditions that determine when the alert fires. Supports event-based triggers (first_seen_event, reappeared_event, regression_event, issue_resolved_trigger) with configurable logic type (any-short, all, none) and optional actions."),
    action_filters: list[Any] | None = Field(None, description="Array of action filter groups that define conditions and corresponding notification actions. Each filter group contains a logic type, conditions array, and actions array specifying email, Slack, PagerDuty, Discord, MSTeams, OpsGenie, Azure DevOps, Jira, or GitHub integrations."),
    owner: str | None = Field(None, description="The owner of the alert, specified as either 'user:USER_ID' or 'team:TEAM_ID' to indicate individual or team ownership."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing alert configuration including its name, enabled status, trigger conditions, action filters, and connected monitors. This endpoint supports the New Monitors and Alerts system and is currently in beta."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAnAlertByIdRequest(
            path=_models.UpdateAnAlertByIdRequestPath(organization_id_or_slug=organization_id_or_slug, workflow_id=workflow_id),
            body=_models.UpdateAnAlertByIdRequestBody(name=name, enabled=enabled, detector_ids=detector_ids, config=config, environment=environment, triggers=triggers, action_filters=action_filters, owner=owner)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_alert: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/workflows/{workflow_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/workflows/{workflow_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_alert")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_alert", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_alert",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def delete_alert(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    workflow_id: int = Field(..., description="The numeric ID of the alert to delete."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes an alert from a workflow. This endpoint is currently in beta and supported by New Monitors and Alerts."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnAlertRequest(
            path=_models.DeleteAnAlertRequestPath(organization_id_or_slug=organization_id_or_slug, workflow_id=workflow_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_alert: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/workflows/{workflow_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/workflows/{workflow_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_alert")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_alert", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_alert",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def get_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific project, including its configuration, settings, and metadata."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAProjectRequest(
            path=_models.RetrieveAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/"
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
@mcp.tool()
async def update_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either its numeric ID or URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either its numeric ID or URL-friendly slug."),
    is_bookmarked: bool | None = Field(None, alias="isBookmarked", description="Star or unstar the project in the projects tab. Updatable with project:read permission."),
    name: str | None = Field(None, description="The display name for the project. Must not exceed 200 characters.", max_length=200),
    slug: str | None = Field(None, description="A URL-friendly identifier for the project used in the interface. Must be 1-100 characters, contain only lowercase letters, numbers, hyphens, and underscores, and cannot be purely numeric.", max_length=100),
    platform: str | None = Field(None, description="The platform or technology stack associated with the project (e.g., 'javascript', 'python', 'java')."),
    subject_prefix: str | None = Field(None, alias="subjectPrefix", description="A custom prefix prepended to email subjects for alerts from this project. Must not exceed 200 characters.", max_length=200),
    subject_template: str | None = Field(None, alias="subjectTemplate", description="The email subject template for individual alerts, supporting variables like $title, $shortID, $projectID, $orgID, and tag references (e.g., ${tag:environment}). Must not exceed 200 characters.", max_length=200),
    resolve_age: int | None = Field(None, alias="resolveAge", description="Hours of inactivity after which issues are automatically resolved. Set to 0 to disable auto-resolution."),
    scm_source_context_enabled: bool | None = Field(None, alias="scmSourceContextEnabled", description="Enable automatic source context retrieval from configured SCM integrations to enrich stack traces with code snippets."),
) -> dict[str, Any] | ToolResult:
    """Update project settings, metadata, and configuration options. Most settings require elevated permissions; only bookmarking and preprod-related automation settings can be modified with basic project:read access."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAProjectRequest(
            path=_models.UpdateAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            body=_models.UpdateAProjectRequestBody(is_bookmarked=is_bookmarked, name=name, slug=slug, platform=platform, subject_prefix=subject_prefix, subject_template=subject_template, resolve_age=resolve_age, scm_source_context_enabled=scm_source_context_enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def delete_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, which can be either the numeric ID or the URL slug of the project to be deleted."),
) -> dict[str, Any] | ToolResult:
    """Schedules a project for deletion. The deletion process is asynchronous, so the project won't be immediately removed, but its state will change and it will be hidden from most public views once deletion begins."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAProjectRequest(
            path=_models.DeleteAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/"
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

# Tags: Environments
@mcp.tool()
async def list_project_environments(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either its unique ID or URL-friendly slug. Required to scope the project within the correct organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, either its unique ID or URL-friendly slug. Required to specify which project's environments to list."),
    visibility: Literal["all", "hidden", "visible"] | None = Field(None, description="Filter environments by their visibility status. Choose 'visible' to show only active environments, 'hidden' to show only inactive ones, or 'all' to include both. Defaults to 'visible' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all environments configured for a specific project, with optional filtering by visibility status. Useful for discovering available deployment targets and their configurations."""

    # Construct request model with validation
    try:
        _request = _models.ListAProjectSEnvironmentsRequest(
            path=_models.ListAProjectSEnvironmentsRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            query=_models.ListAProjectSEnvironmentsRequestQuery(visibility=visibility)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_environments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/environments/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/environments/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_environments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_environments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_environments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def get_project_environment(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project."),
    environment: str = Field(..., description="The name of the environment to retrieve (e.g., 'production', 'staging', 'development')."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific environment within a project, including its configuration and settings."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAProjectEnvironmentRequest(
            path=_models.RetrieveAProjectEnvironmentRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, environment=environment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/environments/{environment}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/environments/{environment}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_environment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_environment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_environment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def update_project_environment_visibility(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug."),
    environment: str = Field(..., description="The name of the environment to update (e.g., 'production', 'staging', 'development')."),
    is_hidden: bool = Field(..., alias="isHidden", description="Set to `true` to make the environment visible, or `false` to hide it from the project's environment list."),
) -> dict[str, Any] | ToolResult:
    """Update the visibility status of a project environment, allowing you to show or hide it from the project's environment list."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAProjectEnvironmentRequest(
            path=_models.UpdateAProjectEnvironmentRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, environment=environment),
            body=_models.UpdateAProjectEnvironmentRequestBody(is_hidden=is_hidden)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project_environment_visibility: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/environments/{environment}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/environments/{environment}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project_environment_visibility")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project_environment_visibility", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project_environment_visibility",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def list_project_error_events(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug."),
    full: bool | None = Field(None, description="Include the complete event payload with stacktraces and additional details. Defaults to false for a lighter response."),
    sample: bool | None = Field(None, description="Return events in a deterministic pseudo-random order. Identical queries will always return the same events in the same order. Defaults to false for chronological ordering."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of error events for a specific project. Optionally include full event details such as stacktraces, and control result ordering."""

    # Construct request model with validation
    try:
        _request = _models.ListAProjectSErrorEventsRequest(
            path=_models.ListAProjectSErrorEventsRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            query=_models.ListAProjectSErrorEventsRequestQuery(full=full, sample=sample)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_error_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/events/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/events/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_error_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_error_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_error_events",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def get_source_map_debug_for_event(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug."),
    event_id: str = Field(..., description="The event identifier as a UUID that uniquely identifies the error event to debug."),
    frame_idx: int = Field(..., description="The zero-based index of the stack frame within the exception to analyze for source map resolution issues."),
    exception_idx: int = Field(..., description="The zero-based index of the exception within the event's exception chain to analyze for source map resolution issues."),
) -> dict[str, Any] | ToolResult:
    """Retrieve source map resolution errors for a specific stack frame and exception within an event, helping diagnose why source maps failed to map minified code back to original sources."""

    # Construct request model with validation
    try:
        _request = _models.DebugIssuesRelatedToSourceMapsForAGivenEventRequest(
            path=_models.DebugIssuesRelatedToSourceMapsForAGivenEventRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, event_id=event_id),
            query=_models.DebugIssuesRelatedToSourceMapsForAGivenEventRequestQuery(frame_idx=frame_idx, exception_idx=exception_idx)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_source_map_debug_for_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/events/{event_id}/source-map-debug/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/events/{event_id}/source-map-debug/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_source_map_debug_for_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_source_map_debug_for_event", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_source_map_debug_for_event",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_project_filters(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all filters configured for a specific project. Filters can be active as either boolean flags or legacy browser filter lists."""

    # Construct request model with validation
    try:
        _request = _models.ListAProjectSDataFiltersRequest(
            path=_models.ListAProjectSDataFiltersRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_filters: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/filters/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/filters/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_filters")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_filters", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_filters",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def update_inbound_data_filter(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either as a numeric ID or URL-friendly slug."),
    filter_id: str = Field(..., description="The type of inbound filter to update: browser-extensions (blocks extension-caused errors), localhost (blocks 127.0.0.1 and ::1 traffic), filtered-transaction (blocks health checks and pings), web-crawlers (blocks known crawler errors), or legacy-browser (blocks errors from outdated browsers)."),
    active: bool | None = Field(None, description="Set to true to enable the filter or false to disable it. Controls whether the specified filter actively blocks matching events."),
) -> dict[str, Any] | ToolResult:
    """Enable or disable a specific inbound data filter for a project to control which events are captured and processed. Filters can target browser extensions, localhost traffic, health check transactions, web crawlers, and legacy browser errors."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAnInboundDataFilterRequest(
            path=_models.UpdateAnInboundDataFilterRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, filter_id=filter_id),
            body=_models.UpdateAnInboundDataFilterRequestBody(active=active)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_inbound_data_filter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/filters/{filter_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/filters/{filter_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_inbound_data_filter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_inbound_data_filter", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_inbound_data_filter",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_project_client_keys(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug."),
    status: str | None = Field(None, description="Filter results to show only active or inactive client keys. If omitted, all keys are returned regardless of status."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all client keys associated with a project. Optionally filter by active or inactive status to manage project authentication credentials."""

    # Construct request model with validation
    try:
        _request = _models.ListAProjectSClientKeysRequest(
            path=_models.ListAProjectSClientKeysRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            query=_models.ListAProjectSClientKeysRequestQuery(status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_client_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/keys/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/keys/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_client_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_client_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_client_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def create_project_client_key(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or URL-friendly slug."),
    name: str | None = Field(None, description="A human-readable name for the key (up to 64 characters). If omitted, the server will auto-generate a name.", max_length=64),
    use_case: Literal["user", "profiling", "tempest", "demo"] | None = Field(None, alias="useCase", description="The intended use case for this key: `user` for standard client integration, `profiling` for performance profiling, `tempest` for testing, or `demo` for demonstration purposes. Defaults to `user` if not specified."),
) -> dict[str, Any] | ToolResult:
    """Generate a new client key for a project with server-generated secret and public key credentials. Use this to create authentication keys for integrating with the project."""

    # Construct request model with validation
    try:
        _request = _models.CreateANewClientKeyRequest(
            path=_models.CreateANewClientKeyRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            body=_models.CreateANewClientKeyRequestBody(name=name, use_case=use_case)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project_client_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/keys/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/keys/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_project_client_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_project_client_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_project_client_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def get_client_key(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization."),
    key_id: str = Field(..., description="The unique identifier of the client key to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific client key associated with a project. Returns the key details including its configuration and status."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAClientKeyRequest(
            path=_models.RetrieveAClientKeyRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, key_id=key_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_client_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/keys/{key_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/keys/{key_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_client_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_client_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_client_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def update_client_key(
    organization_id_or_slug: str = Field(..., description="The ID or slug of the organization that owns the project containing this client key."),
    project_id_or_slug: str = Field(..., description="The ID or slug of the project that contains this client key."),
    key_id: str = Field(..., description="The unique identifier of the client key to update."),
    name: str | None = Field(None, description="A human-readable name for the client key to help identify its purpose or associated application."),
    is_active: bool | None = Field(None, alias="isActive", description="Enable or disable the client key; when deactivated, the key will not accept new events."),
    browser_sdk_version: Literal["latest", "7.x"] | None = Field(None, alias="browserSdkVersion", description="The Sentry JavaScript SDK version to use with this key. Choose 'latest' for the most recent version or '7.x' for version 7 releases."),
    has_replay: bool | None = Field(None, alias="hasReplay", description="Enable or disable session replay capture for events sent with this key."),
    has_performance: bool | None = Field(None, alias="hasPerformance", description="Enable or disable performance monitoring and transaction tracking for events sent with this key."),
    has_debug: bool | None = Field(None, alias="hasDebug", description="Enable or disable debug mode to include additional diagnostic information in events sent with this key."),
    has_feedback: bool | None = Field(None, alias="hasFeedback", description="Enable or disable user feedback collection for events sent with this key."),
    has_logs_and_metrics: bool | None = Field(None, alias="hasLogsAndMetrics", description="Enable or disable logs and metrics collection for events sent with this key."),
) -> dict[str, Any] | ToolResult:
    """Update configuration settings for a client key, including its name, activation status, SDK version, and feature flags for replay, performance monitoring, debug mode, feedback, and logs/metrics collection."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAClientKeyRequest(
            path=_models.UpdateAClientKeyRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, key_id=key_id),
            body=_models.UpdateAClientKeyRequestBody(name=name, is_active=is_active, browser_sdk_version=browser_sdk_version,
                dynamic_sdk_loader_options=_models.UpdateAClientKeyRequestBodyDynamicSdkLoaderOptions(has_replay=has_replay, has_performance=has_performance, has_debug=has_debug, has_feedback=has_feedback, has_logs_and_metrics=has_logs_and_metrics) if any(v is not None for v in [has_replay, has_performance, has_debug, has_feedback, has_logs_and_metrics]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_client_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/keys/{key_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/keys/{key_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_client_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_client_key", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_client_key",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def delete_client_key(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug."),
    key_id: str = Field(..., description="The unique identifier of the client key to be deleted."),
) -> dict[str, Any] | ToolResult:
    """Permanently delete a client key from a project. This action cannot be undone and will invalidate the key for authentication."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAClientKeyRequest(
            path=_models.DeleteAClientKeyRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, key_id=key_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_client_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/keys/{key_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/keys/{key_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_client_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_client_key", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_client_key",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_project_members(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all active organization members who are assigned to at least one team associated with the specified project."""

    # Construct request model with validation
    try:
        _request = _models.ListAProjectSOrganizationMembersRequest(
            path=_models.ListAProjectSOrganizationMembersRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/members/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/members/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Crons
@mcp.tool()
async def get_monitor_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization."),
    monitor_id_or_slug: str = Field(..., description="The monitor identifier, which can be either the numeric ID or the URL-friendly slug uniquely identifying the monitor within the project."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific monitor within a project, including its configuration, status, and alert rules."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAMonitorForAProjectRequest(
            path=_models.RetrieveAMonitorForAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, monitor_id_or_slug=monitor_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_monitor_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/monitors/{monitor_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/monitors/{monitor_id_or_slug}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_monitor_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_monitor_project", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_monitor_project",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Crons
@mcp.tool()
async def update_monitor_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or URL-friendly slug."),
    monitor_id_or_slug: str = Field(..., description="The monitor identifier, either the numeric ID or URL-friendly slug."),
    project: str = Field(..., description="The project slug to associate this monitor with."),
    name: str = Field(..., description="Display name for the monitor used in notifications and UI. Maximum 128 characters. If not provided, the slug will be auto-derived from this name.", max_length=128),
    config: _models.UpdateAMonitorForAProjectBodyConfig = Field(..., description="The monitor's configuration object defining its behavior, thresholds, and check-in expectations."),
    slug: str | None = Field(None, description="Unique identifier for the monitor within the organization. Must start with a letter or underscore, contain only lowercase letters, numbers, hyphens, and underscores, and not exceed 50 characters. Changing this requires updating any check-in calls that reference it.", max_length=50),
    status: Literal["active", "disabled"] | None = Field(None, description="Current operational state of the monitor. Disabled monitors will not accept events and do not count toward quota limits. Defaults to active."),
    owner: str | None = Field(None, description="The team or user responsible for this monitor, specified as 'user:{user_id}' or 'team:{team_id}'."),
    is_muted: bool | None = Field(None, description="When enabled, prevents the creation of new monitor incidents while keeping the monitor active."),
) -> dict[str, Any] | ToolResult:
    """Update an existing monitor's configuration, name, status, and ownership settings. Changes to the monitor slug will require updates to any instrumented check-in calls referencing the old slug."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAMonitorForAProjectRequest(
            path=_models.UpdateAMonitorForAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, monitor_id_or_slug=monitor_id_or_slug),
            body=_models.UpdateAMonitorForAProjectRequestBody(project=project, name=name, config=config, slug=slug, status=status, owner=owner, is_muted=is_muted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_monitor_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/monitors/{monitor_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/monitors/{monitor_id_or_slug}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_monitor_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_monitor_project", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_monitor_project",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Crons
@mcp.tool()
async def delete_monitor_for_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug."),
    monitor_id_or_slug: str = Field(..., description="The monitor identifier, either the numeric ID or the URL-friendly slug."),
    environment: list[str] | None = Field(None, description="Optional list of environment names to delete. When provided, only the specified environments are removed from the monitor; when omitted, the entire monitor is deleted."),
) -> dict[str, Any] | ToolResult:
    """Delete a monitor or specific monitor environments within a project. Optionally target specific environments for deletion; if no environments are specified, the entire monitor is deleted."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAMonitorOrMonitorEnvironmentsForAProjectRequest(
            path=_models.DeleteAMonitorOrMonitorEnvironmentsForAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, monitor_id_or_slug=monitor_id_or_slug),
            query=_models.DeleteAMonitorOrMonitorEnvironmentsForAProjectRequestQuery(environment=environment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_monitor_for_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/monitors/{monitor_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/monitors/{monitor_id_or_slug}/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_monitor_for_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_monitor_for_project", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_monitor_for_project",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Crons
@mcp.tool()
async def list_checkins_for_monitor_in_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug. This scopes the request to a specific organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug. This scopes the request to a specific project within the organization."),
    monitor_id_or_slug: str = Field(..., description="The monitor identifier, either the numeric ID or the URL-friendly slug. This specifies which monitor's check-ins to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all check-ins recorded for a specific monitor within a project. Check-ins represent heartbeat or status update events tracked by the monitor."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveCheckInsForAMonitorByProjectRequest(
            path=_models.RetrieveCheckInsForAMonitorByProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, monitor_id_or_slug=monitor_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_checkins_for_monitor_in_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/monitors/{monitor_id_or_slug}/checkins/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/monitors/{monitor_id_or_slug}/checkins/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_checkins_for_monitor_in_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_checkins_for_monitor_in_project", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_checkins_for_monitor_in_project",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def get_project_ownership_configuration(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, which can be either the numeric ID or the URL slug of the project within the organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the ownership configuration for a project, including details about code ownership rules and assignments."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveOwnershipConfigurationForAProjectRequest(
            path=_models.RetrieveOwnershipConfigurationForAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_ownership_configuration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/ownership/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/ownership/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_ownership_configuration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_ownership_configuration", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_ownership_configuration",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def update_project_ownership_configuration(
    organization_id_or_slug: str = Field(..., description="The ID or slug of the organization that owns the project."),
    project_id_or_slug: str = Field(..., description="The ID or slug of the project whose ownership configuration will be updated."),
    raw: str | None = Field(None, description="Raw ownership rules configuration in the format specified by the Ownership Rules documentation. This defines which team members or groups own specific code paths or issue types."),
    fallthrough: bool | None = Field(None, description="Determines ownership assignment when no ownership rule matches. When true, all project members become owners; when false, no owners are assigned for unmatched cases."),
    auto_assignment: str | None = Field(None, alias="autoAssignment", description="Configures automatic issue assignment behavior. Choose from: auto-assign to the issue creator, auto-assign based on suspect commits from version control, or disable auto-assignment entirely."),
    codeowners_auto_sync: bool | None = Field(None, alias="codeownersAutoSync", description="When enabled, automatically syncs issue owners with updates to the CODEOWNERS file in releases. Defaults to true."),
) -> dict[str, Any] | ToolResult:
    """Updates ownership configurations for a project, including rules, fallthrough behavior, auto-assignment settings, and CODEOWNERS synchronization. Only submitted attributes are modified."""

    # Construct request model with validation
    try:
        _request = _models.UpdateOwnershipConfigurationForAProjectRequest(
            path=_models.UpdateOwnershipConfigurationForAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            body=_models.UpdateOwnershipConfigurationForAProjectRequestBody(raw=raw, fallthrough=fallthrough, auto_assignment=auto_assignment, codeowners_auto_sync=codeowners_auto_sync)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project_ownership_configuration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/ownership/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/ownership/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project_ownership_configuration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project_ownership_configuration", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project_ownership_configuration",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Mobile Builds
@mcp.tool()
async def get_latest_installable_build(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either as a numeric ID or URL-friendly slug."),
    app_id: str = Field(..., alias="appId", description="The application identifier to match exactly against available builds."),
    platform: str = Field(..., description="The target platform for the build: either 'apple' for iOS or 'android' for Android."),
    build_version: str | None = Field(None, alias="buildVersion", description="The current build version installed on the device. When provided, the response includes the current build details and indicates whether an update is available."),
    build_configuration: str | None = Field(None, alias="buildConfiguration", description="Filter results to a specific build configuration by exact name match (e.g., 'debug', 'release')."),
    codesigning_type: str | None = Field(None, alias="codesigningType", description="Filter results by code signing type to match your app's signing configuration."),
    install_groups: list[str] | None = Field(None, alias="installGroups", description="Filter results to one or more install groups by name. Specify multiple times to include builds from multiple groups."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the latest installable build for a project matching the specified criteria. Optionally check for available updates by providing the current build version."""

    # Construct request model with validation
    try:
        _request = _models.GetTheLatestInstallableBuildForAProjectRequest(
            path=_models.GetTheLatestInstallableBuildForAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            query=_models.GetTheLatestInstallableBuildForAProjectRequestQuery(app_id=app_id, platform=platform, build_version=build_version, build_configuration=build_configuration, codesigning_type=codesigning_type, install_groups=install_groups)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_latest_installable_build: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/preprodartifacts/build-distribution/latest/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/preprodartifacts/build-distribution/latest/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_latest_installable_build")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_latest_installable_build", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_latest_installable_build",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Replays
@mcp.tool()
async def delete_replay(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug."),
    replay_id: str = Field(..., description="The unique identifier (UUID) of the replay to delete."),
) -> dict[str, Any] | ToolResult:
    """Permanently delete a replay instance from a project. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAReplayInstanceRequest(
            path=_models.DeleteAReplayInstanceRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, replay_id=replay_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_replay: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/replays/{replay_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/replays/{replay_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_replay")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_replay", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_replay",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Replays
@mcp.tool()
async def list_clicked_nodes(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either its unique ID or URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either its unique ID or URL-friendly slug."),
    replay_id: str = Field(..., description="The unique identifier (UUID format) of the replay session to retrieve click data from."),
    environment: list[str] | None = Field(None, description="Filter results to include only clicks from sessions in specified environments. Provide as a list of environment names."),
    per_page: int | None = Field(None, description="Limit the number of results returned. Maximum allowed is 100 (default)."),
    query: str | None = Field(None, description="Filter results using Sentry's query syntax to narrow down clicks by transaction, release, or other attributes. Supports boolean operators (AND, OR) and comma-separated value lists."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all DOM nodes that were clicked during a session replay, including their RRWeb node IDs and exact click timestamps. Use this to understand user interaction patterns within a specific replay."""

    # Construct request model with validation
    try:
        _request = _models.ListClickedNodesRequest(
            path=_models.ListClickedNodesRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, replay_id=replay_id),
            query=_models.ListClickedNodesRequestQuery(environment=environment, per_page=per_page, query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_clicked_nodes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/replays/{replay_id}/clicks/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/replays/{replay_id}/clicks/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_clicked_nodes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_clicked_nodes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_clicked_nodes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Replays
@mcp.tool()
async def list_replay_recording_segments(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either as a numeric ID or URL-friendly slug."),
    replay_id: str = Field(..., description="The unique identifier (UUID) of the replay session whose recording segments you want to retrieve."),
    per_page: int | None = Field(None, description="Maximum number of segments to return per request. Defaults to 100 and cannot exceed 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all recording segments for a specific replay session. Recording segments contain the captured user interaction data that makes up a replay."""

    # Construct request model with validation
    try:
        _request = _models.ListRecordingSegmentsRequest(
            path=_models.ListRecordingSegmentsRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, replay_id=replay_id),
            query=_models.ListRecordingSegmentsRequestQuery(per_page=per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_replay_recording_segments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/replays/{replay_id}/recording-segments/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/replays/{replay_id}/recording-segments/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_replay_recording_segments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_replay_recording_segments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_replay_recording_segments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Replays
@mcp.tool()
async def get_recording_segment(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug. This determines which organization's resources are accessed."),
    project_id_or_slug: str = Field(..., description="The project identifier, either as a numeric ID or URL-friendly slug. This determines which project within the organization contains the replay."),
    replay_id: str = Field(..., description="The unique identifier of the replay session, formatted as a UUID. This identifies which replay the segment belongs to."),
    segment_id: int = Field(..., description="The numeric identifier of the recording segment within the replay. Segments are indexed sequentially and represent discrete portions of the replay recording."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific recording segment from a replay session. Recording segments contain the captured user interaction data for a portion of the replay."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveARecordingSegmentRequest(
            path=_models.RetrieveARecordingSegmentRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, replay_id=replay_id, segment_id=segment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_recording_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/replays/{replay_id}/recording-segments/{segment_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/replays/{replay_id}/recording-segments/{segment_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_recording_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_recording_segment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_recording_segment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Replays
@mcp.tool()
async def list_users_who_viewed_replay(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug. Used to scope the resource within your organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, either as a numeric ID or URL-friendly slug. Used to scope the replay within a specific project."),
    replay_id: str = Field(..., description="The unique identifier of the replay in UUID format. Specifies which replay's viewers you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of users who have viewed a specific replay within a project. Useful for understanding replay engagement and visibility."""

    # Construct request model with validation
    try:
        _request = _models.ListUsersWhoHaveViewedAReplayRequest(
            path=_models.ListUsersWhoHaveViewedAReplayRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, replay_id=replay_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_users_who_viewed_replay: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/replays/{replay_id}/viewed-by/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/replays/{replay_id}/viewed-by/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_users_who_viewed_replay")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_users_who_viewed_replay", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_users_who_viewed_replay",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Replays
@mcp.tool()
async def list_replay_deletion_jobs(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug. This scopes the request to a specific organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug. This scopes the request to a specific project within the organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of all replay deletion jobs for a project. Use this to monitor the status and history of bulk replay deletion operations."""

    # Construct request model with validation
    try:
        _request = _models.ListReplayBatchDeletionJobsRequest(
            path=_models.ListReplayBatchDeletionJobsRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_replay_deletion_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/replays/jobs/delete/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/replays/jobs/delete/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_replay_deletion_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_replay_deletion_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_replay_deletion_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Replays
@mcp.tool()
async def create_replay_deletion_job(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL slug of the project."),
    range_start: str = Field(..., alias="rangeStart", description="The start of the time range for replay deletion, specified as an ISO 8601 formatted datetime string (inclusive)."),
    range_end: str = Field(..., alias="rangeEnd", description="The end of the time range for replay deletion, specified as an ISO 8601 formatted datetime string (inclusive)."),
    environments: list[str] = Field(..., description="A list of environment names to filter replays for deletion. Only replays from these environments will be included in the job."),
    query: str | None = Field(..., description="A search query string to further filter which replays should be deleted. The query uses the same syntax as replay search filters."),
) -> dict[str, Any] | ToolResult:
    """Create a new batch job to delete replays matching specified criteria. The job will process replays within the given time range, environments, and query filters."""

    # Construct request model with validation
    try:
        _request = _models.CreateReplayBatchDeletionJobRequest(
            path=_models.CreateReplayBatchDeletionJobRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            body=_models.CreateReplayBatchDeletionJobRequestBody(data=_models.CreateReplayBatchDeletionJobRequestBodyData(range_start=range_start, range_end=range_end, environments=environments, query=query))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_replay_deletion_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/replays/jobs/delete/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/replays/jobs/delete/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_replay_deletion_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_replay_deletion_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_replay_deletion_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Replays
@mcp.tool()
async def get_replay_deletion_job(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug. This scopes the request to a specific organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug. This scopes the request to a specific project within the organization."),
    job_id: int = Field(..., description="The unique identifier of the replay deletion job. This must be a positive integer representing the specific job you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the status and details of a specific replay batch deletion job by its ID. Use this to monitor the progress and outcome of a deletion operation."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAReplayBatchDeletionJobRequest(
            path=_models.RetrieveAReplayBatchDeletionJobRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, job_id=job_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_replay_deletion_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/replays/jobs/delete/{job_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/replays/jobs/delete/{job_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_replay_deletion_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_replay_deletion_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_replay_deletion_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Alerts
@mcp.tool()
async def get_issue_alert_rule(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL slug of the project."),
    rule_id: int = Field(..., description="The numeric ID of the alert rule to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve details for a specific issue alert rule in a project. Issue alert rules define triggers, filters, and actions that determine when alerts are sent for matching issues. Note: This endpoint is deprecated; use the Fetch an Alert endpoint instead."""

    # Construct request model with validation
    try:
        _request = _models.DeprecatedRetrieveAnIssueAlertRuleForAProjectRequest(
            path=_models.DeprecatedRetrieveAnIssueAlertRuleForAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, rule_id=rule_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_issue_alert_rule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/rules/{rule_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/rules/{rule_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_issue_alert_rule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_issue_alert_rule", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_issue_alert_rule",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Alerts
@mcp.tool()
async def update_issue_alert_rule(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or URL slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or URL slug."),
    rule_id: int = Field(..., description="The numeric ID of the alert rule to update."),
    name: str = Field(..., description="A descriptive name for the alert rule, up to 256 characters.", max_length=256),
    action_match: Literal["all", "any", "none"] = Field(..., alias="actionMatch", description="Determines how conditions are evaluated: 'all' requires all conditions to be true, 'any' requires at least one to be true, and 'none' requires all to be false."),
    conditions: list[dict[str, Any]] = Field(..., description="An array of trigger conditions that determine when the rule fires. Refer to the Create an Issue Alert Rule endpoint for valid condition types and structures."),
    actions: list[dict[str, Any]] = Field(..., description="An array of actions to execute when conditions and filters are met. Refer to the Create an Issue Alert Rule endpoint for valid action types and structures."),
    frequency: int = Field(..., description="The interval in minutes between repeated actions for the same issue, ranging from 5 to 43200 minutes (30 days).", ge=5, le=43200),
    environment: str | None = Field(None, description="Optional environment name to filter alerts by. If specified, the rule only applies to events from this environment."),
    filter_match: Literal["all", "any", "none"] | None = Field(None, alias="filterMatch", description="Determines how filters are evaluated: 'all' requires all filters to match, 'any' requires at least one to match, and 'none' requires all to not match."),
    filters: list[dict[str, Any]] | None = Field(None, description="An optional array of filters that further refine when the rule fires after conditions are met. Refer to the Create an Issue Alert Rule endpoint for valid filter types and structures."),
    owner: str | None = Field(None, description="Optional identifier of the team or user that owns this alert rule."),
) -> dict[str, Any] | ToolResult:
    """Update an issue alert rule that triggers on events matching specified conditions. This operation fully overwrites the alert rule, so all required fields must be provided. Note: This endpoint is deprecated; use the Alert by ID endpoint instead."""

    # Construct request model with validation
    try:
        _request = _models.DeprecatedUpdateAnIssueAlertRuleRequest(
            path=_models.DeprecatedUpdateAnIssueAlertRuleRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, rule_id=rule_id),
            body=_models.DeprecatedUpdateAnIssueAlertRuleRequestBody(name=name, action_match=action_match, conditions=conditions, actions=actions, frequency=frequency, environment=environment, filter_match=filter_match, filters=filters, owner=owner)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_issue_alert_rule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/rules/{rule_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/rules/{rule_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_issue_alert_rule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_issue_alert_rule", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_issue_alert_rule",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Alerts
@mcp.tool()
async def delete_issue_alert_rule(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug of the organization that owns the project."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL slug of the project containing the alert rule."),
    rule_id: int = Field(..., description="The numeric ID of the alert rule to delete."),
) -> dict[str, Any] | ToolResult:
    """Delete a specific issue alert rule from a project. Issue alert rules trigger on new events matching specified conditions (such as resolved issues reappearing or issues affecting many users) and are configured with triggers, filters, and actions. Note: This endpoint is deprecated; use the Delete an Alert endpoint instead."""

    # Construct request model with validation
    try:
        _request = _models.DeprecatedDeleteAnIssueAlertRuleRequest(
            path=_models.DeprecatedDeleteAnIssueAlertRuleRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, rule_id=rule_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_issue_alert_rule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/rules/{rule_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/rules/{rule_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_issue_alert_rule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_issue_alert_rule", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_issue_alert_rule",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_project_symbol_sources(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all custom symbol sources configured for a specific project. Symbol sources enable the project to resolve debug symbols from external repositories."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAProjectSSymbolSourcesRequest(
            path=_models.RetrieveAProjectSSymbolSourcesRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_symbol_sources: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/symbol-sources/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/symbol-sources/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_symbol_sources")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_symbol_sources", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_symbol_sources",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def add_symbol_source_to_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or URL-friendly slug."),
    type_: Literal["http", "gcs", "s3"] = Field(..., alias="type", description="The symbol source backend type: HTTP (SymbolServer), Google Cloud Storage, or Amazon S3."),
    layout_type: Literal["native", "symstore", "symstore_index2", "ssqp", "unified", "debuginfod", "slashsymbols"] = Field(..., alias="layoutType", description="The directory layout format used by the symbol source: native, symstore, symstore_index2, SSQP, unified, debuginfod, or /symbols."),
    name: str = Field(..., description="A human-readable display name for this symbol source."),
    casing: Literal["lowercase", "uppercase", "default"] = Field(..., description="How file paths are normalized: lowercase, uppercase, or default (no transformation)."),
    filetypes: list[Literal["pe", "pdb", "portablepdb", "mach_debug", "mach_code", "elf_debug", "elf_code", "wasm_debug", "wasm_code", "breakpad", "sourcebundle", "uuidmap", "bcsymbolmap", "il2cpp", "proguard", "dartsymbolmap"]] | None = Field(None, description="Array of file extensions to enable for this source (e.g., 'pdb', 'elf', 'dwarf'). If omitted, all supported types are enabled."),
    path_patterns: list[str] | None = Field(None, description="Array of glob patterns to match against debug and code file paths. If omitted, all paths are accepted."),
    requires_checksum: bool | None = Field(None, description="Whether debug checksums must be present and validated for files from this source."),
    url: str | None = Field(None, description="The base URL of the symbol server. Required for HTTP sources; must be omitted for GCS and S3 sources."),
    username: str | None = Field(None, description="Username for HTTP Basic Authentication. Valid only for HTTP sources."),
    password: str | None = Field(None, description="Password for HTTP Basic Authentication. Valid only for HTTP sources."),
    bucket: str | None = Field(None, description="The bucket name containing symbols. Required for GCS and S3 sources; must be omitted for HTTP sources."),
    region: Literal["us-east-2", "us-east-1", "us-west-1", "us-west-2", "ap-east-1", "ap-south-1", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2", "ap-northeast-1", "ca-central-1", "cn-north-1", "cn-northwest-1", "eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3", "eu-north-1", "sa-east-1", "us-gov-east-1", "us-gov-west-1"] | None = Field(None, description="The AWS region where the S3 bucket is located. Required for S3 sources; must be omitted for HTTP and GCS sources."),
    access_key: str | None = Field(None, description="The AWS Access Key for S3 authentication. Required for S3 sources; must be omitted for HTTP and GCS sources."),
    secret_key: str | None = Field(None, description="The AWS Secret Access Key for S3 authentication. Required for S3 sources; must be omitted for HTTP and GCS sources."),
    prefix: str | None = Field(None, description="A path prefix within the bucket to scope symbol lookups. Optional for GCS and S3 sources; must be omitted for HTTP sources."),
    client_email: str | None = Field(None, description="The service account email address for GCS authentication. Required for GCS sources; must be omitted for HTTP and S3 sources."),
    private_key: str | None = Field(None, description="The private key for GCS service account authentication. Required for GCS sources unless using impersonated tokens; must be omitted for HTTP and S3 sources."),
) -> dict[str, Any] | ToolResult:
    """Add a custom symbol source to a project for debug symbol resolution. Supports HTTP, Google Cloud Storage, and Amazon S3 backends with configurable layout types and casing rules."""

    # Construct request model with validation
    try:
        _request = _models.AddASymbolSourceToAProjectRequest(
            path=_models.AddASymbolSourceToAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            body=_models.AddASymbolSourceToAProjectRequestBody(type_=type_, name=name, url=url, username=username, password=password, bucket=bucket, region=region, access_key=access_key, secret_key=secret_key, prefix=prefix, client_email=client_email, private_key=private_key,
                layout=_models.AddASymbolSourceToAProjectRequestBodyLayout(type_=layout_type, casing=casing),
                filters=_models.AddASymbolSourceToAProjectRequestBodyFilters(filetypes=filetypes, path_patterns=path_patterns, requires_checksum=requires_checksum) if any(v is not None for v in [filetypes, path_patterns, requires_checksum]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_symbol_source_to_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/symbol-sources/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/symbol-sources/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_symbol_source_to_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_symbol_source_to_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_symbol_source_to_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def update_project_symbol_source(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or URL-friendly slug."),
    id_: str = Field(..., alias="id", description="The unique identifier of the symbol source to update."),
    type_: Literal["http", "gcs", "s3"] = Field(..., alias="type", description="The symbol source backend type: HTTP (SymbolServer), Google Cloud Storage, or Amazon S3."),
    layout_type: Literal["native", "symstore", "symstore_index2", "ssqp", "unified", "debuginfod", "slashsymbols"] = Field(..., alias="layoutType", description="The directory structure layout format used by the symbol source: native, symstore, symstore_index2, ssqp, unified, debuginfod, or slashsymbols."),
    name: str = Field(..., description="A human-readable display name for the symbol source."),
    casing: Literal["lowercase", "uppercase", "default"] = Field(..., description="Path casing normalization rule: lowercase, uppercase, or default (no transformation)."),
    id_2: str | None = Field(None, alias="id", description="Custom internal identifier for the source. Must be unique across all sources in the project and cannot begin with 'sentry:'. If omitted, a UUID will be automatically generated."),
    filetypes: list[Literal["pe", "pdb", "portablepdb", "mach_debug", "mach_code", "elf_debug", "elf_code", "wasm_debug", "wasm_code", "breakpad", "sourcebundle", "uuidmap", "bcsymbolmap", "il2cpp", "proguard", "dartsymbolmap"]] | None = Field(None, description="Array of file type extensions to enable for symbol resolution (e.g., 'pdb', 'dwarf', 'macho'). Order is not significant."),
    path_patterns: list[str] | None = Field(None, description="Array of glob patterns to filter which debug and code file paths are queried from this source. Order is not significant."),
    requires_checksum: bool | None = Field(None, description="Whether symbol lookups from this source must include and validate debug checksums."),
    url: str | None = Field(None, description="The base URL of the HTTP symbol server. Required only for HTTP sources; invalid for cloud storage sources."),
    username: str | None = Field(None, description="Username for HTTP Basic Authentication. Valid only for HTTP sources."),
    password: str | None = Field(None, description="Password for HTTP Basic Authentication. Valid only for HTTP sources."),
    bucket: str | None = Field(None, description="The bucket name in Google Cloud Storage or Amazon S3. Required for GCS and S3 sources; invalid for HTTP sources."),
    region: Literal["us-east-2", "us-east-1", "us-west-1", "us-west-2", "ap-east-1", "ap-south-1", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2", "ap-northeast-1", "ca-central-1", "cn-north-1", "cn-northwest-1", "eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3", "eu-north-1", "sa-east-1", "us-gov-east-1", "us-gov-west-1"] | None = Field(None, description="The AWS region where the S3 bucket is located. Required for S3 sources; invalid for HTTP and GCS sources."),
    access_key: str | None = Field(None, description="The AWS Access Key for S3 authentication. Required for S3 sources; invalid for HTTP and GCS sources."),
    secret_key: str | None = Field(None, description="The AWS Secret Access Key for S3 authentication. Required for S3 sources; invalid for HTTP and GCS sources."),
    prefix: str | None = Field(None, description="The object key prefix path within the GCS or S3 bucket. Optional for cloud storage sources; invalid for HTTP sources."),
    client_email: str | None = Field(None, description="The service account email address for GCS authentication. Required for GCS sources; invalid for HTTP and S3 sources."),
    private_key: str | None = Field(None, description="The private key for GCS service account authentication. Required for GCS sources when not using impersonated tokens; invalid for HTTP and S3 sources."),
) -> dict[str, Any] | ToolResult:
    """Update an existing custom symbol source configuration in a project. Modify source type, layout, authentication credentials, and file filtering rules for symbol resolution."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAProjectSSymbolSourceRequest(
            path=_models.UpdateAProjectSSymbolSourceRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            query=_models.UpdateAProjectSSymbolSourceRequestQuery(id_=id_),
            body=_models.UpdateAProjectSSymbolSourceRequestBody(id_=id_2, type_=type_, name=name, url=url, username=username, password=password, bucket=bucket, region=region, access_key=access_key, secret_key=secret_key, prefix=prefix, client_email=client_email, private_key=private_key,
                layout=_models.UpdateAProjectSSymbolSourceRequestBodyLayout(type_=layout_type, casing=casing),
                filters=_models.UpdateAProjectSSymbolSourceRequestBodyFilters(filetypes=filetypes, path_patterns=path_patterns, requires_checksum=requires_checksum) if any(v is not None for v in [filetypes, path_patterns, requires_checksum]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project_symbol_source: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/symbol-sources/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/symbol-sources/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project_symbol_source")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project_symbol_source", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project_symbol_source",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def delete_symbol_source(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug."),
    id_: str = Field(..., alias="id", description="The unique identifier of the symbol source to delete."),
) -> dict[str, Any] | ToolResult:
    """Remove a custom symbol source from a project. This permanently deletes the symbol source configuration and its associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteASymbolSourceFromAProjectRequest(
            path=_models.DeleteASymbolSourceFromAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            query=_models.DeleteASymbolSourceFromAProjectRequestQuery(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_symbol_source: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/symbol-sources/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/symbol-sources/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_symbol_source")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_symbol_source", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_symbol_source",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def list_teams_for_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all teams that have access to a specific project within an organization."""

    # Construct request model with validation
    try:
        _request = _models.ListAProjectSTeamsRequest(
            path=_models.ListAProjectSTeamsRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_teams_for_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/teams/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/teams/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_teams_for_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_teams_for_project", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_teams_for_project",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def add_team_to_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization."),
    team_id_or_slug: str = Field(..., description="The team identifier, which can be either the numeric ID or the URL-friendly slug of the team to grant access."),
) -> dict[str, Any] | ToolResult:
    """Grant a team access to a project, enabling collaboration and resource sharing within the specified organization."""

    # Construct request model with validation
    try:
        _request = _models.AddATeamToAProjectRequest(
            path=_models.AddATeamToAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, team_id_or_slug=team_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_team_to_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/teams/{team_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/teams/{team_id_or_slug}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_team_to_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_team_to_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_team_to_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def delete_team_from_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL slug."),
    team_id_or_slug: str = Field(..., description="The team identifier, either the numeric ID or the URL slug."),
) -> dict[str, Any] | ToolResult:
    """Revoke a team's access to a project. Team Admins can only revoke access for teams they administer."""

    # Construct request model with validation
    try:
        _request = _models.DeleteATeamFromAProjectRequest(
            path=_models.DeleteATeamFromAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, team_id_or_slug=team_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_team_from_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/teams/{team_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/teams/{team_id_or_slug}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_team_from_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_team_from_project", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_team_from_project",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration
@mcp.tool()
async def get_custom_integration(sentry_app_id_or_slug: str = Field(..., description="The unique identifier or URL-friendly slug of the custom integration. You can use either the numeric ID or the slug string to identify which custom integration to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details about a custom integration (Sentry App) by its unique identifier or slug. Use this to fetch configuration, permissions, and metadata for a specific custom integration."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveACustomIntegrationByIdOrSlugRequest(
            path=_models.RetrieveACustomIntegrationByIdOrSlugRequestPath(sentry_app_id_or_slug=sentry_app_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_integration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/sentry-apps/{sentry_app_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/sentry-apps/{sentry_app_id_or_slug}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_integration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_integration", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_integration",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration
@mcp.tool()
async def delete_custom_integration(sentry_app_id_or_slug: str = Field(..., description="The unique identifier or slug of the custom integration to delete. You can use either the numeric ID or the URL-friendly slug name.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a custom integration (Sentry app) from your organization. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteACustomIntegrationRequest(
            path=_models.DeleteACustomIntegrationRequestPath(sentry_app_id_or_slug=sentry_app_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_integration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/sentry-apps/{sentry_app_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/sentry-apps/{sentry_app_id_or_slug}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_custom_integration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_custom_integration", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_custom_integration",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def get_team(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug. This scopes the team lookup to a specific organization."),
    team_id_or_slug: str = Field(..., description="The team identifier, either the numeric ID or the URL-friendly slug. Combined with the organization identifier to uniquely identify the team."),
    expand: str | None = Field(None, description="Comma-separated list of related data to include in the response. Supports `projects` to include team projects and `externalTeams` to include external team integrations."),
    collapse: str | None = Field(None, description="Comma-separated list of data fields to exclude from the response. Supports `organization` to omit the parent organization details."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific team within an organization. Use organization and team identifiers (IDs or slugs) to fetch the team resource with optional expansion of related data."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveATeamRequest(
            path=_models.RetrieveATeamRequestPath(organization_id_or_slug=organization_id_or_slug, team_id_or_slug=team_id_or_slug),
            query=_models.RetrieveATeamRequestQuery(expand=expand, collapse=collapse)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def update_team(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    team_id_or_slug: str = Field(..., description="The team identifier, either the numeric ID or the URL-friendly slug."),
    slug: str = Field(..., description="A unique identifier for the team using lowercase letters, numbers, hyphens, and underscores (cannot be purely numeric). Maximum 50 characters.", max_length=50),
) -> dict[str, Any] | ToolResult:
    """Update team attributes and configurable settings such as the team slug and other team-level properties."""

    # Construct request model with validation
    try:
        _request = _models.UpdateATeamRequest(
            path=_models.UpdateATeamRequestPath(organization_id_or_slug=organization_id_or_slug, team_id_or_slug=team_id_or_slug),
            body=_models.UpdateATeamRequestBody(slug=slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def delete_team(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL slug of the organization."),
    team_id_or_slug: str = Field(..., description="The team identifier, which can be either the numeric ID or the URL slug of the team to be deleted."),
) -> dict[str, Any] | ToolResult:
    """Schedules a team for deletion. The deletion process is asynchronous, so the team won't be immediately removed, but its slug will be released immediately while the deletion completes in the background."""

    # Construct request model with validation
    try:
        _request = _models.DeleteATeamRequest(
            path=_models.DeleteATeamRequestPath(organization_id_or_slug=organization_id_or_slug, team_id_or_slug=team_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_team", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_team",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integrations
@mcp.tool()
async def link_external_team(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug of the organization."),
    team_id_or_slug: str = Field(..., description="The team identifier, either the numeric ID or the URL slug of the team within the organization."),
    external_name: str = Field(..., description="The name or identifier of the external team as it appears in the provider system."),
    provider: Literal["github", "github_enterprise", "jira_server", "slack", "slack_staging", "perforce", "gitlab", "msteams", "custom_scm"] = Field(..., description="The external provider platform. Supported providers include GitHub, GitHub Enterprise, Jira Server, Slack, Slack Staging, Perforce, GitLab, Microsoft Teams, and custom SCM systems."),
    integration_id: int = Field(..., description="The numeric ID of the integration configuration that connects Sentry to the external provider."),
    external_id: str | None = Field(None, description="The unique identifier of the external team or user within the provider system. This field is optional and may be required depending on the provider."),
) -> dict[str, Any] | ToolResult:
    """Link a team from an external provider (such as GitHub, Slack, Jira, or GitLab) to a Sentry team, enabling cross-platform team synchronization and integration."""

    # Construct request model with validation
    try:
        _request = _models.CreateAnExternalTeamRequest(
            path=_models.CreateAnExternalTeamRequestPath(organization_id_or_slug=organization_id_or_slug, team_id_or_slug=team_id_or_slug),
            body=_models.CreateAnExternalTeamRequestBody(external_name=external_name, provider=provider, integration_id=integration_id, external_id=external_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for link_external_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/external-teams/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/external-teams/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("link_external_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("link_external_team", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="link_external_team",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integrations
@mcp.tool()
async def update_external_team(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug of the organization."),
    team_id_or_slug: str = Field(..., description="The team identifier, either the numeric ID or the URL slug of the team within the organization."),
    external_team_id: int = Field(..., description="The unique identifier of the external team object to update, returned when the external team was originally created."),
    external_name: str = Field(..., description="The display name or identifier for the external team in the provider system."),
    provider: Literal["github", "github_enterprise", "jira_server", "slack", "slack_staging", "perforce", "gitlab", "msteams", "custom_scm"] = Field(..., description="The external provider platform. Supported providers include GitHub, GitHub Enterprise, Jira Server, Slack, Slack Staging, Perforce, GitLab, Microsoft Teams, and custom SCM systems."),
    integration_id: int = Field(..., description="The numeric ID of the integration that connects Sentry to the external provider."),
    external_id: str | None = Field(None, description="The unique identifier or handle for the external team within the provider system (e.g., user ID, team ID, or handle). Optional if not applicable to the provider."),
) -> dict[str, Any] | ToolResult:
    """Update the configuration of an external team (from GitHub, Slack, Jira, etc.) that is linked to a Sentry team. This allows you to modify the external team's name, provider details, and associated identifiers."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAnExternalTeamRequest(
            path=_models.UpdateAnExternalTeamRequestPath(organization_id_or_slug=organization_id_or_slug, team_id_or_slug=team_id_or_slug, external_team_id=external_team_id),
            body=_models.UpdateAnExternalTeamRequestBody(external_name=external_name, provider=provider, integration_id=integration_id, external_id=external_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_external_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/external-teams/{external_team_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/external-teams/{external_team_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_external_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_external_team", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_external_team",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integrations
@mcp.tool()
async def delete_external_team_link(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug of the organization containing the team."),
    team_id_or_slug: str = Field(..., description="The team identifier, either the numeric ID or the URL slug of the Sentry team to disconnect from the external provider."),
    external_team_id: int = Field(..., description="The numeric ID of the external team link to delete, as returned when the external team integration was originally created."),
) -> dict[str, Any] | ToolResult:
    """Remove the integration link between an external team (from a provider like GitHub or Slack) and a Sentry team, effectively disconnecting the external team from Sentry's team management."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnExternalTeamRequest(
            path=_models.DeleteAnExternalTeamRequestPath(organization_id_or_slug=organization_id_or_slug, team_id_or_slug=team_id_or_slug, external_team_id=external_team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_external_team_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/external-teams/{external_team_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/external-teams/{external_team_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_external_team_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_external_team_link", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_external_team_link",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def list_team_members(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL slug of the organization."),
    team_id_or_slug: str = Field(..., description="The team identifier, which can be either the numeric ID or the URL slug of the team within the organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all active members of a team within an organization. Note that members with pending invitations are excluded from the results."""

    # Construct request model with validation
    try:
        _request = _models.ListATeamSMembersRequest(
            path=_models.ListATeamSMembersRequestPath(organization_id_or_slug=organization_id_or_slug, team_id_or_slug=team_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/members/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/members/"
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

# Tags: Teams
@mcp.tool()
async def list_team_projects(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    team_id_or_slug: str = Field(..., description="The team identifier, which can be either the numeric ID or the URL-friendly slug of the team within the organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all projects associated with a specific team within an organization. Returns a list of projects bound to the team."""

    # Construct request model with validation
    try:
        _request = _models.ListATeamSProjectsRequest(
            path=_models.ListATeamSProjectsRequestPath(organization_id_or_slug=organization_id_or_slug, team_id_or_slug=team_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/projects/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/projects/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_team_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_team_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_team_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def create_project_for_team(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either its numeric ID or URL slug."),
    team_id_or_slug: str = Field(..., description="The team identifier, either its numeric ID or URL slug."),
    name: str = Field(..., description="The display name for the project. Must not exceed 50 characters.", max_length=50),
    slug: str | None = Field(None, description="A URL-safe identifier for the project used in the interface. If omitted, it will be auto-generated from the project name. Must contain only lowercase letters, numbers, hyphens, and underscores, cannot be purely numeric, and must not exceed 100 characters.", max_length=100),
    platform: str | None = Field(None, description="The platform or technology stack associated with the project (e.g., JavaScript, Python, Java)."),
    default_rules: bool | None = Field(None, description="Whether to enable default alert rules that notify on every new issue. Defaults to true; set to false to require manual alert configuration."),
) -> dict[str, Any] | ToolResult:
    """Create a new project within a team. Requires org:write or team:admin scope if your organization has disabled member project creation."""

    # Construct request model with validation
    try:
        _request = _models.CreateANewProjectRequest(
            path=_models.CreateANewProjectRequestPath(organization_id_or_slug=organization_id_or_slug, team_id_or_slug=team_id_or_slug),
            body=_models.CreateANewProjectRequestBody(name=name, slug=slug, platform=platform, default_rules=default_rules)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project_for_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/projects/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/projects/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_project_for_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_project_for_team", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_project_for_team",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def list_organization_repositories(organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the organization's slug (short name). Use the slug for human-readable requests or the ID for programmatic lookups.")) -> dict[str, Any] | ToolResult:
    """Retrieve all version control repositories belonging to a specified organization. Returns a paginated list of repositories accessible to the authenticated user."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSRepositoriesRequest(
            path=_models.ListAnOrganizationSRepositoriesRequestPath(organization_id_or_slug=organization_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_repositories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/repos/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/repos/"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_debug_information_files(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all debug information files (dSYMs and other debug symbols) associated with a specific project. These files are used for symbolication and error tracking."""

    # Construct request model with validation
    try:
        _request = _models.ListAProjectSDebugInformationFilesRequest(
            path=_models.ListAProjectSDebugInformationFilesRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_debug_information_files: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/files/dsyms/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/files/dsyms/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_debug_information_files")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_debug_information_files", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_debug_information_files",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def upload_dsym_file(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug. Used to scope the project within your organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL slug. Specifies which project receives the debug information file."),
    file_: str = Field(..., alias="file", description="The dSYM file to upload as binary data. Must be a zip archive containing Apple .dSYM folders with debug images."),
) -> dict[str, Any] | ToolResult:
    """Upload a debug information file (dSYM) for a specific release. The file must be a zip archive containing Apple .dSYM folders with debug images; uploading creates separate files for each contained image. Use region-specific domains (e.g., us.sentry.io or de.sentry.io) for this request."""

    # Construct request model with validation
    try:
        _request = _models.UploadANewFileRequest(
            path=_models.UploadANewFileRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            body=_models.UploadANewFileRequestBody(file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_dsym_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/files/dsyms/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/files/dsyms/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_dsym_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_dsym_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_dsym_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def delete_debug_information_file(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug of the organization that owns the project."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug of the project containing the debug information file to delete."),
    id_: str = Field(..., alias="id", description="The unique identifier of the debug information file to delete."),
) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific debug information file (DIF) from a project. This removes the debug symbols associated with the given DIF ID."""

    # Construct request model with validation
    try:
        _request = _models.DeleteASpecificProjectSDebugInformationFileRequest(
            path=_models.DeleteASpecificProjectSDebugInformationFileRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            query=_models.DeleteASpecificProjectSDebugInformationFileRequestQuery(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_debug_information_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/files/dsyms/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/files/dsyms/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_debug_information_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_debug_information_file", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_debug_information_file",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_project_users(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or a URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either as a numeric ID or a URL-friendly slug."),
    query: str | None = Field(None, description="Optional search filter to narrow results by user attributes. Use prefixed queries in the format `field:value` where field is one of: `id`, `email`, `username`, or `ip`. Multiple filters can be combined."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of users who have been seen or are active within a specific project. Optionally filter results by user attributes such as ID, email, username, or IP address."""

    # Construct request model with validation
    try:
        _request = _models.ListAProjectSUsersRequest(
            path=_models.ListAProjectSUsersRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            query=_models.ListAProjectSUsersRequestQuery(query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/users/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/users/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_users")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_users", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_users",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_tag_values(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug."),
    key: str = Field(..., description="The tag key name to retrieve associated values for."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all values associated with a specific tag key in a project. Supports filtering values using a contains-based query parameter and returns up to 1000 results per page."""

    # Construct request model with validation
    try:
        _request = _models.ListATagSValuesRequest(
            path=_models.ListATagSValuesRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, key=key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tag_values: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/tags/{key}/values/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/tags/{key}/values/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tag_values")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tag_values", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tag_values",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def get_event_counts_for_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL slug."),
    stat: Literal["received", "rejected", "blacklisted", "generated"] | None = Field(None, description="The type of event statistic to retrieve: received (accepted events), rejected (rate-limited events), blacklisted (filtered events), or generated (server-generated events)."),
    since: str | None = Field(None, description="The start of the query time range as an ISO 8601 formatted timestamp. If omitted, defaults to a recent time window."),
    until: str | None = Field(None, description="The end of the query time range as an ISO 8601 formatted timestamp. If omitted, defaults to the current time."),
    resolution: Literal["10s", "1h", "1d"] | None = Field(None, description="The time bucket size for aggregating results: 10 seconds for fine-grained data, 1 hour for daily trends, or 1 day for long-term analysis. If omitted, Sentry selects an appropriate resolution based on the query range."),
) -> dict[str, Any] | ToolResult:
    """Retrieve event statistics for a project over a specified time range. Returns normalized timestamps with event counts aggregated at the requested resolution. Query ranges are limited by Sentry's configured time-series resolutions."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveEventCountsForAProjectRequest(
            path=_models.RetrieveEventCountsForAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            query=_models.RetrieveEventCountsForAProjectRequestQuery(stat=stat, since=since, until=until, resolution=resolution)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_event_counts_for_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/stats/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/stats/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_event_counts_for_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_event_counts_for_project", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_event_counts_for_project",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_project_user_feedback(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL slug."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of user feedback items submitted to a project. Note: This returns legacy User Reports format feedback; for User Feedback Widget submissions, use the issues API with the `issue.category:feedback` filter instead."""

    # Construct request model with validation
    try:
        _request = _models.ListAProjectSUserFeedbackRequest(
            path=_models.ListAProjectSUserFeedbackRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_user_feedback: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/user-feedback/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/user-feedback/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_user_feedback")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_user_feedback", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_user_feedback",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def submit_user_feedback(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL slug."),
    event_id: str = Field(..., description="The unique identifier of the event to attach feedback to. This value can be obtained from the beforeSend callback in your SDK configuration."),
    name: str = Field(..., description="The full name of the user providing feedback."),
    email: str = Field(..., description="The email address of the user providing feedback."),
    comments: str = Field(..., description="The user's feedback comments or message describing their experience."),
) -> dict[str, Any] | ToolResult:
    """Submit user feedback for a specific event. This endpoint is deprecated; use the User Feedback Widget or platform-specific User Feedback API instead. Feedback must be submitted within 30 minutes of the event and can be overwritten within 5 minutes of initial submission."""

    # Construct request model with validation
    try:
        _request = _models.SubmitUserFeedbackRequest(
            path=_models.SubmitUserFeedbackRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            body=_models.SubmitUserFeedbackRequestBody(event_id=event_id, name=name, email=email, comments=comments)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for submit_user_feedback: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/user-feedback/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/user-feedback/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("submit_user_feedback")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("submit_user_feedback", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="submit_user_feedback",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_project_service_hooks(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all service hooks configured for a specific project. Service hooks enable integrations that trigger on project events."""

    # Construct request model with validation
    try:
        _request = _models.ListAProjectSServiceHooksRequest(
            path=_models.ListAProjectSServiceHooksRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_service_hooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/hooks/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/hooks/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_service_hooks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_service_hooks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_service_hooks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def get_service_hook(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug."),
    hook_id: str = Field(..., description="The unique identifier (GUID) of the service hook to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific service hook configured for a project. Returns the hook's configuration and metadata."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAServiceHookRequest(
            path=_models.RetrieveAServiceHookRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, hook_id=hook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_service_hook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/hooks/{hook_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/hooks/{hook_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_service_hook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_service_hook", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_service_hook",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def update_service_hook(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug."),
    hook_id: str = Field(..., description="The unique identifier (GUID) of the service hook to update."),
    url: str = Field(..., description="The destination URL where webhook payloads will be sent. Must be a valid HTTP or HTTPS endpoint."),
    events: list[str] = Field(..., description="An array of event types to subscribe to. The hook will trigger for each specified event. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Update an existing service hook configuration for a project, including its webhook URL and subscribed event types."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAServiceHookRequest(
            path=_models.UpdateAServiceHookRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, hook_id=hook_id),
            body=_models.UpdateAServiceHookRequestBody(url=url, events=events)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_service_hook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/hooks/{hook_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/hooks/{hook_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_service_hook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_service_hook", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_service_hook",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def remove_service_hook(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug."),
    hook_id: str = Field(..., description="The unique identifier (GUID) of the service hook to remove."),
) -> dict[str, Any] | ToolResult:
    """Delete a service hook from a project. This removes the webhook integration and stops it from receiving events."""

    # Construct request model with validation
    try:
        _request = _models.RemoveAServiceHookRequest(
            path=_models.RemoveAServiceHookRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, hook_id=hook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_service_hook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/hooks/{hook_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/hooks/{hook_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_service_hook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_service_hook", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_service_hook",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def get_event(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization."),
    event_id: str = Field(..., description="The unique hexadecimal identifier of the event to retrieve, as reported by the client SDK."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific event within a project, including error data, breadcrumbs, and other event metadata."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAnEventForAProjectRequest(
            path=_models.RetrieveAnEventForAProjectRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, event_id=event_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/events/{event_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/events/{event_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_event", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_event",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def list_project_issues(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either as a numeric ID or URL slug."),
    query: str | None = Field(None, description="A Sentry structured search query to filter results. If omitted, defaults to `is:unresolved`. Use an empty query to retrieve all issues regardless of status. Supports filtering by issue category (e.g., `issue.category:feedback` for user feedback items)."),
    hashes: str | None = Field(None, description="A list of issue group hashes to retrieve, up to a maximum of 100. Cannot be used together with the query parameter. Hashes should be provided as comma-separated values."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of issues (groups) for a specific project. By default, only unresolved issues are returned unless a custom query is provided. This endpoint is deprecated in favor of the Organization Issues endpoint."""

    # Construct request model with validation
    try:
        _request = _models.ListAProjectSIssuesRequest(
            path=_models.ListAProjectSIssuesRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            query=_models.ListAProjectSIssuesRequestQuery(query=query, hashes=hashes)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/issues/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/issues/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_issues", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_issues",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def update_issues_bulk(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or URL slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or URL slug."),
    status: str | None = Field(None, description="Optionally filter mutations to only affect issues with a specific status: resolved, reprocessing, unresolved, or ignored."),
    status2: str | None = Field(None, alias="status", description="Set the new status for targeted issues. Accepts: resolved, resolvedInNextRelease, unresolved, or ignored."),
    ignore_duration: int | None = Field(None, alias="ignoreDuration", description="Duration in milliseconds for which an ignored issue should remain ignored before auto-resolving."),
    ignore_count: int | None = Field(None, alias="ignoreCount", description="Number of occurrences before an issue is automatically ignored."),
    ignore_window: int | None = Field(None, alias="ignoreWindow", description="Time window in milliseconds within which occurrences are counted for auto-ignore."),
    ignore_user_count: int | None = Field(None, alias="ignoreUserCount", description="Number of unique users affected before an issue is automatically ignored."),
    ignore_user_window: int | None = Field(None, alias="ignoreUserWindow", description="Time window in milliseconds within which unique user counts are measured for auto-ignore."),
    is_public: bool | None = Field(None, alias="isPublic", description="Make the issue publicly visible (true) or restrict to organization members only (false)."),
    merge: bool | None = Field(None, description="Merge multiple issues into one (true) or separate a merged issue (false)."),
    assigned_to: str | None = Field(None, alias="assignedTo", description="Assign the issue to a user or team by their actor ID or username."),
    has_seen: bool | None = Field(None, alias="hasSeen", description="Mark whether the current user has viewed this issue (true) or not (false). Only applicable when invoked with user context."),
    is_bookmarked: bool | None = Field(None, alias="isBookmarked", description="Add or remove the issue from the current user's bookmarks (true to bookmark, false to remove). Only applicable when invoked with user context."),
) -> dict[str, Any] | ToolResult:
    """Bulk update multiple issues by modifying their attributes such as status, assignment, visibility, and user-specific flags. Target issues using the `id` query parameter (repeatable), with optional filtering by current status."""

    # Construct request model with validation
    try:
        _request = _models.BulkMutateAListOfIssuesRequest(
            path=_models.BulkMutateAListOfIssuesRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug),
            query=_models.BulkMutateAListOfIssuesRequestQuery(status=status),
            body=_models.BulkMutateAListOfIssuesRequestBody(status=status2, is_public=is_public, merge=merge, assigned_to=assigned_to, has_seen=has_seen, is_bookmarked=is_bookmarked,
                status_details=_models.BulkMutateAListOfIssuesRequestBodyStatusDetails(ignore_duration=ignore_duration, ignore_count=ignore_count, ignore_window=ignore_window, ignore_user_count=ignore_user_count, ignore_user_window=ignore_user_window) if any(v is not None for v in [ignore_duration, ignore_count, ignore_window, ignore_user_count, ignore_user_window]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_issues_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/issues/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/issues/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_issues_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_issues_bulk", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_issues_bulk",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def delete_issues(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either its numeric ID or URL slug. Used to scope the project and issues being deleted."),
    project_id_or_slug: str = Field(..., description="The project identifier, either its numeric ID or URL slug. Combined with the organization to locate the issues for deletion."),
) -> dict[str, Any] | ToolResult:
    """Permanently remove one or more issues from a project. Specify issue IDs via query parameters; the operation succeeds even if some IDs are invalid or out of scope without modifying any data."""

    # Construct request model with validation
    try:
        _request = _models.BulkRemoveAListOfIssuesRequest(
            path=_models.BulkRemoveAListOfIssuesRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/issues/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/issues/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_issues", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_issues",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def list_tag_values_for_issue(
    issue_id: int = Field(..., description="The numeric identifier of the issue to query for tag values."),
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    key: str = Field(..., description="The tag key name to retrieve associated values for."),
    environment: list[str] | None = Field(None, description="Optional list of environment names to filter tag values by. When specified, only values from the listed environments are returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all values associated with a specific tag key for an issue, useful for understanding what tags have been applied and their values. Returns up to 1000 values when paginated."""

    # Construct request model with validation
    try:
        _request = _models.ListATagSValuesForAnIssueRequest(
            path=_models.ListATagSValuesForAnIssueRequestPath(issue_id=issue_id, organization_id_or_slug=organization_id_or_slug, key=key),
            query=_models.ListATagSValuesForAnIssueRequestQuery(environment=environment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tag_values_for_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/tags/{key}/values/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/tags/{key}/values/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tag_values_for_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tag_values_for_issue", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tag_values_for_issue",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def list_issue_hashes(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug of the organization."),
    issue_id: str = Field(..., description="The numeric or string identifier of the issue whose hashes should be retrieved."),
    full: bool | None = Field(None, description="When enabled, the response includes the complete event payload with full details such as stack traces. Defaults to true."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the list of hashes (generated checksums) associated with an issue, which are used to aggregate individual events into the issue."""

    # Construct request model with validation
    try:
        _request = _models.ListAnIssueSHashesRequest(
            path=_models.ListAnIssueSHashesRequestPath(organization_id_or_slug=organization_id_or_slug, issue_id=issue_id),
            query=_models.ListAnIssueSHashesRequestQuery(full=full)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_issue_hashes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/hashes/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/hashes/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_hashes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_hashes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_hashes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def get_issue(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization that owns the issue."),
    issue_id: str = Field(..., description="The unique identifier of the issue to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific issue, including its core metadata (title, first/last seen timestamps), engagement metrics (comments, user reports), and summarized event data."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAnIssueRequest(
            path=_models.RetrieveAnIssueRequestPath(organization_id_or_slug=organization_id_or_slug, issue_id=issue_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_issue", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_issue",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def update_issue(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    issue_id: str = Field(..., description="The unique identifier of the issue to update."),
    status: str | None = Field(None, description="The new status for the issue. Must be one of: resolved, resolvedInNextRelease, unresolved, or ignored."),
    assigned_to: str | None = Field(None, alias="assignedTo", description="The actor identifier (user ID, username, or team ID) to assign this issue to. Use null or omit to unassign."),
    has_seen: bool | None = Field(None, alias="hasSeen", description="Mark whether the current user has viewed this issue. Only applicable when the request is made in a user context."),
    is_bookmarked: bool | None = Field(None, alias="isBookmarked", description="Mark whether the current user has bookmarked this issue. Only applicable when the request is made in a user context."),
    is_subscribed: bool | None = Field(None, alias="isSubscribed", description="Subscribe or unsubscribe the current user from workflow notifications for this issue. Only applicable when the request is made in a user context."),
    is_public: bool | None = Field(None, alias="isPublic", description="Set the issue's visibility to public (true) or private (false)."),
) -> dict[str, Any] | ToolResult:
    """Modify an issue's attributes such as status, assignment, visibility, and user-specific flags. Only the attributes provided in the request are updated; omitted fields remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAnIssueRequest(
            path=_models.UpdateAnIssueRequestPath(organization_id_or_slug=organization_id_or_slug, issue_id=issue_id),
            body=_models.UpdateAnIssueRequestBody(status=status, assigned_to=assigned_to, has_seen=has_seen, is_bookmarked=is_bookmarked, is_subscribed=is_subscribed, is_public=is_public)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_issue", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_issue",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def delete_issue(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    issue_id: str = Field(..., description="The unique identifier of the issue to be deleted."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes an individual issue from an organization. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.RemoveAnIssueRequest(
            path=_models.RemoveAnIssueRequestPath(organization_id_or_slug=organization_id_or_slug, issue_id=issue_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_issue", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_issue",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def list_organization_releases(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    query: str | None = Field(None, description="Optional filter to match releases by version prefix using a 'starts with' comparison."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all releases for a given organization, with optional filtering by version prefix."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSReleasesRequest(
            path=_models.ListAnOrganizationSReleasesRequestPath(organization_id_or_slug=organization_id_or_slug),
            query=_models.ListAnOrganizationSReleasesRequestQuery(query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_releases: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/releases/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/releases/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_releases")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_releases", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_releases",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def create_release_for_organization(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either a numeric ID or URL-friendly slug."),
    version: str = Field(..., description="A unique version identifier for this release, such as a semantic version number, commit hash, or other build identifier."),
    projects: list[str] = Field(..., description="A list of project slugs associated with this release. Order is not significant. Each item should be a valid project slug string."),
    url: str | None = Field(None, description="An optional URL pointing to the release, such as a link to the source code repository or release notes page."),
    date_released: str | None = Field(None, alias="dateReleased", description="An optional timestamp indicating when the release was deployed to production. If omitted, the current time is used. Must be in ISO 8601 date-time format."),
    refs: list[_models.CreateANewReleaseForAnOrganizationBodyRefsItem] | None = Field(None, description="An optional array of commit references for repositories included in this release. Each reference should include `repository` and `commit` (the HEAD SHA), and may optionally include `previousCommit` (the previous HEAD SHA, recommended for first-time submissions). The `commit` field can specify a range using the format `previousCommit..commit`."),
) -> dict[str, Any] | ToolResult:
    """Create a new release for an organization to enable Sentry's error reporting, source map uploads, and debug features. Releases correlate first-seen events with the code version that introduced issues."""

    # Construct request model with validation
    try:
        _request = _models.CreateANewReleaseForAnOrganizationRequest(
            path=_models.CreateANewReleaseForAnOrganizationRequestPath(organization_id_or_slug=organization_id_or_slug),
            body=_models.CreateANewReleaseForAnOrganizationRequestBody(version=version, projects=projects, url=url, date_released=date_released, refs=refs)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_release_for_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/releases/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/releases/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_release_for_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_release_for_organization", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_release_for_organization",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def list_release_files(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug name of the organization."),
    version: str = Field(..., description="The version string that uniquely identifies the release. This should match the exact version identifier used when the release was created."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all files associated with a specific release version within an organization. This returns the complete list of artifacts and source files included in that release."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSReleaseFilesRequest(
            path=_models.ListAnOrganizationSReleaseFilesRequestPath(organization_id_or_slug=organization_id_or_slug, version=version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_release_files: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/releases/{version}/files/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/releases/{version}/files/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_release_files")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_release_files", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_release_files",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def upload_release_file(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug."),
    version: str = Field(..., description="The release version identifier to associate this file with."),
    file_: str = Field(..., alias="file", description="The file content to upload, provided as binary multipart form data."),
    name: str | None = Field(None, description="The absolute path or URI where this file will be referenced (e.g., a full web URI for JavaScript files). If omitted, the original filename is used."),
    dist: str | None = Field(None, description="The distribution name to associate with this file, useful for organizing files across different build variants or platforms."),
    header: str | None = Field(None, description="HTTP headers to attach to the file, specified as key:value pairs. This parameter can be supplied multiple times to add multiple headers (e.g., to define content type or caching directives)."),
) -> dict[str, Any] | ToolResult:
    """Upload a new file to a release. Files must be submitted using multipart/form-data encoding and requests should target region-specific domains (e.g., us.sentry.io or de.sentry.io)."""

    # Construct request model with validation
    try:
        _request = _models.UploadANewOrganizationReleaseFileRequest(
            path=_models.UploadANewOrganizationReleaseFileRequestPath(organization_id_or_slug=organization_id_or_slug, version=version),
            body=_models.UploadANewOrganizationReleaseFileRequestBody(file_=file_, name=name, dist=dist, header=header)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_release_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/releases/{version}/files/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/releases/{version}/files/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_release_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_release_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_release_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def list_release_files_for_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization."),
    version: str = Field(..., description="The release version identifier, typically a semantic version string or tag that uniquely identifies the release."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all files associated with a specific release version within a project. This returns the complete list of artifacts and source files included in that release."""

    # Construct request model with validation
    try:
        _request = _models.ListAProjectSReleaseFilesRequest(
            path=_models.ListAProjectSReleaseFilesRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, version=version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_release_files_for_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/releases/{version}/files/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/releases/{version}/files/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_release_files_for_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_release_files_for_project", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_release_files_for_project",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def upload_release_file_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL slug."),
    version: str = Field(..., description="The release version identifier to associate this file with."),
    file_: str = Field(..., alias="file", description="The file content to upload as binary data via multipart form encoding."),
    name: str | None = Field(None, description="Optional absolute path or URI where this file will be referenced (e.g., full web URI for JavaScript files)."),
    dist: str | None = Field(None, description="Optional distribution name to associate with this file artifact."),
    header: str | None = Field(None, description="Optional HTTP headers to attach to the file, specified as key:value pairs. This parameter can be supplied multiple times for multiple headers (e.g., to define content type)."),
) -> dict[str, Any] | ToolResult:
    """Upload a new file artifact for a specific release version. Files must be submitted using multipart/form-data encoding and requests should target region-specific domains (e.g., us.sentry.io or de.sentry.io)."""

    # Construct request model with validation
    try:
        _request = _models.UploadANewProjectReleaseFileRequest(
            path=_models.UploadANewProjectReleaseFileRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, version=version),
            body=_models.UploadANewProjectReleaseFileRequestBody(file_=file_, name=name, dist=dist, header=header)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_release_file_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/releases/{version}/files/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/releases/{version}/files/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_release_file_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_release_file_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_release_file_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def get_release_file(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug name."),
    version: str = Field(..., description="The release version identifier, typically a semantic version string or tag name."),
    file_id: str = Field(..., description="The unique identifier of the file within the release."),
    download: bool | None = Field(None, description="Set to true to retrieve the raw file contents as a binary payload, or false (default) to receive file metadata as JSON."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific file from a release, either as file metadata or raw file contents. Use the download parameter to control whether you receive JSON metadata or the actual file data."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAnOrganizationReleaseSFileRequest(
            path=_models.RetrieveAnOrganizationReleaseSFileRequestPath(organization_id_or_slug=organization_id_or_slug, version=version, file_id=file_id),
            query=_models.RetrieveAnOrganizationReleaseSFileRequestQuery(download=download)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_release_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/releases/{version}/files/{file_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/releases/{version}/files/{file_id}/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_release_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_release_file", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_release_file",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def update_organization_release_file(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    version: str = Field(..., description="The version string that identifies the release."),
    file_id: str = Field(..., description="The unique identifier of the file to update."),
    name: str | None = Field(None, description="The new full file path or name for the release file."),
    dist: str | None = Field(None, description="The new distribution name to associate with the file."),
) -> dict[str, Any] | ToolResult:
    """Update metadata for a file associated with an organization release, such as its name or distribution identifier."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAnOrganizationReleaseFileRequest(
            path=_models.UpdateAnOrganizationReleaseFileRequestPath(organization_id_or_slug=organization_id_or_slug, version=version, file_id=file_id),
            body=_models.UpdateAnOrganizationReleaseFileRequestBody(name=name, dist=dist)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_organization_release_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/releases/{version}/files/{file_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/releases/{version}/files/{file_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_organization_release_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_organization_release_file", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_organization_release_file",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def delete_release_file(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL slug of the organization."),
    version: str = Field(..., description="The version string that uniquely identifies the release within the organization."),
    file_id: str = Field(..., description="The unique identifier of the file to be deleted from the release."),
) -> dict[str, Any] | ToolResult:
    """Permanently delete a file associated with a specific release in an organization. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnOrganizationReleaseSFileRequest(
            path=_models.DeleteAnOrganizationReleaseSFileRequestPath(organization_id_or_slug=organization_id_or_slug, version=version, file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_release_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/releases/{version}/files/{file_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/releases/{version}/files/{file_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_release_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_release_file", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_release_file",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def get_release_file_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL slug of the project within the organization."),
    version: str = Field(..., description="The version string that identifies the release (e.g., semantic version or commit hash)."),
    file_id: str = Field(..., description="The unique identifier of the file within the release."),
    download: bool | None = Field(None, description="When true, returns the raw file contents as the response payload; when false or omitted, returns file metadata as JSON."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a file associated with a specific release, either as file metadata or raw file contents depending on the download parameter."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAProjectReleaseSFileRequest(
            path=_models.RetrieveAProjectReleaseSFileRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, version=version, file_id=file_id),
            query=_models.RetrieveAProjectReleaseSFileRequestQuery(download=download)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_release_file_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/releases/{version}/files/{file_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/releases/{version}/files/{file_id}/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_release_file_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_release_file_project", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_release_file_project",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def update_release_file(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either as a numeric ID or URL-friendly slug."),
    version: str = Field(..., description="The release version identifier to target."),
    file_id: str = Field(..., description="The unique identifier of the file to update."),
    name: str | None = Field(None, description="The new full file path or name for the release file."),
    dist: str | None = Field(None, description="The new distribution name to associate with the file."),
) -> dict[str, Any] | ToolResult:
    """Update metadata for a specific file within a project release, such as its name or distribution identifier."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAProjectReleaseFileRequest(
            path=_models.UpdateAProjectReleaseFileRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, version=version, file_id=file_id),
            body=_models.UpdateAProjectReleaseFileRequestBody(name=name, dist=dist)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_release_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/releases/{version}/files/{file_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/releases/{version}/files/{file_id}/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_release_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_release_file", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_release_file",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def delete_release_file_for_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug."),
    project_id_or_slug: str = Field(..., description="The project identifier, either the numeric ID or the URL-friendly slug."),
    version: str = Field(..., description="The release version string used to identify the specific release."),
    file_id: str = Field(..., description="The unique identifier of the file to be deleted from the release."),
) -> dict[str, Any] | ToolResult:
    """Permanently delete a file associated with a specific release. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAProjectReleaseSFileRequest(
            path=_models.DeleteAProjectReleaseSFileRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, version=version, file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_release_file_for_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/releases/{version}/files/{file_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/releases/{version}/files/{file_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_release_file_for_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_release_file_for_project", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_release_file_for_project",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def list_release_commits(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    version: str = Field(..., description="The version string that uniquely identifies the release within the organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all commits associated with a specific release in an organization. This lists the commits that were included when the release version was created."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationReleaseSCommitsRequest(
            path=_models.ListAnOrganizationReleaseSCommitsRequestPath(organization_id_or_slug=organization_id_or_slug, version=version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_release_commits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/releases/{version}/commits/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/releases/{version}/commits/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_release_commits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_release_commits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_release_commits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def list_release_commits_for_project(
    organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the URL-friendly slug of the organization."),
    project_id_or_slug: str = Field(..., description="The project identifier, which can be either the numeric ID or the URL-friendly slug of the project within the organization."),
    version: str = Field(..., description="The release version identifier, typically a semantic version string or tag name that uniquely identifies the release."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all commits associated with a specific project release. This lists the commits that were included in the release version."""

    # Construct request model with validation
    try:
        _request = _models.ListAProjectReleaseSCommitsRequest(
            path=_models.ListAProjectReleaseSCommitsRequestPath(organization_id_or_slug=organization_id_or_slug, project_id_or_slug=project_id_or_slug, version=version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_release_commits_for_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/releases/{version}/commits/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/projects/{organization_id_or_slug}/{project_id_or_slug}/releases/{version}/commits/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_release_commits_for_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_release_commits_for_project", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_release_commits_for_project",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Releases
@mcp.tool()
async def list_files_changed_in_release_commits(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or the organization's URL slug. Use the slug for human-readable requests or the ID for programmatic lookups."),
    version: str = Field(..., description="The release version identifier. This should match the version tag or semantic version string used to identify the release in your system."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all files that were modified across the commits included in a specific release. This helps identify what code changes were shipped in a particular version."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveFilesChangedInAReleaseSCommitsRequest(
            path=_models.RetrieveFilesChangedInAReleaseSCommitsRequestPath(organization_id_or_slug=organization_id_or_slug, version=version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_files_changed_in_release_commits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/releases/{version}/commitfiles/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/releases/{version}/commitfiles/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_files_changed_in_release_commits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_files_changed_in_release_commits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_files_changed_in_release_commits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration
@mcp.tool()
async def list_organization_sentry_app_installations(organization_id_or_slug: str = Field(..., description="The organization identifier, which can be either the numeric ID or the organization's URL slug (short name). Use the slug for human-readable references or the ID for programmatic lookups.")) -> dict[str, Any] | ToolResult:
    """Retrieve all integration platform (Sentry App) installations configured for a specific organization. This returns the list of third-party integrations that have been installed and are active within the organization."""

    # Construct request model with validation
    try:
        _request = _models.ListAnOrganizationSIntegrationPlatformInstallationsRequest(
            path=_models.ListAnOrganizationSIntegrationPlatformInstallationsRequestPath(organization_id_or_slug=organization_id_or_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_sentry_app_installations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/sentry-app-installations/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/sentry-app-installations/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_sentry_app_installations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_sentry_app_installations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_sentry_app_installations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration
@mcp.tool()
async def create_or_update_external_issue(
    uuid_: str = Field(..., alias="uuid", description="The unique identifier of the integration platform installation that will handle the external issue creation or update."),
    issue_id: int = Field(..., alias="issueId", description="The numeric ID of the Sentry issue to link with the external issue."),
    web_url: str = Field(..., alias="webUrl", description="The full URL of the external issue in the integrated service (e.g., the direct link to the issue in the external tracker)."),
    project: str = Field(..., description="The project identifier or key in the external service where the issue exists or will be created."),
    identifier: str = Field(..., description="A unique identifier for the external issue within the external service (e.g., issue number, ticket ID, or key). This is used to prevent duplicate creations and to identify the issue for updates."),
) -> dict[str, Any] | ToolResult:
    """Create or update an external issue linked to a Sentry issue through an integration platform installation. This establishes a bidirectional link between a Sentry issue and an external service's issue tracker."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrUpdateAnExternalIssueRequest(
            path=_models.CreateOrUpdateAnExternalIssueRequestPath(uuid_=uuid_),
            body=_models.CreateOrUpdateAnExternalIssueRequestBody(issue_id=issue_id, web_url=web_url, project=project, identifier=identifier)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_or_update_external_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/sentry-app-installations/{uuid}/external-issues/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/sentry-app-installations/{uuid}/external-issues/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_or_update_external_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_or_update_external_issue", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_or_update_external_issue",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration
@mcp.tool()
async def delete_external_issue(
    uuid_: str = Field(..., alias="uuid", description="The unique identifier of the Sentry app installation (integration platform integration) that owns the external issue."),
    external_issue_id: str = Field(..., description="The unique identifier of the external issue to delete from the integration platform."),
) -> dict[str, Any] | ToolResult:
    """Delete an external issue linked to a Sentry app installation. This removes the association between the external issue and the integration platform."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnExternalIssueRequest(
            path=_models.DeleteAnExternalIssueRequestPath(uuid_=uuid_, external_issue_id=external_issue_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_external_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/sentry-app-installations/{uuid}/external-issues/{external_issue_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/sentry-app-installations/{uuid}/external-issues/{external_issue_id}/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_external_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_external_issue", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_external_issue",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def enable_spike_protection_for_projects(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug. This determines which organization's projects will have Spike Protection enabled."),
    projects: list[str] = Field(..., description="Array of project slugs to enable Spike Protection for. Use the special value `$all` to enable Spike Protection across all projects in the organization, or provide specific project slugs as an array of strings."),
) -> dict[str, Any] | ToolResult:
    """Enables Spike Protection feature for specified projects within an organization. Spike Protection helps manage error rate spikes by automatically adjusting error sampling thresholds."""

    # Construct request model with validation
    try:
        _request = _models.EnableSpikeProtectionRequest(
            path=_models.EnableSpikeProtectionRequestPath(organization_id_or_slug=organization_id_or_slug),
            body=_models.EnableSpikeProtectionRequestBody(projects=projects)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for enable_spike_protection_for_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/spike-protections/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/spike-protections/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("enable_spike_protection_for_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("enable_spike_protection_for_projects", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="enable_spike_protection_for_projects",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def disable_spike_protection_for_projects(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug of the organization containing the projects."),
    projects: list[str] = Field(..., description="Array of project slugs to disable Spike Protection for. Use the special value `$all` to disable Spike Protection for all projects in the organization at once."),
) -> dict[str, Any] | ToolResult:
    """Disables Spike Protection for specified projects within an organization. Use the special value `$all` to disable Spike Protection across all projects in the organization."""

    # Construct request model with validation
    try:
        _request = _models.DisableSpikeProtectionRequest(
            path=_models.DisableSpikeProtectionRequestPath(organization_id_or_slug=organization_id_or_slug),
            body=_models.DisableSpikeProtectionRequestBody(projects=projects)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for disable_spike_protection_for_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/spike-protections/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/spike-protections/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("disable_spike_protection_for_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("disable_spike_protection_for_projects", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="disable_spike_protection_for_projects",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Seer
@mcp.tool()
async def get_issue_autofix_state(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug. Required to scope the issue within the correct organization."),
    issue_id: int = Field(..., description="The numeric identifier of the issue. Required to retrieve the specific autofix state for that issue."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the current state and progress of an automated fix process for a specific issue, including status, completed steps, root cause analysis, proposed solution, and generated code changes. Note: This endpoint is experimental and the response structure may change."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveSeerIssueFixStateRequest(
            path=_models.RetrieveSeerIssueFixStateRequestPath(organization_id_or_slug=organization_id_or_slug, issue_id=issue_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_issue_autofix_state: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/autofix/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/autofix/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_issue_autofix_state")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_issue_autofix_state", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_issue_autofix_state",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Seer
@mcp.tool()
async def trigger_issue_autofix(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug of the organization."),
    issue_id: int = Field(..., description="The numeric ID of the issue to analyze and fix."),
    event_id: str | None = Field(None, description="Optional event ID to analyze. If omitted, the system will use the recommended event for the issue."),
    instruction: str | None = Field(None, description="Optional custom instruction to guide the autofix analysis and solution generation process."),
    pr_to_comment_on_url: str | None = Field(None, description="Optional URL of a pull request where the autofix should post comments with findings and recommendations."),
    stopping_point: Literal["root_cause", "solution", "code_changes", "open_pr"] | None = Field(None, description="Optional stopping point for the autofix process. Defaults to root cause analysis if not specified. Valid stages are: root_cause (stop after identifying the cause), solution (stop after proposing a fix), code_changes (stop after generating code), or open_pr (complete the process by creating a pull request)."),
) -> dict[str, Any] | ToolResult:
    """Trigger an automated issue fix analysis that identifies root causes, proposes solutions, generates code changes, and optionally creates a pull request. The process runs asynchronously and can be monitored via the GET endpoint."""

    # Construct request model with validation
    try:
        _request = _models.StartSeerIssueFixRequest(
            path=_models.StartSeerIssueFixRequestPath(organization_id_or_slug=organization_id_or_slug, issue_id=issue_id),
            body=_models.StartSeerIssueFixRequestBody(event_id=event_id, instruction=instruction, pr_to_comment_on_url=pr_to_comment_on_url, stopping_point=stopping_point)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for trigger_issue_autofix: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/autofix/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/autofix/"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("trigger_issue_autofix")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("trigger_issue_autofix", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="trigger_issue_autofix",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def list_issue_events(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug."),
    issue_id: int = Field(..., description="The numeric ID of the issue to retrieve events for."),
    environment: list[str] | None = Field(None, description="Filter events to only those from specified environments. Provide as an array of environment names."),
    full: bool | None = Field(None, description="Set to true to include complete event details such as stack traces and breadcrumbs. Defaults to false for lighter payloads."),
    sample: bool | None = Field(None, description="Set to true to return events in pseudo-random but deterministic order, ensuring consistent results across identical queries."),
    query: str | None = Field(None, description="Filter events using Sentry's search syntax. Supports queries like `transaction:foo AND release:abc`. Refer to Sentry's search documentation for available event properties and operators."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of error events associated with a specific issue. Optionally filter by environment, search criteria, or request full event details including stack traces."""

    # Construct request model with validation
    try:
        _request = _models.ListAnIssueSEventsRequest(
            path=_models.ListAnIssueSEventsRequestPath(organization_id_or_slug=organization_id_or_slug, issue_id=issue_id),
            query=_models.ListAnIssueSEventsRequestQuery(environment=environment, full=full, sample=sample, query=query)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_issue_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/events/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/events/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_issue_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_issue_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_issue_events",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def get_issue_event(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL-friendly slug (e.g., 'my-org'). This determines which organization's resources are accessed."),
    issue_id: int = Field(..., description="The numeric ID of the issue containing the event you want to retrieve."),
    event_id: Literal["latest", "oldest", "recommended"] = Field(..., description="The event identifier to retrieve. Accepts a specific event ID or one of three special values: 'latest' for the most recent event, 'oldest' for the first event, or 'recommended' for a system-suggested event."),
    environment: list[str] | None = Field(None, description="Optional filter to limit results to events from specific environments. Provide as a list of environment names; events matching any of the specified environments will be included."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific event associated with an issue, such as comments, status changes, or assignments. You can fetch a particular event by ID or retrieve special event references like the latest, oldest, or recommended event."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAnIssueEventRequest(
            path=_models.RetrieveAnIssueEventRequestPath(organization_id_or_slug=organization_id_or_slug, issue_id=issue_id, event_id=event_id),
            query=_models.RetrieveAnIssueEventRequestQuery(environment=environment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_issue_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/events/{event_id}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/events/{event_id}/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_issue_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_issue_event", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_issue_event",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Integration
@mcp.tool()
async def list_external_issues_for_issue(
    organization_id_or_slug: str = Field(..., description="The organization identifier, either the numeric ID or the URL slug. Use the slug for human-readable references or the ID for programmatic lookups."),
    issue_id: int = Field(..., description="The numeric ID of the Sentry issue. Must be a positive integer representing a valid issue within the organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all custom integration issue links (external issues) associated with a specific Sentry issue. This shows connections between the Sentry issue and external tracking systems."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveCustomIntegrationIssueLinksForTheGivenSentryIssueRequest(
            path=_models.RetrieveCustomIntegrationIssueLinksForTheGivenSentryIssueRequestPath(organization_id_or_slug=organization_id_or_slug, issue_id=issue_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_external_issues_for_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/external-issues/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/external-issues/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_external_issues_for_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_external_issues_for_issue", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_external_issues_for_issue",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Events
@mcp.tool()
async def get_tag_values_for_issue(
    issue_id: int = Field(..., description="The numeric identifier of the issue to query for tag values."),
    organization_id_or_slug: str = Field(..., description="The organization identifier, either as a numeric ID or URL-friendly slug."),
    key: str = Field(..., description="The tag key name to retrieve associated values for."),
    environment: list[str] | None = Field(None, description="Optional list of environment names to filter tag values by. When specified, only values from the listed environments are returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all values associated with a specific tag key for an issue, with optional filtering by environment. Results are paginated and return at most 1000 values."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveTagDetailsRequest(
            path=_models.RetrieveTagDetailsRequestPath(issue_id=issue_id, organization_id_or_slug=organization_id_or_slug, key=key),
            query=_models.RetrieveTagDetailsRequestQuery(environment=environment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_tag_values_for_issue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/tags/{key}/", _request.path.model_dump(by_alias=True)) if _request.path else "/api/0/organizations/{organization_id_or_slug}/issues/{issue_id}/tags/{key}/"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_tag_values_for_issue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_tag_values_for_issue", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_tag_values_for_issue",
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
        print("  python api_reference_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="API Reference MCP Server")

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
    logger.info("Starting API Reference MCP Server")
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

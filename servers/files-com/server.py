#!/usr/bin/env python3
"""
Files.com MCP Server

API Info:
- Contact: Files.com Customer Success Team <support@files.com>

Generated: 2026-05-05 14:57:39 UTC
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
from pydantic import Field

# Server variables (from OpenAPI spec, overridable via SERVER_* env vars)
_SERVER_VARS = {
    "subdomain": os.getenv("SERVER_SUBDOMAIN", ""),
}
BASE_URL = os.getenv("BASE_URL", "https://{subdomain}.files.com/api/rest/v1".format_map(collections.defaultdict(str, _SERVER_VARS)))
SERVER_NAME = "Files.com"
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

def build_destinations(destination_paths: list[str] | None = None, destination_folders: list[dict] | None = None) -> list | None:
    """Helper function for parameter transformation"""
    if destination_paths is None and destination_folders is None:
        return None

    result = []

    if destination_paths:
        result.extend(destination_paths)

    if destination_folders:
        for folder_obj in destination_folders:
            if not isinstance(folder_obj, dict) or 'folder_path' not in folder_obj:
                raise ValueError(f"Each destination folder must be a dict with 'folder_path' key") from None
            result.append(folder_obj)

    return result if result else None

def build_schedule(schedule_days: list[str] | None = None, schedule_times: list[str] | None = None, schedule_timezone: str | None = None) -> dict | None:
    """Helper function for parameter transformation"""
    if schedule_days is None and schedule_times is None and schedule_timezone is None:
        return None

    schedule_obj = {}

    if schedule_days is not None:
        schedule_obj['days'] = schedule_days

    if schedule_times is not None:
        schedule_obj['times'] = schedule_times

    if schedule_timezone is not None:
        schedule_obj['timezone'] = schedule_timezone

    return schedule_obj if schedule_obj else None

def build_sort_by(sort_field: str | None = None, sort_direction: str | None = None) -> dict | None:
    """Helper function for parameter transformation"""
    if sort_field is None and sort_direction is None:
        return None
    if sort_field is None or sort_direction is None:
        raise ValueError("Both sort_field and sort_direction must be provided together") from None
    valid_fields = {'path', 'folder', 'user_id', 'created_at'}
    valid_directions = {'asc', 'desc'}
    if sort_field not in valid_fields:
        raise ValueError(f"Invalid sort_field '{sort_field}'. Valid fields: {', '.join(sorted(valid_fields))}") from None
    if sort_direction not in valid_directions:
        raise ValueError(f"Invalid sort_direction '{sort_direction}'. Valid directions: {', '.join(sorted(valid_directions))}") from None
    return {sort_field: sort_direction}

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
    'api_key',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["api_key"] = _auth.APIKeyAuth(env_var="API_KEY", location="header", param_name="X-FilesAPI-Key")
    logging.info("Authentication configured: api_key")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for api_key not configured: {error_msg}")
    _auth_handlers["api_key"] = None

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

mcp = FastMCP("Files.com", middleware=[_JsonCoercionMiddleware()])

# Tags: action_notification_export_results
@mcp.tool()
async def list_action_notification_export_results(
    action_notification_export_id: str = Field(..., description="The unique identifier of the action notification export whose results you want to retrieve."),
    per_page: str | None = Field(None, description="Maximum number of records to return per page. Recommended to use 1,000 or less for optimal performance."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of results from a specific action notification export. Use the export ID to filter results and control pagination with per_page."""

    _action_notification_export_id = _parse_int(action_notification_export_id)
    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetActionNotificationExportResultsRequest(
            query=_models.GetActionNotificationExportResultsRequestQuery(per_page=_per_page, action_notification_export_id=_action_notification_export_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_action_notification_export_results: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/action_notification_export_results"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_action_notification_export_results")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_action_notification_export_results", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_action_notification_export_results",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: action_notification_exports
@mcp.tool()
async def export_action_notifications(
    end_at: str | None = Field(None, description="End date and time for the export range (inclusive). Notifications triggered after this timestamp will be excluded."),
    query_folder: str | None = Field(None, description="Filter to notifications triggered by actions within a specific folder. Useful for isolating notifications from a particular directory."),
    query_message: str | None = Field(None, description="Filter to notifications with a specific error message. Helps identify notifications that failed with particular error conditions."),
    query_path: str | None = Field(None, description="Filter to notifications triggered by actions on a specific file or resource path. Use to track notifications for a particular file."),
    query_request_method: str | None = Field(None, description="Filter by the HTTP method used in the webhook request (e.g., GET, POST, PUT). Narrows results to notifications sent with a specific request method."),
    query_request_url: str | None = Field(None, description="Filter by the target webhook URL. Use to isolate notifications sent to a specific endpoint."),
    query_status: str | None = Field(None, description="Filter by the HTTP status code returned from the webhook server. Helps identify notifications that received specific response codes."),
    query_success: bool | None = Field(None, description="Filter by webhook delivery success. Set to true for successful deliveries (HTTP 200 or 204 responses) or false for failed deliveries."),
    start_at: str | None = Field(None, description="Start date and time for the export range (inclusive). Notifications triggered before this timestamp will be excluded."),
) -> dict[str, Any] | ToolResult:
    """Generate an export of action notification records filtered by date range, folder, file path, webhook configuration, and delivery status. Use this to audit webhook delivery history and troubleshoot notification failures."""

    # Construct request model with validation
    try:
        _request = _models.PostActionNotificationExportsRequest(
            body=_models.PostActionNotificationExportsRequestBody(end_at=end_at, query_folder=query_folder, query_message=query_message, query_path=query_path, query_request_method=query_request_method, query_request_url=query_request_url, query_status=query_status, query_success=query_success, start_at=start_at)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_action_notifications: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/action_notification_exports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_action_notifications")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_action_notifications", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_action_notifications",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: action_notification_exports
@mcp.tool()
async def get_action_notification_export(id_: str = Field(..., alias="id", description="The unique identifier of the action notification export to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details of a specific action notification export by its ID. Use this to view the status, configuration, and results of a previously created notification export."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetActionNotificationExportsIdRequest(
            path=_models.GetActionNotificationExportsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_action_notification_export: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/action_notification_exports/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/action_notification_exports/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_action_notification_export")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_action_notification_export", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_action_notification_export",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: action_webhook_failures
@mcp.tool()
async def retry_webhook_failure(id_: str = Field(..., alias="id", description="The unique identifier of the action webhook failure to retry.")) -> dict[str, Any] | ToolResult:
    """Retry a failed action webhook by its failure ID. This operation allows you to re-attempt delivery of a webhook that previously failed."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PostActionWebhookFailuresIdRetryRequest(
            path=_models.PostActionWebhookFailuresIdRetryRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for retry_webhook_failure: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/action_webhook_failures/{id}/retry", _request.path.model_dump(by_alias=True)) if _request.path else "/action_webhook_failures/{id}/retry"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("retry_webhook_failure")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("retry_webhook_failure", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="retry_webhook_failure",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: api_key
@mcp.tool()
async def get_current_api_key() -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about the API key currently being used for authentication. This operation requires the API connection to be authenticated using an API key rather than other authentication methods."""

    # Extract parameters for API call
    _http_path = "/api_key"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_current_api_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_current_api_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_current_api_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: api_keys
@mcp.tool()
async def list_api_keys(
    per_page: str | None = Field(None, description="Number of API keys to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort the results by a specified field in ascending or descending order. Supports sorting by expiration date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of API keys with optional sorting by expiration date. Use this to view all API keys associated with your account."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetApiKeysRequest(
            query=_models.GetApiKeysRequestQuery(per_page=_per_page, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_api_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api_keys"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_api_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_api_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_api_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: api_keys
@mcp.tool()
async def create_api_key(
    description: str | None = Field(None, description="A user-supplied description to help identify the purpose or context of this API key."),
    expires_at: str | None = Field(None, description="The date and time when this API key will automatically expire and become invalid. Specify in ISO 8601 format."),
    name: str | None = Field(None, description="An internal name for this API key for your own reference and organization."),
    permission_set: Literal["none", "full", "desktop_app", "sync_app", "office_integration", "mobile_app"] | None = Field(None, description="The permission level for this API key. `full` grants complete API access, `desktop_app` restricts to file and share link operations, `sync_app` for sync functionality, `office_integration` for office tools, and `mobile_app` for mobile access. `none` grants no permissions."),
) -> dict[str, Any] | ToolResult:
    """Create a new API key for programmatic access to the API. Configure the key's name, expiration date, description, and permission level to control its capabilities."""

    # Construct request model with validation
    try:
        _request = _models.PostApiKeysRequest(
            body=_models.PostApiKeysRequestBody(description=description, expires_at=expires_at, name=name, permission_set=permission_set)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_api_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/api_keys"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_api_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_api_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_api_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: api_keys
@mcp.tool()
async def get_api_key(id_: str = Field(..., alias="id", description="The unique identifier of the API key to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific API key by its ID. Use this to view details of an existing API key in your account."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetApiKeysIdRequest(
            path=_models.GetApiKeysIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_api_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api_keys/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api_keys/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_api_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_api_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_api_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: api_keys
@mcp.tool()
async def update_api_key_by_id(
    id_: str = Field(..., alias="id", description="The unique identifier of the API key to update."),
    description: str | None = Field(None, description="A user-supplied description to help identify the purpose or context of this API key."),
    expires_at: str | None = Field(None, description="The date and time when this API key will expire and become invalid."),
    name: str | None = Field(None, description="An internal name for the API key to help you organize and identify it."),
    permission_set: Literal["none", "full", "desktop_app", "sync_app", "office_integration", "mobile_app"] | None = Field(None, description="The permission set determines what operations this API key can perform. Desktop app keys are limited to file and share link operations, while full keys have unrestricted access."),
) -> dict[str, Any] | ToolResult:
    """Update an existing API key's configuration including name, description, expiration date, and permission set."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PatchApiKeysIdRequest(
            path=_models.PatchApiKeysIdRequestPath(id_=_id_),
            body=_models.PatchApiKeysIdRequestBody(description=description, expires_at=expires_at, name=name, permission_set=permission_set)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_api_key_by_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api_keys/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api_keys/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_api_key_by_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_api_key_by_id", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_api_key_by_id",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: api_keys
@mcp.tool()
async def delete_api_key(id_: str = Field(..., alias="id", description="The unique identifier of the API key to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete an API key by its ID. This action cannot be undone and will immediately revoke access for any integrations using this key."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteApiKeysIdRequest(
            path=_models.DeleteApiKeysIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_api_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/api_keys/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/api_keys/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_api_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_api_key", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_api_key",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: apps
@mcp.tool()
async def list_apps(
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, though the API supports up to 10,000 records per page."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Valid sortable fields are `name` and `app_type`. Specify the field name as the key and the direction (asc or desc) as the value."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of all apps with optional sorting capabilities. Use pagination parameters to control result size and sorting to organize results by name or app type."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetAppsRequest(
            query=_models.GetAppsRequestQuery(per_page=_per_page, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_apps: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/apps"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_apps")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_apps", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_apps",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: as2_incoming_messages
@mcp.tool()
async def list_as2_incoming_messages(
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Valid fields are `created_at` and `as2_partner_id`."),
    as2_partner_id: str | None = Field(None, description="Filter messages by a specific AS2 partner ID. When provided, only messages from that partner will be returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of incoming AS2 messages, optionally filtered by AS2 partner and sorted by specified fields. Supports pagination for managing large result sets."""

    _per_page = _parse_int(per_page)
    _as2_partner_id = _parse_int(as2_partner_id)

    # Construct request model with validation
    try:
        _request = _models.GetAs2IncomingMessagesRequest(
            query=_models.GetAs2IncomingMessagesRequestQuery(per_page=_per_page, sort_by=sort_by, as2_partner_id=_as2_partner_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_as2_incoming_messages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/as2_incoming_messages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_as2_incoming_messages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_as2_incoming_messages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_as2_incoming_messages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: as2_outgoing_messages
@mcp.tool()
async def list_as2_outgoing_messages(
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Supported fields are `created_at` and `as2_partner_id`."),
    as2_partner_id: str | None = Field(None, description="Filter results to messages associated with a specific AS2 partner. If omitted, returns messages from all partners."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of outgoing AS2 messages, optionally filtered by AS2 partner and sorted by specified fields. Useful for monitoring message delivery status and history."""

    _per_page = _parse_int(per_page)
    _as2_partner_id = _parse_int(as2_partner_id)

    # Construct request model with validation
    try:
        _request = _models.GetAs2OutgoingMessagesRequest(
            query=_models.GetAs2OutgoingMessagesRequestQuery(per_page=_per_page, sort_by=sort_by, as2_partner_id=_as2_partner_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_as2_outgoing_messages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/as2_outgoing_messages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_as2_outgoing_messages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_as2_outgoing_messages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_as2_outgoing_messages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: as2_partners
@mcp.tool()
async def list_as2_partners(per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of AS2 partners configured in the system. Use the per_page parameter to control result set size."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetAs2PartnersRequest(
            query=_models.GetAs2PartnersRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_as2_partners: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/as2_partners"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_as2_partners")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_as2_partners", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_as2_partners",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: as2_partners
@mcp.tool()
async def create_as2_partner(
    as2_station_id: str = Field(..., description="The ID of the AS2 station that this partner will be associated with."),
    name: str = Field(..., description="The AS2 identifier name for this partner, used in AS2 message headers for partner identification."),
    public_certificate: str = Field(..., description="The public certificate in PEM format used to verify signatures and encrypt messages from this partner."),
    uri: str = Field(..., description="The base URL where AS2 responses and acknowledgments will be sent to this partner."),
    server_certificate: str | None = Field(None, description="The remote server's certificate for validating secure connections to the partner's AS2 endpoint."),
) -> dict[str, Any] | ToolResult:
    """Create a new AS2 partner configuration for secure EDI communication. Requires an associated AS2 station and partner identification details including certificates and response URI."""

    _as2_station_id = _parse_int(as2_station_id)

    # Construct request model with validation
    try:
        _request = _models.PostAs2PartnersRequest(
            body=_models.PostAs2PartnersRequestBody(as2_station_id=_as2_station_id, name=name, public_certificate=public_certificate, server_certificate=server_certificate, uri=uri)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_as2_partner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/as2_partners"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_as2_partner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_as2_partner", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_as2_partner",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: as2_partners
@mcp.tool()
async def get_as2_partner(id_: str = Field(..., alias="id", description="The unique identifier of the AS2 partner to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details for a specific AS2 partner by ID. Returns the partner's configuration and connection information."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetAs2PartnersIdRequest(
            path=_models.GetAs2PartnersIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_as2_partner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/as2_partners/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/as2_partners/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_as2_partner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_as2_partner", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_as2_partner",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: as2_partners
@mcp.tool()
async def update_as2_partner(
    id_: str = Field(..., alias="id", description="The unique identifier of the AS2 partner to update."),
    name: str | None = Field(None, description="The AS2 partner's display name or identifier."),
    public_certificate: str | None = Field(None, description="The public certificate used for verifying signatures and encrypting messages from this AS2 partner."),
    server_certificate: str | None = Field(None, description="The remote server's certificate for establishing secure connections and validating the AS2 partner's identity."),
    uri: str | None = Field(None, description="The base URL where AS2 responses and acknowledgments should be sent to this partner."),
) -> dict[str, Any] | ToolResult:
    """Update an AS2 partner's configuration including name, certificates, and response URI. Allows modification of existing AS2 partner settings for secure EDI communication."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PatchAs2PartnersIdRequest(
            path=_models.PatchAs2PartnersIdRequestPath(id_=_id_),
            body=_models.PatchAs2PartnersIdRequestBody(name=name, public_certificate=public_certificate, server_certificate=server_certificate, uri=uri)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_as2_partner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/as2_partners/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/as2_partners/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_as2_partner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_as2_partner", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_as2_partner",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: as2_partners
@mcp.tool()
async def delete_as2_partner(id_: str = Field(..., alias="id", description="The unique identifier of the AS2 partner to delete.")) -> dict[str, Any] | ToolResult:
    """Delete an AS2 partner configuration. This operation permanently removes the specified AS2 partner from the system."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteAs2PartnersIdRequest(
            path=_models.DeleteAs2PartnersIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_as2_partner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/as2_partners/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/as2_partners/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_as2_partner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_as2_partner", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_as2_partner",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: as2_stations
@mcp.tool()
async def list_as2_stations(per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of AS2 stations. Use the per_page parameter to control the number of records returned per page."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetAs2StationsRequest(
            query=_models.GetAs2StationsRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_as2_stations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/as2_stations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_as2_stations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_as2_stations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_as2_stations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: as2_stations
@mcp.tool()
async def create_as2_station(
    name: str = Field(..., description="The name identifier for the AS2 station. Used to reference this station in AS2 communications and configurations."),
    private_key: str = Field(..., description="The private key used for signing outbound AS2 messages and decrypting inbound messages. Must be in PEM format."),
    public_certificate: str = Field(..., description="The public certificate corresponding to the private key, used for message authentication and encryption verification. Must be in PEM or DER format."),
    private_key_password: str | None = Field(None, description="Optional password protecting the private key. Required if the private key is encrypted."),
) -> dict[str, Any] | ToolResult:
    """Create a new AS2 station for secure EDI communication. Requires cryptographic credentials including a private key and public certificate for message signing and encryption."""

    # Construct request model with validation
    try:
        _request = _models.PostAs2StationsRequest(
            body=_models.PostAs2StationsRequestBody(name=name, private_key=private_key, private_key_password=private_key_password, public_certificate=public_certificate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_as2_station: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/as2_stations"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_as2_station")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_as2_station", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_as2_station",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: as2_stations
@mcp.tool()
async def get_as2_station(id_: str = Field(..., alias="id", description="The unique identifier of the AS2 station to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details for a specific AS2 station by its ID. Returns the configuration and status information for the AS2 station."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetAs2StationsIdRequest(
            path=_models.GetAs2StationsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_as2_station: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/as2_stations/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/as2_stations/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_as2_station")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_as2_station", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_as2_station",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: as2_stations
@mcp.tool()
async def update_as2_station(
    id_: str = Field(..., alias="id", description="The unique identifier of the AS2 station to update."),
    name: str | None = Field(None, description="The AS2 station name or identifier."),
    private_key: str | None = Field(None, description="The private key used for signing AS2 messages."),
    private_key_password: str | None = Field(None, description="The password protecting the private key."),
    public_certificate: str | None = Field(None, description="The public certificate used for verifying AS2 message signatures."),
) -> dict[str, Any] | ToolResult:
    """Update an AS2 station configuration including its name, private key, and public certificate credentials."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PatchAs2StationsIdRequest(
            path=_models.PatchAs2StationsIdRequestPath(id_=_id_),
            body=_models.PatchAs2StationsIdRequestBody(name=name, private_key=private_key, private_key_password=private_key_password, public_certificate=public_certificate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_as2_station: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/as2_stations/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/as2_stations/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_as2_station")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_as2_station", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_as2_station",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: as2_stations
@mcp.tool()
async def delete_as2_station(id_: str = Field(..., alias="id", description="The unique identifier of the AS2 station to delete.")) -> dict[str, Any] | ToolResult:
    """Delete an AS2 station by its ID. This operation permanently removes the AS2 station configuration and cannot be undone."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteAs2StationsIdRequest(
            path=_models.DeleteAs2StationsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_as2_station: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/as2_stations/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/as2_stations/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_as2_station")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_as2_station", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_as2_station",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: automation_runs
@mcp.tool()
async def list_automation_runs(
    automation_id: str = Field(..., description="The ID of the automation whose runs you want to list."),
    per_page: str | None = Field(None, description="Maximum number of records to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Supported fields are `created_at` and `status`."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of automation runs for a specific automation. Filter, sort, and control pagination to find the runs you need."""

    _automation_id = _parse_int(automation_id)
    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetAutomationRunsRequest(
            query=_models.GetAutomationRunsRequestQuery(per_page=_per_page, sort_by=sort_by, automation_id=_automation_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_automation_runs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/automation_runs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_automation_runs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_automation_runs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_automation_runs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: automation_runs
@mcp.tool()
async def get_automation_run(id_: str = Field(..., alias="id", description="The unique identifier of the automation run to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details of a specific automation run by its ID. Returns the current state, execution history, and results of the automation run."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetAutomationRunsIdRequest(
            path=_models.GetAutomationRunsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_automation_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/automation_runs/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/automation_runs/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_automation_run")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_automation_run", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_automation_run",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: automations
@mcp.tool()
async def list_automations(
    per_page: str | None = Field(None, description="Number of automation records to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 is supported."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Valid sortable fields are: automation, disabled, last_modified_at, or name."),
    with_deleted: bool | None = Field(None, description="Include deleted automations in the results. Set to true to show all automations including those that have been deleted."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of automations with optional filtering and sorting. Use this to view all automations in your account, including deleted ones if needed."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetAutomationsRequest(
            query=_models.GetAutomationsRequestQuery(per_page=_per_page, sort_by=sort_by, with_deleted=with_deleted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_automations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/automations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_automations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_automations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_automations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: automations
@mcp.tool()
async def get_automation(id_: str = Field(..., alias="id", description="The unique identifier of the automation to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details for a specific automation by its ID. Returns the automation configuration and current state."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetAutomationsIdRequest(
            path=_models.GetAutomationsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_automation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/automations/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/automations/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_automation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_automation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_automation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: automations
@mcp.tool()
async def update_automation(
    id_: str = Field(..., alias="id", description="The unique identifier of the automation to update."),
    description: str | None = Field(None, description="A descriptive label for this automation."),
    disabled: bool | None = Field(None, description="When true, prevents this automation from executing."),
    interval: str | None = Field(None, description="The execution frequency for this automation. Determines how often the automation runs based on calendar intervals."),
    name: str | None = Field(None, description="A human-readable name for this automation."),
    source: str | None = Field(None, description="The source path associated with this automation."),
    sync_ids: str | None = Field(None, description="Comma-separated list of sync IDs this automation is associated with."),
    trigger: Literal["realtime", "daily", "custom_schedule", "webhook", "email", "action"] | None = Field(None, description="The mechanism that initiates automation execution. Determines whether the automation runs on a schedule, in response to events, or via external triggers."),
    trigger_actions: list[str] | None = Field(None, description="When trigger is set to 'action', specifies which action types activate the automation. Valid actions include create, read, update, destroy, move, and copy operations."),
    user_ids: str | None = Field(None, description="Comma-separated list of user IDs this automation is associated with."),
    value: dict[str, Any] | None = Field(None, description="A structured object containing automation type-specific configuration parameters and settings."),
    destination_paths: list[str] | None = Field(None, description="List of simple destination path strings"),
    destination_folders: list[dict[str, Any]] | None = Field(None, description="List of destination folder objects with 'folder_path' (required) and optional 'file_path' keys"),
    schedule_days: list[str] | None = Field(None, description="Days of week for the schedule (e.g., 'monday', 'tuesday')"),
    schedule_times: list[str] | None = Field(None, description="Times in HH:MM format for the schedule"),
    schedule_timezone: str | None = Field(None, description="Timezone for the schedule (e.g., 'UTC', 'America/New_York')"),
) -> dict[str, Any] | ToolResult:
    """Update an existing automation configuration. Modify automation properties such as schedule, trigger type, associated syncs/users, and behavior settings."""

    # Call helper functions
    destinations = build_destinations(destination_paths, destination_folders)
    schedule = build_schedule(schedule_days, schedule_times, schedule_timezone)

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PatchAutomationsIdRequest(
            path=_models.PatchAutomationsIdRequestPath(id_=_id_),
            body=_models.PatchAutomationsIdRequestBody(description=description, disabled=disabled, interval=interval, name=name, source=source, sync_ids=sync_ids, trigger=trigger, trigger_actions=trigger_actions, user_ids=user_ids, value=value, destinations=destinations, schedule=schedule)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_automation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/automations/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/automations/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_automation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_automation", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_automation",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: automations
@mcp.tool()
async def delete_automation(id_: str = Field(..., alias="id", description="The unique identifier of the automation to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete an automation by its ID. This action cannot be undone."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteAutomationsIdRequest(
            path=_models.DeleteAutomationsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_automation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/automations/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/automations/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_automation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_automation", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_automation",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: bandwidth_snapshots
@mcp.tool()
async def list_bandwidth_snapshots(
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Use the field name as the key and 'asc' or 'desc' as the value. Valid sortable field is 'logged_at'."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of bandwidth snapshots. Results can be sorted by the logged timestamp in ascending or descending order."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetBandwidthSnapshotsRequest(
            query=_models.GetBandwidthSnapshotsRequestQuery(per_page=_per_page, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bandwidth_snapshots: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bandwidth_snapshots"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bandwidth_snapshots")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bandwidth_snapshots", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bandwidth_snapshots",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: behaviors
@mcp.tool()
async def list_behaviors_by_path(
    path: str = Field(..., description="The folder path where behaviors are located. This path determines the starting point for the behavior listing."),
    per_page: str | None = Field(None, description="Maximum number of behavior records to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by the behavior field in ascending or descending order. Specify as an object with the field name as key and sort direction as value."),
    recursive: str | None = Field(None, description="Include behaviors from parent directories above the specified path when enabled. Controls whether the listing is limited to the exact path or includes the hierarchy above it."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of behaviors from a specified folder path, with optional filtering, sorting, and recursive traversal capabilities."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.BehaviorListForPathRequest(
            path=_models.BehaviorListForPathRequestPath(path=path),
            query=_models.BehaviorListForPathRequestQuery(per_page=_per_page, sort_by=sort_by, recursive=recursive)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_behaviors_by_path: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/behaviors/folders/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/behaviors/folders/{path}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_behaviors_by_path")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_behaviors_by_path", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_behaviors_by_path",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: behaviors
@mcp.tool()
async def get_behavior(id_: str = Field(..., alias="id", description="The unique identifier of the behavior to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific behavior by its ID."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetBehaviorsIdRequest(
            path=_models.GetBehaviorsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_behavior: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/behaviors/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/behaviors/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_behavior")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_behavior", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_behavior",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: behaviors
@mcp.tool()
async def delete_behavior(id_: str = Field(..., alias="id", description="The unique identifier of the behavior to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a behavior by its ID. This action cannot be undone."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteBehaviorsIdRequest(
            path=_models.DeleteBehaviorsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_behavior: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/behaviors/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/behaviors/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_behavior")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_behavior", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_behavior",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: bundle_downloads
@mcp.tool()
async def list_bundle_downloads(
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000 records per page."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Only `created_at` is supported as a valid sort field."),
    bundle_id: str | None = Field(None, description="Filter results to downloads associated with a specific bundle by its ID."),
    bundle_registration_id: str | None = Field(None, description="Filter results to downloads associated with a specific bundle registration by its ID."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of bundle downloads with optional filtering by bundle or bundle registration ID, and sorting capabilities."""

    _per_page = _parse_int(per_page)
    _bundle_id = _parse_int(bundle_id)
    _bundle_registration_id = _parse_int(bundle_registration_id)

    # Construct request model with validation
    try:
        _request = _models.GetBundleDownloadsRequest(
            query=_models.GetBundleDownloadsRequestQuery(per_page=_per_page, sort_by=sort_by, bundle_id=_bundle_id, bundle_registration_id=_bundle_registration_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bundle_downloads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bundle_downloads"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bundle_downloads")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bundle_downloads", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bundle_downloads",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: bundle_notifications
@mcp.tool()
async def list_bundle_notifications(
    per_page: str | None = Field(None, description="Maximum number of records to return per page. Recommended to use 1,000 or less for optimal performance."),
    bundle_id: str | None = Field(None, description="Filter notifications by a specific bundle ID. Omit to retrieve notifications for all bundles."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of notifications for a specific bundle or all bundles. Use pagination parameters to control result size and retrieval."""

    _per_page = _parse_int(per_page)
    _bundle_id = _parse_int(bundle_id)

    # Construct request model with validation
    try:
        _request = _models.GetBundleNotificationsRequest(
            query=_models.GetBundleNotificationsRequestQuery(per_page=_per_page, bundle_id=_bundle_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bundle_notifications: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bundle_notifications"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bundle_notifications")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bundle_notifications", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bundle_notifications",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: bundle_notifications
@mcp.tool()
async def get_bundle_notification(id_: str = Field(..., alias="id", description="The unique identifier of the bundle notification to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details for a specific bundle notification by its ID. Use this to fetch the full notification record including its content and metadata."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetBundleNotificationsIdRequest(
            path=_models.GetBundleNotificationsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bundle_notification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bundle_notifications/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/bundle_notifications/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bundle_notification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bundle_notification", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bundle_notification",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: bundle_notifications
@mcp.tool()
async def update_bundle_notification(
    id_: str = Field(..., alias="id", description="The unique identifier of the bundle notification to update."),
    notify_on_registration: bool | None = Field(None, description="Enable or disable notifications when a registration action occurs for this bundle."),
    notify_on_upload: bool | None = Field(None, description="Enable or disable notifications when an upload action occurs for this bundle."),
) -> dict[str, Any] | ToolResult:
    """Update notification settings for a bundle, controlling when notifications are triggered for registration and upload actions."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PatchBundleNotificationsIdRequest(
            path=_models.PatchBundleNotificationsIdRequestPath(id_=_id_),
            body=_models.PatchBundleNotificationsIdRequestBody(notify_on_registration=notify_on_registration, notify_on_upload=notify_on_upload)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_bundle_notification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bundle_notifications/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/bundle_notifications/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_bundle_notification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_bundle_notification", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_bundle_notification",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: bundle_notifications
@mcp.tool()
async def delete_bundle_notification(id_: str = Field(..., alias="id", description="The unique identifier of the bundle notification to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a specific bundle notification by its ID. This operation permanently removes the bundle notification from the system."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteBundleNotificationsIdRequest(
            path=_models.DeleteBundleNotificationsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_bundle_notification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bundle_notifications/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/bundle_notifications/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_bundle_notification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_bundle_notification", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_bundle_notification",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: bundle_recipients
@mcp.tool()
async def list_bundle_recipients(
    bundle_id: str = Field(..., description="The ID of the bundle for which to list recipients."),
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Valid field is `has_registrations`."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of recipients associated with a specific bundle. Supports pagination and sorting by registration status."""

    _bundle_id = _parse_int(bundle_id)
    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetBundleRecipientsRequest(
            query=_models.GetBundleRecipientsRequestQuery(per_page=_per_page, sort_by=sort_by, bundle_id=_bundle_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bundle_recipients: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bundle_recipients"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bundle_recipients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bundle_recipients", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bundle_recipients",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: bundle_recipients
@mcp.tool()
async def share_bundle_with_recipient(
    bundle_id: str = Field(..., description="The ID of the bundle to share with the recipient."),
    recipient: str = Field(..., description="The email address of the recipient to share the bundle with."),
    company: str | None = Field(None, description="The company name associated with the recipient."),
    name: str | None = Field(None, description="The full name of the recipient."),
    note: str | None = Field(None, description="An optional message to include in the share notification email sent to the recipient."),
    share_after_create: bool | None = Field(None, description="When true, automatically sends a share notification email to the recipient upon creation. When false, the recipient is added without sending an email."),
) -> dict[str, Any] | ToolResult:
    """Share a bundle with a recipient by creating a bundle recipient record. Optionally send a share notification email immediately upon creation."""

    _bundle_id = _parse_int(bundle_id)

    # Construct request model with validation
    try:
        _request = _models.PostBundleRecipientsRequest(
            body=_models.PostBundleRecipientsRequestBody(bundle_id=_bundle_id, company=company, name=name, note=note, recipient=recipient, share_after_create=share_after_create)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for share_bundle_with_recipient: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bundle_recipients"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("share_bundle_with_recipient")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("share_bundle_with_recipient", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="share_bundle_with_recipient",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: bundle_registrations
@mcp.tool()
async def list_bundle_registrations(
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance."),
    bundle_id: str | None = Field(None, description="Filter results to registrations associated with a specific bundle by its ID."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of bundle registrations, optionally filtered by a specific bundle ID."""

    _per_page = _parse_int(per_page)
    _bundle_id = _parse_int(bundle_id)

    # Construct request model with validation
    try:
        _request = _models.GetBundleRegistrationsRequest(
            query=_models.GetBundleRegistrationsRequestQuery(per_page=_per_page, bundle_id=_bundle_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bundle_registrations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bundle_registrations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bundle_registrations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bundle_registrations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bundle_registrations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: bundles
@mcp.tool()
async def list_bundles(
    per_page: str | None = Field(None, description="Number of bundle records to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 is supported."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Supports sorting by `created_at` or `code` fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of bundles with optional sorting. Use pagination parameters to control result size and sorting to organize bundles by creation date or code."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetBundlesRequest(
            query=_models.GetBundlesRequestQuery(per_page=_per_page, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bundles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bundles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bundles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bundles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bundles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: bundles
@mcp.tool()
async def create_bundle(
    paths: list[str] = Field(..., description="List of file and folder paths to include in this bundle. Paths are processed in the order specified."),
    clickwrap_id: str | None = Field(None, description="ID of the clickwrap agreement to display to bundle recipients before access is granted."),
    code: str | None = Field(None, description="Custom code that forms the public-facing URL slug for this bundle. Must be unique and URL-safe."),
    description: str | None = Field(None, description="Public-facing description displayed to bundle recipients explaining the bundle's contents and purpose."),
    dont_separate_submissions_by_folder: bool | None = Field(None, description="When enabled, prevents automatic creation of subfolders for uploads from different users. Use with caution due to security implications when accepting anonymous uploads from multiple sources."),
    expires_at: str | None = Field(None, description="Date and time when the bundle automatically expires and becomes inaccessible. Specified in ISO 8601 format."),
    form_field_set_id: str | None = Field(None, description="ID of the form field set to associate with this bundle. Captured data from form submissions will be stored with uploads."),
    inbox_id: str | None = Field(None, description="ID of the inbox where bundle submissions will be delivered. If not specified, submissions go to the default location."),
    max_uses: str | None = Field(None, description="Maximum number of times the bundle can be accessed before it becomes unavailable. Unlimited if not specified."),
    note: str | None = Field(None, description="Internal note for bundle management purposes. Not visible to bundle recipients."),
    path_template: str | None = Field(None, description="Template for organizing submission subfolders using uploader metadata. Supports placeholders for name, email, IP address, company, and custom form fields using double-brace syntax."),
    permissions: Literal["read", "write", "read_write", "full", "none", "preview_only"] | None = Field(None, description="Access level granted to recipients for folders within this bundle. Controls whether recipients can view, download, upload, or modify contents."),
    require_registration: bool | None = Field(None, description="When enabled, recipients must provide their name and email address before accessing the bundle."),
    require_share_recipient: bool | None = Field(None, description="When enabled, only recipients who received an invitation email through the Files.com interface can access the bundle."),
    send_email_receipt_to_uploader: bool | None = Field(None, description="When enabled, an email receipt confirming successful upload is sent to the uploader. Only applicable for bundles with write permissions."),
    watermark_attachment_file: str | None = Field(None, description="Image file to apply as a watermark overlay on all bundle item previews. Uploaded as binary file data."),
) -> dict[str, Any] | ToolResult:
    """Create a shareable bundle that packages files and folders with configurable access controls, expiration, and submission handling. Bundles can require registration, limit access to specific recipients, and apply watermarks to previewed items."""

    _clickwrap_id = _parse_int(clickwrap_id)
    _form_field_set_id = _parse_int(form_field_set_id)
    _inbox_id = _parse_int(inbox_id)
    _max_uses = _parse_int(max_uses)

    # Construct request model with validation
    try:
        _request = _models.PostBundlesRequest(
            body=_models.PostBundlesRequestBody(clickwrap_id=_clickwrap_id, code=code, description=description, dont_separate_submissions_by_folder=dont_separate_submissions_by_folder, expires_at=expires_at, form_field_set_id=_form_field_set_id, inbox_id=_inbox_id, max_uses=_max_uses, note=note, path_template=path_template, paths=paths, permissions=permissions, require_registration=require_registration, require_share_recipient=require_share_recipient, send_email_receipt_to_uploader=send_email_receipt_to_uploader, watermark_attachment_file=watermark_attachment_file)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_bundle: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bundles"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_bundle")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_bundle", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_bundle",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["watermark_attachment_file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: bundles
@mcp.tool()
async def get_bundle(id_: str = Field(..., alias="id", description="The unique identifier of the bundle to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific bundle by its ID."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetBundlesIdRequest(
            path=_models.GetBundlesIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bundle: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bundles/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/bundles/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bundle")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bundle", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bundle",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: bundles
@mcp.tool()
async def update_bundle(
    id_: str = Field(..., alias="id", description="The unique identifier of the bundle to update."),
    clickwrap_id: str | None = Field(None, description="The clickwrap agreement to associate with this bundle for user acceptance."),
    code: str | None = Field(None, description="A unique code that forms the final segment of the bundle's public URL."),
    description: str | None = Field(None, description="A public-facing description displayed to bundle users."),
    dont_separate_submissions_by_folder: bool | None = Field(None, description="When enabled, prevents automatic creation of subfolders for uploads from different users. Use with caution due to potential security implications with anonymous multi-user uploads."),
    expires_at: str | None = Field(None, description="The date and time when the bundle expires and becomes inaccessible. Use ISO 8601 format."),
    form_field_set_id: str | None = Field(None, description="The form field set to associate with this bundle for collecting uploader information."),
    inbox_id: str | None = Field(None, description="The inbox to associate with this bundle for organizing submissions."),
    max_uses: str | None = Field(None, description="The maximum number of times the bundle can be accessed before becoming unavailable."),
    note: str | None = Field(None, description="An internal note for bundle administrators, not visible to users."),
    path_template: str | None = Field(None, description="A template for organizing submission subfolders using uploader metadata. Supports placeholders for name, email, IP address, company, and custom form fields."),
    paths: list[str] | None = Field(None, description="A list of file and folder paths to include in the bundle. Order is preserved as specified."),
    permissions: Literal["read", "write", "read_write", "full", "none", "preview_only"] | None = Field(None, description="The permission level for accessing folders within this bundle."),
    require_registration: bool | None = Field(None, description="When enabled, displays a registration form to capture the downloader's name and email address."),
    require_share_recipient: bool | None = Field(None, description="When enabled, restricts access to only recipients who have been explicitly invited via email through the Files.com interface."),
    send_email_receipt_to_uploader: bool | None = Field(None, description="When enabled, sends a delivery receipt to the uploader upon bundle access. Only applicable for writable bundles."),
    watermark_attachment_file: str | None = Field(None, description="A watermark image file to overlay on all bundle item previews for branding or security purposes."),
) -> dict[str, Any] | ToolResult:
    """Update an existing bundle's configuration, including access controls, expiration, paths, and metadata. Allows modification of sharing permissions, recipient requirements, and submission handling."""

    _id_ = _parse_int(id_)
    _clickwrap_id = _parse_int(clickwrap_id)
    _form_field_set_id = _parse_int(form_field_set_id)
    _inbox_id = _parse_int(inbox_id)
    _max_uses = _parse_int(max_uses)

    # Construct request model with validation
    try:
        _request = _models.PatchBundlesIdRequest(
            path=_models.PatchBundlesIdRequestPath(id_=_id_),
            body=_models.PatchBundlesIdRequestBody(clickwrap_id=_clickwrap_id, code=code, description=description, dont_separate_submissions_by_folder=dont_separate_submissions_by_folder, expires_at=expires_at, form_field_set_id=_form_field_set_id, inbox_id=_inbox_id, max_uses=_max_uses, note=note, path_template=path_template, paths=paths, permissions=permissions, require_registration=require_registration, require_share_recipient=require_share_recipient, send_email_receipt_to_uploader=send_email_receipt_to_uploader, watermark_attachment_file=watermark_attachment_file)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_bundle: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bundles/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/bundles/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_bundle")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_bundle", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_bundle",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["watermark_attachment_file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: bundles
@mcp.tool()
async def delete_bundle(id_: str = Field(..., alias="id", description="The unique identifier of the bundle to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a bundle by its ID. This action cannot be undone."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteBundlesIdRequest(
            path=_models.DeleteBundlesIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_bundle: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bundles/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/bundles/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_bundle")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_bundle", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_bundle",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: bundles
@mcp.tool()
async def share_bundle(
    id_: str = Field(..., alias="id", description="The unique identifier of the bundle to share."),
    note: str | None = Field(None, description="Optional custom message to include in the share email."),
) -> dict[str, Any] | ToolResult:
    """Send email(s) with a shareable link to a bundle. Optionally include a custom note in the email message."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PostBundlesIdShareRequest(
            path=_models.PostBundlesIdShareRequestPath(id_=_id_),
            body=_models.PostBundlesIdShareRequestBody(note=note)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for share_bundle: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bundles/{id}/share", _request.path.model_dump(by_alias=True)) if _request.path else "/bundles/{id}/share"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("share_bundle")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("share_bundle", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="share_bundle",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: clickwraps
@mcp.tool()
async def list_clickwraps(per_page: str | None = Field(None, description="Number of clickwrap records to return per page. Recommended to use 1,000 or less for optimal performance.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of clickwraps. Use the per_page parameter to control the number of records returned in each page."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetClickwrapsRequest(
            query=_models.GetClickwrapsRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_clickwraps: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/clickwraps"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_clickwraps")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_clickwraps", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_clickwraps",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: clickwraps
@mcp.tool()
async def create_clickwrap(
    name: str | None = Field(None, description="Display name for this clickwrap agreement, used when presenting multiple clickwrap options to users."),
    use_with_bundles: Literal["none", "available", "require"] | None = Field(None, description="Determines how this clickwrap applies to bundle operations: 'none' disables it, 'available' makes it optional, 'require' makes acceptance mandatory."),
    use_with_inboxes: Literal["none", "available", "require"] | None = Field(None, description="Determines how this clickwrap applies to inbox operations: 'none' disables it, 'available' makes it optional, 'require' makes acceptance mandatory."),
    use_with_users: Literal["none", "require"] | None = Field(None, description="Determines how this clickwrap applies to user registration via email invitation: 'none' disables it, 'require' makes acceptance mandatory during password setup."),
    body: str | None = Field(None, description="Body text of Clickwrap (supports Markdown formatting)."),
) -> dict[str, Any] | ToolResult:
    """Create a new clickwrap agreement that users must accept. Clickwraps can be configured for use with bundles, inboxes, and user registrations."""

    # Construct request model with validation
    try:
        _request = _models.PostClickwrapsRequest(
            body=_models.PostClickwrapsRequestBody(name=name, use_with_bundles=use_with_bundles, use_with_inboxes=use_with_inboxes, use_with_users=use_with_users, body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_clickwrap: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/clickwraps"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_clickwrap")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_clickwrap", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_clickwrap",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: clickwraps
@mcp.tool()
async def get_clickwrap(id_: str = Field(..., alias="id", description="The unique identifier of the clickwrap agreement to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific clickwrap agreement by its ID. Returns the clickwrap details including its configuration and status."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetClickwrapsIdRequest(
            path=_models.GetClickwrapsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_clickwrap: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/clickwraps/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/clickwraps/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_clickwrap")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_clickwrap", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_clickwrap",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: clickwraps
@mcp.tool()
async def update_clickwrap(
    id_: str = Field(..., alias="id", description="The unique identifier of the Clickwrap agreement to update."),
    name: str | None = Field(None, description="Display name for the Clickwrap agreement, used when presenting multiple agreements to users for selection."),
    use_with_bundles: Literal["none", "available", "require"] | None = Field(None, description="Controls whether this Clickwrap is available for Bundle operations. Set to 'require' to mandate acceptance, 'available' to offer optionally, or 'none' to disable."),
    use_with_inboxes: Literal["none", "available", "require"] | None = Field(None, description="Controls whether this Clickwrap is available for Inbox operations. Set to 'require' to mandate acceptance, 'available' to offer optionally, or 'none' to disable."),
    use_with_users: Literal["none", "require"] | None = Field(None, description="Controls whether this Clickwrap is required for user registrations via email invitation. Applies only when users are invited to set their own password. Set to 'require' to mandate acceptance or 'none' to disable."),
) -> dict[str, Any] | ToolResult:
    """Update an existing Clickwrap agreement configuration, including its name and usage settings across bundles, inboxes, and user registrations."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PatchClickwrapsIdRequest(
            path=_models.PatchClickwrapsIdRequestPath(id_=_id_),
            body=_models.PatchClickwrapsIdRequestBody(name=name, use_with_bundles=use_with_bundles, use_with_inboxes=use_with_inboxes, use_with_users=use_with_users)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_clickwrap: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/clickwraps/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/clickwraps/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_clickwrap")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_clickwrap", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_clickwrap",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: clickwraps
@mcp.tool()
async def delete_clickwrap(id_: str = Field(..., alias="id", description="The unique identifier of the clickwrap to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a clickwrap by its ID. This action cannot be undone."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteClickwrapsIdRequest(
            path=_models.DeleteClickwrapsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_clickwrap: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/clickwraps/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/clickwraps/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_clickwrap")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_clickwrap", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_clickwrap",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dns_records
@mcp.tool()
async def list_dns_records(per_page: str | None = Field(None, description="Number of DNS records to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 records can be retrieved in a single request.")) -> dict[str, Any] | ToolResult:
    """Retrieve the DNS records configured for a site. Results can be paginated to manage large record sets."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetDnsRecordsRequest(
            query=_models.GetDnsRecordsRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dns_records: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/dns_records"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dns_records")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dns_records", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dns_records",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: external_events
@mcp.tool()
async def list_external_events(
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 is supported."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Valid sortable fields are: remote_server_type, site_id, folder_behavior_id, event_type, created_at, or status."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of external events with optional sorting. Use this to monitor and track events from remote servers across your file management system."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetExternalEventsRequest(
            query=_models.GetExternalEventsRequestQuery(per_page=_per_page, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_external_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/external_events"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_external_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_external_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_external_events",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: external_events
@mcp.tool()
async def create_external_event(
    body: str = Field(..., description="The content or payload of the event being created."),
    status: Literal["success", "failure", "partial_failure", "in_progress", "skipped"] = Field(..., description="The current processing state of the event."),
) -> dict[str, Any] | ToolResult:
    """Create a new external event with a specified status. This operation allows you to log events from external systems with their current processing state."""

    # Construct request model with validation
    try:
        _request = _models.PostExternalEventsRequest(
            body=_models.PostExternalEventsRequestBody(body=body, status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_external_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/external_events"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_external_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_external_event", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_external_event",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: external_events
@mcp.tool()
async def get_external_event(id_: str = Field(..., alias="id", description="The unique identifier of the external event to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details for a specific external event by its ID. Returns the complete event information including metadata and configuration."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetExternalEventsIdRequest(
            path=_models.GetExternalEventsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_external_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/external_events/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/external_events/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_external_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_external_event", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_external_event",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: file_actions
@mcp.tool()
async def initiate_file_upload(
    path: str = Field(..., description="The file path where the upload will be stored. Can be a new file or an existing file for append/restart operations."),
    mkdir_parents: bool | None = Field(None, description="Whether to automatically create any missing parent directories in the path hierarchy."),
    parts: str | None = Field(None, description="The number of parts to divide the file into for multipart upload. Determines parallelization strategy for the upload."),
    size: str | None = Field(None, description="The total file size in bytes, including any existing bytes if appending to or restarting an existing file."),
) -> dict[str, Any] | ToolResult:
    """Initiate a file upload by specifying the target path, total file size, and number of parts. Optionally create parent directories and configure multipart upload parameters."""

    _parts = _parse_int(parts)
    _size = _parse_int(size)

    # Construct request model with validation
    try:
        _request = _models.FileActionBeginUploadRequest(
            path=_models.FileActionBeginUploadRequestPath(path=path),
            body=_models.FileActionBeginUploadRequestBody(mkdir_parents=mkdir_parents, parts=_parts, size=_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for initiate_file_upload: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/file_actions/begin_upload/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/file_actions/begin_upload/{path}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("initiate_file_upload")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("initiate_file_upload", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="initiate_file_upload",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: file_actions
@mcp.tool()
async def copy_file(
    path: str = Field(..., description="The file or folder path to copy from."),
    destination: str = Field(..., description="The destination path where the file or folder will be copied to."),
    structure: bool | None = Field(None, description="If true, copy only the directory structure without copying file contents."),
) -> dict[str, Any] | ToolResult:
    """Copy a file or folder to a specified destination. Optionally copy only the directory structure without file contents."""

    # Construct request model with validation
    try:
        _request = _models.FileActionCopyRequest(
            path=_models.FileActionCopyRequestPath(path=path),
            body=_models.FileActionCopyRequestBody(destination=destination, structure=structure)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for copy_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/file_actions/copy/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/file_actions/copy/{path}"
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
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: file_actions
@mcp.tool()
async def get_file_metadata(
    path: str = Field(..., description="The file system path to the target file or folder."),
    preview_size: str | None = Field(None, description="The size of the file preview to include in the response. Determines the resolution and detail level of preview data."),
    with_previews: bool | None = Field(None, description="Whether to include preview information in the response metadata."),
    with_priority_color: bool | None = Field(None, description="Whether to include priority color information in the response metadata."),
) -> dict[str, Any] | ToolResult:
    """Retrieve metadata for a file or folder at the specified path, optionally including preview and priority information."""

    # Construct request model with validation
    try:
        _request = _models.FileActionFindRequest(
            path=_models.FileActionFindRequestPath(path=path),
            query=_models.FileActionFindRequestQuery(preview_size=preview_size, with_previews=with_previews, with_priority_color=with_priority_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/file_actions/metadata/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/file_actions/metadata/{path}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_metadata", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_metadata",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: file_actions
@mcp.tool()
async def move_file(
    path: str = Field(..., description="The current path of the file or folder to be moved."),
    destination: str = Field(..., description="The destination path where the file or folder should be moved to."),
) -> dict[str, Any] | ToolResult:
    """Move a file or folder to a new location. The source path and destination path must both be valid within the file system."""

    # Construct request model with validation
    try:
        _request = _models.FileActionMoveRequest(
            path=_models.FileActionMoveRequestPath(path=path),
            body=_models.FileActionMoveRequestBody(destination=destination)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for move_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/file_actions/move/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/file_actions/move/{path}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("move_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("move_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="move_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: file_comment_reactions
@mcp.tool()
async def add_file_comment_reaction(
    emoji: str = Field(..., description="The emoji character or emoji code to use as the reaction on the file comment."),
    file_comment_id: str = Field(..., description="The unique identifier of the file comment to attach the reaction to."),
) -> dict[str, Any] | ToolResult:
    """Add an emoji reaction to a file comment. This allows users to express feedback or acknowledgment on specific comments within a file."""

    _file_comment_id = _parse_int(file_comment_id)

    # Construct request model with validation
    try:
        _request = _models.PostFileCommentReactionsRequest(
            body=_models.PostFileCommentReactionsRequestBody(emoji=emoji, file_comment_id=_file_comment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_file_comment_reaction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/file_comment_reactions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_file_comment_reaction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_file_comment_reaction", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_file_comment_reaction",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: file_comment_reactions
@mcp.tool()
async def remove_file_comment_reaction(id_: str = Field(..., alias="id", description="The unique identifier of the file comment reaction to delete.")) -> dict[str, Any] | ToolResult:
    """Remove a reaction from a file comment. Deletes the specified file comment reaction by its ID."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteFileCommentReactionsIdRequest(
            path=_models.DeleteFileCommentReactionsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_file_comment_reaction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/file_comment_reactions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/file_comment_reactions/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_file_comment_reaction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_file_comment_reaction", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_file_comment_reaction",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: file_comments
@mcp.tool()
async def update_file_comment(
    id_: str = Field(..., alias="id", description="The unique identifier of the file comment to update."),
    body: str = Field(..., description="The new comment text content to replace the existing body."),
) -> dict[str, Any] | ToolResult:
    """Update the body text of an existing file comment. Allows modification of comment content after initial creation."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PatchFileCommentsIdRequest(
            path=_models.PatchFileCommentsIdRequestPath(id_=_id_),
            body=_models.PatchFileCommentsIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_file_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/file_comments/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/file_comments/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_file_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_file_comment", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_file_comment",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: file_comments
@mcp.tool()
async def delete_file_comment(id_: str = Field(..., alias="id", description="The unique identifier of the file comment to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a specific file comment by its ID. This operation permanently removes the comment from the file."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteFileCommentsIdRequest(
            path=_models.DeleteFileCommentsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_file_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/file_comments/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/file_comments/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_file_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_file_comment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_file_comment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: file_migrations
@mcp.tool()
async def get_file_migration(id_: str = Field(..., alias="id", description="The unique identifier of the file migration to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details of a specific file migration by its ID. Use this to check the status and information of a file migration operation."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetFileMigrationsIdRequest(
            path=_models.GetFileMigrationsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_migration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/file_migrations/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/file_migrations/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_migration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_migration", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_migration",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def download_file(
    path: str = Field(..., description="The file path to download or retrieve information for."),
    action: str | None = Field(None, description="Controls the response behavior: leave blank for standard download, use 'stat' to retrieve file metadata without a download URL, or use 'redirect' to receive a 302 redirect directly to the file."),
    preview_size: str | None = Field(None, description="The size of the preview image to generate. Larger sizes provide higher resolution previews."),
    with_previews: bool | None = Field(None, description="Include preview image data in the response when available."),
    with_priority_color: bool | None = Field(None, description="Include priority color metadata in the response when available."),
) -> dict[str, Any] | ToolResult:
    """Download a file from the specified path with optional preview generation, metadata retrieval, or redirect handling. Supports stat mode to retrieve file information without initiating a download."""

    # Construct request model with validation
    try:
        _request = _models.FileDownloadRequest(
            path=_models.FileDownloadRequestPath(path=path),
            query=_models.FileDownloadRequestQuery(action=action, preview_size=preview_size, with_previews=with_previews, with_priority_color=with_priority_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for download_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{path}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

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

# Tags: files
@mcp.tool()
async def upload_file(
    path: str = Field(..., description="The file system path where the file will be uploaded or operated on."),
    etags_etag: list[str] = Field(..., description="Array of etag identifiers for multipart upload validation, used to verify part integrity. Order corresponds to part numbers."),
    etags_part: list[int] = Field(..., description="Array of part numbers corresponding to each etag, indicating the sequence of multipart upload segments. Order must match the etags array."),
    action: str | None = Field(None, description="The type of upload action to perform: `upload` for standard file upload, `append` to append to existing file, `attachment` for attachment handling, `put` for direct replacement, `end` to finalize multipart upload, or omit for default behavior."),
    length: str | None = Field(None, description="The length of the file being uploaded in bytes."),
    mkdir_parents: bool | None = Field(None, description="Whether to automatically create parent directories in the path if they do not already exist."),
    parts: str | None = Field(None, description="The number of parts to fetch or process for multipart uploads."),
    provided_mtime: str | None = Field(None, description="User-provided modification timestamp for the uploaded file in ISO 8601 format."),
    size: str | None = Field(None, description="The total size of the file in bytes."),
    structure: str | None = Field(None, description="When copying a folder, set to `true` to copy only the directory structure without file contents."),
) -> dict[str, Any] | ToolResult:
    """Upload a file to the specified path, supporting multipart uploads, append operations, and optional parent directory creation. Supports various upload actions including standard upload, append, and multipart completion."""

    _length = _parse_int(length)
    _parts = _parse_int(parts)
    _size = _parse_int(size)

    # Construct request model with validation
    try:
        _request = _models.PostFilesPathRequest(
            path=_models.PostFilesPathRequestPath(path=path),
            body=_models.PostFilesPathRequestBody(action=action, etags_etag=etags_etag, etags_part=etags_part, length=_length, mkdir_parents=mkdir_parents, parts=_parts, provided_mtime=provided_mtime, size=_size, structure=structure)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{path}"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def update_file_metadata(
    path: str = Field(..., description="The file or folder path to update."),
    priority_color: str | None = Field(None, description="Priority or bookmark color to assign to the file or folder."),
    provided_mtime: str | None = Field(None, description="The modification timestamp to set for the file or folder in ISO 8601 format."),
) -> dict[str, Any] | ToolResult:
    """Update metadata for a file or folder, including priority color and modification timestamp."""

    # Construct request model with validation
    try:
        _request = _models.PatchFilesPathRequest(
            path=_models.PatchFilesPathRequestPath(path=path),
            body=_models.PatchFilesPathRequestBody(priority_color=priority_color, provided_mtime=provided_mtime)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_file_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{path}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_file_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_file_metadata", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_file_metadata",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: files
@mcp.tool()
async def delete_file(
    path: str = Field(..., description="The file system path to the file or folder to delete."),
    recursive: bool | None = Field(None, description="When true, recursively deletes folders and their contents. When false, deletion fails if the target folder is not empty."),
) -> dict[str, Any] | ToolResult:
    """Delete a file or folder at the specified path. Use the recursive parameter to delete non-empty folders; otherwise, deletion will fail if the folder contains items."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFilesPathRequest(
            path=_models.DeleteFilesPathRequestPath(path=path),
            query=_models.DeleteFilesPathRequestQuery(recursive=recursive)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/files/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/files/{path}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: folders
@mcp.tool()
async def list_folders(
    path: str = Field(..., description="The folder path to list contents from."),
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance."),
    preview_size: str | None = Field(None, description="Size of file previews to include in the response."),
    search_all: bool | None = Field(None, description="When enabled, searches the entire site and ignores the specified folder path. Use only for ad-hoc human searches, not automated processes, as results are best-effort and not real-time guaranteed."),
    with_previews: bool | None = Field(None, description="Include file preview data in the response."),
    with_priority_color: bool | None = Field(None, description="Include file priority color metadata in the response."),
) -> dict[str, Any] | ToolResult:
    """List folders at a specified path with optional filtering, previews, and metadata. Supports site-wide search when enabled."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.FolderListForPathRequest(
            path=_models.FolderListForPathRequestPath(path=path),
            query=_models.FolderListForPathRequestQuery(per_page=_per_page, preview_size=preview_size, search_all=search_all, with_previews=with_previews, with_priority_color=with_priority_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_folders: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{path}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_folders")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_folders", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_folders",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: folders
@mcp.tool()
async def create_folder(
    path: str = Field(..., description="The file system path where the folder should be created."),
    mkdir_parents: bool | None = Field(None, description="Whether to automatically create any missing parent directories in the path."),
    provided_mtime: str | None = Field(None, description="Custom modification timestamp for the created folder in ISO 8601 date-time format."),
) -> dict[str, Any] | ToolResult:
    """Create a new folder at the specified path. Optionally create parent directories and set a custom modification time."""

    # Construct request model with validation
    try:
        _request = _models.PostFoldersPathRequest(
            path=_models.PostFoldersPathRequestPath(path=path),
            body=_models.PostFoldersPathRequestBody(mkdir_parents=mkdir_parents, provided_mtime=provided_mtime)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{path}"
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
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: form_field_sets
@mcp.tool()
async def list_form_field_sets(per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of form field sets. Use pagination to control the number of records returned per page."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetFormFieldSetsRequest(
            query=_models.GetFormFieldSetsRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_form_field_sets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/form_field_sets"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_form_field_sets")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_form_field_sets", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_form_field_sets",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: form_field_sets
@mcp.tool()
async def create_form_field_set(
    form_fields: list[_models.PostFormFieldSetsBodyFormFieldsItem] | None = Field(None, description="Array of form fields to include in this set. Order is preserved and determines field display sequence. Each item should represent a field configuration."),
    title: str | None = Field(None, description="Display title for the form field set. Used to identify and label the set in user interfaces."),
) -> dict[str, Any] | ToolResult:
    """Create a new form field set with a title and optional collection of form fields. Form field sets organize related fields for structured data collection."""

    # Construct request model with validation
    try:
        _request = _models.PostFormFieldSetsRequest(
            body=_models.PostFormFieldSetsRequestBody(form_fields=form_fields, title=title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_form_field_set: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/form_field_sets"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_form_field_set")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_form_field_set", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_form_field_set",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: form_field_sets
@mcp.tool()
async def get_form_field_set(id_: str = Field(..., alias="id", description="The unique identifier of the form field set to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific form field set by its ID. Returns the complete configuration and structure of the requested form field set."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetFormFieldSetsIdRequest(
            path=_models.GetFormFieldSetsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_form_field_set: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/form_field_sets/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/form_field_sets/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_form_field_set")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_form_field_set", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_form_field_set",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: form_field_sets
@mcp.tool()
async def update_form_field_set(
    id_: str = Field(..., alias="id", description="The unique identifier of the form field set to update."),
    form_fields: list[_models.PatchFormFieldSetsIdBodyFormFieldsItem] | None = Field(None, description="Array of form fields to associate with this field set. Order may be significant for display purposes."),
    title: str | None = Field(None, description="The display title for this form field set."),
) -> dict[str, Any] | ToolResult:
    """Update an existing form field set by modifying its title and/or associated form fields. Changes are applied to the specified form field set."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PatchFormFieldSetsIdRequest(
            path=_models.PatchFormFieldSetsIdRequestPath(id_=_id_),
            body=_models.PatchFormFieldSetsIdRequestBody(form_fields=form_fields, title=title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_form_field_set: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/form_field_sets/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/form_field_sets/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_form_field_set")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_form_field_set", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_form_field_set",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: form_field_sets
@mcp.tool()
async def delete_form_field_set(id_: str = Field(..., alias="id", description="The unique identifier of the form field set to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a form field set by its ID. This operation permanently removes the specified form field set and cannot be undone."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteFormFieldSetsIdRequest(
            path=_models.DeleteFormFieldSetsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_form_field_set: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/form_field_sets/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/form_field_sets/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_form_field_set")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_form_field_set", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_form_field_set",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: group_users
@mcp.tool()
async def list_group_users(
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000."),
    group_id: str | None = Field(None, description="Group ID.  If provided, will return group_users of this group."),
    user_id: str | None = Field(None, description="User ID.  If provided, will return group_users of this user."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of users belonging to a group. Use the per_page parameter to control result set size."""

    _per_page = _parse_int(per_page)
    _group_id = _parse_int(group_id)
    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.GetGroupUsersRequest(
            query=_models.GetGroupUsersRequestQuery(per_page=_per_page, group_id=_group_id, user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_group_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/group_users"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_group_users")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_group_users", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_group_users",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: group_users
@mcp.tool()
async def add_user_to_group(
    group_id: str = Field(..., description="The ID of the group to which the user will be added."),
    user_id: str = Field(..., description="The ID of the user to add to the group."),
    admin: bool | None = Field(None, description="Grant group administrator privileges to the user, allowing them to manage group membership and settings."),
) -> dict[str, Any] | ToolResult:
    """Add a user to a group with optional administrator privileges. The user will gain access to all group resources based on their assigned role."""

    _group_id = _parse_int(group_id)
    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.PostGroupUsersRequest(
            body=_models.PostGroupUsersRequestBody(admin=admin, group_id=_group_id, user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_user_to_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/group_users"
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
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: group_users
@mcp.tool()
async def update_group_user(
    id_: str = Field(..., alias="id", description="The unique identifier of the group user membership record to update."),
    group_id: str = Field(..., description="The group to which the user belongs or should be associated."),
    user_id: str = Field(..., description="The user to be added or updated in the group membership."),
    admin: bool | None = Field(None, description="Whether the user should have administrator privileges within the group."),
) -> dict[str, Any] | ToolResult:
    """Update a user's membership in a group, including their administrator status. Modify group user associations and permissions."""

    _id_ = _parse_int(id_)
    _group_id = _parse_int(group_id)
    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.PatchGroupUsersIdRequest(
            path=_models.PatchGroupUsersIdRequestPath(id_=_id_),
            body=_models.PatchGroupUsersIdRequestBody(admin=admin, group_id=_group_id, user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_group_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/group_users/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/group_users/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_group_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_group_user", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_group_user",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: group_users
@mcp.tool()
async def remove_user_from_group(
    id_: str = Field(..., alias="id", description="The unique identifier of the group user membership record to delete."),
    group_id: str = Field(..., description="The unique identifier of the group from which the user will be removed."),
    user_id: str = Field(..., description="The unique identifier of the user to remove from the group."),
) -> dict[str, Any] | ToolResult:
    """Remove a user from a group by deleting the group membership record. This operation requires the group user ID along with the group and user IDs for verification."""

    _id_ = _parse_int(id_)
    _group_id = _parse_int(group_id)
    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteGroupUsersIdRequest(
            path=_models.DeleteGroupUsersIdRequestPath(id_=_id_),
            query=_models.DeleteGroupUsersIdRequestQuery(group_id=_group_id, user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_user_from_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/group_users/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/group_users/{id}"
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

# Tags: groups
@mcp.tool()
async def list_groups(
    per_page: str | None = Field(None, description="Maximum number of group records to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. The `name` field is supported for sorting."),
    ids: str | None = Field(None, description="Filter results to include only groups with the specified IDs. Provide as a comma-separated list of group identifiers."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of groups with optional filtering by IDs and sorting capabilities. Use this operation to browse available groups in your system."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetGroupsRequest(
            query=_models.GetGroupsRequestQuery(per_page=_per_page, sort_by=sort_by, ids=ids)
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

# Tags: groups
@mcp.tool()
async def create_group(
    admin_ids: str | None = Field(None, description="Comma-delimited list of user IDs to designate as group administrators. Administrators have elevated permissions within the group."),
    name: str | None = Field(None, description="The name of the group. Used for identification and display purposes."),
    notes: str | None = Field(None, description="Optional notes or description for the group. Useful for documenting the group's purpose or additional context."),
    user_ids: str | None = Field(None, description="Comma-delimited list of user IDs to add as members of the group. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Create a new group with specified members and administrators. Optionally include group name, notes, and assign users and admins during creation."""

    # Construct request model with validation
    try:
        _request = _models.PostGroupsRequest(
            body=_models.PostGroupsRequestBody(admin_ids=admin_ids, name=name, notes=notes, user_ids=user_ids)
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
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: groups
@mcp.tool()
async def update_group_membership(
    group_id: str = Field(..., description="The unique identifier of the group containing the membership to update."),
    user_id: str = Field(..., description="The unique identifier of the user whose group membership should be updated."),
    admin: bool | None = Field(None, description="Whether the user should have administrator privileges within the group."),
) -> dict[str, Any] | ToolResult:
    """Update a user's membership status in a group, including their administrator privileges. Allows modification of a user's role within the specified group."""

    _group_id = _parse_int(group_id)
    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.PatchGroupsGroupIdMembershipsUserIdRequest(
            path=_models.PatchGroupsGroupIdMembershipsUserIdRequestPath(group_id=_group_id, user_id=_user_id),
            body=_models.PatchGroupsGroupIdMembershipsUserIdRequestBody(admin=admin)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_group_membership: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{group_id}/memberships/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{group_id}/memberships/{user_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_group_membership")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_group_membership", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_group_membership",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: groups
@mcp.tool()
async def remove_group_member(
    group_id: str = Field(..., description="The unique identifier of the group from which the user will be removed."),
    user_id: str = Field(..., description="The unique identifier of the user to be removed from the group."),
) -> dict[str, Any] | ToolResult:
    """Remove a user from a group by deleting their membership. This operation revokes the user's access to the group."""

    _group_id = _parse_int(group_id)
    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteGroupsGroupIdMembershipsUserIdRequest(
            path=_models.DeleteGroupsGroupIdMembershipsUserIdRequestPath(group_id=_group_id, user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_group_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{group_id}/memberships/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{group_id}/memberships/{user_id}"
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

# Tags: groups
@mcp.tool()
async def list_group_permissions(
    group_id: str = Field(..., description="The ID of the group for which to list permissions. Note: This parameter is deprecated; use the `filter[group_id]` query parameter for filtering instead."),
    per_page: str | None = Field(None, description="Number of permission records to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort the results by a specified field in ascending or descending order. Valid sortable fields are `group_id`, `path`, `user_id`, or `permission`."),
    include_groups: bool | None = Field(None, description="When enabled, includes permissions inherited from the group's parent groups in addition to directly assigned permissions."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of permissions for a specific group. Supports filtering, sorting, and optionally including inherited permissions from parent groups."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetGroupsGroupIdPermissionsRequest(
            path=_models.GetGroupsGroupIdPermissionsRequestPath(group_id=group_id),
            query=_models.GetGroupsGroupIdPermissionsRequestQuery(per_page=_per_page, sort_by=sort_by, include_groups=include_groups)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_group_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{group_id}/permissions", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{group_id}/permissions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_group_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_group_permissions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_group_permissions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: groups
@mcp.tool()
async def list_group_members(
    group_id: str = Field(..., description="The unique identifier of the group whose members you want to retrieve."),
    per_page: str | None = Field(None, description="Number of user records to return per page. Recommended to use 1,000 or less for optimal performance; maximum allowed is 10,000."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of users who are members of a specific group. Use pagination parameters to control result size and navigate through large member lists."""

    _group_id = _parse_int(group_id)
    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetGroupsGroupIdUsersRequest(
            path=_models.GetGroupsGroupIdUsersRequestPath(group_id=_group_id),
            query=_models.GetGroupsGroupIdUsersRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_group_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{group_id}/users", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{group_id}/users"
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

# Tags: groups
@mcp.tool()
async def create_group_user(
    group_id: str = Field(..., description="The group ID to associate with the new user."),
    allowed_ips: str | None = Field(None, description="Newline-delimited list of IP addresses permitted to access this user's account."),
    announcements_read: bool | None = Field(None, description="Whether the user has read all announcements displayed in the UI."),
    authenticate_until: str | None = Field(None, description="Date and time at which the user account will be automatically deactivated."),
    authentication_method: Literal["password", "unused_former_ldap", "sso", "none", "email_signup", "password_with_imported_hash"] | None = Field(None, description="The authentication method used for this user's login credentials."),
    billing_permission: bool | None = Field(None, description="Whether this user can perform operations on account settings, payments, and invoices."),
    bypass_inactive_disable: bool | None = Field(None, description="Whether this user is exempt from automatic deactivation due to inactivity."),
    bypass_site_allowed_ips: bool | None = Field(None, description="Whether this user can bypass site-wide IP blacklist restrictions."),
    company: str | None = Field(None, description="The user's company or organization name."),
    dav_permission: bool | None = Field(None, description="Whether the user can connect and authenticate via WebDAV protocol."),
    disabled: bool | None = Field(None, description="Whether the user account is disabled. Disabled users cannot log in and do not consume billing seats."),
    email: str | None = Field(None, description="The user's email address."),
    ftp_permission: bool | None = Field(None, description="Whether the user can access files and folders via FTP or FTPS protocols."),
    grant_permission: str | None = Field(None, description="Permission level to grant on the user's root folder. Options include full access, read-only, write, list, or history."),
    header_text: str | None = Field(None, description="Custom text message displayed to the user in the UI header."),
    language: str | None = Field(None, description="The user's preferred language for the UI."),
    name: str | None = Field(None, description="The user's full name."),
    notes: str | None = Field(None, description="Internal notes or comments about the user for administrative reference."),
    notification_daily_send_time: str | None = Field(None, description="The hour of the day (0-23) when daily notifications should be sent to the user."),
    office_integration_enabled: bool | None = Field(None, description="Whether to enable integration with Microsoft Office for the web applications."),
    password_validity_days: str | None = Field(None, description="Number of days a user can use the same password before being required to change it."),
    receive_admin_alerts: bool | None = Field(None, description="Whether the user receives administrative alerts such as certificate expiration and usage overages."),
    require_2fa: Literal["use_system_setting", "always_require", "never_require"] | None = Field(None, description="Whether two-factor authentication is required for this user's login."),
    require_password_change: bool | None = Field(None, description="Whether the user must change their password on the next login."),
    restapi_permission: bool | None = Field(None, description="Whether the user can authenticate and access the REST API."),
    self_managed: bool | None = Field(None, description="Whether this user manages their own credentials or is a shared/bot account with managed credentials."),
    sftp_permission: bool | None = Field(None, description="Whether the user can access files and folders via SFTP protocol."),
    site_admin: bool | None = Field(None, description="Whether the user has administrator privileges for this site."),
    skip_welcome_screen: bool | None = Field(None, description="Whether to skip displaying the welcome screen to the user on first login."),
    ssl_required: Literal["use_system_setting", "always_require", "never_require"] | None = Field(None, description="Whether SSL/TLS encryption is required for this user's connections."),
    sso_strategy_id: str | None = Field(None, description="The ID of the SSO (Single Sign On) strategy to use for this user's authentication."),
    subscribe_to_newsletter: bool | None = Field(None, description="Whether the user is subscribed to receive newsletter communications."),
    time_zone: str | None = Field(None, description="The user's time zone for scheduling and time-based operations."),
    user_root: str | None = Field(None, description="Root folder path for FTP access and optionally SFTP if configured site-wide. Not used for API, desktop, or web interface access."),
    username: str | None = Field(None, description="User's username"),
) -> dict[str, Any] | ToolResult:
    """Create a new user within a specified group with configurable authentication, permissions, and access settings."""

    _group_id = _parse_int(group_id)
    _notification_daily_send_time = _parse_int(notification_daily_send_time)
    _password_validity_days = _parse_int(password_validity_days)
    _sso_strategy_id = _parse_int(sso_strategy_id)

    # Construct request model with validation
    try:
        _request = _models.PostGroupsGroupIdUsersRequest(
            path=_models.PostGroupsGroupIdUsersRequestPath(group_id=_group_id),
            body=_models.PostGroupsGroupIdUsersRequestBody(allowed_ips=allowed_ips, announcements_read=announcements_read, authenticate_until=authenticate_until, authentication_method=authentication_method, billing_permission=billing_permission, bypass_inactive_disable=bypass_inactive_disable, bypass_site_allowed_ips=bypass_site_allowed_ips, company=company, dav_permission=dav_permission, disabled=disabled, email=email, ftp_permission=ftp_permission, grant_permission=grant_permission, header_text=header_text, language=language, name=name, notes=notes, notification_daily_send_time=_notification_daily_send_time, office_integration_enabled=office_integration_enabled, password_validity_days=_password_validity_days, receive_admin_alerts=receive_admin_alerts, require_2fa=require_2fa, require_password_change=require_password_change, restapi_permission=restapi_permission, self_managed=self_managed, sftp_permission=sftp_permission, site_admin=site_admin, skip_welcome_screen=skip_welcome_screen, ssl_required=ssl_required, sso_strategy_id=_sso_strategy_id, subscribe_to_newsletter=subscribe_to_newsletter, time_zone=time_zone, user_root=user_root, username=username)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_group_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{group_id}/users", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{group_id}/users"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_group_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_group_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_group_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: groups
@mcp.tool()
async def get_group(id_: str = Field(..., alias="id", description="The unique identifier of the group to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific group by its ID."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetGroupsIdRequest(
            path=_models.GetGroupsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{id}"
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

# Tags: groups
@mcp.tool()
async def update_group(
    id_: str = Field(..., alias="id", description="The unique identifier of the group to update."),
    admin_ids: str | None = Field(None, description="Comma-separated list of user IDs to designate as group administrators."),
    name: str | None = Field(None, description="The name of the group."),
    notes: str | None = Field(None, description="Additional notes or description for the group."),
    user_ids: str | None = Field(None, description="Comma-separated list of user IDs to add as members of the group."),
) -> dict[str, Any] | ToolResult:
    """Update an existing group's properties including name, notes, members, and administrators. Provide only the fields you want to modify."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PatchGroupsIdRequest(
            path=_models.PatchGroupsIdRequestPath(id_=_id_),
            body=_models.PatchGroupsIdRequestBody(admin_ids=admin_ids, name=name, notes=notes, user_ids=user_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_group", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_group",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: groups
@mcp.tool()
async def delete_group(id_: str = Field(..., alias="id", description="The unique identifier of the group to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a group by its ID. This action cannot be undone."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteGroupsIdRequest(
            path=_models.DeleteGroupsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{id}"
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

# Tags: history
@mcp.tool()
async def list_history(
    start_at: str | None = Field(None, description="Filter to exclude history entries before this date and time. Leave blank to include all earlier entries."),
    end_at: str | None = Field(None, description="Filter to exclude history entries after this date and time. Leave blank to include all later entries."),
    display: str | None = Field(None, description="Control the detail level of returned history entries. Use `full` for complete details or `parent` for parent-only view. Leave blank for default format."),
    per_page: str | None = Field(None, description="Number of history records to return per page. Maximum allowed is 10,000, though 1,000 or fewer is recommended for optimal performance."),
    sort_field: str | None = Field(None, description="Field to sort by. Valid values: 'path', 'folder', 'user_id', 'created_at'"),
    sort_direction: str | None = Field(None, description="Sort direction. Valid values: 'asc' or 'desc'"),
) -> dict[str, Any] | ToolResult:
    """Retrieve the complete action history for the site with optional filtering by date range and customizable display format."""

    # Call helper functions
    sort_by = build_sort_by(sort_field, sort_direction)

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.HistoryListRequest(
            query=_models.HistoryListRequestQuery(start_at=start_at, end_at=end_at, display=display, per_page=_per_page, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: history
@mcp.tool()
async def list_file_history(
    path: str = Field(..., description="The file path to retrieve history for."),
    start_at: str | None = Field(None, description="Filter to only include history entries created on or after this date and time."),
    end_at: str | None = Field(None, description="Filter to only include history entries created on or before this date and time."),
    display: str | None = Field(None, description="Control the detail level of returned records. Use `full` for complete details or `parent` for parent-only information."),
    per_page: str | None = Field(None, description="Number of records to return per page. Maximum is 10,000; 1,000 or less is recommended."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Use object notation (e.g., `sort_by[user_id]=desc`). Valid fields are `user_id` and `created_at`."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the change history for a specific file, with optional filtering by date range and customizable sorting and pagination."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.HistoryListForFileRequest(
            path=_models.HistoryListForFileRequestPath(path=path),
            query=_models.HistoryListForFileRequestQuery(start_at=start_at, end_at=end_at, display=display, per_page=_per_page, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/history/files/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/history/files/{path}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: history
@mcp.tool()
async def list_folder_history(
    path: str = Field(..., description="The folder path for which to retrieve history."),
    start_at: str | None = Field(None, description="Filter to exclude history entries created before this date and time."),
    end_at: str | None = Field(None, description="Filter to exclude history entries created after this date and time."),
    display: str | None = Field(None, description="Control the detail level of returned records: `full` for complete details or `parent` for parent-only information."),
    per_page: str | None = Field(None, description="Number of history records to return per page. Recommended maximum is 1,000 for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Supported fields are `user_id` and `created_at`."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the change history for a specific folder, with optional filtering by date range and customizable sorting and pagination."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.HistoryListForFolderRequest(
            path=_models.HistoryListForFolderRequestPath(path=path),
            query=_models.HistoryListForFolderRequestQuery(start_at=start_at, end_at=end_at, display=display, per_page=_per_page, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_folder_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/history/folders/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/history/folders/{path}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_folder_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_folder_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_folder_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: history
@mcp.tool()
async def list_logins(
    start_at: str | None = Field(None, description="Filter to exclude login records before this date and time. Leave blank to include all earlier entries."),
    end_at: str | None = Field(None, description="Filter to exclude login records after this date and time. Leave blank to include all later entries."),
    display: str | None = Field(None, description="Control the response format. Use `full` for complete details or `parent` for parent-level information only."),
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended maximum is 1,000 for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Use format `sort_by[field_name]=direction` where field_name is `user_id` or `created_at` and direction is `asc` or `desc`."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of site login history with optional filtering by date range and sorting capabilities."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.HistoryListLoginsRequest(
            query=_models.HistoryListLoginsRequestQuery(start_at=start_at, end_at=end_at, display=display, per_page=_per_page, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_logins: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/history/login"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_logins")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_logins", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_logins",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: history
@mcp.tool()
async def list_user_history(
    user_id: str = Field(..., description="The unique identifier of the user whose history records should be retrieved."),
    start_at: str | None = Field(None, description="Filter to exclude history entries created before this date and time. Leave blank to include all earlier entries."),
    end_at: str | None = Field(None, description="Filter to exclude history entries created after this date and time. Leave blank to include all later entries."),
    display: str | None = Field(None, description="Control the detail level of returned records. Use `full` for complete details or `parent` for parent-only information."),
    per_page: str | None = Field(None, description="Maximum number of records to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Use field names `user_id` or `created_at` with direction indicators."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of history records for a specific user, with optional filtering by date range and customizable sorting and display format."""

    _user_id = _parse_int(user_id)
    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.HistoryListForUserRequest(
            path=_models.HistoryListForUserRequestPath(user_id=_user_id),
            query=_models.HistoryListForUserRequestQuery(start_at=start_at, end_at=end_at, display=display, per_page=_per_page, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/history/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/history/users/{user_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: history_export_results
@mcp.tool()
async def list_history_export_results(
    history_export_id: str = Field(..., description="The unique identifier of the history export whose results you want to retrieve."),
    per_page: str | None = Field(None, description="Number of results to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 is supported."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of results from a completed history export. Use the history export ID to fetch the exported records with configurable page size."""

    _history_export_id = _parse_int(history_export_id)
    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetHistoryExportResultsRequest(
            query=_models.GetHistoryExportResultsRequestQuery(per_page=_per_page, history_export_id=_history_export_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_history_export_results: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/history_export_results"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_history_export_results")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_history_export_results", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_history_export_results",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: history_exports
@mcp.tool()
async def create_history_export(
    end_at: str | None = Field(None, description="End date and time for the export range (inclusive). Use ISO 8601 format."),
    query_action: str | None = Field(None, description="Filter exported history records by action type performed (e.g., file operations, user management, authentication events)."),
    query_destination: str | None = Field(None, description="Filter results to include only file move operations with this destination path."),
    query_failure_type: str | None = Field(None, description="When filtering for login failures, restrict results to failures of this specific type."),
    query_file_id: str | None = Field(None, description="Filter results to include only actions related to the specified file ID."),
    query_folder: str | None = Field(None, description="Filter results to include only actions on files or folders within this folder path."),
    query_interface: str | None = Field(None, description="Filter exported history records by the interface or protocol used to perform the action."),
    query_ip: str | None = Field(None, description="Filter results to include only actions originating from this IP address."),
    query_parent_id: str | None = Field(None, description="Filter results to include only actions within the parent folder specified by this folder ID."),
    query_path: str | None = Field(None, description="Filter results to include only actions related to this file or folder path."),
    query_src: str | None = Field(None, description="Filter results to include only file move operations originating from this source path."),
    query_target_id: str | None = Field(None, description="Filter results to include only actions on objects (users, API keys, etc.) matching this target object ID."),
    query_target_name: str | None = Field(None, description="Filter results to include only actions on objects (users, groups, etc.) matching this name or username."),
    query_target_permission: str | None = Field(None, description="When filtering for permission-related actions, restrict results to permissions at this access level."),
    query_target_permission_set: str | None = Field(None, description="When filtering for API key actions, restrict results to API keys with this permission set."),
    query_target_platform: str | None = Field(None, description="When filtering for API key actions, restrict results to API keys associated with this platform."),
    query_user_id: str | None = Field(None, description="Filter results to include only actions performed by the user with this user ID."),
    query_username: str | None = Field(None, description="Filter results to include only actions performed by this username."),
    start_at: str | None = Field(None, description="Start date and time for the export range (inclusive). Use ISO 8601 format."),
) -> dict[str, Any] | ToolResult:
    """Initiate a history export with optional filtering by date range, user, action type, interface, and target object. Returns an export job that can be monitored for completion."""

    # Construct request model with validation
    try:
        _request = _models.PostHistoryExportsRequest(
            body=_models.PostHistoryExportsRequestBody(end_at=end_at, query_action=query_action, query_destination=query_destination, query_failure_type=query_failure_type, query_file_id=query_file_id, query_folder=query_folder, query_interface=query_interface, query_ip=query_ip, query_parent_id=query_parent_id, query_path=query_path, query_src=query_src, query_target_id=query_target_id, query_target_name=query_target_name, query_target_permission=query_target_permission, query_target_permission_set=query_target_permission_set, query_target_platform=query_target_platform, query_user_id=query_user_id, query_username=query_username, start_at=start_at)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_history_export: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/history_exports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_history_export")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_history_export", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_history_export",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: history_exports
@mcp.tool()
async def get_history_export(id_: str = Field(..., alias="id", description="The unique identifier of the history export to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details of a specific history export by its ID. Use this to check the status, metadata, and information about a previously created history export."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetHistoryExportsIdRequest(
            path=_models.GetHistoryExportsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_history_export: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/history_exports/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/history_exports/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_history_export")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_history_export", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_history_export",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: inbox_recipients
@mcp.tool()
async def list_inbox_recipients(
    inbox_id: str = Field(..., description="The unique identifier of the inbox for which to list recipients."),
    per_page: str | None = Field(None, description="Maximum number of records to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Only `has_registrations` is supported as a sortable field."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of recipients associated with a specific inbox. Use sorting and pagination to manage large result sets."""

    _inbox_id = _parse_int(inbox_id)
    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetInboxRecipientsRequest(
            query=_models.GetInboxRecipientsRequestQuery(per_page=_per_page, sort_by=sort_by, inbox_id=_inbox_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_inbox_recipients: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/inbox_recipients"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_inbox_recipients")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_inbox_recipients", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_inbox_recipients",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: inbox_recipients
@mcp.tool()
async def share_inbox_with_recipient(
    inbox_id: str = Field(..., description="The ID of the inbox to be shared with the recipient."),
    recipient: str = Field(..., description="Email address of the recipient who will receive access to the inbox."),
    company: str | None = Field(None, description="Company name associated with the recipient for organizational context."),
    name: str | None = Field(None, description="Full name of the recipient for identification purposes."),
    note: str | None = Field(None, description="Optional message to include in the notification email sent to the recipient."),
    share_after_create: bool | None = Field(None, description="When true, automatically sends a sharing notification email to the recipient upon creation."),
) -> dict[str, Any] | ToolResult:
    """Grant a recipient access to an inbox by sharing it with their email address. Optionally send them a notification email upon creation."""

    _inbox_id = _parse_int(inbox_id)

    # Construct request model with validation
    try:
        _request = _models.PostInboxRecipientsRequest(
            body=_models.PostInboxRecipientsRequestBody(company=company, inbox_id=_inbox_id, name=name, note=note, recipient=recipient, share_after_create=share_after_create)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for share_inbox_with_recipient: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/inbox_recipients"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("share_inbox_with_recipient")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("share_inbox_with_recipient", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="share_inbox_with_recipient",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: inbox_registrations
@mcp.tool()
async def list_inbox_registrations(
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000."),
    folder_behavior_id: str | None = Field(None, description="Filter results by the ID of the associated inbox. When provided, only registrations for that specific inbox are returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of inbox registrations, optionally filtered by a specific inbox. Use pagination parameters to control result set size."""

    _per_page = _parse_int(per_page)
    _folder_behavior_id = _parse_int(folder_behavior_id)

    # Construct request model with validation
    try:
        _request = _models.GetInboxRegistrationsRequest(
            query=_models.GetInboxRegistrationsRequestQuery(per_page=_per_page, folder_behavior_id=_folder_behavior_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_inbox_registrations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/inbox_registrations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_inbox_registrations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_inbox_registrations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_inbox_registrations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: inbox_uploads
@mcp.tool()
async def list_inbox_uploads(
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Only `created_at` is supported as a valid sort field."),
    inbox_registration_id: str | None = Field(None, description="Filter uploads by the associated inbox registration ID."),
    inbox_id: str | None = Field(None, description="Filter uploads by the associated inbox ID."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of uploads associated with inboxes. Filter by specific inbox or inbox registration, and optionally sort results by creation date."""

    _per_page = _parse_int(per_page)
    _inbox_registration_id = _parse_int(inbox_registration_id)
    _inbox_id = _parse_int(inbox_id)

    # Construct request model with validation
    try:
        _request = _models.GetInboxUploadsRequest(
            query=_models.GetInboxUploadsRequestQuery(per_page=_per_page, sort_by=sort_by, inbox_registration_id=_inbox_registration_id, inbox_id=_inbox_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_inbox_uploads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/inbox_uploads"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_inbox_uploads")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_inbox_uploads", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_inbox_uploads",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: invoices
@mcp.tool()
async def list_invoices(per_page: str | None = Field(None, description="Number of invoice records to return per page. Recommended to use 1,000 or less for optimal performance.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of invoices. Use the per_page parameter to control the number of results returned per page."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetInvoicesRequest(
            query=_models.GetInvoicesRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_invoices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/invoices"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_invoices")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_invoices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_invoices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: invoices
@mcp.tool()
async def get_invoice(id_: str = Field(..., alias="id", description="The unique identifier of the invoice to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific invoice by its ID. Returns detailed invoice information including amounts, dates, and line items."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetInvoicesIdRequest(
            path=_models.GetInvoicesIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_invoice: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/invoices/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/invoices/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_invoice")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_invoice", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_invoice",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: ip_addresses
@mcp.tool()
async def list_ip_addresses(per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, though the API supports up to 10,000 records per page.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of IP addresses associated with the current site. Use the per_page parameter to control result set size."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetIpAddressesRequest(
            query=_models.GetIpAddressesRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_ip_addresses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/ip_addresses"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_ip_addresses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_ip_addresses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_ip_addresses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: ip_addresses
@mcp.tool()
async def list_exavault_reserved_ip_addresses(per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000 records per page.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of all public IP addresses reserved and used by ExaVault for its services. Use this to configure firewall rules or IP allowlists for ExaVault connectivity."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetIpAddressesExavaultReservedRequest(
            query=_models.GetIpAddressesExavaultReservedRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_exavault_reserved_ip_addresses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/ip_addresses/exavault-reserved"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_exavault_reserved_ip_addresses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_exavault_reserved_ip_addresses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_exavault_reserved_ip_addresses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: ip_addresses
@mcp.tool()
async def list_reserved_ip_addresses(per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000 records per page.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of all reserved public IP addresses available in the system."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetIpAddressesReservedRequest(
            query=_models.GetIpAddressesReservedRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_reserved_ip_addresses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/ip_addresses/reserved"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_reserved_ip_addresses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_reserved_ip_addresses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_reserved_ip_addresses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: locks
@mcp.tool()
async def list_locks(
    path: str = Field(..., description="The resource path for which to retrieve locks."),
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000."),
    include_children: bool | None = Field(None, description="Whether to include locks from child objects in addition to the specified path."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all locks for a specified path, with optional support for including locks from child objects and pagination control."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.LockListForPathRequest(
            path=_models.LockListForPathRequestPath(path=path),
            query=_models.LockListForPathRequestQuery(per_page=_per_page, include_children=include_children)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_locks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/locks/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/locks/{path}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_locks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_locks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_locks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: locks
@mcp.tool()
async def release_lock(
    path: str = Field(..., description="The resource path for which the lock should be released."),
    token: str = Field(..., description="The unique token that identifies and authorizes the release of this specific lock."),
) -> dict[str, Any] | ToolResult:
    """Release a lock on a resource by providing its path and token. This removes the lock, allowing other operations to proceed."""

    # Construct request model with validation
    try:
        _request = _models.DeleteLocksPathRequest(
            path=_models.DeleteLocksPathRequestPath(path=path),
            query=_models.DeleteLocksPathRequestQuery(token=token)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for release_lock: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/locks/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/locks/{path}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("release_lock")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("release_lock", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="release_lock",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: message_comment_reactions
@mcp.tool()
async def list_message_comment_reactions(
    message_comment_id: str = Field(..., description="The ID of the message comment for which to retrieve reactions."),
    per_page: str | None = Field(None, description="Maximum number of reactions to return per page. Recommended to use 1,000 or less for optimal performance."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all reactions added to a specific message comment. Results are paginated and can be controlled via the per_page parameter."""

    _message_comment_id = _parse_int(message_comment_id)
    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetMessageCommentReactionsRequest(
            query=_models.GetMessageCommentReactionsRequestQuery(per_page=_per_page, message_comment_id=_message_comment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_message_comment_reactions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/message_comment_reactions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_message_comment_reactions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_message_comment_reactions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_message_comment_reactions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: message_comment_reactions
@mcp.tool()
async def get_message_comment_reaction(id_: str = Field(..., alias="id", description="The unique identifier of the message comment reaction to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details of a specific message comment reaction by its ID. Use this to fetch information about a user's reaction to a message comment."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetMessageCommentReactionsIdRequest(
            path=_models.GetMessageCommentReactionsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_message_comment_reaction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/message_comment_reactions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/message_comment_reactions/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_message_comment_reaction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_message_comment_reaction", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_message_comment_reaction",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: message_comment_reactions
@mcp.tool()
async def remove_message_comment_reaction(id_: str = Field(..., alias="id", description="The unique identifier of the message comment reaction to delete.")) -> dict[str, Any] | ToolResult:
    """Remove a reaction from a message comment. Deletes the specified reaction by its ID."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteMessageCommentReactionsIdRequest(
            path=_models.DeleteMessageCommentReactionsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_message_comment_reaction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/message_comment_reactions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/message_comment_reactions/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_message_comment_reaction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_message_comment_reaction", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_message_comment_reaction",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: message_comments
@mcp.tool()
async def list_message_comments(
    message_id: str = Field(..., description="The ID of the message for which to retrieve comments."),
    per_page: str | None = Field(None, description="Maximum number of comments to return per page. Recommended to use 1,000 or less for optimal performance."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all comments associated with a specific message. Results are paginated and can be controlled via the per_page parameter."""

    _message_id = _parse_int(message_id)
    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetMessageCommentsRequest(
            query=_models.GetMessageCommentsRequestQuery(per_page=_per_page, message_id=_message_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_message_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/message_comments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_message_comments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_message_comments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_message_comments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: message_comments
@mcp.tool()
async def get_message_comment(id_: str = Field(..., alias="id", description="The unique identifier of the message comment to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific message comment by its ID. Returns the full details of the requested comment."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetMessageCommentsIdRequest(
            path=_models.GetMessageCommentsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_message_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/message_comments/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/message_comments/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_message_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_message_comment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_message_comment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: message_comments
@mcp.tool()
async def update_message_comment(
    id_: str = Field(..., alias="id", description="The unique identifier of the message comment to update."),
    body: str = Field(..., description="The updated text content for the message comment."),
) -> dict[str, Any] | ToolResult:
    """Update the body text of an existing message comment. Allows modification of comment content after initial creation."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PatchMessageCommentsIdRequest(
            path=_models.PatchMessageCommentsIdRequestPath(id_=_id_),
            body=_models.PatchMessageCommentsIdRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_message_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/message_comments/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/message_comments/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_message_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_message_comment", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_message_comment",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: message_comments
@mcp.tool()
async def delete_message_comment(id_: str = Field(..., alias="id", description="The unique identifier of the message comment to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a specific message comment by its ID. This operation permanently removes the comment from the message thread."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteMessageCommentsIdRequest(
            path=_models.DeleteMessageCommentsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_message_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/message_comments/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/message_comments/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_message_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_message_comment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_message_comment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: message_reactions
@mcp.tool()
async def list_message_reactions(
    message_id: str = Field(..., description="The ID of the message to retrieve reactions for."),
    per_page: str | None = Field(None, description="Maximum number of reactions to return per page. Recommended to use 1,000 or less for optimal performance."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all reactions added to a specific message. Supports pagination to control the number of results returned per page."""

    _message_id = _parse_int(message_id)
    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetMessageReactionsRequest(
            query=_models.GetMessageReactionsRequestQuery(per_page=_per_page, message_id=_message_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_message_reactions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/message_reactions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_message_reactions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_message_reactions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_message_reactions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: message_reactions
@mcp.tool()
async def get_message_reaction(id_: str = Field(..., alias="id", description="The unique identifier of the message reaction to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details of a specific message reaction by its ID. Use this to fetch information about a single reaction to a message."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetMessageReactionsIdRequest(
            path=_models.GetMessageReactionsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_message_reaction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/message_reactions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/message_reactions/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_message_reaction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_message_reaction", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_message_reaction",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: message_reactions
@mcp.tool()
async def remove_message_reaction(id_: str = Field(..., alias="id", description="The unique identifier of the message reaction to delete.")) -> dict[str, Any] | ToolResult:
    """Remove a reaction from a message by its reaction ID. This deletes the association between the user and the message reaction."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteMessageReactionsIdRequest(
            path=_models.DeleteMessageReactionsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_message_reaction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/message_reactions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/message_reactions/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_message_reaction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_message_reaction", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_message_reaction",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: messages
@mcp.tool()
async def list_messages(
    project_id: str = Field(..., description="The project ID for which to retrieve messages. Required to scope results to a specific project."),
    per_page: str | None = Field(None, description="Number of messages to return per page. Recommended to use 1,000 or less for optimal performance."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of messages for a specific project. Use pagination parameters to control the number of results returned per page."""

    _project_id = _parse_int(project_id)
    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetMessagesRequest(
            query=_models.GetMessagesRequestQuery(per_page=_per_page, project_id=_project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_messages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/messages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_messages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_messages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_messages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: messages
@mcp.tool()
async def create_message(
    body: str = Field(..., description="The content of the message to be created."),
    project_id: str = Field(..., description="The unique identifier of the project to which this message should be attached."),
    subject: str = Field(..., description="The subject line or title for the message."),
) -> dict[str, Any] | ToolResult:
    """Create a new message attached to a specific project. Messages can be used for project communication and collaboration."""

    _project_id = _parse_int(project_id)

    # Construct request model with validation
    try:
        _request = _models.PostMessagesRequest(
            body=_models.PostMessagesRequestBody(body=body, project_id=_project_id, subject=subject)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/messages"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_message", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_message",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: messages
@mcp.tool()
async def get_message(id_: str = Field(..., alias="id", description="The unique identifier of the message to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific message by its ID. Returns the full message details including content, metadata, and timestamps."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetMessagesIdRequest(
            path=_models.GetMessagesIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/messages/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/messages/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: messages
@mcp.tool()
async def update_message(
    id_: str = Field(..., alias="id", description="The unique identifier of the message to update."),
    body: str = Field(..., description="The new content body for the message."),
    project_id: str = Field(..., description="The project ID to which this message should be attached or reassigned."),
    subject: str = Field(..., description="The new subject line for the message."),
) -> dict[str, Any] | ToolResult:
    """Update an existing message with new subject and body content. The message will be associated with the specified project."""

    _id_ = _parse_int(id_)
    _project_id = _parse_int(project_id)

    # Construct request model with validation
    try:
        _request = _models.PatchMessagesIdRequest(
            path=_models.PatchMessagesIdRequestPath(id_=_id_),
            body=_models.PatchMessagesIdRequestBody(body=body, project_id=_project_id, subject=subject)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/messages/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/messages/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_message", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_message",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: messages
@mcp.tool()
async def delete_message(id_: str = Field(..., alias="id", description="The unique identifier of the message to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a message by its ID. This action cannot be undone."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteMessagesIdRequest(
            path=_models.DeleteMessagesIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/messages/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/messages/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_message", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_message",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: notifications
@mcp.tool()
async def list_notifications(
    per_page: str | None = Field(None, description="Maximum number of notification records to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Valid sortable fields are `path`, `user_id`, or `group_id`."),
    include_ancestors: bool | None = Field(None, description="When enabled and a `path` filter is applied, include notifications from all parent paths in addition to the specified path. Has no effect if `path` is not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of notifications with optional sorting and ancestor path inclusion. Use this to display notification feeds or audit logs with flexible filtering options."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetNotificationsRequest(
            query=_models.GetNotificationsRequestQuery(per_page=_per_page, sort_by=sort_by, include_ancestors=include_ancestors)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_notifications: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/notifications"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_notifications")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_notifications", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_notifications",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: notifications
@mcp.tool()
async def create_notification(
    message: str | None = Field(None, description="Custom message to include in notification emails sent when the rule is triggered."),
    notify_on_copy: bool | None = Field(None, description="When enabled, copying or moving resources into this path will trigger a notification in addition to upload events."),
    notify_on_delete: bool | None = Field(None, description="When enabled, deleting files from this path will trigger a notification."),
    notify_on_download: bool | None = Field(None, description="When enabled, downloading files from this path will trigger a notification."),
    notify_on_move: bool | None = Field(None, description="When enabled, moving files to this path will trigger a notification."),
    notify_on_upload: bool | None = Field(None, description="When enabled, uploading new files to this path will trigger a notification."),
    notify_user_actions: bool | None = Field(None, description="When enabled, actions initiated by the user account itself will still result in a notification."),
    recursive: bool | None = Field(None, description="When enabled, notifications will be triggered for actions in all subfolders under this path."),
    send_interval: str | None = Field(None, description="The time interval over which notifications are aggregated before being sent. Longer intervals batch multiple events into a single notification."),
    trigger_by_share_recipients: bool | None = Field(None, description="When enabled, notifications will be triggered for actions performed by users who have access through a share link or shared folder."),
    triggering_filenames: list[str] | None = Field(None, description="Array of filename patterns to match against the action path. Supports wildcards to filter which files trigger notifications. Patterns are evaluated in order."),
    triggering_group_ids: list[int] | None = Field(None, description="Array of group IDs. When specified, only actions performed by members of these groups will trigger notifications."),
    triggering_user_ids: list[int] | None = Field(None, description="Array of user IDs. When specified, only actions performed by these users will trigger notifications."),
    path: str | None = Field(None, description="Path"),
    user_id: str | None = Field(None, description="The id of the user to notify. Provide `user_id`, `username` or `group_id`."),
    group_id: str | None = Field(None, description="The ID of the group to notify.  Provide `user_id`, `username` or `group_id`."),
) -> dict[str, Any] | ToolResult:
    """Create a notification rule that triggers on specified file system actions within a path. Configure which actions trigger notifications, who performs them, and how notifications are aggregated."""

    _user_id = _parse_int(user_id)
    _group_id = _parse_int(group_id)

    # Construct request model with validation
    try:
        _request = _models.PostNotificationsRequest(
            body=_models.PostNotificationsRequestBody(message=message, notify_on_copy=notify_on_copy, notify_on_delete=notify_on_delete, notify_on_download=notify_on_download, notify_on_move=notify_on_move, notify_on_upload=notify_on_upload, notify_user_actions=notify_user_actions, recursive=recursive, send_interval=send_interval, trigger_by_share_recipients=trigger_by_share_recipients, triggering_filenames=triggering_filenames, triggering_group_ids=triggering_group_ids, triggering_user_ids=triggering_user_ids, path=path, user_id=_user_id, group_id=_group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_notification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/notifications"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_notification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_notification", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_notification",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: notifications
@mcp.tool()
async def get_notification(id_: str = Field(..., alias="id", description="The unique identifier of the notification to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific notification by its ID. Returns the full details of the requested notification."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetNotificationsIdRequest(
            path=_models.GetNotificationsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_notification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/notifications/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/notifications/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_notification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_notification", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_notification",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: notifications
@mcp.tool()
async def update_notification(
    id_: str = Field(..., alias="id", description="The unique identifier of the notification rule to update."),
    message: str | None = Field(None, description="Custom message text to include in notification emails sent for this rule."),
    notify_on_copy: bool | None = Field(None, description="When enabled, copying or moving resources into the monitored path will trigger notifications in addition to upload events."),
    notify_on_delete: bool | None = Field(None, description="When enabled, file deletions from the monitored path will trigger notifications."),
    notify_on_download: bool | None = Field(None, description="When enabled, file downloads from the monitored path will trigger notifications."),
    notify_on_move: bool | None = Field(None, description="When enabled, file moves to the monitored path will trigger notifications."),
    notify_on_upload: bool | None = Field(None, description="When enabled, file uploads to the monitored path will trigger notifications."),
    notify_user_actions: bool | None = Field(None, description="When enabled, notifications will be sent for actions initiated by the user account itself, not just external actions."),
    recursive: bool | None = Field(None, description="When enabled, notifications will apply to all subfolders within the monitored path."),
    send_interval: str | None = Field(None, description="The time interval over which notifications are aggregated before sending. Valid values are five_minutes, fifteen_minutes, hourly, or daily."),
    trigger_by_share_recipients: bool | None = Field(None, description="When enabled, actions performed by share recipients will trigger notifications."),
    triggering_filenames: list[str] | None = Field(None, description="Array of filename patterns (supporting wildcards) to match against action paths. Only actions on matching files will trigger notifications."),
    triggering_group_ids: list[int] | None = Field(None, description="Array of group IDs. When specified, only actions performed by members of these groups will trigger notifications."),
    triggering_user_ids: list[int] | None = Field(None, description="Array of user IDs. When specified, only actions performed by these users will trigger notifications."),
) -> dict[str, Any] | ToolResult:
    """Update notification settings for a specific notification rule, including trigger conditions, aggregation intervals, and recipient filters."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PatchNotificationsIdRequest(
            path=_models.PatchNotificationsIdRequestPath(id_=_id_),
            body=_models.PatchNotificationsIdRequestBody(message=message, notify_on_copy=notify_on_copy, notify_on_delete=notify_on_delete, notify_on_download=notify_on_download, notify_on_move=notify_on_move, notify_on_upload=notify_on_upload, notify_user_actions=notify_user_actions, recursive=recursive, send_interval=send_interval, trigger_by_share_recipients=trigger_by_share_recipients, triggering_filenames=triggering_filenames, triggering_group_ids=triggering_group_ids, triggering_user_ids=triggering_user_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_notification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/notifications/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/notifications/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_notification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_notification", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_notification",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: notifications
@mcp.tool()
async def delete_notification(id_: str = Field(..., alias="id", description="The unique identifier of the notification to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a notification by its ID. This action cannot be undone."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteNotificationsIdRequest(
            path=_models.DeleteNotificationsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_notification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/notifications/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/notifications/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_notification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_notification", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_notification",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: payments
@mcp.tool()
async def list_payments(per_page: str | None = Field(None, description="Number of payment records to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 is supported.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of payments. Use the per_page parameter to control the number of records returned per page."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetPaymentsRequest(
            query=_models.GetPaymentsRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_payments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/payments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_payments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_payments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_payments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: payments
@mcp.tool()
async def get_payment(id_: str = Field(..., alias="id", description="The unique identifier of the payment to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details for a specific payment by its ID. Returns the payment information including amount, status, and transaction details."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetPaymentsIdRequest(
            path=_models.GetPaymentsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_payment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/payments/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/payments/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_payment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_payment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_payment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: permissions
@mcp.tool()
async def list_permissions(
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 is supported."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Valid sortable fields are: group_id, path, user_id, or permission."),
    include_groups: bool | None = Field(None, description="When filtering by user or group, include permissions inherited from the user's group memberships in addition to directly assigned permissions."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of permissions with optional sorting and group inheritance filtering. Use this to view all permissions in the system, optionally including permissions inherited from group memberships."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetPermissionsRequest(
            query=_models.GetPermissionsRequestQuery(per_page=_per_page, sort_by=sort_by, include_groups=include_groups)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/permissions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_permissions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_permissions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: permissions
@mcp.tool()
async def create_permission(
    permission: str | None = Field(None, description="The access level type to assign. Determines what actions are permitted."),
    recursive: bool | None = Field(None, description="Whether to apply this permission to all subfolders in addition to the target folder."),
    path: str | None = Field(None, description="Folder path"),
    user_id: str | None = Field(None, description="User ID.  Provide `username` or `user_id`"),
    group_id: str | None = Field(None, description="Group ID"),
) -> dict[str, Any] | ToolResult:
    """Create a new permission with specified access level and optional recursive application to subfolders."""

    _user_id = _parse_int(user_id)
    _group_id = _parse_int(group_id)

    # Construct request model with validation
    try:
        _request = _models.PostPermissionsRequest(
            body=_models.PostPermissionsRequestBody(permission=permission, recursive=recursive, path=path, user_id=_user_id, group_id=_group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/permissions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_permission", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_permission",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: permissions
@mcp.tool()
async def delete_permission(id_: str = Field(..., alias="id", description="The unique identifier of the permission to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a permission by its ID. This operation permanently removes the specified permission from the system."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeletePermissionsIdRequest(
            path=_models.DeletePermissionsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/permissions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/permissions/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_permission", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_permission",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: projects
@mcp.tool()
async def create_project(global_access: str = Field(..., description="Sets the global access level for the project, controlling visibility and permissions for all users in the organization.")) -> dict[str, Any] | ToolResult:
    """Create a new project with specified global access permissions. Global access determines who can view or modify the project across your organization."""

    # Construct request model with validation
    try:
        _request = _models.PostProjectsRequest(
            body=_models.PostProjectsRequestBody(global_access=global_access)
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
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: projects
@mcp.tool()
async def get_project(id_: str = Field(..., alias="id", description="The unique identifier of the project to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific project by its ID."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetProjectsIdRequest(
            path=_models.GetProjectsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}"
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

# Tags: projects
@mcp.tool()
async def delete_project(id_: str = Field(..., alias="id", description="The unique identifier of the project to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a project by its ID. This action cannot be undone."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteProjectsIdRequest(
            path=_models.DeleteProjectsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}"
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

# Tags: public_keys
@mcp.tool()
async def list_public_keys(per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of public keys. Use the per_page parameter to control the number of results returned per page."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetPublicKeysRequest(
            query=_models.GetPublicKeysRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_public_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/public_keys"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_public_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_public_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_public_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: public_keys
@mcp.tool()
async def create_public_key(
    public_key: str = Field(..., description="The complete SSH public key content in standard format (typically starting with ssh-rsa, ssh-ed25519, or similar)."),
    title: str = Field(..., description="A descriptive name or label for this public key to help identify it among multiple keys."),
) -> dict[str, Any] | ToolResult:
    """Create a new SSH public key for authentication. The key is stored with an internal reference title for easy identification."""

    # Construct request model with validation
    try:
        _request = _models.PostPublicKeysRequest(
            body=_models.PostPublicKeysRequestBody(public_key=public_key, title=title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_public_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/public_keys"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_public_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_public_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_public_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: public_keys
@mcp.tool()
async def get_public_key(id_: str = Field(..., alias="id", description="The unique identifier of the public key to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific public key by its ID. Use this to fetch details of a previously created or stored public key."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetPublicKeysIdRequest(
            path=_models.GetPublicKeysIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_public_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/public_keys/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/public_keys/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_public_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_public_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_public_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: public_keys
@mcp.tool()
async def update_public_key(
    id_: str = Field(..., alias="id", description="The unique identifier of the public key to update."),
    title: str = Field(..., description="A descriptive name or label for the public key used for internal reference and identification."),
) -> dict[str, Any] | ToolResult:
    """Update the title or metadata of an existing public key. This allows you to change the internal reference name for a key that has already been created."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PatchPublicKeysIdRequest(
            path=_models.PatchPublicKeysIdRequestPath(id_=_id_),
            body=_models.PatchPublicKeysIdRequestBody(title=title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_public_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/public_keys/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/public_keys/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_public_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_public_key", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_public_key",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: public_keys
@mcp.tool()
async def delete_public_key(id_: str = Field(..., alias="id", description="The unique identifier of the public key to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a public key by its ID. This action cannot be undone."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeletePublicKeysIdRequest(
            path=_models.DeletePublicKeysIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_public_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/public_keys/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/public_keys/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_public_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_public_key", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_public_key",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: remote_bandwidth_snapshots
@mcp.tool()
async def list_bandwidth_snapshots_remote(
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Use the field name as the key and 'asc' or 'desc' as the value. Valid sortable field is 'logged_at'."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of remote bandwidth snapshots. Results can be sorted by the logged timestamp in ascending or descending order."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetRemoteBandwidthSnapshotsRequest(
            query=_models.GetRemoteBandwidthSnapshotsRequestQuery(per_page=_per_page, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_bandwidth_snapshots_remote: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/remote_bandwidth_snapshots"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_bandwidth_snapshots_remote")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_bandwidth_snapshots_remote", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_bandwidth_snapshots_remote",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: remote_servers
@mcp.tool()
async def list_remote_servers(per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of remote servers. Use the per_page parameter to control the number of results returned per page."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetRemoteServersRequest(
            query=_models.GetRemoteServersRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_remote_servers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/remote_servers"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_remote_servers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_remote_servers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_remote_servers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: remote_servers
@mcp.tool()
async def create_remote_server(
    enable_dedicated_ips: bool | None = Field(None, description="When enabled, restricts remote server connections to dedicated IP addresses only."),
    files_agent_permission_set: Literal["read_write", "read_only", "write_only"] | None = Field(None, description="File permissions level for the files agent: read_only allows downloads only, write_only allows uploads only, read_write allows both operations."),
    files_agent_root: str | None = Field(None, description="Local root directory path where the files agent will access files."),
    max_connections: str | None = Field(None, description="Maximum number of parallel connections to the remote server. Ignored for S3 connections which parallelize automatically."),
    name: str | None = Field(None, description="Internal display name for this remote server configuration."),
    one_drive_account_type: Literal["personal", "business_other"] | None = Field(None, description="OneDrive account type: personal for individual accounts or business_other for business/organizational accounts."),
    pin_to_site_region: bool | None = Field(None, description="When enabled, all communications with this remote server route through the primary region of the site. Can be overridden by site-wide settings."),
    private_key: str | None = Field(None, description="Private key for SFTP or other key-based authentication methods."),
    private_key_passphrase: str | None = Field(None, description="Passphrase to decrypt the private key if it is encrypted."),
    s3_bucket: str | None = Field(None, description="AWS S3 bucket name where files will be stored."),
    s3_region: str | None = Field(None, description="AWS region code where the S3 bucket is located."),
    server_certificate: Literal["require_match", "allow_any"] | None = Field(None, description="SSL certificate validation mode: require_match enforces exact certificate matching, allow_any accepts any valid certificate."),
    server_host_key: str | None = Field(None, description="Remote server SSH host key in OpenSSH format (as would appear in ~/.ssh/known_hosts). When provided, the server's host key must match exactly."),
    server_type: Literal["ftp", "sftp", "s3", "google_cloud_storage", "webdav", "wasabi", "backblaze_b2", "one_drive", "rackspace", "box", "dropbox", "google_drive", "azure", "sharepoint", "s3_compatible", "azure_files", "files_agent", "filebase"] | None = Field(None, description="Type of remote server to configure. Determines which authentication credentials and configuration parameters are required."),
    ssl: Literal["if_available", "require", "require_implicit", "never"] | None = Field(None, description="SSL/TLS requirement level: if_available uses SSL when supported, require enforces SSL, require_implicit uses implicit SSL, never disables SSL."),
    ssl_certificate: str | None = Field(None, description="SSL client certificate for mutual TLS authentication with the remote server."),
    aws: _models.PostRemoteServersBodyAws | None = Field(None, description="AWS S3 connection settings (access key, secret key)"),
    azure_blob_storage: _models.PostRemoteServersBodyAzureBlobStorage | None = Field(None, description="Azure Blob Storage connection settings"),
    azure_files_storage: _models.PostRemoteServersBodyAzureFilesStorage | None = Field(None, description="Azure File Storage connection settings"),
    backblaze_b2: _models.PostRemoteServersBodyBackblazeB2 | None = Field(None, description="Backblaze B2 connection settings"),
    filebase: _models.PostRemoteServersBodyFilebase | None = Field(None, description="Filebase connection settings"),
    google_cloud_storage: _models.PostRemoteServersBodyGoogleCloudStorage | None = Field(None, description="Google Cloud Storage connection settings"),
    rackspace: _models.PostRemoteServersBodyRackspace | None = Field(None, description="Rackspace Cloud Files connection settings"),
    s3_compatible: _models.PostRemoteServersBodyS3Compatible | None = Field(None, description="S3-compatible storage connection settings"),
    wasabi: _models.PostRemoteServersBodyWasabi | None = Field(None, description="Wasabi storage connection settings"),
    hostname: str | None = Field(None, description="Hostname or IP address"),
    port: str | None = Field(None, description="Port for remote server.  Not needed for S3."),
) -> dict[str, Any] | ToolResult:
    """Create a remote server configuration for cloud storage or file transfer integration. Supports multiple storage backends including AWS S3, Azure, Google Cloud Storage, and various other cloud providers."""

    _max_connections = _parse_int(max_connections)
    _port = _parse_int(port)

    # Construct request model with validation
    try:
        _request = _models.PostRemoteServersRequest(
            body=_models.PostRemoteServersRequestBody(enable_dedicated_ips=enable_dedicated_ips, files_agent_permission_set=files_agent_permission_set, files_agent_root=files_agent_root, max_connections=_max_connections, name=name, one_drive_account_type=one_drive_account_type, pin_to_site_region=pin_to_site_region, private_key=private_key, private_key_passphrase=private_key_passphrase, s3_bucket=s3_bucket, s3_region=s3_region, server_certificate=server_certificate, server_host_key=server_host_key, server_type=server_type, ssl=ssl, ssl_certificate=ssl_certificate, aws=aws, azure_blob_storage=azure_blob_storage, azure_files_storage=azure_files_storage, backblaze_b2=backblaze_b2, filebase=filebase, google_cloud_storage=google_cloud_storage, rackspace=rackspace, s3_compatible=s3_compatible, wasabi=wasabi, hostname=hostname, port=_port)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_remote_server: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/remote_servers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_remote_server")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_remote_server", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_remote_server",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: remote_servers
@mcp.tool()
async def get_remote_server(id_: str = Field(..., alias="id", description="The unique identifier of the remote server to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details for a specific remote server by its ID. Returns the configuration and status information for the requested remote server."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetRemoteServersIdRequest(
            path=_models.GetRemoteServersIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_remote_server: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/remote_servers/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/remote_servers/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_remote_server")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_remote_server", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_remote_server",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: remote_servers
@mcp.tool()
async def update_remote_server(
    id_: str = Field(..., alias="id", description="The unique identifier of the remote server to update."),
    enable_dedicated_ips: bool | None = Field(None, description="Restrict remote server connections to dedicated IP addresses only."),
    files_agent_permission_set: Literal["read_write", "read_only", "write_only"] | None = Field(None, description="Permission level for the files agent to access local files."),
    files_agent_root: str | None = Field(None, description="Local root directory path for the files agent."),
    hostname: str | None = Field(None, description="Hostname or IP address of the remote server."),
    max_connections: str | None = Field(None, description="Maximum number of parallel connections to the remote server. Ignored for S3 connections which parallelize automatically."),
    name: str | None = Field(None, description="Internal name for the remote server for reference and identification."),
    one_drive_account_type: Literal["personal", "business_other"] | None = Field(None, description="OneDrive account type: personal for individual accounts or business_other for organizational accounts."),
    pin_to_site_region: bool | None = Field(None, description="Force all communications with this remote server through the primary region of the site. Can be overridden by site-wide settings."),
    port: str | None = Field(None, description="Port number for the remote server connection. Not required for S3 or cloud storage providers."),
    private_key: str | None = Field(None, description="Private key for SSH or certificate-based authentication."),
    private_key_passphrase: str | None = Field(None, description="Passphrase to decrypt the private key if it is encrypted."),
    s3_bucket: str | None = Field(None, description="S3 bucket name for file storage."),
    s3_region: str | None = Field(None, description="AWS region code for S3 bucket location."),
    server_certificate: Literal["require_match", "allow_any"] | None = Field(None, description="SSL certificate validation mode: require_match to validate against server certificate, or allow_any to accept any certificate."),
    server_host_key: str | None = Field(None, description="SSH host key in OpenSSH format (as would appear in ~/.ssh/known_hosts). If provided, the server host key must match exactly."),
    server_type: Literal["ftp", "sftp", "s3", "google_cloud_storage", "webdav", "wasabi", "backblaze_b2", "one_drive", "rackspace", "box", "dropbox", "google_drive", "azure", "sharepoint", "s3_compatible", "azure_files", "files_agent", "filebase"] | None = Field(None, description="Type of remote server connection."),
    ssl: Literal["if_available", "require", "require_implicit", "never"] | None = Field(None, description="SSL/TLS requirement for the connection: if_available to use when supported, require to mandate SSL, require_implicit for implicit SSL, or never to disable."),
    ssl_certificate: str | None = Field(None, description="SSL client certificate for mutual TLS authentication."),
    aws: _models.PatchRemoteServersIdBodyAws | None = Field(None, description="AWS S3 connection settings (access key, secret key)"),
    azure_blob_storage: _models.PatchRemoteServersIdBodyAzureBlobStorage | None = Field(None, description="Azure Blob Storage connection settings"),
    azure_files_storage: _models.PatchRemoteServersIdBodyAzureFilesStorage | None = Field(None, description="Azure File Storage connection settings"),
    backblaze_b2: _models.PatchRemoteServersIdBodyBackblazeB2 | None = Field(None, description="Backblaze B2 connection settings"),
    filebase: _models.PatchRemoteServersIdBodyFilebase | None = Field(None, description="Filebase connection settings"),
    google_cloud_storage: _models.PatchRemoteServersIdBodyGoogleCloudStorage | None = Field(None, description="Google Cloud Storage connection settings"),
    rackspace: _models.PatchRemoteServersIdBodyRackspace | None = Field(None, description="Rackspace Cloud Files connection settings"),
    s3_compatible: _models.PatchRemoteServersIdBodyS3Compatible | None = Field(None, description="S3-compatible storage connection settings"),
    wasabi: _models.PatchRemoteServersIdBodyWasabi | None = Field(None, description="Wasabi storage connection settings"),
) -> dict[str, Any] | ToolResult:
    """Update configuration for a remote server connection. Modify authentication credentials, connection settings, storage bucket details, and security parameters for cloud storage providers (S3, Azure, Google Cloud, etc.) or traditional servers (FTP, SFTP, WebDAV)."""

    _id_ = _parse_int(id_)
    _max_connections = _parse_int(max_connections)
    _port = _parse_int(port)

    # Construct request model with validation
    try:
        _request = _models.PatchRemoteServersIdRequest(
            path=_models.PatchRemoteServersIdRequestPath(id_=_id_),
            body=_models.PatchRemoteServersIdRequestBody(enable_dedicated_ips=enable_dedicated_ips, files_agent_permission_set=files_agent_permission_set, files_agent_root=files_agent_root, hostname=hostname, max_connections=_max_connections, name=name, one_drive_account_type=one_drive_account_type, pin_to_site_region=pin_to_site_region, port=_port, private_key=private_key, private_key_passphrase=private_key_passphrase, s3_bucket=s3_bucket, s3_region=s3_region, server_certificate=server_certificate, server_host_key=server_host_key, server_type=server_type, ssl=ssl, ssl_certificate=ssl_certificate, aws=aws, azure_blob_storage=azure_blob_storage, azure_files_storage=azure_files_storage, backblaze_b2=backblaze_b2, filebase=filebase, google_cloud_storage=google_cloud_storage, rackspace=rackspace, s3_compatible=s3_compatible, wasabi=wasabi)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_remote_server: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/remote_servers/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/remote_servers/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_remote_server")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_remote_server", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_remote_server",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: remote_servers
@mcp.tool()
async def delete_remote_server(id_: str = Field(..., alias="id", description="The unique identifier of the remote server to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a remote server by its ID. This action cannot be undone."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteRemoteServersIdRequest(
            path=_models.DeleteRemoteServersIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_remote_server: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/remote_servers/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/remote_servers/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_remote_server")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_remote_server", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_remote_server",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: remote_servers
@mcp.tool()
async def download_remote_server_configuration(id_: str = Field(..., alias="id", description="The unique identifier of the Remote Server for which to download the configuration file.")) -> dict[str, Any] | ToolResult:
    """Download the configuration file for a Remote Server. This file is required for integrating certain Remote Server types, such as the Files.com Agent."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetRemoteServersIdConfigurationFileRequest(
            path=_models.GetRemoteServersIdConfigurationFileRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for download_remote_server_configuration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/remote_servers/{id}/configuration_file", _request.path.model_dump(by_alias=True)) if _request.path else "/remote_servers/{id}/configuration_file"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("download_remote_server_configuration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("download_remote_server_configuration", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="download_remote_server_configuration",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: remote_servers
@mcp.tool()
async def update_remote_server_configuration(
    id_: str = Field(..., alias="id", description="The unique identifier of the remote server to update."),
    config_version: str | None = Field(None, description="The version identifier of the agent configuration being submitted."),
    hostname: str | None = Field(None, description="The hostname or IP address of the remote server."),
    permission_set: str | None = Field(None, description="The permission level for the agent, controlling access scope."),
    port: str | None = Field(None, description="The network port on which the agent listens for incoming connections."),
    private_key: str | None = Field(None, description="The private key used for secure authentication and encryption."),
    public_key: str | None = Field(None, description="The public key corresponding to the private key for secure communication."),
    root: str | None = Field(None, description="The local filesystem root path where the agent operates and stores files."),
    server_host_key: str | None = Field(None, description="The server's host key used for SSH-based authentication and verification."),
    status: str | None = Field(None, description="The current operational state of the agent, either running or shutdown."),
    subdomain: str | None = Field(None, description="The subdomain identifier for the remote server configuration."),
) -> dict[str, Any] | ToolResult:
    """Submit local configuration changes, commit them, and retrieve the updated configuration file for a remote server. This operation is used by Remote Server integrations such as the Files.com Agent to synchronize agent configuration state."""

    _id_ = _parse_int(id_)
    _port = _parse_int(port)

    # Construct request model with validation
    try:
        _request = _models.PostRemoteServersIdConfigurationFileRequest(
            path=_models.PostRemoteServersIdConfigurationFileRequestPath(id_=_id_),
            body=_models.PostRemoteServersIdConfigurationFileRequestBody(config_version=config_version, hostname=hostname, permission_set=permission_set, port=_port, private_key=private_key, public_key=public_key, root=root, server_host_key=server_host_key, status=status, subdomain=subdomain)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_remote_server_configuration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/remote_servers/{id}/configuration_file", _request.path.model_dump(by_alias=True)) if _request.path else "/remote_servers/{id}/configuration_file"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_remote_server_configuration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_remote_server_configuration", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_remote_server_configuration",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: requests
@mcp.tool()
async def list_requests(
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Only the `destination` field is supported for sorting."),
    mine: bool | None = Field(None, description="Filter to show only requests belonging to the current user. Defaults to true for non-admin users."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of requests with optional filtering and sorting. By default, shows only the current user's requests unless the user is a site admin."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetRequestsRequest(
            query=_models.GetRequestsRequestQuery(per_page=_per_page, sort_by=sort_by, mine=mine)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/requests"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_requests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_requests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_requests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: requests
@mcp.tool()
async def request_file(
    destination: str = Field(..., description="The destination filename (without file extension) being requested."),
    path: str = Field(..., description="The folder path where the requested file is located."),
    user_ids: str | None = Field(None, description="List of user IDs to request the file from. Provide as comma-separated values when sent as a string."),
) -> dict[str, Any] | ToolResult:
    """Request a file from specified users by destination filename and folder path. Optionally target specific users; if no users are specified, the request is sent broadly."""

    # Construct request model with validation
    try:
        _request = _models.PostRequestsRequest(
            body=_models.PostRequestsRequestBody(destination=destination, path=path, user_ids=user_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for request_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/requests"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("request_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("request_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="request_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: requests
@mcp.tool()
async def list_requests_folder(
    path: str = Field(..., description="The folder path to filter requests. Use `/` to represent the root directory. Required parameter."),
    per_page: str | None = Field(None, description="Number of records to return per page. Maximum allowed is 10,000, though 1,000 or less is recommended for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Valid field is `destination`."),
    mine: bool | None = Field(None, description="Filter to show only requests created by the current user. Defaults to true for non-admin users."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of requests, optionally filtered by folder path and user ownership. Results can be paginated and sorted by destination."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetRequestsFoldersPathRequest(
            path=_models.GetRequestsFoldersPathRequestPath(path=path),
            query=_models.GetRequestsFoldersPathRequestQuery(per_page=_per_page, sort_by=sort_by, mine=mine)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_requests_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/requests/folders/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/requests/folders/{path}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_requests_folder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_requests_folder", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_requests_folder",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: requests
@mcp.tool()
async def delete_request(id_: str = Field(..., alias="id", description="The unique identifier of the request to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a specific request by its ID. This operation permanently removes the request from the system."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteRequestsIdRequest(
            path=_models.DeleteRequestsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/requests/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/requests/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_request", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_request",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: sftp_host_keys
@mcp.tool()
async def list_sftp_host_keys(per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of SFTP host keys. Use pagination to manage large result sets efficiently."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetSftpHostKeysRequest(
            query=_models.GetSftpHostKeysRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_sftp_host_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/sftp_host_keys"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sftp_host_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sftp_host_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sftp_host_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: sftp_host_keys
@mcp.tool()
async def create_sftp_host_key(
    name: str | None = Field(None, description="A user-friendly name to identify this SFTP host key for reference and management purposes."),
    private_key: str | None = Field(None, description="The private key data in PEM format used for SFTP host authentication. This should be the complete private key content."),
) -> dict[str, Any] | ToolResult:
    """Create a new SFTP host key for secure file transfer authentication. The host key consists of a friendly name and the associated private key data."""

    # Construct request model with validation
    try:
        _request = _models.PostSftpHostKeysRequest(
            body=_models.PostSftpHostKeysRequestBody(name=name, private_key=private_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_sftp_host_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/sftp_host_keys"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_sftp_host_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_sftp_host_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_sftp_host_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: sftp_host_keys
@mcp.tool()
async def get_sftp_host_key(id_: str = Field(..., alias="id", description="The unique identifier of the SFTP host key to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details for a specific SFTP host key by its ID. Use this to view the configuration and properties of an existing host key."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetSftpHostKeysIdRequest(
            path=_models.GetSftpHostKeysIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sftp_host_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sftp_host_keys/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sftp_host_keys/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sftp_host_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sftp_host_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sftp_host_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: sftp_host_keys
@mcp.tool()
async def update_sftp_host_key(
    id_: str = Field(..., alias="id", description="The unique identifier of the SFTP host key to update."),
    name: str | None = Field(None, description="A user-friendly name to identify this SFTP host key."),
    private_key: str | None = Field(None, description="The private key data in PEM format or other standard key format."),
) -> dict[str, Any] | ToolResult:
    """Update an SFTP host key's friendly name and/or private key data. Specify the host key ID and provide the fields you want to modify."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PatchSftpHostKeysIdRequest(
            path=_models.PatchSftpHostKeysIdRequestPath(id_=_id_),
            body=_models.PatchSftpHostKeysIdRequestBody(name=name, private_key=private_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sftp_host_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sftp_host_keys/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sftp_host_keys/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_sftp_host_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_sftp_host_key", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_sftp_host_key",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: sftp_host_keys
@mcp.tool()
async def delete_sftp_host_key(id_: str = Field(..., alias="id", description="The unique identifier of the SFTP host key to delete.")) -> dict[str, Any] | ToolResult:
    """Delete an SFTP host key by its ID. This operation permanently removes the specified host key from the system."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteSftpHostKeysIdRequest(
            path=_models.DeleteSftpHostKeysIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_sftp_host_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sftp_host_keys/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sftp_host_keys/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_sftp_host_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_sftp_host_key", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_sftp_host_key",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: site
@mcp.tool()
async def list_api_keys_site(
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Supports sorting by expiration date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of API keys for your site. Optionally sort and filter results to manage your API credentials."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetSiteApiKeysRequest(
            query=_models.GetSiteApiKeysRequestQuery(per_page=_per_page, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_api_keys_site: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/site/api_keys"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_api_keys_site")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_api_keys_site", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_api_keys_site",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: site
@mcp.tool()
async def create_api_key_site(
    description: str | None = Field(None, description="A user-supplied description to help identify the purpose or context of this API key."),
    expires_at: str | None = Field(None, description="The date and time when this API key will automatically expire and become invalid. Specified in ISO 8601 format."),
    name: str | None = Field(None, description="An internal name for this API key to help you identify and manage it."),
    permission_set: Literal["none", "full", "desktop_app", "sync_app", "office_integration", "mobile_app"] | None = Field(None, description="The permission level for this API key, controlling which operations it can perform. Desktop app keys are limited to file and share link operations, while full keys have unrestricted access."),
) -> dict[str, Any] | ToolResult:
    """Create a new API key for authenticating requests to the Files.com. Configure the key's name, expiration date, description, and permission level to control its access scope."""

    # Construct request model with validation
    try:
        _request = _models.PostSiteApiKeysRequest(
            body=_models.PostSiteApiKeysRequestBody(description=description, expires_at=expires_at, name=name, permission_set=permission_set)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_api_key_site: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/site/api_keys"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_api_key_site")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_api_key_site", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_api_key_site",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: site
@mcp.tool()
async def list_dns_records_site(per_page: str | None = Field(None, description="Number of DNS records to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 records can be retrieved in a single request.")) -> dict[str, Any] | ToolResult:
    """Retrieve the DNS records configured for a site. Results can be paginated to manage large record sets."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetSiteDnsRecordsRequest(
            query=_models.GetSiteDnsRecordsRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dns_records_site: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/site/dns_records"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dns_records_site")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dns_records_site", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dns_records_site",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: site
@mcp.tool()
async def list_site_ip_addresses(per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of IP addresses associated with the current site. Use the per_page parameter to control result set size."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetSiteIpAddressesRequest(
            query=_models.GetSiteIpAddressesRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_site_ip_addresses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/site/ip_addresses"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_site_ip_addresses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_site_ip_addresses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_site_ip_addresses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: site
@mcp.tool()
async def get_site_usage() -> dict[str, Any] | ToolResult:
    """Retrieve the most recent usage snapshot for a site, containing billing-related usage data. This provides a point-in-time view of resource consumption metrics."""

    # Extract parameters for API call
    _http_path = "/site/usage"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_site_usage")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_site_usage", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_site_usage",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: sso_strategies
@mcp.tool()
async def get_sso_strategy(id_: str = Field(..., alias="id", description="The unique identifier of the SSO strategy to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific SSO (Single Sign-On) strategy by its ID. Use this to view the configuration and details of an existing SSO strategy."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetSsoStrategiesIdRequest(
            path=_models.GetSsoStrategiesIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sso_strategy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sso_strategies/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/sso_strategies/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sso_strategy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sso_strategy", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sso_strategy",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: sso_strategies
@mcp.tool()
async def sync_sso_strategy(id_: str = Field(..., alias="id", description="The unique identifier of the SSO strategy to synchronize.")) -> dict[str, Any] | ToolResult:
    """Synchronize provisioning data between the local system and the remote SSO server for the specified strategy. This operation ensures user and group data are up-to-date across both systems."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PostSsoStrategiesIdSyncRequest(
            path=_models.PostSsoStrategiesIdSyncRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for sync_sso_strategy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/sso_strategies/{id}/sync", _request.path.model_dump(by_alias=True)) if _request.path else "/sso_strategies/{id}/sync"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("sync_sso_strategy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("sync_sso_strategy", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="sync_sso_strategy",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: styles
@mcp.tool()
async def update_style(
    path: str = Field(..., description="The path identifier for the style to update."),
    file_: str = Field(..., alias="file", description="Binary file containing the logo or branding assets for custom styling."),
) -> dict[str, Any] | ToolResult:
    """Update a style configuration by uploading a new branding file. Specify the style path and provide the binary file for custom branding."""

    # Construct request model with validation
    try:
        _request = _models.PatchStylesPathRequest(
            path=_models.PatchStylesPathRequestPath(path=path),
            body=_models.PatchStylesPathRequestBody(file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_style: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/styles/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/styles/{path}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_style")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_style", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_style",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: styles
@mcp.tool()
async def delete_style(path: str = Field(..., description="The path identifier of the style to delete. This uniquely identifies which style resource to remove.")) -> dict[str, Any] | ToolResult:
    """Delete a style by its path. This operation permanently removes the style from the system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteStylesPathRequest(
            path=_models.DeleteStylesPathRequestPath(path=path)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_style: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/styles/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/styles/{path}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_style")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_style", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_style",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: usage_daily_snapshots
@mcp.tool()
async def list_usage_snapshots_daily(
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000 records per page."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Supported fields are `date` and `usage_snapshot_id`. Specify as an object with field name as key and sort direction as value."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of daily usage snapshots. Results can be sorted by date or snapshot ID to track usage patterns over time."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetUsageDailySnapshotsRequest(
            query=_models.GetUsageDailySnapshotsRequestQuery(per_page=_per_page, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_usage_snapshots_daily: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/usage_daily_snapshots"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_usage_snapshots_daily")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_usage_snapshots_daily", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_usage_snapshots_daily",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: usage_snapshots
@mcp.tool()
async def list_usage_snapshots(per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of usage snapshots. Use the per_page parameter to control the number of records returned per page."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetUsageSnapshotsRequest(
            query=_models.GetUsageSnapshotsRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_usage_snapshots: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/usage_snapshots"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_usage_snapshots")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_usage_snapshots", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_usage_snapshots",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: user
@mcp.tool()
async def update_user(
    allowed_ips: str | None = Field(None, description="Comma-separated or newline-delimited list of IP addresses permitted to access this user account. Leave empty to allow all IPs."),
    announcements_read: bool | None = Field(None, description="Mark whether the user has acknowledged all announcements displayed in the UI."),
    authenticate_until: str | None = Field(None, description="Scheduled date and time when this user account will be automatically deactivated."),
    authentication_method: Literal["password", "unused_former_ldap", "sso", "none", "email_signup", "password_with_imported_hash"] | None = Field(None, description="Authentication method used for this user account."),
    billing_permission: bool | None = Field(None, description="Grant this user permission to manage account settings, process payments, and view invoices."),
    bypass_inactive_disable: bool | None = Field(None, description="Prevent this user from being automatically disabled due to inactivity, overriding site-wide settings."),
    bypass_site_allowed_ips: bool | None = Field(None, description="Allow this user to bypass site-wide IP address restrictions and blacklists."),
    company: str | None = Field(None, description="User's organization or company name."),
    dav_permission: bool | None = Field(None, description="Enable or disable WebDAV protocol access for this user."),
    disabled: bool | None = Field(None, description="Disable or enable the user account. Disabled users cannot log in and do not consume billing seats. Users may be automatically disabled after prolonged inactivity based on site configuration."),
    email: str | None = Field(None, description="User's email address."),
    ftp_permission: bool | None = Field(None, description="Enable or disable FTP and FTPS protocol access for this user."),
    grant_permission: str | None = Field(None, description="Permission level to grant on the user's root folder. Options include full access, read-only, write, list directory contents, or history access."),
    header_text: str | None = Field(None, description="Custom message text displayed to this user in the UI header."),
    language: str | None = Field(None, description="User's preferred language for the UI."),
    name: str | None = Field(None, description="User's full name."),
    notes: str | None = Field(None, description="Internal notes or comments about this user for administrative reference."),
    notification_daily_send_time: str | None = Field(None, description="Hour of the day (0-23) when daily notifications should be sent to this user."),
    office_integration_enabled: bool | None = Field(None, description="Enable integration with Microsoft Office for the web applications."),
    password_validity_days: str | None = Field(None, description="Number of days a user can use the same password before being required to change it."),
    receive_admin_alerts: bool | None = Field(None, description="Enable or disable receipt of administrative alerts such as certificate expiration warnings and account overages."),
    require_2fa: Literal["use_system_setting", "always_require", "never_require"] | None = Field(None, description="Two-factor authentication requirement setting for this user."),
    require_password_change: bool | None = Field(None, description="Require this user to change their password on the next login."),
    restapi_permission: bool | None = Field(None, description="Enable or disable REST API access for this user."),
    self_managed: bool | None = Field(None, description="Indicate whether this user manages their own credentials or is a shared/bot account with managed credentials."),
    sftp_permission: bool | None = Field(None, description="Enable or disable SFTP protocol access for this user."),
    site_admin: bool | None = Field(None, description="Grant or revoke site administrator privileges for this user."),
    skip_welcome_screen: bool | None = Field(None, description="Skip the welcome screen when this user first logs into the UI."),
    ssl_required: Literal["use_system_setting", "always_require", "never_require"] | None = Field(None, description="SSL/TLS encryption requirement setting for this user's connections."),
    sso_strategy_id: str | None = Field(None, description="SSO (Single Sign On) strategy ID associated with this user for federated authentication."),
    subscribe_to_newsletter: bool | None = Field(None, description="Subscribe or unsubscribe this user from the newsletter."),
    time_zone: str | None = Field(None, description="User's time zone for scheduling and time-based operations."),
    user_root: str | None = Field(None, description="Root folder path for FTP access and optionally SFTP if configured site-wide. Not used for API, desktop, or web interface access."),
) -> dict[str, Any] | ToolResult:
    """Update user account settings, permissions, and authentication configuration. Allows modification of user profile, access controls, security settings, and notification preferences."""

    _notification_daily_send_time = _parse_int(notification_daily_send_time)
    _password_validity_days = _parse_int(password_validity_days)
    _sso_strategy_id = _parse_int(sso_strategy_id)

    # Construct request model with validation
    try:
        _request = _models.PatchUserRequest(
            body=_models.PatchUserRequestBody(allowed_ips=allowed_ips, announcements_read=announcements_read, authenticate_until=authenticate_until, authentication_method=authentication_method, billing_permission=billing_permission, bypass_inactive_disable=bypass_inactive_disable, bypass_site_allowed_ips=bypass_site_allowed_ips, company=company, dav_permission=dav_permission, disabled=disabled, email=email, ftp_permission=ftp_permission, grant_permission=grant_permission, header_text=header_text, language=language, name=name, notes=notes, notification_daily_send_time=_notification_daily_send_time, office_integration_enabled=office_integration_enabled, password_validity_days=_password_validity_days, receive_admin_alerts=receive_admin_alerts, require_2fa=require_2fa, require_password_change=require_password_change, restapi_permission=restapi_permission, self_managed=self_managed, sftp_permission=sftp_permission, site_admin=site_admin, skip_welcome_screen=skip_welcome_screen, ssl_required=ssl_required, sso_strategy_id=_sso_strategy_id, subscribe_to_newsletter=subscribe_to_newsletter, time_zone=time_zone, user_root=user_root)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: user
@mcp.tool()
async def list_api_keys_current_user(
    per_page: str | None = Field(None, description="Number of API keys to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Supports sorting by expiration date (e.g., sort_by[expires_at]=desc)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of API keys for the authenticated user. Supports sorting by expiration date and customizable page size."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetUserApiKeysRequest(
            query=_models.GetUserApiKeysRequestQuery(per_page=_per_page, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_api_keys_current_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user/api_keys"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_api_keys_current_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_api_keys_current_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_api_keys_current_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: user
@mcp.tool()
async def create_api_key_user(
    description: str | None = Field(None, description="Optional user-supplied description to help identify the purpose or context of this API key."),
    expires_at: str | None = Field(None, description="Optional expiration date and time for this API key in ISO 8601 format. After this date, the key will no longer be valid for authentication."),
    name: str | None = Field(None, description="Optional internal name for this API key to help you identify and manage it."),
    permission_set: Literal["none", "full", "desktop_app", "sync_app", "office_integration", "mobile_app"] | None = Field(None, description="Permission level for this API key. Controls which operations and resources the key can access. Desktop app keys are limited to file and share link operations, while full keys have unrestricted access."),
) -> dict[str, Any] | ToolResult:
    """Create a new API key for programmatic access to your account. Configure the key's name, permissions, expiration date, and optional description."""

    # Construct request model with validation
    try:
        _request = _models.PostUserApiKeysRequest(
            body=_models.PostUserApiKeysRequestBody(description=description, expires_at=expires_at, name=name, permission_set=permission_set)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_api_key_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user/api_keys"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_api_key_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_api_key_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_api_key_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: user
@mcp.tool()
async def list_user_groups(per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, though the API supports up to 10,000 records per page.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of users belonging to groups. Use the per_page parameter to control result set size for optimal performance."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetUserGroupsRequest(
            query=_models.GetUserGroupsRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user/groups"
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

# Tags: user
@mcp.tool()
async def list_public_keys_current_user(per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, though the API supports up to 10,000 records per page.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of public keys associated with the user account. Use the per_page parameter to control pagination size."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetUserPublicKeysRequest(
            query=_models.GetUserPublicKeysRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_public_keys_current_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user/public_keys"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_public_keys_current_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_public_keys_current_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_public_keys_current_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: user
@mcp.tool()
async def add_public_key(
    public_key: str = Field(..., description="The complete SSH public key content (typically starts with 'ssh-rsa', 'ssh-ed25519', or similar algorithm identifier)."),
    title: str = Field(..., description="A descriptive label to identify this key within your account."),
) -> dict[str, Any] | ToolResult:
    """Add a new SSH public key to your account for authentication purposes. Each key requires a descriptive title for easy identification."""

    # Construct request model with validation
    try:
        _request = _models.PostUserPublicKeysRequest(
            body=_models.PostUserPublicKeysRequestBody(public_key=public_key, title=title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_public_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user/public_keys"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_public_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_public_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_public_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: user_cipher_uses
@mcp.tool()
async def list_cipher_uses(per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 is supported.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of cipher uses associated with the authenticated user. Use the per_page parameter to control result set size."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetUserCipherUsesRequest(
            query=_models.GetUserCipherUsesRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_cipher_uses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user_cipher_uses"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_cipher_uses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_cipher_uses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_cipher_uses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: user_requests
@mcp.tool()
async def list_requests_user(per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of user requests. Use the per_page parameter to control result set size for optimal performance."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetUserRequestsRequest(
            query=_models.GetUserRequestsRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_requests_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user_requests"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_requests_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_requests_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_requests_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: user_requests
@mcp.tool()
async def create_user_request(
    details: str = Field(..., description="Detailed description or content of the user request, providing context about what is being requested."),
    email: str = Field(..., description="Email address of the user associated with this request. Used for identification and communication purposes."),
    name: str = Field(..., description="Full name of the user associated with this request."),
) -> dict[str, Any] | ToolResult:
    """Create a new user request with details about a specific user. This operation registers a request associated with the provided user's email and name."""

    # Construct request model with validation
    try:
        _request = _models.PostUserRequestsRequest(
            body=_models.PostUserRequestsRequestBody(details=details, email=email, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_user_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user_requests"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_user_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_user_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_user_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: user_requests
@mcp.tool()
async def get_user_request(id_: str = Field(..., alias="id", description="The unique identifier of the user request to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details for a specific user request by its ID. Returns the complete request information including status, content, and metadata."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetUserRequestsIdRequest(
            path=_models.GetUserRequestsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user_requests/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/user_requests/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_request", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_request",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: user_requests
@mcp.tool()
async def delete_user_request(id_: str = Field(..., alias="id", description="The unique identifier of the user request to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a specific user request by its ID. This operation permanently removes the user request from the system."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteUserRequestsIdRequest(
            path=_models.DeleteUserRequestsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user_requests/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/user_requests/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_user_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_user_request", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_user_request",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_users(
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance."),
    ids: str | None = Field(None, description="Filter results by one or more user IDs using comma-separated values."),
    q_username: str | None = Field(None, alias="qusername", description="Filter results to users whose username matches the provided value."),
    q_email: str | None = Field(None, alias="qemail", description="Filter results to users whose email address matches the provided value."),
    q_notes: str | None = Field(None, alias="qnotes", description="Filter results to users whose notes field matches the provided value."),
    q_admin: str | None = Field(None, alias="qadmin", description="Filter results to include only administrative users when set to true."),
    q_allowed_ips: str | None = Field(None, alias="qallowed_ips", description="Filter results to include only users with custom allowed IP address restrictions configured."),
    q_password_validity_days: str | None = Field(None, alias="qpassword_validity_days", description="Filter results to include only users with custom password validity days settings configured."),
    q_ssl_required: str | None = Field(None, alias="qssl_required", description="Filter results to include only users with custom SSL requirement settings configured."),
    sort_field: str | None = Field(None, description="Field to sort by. Valid values: 'path', 'folder', 'user_id', 'created_at'"),
    sort_direction: str | None = Field(None, description="Sort direction. Valid values: 'asc' or 'desc'"),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of users with optional filtering by ID, username, email, notes, or administrative and security settings."""

    # Call helper functions
    sort_by = build_sort_by(sort_field, sort_direction)

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetUsersRequest(
            query=_models.GetUsersRequestQuery(per_page=_per_page, ids=ids, q_username=q_username, q_email=q_email, q_notes=q_notes, q_admin=q_admin, q_allowed_ips=q_allowed_ips, q_password_validity_days=q_password_validity_days, q_ssl_required=q_ssl_required, sort_by=sort_by)
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

# Tags: users
@mcp.tool()
async def create_user(
    allowed_ips: str | None = Field(None, description="Comma-separated or newline-delimited list of IP addresses permitted to access this user account. Leave empty to allow all IPs."),
    announcements_read: bool | None = Field(None, description="Indicates whether the user has acknowledged all announcements displayed in the UI."),
    authenticate_until: str | None = Field(None, description="Date and time after which the user account will be automatically deactivated. Useful for temporary or contract-based access."),
    authentication_method: Literal["password", "unused_former_ldap", "sso", "none", "email_signup", "password_with_imported_hash"] | None = Field(None, description="Authentication mechanism used for this user. Determines how credentials are validated and managed."),
    billing_permission: bool | None = Field(None, description="Grant permission to manage account operations, payments, and invoices. Restricted to trusted users only."),
    bypass_inactive_disable: bool | None = Field(None, description="Prevent this user from being automatically disabled due to inactivity, overriding site-wide inactivity policies."),
    bypass_site_allowed_ips: bool | None = Field(None, description="Allow this user to bypass site-wide IP address blacklists and restrictions."),
    company: str | None = Field(None, description="User's organization or company name for identification and organizational purposes."),
    dav_permission: bool | None = Field(None, description="Enable WebDAV protocol access for this user."),
    disabled: bool | None = Field(None, description="Disable user account. Disabled users cannot log in and do not consume billing seats. Can be automatically applied after inactivity."),
    email: str | None = Field(None, description="User's email address used for login, notifications, and account recovery."),
    ftp_permission: bool | None = Field(None, description="Enable FTP/FTPS protocol access for this user."),
    grant_permission: str | None = Field(None, description="Default permission level for the user's root folder. Options include full access, read-only, write, list, or history viewing."),
    header_text: str | None = Field(None, description="Custom message displayed in the UI header for this user. Useful for notifications or instructions."),
    language: str | None = Field(None, description="User's preferred language for the UI interface."),
    name: str | None = Field(None, description="User's full name for display and identification purposes."),
    notes: str | None = Field(None, description="Internal notes or comments about the user for administrative reference. Not visible to the user."),
    notification_daily_send_time: str | None = Field(None, description="Hour of day (0-23) when daily notification digests should be sent to this user."),
    office_integration_enabled: bool | None = Field(None, description="Enable integration with Microsoft Office for the web applications."),
    password_validity_days: str | None = Field(None, description="Number of days before the user must change their password. Enforces periodic password rotation."),
    receive_admin_alerts: bool | None = Field(None, description="Send administrative alerts to this user, including certificate expiration warnings and account overages."),
    require_2fa: Literal["use_system_setting", "always_require", "never_require"] | None = Field(None, description="Two-factor authentication requirement for this user. Can override system-wide settings."),
    require_password_change: bool | None = Field(None, description="Require the user to change their password on the next login attempt."),
    restapi_permission: bool | None = Field(None, description="Enable REST API access for this user."),
    self_managed: bool | None = Field(None, description="Indicate whether the user manages their own credentials or is a shared/bot account with managed credentials."),
    sftp_permission: bool | None = Field(None, description="Enable SFTP protocol access for this user."),
    site_admin: bool | None = Field(None, description="Grant site administrator privileges to this user, allowing management of other users and system settings."),
    skip_welcome_screen: bool | None = Field(None, description="Skip the welcome/onboarding screen on first login to the UI."),
    ssl_required: Literal["use_system_setting", "always_require", "never_require"] | None = Field(None, description="SSL/TLS encryption requirement for this user's connections. Can override system-wide settings."),
    sso_strategy_id: str | None = Field(None, description="ID of the SSO (Single Sign On) strategy to use for this user's authentication."),
    subscribe_to_newsletter: bool | None = Field(None, description="Subscribe this user to the system newsletter for updates and announcements."),
    time_zone: str | None = Field(None, description="User's time zone for scheduling notifications and displaying timestamps in the UI."),
    user_root: str | None = Field(None, description="Root folder path for FTP access and optionally SFTP (if configured site-wide). Does not apply to API, desktop, or web interface access."),
    username: str | None = Field(None, description="User's username"),
) -> dict[str, Any] | ToolResult:
    """Create a new user account with configurable authentication, permissions, and security settings. Supports multiple authentication methods and granular access control across protocols (FTP, SFTP, WebDAV, REST API)."""

    _notification_daily_send_time = _parse_int(notification_daily_send_time)
    _password_validity_days = _parse_int(password_validity_days)
    _sso_strategy_id = _parse_int(sso_strategy_id)

    # Construct request model with validation
    try:
        _request = _models.PostUsersRequest(
            body=_models.PostUsersRequestBody(allowed_ips=allowed_ips, announcements_read=announcements_read, authenticate_until=authenticate_until, authentication_method=authentication_method, billing_permission=billing_permission, bypass_inactive_disable=bypass_inactive_disable, bypass_site_allowed_ips=bypass_site_allowed_ips, company=company, dav_permission=dav_permission, disabled=disabled, email=email, ftp_permission=ftp_permission, grant_permission=grant_permission, header_text=header_text, language=language, name=name, notes=notes, notification_daily_send_time=_notification_daily_send_time, office_integration_enabled=office_integration_enabled, password_validity_days=_password_validity_days, receive_admin_alerts=receive_admin_alerts, require_2fa=require_2fa, require_password_change=require_password_change, restapi_permission=restapi_permission, self_managed=self_managed, sftp_permission=sftp_permission, site_admin=site_admin, skip_welcome_screen=skip_welcome_screen, ssl_required=ssl_required, sso_strategy_id=_sso_strategy_id, subscribe_to_newsletter=subscribe_to_newsletter, time_zone=time_zone, user_root=user_root, username=username)
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
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_user(id_: str = Field(..., alias="id", description="The unique identifier of the user to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information for a specific user by their ID."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetUsersIdRequest(
            path=_models.GetUsersIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{id}"
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

# Tags: users
@mcp.tool()
async def update_user_account(
    id_: str = Field(..., alias="id", description="The unique identifier of the user to update."),
    allowed_ips: str | None = Field(None, description="Comma-separated or newline-delimited list of IP addresses permitted to access this user account."),
    announcements_read: bool | None = Field(None, description="Whether the user has read all announcements displayed in the UI."),
    authenticate_until: str | None = Field(None, description="Date and time when the user account will be automatically deactivated."),
    authentication_method: Literal["password", "unused_former_ldap", "sso", "none", "email_signup", "password_with_imported_hash"] | None = Field(None, description="The authentication method used for this user account."),
    billing_permission: bool | None = Field(None, description="Whether the user can perform operations on account settings, payments, and invoices."),
    bypass_inactive_disable: bool | None = Field(None, description="Whether the user is exempt from automatic deactivation due to inactivity."),
    bypass_site_allowed_ips: bool | None = Field(None, description="Whether the user can bypass site-wide IP blacklist restrictions."),
    company: str | None = Field(None, description="The user's company or organization name."),
    dav_permission: bool | None = Field(None, description="Whether the user can connect and access files via WebDAV protocol."),
    disabled: bool | None = Field(None, description="Whether the user account is disabled. Disabled users cannot log in and do not count toward billing. Users may be automatically disabled after an inactivity period based on site settings."),
    email: str | None = Field(None, description="The user's email address."),
    ftp_permission: bool | None = Field(None, description="Whether the user can access files and accounts via FTP or FTPS protocols."),
    grant_permission: str | None = Field(None, description="Permission level to grant on the user's root folder. Options include full access, read-only, write, list, or history access."),
    header_text: str | None = Field(None, description="Custom text message displayed to the user in the UI header for notifications or announcements."),
    language: str | None = Field(None, description="The user's preferred language for the UI."),
    name: str | None = Field(None, description="The user's full name."),
    notes: str | None = Field(None, description="Internal notes or comments about the user for administrative reference."),
    notification_daily_send_time: str | None = Field(None, description="The hour of the day (0-23) when daily notifications should be sent to the user."),
    office_integration_enabled: bool | None = Field(None, description="Whether to enable integration with Microsoft Office for the web applications."),
    password_validity_days: str | None = Field(None, description="Number of days a user can use the same password before being required to change it."),
    receive_admin_alerts: bool | None = Field(None, description="Whether the user receives administrative alerts such as certificate expiration warnings and account overages."),
    require_2fa: Literal["use_system_setting", "always_require", "never_require"] | None = Field(None, description="Two-factor authentication requirement setting for this user."),
    require_password_change: bool | None = Field(None, description="Whether the user must change their password on the next login."),
    restapi_permission: bool | None = Field(None, description="Whether the user can access and use the REST API."),
    self_managed: bool | None = Field(None, description="Whether the user manages their own credentials or is a shared/bot account with managed credentials."),
    sftp_permission: bool | None = Field(None, description="Whether the user can access files and accounts via SFTP protocol."),
    site_admin: bool | None = Field(None, description="Whether the user has administrator privileges for this site."),
    skip_welcome_screen: bool | None = Field(None, description="Whether to skip the welcome screen when the user first logs into the UI."),
    ssl_required: Literal["use_system_setting", "always_require", "never_require"] | None = Field(None, description="SSL/TLS encryption requirement setting for this user's connections."),
    sso_strategy_id: str | None = Field(None, description="The ID of the SSO (Single Sign On) strategy assigned to this user, if applicable."),
    subscribe_to_newsletter: bool | None = Field(None, description="Whether the user is subscribed to receive newsletter communications."),
    time_zone: str | None = Field(None, description="The user's time zone for scheduling and time-based operations."),
    user_root: str | None = Field(None, description="Root folder path for FTP access and optionally SFTP if configured at the site level. Not used for API, desktop, or web interface access."),
) -> dict[str, Any] | ToolResult:
    """Update user account settings, permissions, and authentication configuration. Allows modification of user profile, access controls, security settings, and notification preferences."""

    _id_ = _parse_int(id_)
    _notification_daily_send_time = _parse_int(notification_daily_send_time)
    _password_validity_days = _parse_int(password_validity_days)
    _sso_strategy_id = _parse_int(sso_strategy_id)

    # Construct request model with validation
    try:
        _request = _models.PatchUsersIdRequest(
            path=_models.PatchUsersIdRequestPath(id_=_id_),
            body=_models.PatchUsersIdRequestBody(allowed_ips=allowed_ips, announcements_read=announcements_read, authenticate_until=authenticate_until, authentication_method=authentication_method, billing_permission=billing_permission, bypass_inactive_disable=bypass_inactive_disable, bypass_site_allowed_ips=bypass_site_allowed_ips, company=company, dav_permission=dav_permission, disabled=disabled, email=email, ftp_permission=ftp_permission, grant_permission=grant_permission, header_text=header_text, language=language, name=name, notes=notes, notification_daily_send_time=_notification_daily_send_time, office_integration_enabled=office_integration_enabled, password_validity_days=_password_validity_days, receive_admin_alerts=receive_admin_alerts, require_2fa=require_2fa, require_password_change=require_password_change, restapi_permission=restapi_permission, self_managed=self_managed, sftp_permission=sftp_permission, site_admin=site_admin, skip_welcome_screen=skip_welcome_screen, ssl_required=ssl_required, sso_strategy_id=_sso_strategy_id, subscribe_to_newsletter=subscribe_to_newsletter, time_zone=time_zone, user_root=user_root)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user_account", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user_account",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def delete_user(id_: str = Field(..., alias="id", description="The unique identifier of the user to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a user account by ID. This action cannot be undone."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteUsersIdRequest(
            path=_models.DeleteUsersIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{id}"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def reset_user_2fa(id_: str = Field(..., alias="id", description="The unique identifier of the user whose 2FA needs to be reset.")) -> dict[str, Any] | ToolResult:
    """Initiate a two-factor authentication reset for a user who has lost access to their existing 2FA methods. This process allows the user to regain account access and reconfigure their authentication."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PostUsersId2faResetRequest(
            path=_models.PostUsersId2faResetRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reset_user_2fa: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{id}/2fa/reset", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{id}/2fa/reset"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reset_user_2fa")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reset_user_2fa", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reset_user_2fa",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def resend_welcome_email(id_: str = Field(..., alias="id", description="The unique identifier of the user who should receive the welcome email.")) -> dict[str, Any] | ToolResult:
    """Resend the welcome email to a user. This operation is useful when the initial welcome email was not received or needs to be sent again."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PostUsersIdResendWelcomeEmailRequest(
            path=_models.PostUsersIdResendWelcomeEmailRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for resend_welcome_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{id}/resend_welcome_email", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{id}/resend_welcome_email"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("resend_welcome_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("resend_welcome_email", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="resend_welcome_email",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def unlock_user(id_: str = Field(..., alias="id", description="The unique identifier of the user account to unlock.")) -> dict[str, Any] | ToolResult:
    """Unlock a user account that has been locked due to failed login attempts. This restores the user's ability to authenticate."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PostUsersIdUnlockRequest(
            path=_models.PostUsersIdUnlockRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unlock_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{id}/unlock", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{id}/unlock"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unlock_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unlock_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unlock_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_api_keys_for_user(
    user_id: str = Field(..., description="The user ID whose API keys to retrieve. Use `0` to operate on the current session's user."),
    per_page: str | None = Field(None, description="Number of records to return per page. Maximum 10,000; 1,000 or less is recommended."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort results by a specified field in ascending or descending order. Valid field: `expires_at`."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of API keys for a user. Use user_id `0` to list keys for the current session's user."""

    _user_id = _parse_int(user_id)
    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetUsersUserIdApiKeysRequest(
            path=_models.GetUsersUserIdApiKeysRequestPath(user_id=_user_id),
            query=_models.GetUsersUserIdApiKeysRequestQuery(per_page=_per_page, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_api_keys_for_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/api_keys", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/api_keys"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_api_keys_for_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_api_keys_for_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_api_keys_for_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def create_api_key_admin(
    user_id: str = Field(..., description="The user ID for which to create the API key. Use `0` to create a key for the current authenticated user."),
    description: str | None = Field(None, description="Optional user-supplied description to help identify the purpose or context of this API key."),
    expires_at: str | None = Field(None, description="Optional expiration date and time for the API key in ISO 8601 format. After this date, the key will no longer be valid."),
    name: str | None = Field(None, description="Optional internal name for the API key for your own reference and organization."),
    permission_set: Literal["none", "full", "desktop_app", "sync_app", "office_integration", "mobile_app"] | None = Field(None, description="Permission level for this API key. `full` grants all permissions, `desktop_app` restricts to file and share link operations, and other sets provide specialized access for specific applications."),
) -> dict[str, Any] | ToolResult:
    """Create a new API key for the specified user with configurable permissions and optional expiration. Use user_id `0` to create a key for the current session's user."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.PostUsersUserIdApiKeysRequest(
            path=_models.PostUsersUserIdApiKeysRequestPath(user_id=_user_id),
            body=_models.PostUsersUserIdApiKeysRequestBody(description=description, expires_at=expires_at, name=name, permission_set=permission_set)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_api_key_admin: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/api_keys", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/api_keys"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_api_key_admin")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_api_key_admin", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_api_key_admin",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_cipher_uses_by_user(
    user_id: str = Field(..., description="The unique identifier of the user whose cipher uses should be retrieved. Use 0 to refer to the current session's authenticated user."),
    per_page: str | None = Field(None, description="Number of cipher use records to return per page. Maximum allowed is 10,000, though 1,000 or fewer is recommended for optimal performance."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of cipher uses for a specific user. Use user_id value of 0 to retrieve cipher uses for the current authenticated session's user."""

    _user_id = _parse_int(user_id)
    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetUsersUserIdCipherUsesRequest(
            path=_models.GetUsersUserIdCipherUsesRequestPath(user_id=_user_id),
            query=_models.GetUsersUserIdCipherUsesRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_cipher_uses_by_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/cipher_uses", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/cipher_uses"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_cipher_uses_by_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_cipher_uses_by_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_cipher_uses_by_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_user_groups_2(
    user_id: str = Field(..., description="The unique identifier of the user whose group memberships should be retrieved."),
    per_page: str | None = Field(None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance; maximum allowed is 10,000."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all groups that a specific user belongs to. Supports pagination to handle large result sets."""

    _user_id = _parse_int(user_id)
    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetUsersUserIdGroupsRequest(
            path=_models.GetUsersUserIdGroupsRequestPath(user_id=_user_id),
            query=_models.GetUsersUserIdGroupsRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_groups_2: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/groups"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_groups_2")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_groups_2", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_groups_2",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_user_permissions(
    user_id: str = Field(..., description="The user ID to retrieve permissions for. Note: This parameter is deprecated; use the filter[user_id] query parameter instead for new implementations."),
    per_page: str | None = Field(None, description="Number of permission records to return per page. Recommended to use 1,000 or less for optimal performance."),
    sort_by: dict[str, Any] | None = Field(None, description="Sort the results by a specified field in ascending or descending order. Valid sortable fields are group_id, path, user_id, or permission."),
    include_groups: bool | None = Field(None, description="When enabled, includes permissions inherited from the user's group memberships in addition to directly assigned permissions."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of permissions for a specific user, with optional filtering by group inheritance and sorting capabilities."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetUsersUserIdPermissionsRequest(
            path=_models.GetUsersUserIdPermissionsRequestPath(user_id=user_id),
            query=_models.GetUsersUserIdPermissionsRequestQuery(per_page=_per_page, sort_by=sort_by, include_groups=include_groups)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/permissions", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/permissions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_permissions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_permissions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_public_keys_by_user(
    user_id: str = Field(..., description="The unique identifier of the user whose public keys should be retrieved. Use `0` to refer to the current authenticated user."),
    per_page: str | None = Field(None, description="Number of public keys to return per page. Recommended to use 1,000 or less for optimal performance."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of public keys for a specified user. Use user ID `0` to retrieve keys for the current authenticated session."""

    _user_id = _parse_int(user_id)
    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetUsersUserIdPublicKeysRequest(
            path=_models.GetUsersUserIdPublicKeysRequestPath(user_id=_user_id),
            query=_models.GetUsersUserIdPublicKeysRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_public_keys_by_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/public_keys", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/public_keys"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_public_keys_by_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_public_keys_by_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_public_keys_by_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def create_public_key_for_user(
    user_id: str = Field(..., description="The ID of the user to create the public key for. Use 0 to create a key for the current session's authenticated user."),
    public_key: str = Field(..., description="The complete SSH public key content (typically starting with ssh-rsa, ssh-ed25519, or similar)."),
    title: str = Field(..., description="A descriptive label for this public key to help identify it among multiple keys."),
) -> dict[str, Any] | ToolResult:
    """Create a new SSH public key for a user account. The key can be associated with the current session's user by providing a user_id of 0."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.PostUsersUserIdPublicKeysRequest(
            path=_models.PostUsersUserIdPublicKeysRequestPath(user_id=_user_id),
            body=_models.PostUsersUserIdPublicKeysRequestBody(public_key=public_key, title=title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_public_key_for_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/public_keys", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/public_keys"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_public_key_for_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_public_key_for_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_public_key_for_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: webhook_tests
@mcp.tool()
async def test_webhook(
    url: str = Field(..., description="The webhook URL endpoint to test. Must be a valid HTTP or HTTPS URL."),
    action: str | None = Field(None, description="Action identifier to include in the test request body."),
    encoding: str | None = Field(None, description="HTTP encoding format for the request body: JSON, XML, or RAW (form data)."),
    file_as_body: bool | None = Field(None, description="Whether to send file data as the raw request body instead of as a form field."),
    file_form_field: str | None = Field(None, description="Form field name to use when sending file data as a named parameter in the POST body."),
    headers: dict[str, Any] | None = Field(None, description="Custom HTTP headers to include in the test request as key-value pairs."),
    method: str | None = Field(None, description="HTTP method for the test request: GET or POST."),
) -> dict[str, Any] | ToolResult:
    """Execute a test request to a webhook URL to validate connectivity and configuration. Supports custom headers, multiple encoding formats, and optional file payload."""

    # Construct request model with validation
    try:
        _request = _models.PostWebhookTestsRequest(
            body=_models.PostWebhookTestsRequestBody(action=action, encoding=encoding, file_as_body=file_as_body, file_form_field=file_form_field, headers=headers, method=method, url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for test_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/webhook_tests"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("test_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("test_webhook", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="test_webhook",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
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
        print("  python files_com_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Files.com MCP Server")

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
    logger.info("Starting Files.com MCP Server")
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

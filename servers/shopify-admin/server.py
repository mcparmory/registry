#!/usr/bin/env python3
"""
Shopify Admin API MCP Server
Generated: 2026-05-05 16:21:14 UTC
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

# Server variables (from OpenAPI spec, overridable via SERVER_* env vars)
_SERVER_VARS = {
    "store_name": os.getenv("SERVER_STORE_NAME", ""),
}
BASE_URL = os.getenv("BASE_URL", "https://{store_name}.myshopify.com/admin/api/2024-01".format_map(collections.defaultdict(str, _SERVER_VARS)))
SERVER_NAME = "Shopify Admin API"
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
    'OAuth2Auth',
    'CustomAppAccessToken',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["OAuth2Auth"] = _auth.OAuth2Auth()
    logging.info("Authentication configured: OAuth2Auth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for OAuth2Auth not configured: {error_msg}")
    _auth_handlers["OAuth2Auth"] = None
try:
    _auth_handlers["CustomAppAccessToken"] = _auth.APIKeyAuth(env_var="API_KEY", location="header", param_name="X-Shopify-Access-Token")
    logging.info("Authentication configured: CustomAppAccessToken")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for CustomAppAccessToken not configured: {error_msg}")
    _auth_handlers["CustomAppAccessToken"] = None

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

mcp = FastMCP("Shopify Admin API", middleware=[_JsonCoercionMiddleware()])

# Tags: billing, applicationcharge, billing/applicationcharge, latest_api_version
@mcp.tool()
async def list_application_charges(
    since_id: Any | None = Field(None, description="Restrict results to charges after the specified ID. Use this for cursor-based pagination to fetch subsequent pages of results."),
    fields: Any | None = Field(None, description="A comma-separated list of specific fields to include in the response. Omit to receive all available fields for each charge."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of application charges for the store. Use this to view all charges or filter results by cursor position."""

    # Construct request model with validation
    try:
        _request = _models.GetApplicationChargesRequest(
            query=_models.GetApplicationChargesRequestQuery(since_id=since_id, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_application_charges: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/application_charges.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_application_charges")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_application_charges", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_application_charges",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: billing, applicationcharge, billing/applicationcharge, latest_api_version
@mcp.tool()
async def get_application_charge(
    application_charge_id: str = Field(..., description="The unique identifier of the application charge to retrieve."),
    fields: Any | None = Field(None, description="A comma-separated list of specific fields to include in the response. If omitted, all fields are returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific application charge by its ID, including status, price, and billing information."""

    # Construct request model with validation
    try:
        _request = _models.GetApplicationChargesParamApplicationChargeIdRequest(
            path=_models.GetApplicationChargesParamApplicationChargeIdRequestPath(application_charge_id=application_charge_id),
            query=_models.GetApplicationChargesParamApplicationChargeIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_application_charge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/application_charges/{application_charge_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/application_charges/{application_charge_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_application_charge")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_application_charge", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_application_charge",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: billing, applicationcredit, billing/applicationcredit, latest_api_version
@mcp.tool()
async def list_application_credits(fields: Any | None = Field(None, description="A comma-separated list of field names to include in the response. Omit this parameter to return all available fields.")) -> dict[str, Any] | ToolResult:
    """Retrieves all application credits for the store. Use this to view credit transactions and their details."""

    # Construct request model with validation
    try:
        _request = _models.GetApplicationCreditsRequest(
            query=_models.GetApplicationCreditsRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_application_credits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/application_credits.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_application_credits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_application_credits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_application_credits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: billing, applicationcredit, billing/applicationcredit, latest_api_version
@mcp.tool()
async def get_application_credit(
    application_credit_id: str = Field(..., description="The unique identifier of the application credit to retrieve."),
    fields: Any | None = Field(None, description="A comma-separated list of specific fields to include in the response. Omit to return all available fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a single application credit by its ID. Use this to fetch information about a specific credit issued to an app."""

    # Construct request model with validation
    try:
        _request = _models.GetApplicationCreditsParamApplicationCreditIdRequest(
            path=_models.GetApplicationCreditsParamApplicationCreditIdRequestPath(application_credit_id=application_credit_id),
            query=_models.GetApplicationCreditsParamApplicationCreditIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_application_credit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/application_credits/{application_credit_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/application_credits/{application_credit_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_application_credit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_application_credit", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_application_credit",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, article, online-store/article, latest_api_version
@mcp.tool()
async def list_article_authors() -> dict[str, Any] | ToolResult:
    """Retrieves a list of all article authors available in the online store. Use this to discover which authors have contributed articles."""

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/articles/authors.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_article_authors")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_article_authors", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_article_authors",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, article, online-store/article, latest_api_version
@mcp.tool()
async def list_article_tags(
    limit: Any | None = Field(None, description="Maximum number of tags to return in the response. Limits the size of the result set."),
    popular: Any | None = Field(None, description="When included, orders results by tag popularity in descending order (most popular first). Omit this parameter to retrieve tags in default order."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all tags used across articles in the online store. Results can be optionally ordered by popularity to surface the most frequently used tags."""

    # Construct request model with validation
    try:
        _request = _models.GetArticlesTagsRequest(
            query=_models.GetArticlesTagsRequestQuery(limit=limit, popular=popular)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_article_tags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/articles/tags.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_article_tags")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_article_tags", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_article_tags",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, article, online-store/article, latest_api_version
@mcp.tool()
async def list_blog_articles(
    blog_id: str = Field(..., description="The unique identifier of the blog from which to retrieve articles."),
    limit: Any | None = Field(None, description="Maximum number of articles to return per request, between 1 and 250 (defaults to 50)."),
    since_id: Any | None = Field(None, description="Return only articles with an ID greater than this value, useful for pagination and filtering out previously retrieved results."),
    published_status: Any | None = Field(None, description="Filter articles by publication status: published (live articles only), unpublished (draft articles only), or any (all articles regardless of status). Defaults to any."),
    handle: Any | None = Field(None, description="Return only the article with this specific URL-friendly handle."),
    tag: Any | None = Field(None, description="Return only articles tagged with this specific tag."),
    author: Any | None = Field(None, description="Return only articles written by this specific author."),
    fields: Any | None = Field(None, description="Limit the response to only these fields, specified as a comma-separated list of field names. Reduces payload size when only certain article properties are needed."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of articles from a specific blog. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""

    # Construct request model with validation
    try:
        _request = _models.GetBlogsParamBlogIdArticlesRequest(
            path=_models.GetBlogsParamBlogIdArticlesRequestPath(blog_id=blog_id),
            query=_models.GetBlogsParamBlogIdArticlesRequestQuery(limit=limit, since_id=since_id, published_status=published_status, handle=handle, tag=tag, author=author, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_blog_articles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/blogs/{blog_id}/articles.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/blogs/{blog_id}/articles.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_blog_articles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_blog_articles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_blog_articles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, article, online-store/article, latest_api_version
@mcp.tool()
async def count_articles_in_blog(
    blog_id: str = Field(..., description="The unique identifier of the blog for which to count articles."),
    published_status: Any | None = Field(None, description="Filter articles by publication status: use 'published' to count only published articles, 'unpublished' to count only unpublished articles, or 'any' to count all articles regardless of status. Defaults to 'any' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the total count of articles in a specific blog, with optional filtering by publication status."""

    # Construct request model with validation
    try:
        _request = _models.GetBlogsParamBlogIdArticlesCountRequest(
            path=_models.GetBlogsParamBlogIdArticlesCountRequestPath(blog_id=blog_id),
            query=_models.GetBlogsParamBlogIdArticlesCountRequestQuery(published_status=published_status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for count_articles_in_blog: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/blogs/{blog_id}/articles/count.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/blogs/{blog_id}/articles/count.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("count_articles_in_blog")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("count_articles_in_blog", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="count_articles_in_blog",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, article, online-store/article, latest_api_version
@mcp.tool()
async def get_article(
    blog_id: str = Field(..., description="The unique identifier of the blog containing the article."),
    article_id: str = Field(..., description="The unique identifier of the article to retrieve."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. If omitted, all fields are returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single article from a blog by its ID. Returns the full article object unless specific fields are requested."""

    # Construct request model with validation
    try:
        _request = _models.GetBlogsParamBlogIdArticlesParamArticleIdRequest(
            path=_models.GetBlogsParamBlogIdArticlesParamArticleIdRequestPath(blog_id=blog_id, article_id=article_id),
            query=_models.GetBlogsParamBlogIdArticlesParamArticleIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_article: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/blogs/{blog_id}/articles/{article_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/blogs/{blog_id}/articles/{article_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_article")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_article", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_article",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, article, online-store/article, latest_api_version
@mcp.tool()
async def update_article(
    blog_id: str = Field(..., description="The unique identifier of the blog containing the article to update."),
    article_id: str = Field(..., description="The unique identifier of the article to update."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing article within a blog. Modify article content, metadata, and publishing settings by providing the blog and article identifiers."""

    # Construct request model with validation
    try:
        _request = _models.UpdateBlogsParamBlogIdArticlesParamArticleIdRequest(
            path=_models.UpdateBlogsParamBlogIdArticlesParamArticleIdRequestPath(blog_id=blog_id, article_id=article_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_article: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/blogs/{blog_id}/articles/{article_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/blogs/{blog_id}/articles/{article_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_article")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_article", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_article",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, article, online-store/article, latest_api_version
@mcp.tool()
async def delete_article(
    blog_id: str = Field(..., description="The unique identifier of the blog containing the article to delete."),
    article_id: str = Field(..., description="The unique identifier of the article to delete."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes an article from a blog. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteBlogsParamBlogIdArticlesParamArticleIdRequest(
            path=_models.DeleteBlogsParamBlogIdArticlesParamArticleIdRequestPath(blog_id=blog_id, article_id=article_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_article: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/blogs/{blog_id}/articles/{article_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/blogs/{blog_id}/articles/{article_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_article")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_article", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_article",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, carrierservice, shipping-and-fulfillment/carrierservice, latest_api_version
@mcp.tool()
async def list_carrier_services() -> dict[str, Any] | ToolResult:
    """Retrieves all carrier services available for the store. Carrier services represent shipping methods that can be offered to customers during checkout."""

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/carrier_services.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_carrier_services")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_carrier_services", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_carrier_services",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, carrierservice, shipping-and-fulfillment/carrierservice, latest_api_version
@mcp.tool()
async def get_carrier_service(carrier_service_id: str = Field(..., description="The unique identifier of the carrier service to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a single carrier service by its unique identifier. Use this to fetch configuration and capabilities for a specific shipping carrier integration."""

    # Construct request model with validation
    try:
        _request = _models.GetCarrierServicesParamCarrierServiceIdRequest(
            path=_models.GetCarrierServicesParamCarrierServiceIdRequestPath(carrier_service_id=carrier_service_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_carrier_service: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/carrier_services/{carrier_service_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/carrier_services/{carrier_service_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_carrier_service")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_carrier_service", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_carrier_service",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, carrierservice, shipping-and-fulfillment/carrierservice, latest_api_version
@mcp.tool()
async def update_carrier_service(carrier_service_id: str = Field(..., description="The unique identifier of the carrier service to update.")) -> dict[str, Any] | ToolResult:
    """Updates an existing carrier service configuration. Only the application that originally created the carrier service can modify it."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCarrierServicesParamCarrierServiceIdRequest(
            path=_models.UpdateCarrierServicesParamCarrierServiceIdRequestPath(carrier_service_id=carrier_service_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_carrier_service: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/carrier_services/{carrier_service_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/carrier_services/{carrier_service_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_carrier_service")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_carrier_service", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_carrier_service",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, carrierservice, shipping-and-fulfillment/carrierservice, latest_api_version
@mcp.tool()
async def delete_carrier_service(carrier_service_id: str = Field(..., description="The unique identifier of the carrier service to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a carrier service from the store. This removes the shipping method and all associated configurations."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCarrierServicesParamCarrierServiceIdRequest(
            path=_models.DeleteCarrierServicesParamCarrierServiceIdRequestPath(carrier_service_id=carrier_service_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_carrier_service: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/carrier_services/{carrier_service_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/carrier_services/{carrier_service_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_carrier_service")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_carrier_service", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_carrier_service",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: orders, abandoned-checkouts, orders/abandoned-checkouts, latest_api_version
@mcp.tool()
async def get_checkouts_count(
    since_id: Any | None = Field(None, description="Restrict the count to checkouts created after the specified checkout ID, useful for pagination or incremental syncing."),
    status: Any | None = Field(None, description="Filter checkouts by status: 'open' counts only active abandoned checkouts (default), while 'closed' counts only completed or cancelled abandoned checkouts."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the count of abandoned checkouts from the past 90 days, optionally filtered by status or since a specific checkpoint ID."""

    # Construct request model with validation
    try:
        _request = _models.GetCheckoutsCountRequest(
            query=_models.GetCheckoutsCountRequestQuery(since_id=since_id, status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_checkouts_count: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/checkouts/count.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_checkouts_count")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_checkouts_count", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_checkouts_count",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, collection, products/collection, latest_api_version
@mcp.tool()
async def get_collection(
    collection_id: str = Field(..., description="The unique identifier of the collection to retrieve."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields are returned, reducing payload size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single collection by its ID. Use this to fetch detailed information about a specific collection, including its products, metadata, and configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetCollectionsParamCollectionIdRequest(
            path=_models.GetCollectionsParamCollectionIdRequestPath(collection_id=collection_id),
            query=_models.GetCollectionsParamCollectionIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/collections/{collection_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/collections/{collection_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, collection, products/collection, latest_api_version
@mcp.tool()
async def list_collection_products(
    collection_id: str = Field(..., description="The unique identifier of the collection whose products you want to retrieve."),
    limit: Any | None = Field(None, description="The maximum number of products to return per request, ranging from 1 to 250 products. Defaults to 50 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve products belonging to a specific collection, sorted according to the collection's configured sort order. Results are paginated using link-based navigation provided in response headers."""

    # Construct request model with validation
    try:
        _request = _models.GetCollectionsParamCollectionIdProductsRequest(
            path=_models.GetCollectionsParamCollectionIdProductsRequestPath(collection_id=collection_id),
            query=_models.GetCollectionsParamCollectionIdProductsRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_collection_products: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/collections/{collection_id}/products.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/collections/{collection_id}/products.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_collection_products")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_collection_products", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_collection_products",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, collect, products/collect, latest_api_version
@mcp.tool()
async def list_collects(
    limit: Any | None = Field(None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50 if not specified."),
    since_id: Any | None = Field(None, description="Restrict results to collects created after the specified collect ID, useful for incremental syncing."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. Omit to return all fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of collects (product-to-collection associations). Results are paginated using cursor-based links provided in response headers; use the link relations to navigate pages rather than the page parameter."""

    # Construct request model with validation
    try:
        _request = _models.GetCollectsRequest(
            query=_models.GetCollectsRequestQuery(limit=limit, since_id=since_id, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_collects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/collects.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_collects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_collects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_collects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, collect, products/collect, latest_api_version
@mcp.tool()
async def get_collects_count(collection_id: int | None = Field(None, description="Filter the count to only include collects within a specific collection. When omitted, returns the total count of all collects.")) -> dict[str, Any] | ToolResult:
    """Retrieves the total count of collects, optionally filtered by a specific collection. Use this to determine how many products are associated with a collection or to get the total number of collects across all collections."""

    # Construct request model with validation
    try:
        _request = _models.GetCollectsCountRequest(
            query=_models.GetCollectsCountRequestQuery(collection_id=collection_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_collects_count: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/collects/count.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_collects_count")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_collects_count", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_collects_count",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, collect, products/collect, latest_api_version
@mcp.tool()
async def get_collect(
    collect_id: str = Field(..., description="The unique identifier of the collect to retrieve."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields are returned, reducing payload size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific product collection by its ID. Use this to fetch detailed information about a single collect resource."""

    # Construct request model with validation
    try:
        _request = _models.GetCollectsParamCollectIdRequest(
            path=_models.GetCollectsParamCollectIdRequestPath(collect_id=collect_id),
            query=_models.GetCollectsParamCollectIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_collect: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/collects/{collect_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/collects/{collect_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_collect")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_collect", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_collect",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, collect, products/collect, latest_api_version
@mcp.tool()
async def remove_product_from_collection(collect_id: str = Field(..., description="The unique identifier of the collect relationship to remove. This ID represents the link between a product and a collection.")) -> dict[str, Any] | ToolResult:
    """Removes a product from a collection by deleting the collect relationship. This operation unlinks a product from a specific collection without affecting the product or collection itself."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCollectsParamCollectIdRequest(
            path=_models.DeleteCollectsParamCollectIdRequestPath(collect_id=collect_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_product_from_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/collects/{collect_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/collects/{collect_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_product_from_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_product_from_collection", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_product_from_collection",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: store-properties, country, store-properties/country, latest_api_version
@mcp.tool()
async def list_countries(
    since_id: Any | None = Field(None, description="Restrict results to countries after the specified country ID, useful for pagination or resuming from a previous request."),
    fields: Any | None = Field(None, description="Limit the response to specific fields by providing a comma-separated list of field names, reducing payload size when only certain data is needed."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of all countries available in the Shopify store, optionally filtered and with customizable field selection."""

    # Construct request model with validation
    try:
        _request = _models.GetCountriesRequest(
            query=_models.GetCountriesRequestQuery(since_id=since_id, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_countries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/countries.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: store-properties, country, store-properties/country, latest_api_version
@mcp.tool()
async def get_countries_count() -> dict[str, Any] | ToolResult:
    """Retrieves the total count of countries available in the store's system. Useful for understanding the scope of country data without fetching individual records."""

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/countries/count.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_countries_count")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_countries_count", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_countries_count",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: store-properties, country, store-properties/country, latest_api_version
@mcp.tool()
async def get_country(
    country_id: str = Field(..., description="The unique identifier of the country to retrieve."),
    fields: Any | None = Field(None, description="Comma-separated list of specific fields to include in the response. If omitted, all fields are returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific country, including its provinces, tax rates, and other regional properties."""

    # Construct request model with validation
    try:
        _request = _models.GetCountriesParamCountryIdRequest(
            path=_models.GetCountriesParamCountryIdRequestPath(country_id=country_id),
            query=_models.GetCountriesParamCountryIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_country: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/countries/{country_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/countries/{country_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_country")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_country", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_country",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: store-properties, country, store-properties/country, latest_api_version
@mcp.tool()
async def delete_country(country_id: str = Field(..., description="The unique identifier of the country to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a country from the store's shipping configuration. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCountriesParamCountryIdRequest(
            path=_models.DeleteCountriesParamCountryIdRequestPath(country_id=country_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_country: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/countries/{country_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/countries/{country_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_country")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_country", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_country",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: store-properties, province, store-properties/province, latest_api_version
@mcp.tool()
async def list_provinces_for_country(
    country_id: str = Field(..., description="The unique identifier of the country for which to retrieve provinces."),
    since_id: Any | None = Field(None, description="Restrict results to provinces after the specified ID, useful for pagination or fetching only recently added provinces."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. Omit to return all available fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of provinces or states for a specified country. Use this to populate location selectors or display regional subdivisions."""

    # Construct request model with validation
    try:
        _request = _models.GetCountriesParamCountryIdProvincesRequest(
            path=_models.GetCountriesParamCountryIdProvincesRequestPath(country_id=country_id),
            query=_models.GetCountriesParamCountryIdProvincesRequestQuery(since_id=since_id, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_provinces_for_country: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/countries/{country_id}/provinces.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/countries/{country_id}/provinces.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_provinces_for_country")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_provinces_for_country", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_provinces_for_country",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: store-properties, province, store-properties/province, latest_api_version
@mcp.tool()
async def get_province_count_for_country(country_id: str = Field(..., description="The unique identifier of the country for which to retrieve the province count.")) -> dict[str, Any] | ToolResult:
    """Retrieves the total count of provinces or states for a specified country. Useful for understanding administrative divisions available in a country."""

    # Construct request model with validation
    try:
        _request = _models.GetCountriesParamCountryIdProvincesCountRequest(
            path=_models.GetCountriesParamCountryIdProvincesCountRequestPath(country_id=country_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_province_count_for_country: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/countries/{country_id}/provinces/count.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/countries/{country_id}/provinces/count.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_province_count_for_country")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_province_count_for_country", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_province_count_for_country",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: store-properties, province, store-properties/province, latest_api_version
@mcp.tool()
async def get_province(
    country_id: str = Field(..., description="The unique identifier of the country. Required to scope the province lookup to the correct country."),
    province_id: str = Field(..., description="The unique identifier of the province within the specified country. Required to retrieve the specific province details."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields will be returned, allowing you to optimize response payload size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific province within a country. Use this to fetch province data such as name, code, and tax information for a given country."""

    # Construct request model with validation
    try:
        _request = _models.GetCountriesParamCountryIdProvincesParamProvinceIdRequest(
            path=_models.GetCountriesParamCountryIdProvincesParamProvinceIdRequestPath(country_id=country_id, province_id=province_id),
            query=_models.GetCountriesParamCountryIdProvincesParamProvinceIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_province: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/countries/{country_id}/provinces/{province_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/countries/{country_id}/provinces/{province_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_province")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_province", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_province",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: store-properties, currency, store-properties/currency, latest_api_version
@mcp.tool()
async def list_currencies() -> dict[str, Any] | ToolResult:
    """Retrieves a list of all currencies that are enabled and available on the shop for transactions and pricing."""

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/currencies.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_currencies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_currencies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_currencies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, customcollection, products/customcollection, latest_api_version
@mcp.tool()
async def list_custom_collections(
    limit: Any | None = Field(None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50 if not specified."),
    ids: Any | None = Field(None, description="Filter results to only include collections with IDs matching this comma-separated list."),
    since_id: Any | None = Field(None, description="Return only collections with IDs greater than this value, useful for cursor-based pagination when combined with limit."),
    title: Any | None = Field(None, description="Filter results to collections matching this exact title."),
    product_id: Any | None = Field(None, description="Filter results to only collections that contain the product with this ID."),
    handle: Any | None = Field(None, description="Filter results to collections matching this handle (the URL-friendly identifier)."),
    published_status: Any | None = Field(None, description="Filter by publication status: 'published' for published collections only, 'unpublished' for unpublished only, or 'any' for all statuses. Defaults to 'any'."),
    fields: Any | None = Field(None, description="Limit the response to only these fields, specified as a comma-separated list of field names. Reduces payload size when you only need specific data."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of custom collections from your store, with support for filtering, sorting, and field selection. Results are paginated using cursor-based links provided in response headers."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomCollectionsRequest(
            query=_models.GetCustomCollectionsRequestQuery(limit=limit, ids=ids, since_id=since_id, title=title, product_id=product_id, handle=handle, published_status=published_status, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_collections: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/custom_collections.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_collections")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_collections", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_collections",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, customcollection, products/customcollection, latest_api_version
@mcp.tool()
async def count_custom_collections(
    title: Any | None = Field(None, description="Filter the count to include only custom collections with this exact title."),
    product_id: Any | None = Field(None, description="Filter the count to include only custom collections that contain this specific product."),
    published_status: Any | None = Field(None, description="Filter the count by publication status: 'published' for published collections only, 'unpublished' for unpublished collections only, or 'any' for all collections regardless of status. Defaults to 'any'."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the total count of custom collections, optionally filtered by title, product inclusion, or published status."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomCollectionsCountRequest(
            query=_models.GetCustomCollectionsCountRequestQuery(title=title, product_id=product_id, published_status=published_status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for count_custom_collections: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/custom_collections/count.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("count_custom_collections")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("count_custom_collections", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="count_custom_collections",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, customcollection, products/customcollection, latest_api_version
@mcp.tool()
async def get_custom_collection(
    custom_collection_id: str = Field(..., description="The unique identifier of the custom collection to retrieve."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields are returned, reducing payload size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single custom collection by its ID. Use this to fetch detailed information about a specific custom collection in your store."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomCollectionsParamCustomCollectionIdRequest(
            path=_models.GetCustomCollectionsParamCustomCollectionIdRequestPath(custom_collection_id=custom_collection_id),
            query=_models.GetCustomCollectionsParamCustomCollectionIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/custom_collections/{custom_collection_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/custom_collections/{custom_collection_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_collection", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_collection",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, customcollection, products/customcollection, latest_api_version
@mcp.tool()
async def update_custom_collection(custom_collection_id: str = Field(..., description="The unique identifier of the custom collection to update.")) -> dict[str, Any] | ToolResult:
    """Updates the properties of an existing custom collection, such as title, description, image, or sort order of products."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCustomCollectionsParamCustomCollectionIdRequest(
            path=_models.UpdateCustomCollectionsParamCustomCollectionIdRequestPath(custom_collection_id=custom_collection_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/custom_collections/{custom_collection_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/custom_collections/{custom_collection_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_collection", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_collection",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, customcollection, products/customcollection, latest_api_version
@mcp.tool()
async def delete_custom_collection(custom_collection_id: str = Field(..., description="The unique identifier of the custom collection to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a custom collection from the store. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomCollectionsParamCustomCollectionIdRequest(
            path=_models.DeleteCustomCollectionsParamCustomCollectionIdRequestPath(custom_collection_id=custom_collection_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/custom_collections/{custom_collection_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/custom_collections/{custom_collection_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_custom_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_custom_collection", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_custom_collection",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customersavedsearch, customers/customersavedsearch, latest_api_version
@mcp.tool()
async def get_customer_saved_search(
    customer_saved_search_id: str = Field(..., description="The unique identifier of the customer saved search to retrieve."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields are returned, reducing payload size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single customer saved search by its ID. Use this to fetch detailed information about a specific saved search that a customer has created."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomerSavedSearchesParamCustomerSavedSearchIdRequest(
            path=_models.GetCustomerSavedSearchesParamCustomerSavedSearchIdRequestPath(customer_saved_search_id=customer_saved_search_id),
            query=_models.GetCustomerSavedSearchesParamCustomerSavedSearchIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_customer_saved_search: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customer_saved_searches/{customer_saved_search_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customer_saved_searches/{customer_saved_search_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_customer_saved_search")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_customer_saved_search", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_customer_saved_search",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customersavedsearch, customers/customersavedsearch, latest_api_version
@mcp.tool()
async def update_customer_saved_search(customer_saved_search_id: str = Field(..., description="The unique identifier of the customer saved search to update. This ID is returned when the saved search is created and is required to target the correct search for modification.")) -> dict[str, Any] | ToolResult:
    """Updates an existing customer saved search with new criteria or settings. This allows modification of a previously created saved search that customers can use to filter and organize customer data."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCustomerSavedSearchesParamCustomerSavedSearchIdRequest(
            path=_models.UpdateCustomerSavedSearchesParamCustomerSavedSearchIdRequestPath(customer_saved_search_id=customer_saved_search_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_customer_saved_search: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customer_saved_searches/{customer_saved_search_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customer_saved_searches/{customer_saved_search_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_customer_saved_search")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_customer_saved_search", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_customer_saved_search",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customersavedsearch, customers/customersavedsearch, latest_api_version
@mcp.tool()
async def delete_customer_saved_search(customer_saved_search_id: str = Field(..., description="The unique identifier of the customer saved search to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a customer saved search by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomerSavedSearchesParamCustomerSavedSearchIdRequest(
            path=_models.DeleteCustomerSavedSearchesParamCustomerSavedSearchIdRequestPath(customer_saved_search_id=customer_saved_search_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_customer_saved_search: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customer_saved_searches/{customer_saved_search_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customer_saved_searches/{customer_saved_search_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_customer_saved_search")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_customer_saved_search", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_customer_saved_search",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customersavedsearch, customers/customersavedsearch, latest_api_version
@mcp.tool()
async def list_customers_for_saved_search(
    customer_saved_search_id: str = Field(..., description="The unique identifier of the customer saved search whose matching customers you want to retrieve."),
    order: Any | None = Field(None, description="Specifies the field and sort direction for ordering results. Defaults to sorting by last order date in descending order."),
    limit: Any | None = Field(None, description="The maximum number of customer records to return per request, ranging from 1 to 250. Defaults to 50 results."),
    fields: Any | None = Field(None, description="Comma-separated list of customer field names to include in the response. Omit to return all available fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all customers matching the criteria defined in a customer saved search. Use this to fetch customer lists based on pre-configured search filters."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequest(
            path=_models.GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestPath(customer_saved_search_id=customer_saved_search_id),
            query=_models.GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestQuery(order=order, limit=limit, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_customers_for_saved_search: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customer_saved_searches/{customer_saved_search_id}/customers.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customer_saved_searches/{customer_saved_search_id}/customers.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_customers_for_saved_search")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_customers_for_saved_search", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_customers_for_saved_search",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customer, customers/customer, latest_api_version
@mcp.tool()
async def list_customers(
    ids: Any | None = Field(None, description="Filter results to only customers with IDs matching this comma-separated list of customer identifiers."),
    since_id: Any | None = Field(None, description="Return only customers with IDs greater than this value, useful for cursor-based pagination when link headers are unavailable."),
    limit: Any | None = Field(None, description="Maximum number of customers to return per request; defaults to 50 and cannot exceed 250."),
    fields: Any | None = Field(None, description="Restrict the response to only these fields, specified as a comma-separated list of field names; omit to receive all available fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of customers from the store. Results are paginated using cursor-based links provided in response headers; use the link relations to navigate pages rather than the page parameter."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomersRequest(
            query=_models.GetCustomersRequestQuery(ids=ids, since_id=since_id, limit=limit, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_customers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/customers.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_customers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_customers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_customers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customer, customers/customer, latest_api_version
@mcp.tool()
async def get_customers_count() -> dict[str, Any] | ToolResult:
    """Retrieves the total count of all customers in the store. Useful for understanding customer base size and pagination planning."""

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/customers/count.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_customers_count")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_customers_count", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_customers_count",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customer, customers/customer, latest_api_version
@mcp.tool()
async def search_customers(
    order: Any | None = Field(None, description="Specify the field and direction to sort results. Use format: field_name ASC or field_name DESC. Defaults to sorting by last order date in descending order."),
    query: Any | None = Field(None, description="Text query to search across customer data fields such as name, email, phone, and address information."),
    limit: Any | None = Field(None, description="Maximum number of results to return per request. Must be between 1 and 250. Defaults to 50 results."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. If omitted, all fields are returned."),
) -> dict[str, Any] | ToolResult:
    """Search for customers in the shop by query text, with support for sorting and field filtering. Results are paginated using cursor-based links provided in response headers."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomersSearchRequest(
            query=_models.GetCustomersSearchRequestQuery(order=order, query=query, limit=limit, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_customers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/customers/search.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_customers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_customers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_customers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customer, customers/customer, latest_api_version
@mcp.tool()
async def get_customer(
    customer_id: str = Field(..., description="The unique identifier of the customer to retrieve."),
    fields: Any | None = Field(None, description="Comma-separated list of specific fields to return in the response. Omit to retrieve all available customer fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single customer by ID from the Shopify store. Use this to fetch detailed customer information including contact details, addresses, and order history."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomersParamCustomerIdRequest(
            path=_models.GetCustomersParamCustomerIdRequestPath(customer_id=customer_id),
            query=_models.GetCustomersParamCustomerIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_customer: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customers/{customer_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customers/{customer_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_customer")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_customer", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_customer",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customer, customers/customer, latest_api_version
@mcp.tool()
async def update_customer(customer_id: str = Field(..., description="The unique identifier of the customer to update. This ID is required to specify which customer record should be modified.")) -> dict[str, Any] | ToolResult:
    """Updates an existing customer's information in Shopify. Modify customer details such as name, email, phone, and other profile attributes."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCustomersParamCustomerIdRequest(
            path=_models.UpdateCustomersParamCustomerIdRequestPath(customer_id=customer_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_customer: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customers/{customer_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customers/{customer_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_customer")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_customer", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_customer",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customer, customers/customer, latest_api_version
@mcp.tool()
async def delete_customer(customer_id: str = Field(..., description="The unique identifier of the customer to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a customer from the store. The deletion will fail if the customer has any existing orders."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomersParamCustomerIdRequest(
            path=_models.DeleteCustomersParamCustomerIdRequestPath(customer_id=customer_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_customer: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customers/{customer_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customers/{customer_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_customer")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_customer", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_customer",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customer, customers/customer, latest_api_version
@mcp.tool()
async def generate_customer_account_activation_url(customer_id: str = Field(..., description="The unique identifier of the customer for whom to generate the activation URL.")) -> dict[str, Any] | ToolResult:
    """Generate a one-time account activation URL for a customer whose account is not yet enabled. The URL expires after 30 days; generating a new URL invalidates any previously generated URLs."""

    # Construct request model with validation
    try:
        _request = _models.CreateCustomersParamCustomerIdAccountActivationUrlRequest(
            path=_models.CreateCustomersParamCustomerIdAccountActivationUrlRequestPath(customer_id=customer_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_customer_account_activation_url: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customers/{customer_id}/account_activation_url.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customers/{customer_id}/account_activation_url.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_customer_account_activation_url")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_customer_account_activation_url", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_customer_account_activation_url",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customer-address, customers/customer-address, latest_api_version
@mcp.tool()
async def list_customer_addresses(customer_id: str = Field(..., description="The unique identifier of the customer whose addresses you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves all addresses associated with a specific customer. Results are paginated using link-based navigation provided in response headers."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomersParamCustomerIdAddressesRequest(
            path=_models.GetCustomersParamCustomerIdAddressesRequestPath(customer_id=customer_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_customer_addresses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customers/{customer_id}/addresses.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customers/{customer_id}/addresses.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_customer_addresses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_customer_addresses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_customer_addresses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customer-address, customers/customer-address, latest_api_version
@mcp.tool()
async def add_address_for_customer(customer_id: str = Field(..., description="The unique identifier of the customer to whom the address will be added.")) -> dict[str, Any] | ToolResult:
    """Adds a new address to a customer's address book. The address will be associated with the specified customer and can be used for shipping or billing purposes."""

    # Construct request model with validation
    try:
        _request = _models.CreateCustomersParamCustomerIdAddressesRequest(
            path=_models.CreateCustomersParamCustomerIdAddressesRequestPath(customer_id=customer_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_address_for_customer: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customers/{customer_id}/addresses.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customers/{customer_id}/addresses.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_address_for_customer")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_address_for_customer", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_address_for_customer",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customer-address, customers/customer-address, latest_api_version
@mcp.tool()
async def update_customer_addresses(
    customer_id: str = Field(..., description="The unique identifier of the customer whose addresses will be modified."),
    address_ids: int | None = Field(None, description="Array of address IDs to include in the bulk operation. The order may be significant depending on the operation type."),
    operation: str | None = Field(None, description="The type of bulk operation to perform on the specified addresses (e.g., set as default, delete, or activate)."),
) -> dict[str, Any] | ToolResult:
    """Perform bulk operations on multiple addresses for a specific customer, such as setting a default address or removing addresses in batch."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCustomersParamCustomerIdAddressesSetRequest(
            path=_models.UpdateCustomersParamCustomerIdAddressesSetRequestPath(customer_id=customer_id),
            query=_models.UpdateCustomersParamCustomerIdAddressesSetRequestQuery(address_ids=address_ids, operation=operation)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_customer_addresses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customers/{customer_id}/addresses/set.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customers/{customer_id}/addresses/set.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_customer_addresses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_customer_addresses", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_customer_addresses",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customer-address, customers/customer-address, latest_api_version
@mcp.tool()
async def get_customer_address(
    customer_id: str = Field(..., description="The unique identifier of the customer who owns the address."),
    address_id: str = Field(..., description="The unique identifier of the address to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific address associated with a customer account."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomersParamCustomerIdAddressesParamAddressIdRequest(
            path=_models.GetCustomersParamCustomerIdAddressesParamAddressIdRequestPath(customer_id=customer_id, address_id=address_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_customer_address: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customers/{customer_id}/addresses/{address_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customers/{customer_id}/addresses/{address_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_customer_address")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_customer_address", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_customer_address",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customer-address, customers/customer-address, latest_api_version
@mcp.tool()
async def update_customer_address(
    customer_id: str = Field(..., description="The unique identifier of the customer whose address is being updated."),
    address_id: str = Field(..., description="The unique identifier of the specific address to update for the customer."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing address for a customer. Provide the customer ID and address ID to modify the address details."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCustomersParamCustomerIdAddressesParamAddressIdRequest(
            path=_models.UpdateCustomersParamCustomerIdAddressesParamAddressIdRequestPath(customer_id=customer_id, address_id=address_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_customer_address: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customers/{customer_id}/addresses/{address_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customers/{customer_id}/addresses/{address_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_customer_address")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_customer_address", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_customer_address",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customer-address, customers/customer-address, latest_api_version
@mcp.tool()
async def delete_customer_address(
    customer_id: str = Field(..., description="The unique identifier of the customer whose address is being removed."),
    address_id: str = Field(..., description="The unique identifier of the address to be deleted from the customer's address list."),
) -> dict[str, Any] | ToolResult:
    """Removes a specific address from a customer's address list. This operation permanently deletes the address record associated with the given customer."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomersParamCustomerIdAddressesParamAddressIdRequest(
            path=_models.DeleteCustomersParamCustomerIdAddressesParamAddressIdRequestPath(customer_id=customer_id, address_id=address_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_customer_address: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customers/{customer_id}/addresses/{address_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customers/{customer_id}/addresses/{address_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_customer_address")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_customer_address", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_customer_address",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customer-address, customers/customer-address, latest_api_version
@mcp.tool()
async def set_customer_default_address(
    customer_id: str = Field(..., description="The unique identifier of the customer whose default address is being updated."),
    address_id: str = Field(..., description="The unique identifier of the address to set as the customer's default address."),
) -> dict[str, Any] | ToolResult:
    """Designates a specific address as the default address for a customer. This address will be used as the primary contact address for the customer account."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequest(
            path=_models.UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequestPath(customer_id=customer_id, address_id=address_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_customer_default_address: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customers/{customer_id}/addresses/{address_id}/default.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customers/{customer_id}/addresses/{address_id}/default.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_customer_default_address")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_customer_default_address", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_customer_default_address",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customer, customers/customer, latest_api_version
@mcp.tool()
async def list_customer_orders(customer_id: str = Field(..., description="The unique identifier of the customer whose orders should be retrieved.")) -> dict[str, Any] | ToolResult:
    """Retrieves all orders for a specific customer. Supports standard order resource query parameters for filtering, sorting, and pagination."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomersParamCustomerIdOrdersRequest(
            path=_models.GetCustomersParamCustomerIdOrdersRequestPath(customer_id=customer_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_customer_orders: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customers/{customer_id}/orders.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customers/{customer_id}/orders.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_customer_orders")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_customer_orders", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_customer_orders",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: customers, customer, customers/customer, latest_api_version
@mcp.tool()
async def send_customer_invite(customer_id: str = Field(..., description="The unique identifier of the customer who will receive the invitation.")) -> dict[str, Any] | ToolResult:
    """Sends an account invitation email to a customer, allowing them to create or access their account."""

    # Construct request model with validation
    try:
        _request = _models.CreateCustomersParamCustomerIdSendInviteRequest(
            path=_models.CreateCustomersParamCustomerIdSendInviteRequestPath(customer_id=customer_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_customer_invite: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/customers/{customer_id}/send_invite.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/customers/{customer_id}/send_invite.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_customer_invite")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_customer_invite", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_customer_invite",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: discounts, discountcode, discounts/discountcode, latest_api_version
@mcp.tool()
async def lookup_discount_code(code: str | None = Field(None, description="The discount code string to look up. Used to find and return the resource location of the matching discount code.")) -> dict[str, Any] | ToolResult:
    """Retrieves the location of a discount code by its code value. The discount code's location is returned in the HTTP location header rather than in the response body."""

    # Construct request model with validation
    try:
        _request = _models.GetDiscountCodesLookupRequest(
            query=_models.GetDiscountCodesLookupRequestQuery(code=code)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for lookup_discount_code: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/discount_codes/lookup.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("lookup_discount_code")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("lookup_discount_code", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="lookup_discount_code",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: events, event, events/event, latest_api_version
@mcp.tool()
async def list_events(
    limit: Any | None = Field(None, description="Maximum number of events to return per request. Defaults to 50 if not specified; maximum allowed is 250."),
    since_id: Any | None = Field(None, description="Return only events that occurred after the specified event ID, useful for incremental syncing."),
    filter_: Any | None = Field(None, alias="filter", description="Filter events by a specific criteria or resource type to narrow results."),
    verb: Any | None = Field(None, description="Filter events by action type (e.g., create, update, delete) to show only events of a certain kind."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response; omit to return all fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of events from the store. Results are paginated using cursor-based links provided in response headers; use the link relations to navigate pages rather than the page parameter."""

    # Construct request model with validation
    try:
        _request = _models.GetEventsRequest(
            query=_models.GetEventsRequestQuery(limit=limit, since_id=since_id, filter_=filter_, verb=verb, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/events.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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

# Tags: events, event, events/event, latest_api_version
@mcp.tool()
async def get_events_count() -> dict[str, Any] | ToolResult:
    """Retrieves the total count of events in the Shopify store. Use this to get a quick aggregate metric without fetching individual event records."""

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/events/count.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_events_count")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_events_count", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_events_count",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: events, event, events/event, latest_api_version
@mcp.tool()
async def get_event(
    event_id: str = Field(..., description="The unique identifier of the event to retrieve."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields will be returned, reducing payload size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single event by its ID from the Shopify admin. Use this to fetch detailed information about a specific event that occurred in your store."""

    # Construct request model with validation
    try:
        _request = _models.GetEventsParamEventIdRequest(
            path=_models.GetEventsParamEventIdRequestPath(event_id=event_id),
            query=_models.GetEventsParamEventIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/events/{event_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/events/{event_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillmentorder, shipping-and-fulfillment/fulfillmentorder, latest_api_version
@mcp.tool()
async def get_fulfillment_order(fulfillment_order_id: str = Field(..., description="The unique identifier of the fulfillment order to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific fulfillment order by its ID, including order status, line items, and fulfillment tracking information."""

    # Construct request model with validation
    try:
        _request = _models.GetFulfillmentOrdersParamFulfillmentOrderIdRequest(
            path=_models.GetFulfillmentOrdersParamFulfillmentOrderIdRequestPath(fulfillment_order_id=fulfillment_order_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_fulfillment_order: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_fulfillment_order")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_fulfillment_order", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_fulfillment_order",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillmentorder, shipping-and-fulfillment/fulfillmentorder, latest_api_version
@mcp.tool()
async def cancel_fulfillment_order(fulfillment_order_id: str = Field(..., description="The unique identifier of the fulfillment order to cancel. This ID references a specific fulfillment order within your store.")) -> dict[str, Any] | ToolResult:
    """Cancels a fulfillment order, marking it as no longer needed for processing. This operation prevents further fulfillment actions on the specified order."""

    # Construct request model with validation
    try:
        _request = _models.CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequest(
            path=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequestPath(fulfillment_order_id=fulfillment_order_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for cancel_fulfillment_order: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/cancel.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/cancel.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("cancel_fulfillment_order")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("cancel_fulfillment_order", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="cancel_fulfillment_order",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, cancellationrequest, shipping-and-fulfillment/cancellationrequest, latest_api_version
@mcp.tool()
async def send_fulfillment_order_cancellation_request(
    fulfillment_order_id: str = Field(..., description="The unique identifier of the fulfillment order to cancel. This ID references a specific fulfillment order within your Shopify store."),
    message: Any | None = Field(None, description="An optional message explaining the reason for the cancellation request. This message is typically sent to the fulfillment service to provide context for the cancellation."),
) -> dict[str, Any] | ToolResult:
    """Sends a cancellation request to the fulfillment service for a specific fulfillment order. This notifies the fulfillment provider that the order should be cancelled if not yet fulfilled."""

    # Construct request model with validation
    try:
        _request = _models.CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequest(
            path=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestPath(fulfillment_order_id=fulfillment_order_id),
            query=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestQuery(message=message)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_fulfillment_order_cancellation_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/cancellation_request.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/cancellation_request.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_fulfillment_order_cancellation_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_fulfillment_order_cancellation_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_fulfillment_order_cancellation_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, cancellationrequest, shipping-and-fulfillment/cancellationrequest, latest_api_version
@mcp.tool()
async def accept_fulfillment_order_cancellation_request(
    fulfillment_order_id: str = Field(..., description="The unique identifier of the fulfillment order for which the cancellation request is being accepted."),
    message: Any | None = Field(None, description="An optional message explaining the reason for accepting the cancellation request."),
) -> dict[str, Any] | ToolResult:
    """Accepts a cancellation request for a fulfillment order, notifying the fulfillment service that the cancellation has been approved. Optionally include a reason for accepting the request."""

    # Construct request model with validation
    try:
        _request = _models.CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequest(
            path=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestPath(fulfillment_order_id=fulfillment_order_id),
            query=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestQuery(message=message)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for accept_fulfillment_order_cancellation_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/cancellation_request/accept.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/cancellation_request/accept.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("accept_fulfillment_order_cancellation_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("accept_fulfillment_order_cancellation_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="accept_fulfillment_order_cancellation_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, cancellationrequest, shipping-and-fulfillment/cancellationrequest, latest_api_version
@mcp.tool()
async def reject_fulfillment_order_cancellation_request(
    fulfillment_order_id: str = Field(..., description="The unique identifier of the fulfillment order for which the cancellation request should be rejected."),
    message: Any | None = Field(None, description="An optional message explaining why the cancellation request is being rejected. This reason will be communicated to the fulfillment service."),
) -> dict[str, Any] | ToolResult:
    """Rejects a cancellation request that was sent to a fulfillment service for a specific fulfillment order. Use this when you need to decline a cancellation and optionally provide a reason to the fulfillment service."""

    # Construct request model with validation
    try:
        _request = _models.CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequest(
            path=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestPath(fulfillment_order_id=fulfillment_order_id),
            query=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestQuery(message=message)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reject_fulfillment_order_cancellation_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/cancellation_request/reject.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/cancellation_request/reject.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reject_fulfillment_order_cancellation_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reject_fulfillment_order_cancellation_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reject_fulfillment_order_cancellation_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillmentorder, shipping-and-fulfillment/fulfillmentorder, latest_api_version
@mcp.tool()
async def close_fulfillment_order(
    fulfillment_order_id: str = Field(..., description="The unique identifier of the fulfillment order to close."),
    message: Any | None = Field(None, description="An optional reason or note explaining why the fulfillment order is being marked as incomplete."),
) -> dict[str, Any] | ToolResult:
    """Marks an in-progress fulfillment order as incomplete, indicating the fulfillment service cannot ship remaining items and is closing the order."""

    # Construct request model with validation
    try:
        _request = _models.CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequest(
            path=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestPath(fulfillment_order_id=fulfillment_order_id),
            query=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestQuery(message=message)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for close_fulfillment_order: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/close.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/close.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("close_fulfillment_order")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("close_fulfillment_order", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="close_fulfillment_order",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillmentrequest, shipping-and-fulfillment/fulfillmentrequest, latest_api_version
@mcp.tool()
async def send_fulfillment_request(
    fulfillment_order_id: str = Field(..., description="The unique identifier of the fulfillment order to request fulfillment for."),
    message: Any | None = Field(None, description="An optional message to include with the fulfillment request, typically for communicating special instructions or notes to the fulfillment service."),
    fulfillment_order_line_items: Any | None = Field(None, description="An optional list of specific line items from the fulfillment order to request for fulfillment. If omitted, all unfulfilled line items in the order are included in the request."),
) -> dict[str, Any] | ToolResult:
    """Sends a fulfillment request to the fulfillment service for a specific fulfillment order, optionally targeting specific line items or including a message for the fulfillment provider."""

    # Construct request model with validation
    try:
        _request = _models.CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequest(
            path=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestPath(fulfillment_order_id=fulfillment_order_id),
            query=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestQuery(message=message, fulfillment_order_line_items=fulfillment_order_line_items)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_fulfillment_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/fulfillment_request.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/fulfillment_request.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_fulfillment_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_fulfillment_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_fulfillment_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillmentrequest, shipping-and-fulfillment/fulfillmentrequest, latest_api_version
@mcp.tool()
async def accept_fulfillment_request(
    fulfillment_order_id: str = Field(..., description="The unique identifier of the fulfillment order for which the fulfillment request is being accepted."),
    message: Any | None = Field(None, description="An optional message explaining the reason for accepting the fulfillment request."),
) -> dict[str, Any] | ToolResult:
    """Accepts a fulfillment request that was sent to a fulfillment service for a specific fulfillment order, optionally providing a reason for acceptance."""

    # Construct request model with validation
    try:
        _request = _models.CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequest(
            path=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestPath(fulfillment_order_id=fulfillment_order_id),
            query=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestQuery(message=message)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for accept_fulfillment_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/fulfillment_request/accept.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/fulfillment_request/accept.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("accept_fulfillment_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("accept_fulfillment_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="accept_fulfillment_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillmentrequest, shipping-and-fulfillment/fulfillmentrequest, latest_api_version
@mcp.tool()
async def reject_fulfillment_request(
    fulfillment_order_id: str = Field(..., description="The unique identifier of the fulfillment order for which the fulfillment request should be rejected."),
    message: Any | None = Field(None, description="An optional message explaining the reason for rejecting the fulfillment request."),
) -> dict[str, Any] | ToolResult:
    """Rejects a fulfillment request that was sent to a fulfillment service for a specific fulfillment order, optionally providing a reason for the rejection."""

    # Construct request model with validation
    try:
        _request = _models.CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequest(
            path=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestPath(fulfillment_order_id=fulfillment_order_id),
            query=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestQuery(message=message)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reject_fulfillment_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/fulfillment_request/reject.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/fulfillment_request/reject.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reject_fulfillment_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reject_fulfillment_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reject_fulfillment_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillment, shipping-and-fulfillment/fulfillment, latest_api_version
@mcp.tool()
async def list_fulfillments_for_order(fulfillment_order_id: str = Field(..., description="The unique identifier of the fulfillment order. This ID is required to retrieve its associated fulfillments.")) -> dict[str, Any] | ToolResult:
    """Retrieves all fulfillments associated with a specific fulfillment order. Use this to view fulfillment details and status for a given order."""

    # Construct request model with validation
    try:
        _request = _models.GetFulfillmentOrdersParamFulfillmentOrderIdFulfillmentsRequest(
            path=_models.GetFulfillmentOrdersParamFulfillmentOrderIdFulfillmentsRequestPath(fulfillment_order_id=fulfillment_order_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_fulfillments_for_order: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/fulfillments.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/fulfillments.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_fulfillments_for_order")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_fulfillments_for_order", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_fulfillments_for_order",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, locationsformove, shipping-and-fulfillment/locationsformove, latest_api_version
@mcp.tool()
async def list_locations_for_fulfillment_order_move(fulfillment_order_id: str = Field(..., description="The unique identifier of the fulfillment order for which to retrieve available move destinations.")) -> dict[str, Any] | ToolResult:
    """Retrieves a list of locations where a fulfillment order can be moved to. Results are sorted alphabetically by location name in ascending order."""

    # Construct request model with validation
    try:
        _request = _models.GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequest(
            path=_models.GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequestPath(fulfillment_order_id=fulfillment_order_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_locations_for_fulfillment_order_move: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/locations_for_move.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/locations_for_move.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_locations_for_fulfillment_order_move")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_locations_for_fulfillment_order_move", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_locations_for_fulfillment_order_move",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillmentorder, shipping-and-fulfillment/fulfillmentorder, latest_api_version
@mcp.tool()
async def move_fulfillment_order(
    fulfillment_order_id: str = Field(..., description="The unique identifier of the fulfillment order to be moved."),
    new_location_id: Any | None = Field(None, description="The unique identifier of the destination location where the fulfillment order will be transferred. Must be a merchant-managed location."),
) -> dict[str, Any] | ToolResult:
    """Relocates a fulfillment order to a different merchant-managed location, enabling inventory redistribution across fulfillment centers."""

    # Construct request model with validation
    try:
        _request = _models.CreateFulfillmentOrdersParamFulfillmentOrderIdMoveRequest(
            path=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdMoveRequestPath(fulfillment_order_id=fulfillment_order_id),
            query=_models.CreateFulfillmentOrdersParamFulfillmentOrderIdMoveRequestQuery(new_location_id=new_location_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for move_fulfillment_order: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/move.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillment_orders/{fulfillment_order_id}/move.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("move_fulfillment_order")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("move_fulfillment_order", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="move_fulfillment_order",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillmentservice, shipping-and-fulfillment/fulfillmentservice, latest_api_version
@mcp.tool()
async def list_fulfillment_services(scope: Any | None = Field(None, description="Filter scope for returned fulfillment providers. Use 'current_client' (default) to return only providers created by this app, or 'all' to return every fulfillment provider in the store.")) -> dict[str, Any] | ToolResult:
    """Retrieve a list of fulfillment service providers. By default, returns only fulfillment providers created by the requesting app, or optionally all available providers in the store."""

    # Construct request model with validation
    try:
        _request = _models.GetFulfillmentServicesRequest(
            query=_models.GetFulfillmentServicesRequestQuery(scope=scope)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_fulfillment_services: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/fulfillment_services.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_fulfillment_services")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_fulfillment_services", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_fulfillment_services",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillmentservice, shipping-and-fulfillment/fulfillmentservice, latest_api_version
@mcp.tool()
async def get_fulfillment_service(fulfillment_service_id: str = Field(..., description="The unique identifier of the fulfillment service to retrieve. This ID is assigned by Shopify when the service is created or integrated.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific fulfillment service by its ID. Use this to fetch configuration, capabilities, and status of a fulfillment service integrated with your Shopify store."""

    # Construct request model with validation
    try:
        _request = _models.GetFulfillmentServicesParamFulfillmentServiceIdRequest(
            path=_models.GetFulfillmentServicesParamFulfillmentServiceIdRequestPath(fulfillment_service_id=fulfillment_service_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_fulfillment_service: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillment_services/{fulfillment_service_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillment_services/{fulfillment_service_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_fulfillment_service")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_fulfillment_service", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_fulfillment_service",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillmentservice, shipping-and-fulfillment/fulfillmentservice, latest_api_version
@mcp.tool()
async def update_fulfillment_service(fulfillment_service_id: str = Field(..., description="The unique identifier of the fulfillment service to update.")) -> dict[str, Any] | ToolResult:
    """Update the configuration and settings of an existing fulfillment service, such as its name, callback URLs, or tracking capabilities."""

    # Construct request model with validation
    try:
        _request = _models.UpdateFulfillmentServicesParamFulfillmentServiceIdRequest(
            path=_models.UpdateFulfillmentServicesParamFulfillmentServiceIdRequestPath(fulfillment_service_id=fulfillment_service_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_fulfillment_service: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillment_services/{fulfillment_service_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillment_services/{fulfillment_service_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_fulfillment_service")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_fulfillment_service", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_fulfillment_service",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillmentservice, shipping-and-fulfillment/fulfillmentservice, latest_api_version
@mcp.tool()
async def delete_fulfillment_service(fulfillment_service_id: str = Field(..., description="The unique identifier of the fulfillment service to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a fulfillment service by its ID. This removes the fulfillment service from your Shopify store."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFulfillmentServicesParamFulfillmentServiceIdRequest(
            path=_models.DeleteFulfillmentServicesParamFulfillmentServiceIdRequestPath(fulfillment_service_id=fulfillment_service_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_fulfillment_service: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillment_services/{fulfillment_service_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillment_services/{fulfillment_service_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_fulfillment_service")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_fulfillment_service", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_fulfillment_service",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillment, shipping-and-fulfillment/fulfillment, latest_api_version
@mcp.tool()
async def cancel_fulfillment(fulfillment_id: str = Field(..., description="The unique identifier of the fulfillment to cancel. This ID references a specific fulfillment record that must exist and be in a cancellable state.")) -> dict[str, Any] | ToolResult:
    """Cancels an existing fulfillment, preventing further processing or shipment of the associated items."""

    # Construct request model with validation
    try:
        _request = _models.CreateFulfillmentsParamFulfillmentIdCancelRequest(
            path=_models.CreateFulfillmentsParamFulfillmentIdCancelRequestPath(fulfillment_id=fulfillment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for cancel_fulfillment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillments/{fulfillment_id}/cancel.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillments/{fulfillment_id}/cancel.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("cancel_fulfillment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("cancel_fulfillment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="cancel_fulfillment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillment, shipping-and-fulfillment/fulfillment, latest_api_version
@mcp.tool()
async def update_fulfillment_tracking(fulfillment_id: str = Field(..., description="The unique identifier of the fulfillment whose tracking information should be updated.")) -> dict[str, Any] | ToolResult:
    """Updates the tracking information for a fulfillment, allowing you to modify shipment tracking details after the fulfillment has been created."""

    # Construct request model with validation
    try:
        _request = _models.CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequest(
            path=_models.CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequestPath(fulfillment_id=fulfillment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_fulfillment_tracking: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/fulfillments/{fulfillment_id}/update_tracking.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/fulfillments/{fulfillment_id}/update_tracking.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_fulfillment_tracking")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_fulfillment_tracking", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_fulfillment_tracking",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: plus, giftcard, plus/giftcard, latest_api_version
@mcp.tool()
async def list_gift_cards(
    status: Any | None = Field(None, description="Filter results to gift cards with a specific status: enabled to show only active gift cards, or disabled to show only inactive gift cards."),
    limit: Any | None = Field(None, description="Maximum number of results to return per request, between 1 and 250 (defaults to 50)."),
    since_id: Any | None = Field(None, description="Cursor-based pagination parameter: retrieve only gift cards with IDs after the specified ID to continue from a previous result set."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response; omit to return all fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of gift cards from the store, optionally filtered by status. Results are paginated using cursor-based links provided in response headers."""

    # Construct request model with validation
    try:
        _request = _models.GetGiftCardsRequest(
            query=_models.GetGiftCardsRequestQuery(status=status, limit=limit, since_id=since_id, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_gift_cards: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/gift_cards.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_gift_cards")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_gift_cards", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_gift_cards",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: plus, giftcard, plus/giftcard, latest_api_version
@mcp.tool()
async def get_gift_cards_count(status: Any | None = Field(None, description="Filter the count to only include gift cards with a specific status: enabled for active gift cards, or disabled for inactive gift cards. Omit to count all gift cards regardless of status.")) -> dict[str, Any] | ToolResult:
    """Retrieves the total count of gift cards in the store, optionally filtered by status (enabled or disabled)."""

    # Construct request model with validation
    try:
        _request = _models.GetGiftCardsCountRequest(
            query=_models.GetGiftCardsCountRequestQuery(status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_gift_cards_count: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/gift_cards/count.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_gift_cards_count")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_gift_cards_count", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_gift_cards_count",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: plus, giftcard, plus/giftcard, latest_api_version
@mcp.tool()
async def search_gift_cards(
    order: Any | None = Field(None, description="The field and direction to sort results by. Specify a field name followed by ASC or DESC (for example: balance DESC or created_at ASC). Defaults to sorting by disabled_at in descending order."),
    query: Any | None = Field(None, description="The search query text to match against indexed gift card fields including created_at, updated_at, disabled_at, balance, initial_value, amount_spent, email, and last_characters."),
    limit: Any | None = Field(None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50 results."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. Omit to return all fields."),
) -> dict[str, Any] | ToolResult:
    """Search for gift cards using indexed fields like balance, email, or creation date. Results are paginated and can be filtered, sorted, and limited to specific fields."""

    # Construct request model with validation
    try:
        _request = _models.GetGiftCardsSearchRequest(
            query=_models.GetGiftCardsSearchRequestQuery(order=order, query=query, limit=limit, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_gift_cards: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/gift_cards/search.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_gift_cards")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_gift_cards", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_gift_cards",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: plus, giftcard, plus/giftcard, latest_api_version
@mcp.tool()
async def get_gift_card(gift_card_id: str = Field(..., description="The unique identifier of the gift card to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a single gift card by its unique identifier. Use this to fetch gift card information such as balance, status, and creation date."""

    # Construct request model with validation
    try:
        _request = _models.GetGiftCardsParamGiftCardIdRequest(
            path=_models.GetGiftCardsParamGiftCardIdRequestPath(gift_card_id=gift_card_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_gift_card: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/gift_cards/{gift_card_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/gift_cards/{gift_card_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_gift_card")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_gift_card", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_gift_card",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: plus, giftcard, plus/giftcard, latest_api_version
@mcp.tool()
async def update_gift_card(gift_card_id: str = Field(..., description="The unique identifier of the gift card to update.")) -> dict[str, Any] | ToolResult:
    """Updates an existing gift card's expiry date, note, and template suffix. The gift card's balance cannot be modified through the API."""

    # Construct request model with validation
    try:
        _request = _models.UpdateGiftCardsParamGiftCardIdRequest(
            path=_models.UpdateGiftCardsParamGiftCardIdRequestPath(gift_card_id=gift_card_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_gift_card: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/gift_cards/{gift_card_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/gift_cards/{gift_card_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_gift_card")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_gift_card", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_gift_card",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: plus, giftcard, plus/giftcard, latest_api_version
@mcp.tool()
async def disable_gift_card(gift_card_id: str = Field(..., description="The unique identifier of the gift card to disable.")) -> dict[str, Any] | ToolResult:
    """Permanently disables a gift card, preventing further use. This action cannot be reversed."""

    # Construct request model with validation
    try:
        _request = _models.CreateGiftCardsParamGiftCardIdDisableRequest(
            path=_models.CreateGiftCardsParamGiftCardIdDisableRequestPath(gift_card_id=gift_card_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for disable_gift_card: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/gift_cards/{gift_card_id}/disable.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/gift_cards/{gift_card_id}/disable.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("disable_gift_card")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("disable_gift_card", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="disable_gift_card",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: inventory, inventoryitem, inventory/inventoryitem, latest_api_version
@mcp.tool()
async def list_inventory_items(
    limit: Any | None = Field(None, description="Maximum number of results to return per request, between 1 and 250 items. Defaults to 50 if not specified."),
    ids: str | None = Field(None, description="Filter results to specific inventory items by their numeric IDs. Provide one or more comma-separated integer IDs."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of inventory items. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""

    # Construct request model with validation
    try:
        _request = _models.GetInventoryItemsRequest(
            query=_models.GetInventoryItemsRequestQuery(limit=limit, ids=ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_inventory_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/inventory_items.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_inventory_items")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_inventory_items", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_inventory_items",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: inventory, inventoryitem, inventory/inventoryitem, latest_api_version
@mcp.tool()
async def get_inventory_item(inventory_item_id: str = Field(..., description="The unique identifier of the inventory item to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a single inventory item by its unique identifier. Use this to fetch detailed inventory information for a specific product variant."""

    # Construct request model with validation
    try:
        _request = _models.GetInventoryItemsParamInventoryItemIdRequest(
            path=_models.GetInventoryItemsParamInventoryItemIdRequestPath(inventory_item_id=inventory_item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_inventory_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/inventory_items/{inventory_item_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/inventory_items/{inventory_item_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_inventory_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_inventory_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_inventory_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: inventory, inventoryitem, inventory/inventoryitem, latest_api_version
@mcp.tool()
async def update_inventory_item(inventory_item_id: str = Field(..., description="The unique identifier of the inventory item to update. This ID is assigned by Shopify when the inventory item is created.")) -> dict[str, Any] | ToolResult:
    """Updates an existing inventory item in your store's inventory system. Use this to modify properties like SKU, tracked status, or other inventory attributes for a specific item."""

    # Construct request model with validation
    try:
        _request = _models.UpdateInventoryItemsParamInventoryItemIdRequest(
            path=_models.UpdateInventoryItemsParamInventoryItemIdRequestPath(inventory_item_id=inventory_item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_inventory_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/inventory_items/{inventory_item_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/inventory_items/{inventory_item_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_inventory_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_inventory_item", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_inventory_item",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: inventory, inventorylevel, inventory/inventorylevel, latest_api_version
@mcp.tool()
async def list_inventory_levels(
    inventory_item_ids: Any | None = Field(None, description="Comma-separated list of inventory item IDs to filter results. Maximum of 50 IDs per request."),
    location_ids: Any | None = Field(None, description="Comma-separated list of location IDs to filter results. Maximum of 50 IDs per request. Use the Location resource to find location IDs."),
    limit: Any | None = Field(None, description="Maximum number of results to return per request. Defaults to 50 if not specified; maximum allowed is 250."),
) -> dict[str, Any] | ToolResult:
    """Retrieves inventory levels across locations and inventory items. You must filter by at least one inventory item ID or location ID to retrieve results."""

    # Construct request model with validation
    try:
        _request = _models.GetInventoryLevelsRequest(
            query=_models.GetInventoryLevelsRequestQuery(inventory_item_ids=inventory_item_ids, location_ids=location_ids, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_inventory_levels: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/inventory_levels.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_inventory_levels")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_inventory_levels", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_inventory_levels",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: inventory, inventorylevel, inventory/inventorylevel, latest_api_version
@mcp.tool()
async def delete_inventory_level(
    inventory_item_id: int | None = Field(None, description="The unique identifier of the inventory item whose level should be deleted."),
    location_id: int | None = Field(None, description="The unique identifier of the location where the inventory level should be removed."),
) -> dict[str, Any] | ToolResult:
    """Removes an inventory level for a specific inventory item at a location. This disconnects the item from that location; note that every inventory item must retain at least one inventory level, so connect the item to another location before deleting its last level."""

    # Construct request model with validation
    try:
        _request = _models.DeleteInventoryLevelsRequest(
            query=_models.DeleteInventoryLevelsRequestQuery(inventory_item_id=inventory_item_id, location_id=location_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_inventory_level: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/inventory_levels.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_inventory_level")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_inventory_level", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_inventory_level",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: inventory, location, inventory/location, latest_api_version
@mcp.tool()
async def list_locations() -> dict[str, Any] | ToolResult:
    """Retrieves all inventory locations for the store. Use this to get a complete list of physical and virtual locations where inventory is managed."""

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/locations.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_locations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_locations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_locations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: inventory, location, inventory/location, latest_api_version
@mcp.tool()
async def get_locations_count() -> dict[str, Any] | ToolResult:
    """Retrieves the total count of locations in the Shopify store. Use this to determine how many physical or virtual locations exist without fetching full location details."""

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/locations/count.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_locations_count")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_locations_count", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_locations_count",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: inventory, location, inventory/location, latest_api_version
@mcp.tool()
async def get_location(location_id: str = Field(..., description="The unique identifier of the location to retrieve. This ID is assigned by Shopify and is required to fetch the specific location's details.")) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific inventory location by its ID. Use this to fetch location details such as address, fulfillment capabilities, and operational status."""

    # Construct request model with validation
    try:
        _request = _models.GetLocationsParamLocationIdRequest(
            path=_models.GetLocationsParamLocationIdRequestPath(location_id=location_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_location: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/locations/{location_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/locations/{location_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_location")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_location", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_location",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: inventory, location, inventory/location, latest_api_version
@mcp.tool()
async def list_inventory_levels_for_location(location_id: str = Field(..., description="The unique identifier of the location for which to retrieve inventory levels.")) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of inventory levels for a specific location. Results are paginated using link headers in the response; use the provided links to navigate pages rather than query parameters."""

    # Construct request model with validation
    try:
        _request = _models.GetLocationsParamLocationIdInventoryLevelsRequest(
            path=_models.GetLocationsParamLocationIdInventoryLevelsRequestPath(location_id=location_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_inventory_levels_for_location: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/locations/{location_id}/inventory_levels.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/locations/{location_id}/inventory_levels.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_inventory_levels_for_location")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_inventory_levels_for_location", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_inventory_levels_for_location",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: metafield, latest_api_version
@mcp.tool()
async def list_metafields_for_product_image(
    metafield_owner_id: int | None = Field(None, alias="metafieldowner_id", description="The unique identifier of the Product Image resource that owns the metafields. Required when filtering metafields by a specific image."),
    metafield_owner_resource: str | None = Field(None, alias="metafieldowner_resource", description="The resource type that owns the metafields. Should be set to 'product_image' to retrieve metafields for Product Image resources."),
) -> dict[str, Any] | ToolResult:
    """Retrieves metafields associated with a specific Product Image resource. Use owner_id and owner_resource to filter metafields for a particular image."""

    # Construct request model with validation
    try:
        _request = _models.GetMetafieldsRequest(
            query=_models.GetMetafieldsRequestQuery(metafield_owner_id=metafield_owner_id, metafield_owner_resource=metafield_owner_resource)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_metafields_for_product_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/metafields.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_metafields_for_product_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_metafields_for_product_image", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_metafields_for_product_image",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: metafield, latest_api_version
@mcp.tool()
async def get_metafields_count() -> dict[str, Any] | ToolResult:
    """Retrieves the total count of metafields associated with a resource. Use this to determine how many custom metadata fields exist without fetching the full list."""

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/metafields/count.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metafields_count")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metafields_count", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metafields_count",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: metafield, latest_api_version
@mcp.tool()
async def get_metafield(
    metafield_id: str = Field(..., description="The unique identifier of the metafield to retrieve."),
    fields: Any | None = Field(None, description="Optionally limit the response to specific fields by providing a comma-separated list of field names. Reduces payload size when only certain metafield properties are needed."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single metafield by its ID. Use this to fetch detailed information about a specific metafield attached to a resource."""

    # Construct request model with validation
    try:
        _request = _models.GetMetafieldsParamMetafieldIdRequest(
            path=_models.GetMetafieldsParamMetafieldIdRequestPath(metafield_id=metafield_id),
            query=_models.GetMetafieldsParamMetafieldIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_metafield: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/metafields/{metafield_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/metafields/{metafield_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_metafield")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_metafield", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_metafield",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: metafield, latest_api_version
@mcp.tool()
async def update_metafield(metafield_id: str = Field(..., description="The unique identifier of the metafield to update. This ID is returned when a metafield is created and is required to target the specific metafield for modification.")) -> dict[str, Any] | ToolResult:
    """Updates an existing metafield by ID. Modify metafield properties such as namespace, key, value, and type."""

    # Construct request model with validation
    try:
        _request = _models.UpdateMetafieldsParamMetafieldIdRequest(
            path=_models.UpdateMetafieldsParamMetafieldIdRequestPath(metafield_id=metafield_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_metafield: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/metafields/{metafield_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/metafields/{metafield_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_metafield")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_metafield", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_metafield",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: metafield, latest_api_version
@mcp.tool()
async def delete_metafield(metafield_id: str = Field(..., description="The unique identifier of the metafield to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a metafield by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteMetafieldsParamMetafieldIdRequest(
            path=_models.DeleteMetafieldsParamMetafieldIdRequestPath(metafield_id=metafield_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_metafield: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/metafields/{metafield_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/metafields/{metafield_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_metafield")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_metafield", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_metafield",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillmentorder, shipping-and-fulfillment/fulfillmentorder, latest_api_version
@mcp.tool()
async def list_fulfillment_orders(order_id: str = Field(..., description="The unique identifier of the order for which to retrieve fulfillment orders.")) -> dict[str, Any] | ToolResult:
    """Retrieves all fulfillment orders associated with a specific order, including their current status and fulfillment details."""

    # Construct request model with validation
    try:
        _request = _models.GetOrdersParamOrderIdFulfillmentOrdersRequest(
            path=_models.GetOrdersParamOrderIdFulfillmentOrdersRequestPath(order_id=order_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_fulfillment_orders: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/fulfillment_orders.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/fulfillment_orders.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_fulfillment_orders")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_fulfillment_orders", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_fulfillment_orders",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillment, shipping-and-fulfillment/fulfillment, latest_api_version
@mcp.tool()
async def list_order_fulfillments(
    order_id: str = Field(..., description="The unique identifier of the order for which to retrieve fulfillments."),
    fields: Any | None = Field(None, description="A comma-separated list of specific fields to include in the response. Omit to return all fields."),
    limit: Any | None = Field(None, description="Maximum number of fulfillments to return per request. Defaults to 50; maximum allowed is 250."),
    since_id: Any | None = Field(None, description="Restrict results to fulfillments created after the specified fulfillment ID, useful for pagination when combined with link headers."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all fulfillments associated with a specific order. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""

    # Construct request model with validation
    try:
        _request = _models.GetOrdersParamOrderIdFulfillmentsRequest(
            path=_models.GetOrdersParamOrderIdFulfillmentsRequestPath(order_id=order_id),
            query=_models.GetOrdersParamOrderIdFulfillmentsRequestQuery(fields=fields, limit=limit, since_id=since_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_order_fulfillments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/fulfillments.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/fulfillments.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_order_fulfillments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_order_fulfillments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_order_fulfillments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillment, shipping-and-fulfillment/fulfillment, latest_api_version
@mcp.tool()
async def create_fulfillment_for_order(order_id: str = Field(..., description="The unique identifier of the order for which to create the fulfillment. Required to specify which order's line items should be fulfilled.")) -> dict[str, Any] | ToolResult:
    """Create a fulfillment for specified line items in an order. The fulfillment status depends on the fulfillment service type: manual/custom services set status immediately, while external services queue the fulfillment with pending status until processed. All line items in a fulfillment must use the same fulfillment service, and refunded orders or line items cannot be fulfilled."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrdersParamOrderIdFulfillmentsRequest(
            path=_models.CreateOrdersParamOrderIdFulfillmentsRequestPath(order_id=order_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_fulfillment_for_order: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/fulfillments.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/fulfillments.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_fulfillment_for_order")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_fulfillment_for_order", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_fulfillment_for_order",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillment, shipping-and-fulfillment/fulfillment, latest_api_version
@mcp.tool()
async def get_fulfillment_count(order_id: str = Field(..., description="The unique identifier of the order for which to retrieve the fulfillment count.")) -> dict[str, Any] | ToolResult:
    """Retrieves the total count of fulfillments associated with a specific order. Useful for understanding fulfillment status and logistics tracking without fetching full fulfillment details."""

    # Construct request model with validation
    try:
        _request = _models.GetOrdersParamOrderIdFulfillmentsCountRequest(
            path=_models.GetOrdersParamOrderIdFulfillmentsCountRequestPath(order_id=order_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_fulfillment_count: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/fulfillments/count.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/fulfillments/count.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_fulfillment_count")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_fulfillment_count", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_fulfillment_count",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillment, shipping-and-fulfillment/fulfillment, latest_api_version
@mcp.tool()
async def get_fulfillment(
    order_id: str = Field(..., description="The unique identifier of the order containing the fulfillment."),
    fulfillment_id: str = Field(..., description="The unique identifier of the fulfillment to retrieve."),
    fields: Any | None = Field(None, description="Comma-separated list of specific fields to include in the response. If omitted, all fields are returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific fulfillment for an order, including tracking and line item fulfillment status."""

    # Construct request model with validation
    try:
        _request = _models.GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest(
            path=_models.GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath(order_id=order_id, fulfillment_id=fulfillment_id),
            query=_models.GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_fulfillment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_fulfillment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_fulfillment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_fulfillment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillment, shipping-and-fulfillment/fulfillment, latest_api_version
@mcp.tool()
async def update_fulfillment(
    order_id: str = Field(..., description="The unique identifier of the order containing the fulfillment to update."),
    fulfillment_id: str = Field(..., description="The unique identifier of the fulfillment to update."),
) -> dict[str, Any] | ToolResult:
    """Update fulfillment details for a specific order, such as tracking information, status, or line items included in the shipment."""

    # Construct request model with validation
    try:
        _request = _models.UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest(
            path=_models.UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath(order_id=order_id, fulfillment_id=fulfillment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_fulfillment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_fulfillment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_fulfillment", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_fulfillment",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillment, shipping-and-fulfillment/fulfillment, latest_api_version
@mcp.tool()
async def cancel_fulfillment_order_2(
    order_id: str = Field(..., description="The unique identifier of the order containing the fulfillment to cancel."),
    fulfillment_id: str = Field(..., description="The unique identifier of the fulfillment to cancel within the specified order."),
) -> dict[str, Any] | ToolResult:
    """Cancel an active fulfillment for a specific order. This operation marks the fulfillment as cancelled and may trigger related notifications depending on the fulfillment state."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequest(
            path=_models.CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequestPath(order_id=order_id, fulfillment_id=fulfillment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for cancel_fulfillment_order_2: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}/cancel.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}/cancel.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("cancel_fulfillment_order_2")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("cancel_fulfillment_order_2", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="cancel_fulfillment_order_2",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillment, shipping-and-fulfillment/fulfillment, latest_api_version
@mcp.tool()
async def complete_fulfillment(
    order_id: str = Field(..., description="The unique identifier of the order containing the fulfillment to be completed."),
    fulfillment_id: str = Field(..., description="The unique identifier of the fulfillment to mark as complete."),
) -> dict[str, Any] | ToolResult:
    """Mark a fulfillment as complete, indicating that all items in the fulfillment have been shipped and are on their way to the customer."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequest(
            path=_models.CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequestPath(order_id=order_id, fulfillment_id=fulfillment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for complete_fulfillment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}/complete.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}/complete.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("complete_fulfillment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("complete_fulfillment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="complete_fulfillment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillmentevent, shipping-and-fulfillment/fulfillmentevent, latest_api_version
@mcp.tool()
async def list_fulfillment_events(
    order_id: str = Field(..., description="The unique identifier of the order containing the fulfillment."),
    fulfillment_id: str = Field(..., description="The unique identifier of the fulfillment within the specified order."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all events associated with a specific fulfillment for an order, including status updates and tracking information."""

    # Construct request model with validation
    try:
        _request = _models.GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest(
            path=_models.GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath(order_id=order_id, fulfillment_id=fulfillment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_fulfillment_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}/events.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}/events.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_fulfillment_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_fulfillment_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_fulfillment_events",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillmentevent, shipping-and-fulfillment/fulfillmentevent, latest_api_version
@mcp.tool()
async def create_fulfillment_event(
    order_id: str = Field(..., description="The unique identifier of the order containing the fulfillment."),
    fulfillment_id: str = Field(..., description="The unique identifier of the fulfillment for which to create the event."),
) -> dict[str, Any] | ToolResult:
    """Creates a fulfillment event for a specific fulfillment within an order. Fulfillment events track status changes and milestones in the fulfillment lifecycle."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest(
            path=_models.CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath(order_id=order_id, fulfillment_id=fulfillment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_fulfillment_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}/events.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}/events.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_fulfillment_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_fulfillment_event", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_fulfillment_event",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillmentevent, shipping-and-fulfillment/fulfillmentevent, latest_api_version
@mcp.tool()
async def get_fulfillment_event(
    order_id: str = Field(..., description="The unique identifier of the order containing the fulfillment event."),
    fulfillment_id: str = Field(..., description="The unique identifier of the fulfillment within the order."),
    event_id: str = Field(..., description="The unique identifier of the specific fulfillment event to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific fulfillment event for a given order and fulfillment. Use this to fetch details about a particular event in the fulfillment lifecycle, such as tracking updates or status changes."""

    # Construct request model with validation
    try:
        _request = _models.GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsParamEventIdRequest(
            path=_models.GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsParamEventIdRequestPath(order_id=order_id, fulfillment_id=fulfillment_id, event_id=event_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_fulfillment_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}/events/{event_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}/events/{event_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_fulfillment_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_fulfillment_event", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_fulfillment_event",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillmentevent, shipping-and-fulfillment/fulfillmentevent, latest_api_version
@mcp.tool()
async def delete_fulfillment_event(
    order_id: str = Field(..., description="The unique identifier of the order containing the fulfillment event to delete."),
    fulfillment_id: str = Field(..., description="The unique identifier of the fulfillment within the order that contains the event to delete."),
    event_id: str = Field(..., description="The unique identifier of the fulfillment event to delete."),
) -> dict[str, Any] | ToolResult:
    """Deletes a specific fulfillment event from an order's fulfillment. This removes the event record associated with the fulfillment tracking."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsParamEventIdRequest(
            path=_models.DeleteOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsParamEventIdRequestPath(order_id=order_id, fulfillment_id=fulfillment_id, event_id=event_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_fulfillment_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}/events/{event_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}/events/{event_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_fulfillment_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_fulfillment_event", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_fulfillment_event",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shipping-and-fulfillment, fulfillment, shipping-and-fulfillment/fulfillment, latest_api_version
@mcp.tool()
async def open_fulfillment(
    order_id: str = Field(..., description="The unique identifier of the order containing the fulfillment to be opened."),
    fulfillment_id: str = Field(..., description="The unique identifier of the fulfillment to mark as open."),
) -> dict[str, Any] | ToolResult:
    """Mark a fulfillment as open, allowing it to receive additional items or changes. This transitions the fulfillment to an open state for the specified order."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequest(
            path=_models.CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequestPath(order_id=order_id, fulfillment_id=fulfillment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for open_fulfillment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}/open.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/fulfillments/{fulfillment_id}/open.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("open_fulfillment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("open_fulfillment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="open_fulfillment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: orders, refund, orders/refund, latest_api_version
@mcp.tool()
async def list_order_refunds(
    order_id: str = Field(..., description="The unique identifier of the order for which to retrieve refunds."),
    limit: Any | None = Field(None, description="Maximum number of refunds to return per request, between 1 and 250 (defaults to 50)."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. Omit to return all fields."),
    in_shop_currency: Any | None = Field(None, description="When true, displays monetary amounts in the shop's currency for the underlying transaction (defaults to false)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of refunds for a specific order. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""

    # Construct request model with validation
    try:
        _request = _models.GetOrdersParamOrderIdRefundsRequest(
            path=_models.GetOrdersParamOrderIdRefundsRequestPath(order_id=order_id),
            query=_models.GetOrdersParamOrderIdRefundsRequestQuery(limit=limit, fields=fields, in_shop_currency=in_shop_currency)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_order_refunds: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/refunds.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/refunds.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_order_refunds")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_order_refunds", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_order_refunds",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: orders, refund, orders/refund, latest_api_version
@mcp.tool()
async def create_order_refund(
    order_id: str = Field(..., description="The unique identifier of the order for which to create a refund."),
    notify: Any | None = Field(None, description="Whether to send a refund notification email to the customer."),
    note: Any | None = Field(None, description="An optional note to attach to the refund for internal reference."),
    discrepancy_reason: Any | None = Field(None, description="An optional reason explaining any discrepancy between calculated and actual refund amounts. Valid values are: restock, damage, customer, or other."),
    shipping: Any | None = Field(None, description="Specifies how much shipping to refund. Provide either full_refund (boolean) to refund all remaining shipping, or amount (decimal) to refund a specific shipping amount. The amount takes precedence if both are provided."),
    refund_line_items: Any | None = Field(None, description="A list of line items to refund, each specifying the line_item_id, quantity to refund, restock_type (no_restock, cancel, or return), and location_id (required for cancel or return restock types). The location_id determines where restocked items are added back to inventory."),
    transactions: Any | None = Field(None, description="A list of transactions to process as refunds. These should be obtained from the calculate endpoint to ensure accuracy."),
    currency: Any | None = Field(None, description="The three-letter ISO 4217 currency code for the refund. Required for multi-currency orders when an amount property is provided."),
) -> dict[str, Any] | ToolResult:
    """Creates a refund for an order. Use the calculate endpoint first to determine the correct transactions to submit. For multi-currency orders, the currency property is required whenever an amount is specified."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrdersParamOrderIdRefundsRequest(
            path=_models.CreateOrdersParamOrderIdRefundsRequestPath(order_id=order_id),
            query=_models.CreateOrdersParamOrderIdRefundsRequestQuery(notify=notify, note=note, discrepancy_reason=discrepancy_reason, shipping=shipping, refund_line_items=refund_line_items, transactions=transactions, currency=currency)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_order_refund: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/refunds.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/refunds.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_order_refund")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_order_refund", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_order_refund",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: orders, refund, orders/refund, latest_api_version
@mcp.tool()
async def calculate_order_refund(
    order_id: str = Field(..., description="The unique identifier of the order for which to calculate the refund."),
    shipping: Any | None = Field(None, description="Shipping refund configuration. Specify either full_refund to refund all remaining shipping costs, or amount to refund a specific shipping amount. The amount property takes precedence over full_refund if both are provided. Required for multi-currency orders when amount is specified."),
    refund_line_items: Any | None = Field(None, description="A list of line items to refund, each specifying the line item ID, quantity to refund, and how the refund affects inventory (no_restock, cancel, or return). Optionally specify the location_id where items should be restocked; if not provided, the system will suggest a suitable location for return or cancel operations. Use already_stocked to indicate whether the item is already in stock at the location."),
    currency: Any | None = Field(None, description="The three-letter ISO 4217 currency code for the refund amount. Required whenever a shipping amount is specified for multi-currency orders."),
) -> dict[str, Any] | ToolResult:
    """Calculates refund transactions for an order based on specified line items, quantities, restock instructions, and shipping costs. Use this endpoint to generate accurate refund details before creating the actual refund. The response includes suggested refund transactions that must be converted to actual refunds when submitting the refund creation request."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrdersParamOrderIdRefundsCalculateRequest(
            path=_models.CreateOrdersParamOrderIdRefundsCalculateRequestPath(order_id=order_id),
            query=_models.CreateOrdersParamOrderIdRefundsCalculateRequestQuery(shipping=shipping, refund_line_items=refund_line_items, currency=currency)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_order_refund: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/refunds/calculate.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/refunds/calculate.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_order_refund")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_order_refund", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_order_refund",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: orders, refund, orders/refund, latest_api_version
@mcp.tool()
async def get_refund(
    order_id: str = Field(..., description="The unique identifier of the order containing the refund."),
    refund_id: str = Field(..., description="The unique identifier of the refund to retrieve."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields are returned, reducing payload size."),
    in_shop_currency: Any | None = Field(None, description="When enabled, monetary amounts in the response are displayed in the shop's currency rather than the transaction currency. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific refund associated with an order. Use this to view refund information including amounts, line items, and status."""

    # Construct request model with validation
    try:
        _request = _models.GetOrdersParamOrderIdRefundsParamRefundIdRequest(
            path=_models.GetOrdersParamOrderIdRefundsParamRefundIdRequestPath(order_id=order_id, refund_id=refund_id),
            query=_models.GetOrdersParamOrderIdRefundsParamRefundIdRequestQuery(fields=fields, in_shop_currency=in_shop_currency)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_refund: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/refunds/{refund_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/refunds/{refund_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_refund")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_refund", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_refund",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: orders, order-risk, orders/order-risk, latest_api_version
@mcp.tool()
async def list_order_risks(order_id: str = Field(..., description="The unique identifier of the order for which to retrieve risk assessments.")) -> dict[str, Any] | ToolResult:
    """Retrieves all fraud and risk assessments associated with a specific order. Use this to review potential risks flagged by Shopify's risk analysis system for an order."""

    # Construct request model with validation
    try:
        _request = _models.GetOrdersParamOrderIdRisksRequest(
            path=_models.GetOrdersParamOrderIdRisksRequestPath(order_id=order_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_order_risks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/risks.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/risks.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_order_risks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_order_risks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_order_risks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: orders, order-risk, orders/order-risk, latest_api_version
@mcp.tool()
async def create_order_risk(order_id: str = Field(..., description="The unique identifier of the order for which the risk is being created.")) -> dict[str, Any] | ToolResult:
    """Creates a risk assessment record for an order, allowing merchants to flag potential issues or concerns associated with the order."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrdersParamOrderIdRisksRequest(
            path=_models.CreateOrdersParamOrderIdRisksRequestPath(order_id=order_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_order_risk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/risks.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/risks.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_order_risk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_order_risk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_order_risk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: orders, order-risk, orders/order-risk, latest_api_version
@mcp.tool()
async def get_order_risk(
    order_id: str = Field(..., description="The unique identifier of the order containing the risk assessment."),
    risk_id: str = Field(..., description="The unique identifier of the specific risk assessment to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single risk assessment associated with an order. Use this to fetch detailed information about a specific fraud or security risk flagged on an order."""

    # Construct request model with validation
    try:
        _request = _models.GetOrdersParamOrderIdRisksParamRiskIdRequest(
            path=_models.GetOrdersParamOrderIdRisksParamRiskIdRequestPath(order_id=order_id, risk_id=risk_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_order_risk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/risks/{risk_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/risks/{risk_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_order_risk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_order_risk", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_order_risk",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: orders, order-risk, orders/order-risk, latest_api_version
@mcp.tool()
async def update_order_risk(
    order_id: str = Field(..., description="The unique identifier of the order containing the risk to be updated."),
    risk_id: str = Field(..., description="The unique identifier of the order risk to be updated."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing order risk for a specific order. Note that you cannot modify an order risk that was created by another application."""

    # Construct request model with validation
    try:
        _request = _models.UpdateOrdersParamOrderIdRisksParamRiskIdRequest(
            path=_models.UpdateOrdersParamOrderIdRisksParamRiskIdRequestPath(order_id=order_id, risk_id=risk_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_order_risk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/risks/{risk_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/risks/{risk_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_order_risk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_order_risk", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_order_risk",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: orders, order-risk, orders/order-risk, latest_api_version
@mcp.tool()
async def delete_order_risk(
    order_id: str = Field(..., description="The unique identifier of the order containing the risk to delete."),
    risk_id: str = Field(..., description="The unique identifier of the risk assessment to delete."),
) -> dict[str, Any] | ToolResult:
    """Deletes a fraud risk assessment associated with an order. Note that you can only delete risks created by your application; risks created by other applications cannot be removed."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOrdersParamOrderIdRisksParamRiskIdRequest(
            path=_models.DeleteOrdersParamOrderIdRisksParamRiskIdRequestPath(order_id=order_id, risk_id=risk_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_order_risk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/orders/{order_id}/risks/{risk_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/orders/{order_id}/risks/{risk_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_order_risk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_order_risk", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_order_risk",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: store-properties, policy, store-properties/policy, latest_api_version
@mcp.tool()
async def list_policies() -> dict[str, Any] | ToolResult:
    """Retrieves all policies configured for the shop, including return, privacy, shipping, and other store policies."""

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/policies.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_policies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_policies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_policies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: discounts, discountcode, discounts/discountcode, latest_api_version
@mcp.tool()
async def create_discount_codes_batch(price_rule_id: str = Field(..., description="The unique identifier of the price rule for which discount codes will be created.")) -> dict[str, Any] | ToolResult:
    """Asynchronously create up to 100 discount codes for a price rule in a single batch job. Returns a discount code creation job object that can be monitored for completion status, import counts, and validation errors."""

    # Construct request model with validation
    try:
        _request = _models.CreatePriceRulesParamPriceRuleIdBatchRequest(
            path=_models.CreatePriceRulesParamPriceRuleIdBatchRequestPath(price_rule_id=price_rule_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_discount_codes_batch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/price_rules/{price_rule_id}/batch.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/price_rules/{price_rule_id}/batch.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_discount_codes_batch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_discount_codes_batch", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_discount_codes_batch",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: discounts, discountcode, discounts/discountcode, latest_api_version
@mcp.tool()
async def get_discount_code_batch(
    price_rule_id: str = Field(..., description="The unique identifier of the price rule associated with the discount code batch job."),
    batch_id: str = Field(..., description="The unique identifier of the batch job to retrieve status and results for."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the status and details of a discount code creation job batch for a specific price rule."""

    # Construct request model with validation
    try:
        _request = _models.GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequest(
            path=_models.GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequestPath(price_rule_id=price_rule_id, batch_id=batch_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_discount_code_batch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/price_rules/{price_rule_id}/batch/{batch_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/price_rules/{price_rule_id}/batch/{batch_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_discount_code_batch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_discount_code_batch", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_discount_code_batch",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: discounts, discountcode, discounts/discountcode, latest_api_version
@mcp.tool()
async def list_discount_codes_for_batch(
    price_rule_id: str = Field(..., description="The unique identifier of the price rule that contains the discount code batch job."),
    batch_id: str = Field(..., description="The unique identifier of the batch job for which to retrieve discount codes."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all discount codes generated from a specific batch job within a price rule. Results include successfully created codes (with populated id) and codes that failed during creation (with populated errors)."""

    # Construct request model with validation
    try:
        _request = _models.GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequest(
            path=_models.GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequestPath(price_rule_id=price_rule_id, batch_id=batch_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_discount_codes_for_batch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/price_rules/{price_rule_id}/batch/{batch_id}/discount_codes.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/price_rules/{price_rule_id}/batch/{batch_id}/discount_codes.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_discount_codes_for_batch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_discount_codes_for_batch", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_discount_codes_for_batch",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: discounts, discountcode, discounts/discountcode, latest_api_version
@mcp.tool()
async def list_discount_codes_for_price_rule(price_rule_id: str = Field(..., description="The unique identifier of the price rule for which to retrieve associated discount codes.")) -> dict[str, Any] | ToolResult:
    """Retrieve all discount codes associated with a specific price rule. Results are paginated using link headers in the response; use the provided links to navigate pages rather than query parameters."""

    # Construct request model with validation
    try:
        _request = _models.GetPriceRulesParamPriceRuleIdDiscountCodesRequest(
            path=_models.GetPriceRulesParamPriceRuleIdDiscountCodesRequestPath(price_rule_id=price_rule_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_discount_codes_for_price_rule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/price_rules/{price_rule_id}/discount_codes.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/price_rules/{price_rule_id}/discount_codes.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_discount_codes_for_price_rule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_discount_codes_for_price_rule", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_discount_codes_for_price_rule",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: discounts, discountcode, discounts/discountcode, latest_api_version
@mcp.tool()
async def create_discount_code(price_rule_id: str = Field(..., description="The unique identifier of the price rule to which this discount code will be associated. This price rule must already exist.")) -> dict[str, Any] | ToolResult:
    """Creates a new discount code associated with a specific price rule. The discount code can be used by customers to apply the price rule's discounts during checkout."""

    # Construct request model with validation
    try:
        _request = _models.CreatePriceRulesParamPriceRuleIdDiscountCodesRequest(
            path=_models.CreatePriceRulesParamPriceRuleIdDiscountCodesRequestPath(price_rule_id=price_rule_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_discount_code: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/price_rules/{price_rule_id}/discount_codes.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/price_rules/{price_rule_id}/discount_codes.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_discount_code")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_discount_code", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_discount_code",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: discounts, discountcode, discounts/discountcode, latest_api_version
@mcp.tool()
async def get_discount_code(
    price_rule_id: str = Field(..., description="The unique identifier of the price rule that contains the discount code."),
    discount_code_id: str = Field(..., description="The unique identifier of the discount code to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single discount code associated with a specific price rule. Use this to fetch detailed information about a discount code by its ID."""

    # Construct request model with validation
    try:
        _request = _models.GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(
            path=_models.GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(price_rule_id=price_rule_id, discount_code_id=discount_code_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_discount_code: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/price_rules/{price_rule_id}/discount_codes/{discount_code_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/price_rules/{price_rule_id}/discount_codes/{discount_code_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_discount_code")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_discount_code", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_discount_code",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: discounts, discountcode, discounts/discountcode, latest_api_version
@mcp.tool()
async def update_discount_code(
    price_rule_id: str = Field(..., description="The unique identifier of the price rule that contains the discount code being updated."),
    discount_code_id: str = Field(..., description="The unique identifier of the discount code to update."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing discount code associated with a price rule. Modify discount code properties such as code value, usage limits, and other configurations."""

    # Construct request model with validation
    try:
        _request = _models.UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(
            path=_models.UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(price_rule_id=price_rule_id, discount_code_id=discount_code_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_discount_code: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/price_rules/{price_rule_id}/discount_codes/{discount_code_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/price_rules/{price_rule_id}/discount_codes/{discount_code_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_discount_code")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_discount_code", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_discount_code",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: discounts, discountcode, discounts/discountcode, latest_api_version
@mcp.tool()
async def delete_discount_code(
    price_rule_id: str = Field(..., description="The unique identifier of the price rule that contains the discount code to be deleted."),
    discount_code_id: str = Field(..., description="The unique identifier of the discount code to be deleted."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific discount code associated with a price rule. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(
            path=_models.DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(price_rule_id=price_rule_id, discount_code_id=discount_code_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_discount_code: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/price_rules/{price_rule_id}/discount_codes/{discount_code_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/price_rules/{price_rule_id}/discount_codes/{discount_code_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_discount_code")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_discount_code", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_discount_code",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, product, products/product, latest_api_version
@mcp.tool()
async def list_products(
    ids: Any | None = Field(None, description="Filter results to only products with IDs in this comma-separated list."),
    limit: Any | None = Field(None, description="Maximum number of products to return per page; defaults to 50 and cannot exceed 250."),
    since_id: Any | None = Field(None, description="Return only products with IDs greater than this value, useful for cursor-based pagination."),
    title: Any | None = Field(None, description="Filter results to products matching this title exactly or partially."),
    vendor: Any | None = Field(None, description="Filter results to products from this vendor."),
    handle: Any | None = Field(None, description="Filter results to products with this handle (URL-friendly identifier)."),
    product_type: Any | None = Field(None, description="Filter results to products of this type."),
    status: Any | None = Field(None, description="Filter results by product status: active (default), archived, or draft."),
    collection_id: Any | None = Field(None, description="Filter results to products in this collection by collection ID."),
    published_status: Any | None = Field(None, description="Filter results by publication status: published, unpublished, or any (default)."),
    fields: Any | None = Field(None, description="Return only specified fields as a comma-separated list; omit to return all fields."),
    presentment_currencies: Any | None = Field(None, description="Return presentment prices in only these currencies, specified as a comma-separated list of ISO 4217 currency codes."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of products from the store, with support for filtering by various attributes and controlling which fields are returned. Results are paginated using link headers rather than page parameters."""

    # Construct request model with validation
    try:
        _request = _models.GetProductsRequest(
            query=_models.GetProductsRequestQuery(ids=ids, limit=limit, since_id=since_id, title=title, vendor=vendor, handle=handle, product_type=product_type, status=status, collection_id=collection_id, published_status=published_status, fields=fields, presentment_currencies=presentment_currencies)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_products: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/products.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_products")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_products", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_products",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, product, products/product, latest_api_version
@mcp.tool()
async def get_products_count(
    vendor: Any | None = Field(None, description="Filter the count to include only products from a specific vendor."),
    product_type: Any | None = Field(None, description="Filter the count to include only products of a specific product type."),
    collection_id: Any | None = Field(None, description="Filter the count to include only products belonging to a specific collection."),
    published_status: Any | None = Field(None, description="Filter the count by product publication status: 'published' for published products only, 'unpublished' for unpublished products only, or 'any' to include all products regardless of status (default: any)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the total count of products in the store, with optional filtering by vendor, product type, collection, or published status."""

    # Construct request model with validation
    try:
        _request = _models.GetProductsCountRequest(
            query=_models.GetProductsCountRequestQuery(vendor=vendor, product_type=product_type, collection_id=collection_id, published_status=published_status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_products_count: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/products/count.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_products_count")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_products_count", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_products_count",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, product, products/product, latest_api_version
@mcp.tool()
async def get_product(
    product_id: str = Field(..., description="The unique identifier of the product to retrieve."),
    fields: Any | None = Field(None, description="A comma-separated list of specific fields to include in the response. Omit to return all available product fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single product by its ID from the Shopify store. Use this to fetch detailed product information including variants, images, and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetProductsParamProductIdRequest(
            path=_models.GetProductsParamProductIdRequestPath(product_id=product_id),
            query=_models.GetProductsParamProductIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_product: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/products/{product_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/products/{product_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_product")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_product", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_product",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, product, products/product, latest_api_version
@mcp.tool()
async def update_product(product_id: str = Field(..., description="The unique identifier of the product to update.")) -> dict[str, Any] | ToolResult:
    """Updates a product's details, variants, images, and SEO metadata. Use metafields_global_title_tag and metafields_global_description_tag to manage SEO title and description tags."""

    # Construct request model with validation
    try:
        _request = _models.UpdateProductsParamProductIdRequest(
            path=_models.UpdateProductsParamProductIdRequestPath(product_id=product_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_product: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/products/{product_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/products/{product_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_product")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_product", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_product",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, product, products/product, latest_api_version
@mcp.tool()
async def delete_product(product_id: str = Field(..., description="The unique identifier of the product to delete. This is a required string value that identifies which product should be removed.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a product from the store. This action cannot be undone and will remove the product and all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteProductsParamProductIdRequest(
            path=_models.DeleteProductsParamProductIdRequestPath(product_id=product_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_product: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/products/{product_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/products/{product_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_product")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_product", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_product",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, product-image, products/product-image, latest_api_version
@mcp.tool()
async def list_product_images(
    product_id: str = Field(..., description="The unique identifier of the product whose images you want to retrieve."),
    since_id: Any | None = Field(None, description="Filter results to return only images created after the specified image ID. Useful for pagination when combined with limit parameters."),
    fields: Any | None = Field(None, description="Comma-separated list of specific fields to include in the response. Omit to return all available fields for each image."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all images associated with a specific product. Images are returned in the order they appear in the product's image gallery."""

    # Construct request model with validation
    try:
        _request = _models.GetProductsParamProductIdImagesRequest(
            path=_models.GetProductsParamProductIdImagesRequestPath(product_id=product_id),
            query=_models.GetProductsParamProductIdImagesRequestQuery(since_id=since_id, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_product_images: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/products/{product_id}/images.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/products/{product_id}/images.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_product_images")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_product_images", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_product_images",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, product-image, products/product-image, latest_api_version
@mcp.tool()
async def create_product_image(product_id: str = Field(..., description="The unique identifier of the product to which the image will be attached. This product must exist in the store.")) -> dict[str, Any] | ToolResult:
    """Upload and attach a new image to a product. The image will be associated with the specified product and can be used for product display across storefronts."""

    # Construct request model with validation
    try:
        _request = _models.CreateProductsParamProductIdImagesRequest(
            path=_models.CreateProductsParamProductIdImagesRequestPath(product_id=product_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_product_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/products/{product_id}/images.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/products/{product_id}/images.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_product_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_product_image", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_product_image",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, product-image, products/product-image, latest_api_version
@mcp.tool()
async def count_product_images(
    product_id: str = Field(..., description="The unique identifier of the product for which to count images."),
    since_id: Any | None = Field(None, description="Optional filter to count only images with an ID greater than this value, useful for pagination or incremental updates."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the total count of images associated with a specific product. Optionally filter to count only images added after a specified image ID."""

    # Construct request model with validation
    try:
        _request = _models.GetProductsParamProductIdImagesCountRequest(
            path=_models.GetProductsParamProductIdImagesCountRequestPath(product_id=product_id),
            query=_models.GetProductsParamProductIdImagesCountRequestQuery(since_id=since_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for count_product_images: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/products/{product_id}/images/count.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/products/{product_id}/images/count.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("count_product_images")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("count_product_images", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="count_product_images",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, product-image, products/product-image, latest_api_version
@mcp.tool()
async def get_product_image(
    product_id: str = Field(..., description="The unique identifier of the product that contains the image."),
    image_id: str = Field(..., description="The unique identifier of the image to retrieve."),
    fields: Any | None = Field(None, description="Comma-separated list of specific fields to include in the response. If omitted, all fields are returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a single product image by its ID. Returns detailed metadata for the specified image associated with a product."""

    # Construct request model with validation
    try:
        _request = _models.GetProductsParamProductIdImagesParamImageIdRequest(
            path=_models.GetProductsParamProductIdImagesParamImageIdRequestPath(product_id=product_id, image_id=image_id),
            query=_models.GetProductsParamProductIdImagesParamImageIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_product_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/products/{product_id}/images/{image_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/products/{product_id}/images/{image_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_product_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_product_image", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_product_image",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, product-image, products/product-image, latest_api_version
@mcp.tool()
async def update_product_image(
    product_id: str = Field(..., description="The unique identifier of the product that contains the image to be updated."),
    image_id: str = Field(..., description="The unique identifier of the image within the product to be updated."),
) -> dict[str, Any] | ToolResult:
    """Update metadata and properties of an existing product image, such as alt text, position, or other image attributes."""

    # Construct request model with validation
    try:
        _request = _models.UpdateProductsParamProductIdImagesParamImageIdRequest(
            path=_models.UpdateProductsParamProductIdImagesParamImageIdRequestPath(product_id=product_id, image_id=image_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_product_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/products/{product_id}/images/{image_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/products/{product_id}/images/{image_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_product_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_product_image", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_product_image",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, product-image, products/product-image, latest_api_version
@mcp.tool()
async def delete_product_image(
    product_id: str = Field(..., description="The unique identifier of the product containing the image to delete."),
    image_id: str = Field(..., description="The unique identifier of the image to delete from the product."),
) -> dict[str, Any] | ToolResult:
    """Delete a specific image from a product. This removes the image association and makes it unavailable for the product."""

    # Construct request model with validation
    try:
        _request = _models.DeleteProductsParamProductIdImagesParamImageIdRequest(
            path=_models.DeleteProductsParamProductIdImagesParamImageIdRequestPath(product_id=product_id, image_id=image_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_product_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/products/{product_id}/images/{image_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/products/{product_id}/images/{image_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_product_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_product_image", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_product_image",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: billing, recurringapplicationcharge, billing/recurringapplicationcharge, latest_api_version
@mcp.tool()
async def list_recurring_application_charges(
    since_id: Any | None = Field(None, description="Filter results to return only charges created after the specified charge ID, useful for pagination or retrieving newly created charges."),
    fields: Any | None = Field(None, description="Comma-separated list of specific fields to include in the response. Omit to receive all available fields for each charge."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of all recurring application charges for the store. Use this to view subscription-based charges associated with your app."""

    # Construct request model with validation
    try:
        _request = _models.GetRecurringApplicationChargesRequest(
            query=_models.GetRecurringApplicationChargesRequestQuery(since_id=since_id, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_recurring_application_charges: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/recurring_application_charges.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_recurring_application_charges")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_recurring_application_charges", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_recurring_application_charges",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: billing, recurringapplicationcharge, billing/recurringapplicationcharge, latest_api_version
@mcp.tool()
async def get_recurring_application_charge(
    recurring_application_charge_id: str = Field(..., description="The unique identifier of the recurring application charge to retrieve."),
    fields: Any | None = Field(None, description="A comma-separated list of specific fields to include in the response. Omit to return all available fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a single recurring application charge by its ID. Use this to fetch current status, pricing, and other metadata for a specific recurring charge."""

    # Construct request model with validation
    try:
        _request = _models.GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequest(
            path=_models.GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath(recurring_application_charge_id=recurring_application_charge_id),
            query=_models.GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_recurring_application_charge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/recurring_application_charges/{recurring_application_charge_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/recurring_application_charges/{recurring_application_charge_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_recurring_application_charge")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_recurring_application_charge", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_recurring_application_charge",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: billing, recurringapplicationcharge, billing/recurringapplicationcharge, latest_api_version
@mcp.tool()
async def delete_recurring_application_charge(recurring_application_charge_id: str = Field(..., description="The unique identifier of the recurring application charge to cancel. This ID is returned when the charge is created.")) -> dict[str, Any] | ToolResult:
    """Cancels an active recurring application charge for the store. This operation permanently removes the charge and stops any future billing cycles associated with it."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequest(
            path=_models.DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath(recurring_application_charge_id=recurring_application_charge_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_recurring_application_charge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/recurring_application_charges/{recurring_application_charge_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/recurring_application_charges/{recurring_application_charge_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_recurring_application_charge")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_recurring_application_charge", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_recurring_application_charge",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: billing, recurringapplicationcharge, billing/recurringapplicationcharge, latest_api_version
@mcp.tool()
async def update_recurring_application_charge_capped_amount(
    recurring_application_charge_id: str = Field(..., description="The unique identifier of the recurring application charge to update. This must be an active charge."),
    recurring_application_charge_capped_amount: int | None = Field(None, alias="recurring_application_chargecapped_amount", description="The new maximum billing cap amount for the recurring charge, specified as a monetary value in the store's currency."),
) -> dict[str, Any] | ToolResult:
    """Updates the capped amount of an active recurring application charge. This allows you to modify the maximum billing cap for an existing charge without canceling and recreating it."""

    # Construct request model with validation
    try:
        _request = _models.UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequest(
            path=_models.UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestPath(recurring_application_charge_id=recurring_application_charge_id),
            query=_models.UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestQuery(recurring_application_charge_capped_amount=recurring_application_charge_capped_amount)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_recurring_application_charge_capped_amount: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/recurring_application_charges/{recurring_application_charge_id}/customize.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/recurring_application_charges/{recurring_application_charge_id}/customize.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_recurring_application_charge_capped_amount")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_recurring_application_charge_capped_amount", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_recurring_application_charge_capped_amount",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: billing, usagecharge, billing/usagecharge, latest_api_version
@mcp.tool()
async def list_usage_charges_for_recurring_application_charge(
    recurring_application_charge_id: str = Field(..., description="The unique identifier of the recurring application charge for which to retrieve usage charges."),
    fields: Any | None = Field(None, description="A comma-separated list of specific fields to include in the response. Omit to return all available fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all usage charges associated with a specific recurring application charge. Usage charges represent variable fees billed on top of a recurring application charge."""

    # Construct request model with validation
    try:
        _request = _models.GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest(
            path=_models.GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath(recurring_application_charge_id=recurring_application_charge_id),
            query=_models.GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_usage_charges_for_recurring_application_charge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/recurring_application_charges/{recurring_application_charge_id}/usage_charges.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/recurring_application_charges/{recurring_application_charge_id}/usage_charges.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_usage_charges_for_recurring_application_charge")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_usage_charges_for_recurring_application_charge", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_usage_charges_for_recurring_application_charge",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: billing, usagecharge, billing/usagecharge, latest_api_version
@mcp.tool()
async def create_usage_charge_for_recurring_application_charge(recurring_application_charge_id: str = Field(..., description="The unique identifier of the recurring application charge to which this usage charge will be applied.")) -> dict[str, Any] | ToolResult:
    """Creates a usage charge against an existing recurring application charge. Usage charges allow you to bill merchants for variable consumption on top of their recurring subscription."""

    # Construct request model with validation
    try:
        _request = _models.CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest(
            path=_models.CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath(recurring_application_charge_id=recurring_application_charge_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_usage_charge_for_recurring_application_charge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/recurring_application_charges/{recurring_application_charge_id}/usage_charges.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/recurring_application_charges/{recurring_application_charge_id}/usage_charges.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_usage_charge_for_recurring_application_charge")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_usage_charge_for_recurring_application_charge", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_usage_charge_for_recurring_application_charge",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: billing, usagecharge, billing/usagecharge, latest_api_version
@mcp.tool()
async def get_usage_charge(
    recurring_application_charge_id: str = Field(..., description="The unique identifier of the recurring application charge that contains the usage charge."),
    usage_charge_id: str = Field(..., description="The unique identifier of the usage charge to retrieve."),
    fields: Any | None = Field(None, description="A comma-separated list of specific fields to include in the response. Omit to return all available fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single usage charge associated with a recurring application charge. Use this to fetch details about a specific metered billing charge."""

    # Construct request model with validation
    try:
        _request = _models.GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequest(
            path=_models.GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequestPath(recurring_application_charge_id=recurring_application_charge_id, usage_charge_id=usage_charge_id),
            query=_models.GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_usage_charge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/recurring_application_charges/{recurring_application_charge_id}/usage_charges/{usage_charge_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/recurring_application_charges/{recurring_application_charge_id}/usage_charges/{usage_charge_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_usage_charge")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_usage_charge", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_usage_charge",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, redirect, online-store/redirect, latest_api_version
@mcp.tool()
async def list_redirects(
    limit: Any | None = Field(None, description="Maximum number of redirects to return per request. Defaults to 50 and cannot exceed 250."),
    since_id: Any | None = Field(None, description="Filter results to return only redirects with IDs greater than this value, useful for cursor-based pagination."),
    path: Any | None = Field(None, description="Filter results to show only redirects matching the specified source path."),
    target: Any | None = Field(None, description="Filter results to show only redirects pointing to the specified target URL."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. Omit to return all fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of URL redirects configured in the store. Results are paginated using cursor-based links provided in response headers."""

    # Construct request model with validation
    try:
        _request = _models.GetRedirectsRequest(
            query=_models.GetRedirectsRequestQuery(limit=limit, since_id=since_id, path=path, target=target, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_redirects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/redirects.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_redirects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_redirects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_redirects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, redirect, online-store/redirect, latest_api_version
@mcp.tool()
async def get_redirects_count(
    path: Any | None = Field(None, description="Filter the count to only include redirects with this specific path value."),
    target: Any | None = Field(None, description="Filter the count to only include redirects with this specific target URL."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the total count of URL redirects in the store, with optional filtering by path or target URL."""

    # Construct request model with validation
    try:
        _request = _models.GetRedirectsCountRequest(
            query=_models.GetRedirectsCountRequestQuery(path=path, target=target)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_redirects_count: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/redirects/count.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_redirects_count")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_redirects_count", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_redirects_count",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, redirect, online-store/redirect, latest_api_version
@mcp.tool()
async def get_redirect(
    redirect_id: str = Field(..., description="The unique identifier of the redirect to retrieve."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields are returned, allowing you to optimize response payload size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single redirect by its ID. Use this to fetch detailed information about a specific URL redirect configured in the online store."""

    # Construct request model with validation
    try:
        _request = _models.GetRedirectsParamRedirectIdRequest(
            path=_models.GetRedirectsParamRedirectIdRequestPath(redirect_id=redirect_id),
            query=_models.GetRedirectsParamRedirectIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_redirect: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/redirects/{redirect_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/redirects/{redirect_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_redirect")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_redirect", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_redirect",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, redirect, online-store/redirect, latest_api_version
@mcp.tool()
async def update_redirect(redirect_id: str = Field(..., description="The unique identifier of the redirect to update. This ID is required to locate and modify the specific redirect rule.")) -> dict[str, Any] | ToolResult:
    """Updates an existing redirect configuration in the online store. Modify redirect rules by specifying the redirect ID and providing updated redirect details."""

    # Construct request model with validation
    try:
        _request = _models.UpdateRedirectsParamRedirectIdRequest(
            path=_models.UpdateRedirectsParamRedirectIdRequestPath(redirect_id=redirect_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_redirect: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/redirects/{redirect_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/redirects/{redirect_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_redirect")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_redirect", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_redirect",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, redirect, online-store/redirect, latest_api_version
@mcp.tool()
async def delete_redirect(redirect_id: str = Field(..., description="The unique identifier of the redirect to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a redirect from the online store. Once deleted, the redirect cannot be recovered."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRedirectsParamRedirectIdRequest(
            path=_models.DeleteRedirectsParamRedirectIdRequestPath(redirect_id=redirect_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_redirect: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/redirects/{redirect_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/redirects/{redirect_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_redirect")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_redirect", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_redirect",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, scripttag, online-store/scripttag, latest_api_version
@mcp.tool()
async def list_script_tags(
    limit: Any | None = Field(None, description="Maximum number of results to return per request. Defaults to 50 if not specified; maximum allowed is 250."),
    since_id: Any | None = Field(None, description="Filters results to return only script tags created after the specified tag ID, useful for incremental syncing."),
    fields: Any | None = Field(None, description="Comma-separated list of specific fields to include in the response. Omit to return all available fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all script tags in the store. Results are paginated using cursor-based links provided in the response header."""

    # Construct request model with validation
    try:
        _request = _models.GetScriptTagsRequest(
            query=_models.GetScriptTagsRequestQuery(limit=limit, since_id=since_id, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_script_tags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/script_tags.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_script_tags")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_script_tags", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_script_tags",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, scripttag, online-store/scripttag, latest_api_version
@mcp.tool()
async def get_script_tags_count() -> dict[str, Any] | ToolResult:
    """Retrieves the total count of all script tags in the online store. Useful for understanding the scope of script tag usage without fetching individual records."""

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/script_tags/count.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_script_tags_count")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_script_tags_count", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_script_tags_count",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, scripttag, online-store/scripttag, latest_api_version
@mcp.tool()
async def get_script_tag(
    script_tag_id: str = Field(..., description="The unique identifier of the script tag to retrieve."),
    fields: Any | None = Field(None, description="A comma-separated list of specific fields to include in the response. Omit to return all available fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single script tag by its ID from the online store. Use this to fetch detailed information about a specific script tag resource."""

    # Construct request model with validation
    try:
        _request = _models.GetScriptTagsParamScriptTagIdRequest(
            path=_models.GetScriptTagsParamScriptTagIdRequestPath(script_tag_id=script_tag_id),
            query=_models.GetScriptTagsParamScriptTagIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_script_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/script_tags/{script_tag_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/script_tags/{script_tag_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_script_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_script_tag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_script_tag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, scripttag, online-store/scripttag, latest_api_version
@mcp.tool()
async def update_script_tag(script_tag_id: str = Field(..., description="The unique identifier of the script tag to update. This ID is returned when the script tag is created and is required to target the correct script tag for modification.")) -> dict[str, Any] | ToolResult:
    """Updates an existing script tag in the online store. Modify script tag properties such as source URL, event triggers, or display scope."""

    # Construct request model with validation
    try:
        _request = _models.UpdateScriptTagsParamScriptTagIdRequest(
            path=_models.UpdateScriptTagsParamScriptTagIdRequestPath(script_tag_id=script_tag_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_script_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/script_tags/{script_tag_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/script_tags/{script_tag_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_script_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_script_tag", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_script_tag",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, scripttag, online-store/scripttag, latest_api_version
@mcp.tool()
async def delete_script_tag(script_tag_id: str = Field(..., description="The unique identifier of the script tag to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a script tag from the store. This removes the associated script injection from the online store."""

    # Construct request model with validation
    try:
        _request = _models.DeleteScriptTagsParamScriptTagIdRequest(
            path=_models.DeleteScriptTagsParamScriptTagIdRequestPath(script_tag_id=script_tag_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_script_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/script_tags/{script_tag_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/script_tags/{script_tag_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_script_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_script_tag", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_script_tag",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: store-properties, shippingzone, store-properties/shippingzone, latest_api_version
@mcp.tool()
async def list_shipping_zones(fields: Any | None = Field(None, description="Comma-separated list of specific fields to include in the response. If omitted, all fields are returned.")) -> dict[str, Any] | ToolResult:
    """Retrieve all shipping zones configured for the store. Shipping zones define geographic areas and their associated shipping rates and methods."""

    # Construct request model with validation
    try:
        _request = _models.GetShippingZonesRequest(
            query=_models.GetShippingZonesRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_shipping_zones: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/shipping_zones.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_shipping_zones")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_shipping_zones", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_shipping_zones",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: store-properties, shop, store-properties/shop, latest_api_version
@mcp.tool()
async def get_shop(fields: Any | None = Field(None, description="A comma-separated list of specific fields to include in the response. When omitted, all available fields are returned. Use this to optimize response payload by requesting only the fields your application needs.")) -> dict[str, Any] | ToolResult:
    """Retrieves the shop's configuration and store properties. Use this to access fundamental shop information such as name, currency, timezone, and other store-level settings."""

    # Construct request model with validation
    try:
        _request = _models.GetShopRequest(
            query=_models.GetShopRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_shop: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/shop.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_shop")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_shop", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_shop",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: shopify_payments, balance, shopify_payments/balance, latest_api_version
@mcp.tool()
async def get_shopify_payments_balance() -> dict[str, Any] | ToolResult:
    """Retrieves the current account balance for Shopify Payments, including available funds and pending amounts."""

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/shopify_payments/balance.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_shopify_payments_balance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_shopify_payments_balance", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_shopify_payments_balance",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shopify_payments, payout, shopify_payments/payout, latest_api_version
@mcp.tool()
async def list_shopify_payments_payouts(
    since_id: Any | None = Field(None, description="Filter results to payouts made after the specified payout ID, useful for fetching payouts created since a known reference point."),
    date_min: Any | None = Field(None, description="Filter results to payouts made on or after the specified date (inclusive). Use ISO 8601 format."),
    date_max: Any | None = Field(None, description="Filter results to payouts made on or before the specified date (inclusive). Use ISO 8601 format."),
    status: Any | None = Field(None, description="Filter results to payouts with a specific status (e.g., pending, paid, failed, cancelled)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of all payouts ordered by most recent first. Results are paginated using link headers in the response; use the provided links to navigate pages rather than query parameters."""

    # Construct request model with validation
    try:
        _request = _models.GetShopifyPaymentsPayoutsRequest(
            query=_models.GetShopifyPaymentsPayoutsRequestQuery(since_id=since_id, date_min=date_min, date_max=date_max, status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_shopify_payments_payouts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/shopify_payments/payouts.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_shopify_payments_payouts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_shopify_payments_payouts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_shopify_payments_payouts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: shopify_payments, payout, shopify_payments/payout, latest_api_version
@mcp.tool()
async def get_payout(payout_id: str = Field(..., description="The unique identifier of the payout to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a single Shopify Payments payout by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetShopifyPaymentsPayoutsParamPayoutIdRequest(
            path=_models.GetShopifyPaymentsPayoutsParamPayoutIdRequestPath(payout_id=payout_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_payout: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/shopify_payments/payouts/{payout_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/shopify_payments/payouts/{payout_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_payout")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_payout", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_payout",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, smartcollection, products/smartcollection, latest_api_version
@mcp.tool()
async def list_smart_collections(
    limit: Any | None = Field(None, description="Maximum number of smart collections to return per request. Defaults to 50 if not specified; maximum allowed is 250."),
    ids: Any | None = Field(None, description="Filter results to only smart collections with the specified IDs. Provide as a comma-separated list of numeric IDs."),
    since_id: Any | None = Field(None, description="Return only smart collections with an ID greater than this value. Useful for pagination when not using link headers."),
    title: Any | None = Field(None, description="Filter results to smart collections matching the exact title."),
    product_id: Any | None = Field(None, description="Filter results to only smart collections that contain the specified product ID."),
    handle: Any | None = Field(None, description="Filter results by the smart collection's URL-friendly handle."),
    published_status: Any | None = Field(None, description="Filter results by publication status. Use 'published' for published collections only, 'unpublished' for unpublished only, or 'any' to include all collections regardless of status. Defaults to 'any'."),
    fields: Any | None = Field(None, description="Limit the response to only specified fields. Provide as a comma-separated list of field names to reduce payload size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of smart collections from your store. Results are paginated using link headers in the response; use the provided links to navigate between pages."""

    # Construct request model with validation
    try:
        _request = _models.GetSmartCollectionsRequest(
            query=_models.GetSmartCollectionsRequestQuery(limit=limit, ids=ids, since_id=since_id, title=title, product_id=product_id, handle=handle, published_status=published_status, fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_smart_collections: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/smart_collections.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_smart_collections")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_smart_collections", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_smart_collections",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, smartcollection, products/smartcollection, latest_api_version
@mcp.tool()
async def count_smart_collections(
    title: Any | None = Field(None, description="Filter to smart collections with an exact matching title."),
    product_id: Any | None = Field(None, description="Filter to smart collections that contain the specified product ID."),
    published_status: Any | None = Field(None, description="Filter results by publication status: 'published' for live collections, 'unpublished' for draft collections, or 'any' to include all collections regardless of status. Defaults to 'any'."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the total count of smart collections, optionally filtered by title, product inclusion, or published status."""

    # Construct request model with validation
    try:
        _request = _models.GetSmartCollectionsCountRequest(
            query=_models.GetSmartCollectionsCountRequestQuery(title=title, product_id=product_id, published_status=published_status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for count_smart_collections: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/smart_collections/count.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("count_smart_collections")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("count_smart_collections", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="count_smart_collections",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, smartcollection, products/smartcollection, latest_api_version
@mcp.tool()
async def get_smart_collection(
    smart_collection_id: str = Field(..., description="The unique identifier of the smart collection to retrieve."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields are returned, reducing payload size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single smart collection by ID. Use this to fetch detailed information about a specific smart collection, including its rules, products, and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetSmartCollectionsParamSmartCollectionIdRequest(
            path=_models.GetSmartCollectionsParamSmartCollectionIdRequestPath(smart_collection_id=smart_collection_id),
            query=_models.GetSmartCollectionsParamSmartCollectionIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_smart_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/smart_collections/{smart_collection_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/smart_collections/{smart_collection_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_smart_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_smart_collection", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_smart_collection",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, smartcollection, products/smartcollection, latest_api_version
@mcp.tool()
async def update_smart_collection(smart_collection_id: str = Field(..., description="The unique identifier of the smart collection to update.")) -> dict[str, Any] | ToolResult:
    """Updates an existing smart collection by ID. Modify collection properties such as title, rules, sorting, and visibility settings."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSmartCollectionsParamSmartCollectionIdRequest(
            path=_models.UpdateSmartCollectionsParamSmartCollectionIdRequestPath(smart_collection_id=smart_collection_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_smart_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/smart_collections/{smart_collection_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/smart_collections/{smart_collection_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_smart_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_smart_collection", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_smart_collection",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, smartcollection, products/smartcollection, latest_api_version
@mcp.tool()
async def delete_smart_collection(smart_collection_id: str = Field(..., description="The unique identifier of the smart collection to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently removes a smart collection from the store. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSmartCollectionsParamSmartCollectionIdRequest(
            path=_models.DeleteSmartCollectionsParamSmartCollectionIdRequestPath(smart_collection_id=smart_collection_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_smart_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/smart_collections/{smart_collection_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/smart_collections/{smart_collection_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_smart_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_smart_collection", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_smart_collection",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: products, smartcollection, products/smartcollection, latest_api_version
@mcp.tool()
async def update_smart_collection_order(
    smart_collection_id: str = Field(..., description="The unique identifier of the smart collection to update."),
    products: Any | None = Field(None, description="An ordered array of product IDs to pin at the top of the collection. Pass an empty array to clear any previously pinned products and return to automatic sorting."),
    sort_order: Any | None = Field(None, description="The automatic sorting method to apply to the collection (e.g., alphabetical, price, newest). If not specified, the current sort order is preserved."),
) -> dict[str, Any] | ToolResult:
    """Updates the sorting configuration for products in a smart collection, allowing you to manually order specific products at the top or apply an automatic sort order."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSmartCollectionsParamSmartCollectionIdOrderRequest(
            path=_models.UpdateSmartCollectionsParamSmartCollectionIdOrderRequestPath(smart_collection_id=smart_collection_id),
            query=_models.UpdateSmartCollectionsParamSmartCollectionIdOrderRequestQuery(products=products, sort_order=sort_order)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_smart_collection_order: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/smart_collections/{smart_collection_id}/order.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/smart_collections/{smart_collection_id}/order.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_smart_collection_order")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_smart_collection_order", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_smart_collection_order",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: tendertransaction, latest_api_version
@mcp.tool()
async def list_tender_transactions(
    limit: Any | None = Field(None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50 if not specified."),
    since_id: Any | None = Field(None, description="Retrieve only transactions with an ID greater than this value, useful for resuming pagination or fetching incremental updates."),
    processed_at_min: Any | None = Field(None, description="Filter to show only transactions processed on or after this date (ISO 8601 format)."),
    processed_at_max: Any | None = Field(None, description="Filter to show only transactions processed on or before this date (ISO 8601 format)."),
    order: Any | None = Field(None, description="Sort results by processed_at timestamp in either ascending or descending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of tender transactions. Results are paginated using link headers in the response; use the provided links to navigate through pages rather than manual offset calculations."""

    # Construct request model with validation
    try:
        _request = _models.GetTenderTransactionsRequest(
            query=_models.GetTenderTransactionsRequestQuery(limit=limit, since_id=since_id, processed_at_min=processed_at_min, processed_at_max=processed_at_max, order=order)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tender_transactions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/tender_transactions.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tender_transactions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tender_transactions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tender_transactions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, theme, online-store/theme, latest_api_version
@mcp.tool()
async def list_themes(fields: Any | None = Field(None, description="Comma-separated list of specific theme fields to return in the response. Omit to retrieve all available fields for each theme.")) -> dict[str, Any] | ToolResult:
    """Retrieves a list of all themes available in the Shopify store. Use this to discover theme IDs and metadata for further operations."""

    # Construct request model with validation
    try:
        _request = _models.GetThemesRequest(
            query=_models.GetThemesRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_themes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/themes.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_themes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_themes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_themes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, theme, online-store/theme, latest_api_version
@mcp.tool()
async def get_theme(
    theme_id: str = Field(..., description="The unique identifier of the theme to retrieve."),
    fields: Any | None = Field(None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields are returned, reducing payload size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single theme by its ID from the Shopify online store."""

    # Construct request model with validation
    try:
        _request = _models.GetThemesParamThemeIdRequest(
            path=_models.GetThemesParamThemeIdRequestPath(theme_id=theme_id),
            query=_models.GetThemesParamThemeIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_theme: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/themes/{theme_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/themes/{theme_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_theme")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_theme", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_theme",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, theme, online-store/theme, latest_api_version
@mcp.tool()
async def delete_theme(theme_id: str = Field(..., description="The unique identifier of the theme to delete, returned as a string by the Shopify API.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a theme from the store. The theme must not be the currently active theme."""

    # Construct request model with validation
    try:
        _request = _models.DeleteThemesParamThemeIdRequest(
            path=_models.DeleteThemesParamThemeIdRequestPath(theme_id=theme_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_theme: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/themes/{theme_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/themes/{theme_id}.json"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_theme")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_theme", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_theme",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, asset, online-store/asset, latest_api_version
@mcp.tool()
async def get_theme_asset(
    theme_id: str = Field(..., description="The unique identifier of the theme containing the asset."),
    fields: Any | None = Field(None, description="Comma-separated list of specific fields to include in the response. If omitted, all asset fields are returned."),
    asset_key: str | None = Field(None, alias="assetkey", description="The key path of the asset to retrieve, such as templates/index.liquid or config/settings_data.json. This parameter is required to fetch a specific asset."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single asset file from a theme by its key. Use the asset[key] parameter to specify which asset to retrieve, such as templates/index.liquid or other theme files."""

    # Construct request model with validation
    try:
        _request = _models.GetThemesParamThemeIdAssetsRequest(
            path=_models.GetThemesParamThemeIdAssetsRequestPath(theme_id=theme_id),
            query=_models.GetThemesParamThemeIdAssetsRequestQuery(fields=fields, asset_key=asset_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_theme_asset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/themes/{theme_id}/assets.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/themes/{theme_id}/assets.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_theme_asset")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_theme_asset", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_theme_asset",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: online-store, asset, online-store/asset, latest_api_version
@mcp.tool()
async def delete_theme_asset(
    theme_id: str = Field(..., description="The unique identifier of the theme from which the asset will be deleted."),
    asset_key: str | None = Field(None, alias="assetkey", description="The key (file path) of the asset to delete from the theme. This identifies which specific asset file to remove."),
) -> dict[str, Any] | ToolResult:
    """Removes a specific asset file from a theme. The asset is identified by its key within the theme."""

    # Construct request model with validation
    try:
        _request = _models.DeleteThemesParamThemeIdAssetsRequest(
            path=_models.DeleteThemesParamThemeIdAssetsRequestPath(theme_id=theme_id),
            query=_models.DeleteThemesParamThemeIdAssetsRequestQuery(asset_key=asset_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_theme_asset: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/themes/{theme_id}/assets.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/themes/{theme_id}/assets.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_theme_asset")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_theme_asset", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_theme_asset",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: events, webhook, events/webhook, latest_api_version
@mcp.tool()
async def list_webhooks(
    address: Any | None = Field(None, description="Filter webhooks by the URI endpoint where they send POST requests."),
    fields: Any | None = Field(None, description="Comma-separated list of specific properties to return for each webhook. Omit to receive all properties."),
    limit: Any | None = Field(None, description="Maximum number of webhooks to return per request. Defaults to 50; maximum allowed is 250."),
    since_id: Any | None = Field(None, description="Return only webhooks with an ID greater than this value. Use for pagination when combined with limit."),
    topic: Any | None = Field(None, description="Filter webhooks by topic (e.g., orders/create, products/update). Refer to webhook topic documentation for valid values."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of webhook subscriptions configured for your store. Results are paginated using link headers in the response."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhooksRequest(
            query=_models.GetWebhooksRequestQuery(address=address, fields=fields, limit=limit, since_id=since_id, topic=topic)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/webhooks.json"
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

# Tags: events, webhook, events/webhook, latest_api_version
@mcp.tool()
async def get_webhooks_count(
    address: Any | None = Field(None, description="Filter the count to only include webhook subscriptions that send POST requests to this specific URI."),
    topic: Any | None = Field(None, description="Filter the count to only include webhook subscriptions for a specific event topic (e.g., orders/create, products/update). Refer to Shopify's webhook topic documentation for valid values."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the total count of webhook subscriptions configured for your Shopify store, with optional filtering by destination address or event topic."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhooksCountRequest(
            query=_models.GetWebhooksCountRequestQuery(address=address, topic=topic)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhooks_count: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/api/2020-10/webhooks/count.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_webhooks_count")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_webhooks_count", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_webhooks_count",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: events, webhook, events/webhook, latest_api_version
@mcp.tool()
async def get_webhook(
    webhook_id: str = Field(..., description="The unique identifier of the webhook subscription to retrieve."),
    fields: Any | None = Field(None, description="Comma-separated list of specific webhook properties to return in the response. When omitted, all properties are returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a single webhook subscription by its ID, including its configuration and event subscriptions."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhooksParamWebhookIdRequest(
            path=_models.GetWebhooksParamWebhookIdRequestPath(webhook_id=webhook_id),
            query=_models.GetWebhooksParamWebhookIdRequestQuery(fields=fields)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/webhooks/{webhook_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/webhooks/{webhook_id}.json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: events, webhook, events/webhook, latest_api_version
@mcp.tool()
async def delete_webhook(webhook_id: str = Field(..., description="The unique identifier of the webhook subscription to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a webhook subscription by its ID. Once deleted, the webhook will no longer receive event notifications."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWebhooksParamWebhookIdRequest(
            path=_models.DeleteWebhooksParamWebhookIdRequestPath(webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/api/2020-10/webhooks/{webhook_id}.json", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/api/2020-10/webhooks/{webhook_id}.json"
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
        print("  python shopify_admin_api_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Shopify Admin API MCP Server")

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
    logger.info("Starting Shopify Admin API MCP Server")
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

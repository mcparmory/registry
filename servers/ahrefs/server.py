#!/usr/bin/env python3
"""
Ahrefs API MCP Server

API Info:
- Terms of Service: https://ahrefs.com/terms

Generated: 2026-05-05 14:03:03 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

import argparse
import asyncio
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

BASE_URL = os.getenv("BASE_URL", "https://api.ahrefs.com")
SERVER_NAME = "Ahrefs API"
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

def build_where_filter(where_column: str | None = None, where_operator: str | None = None, where_value: str | None = None) -> str | None:
    """Helper function for parameter transformation"""
    if where_column is None and where_operator is None and where_value is None:
        return None
    if where_column is None:
        raise ValueError('where_column is required when building a filter expression')
    operator = where_operator or '=='
    if operator not in ('>', '<', '>=', '<=', '==', '!='):
        raise ValueError(f'Invalid operator: {operator}. Must be one of: >, <, >=, <=, ==, !=')
    if where_value is None:
        raise ValueError('where_value is required when building a filter expression')
    try:
        filter_expr = f'{where_column}{operator}{where_value}'
        return filter_expr
    except Exception as e:
        raise ValueError(f'Failed to build filter expression: {e}') from e

def build_order_by(order_by_metric: str | None = None, order_by_direction: str | None = None) -> str | None:
    """Helper function for parameter transformation"""
    if order_by_metric is None and order_by_direction is None:
        return None
    if order_by_metric is None or order_by_direction is None:
        raise ValueError("Both order_by_metric and order_by_direction must be provided together") from None
    valid_metrics = {'entry_page', 'visitors', 'entries', 'avg_session_duration_sec'}
    if order_by_metric not in valid_metrics:
        raise ValueError(f"Invalid metric '{order_by_metric}'. Supported metrics: {', '.join(sorted(valid_metrics))}") from None
    valid_directions = {'asc', 'desc'}
    if order_by_direction not in valid_directions:
        raise ValueError(f"Invalid direction '{order_by_direction}'. Must be 'asc' or 'desc'") from None
    return f"{order_by_metric}:{order_by_direction}"


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
    'AhrefsConnectOAuth',
    'bearerAuth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["AhrefsConnectOAuth"] = _auth.OAuth2Auth()
    logging.info("Authentication configured: AhrefsConnectOAuth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for AhrefsConnectOAuth not configured: {error_msg}")
    _auth_handlers["AhrefsConnectOAuth"] = None
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

mcp = FastMCP("Ahrefs API", middleware=[_JsonCoercionMiddleware()])

# Tags: Site Explorer
@mcp.tool()
async def get_domain_rating(
    target: str = Field(..., description="The domain or URL to analyze. This is the primary target for which you want to retrieve the domain rating."),
    date: str = Field(..., description="The date for which to retrieve metrics, specified in YYYY-MM-DD format (e.g., 2024-01-15)."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="The protocol scheme to include in the analysis. Choose 'http' for HTTP only, 'https' for HTTPS only, or 'both' to analyze both protocols together. Defaults to 'both' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the domain rating for a target domain or URL on a specific date. Domain rating is a metric that indicates the authority and trustworthiness of a domain."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerDomainRatingRequest(
            query=_models.GetV3SiteExplorerDomainRatingRequestQuery(protocol=protocol, target=target, date=date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_domain_rating: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/domain-rating"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_domain_rating")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_domain_rating", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_domain_rating",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def get_backlinks_stats(
    target: str = Field(..., description="The domain or URL to analyze for backlink statistics. This is the target you want to get data for."),
    date: str = Field(..., description="The date for which to retrieve backlink metrics, specified in YYYY-MM-DD format."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="The protocol to include in the search results: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both protocols if not specified."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="The scope of the search relative to your target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to subdomains if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve backlink statistics for a target domain or URL on a specific date. Returns metrics about incoming links based on your specified scope and protocol."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerBacklinksStatsRequest(
            query=_models.GetV3SiteExplorerBacklinksStatsRequestQuery(protocol=protocol, target=target, mode=mode, date=date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_backlinks_stats: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/backlinks-stats"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_backlinks_stats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_backlinks_stats", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_backlinks_stats",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_outlinks_stats(
    target: str = Field(..., description="The domain or URL to analyze for outlink statistics."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="The protocol to filter by: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both protocols if not specified."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="The scope of the search relative to your target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to all subdomains if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve outlink statistics for a target domain or URL. This beta endpoint provides insights into outbound links, though data may not perfectly match the Ahrefs UI and accuracy improvements are ongoing."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerOutlinksStatsRequest(
            query=_models.GetV3SiteExplorerOutlinksStatsRequestQuery(protocol=protocol, mode=mode, target=target)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_outlinks_stats: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/outlinks-stats"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_outlinks_stats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_outlinks_stats", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_outlinks_stats",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def get_domain_metrics(
    target: str = Field(..., description="The domain or URL to analyze. Can be a full domain (example.com) or a specific URL path."),
    date: str = Field(..., description="The date for which to retrieve metrics, specified in YYYY-MM-DD format."),
    volume_mode: Literal["monthly", "average"] | None = Field(None, description="Determines how search volume is calculated: use 'monthly' for monthly averages or 'average' for overall average. This affects volume, traffic, and traffic value calculations. Defaults to 'monthly'."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="The protocol scheme to include in the analysis: 'http', 'https', or 'both' to include both protocols. Defaults to 'both'."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="The scope of analysis relative to your target: 'exact' for the exact URL, 'prefix' for URL prefix matching, 'domain' for the entire domain, or 'subdomains' to include all subdomains. Defaults to 'subdomains'."),
) -> dict[str, Any] | ToolResult:
    """Retrieve comprehensive SEO metrics for a domain or URL, including keyword rankings, traffic estimates, and search volume data for a specified date."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerMetricsRequest(
            query=_models.GetV3SiteExplorerMetricsRequestQuery(target=target, date=date, volume_mode=volume_mode, protocol=protocol, mode=mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_domain_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/metrics"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_domain_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_domain_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_domain_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def get_refdomains_history(
    target: str = Field(..., description="The domain or URL to analyze for referring domain history."),
    date_from: str = Field(..., description="The start date for the historical analysis period, specified in YYYY-MM-DD format."),
    date_to: str | None = Field(None, description="The end date for the historical analysis period, specified in YYYY-MM-DD format. If omitted, defaults to the current date."),
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(None, description="The time interval for grouping historical data points. Choose from daily, weekly, or monthly aggregation; defaults to monthly."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="The protocol scope to include in the analysis: both HTTP and HTTPS, HTTP only, or HTTPS only; defaults to both."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="The search scope relative to your target: exact domain match, prefix match, entire domain, or all subdomains; defaults to subdomains."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical data on referring domains for a target domain or URL over a specified time period, with flexible grouping and protocol filtering options."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerRefdomainsHistoryRequest(
            query=_models.GetV3SiteExplorerRefdomainsHistoryRequestQuery(target=target, date_from=date_from, date_to=date_to, history_grouping=history_grouping, protocol=protocol, mode=mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_refdomains_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/refdomains-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_refdomains_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_refdomains_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_refdomains_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def get_domain_rating_history(
    target: str = Field(..., description="The domain or URL to analyze. Can be a full domain (e.g., example.com) or a specific URL path."),
    date_from: str = Field(..., description="The start date for the historical data range in YYYY-MM-DD format (e.g., 2024-01-01)."),
    date_to: str | None = Field(None, description="The end date for the historical data range in YYYY-MM-DD format (e.g., 2024-12-31). If not provided, defaults to today's date."),
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(None, description="How to group the historical data by time interval: daily, weekly, or monthly. Defaults to monthly grouping if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical Domain Rating data for a domain or URL over a specified time period, grouped by your chosen time interval."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerDomainRatingHistoryRequest(
            query=_models.GetV3SiteExplorerDomainRatingHistoryRequestQuery(target=target, date_from=date_from, date_to=date_to, history_grouping=history_grouping)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_domain_rating_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/domain-rating-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_domain_rating_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_domain_rating_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_domain_rating_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def get_url_rating_history(
    target: str = Field(..., description="The domain or URL to analyze. Can be a full domain (e.g., example.com) or a specific URL path."),
    date_from: str = Field(..., description="The start date for the historical data retrieval in YYYY-MM-DD format (e.g., 2024-01-01)."),
    date_to: str | None = Field(None, description="The end date for the historical data retrieval in YYYY-MM-DD format (e.g., 2024-12-31). If omitted, defaults to the current date."),
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(None, description="The time interval for grouping historical data points. Choose from daily, weekly, or monthly granularity. Defaults to monthly if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the historical URL Rating progression for a target domain or URL over a specified date range, with flexible time-based grouping options."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerUrlRatingHistoryRequest(
            query=_models.GetV3SiteExplorerUrlRatingHistoryRequestQuery(target=target, date_from=date_from, date_to=date_to, history_grouping=history_grouping)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_url_rating_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/url-rating-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_url_rating_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_url_rating_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_url_rating_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_page_history(
    target: str = Field(..., description="The domain or URL to analyze. This is the primary search target for retrieving page history data."),
    date_from: str = Field(..., description="The start date for the historical period in YYYY-MM-DD format (e.g., 2024-01-15). This marks the beginning of the data range to retrieve."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="The scope of the search relative to your target: 'exact' matches the target precisely, 'prefix' matches URLs starting with the target, 'domain' searches the entire domain, or 'subdomains' includes all subdomains. Defaults to 'subdomains'."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="The protocol to include in results: 'http', 'https', or 'both' for both protocols. Defaults to 'both'."),
    date_to: str | None = Field(None, description="The end date for the historical period in YYYY-MM-DD format (e.g., 2024-12-31). If omitted, defaults to the current date."),
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(None, description="The time interval for grouping historical data: 'daily' for day-by-day data, 'weekly' for week-by-week aggregation, or 'monthly' for month-by-month aggregation. Defaults to 'monthly'."),
    page_positions: Literal["top10", "top100"] | None = Field(None, description="Filter results by ranking position: 'top10' returns only pages ranking in the top 10 positions, or 'top100' returns all pages ranking in the top 100. Defaults to 'top100'."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical ranking data for pages from a target domain or URL over a specified time period. Results can be grouped by daily, weekly, or monthly intervals and filtered by search scope and ranking position."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerPagesHistoryRequest(
            query=_models.GetV3SiteExplorerPagesHistoryRequestQuery(target=target, date_from=date_from, mode=mode, protocol=protocol, date_to=date_to, history_grouping=history_grouping, page_positions=page_positions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_page_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/pages-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_page_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_page_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_page_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def get_domain_metrics_history(
    target: str = Field(..., description="The domain or URL to analyze. Can be a full domain, subdomain, or specific URL path depending on the mode parameter."),
    date_from: str = Field(..., description="The start date for the historical data range in YYYY-MM-DD format (e.g., 2024-01-01)."),
    date_to: str | None = Field(None, description="The end date for the historical data range in YYYY-MM-DD format (e.g., 2024-12-31). If omitted, defaults to the current date."),
    select: str | None = Field(None, description="Comma-separated list of specific metrics to include in the response (e.g., date, org_cost, org_traffic). If not specified, returns date, org_cost, org_traffic, paid_cost, and paid_traffic by default."),
    volume_mode: Literal["monthly", "average"] | None = Field(None, description="Determines how search volume is calculated: monthly totals or average values. Affects volume, traffic, and traffic value metrics. Defaults to monthly."),
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(None, description="The time interval for grouping historical data: daily, weekly, or monthly. Defaults to monthly for broader trends."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="Filter results by protocol: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="The scope of analysis relative to the target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to subdomains."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical performance metrics for a domain or URL over a specified date range, with options to customize time intervals, volume calculations, and protocol scope."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerMetricsHistoryRequest(
            query=_models.GetV3SiteExplorerMetricsHistoryRequestQuery(target=target, date_from=date_from, date_to=date_to, select=select, volume_mode=volume_mode, history_grouping=history_grouping, protocol=protocol, mode=mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_domain_metrics_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/metrics-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_domain_metrics_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_domain_metrics_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_domain_metrics_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_keyword_history(
    target: str = Field(..., description="The domain or URL to analyze for keyword history."),
    date_from: str = Field(..., description="The start date for the historical period in YYYY-MM-DD format."),
    date_to: str | None = Field(None, description="The end date for the historical period in YYYY-MM-DD format. If omitted, defaults to the current date."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="The search scope relative to your target: exact URL match, URL prefix, entire domain, or all subdomains. Defaults to subdomains."),
    select: str | None = Field(None, description="A comma-separated list of data columns to include in the response. Defaults to date, top 3 keywords, top 4-10 keywords, and top 11+ keywords."),
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(None, description="The time interval for grouping historical data: daily, weekly, or monthly. Defaults to monthly."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="Filter results by protocol: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the historical ranking data for keywords associated with a target domain or URL across a specified date range, with options to group results by time interval and filter by protocol."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerKeywordsHistoryRequest(
            query=_models.GetV3SiteExplorerKeywordsHistoryRequestQuery(target=target, date_from=date_from, date_to=date_to, mode=mode, select=select, history_grouping=history_grouping, protocol=protocol)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_keyword_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/keywords-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_keyword_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_keyword_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_keyword_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_country_metrics(
    target: str = Field(..., description="The domain or URL to analyze. Can be a full domain (example.com) or a specific URL path depending on the mode parameter."),
    date: str = Field(..., description="The date for which to retrieve metrics, specified in YYYY-MM-DD format."),
    select: str | None = Field(None, description="A comma-separated list of specific metrics to include in the response. If not specified, defaults to paid_cost, paid_keywords, org_cost, paid_pages, org_keywords_1_3, org_keywords, org_traffic, paid_traffic, and country."),
    volume_mode: Literal["monthly", "average"] | None = Field(None, description="Determines how search volume is calculated: either as a monthly total or as an average. This affects volume, traffic, and traffic value metrics. Defaults to monthly."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="The protocol to include in the analysis: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="The scope of analysis based on your target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to subdomains."),
) -> dict[str, Any] | ToolResult:
    """Retrieve performance metrics broken down by country for a target domain or URL on a specific date. Useful for analyzing geographic traffic distribution and keyword performance across regions."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerMetricsByCountryRequest(
            query=_models.GetV3SiteExplorerMetricsByCountryRequestQuery(target=target, date=date, select=select, volume_mode=volume_mode, protocol=protocol, mode=mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_country_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/metrics-by-country"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_country_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_country_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_country_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_pages_by_traffic(
    target: str = Field(..., description="The domain or URL to analyze for traffic data."),
    volume_mode: Literal["monthly", "average"] | None = Field(None, description="Calculate search volume based on monthly totals or average values. Defaults to monthly calculation, which also affects traffic and traffic value metrics."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="Filter results by protocol type: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both protocols."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="Define the search scope relative to your target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to subdomains."),
) -> dict[str, Any] | ToolResult:
    """Retrieve pages grouped by traffic volume ranges for a domain or URL. Useful for identifying high-traffic pages and traffic distribution patterns across your site."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerPagesByTrafficRequest(
            query=_models.GetV3SiteExplorerPagesByTrafficRequestQuery(target=target, volume_mode=volume_mode, protocol=protocol, mode=mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pages_by_traffic: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/pages-by-traffic"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pages_by_traffic")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pages_by_traffic", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pages_by_traffic",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def get_search_volume_history(
    target: str = Field(..., description="The domain or URL to analyze. Can be a full domain, subdomain, or specific URL path depending on the mode selected."),
    date_from: str = Field(..., description="The start date for the historical data range in YYYY-MM-DD format."),
    date_to: str | None = Field(None, description="The end date for the historical data range in YYYY-MM-DD format. If not provided, defaults to the current date."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="The scope of analysis relative to your target: exact URL match, URL prefix, entire domain, or all subdomains. Defaults to analyzing all subdomains."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="Whether to include both HTTP and HTTPS protocols, or filter to a specific protocol. Defaults to both."),
    volume_mode: Literal["monthly", "average"] | None = Field(None, description="How search volume is calculated: monthly totals or average per month. This affects reported volume, traffic, and traffic value metrics. Defaults to monthly totals."),
    top_positions: Literal["top_10", "top_100"] | None = Field(None, description="The number of top organic search positions to include in volume calculations: top 10 or top 100 results. Defaults to top 10."),
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(None, description="The time interval for grouping historical data: daily, weekly, or monthly snapshots. Defaults to monthly grouping."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical search volume data for a domain or URL over a specified time period. Use this to analyze organic search trends and traffic patterns."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerTotalSearchVolumeHistoryRequest(
            query=_models.GetV3SiteExplorerTotalSearchVolumeHistoryRequestQuery(target=target, date_from=date_from, date_to=date_to, mode=mode, protocol=protocol, volume_mode=volume_mode, top_positions=top_positions, history_grouping=history_grouping)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_search_volume_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/total-search-volume-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_search_volume_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_search_volume_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_search_volume_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_backlinks(
    target: str = Field(..., description="The domain or URL to analyze for backlinks."),
    select: str = Field(..., description="Comma-separated list of data columns to include in the response. Refer to the response schema for valid column identifiers."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="Search scope relative to the target: exact URL match, URL prefix, entire domain, or all subdomains. Defaults to subdomains."),
    aggregation: Literal["similar_links", "1_per_domain", "all"] | None = Field(None, description="How to group backlinks in results: similar links (deduplicated), one per domain, or all individual links. Defaults to similar links."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="Filter results by protocol: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both."),
    history: str | None = Field(None, description="Time frame for backlink data: live (current only), since a specific date in YYYY-MM-DD format, or all historical data. Defaults to all time."),
    order_by: str | None = Field(None, description="Column identifier to sort results by. Refer to the response schema for valid options; link_group_count is not supported for sorting."),
    where: str | None = Field(None, description="Filter expression to narrow results based on column values. Refer to the response schema for recognized column identifiers."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 1000."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all backlinks pointing to a target domain or URL, including detailed backlink profile metrics and historical data. Results can be aggregated, filtered, and sorted to analyze link quality and sources."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerAllBacklinksRequest(
            query=_models.GetV3SiteExplorerAllBacklinksRequestQuery(target=target, select=select, mode=mode, aggregation=aggregation, protocol=protocol, history=history, order_by=order_by, where=where, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_backlinks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/all-backlinks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_backlinks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_backlinks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_backlinks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_broken_backlinks(
    select: str = Field(..., description="Comma-separated list of column names to include in the response. See the response schema for all available column identifiers."),
    target: str = Field(..., description="The target of your search: either a domain name or a specific URL."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Defaults to 1000 results."),
    order_by: str | None = Field(None, description="Column name to sort results by. Refer to the response schema for valid column identifiers; note that http_code_target, last_visited_target, and link_group_count cannot be used for sorting."),
    where: str | None = Field(None, description="Filter expression to narrow results. Use column identifiers from the response schema to construct conditions (column identifiers differ from those used in the select parameter)."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="Protocol to search within: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to searching both protocols."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="Scope of the search relative to your target. Use 'exact' for the precise URL, 'prefix' for URLs starting with the target, 'domain' for the exact domain, or 'subdomains' to include all subdomains. Defaults to subdomains."),
    aggregation: Literal["similar_links", "1_per_domain", "all"] | None = Field(None, description="Grouping strategy for backlinks: 'similar_links' groups by similarity, '1_per_domain' returns one backlink per referring domain, or 'all' returns every backlink. Defaults to similar_links."),
) -> dict[str, Any] | ToolResult:
    """Retrieve broken backlinks pointing to a target domain or URL. Returns backlinks that result in HTTP errors, with options to filter, sort, and aggregate results by domain or similarity."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerBrokenBacklinksRequest(
            query=_models.GetV3SiteExplorerBrokenBacklinksRequestQuery(limit=limit, order_by=order_by, where=where, select=select, protocol=protocol, target=target, mode=mode, aggregation=aggregation)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_broken_backlinks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/broken-backlinks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_broken_backlinks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_broken_backlinks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_broken_backlinks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_refdomains(
    target: str = Field(..., description="The domain or URL to analyze for referring domains."),
    select: str = Field(..., description="Comma-separated list of data columns to include in the response. Refer to the response schema for valid column identifiers."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="Search scope relative to the target: exact URL match, URL prefix, entire domain, or all subdomains. Defaults to subdomains."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="Filter results by protocol type: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 1000."),
    order_by: str | None = Field(None, description="Column identifier to sort results by. Refer to the response schema for valid column identifiers."),
    where: str | None = Field(None, description="Filter expression to narrow results based on column values. Refer to the response schema for recognized column identifiers."),
    history: str | None = Field(None, description="Time frame for historical backlink data: 'live' for current data only, 'since:<date>' for data since a specific date in YYYY-MM-DD format, or 'all_time' for complete history. Defaults to all_time."),
) -> dict[str, Any] | ToolResult:
    """Retrieve referring domains data for a target domain or URL, with filtering and sorting capabilities to analyze backlink sources."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerRefdomainsRequest(
            query=_models.GetV3SiteExplorerRefdomainsRequestQuery(target=target, select=select, mode=mode, protocol=protocol, limit=limit, order_by=order_by, where=where, history=history)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_refdomains: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/refdomains"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_refdomains")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_refdomains", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_refdomains",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_anchor_text(
    target: str = Field(..., description="The target domain or URL to analyze for incoming anchor text. Can be a full domain or specific URL path."),
    select: str = Field(..., description="Comma-separated list of data columns to include in the response. Refer to the response schema for valid column identifiers."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="Search scope relative to your target: 'exact' for the precise URL, 'prefix' for URLs starting with your target, 'domain' for the entire domain, or 'subdomains' to include all subdomains. Defaults to subdomains."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="Filter results by protocol type: 'http', 'https', or 'both' to include all protocols. Defaults to both."),
    limit: int | None = Field(None, description="Maximum number of results to return in a single response. Defaults to 1000."),
    order_by: str | None = Field(None, description="Column identifier to sort results by. Refer to the response schema for valid column identifiers."),
    where: str | None = Field(None, description="Filter expression to narrow results based on specific column values. Supports the column identifiers documented in the response schema."),
    history: str | None = Field(None, description="Time frame for historical data: 'live' for current data only, 'since:YYYY-MM-DD' to include data from a specific date forward, or 'all_time' for complete historical records. Defaults to all_time."),
) -> dict[str, Any] | ToolResult:
    """Retrieve anchor text (clickable words in hyperlinks) that point to a target domain or URL. Use this to analyze inbound link text and understand how external sites reference your target."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerAnchorsRequest(
            query=_models.GetV3SiteExplorerAnchorsRequestQuery(target=target, select=select, mode=mode, protocol=protocol, limit=limit, order_by=order_by, where=where, history=history)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_anchor_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/anchors"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_anchor_text")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_anchor_text", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_anchor_text",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_organic_keywords(
    select: str = Field(..., description="Comma-separated list of column names to include in the response; refer to the response schema for valid identifiers."),
    target: str = Field(..., description="The domain or URL to analyze for organic keywords."),
    date: str = Field(..., description="Date for which to report metrics, formatted as YYYY-MM-DD."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response; defaults to 1000 if not specified."),
    order_by: str | None = Field(None, description="Column name to sort results by; refer to the response schema for valid column identifiers."),
    where: str | None = Field(None, description="Filter expression to narrow results; use column identifiers recognized by the API (note: these differ from select parameter identifiers)."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="Protocol scheme to target: both HTTP and HTTPS, HTTP only, or HTTPS only; defaults to both."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="Search scope relative to the target: exact URL match, URL prefix match, entire domain, or domain with subdomains; defaults to subdomains."),
    volume_mode: Literal["monthly", "average"] | None = Field(None, description="Method for calculating search volume: monthly totals or average across the period; defaults to monthly."),
) -> dict[str, Any] | ToolResult:
    """Retrieve organic keywords that drive traffic to a target domain or URL, with metrics for a specified date. Results can be filtered, sorted, and customized to show specific data columns."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerOrganicKeywordsRequest(
            query=_models.GetV3SiteExplorerOrganicKeywordsRequestQuery(limit=limit, order_by=order_by, where=where, select=select, protocol=protocol, target=target, mode=mode, date=date, volume_mode=volume_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organic_keywords: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/organic-keywords"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organic_keywords")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organic_keywords", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organic_keywords",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_organic_competitors(
    target: str = Field(..., description="The domain or URL to analyze for competitors. Can be a full domain (example.com) or specific URL path."),
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(..., description="Two-letter country code (ISO 3166-1 alpha-2 format) specifying the geographic market for competitor analysis."),
    date: str = Field(..., description="Report date in YYYY-MM-DD format. Metrics will be calculated for this specific date."),
    select: str = Field(..., description="Comma-separated list of data columns to include in results. Valid identifiers correspond to the response schema fields."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="Search scope relative to the target: exact URL match, URL prefix, entire domain, or all subdomains. Defaults to subdomains."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="HTTP protocol filter: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both."),
    limit: int | None = Field(None, description="Maximum number of competitor results to return. Defaults to 1000."),
    offset: int | None = Field(None, description="Number of results to skip for pagination. Use with limit to retrieve subsequent result pages."),
    order_by: str | None = Field(None, description="Column identifier to sort results by. Must correspond to a valid response schema field."),
    where: str | None = Field(None, description="Filter expression to narrow results. Supports column identifiers from the response schema (different set than select parameter)."),
    volume_mode: Literal["monthly", "average"] | None = Field(None, description="Search volume calculation method: monthly totals or average across the period. Affects volume, traffic, and traffic value metrics. Defaults to monthly."),
) -> dict[str, Any] | ToolResult:
    """Identify organic search competitors for a target domain or URL by analyzing shared keyword rankings in a specific country and date."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerOrganicCompetitorsRequest(
            query=_models.GetV3SiteExplorerOrganicCompetitorsRequestQuery(target=target, country=country, date=date, select=select, mode=mode, protocol=protocol, limit=limit, offset=offset, order_by=order_by, where=where, volume_mode=volume_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organic_competitors: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/organic-competitors"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organic_competitors")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organic_competitors", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organic_competitors",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_top_pages(
    target: str = Field(..., description="The domain or URL to analyze. Can be a full domain, subdomain, or specific URL path depending on the mode selected."),
    date: str = Field(..., description="The date for which to retrieve metrics, specified in YYYY-MM-DD format."),
    select: str = Field(..., description="A comma-separated list of metric columns to include in the response. Refer to the response schema for valid column identifiers."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="The scope of analysis relative to your target. Use 'exact' for the precise URL, 'prefix' for URL path matching, 'domain' for the entire domain, or 'subdomains' to include all subdomains. Defaults to subdomains."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="Filter results by protocol type: 'http', 'https', or 'both' to include all protocols. Defaults to both."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 1000."),
    order_by: str | None = Field(None, description="Column identifier to sort results by. Refer to the response schema for valid column identifiers."),
    where: str | None = Field(None, description="Filter expression to narrow results based on column values. Refer to the response schema for recognized column identifiers and filtering syntax."),
    volume_mode: Literal["monthly", "average"] | None = Field(None, description="Calculation method for search volume metrics: 'monthly' for current month data or 'average' for historical average. Affects volume, traffic, and traffic value calculations. Defaults to monthly."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the top-performing pages for a domain or URL, including organic search metrics such as traffic and rankings for a specified date."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerTopPagesRequest(
            query=_models.GetV3SiteExplorerTopPagesRequestQuery(target=target, date=date, select=select, mode=mode, protocol=protocol, limit=limit, order_by=order_by, where=where, volume_mode=volume_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_top_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/top-pages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_top_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_top_pages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_top_pages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_paid_pages(
    select: str = Field(..., description="Comma-separated list of column names to include in the response. Refer to the response schema for valid column identifiers."),
    target: str = Field(..., description="The domain or URL to analyze for paid pages."),
    date: str = Field(..., description="The date for which to report metrics, specified in YYYY-MM-DD format."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response, up to 1000 by default."),
    order_by: str | None = Field(None, description="Column name to sort results by. Refer to the response schema for valid column identifiers."),
    where: str | None = Field(None, description="Filter expression to narrow results. Use column identifiers from the response schema to construct conditions."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="Protocol to search within: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="Search scope relative to the target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to all subdomains."),
    volume_mode: Literal["monthly", "average"] | None = Field(None, description="Calculation method for search volume metrics: monthly totals or average over time. Defaults to monthly and affects volume, traffic, and traffic value columns."),
) -> dict[str, Any] | ToolResult:
    """Retrieve paid search pages for a target domain or URL, showing which pages are generating paid search traffic on a specified date."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerPaidPagesRequest(
            query=_models.GetV3SiteExplorerPaidPagesRequestQuery(limit=limit, order_by=order_by, where=where, select=select, protocol=protocol, target=target, mode=mode, date=date, volume_mode=volume_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_paid_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/paid-pages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_paid_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_paid_pages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_paid_pages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_pages_by_backlinks(
    select: str = Field(..., description="Comma-separated list of column names to include in the response. Consult the response schema to see all available columns you can request."),
    target: str = Field(..., description="The domain or URL to analyze. This is the target for which you want to find pages ranked by backlinks."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Defaults to 1000 results if not specified."),
    order_by: str | None = Field(None, description="Column name to sort results by in ascending or descending order. Refer to the response schema for valid column names; note that certain columns like http_code_target, languages_target, last_visited_target, powered_by_target, target_redirect, title_target, url_rating_target, and url_rating_target are not sortable."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="Protocol scheme to filter results by: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both if not specified."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="Search scope relative to your target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to all subdomains if not specified."),
    history: str | None = Field(None, description="Time frame for including historical backlink data: live data only, backlinks since a specific date (format: YYYY-MM-DD), or complete historical data. Defaults to all_time if not specified."),
    where_column: str | None = Field(None, description="Column identifier to filter on (e.g., 'backlinks', 'url_rating_source', 'domain_rating_source')"),
    where_operator: str | None = Field(None, description="Comparison operator: '>', '<', '>=', '<=', '==', '!=' (default: '==')"),
    where_value: str | None = Field(None, description="Value to compare against (will be properly escaped)"),
) -> dict[str, Any] | ToolResult:
    """Retrieve the best performing pages for a target domain or URL ranked by backlink count. Use this to identify which pages attract the most external links and understand your site's link profile."""

    # Call helper functions
    where = build_where_filter(where_column, where_operator, where_value)

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerPagesByBacklinksRequest(
            query=_models.GetV3SiteExplorerPagesByBacklinksRequestQuery(limit=limit, order_by=order_by, select=select, protocol=protocol, target=target, mode=mode, history=history, where=where)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pages_by_backlinks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/pages-by-backlinks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pages_by_backlinks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pages_by_backlinks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pages_by_backlinks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_pages_by_internal_links(
    target: str = Field(..., description="The domain or URL to analyze. Can be a full domain (example.com) or a specific URL path depending on the mode parameter."),
    select: str = Field(..., description="Comma-separated list of data columns to include in the response. Refer to the response schema for valid column identifiers."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="Defines the search scope relative to your target. Use 'exact' for the precise URL, 'prefix' for URL path matching, 'domain' for the root domain only, or 'subdomains' to include all subdomains. Defaults to subdomains."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="Filter results by protocol type. Choose 'http', 'https', or 'both' to include all protocols. Defaults to both."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 1000."),
    order_by: str | None = Field(None, description="Column identifier to sort results by. See the response schema for valid options. Note that certain columns like http_code_target, languages_target, last_visited_target, powered_by_target, target_redirect, title_target, url_rating_target, and target_redirect are not supported for sorting."),
    where: str | None = Field(None, description="Filter expression to narrow results. Accepts column identifiers recognized by the API's filter syntax (note: these may differ from the select parameter's column identifiers)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the best-performing pages for a target domain or URL ranked by the number of internal links pointing to them. Use this to identify which pages are most linked internally and understand your site's link structure."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerPagesByInternalLinksRequest(
            query=_models.GetV3SiteExplorerPagesByInternalLinksRequestQuery(target=target, select=select, mode=mode, protocol=protocol, limit=limit, order_by=order_by, where=where)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pages_by_internal_links: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/pages-by-internal-links"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pages_by_internal_links")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pages_by_internal_links", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pages_by_internal_links",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_linked_domains(
    target: str = Field(..., description="The domain or URL to analyze for incoming links. This is the target whose linked domains you want to discover."),
    select: str = Field(..., description="Comma-separated list of data columns to include in results. Refer to the response schema for valid column identifiers."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="Defines the search scope relative to your target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to subdomains."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="Filter results by protocol type: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 1000."),
    order_by: str | None = Field(None, description="Column identifier to sort results by. Refer to the response schema for valid column identifiers."),
    where: str | None = Field(None, description="Filter expression to narrow results. Supports column identifiers recognized by the API (note: these may differ from the select parameter identifiers)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve domains that link to your target domain or URL, with customizable filtering, sorting, and column selection for link analysis."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerLinkeddomainsRequest(
            query=_models.GetV3SiteExplorerLinkeddomainsRequestQuery(target=target, select=select, mode=mode, protocol=protocol, limit=limit, order_by=order_by, where=where)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_linked_domains: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/linkeddomains"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_linked_domains")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_linked_domains", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_linked_domains",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_external_anchors(
    target: str = Field(..., description="The domain or URL to analyze for outgoing external anchors."),
    select: str = Field(..., description="Comma-separated list of column identifiers to include in the response. See response schema for valid column names."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="The scope of the search relative to your target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to subdomains."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="Filter results by protocol type: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 1000."),
    order_by: str | None = Field(None, description="Column identifier to sort results by. See response schema for valid column names."),
    where: str | None = Field(None, description="Filter expression to narrow results. Supports column identifiers recognized by the API (note: different set than the select parameter)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve outgoing external anchor links from a target domain or URL. Results can be filtered by search scope, protocol, and custom expressions, with configurable sorting and pagination."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerLinkedAnchorsExternalRequest(
            query=_models.GetV3SiteExplorerLinkedAnchorsExternalRequestQuery(target=target, select=select, mode=mode, protocol=protocol, limit=limit, order_by=order_by, where=where)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_external_anchors: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/linked-anchors-external"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_external_anchors")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_external_anchors", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_external_anchors",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Explorer
@mcp.tool()
async def list_internal_anchors(
    target: str = Field(..., description="The domain or URL to analyze for outgoing internal anchors."),
    select: str = Field(..., description="Comma-separated list of columns to include in the response. See response schema for valid column identifiers."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="The scope of the search relative to your target: exact URL match, URL prefix match, entire domain, or subdomains. Defaults to subdomains."),
    protocol: Literal["both", "http", "https"] | None = Field(None, description="Filter results by protocol type: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 1000."),
    order_by: str | None = Field(None, description="Column identifier to sort results by. See response schema for valid column identifiers."),
    where: str | None = Field(None, description="Filter expression to narrow results. Supports the column identifiers listed in the response schema (note: different identifiers than the select parameter)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve outgoing internal anchor links from a target domain or URL. Results can be filtered, ordered, and scoped by search mode and protocol."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteExplorerLinkedAnchorsInternalRequest(
            query=_models.GetV3SiteExplorerLinkedAnchorsInternalRequestQuery(target=target, select=select, mode=mode, protocol=protocol, limit=limit, order_by=order_by, where=where)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_internal_anchors: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-explorer/linked-anchors-internal"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_internal_anchors")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_internal_anchors", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_internal_anchors",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Keywords Explorer
@mcp.tool()
async def get_keyword_metrics(
    select: str = Field(..., description="Comma-separated list of data columns to include in the response. Refer to the response schema for valid column identifiers."),
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(..., description="Two-letter ISO 3166-1 country code (e.g., 'us', 'gb', 'de') specifying the target market for keyword data."),
    target: str | None = Field(None, description="Optional domain or URL to analyze keyword rankings for. Use with target_mode to define the scope of analysis."),
    target_mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(None, description="Scope of the target URL analysis: 'exact' for the exact URL, 'prefix' for URL path prefix, 'domain' for the entire domain, or 'subdomains' for all subdomains."),
    target_position: Literal["in_top10", "in_top100"] | None = Field(None, description="Filter keywords by the ranking position of the specified target: 'in_top10' for top 10 rankings or 'in_top100' for top 100 rankings."),
    volume_monthly_date_from: str | None = Field(None, description="Start date in YYYY-MM-DD format for retrieving historical monthly search volume data. Required only when requesting volume_monthly_history."),
    volume_monthly_date_to: str | None = Field(None, description="End date in YYYY-MM-DD format for retrieving historical monthly search volume data. Required only when requesting volume_monthly_history."),
    where: str | None = Field(None, description="Filter expression to narrow results based on keyword metrics and attributes. Refer to the response schema for supported column identifiers."),
    order_by: str | None = Field(None, description="Column identifier to sort results by. Refer to the response schema for valid options; note that volume_monthly is not supported for sorting on this endpoint."),
    limit: int | None = Field(None, description="Maximum number of results to return. Defaults to 1000 if not specified."),
    search_engine: Literal["google"] | None = Field(None, description="Deprecated parameter. Only 'google' is supported; included for backward compatibility."),
) -> dict[str, Any] | ToolResult:
    """Retrieve keyword performance metrics and search data for specified keywords in a target country, with optional filtering by domain/URL ranking position and historical volume trends."""

    # Construct request model with validation
    try:
        _request = _models.GetV3KeywordsExplorerOverviewRequest(
            query=_models.GetV3KeywordsExplorerOverviewRequestQuery(select=select, country=country, target=target, target_mode=target_mode, target_position=target_position, volume_monthly_date_from=volume_monthly_date_from, volume_monthly_date_to=volume_monthly_date_to, where=where, order_by=order_by, limit=limit, search_engine=search_engine)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_keyword_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/keywords-explorer/overview"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_keyword_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_keyword_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_keyword_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Keywords Explorer
@mcp.tool()
async def get_keyword_volume_history(
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(..., description="The target country for volume data, specified as a two-letter ISO 3166-1 alpha-2 country code (e.g., 'us' for United States, 'gb' for United Kingdom)."),
    keyword: str = Field(..., description="The keyword term to retrieve volume history for."),
    date_from: str | None = Field(None, description="The start date for the historical period in YYYY-MM-DD format. If omitted, defaults to the earliest available data."),
    date_to: str | None = Field(None, description="The end date for the historical period in YYYY-MM-DD format. If omitted, defaults to the most recent available data."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical search volume data for a keyword across a specified date range in a given country. Use this to analyze keyword popularity trends over time."""

    # Construct request model with validation
    try:
        _request = _models.GetV3KeywordsExplorerVolumeHistoryRequest(
            query=_models.GetV3KeywordsExplorerVolumeHistoryRequestQuery(country=country, keyword=keyword, date_from=date_from, date_to=date_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_keyword_volume_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/keywords-explorer/volume-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_keyword_volume_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_keyword_volume_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_keyword_volume_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Keywords Explorer
@mcp.tool()
async def get_keyword_volume_by_country(
    keyword: str = Field(..., description="The keyword to analyze. Provide the exact search term you want to get volume data for."),
    limit: int | None = Field(None, description="Maximum number of countries to return in the results. Omit to get all available data."),
    search_engine: Literal["google"] | None = Field(None, description="Search engine to query (currently only Google is supported). This parameter is deprecated as of August 5, 2024."),
) -> dict[str, Any] | ToolResult:
    """Retrieve search volume metrics for a keyword broken down by country. Use this to understand geographic demand patterns and identify high-opportunity markets for your target keyword."""

    # Construct request model with validation
    try:
        _request = _models.GetV3KeywordsExplorerVolumeByCountryRequest(
            query=_models.GetV3KeywordsExplorerVolumeByCountryRequestQuery(keyword=keyword, limit=limit, search_engine=search_engine)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_keyword_volume_by_country: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/keywords-explorer/volume-by-country"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_keyword_volume_by_country")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_keyword_volume_by_country", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_keyword_volume_by_country",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Keywords Explorer
@mcp.tool()
async def search_matching_keywords(
    select: str = Field(..., description="Comma-separated list of data columns to include in the response. Specify which metrics and attributes you want returned for each matching keyword."),
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(..., description="Two-letter ISO country code (e.g., 'us', 'gb', 'de') that determines the geographic market for keyword data and search volume metrics."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Defaults to 1000 results if not specified."),
    order_by: str | None = Field(None, description="Column name to sort results by in ascending order. Refer to the response schema for valid column names; monthly search volume is not supported for sorting on this endpoint."),
    where: str | None = Field(None, description="Filter expression to narrow results based on keyword metrics and attributes. Use column identifiers from the response schema to construct filter conditions."),
    search_engine: Literal["google"] | None = Field(None, description="Deprecated parameter. Only 'google' is supported; included for backward compatibility."),
    match_mode: Literal["terms", "phrase"] | None = Field(None, description="Search matching mode: 'terms' finds keywords containing your search words in any order, while 'phrase' requires exact word order. Defaults to 'terms' mode."),
    terms: Literal["all", "questions"] | None = Field(None, description="Filter results to include all keyword ideas or only those phrased as questions. Defaults to returning all keyword ideas."),
) -> dict[str, Any] | ToolResult:
    """Find keyword variations and related search terms with performance metrics for a specific country. Returns matching keywords based on search mode (exact phrase or term-based) with optional filtering and sorting capabilities."""

    # Construct request model with validation
    try:
        _request = _models.GetV3KeywordsExplorerMatchingTermsRequest(
            query=_models.GetV3KeywordsExplorerMatchingTermsRequestQuery(limit=limit, order_by=order_by, where=where, select=select, country=country, search_engine=search_engine, match_mode=match_mode, terms=terms)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_matching_keywords: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/keywords-explorer/matching-terms"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_matching_keywords")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_matching_keywords", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_matching_keywords",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Keywords Explorer
@mcp.tool()
async def list_related_keywords(
    select: str = Field(..., description="Comma-separated list of data columns to include in the response. Required parameter that determines which metrics and attributes are returned."),
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(..., description="Two-letter ISO country code (e.g., 'us', 'gb', 'de') specifying the geographic market for keyword data. Required parameter."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Defaults to 1000 results if not specified."),
    order_by: str | None = Field(None, description="Column name to sort results by. Refer to the response schema for valid column identifiers; note that monthly search volume is not available as a sort option for this endpoint."),
    where: str | None = Field(None, description="Filter expression to narrow results. Use column identifiers from the response schema to create conditions (note: different identifiers than those used in the select parameter)."),
    view_for: Literal["top_10", "top_100"] | None = Field(None, description="Scope of analysis: analyze keywords from the top 10 or top 100 ranking pages. Defaults to top 10 if not specified."),
    terms: Literal["also_rank_for", "also_talk_about", "all"] | None = Field(None, description="Type of related keywords to retrieve: keywords the top pages also rank for, topics they mention, or both combined. Defaults to all types if not specified."),
) -> dict[str, Any] | ToolResult:
    """Discover related keywords that top-ranking pages rank for or mention, including keywords they also target and topics they discuss. Use this to identify keyword opportunities and content gaps around your target search terms."""

    # Construct request model with validation
    try:
        _request = _models.GetV3KeywordsExplorerRelatedTermsRequest(
            query=_models.GetV3KeywordsExplorerRelatedTermsRequestQuery(limit=limit, order_by=order_by, where=where, select=select, country=country, view_for=view_for, terms=terms)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_related_keywords: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/keywords-explorer/related-terms"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_related_keywords")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_related_keywords", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_related_keywords",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Keywords Explorer
@mcp.tool()
async def search_keyword_suggestions(
    select: str = Field(..., description="Comma-separated list of data columns to include in the response. Required parameter that determines which fields are returned for each suggestion."),
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(..., description="Two-letter ISO 3166-1 country code specifying the geographic market for keyword suggestions. Required parameter that determines regional search data."),
    limit: int | None = Field(None, description="Maximum number of suggestions to return in the response. Defaults to 1000 results if not specified."),
    order_by: str | None = Field(None, description="Column name to sort results by. Refer to the response schema for valid column identifiers; note that monthly search volume is not available as a sort option for this endpoint."),
    where: str | None = Field(None, description="Filter expression to narrow results. Use column identifiers from the response schema to create conditions (different identifiers than those used in the select parameter)."),
    search_engine: Literal["google"] | None = Field(None, description="Search engine source for suggestions. Currently supports Google only; this parameter is deprecated as of August 5, 2024."),
) -> dict[str, Any] | ToolResult:
    """Retrieve keyword search suggestions for a specified country. Returns relevant keyword variations and related search terms to help identify search opportunities in your target market."""

    # Construct request model with validation
    try:
        _request = _models.GetV3KeywordsExplorerSearchSuggestionsRequest(
            query=_models.GetV3KeywordsExplorerSearchSuggestionsRequestQuery(limit=limit, order_by=order_by, where=where, select=select, country=country, search_engine=search_engine)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_keyword_suggestions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/keywords-explorer/search-suggestions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_keyword_suggestions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_keyword_suggestions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_keyword_suggestions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Audit
@mcp.tool()
async def list_audit_projects(
    project_url: str | None = Field(None, description="Filter results to projects matching this target URL. The comparison ignores protocol differences and trailing slashes for flexible matching."),
    project_name: str | None = Field(None, description="Filter results to projects matching this name."),
    date: str | None = Field(None, description="Retrieve metrics from a specific crawl date and time in ISO 8601 format (YYYY-MM-DDThh:mm:ss UTC). If omitted, returns data from the most recent available crawl. For scheduled crawls, returns the latest crawl completed before this timestamp; for Always-on audits, returns data as of the specified moment. The time component defaults to 00:00:00 if not provided."),
) -> dict[str, Any] | ToolResult:
    """Retrieve health scores and performance metrics for Site Audit projects. Returns data from the most recent crawl by default, or from a specified crawl date if provided."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteAuditProjectsRequest(
            query=_models.GetV3SiteAuditProjectsRequestQuery(project_url=project_url, project_name=project_name, date=date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_audit_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-audit/projects"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_audit_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_audit_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_audit_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Audit
@mcp.tool()
async def list_audit_issues(
    project_id: int = Field(..., description="The unique identifier of the project, found in the URL of your Site Audit project dashboard (https://app.ahrefs.com/site-audit/#project_id#)."),
    date: str | None = Field(None, description="Optional timestamp in ISO 8601 format (YYYY-MM-DDThh:mm:ss UTC) to retrieve issues from a specific crawl. Defaults to the most recent crawl if not provided. For scheduled crawls, returns data from the latest crawl completed before this timestamp; for Always-on audits, returns data as of the specified date and time. If only the date is provided without time, it defaults to 00:00:00 UTC."),
) -> dict[str, Any] | ToolResult:
    """Retrieve site audit issues for a specific project. This operation costs 50 API units per request and returns issues from either a specified crawl date or the most recent available crawl."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteAuditIssuesRequest(
            query=_models.GetV3SiteAuditIssuesRequestQuery(project_id=project_id, date=date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_audit_issues: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-audit/issues"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_audit_issues")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_audit_issues", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_audit_issues",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Audit
@mcp.tool()
async def get_page_content(
    select: str = Field(..., description="Comma-separated list of column identifiers to include in the response. Refer to the response schema for valid column names."),
    target_url: str = Field(..., description="The full URL of the page to retrieve content for."),
    project_id: int = Field(..., description="The unique identifier of the Site Audit project. Only projects with verified ownership are supported. You can find this ID in your Site Audit project URL on Ahrefs."),
    date: str | None = Field(None, description="Optional crawl date in ISO 8601 format (YYYY-MM-DDThh:mm:ss UTC). Defaults to the most recent crawl if omitted. For scheduled crawls, returns data from the latest crawl completed before this timestamp; for Always-on audits, returns data as of the specified date and time. If only the date is provided, the time defaults to 00:00:00 UTC."),
) -> dict[str, Any] | ToolResult:
    """Retrieve page content and metadata from a Site Audit project for a specific URL. This operation consumes 50 API units per request."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteAuditPageContentRequest(
            query=_models.GetV3SiteAuditPageContentRequestQuery(select=select, date=date, target_url=target_url, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_page_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-audit/page-content"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_page_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_page_content", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_page_content",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Site Audit
@mcp.tool()
async def list_audit_pages(
    project_id: int = Field(..., description="The unique identifier of the project. Only projects with verified ownership are supported. You can find this in your Site Audit project URL on Ahrefs."),
    date: str | None = Field(None, description="The crawl date to retrieve metrics from in ISO 8601 format (YYYY-MM-DDThh:mm:ss UTC). Defaults to the most recent crawl if omitted. For scheduled crawls, returns data from the latest crawl before this timestamp; for Always-on audits, returns data as of the specified date. If time is omitted, defaults to 00:00:00 UTC."),
    select: str | None = Field(None, description="A comma-separated list of columns to include in the response. Defaults to a comprehensive set including page rating, URL, HTTP status, content type, title, meta description, heading, traffic, canonical status, redirect information, link counts, Core Web Vitals categories, and schema validation data."),
    order_by: str | None = Field(None, description="The column name to sort results by. Must be one of the valid columns available in the response schema."),
    limit: int | None = Field(None, description="The maximum number of results to return. Defaults to 1000 results per request."),
    filter_mode: Literal["added", "new", "removed", "missing", "no_change"] | None = Field(None, description="Filter pages by their status relative to the previous crawl. Use 'added' for new matches, 'new' for newly crawled pages, 'removed' for pages no longer matching filters, 'missing' for uncrawled pages that previously matched, or 'no_change' for pages matching in both crawls. If omitted, returns all matching pages."),
    issue_id: str | None = Field(None, description="The unique identifier of a specific issue to filter by. When specified, only pages affected by this issue are returned. Retrieve issue IDs from the site-audit/issues endpoint."),
    where_column: str | None = Field(None, description="Column identifier to filter on (e.g., 'backlinks', 'url_rating_source', 'domain_rating_source')"),
    where_operator: str | None = Field(None, description="Comparison operator: '>', '<', '>=', '<=', '==', '!=' (default: '==')"),
    where_value: str | None = Field(None, description="Value to compare against (will be properly escaped)"),
) -> dict[str, Any] | ToolResult:
    """Retrieve page-level metrics and SEO data from a Site Audit crawl. This endpoint costs 50 API units per request and supports filtering, sorting, and comparison against previous crawls."""

    # Call helper functions
    where = build_where_filter(where_column, where_operator, where_value)

    # Construct request model with validation
    try:
        _request = _models.GetV3SiteAuditPageExplorerRequest(
            query=_models.GetV3SiteAuditPageExplorerRequestQuery(project_id=project_id, date=date, select=select, order_by=order_by, limit=limit, filter_mode=filter_mode, issue_id=issue_id, where=where)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_audit_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/site-audit/page-explorer"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_audit_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_audit_pages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_audit_pages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Rank Tracker
@mcp.tool()
async def get_rank_tracker_overview(
    project_id: int = Field(..., description="The unique identifier of the Rank Tracker project, found in the project URL on Ahrefs."),
    date: str = Field(..., description="The date for which to report metrics, specified in YYYY-MM-DD format."),
    device: Literal["desktop", "mobile"] = Field(..., description="The device type for ranking data: either desktop or mobile."),
    select: str = Field(..., description="A comma-separated list of metric columns to include in the response. Refer to the response schema for valid column identifiers."),
    volume_mode: Literal["monthly", "average"] | None = Field(None, description="The search volume calculation method: monthly (default) calculates based on monthly data, while average uses historical averages. This affects volume, traffic, and traffic value metrics."),
    order_by: str | None = Field(None, description="A column identifier to sort results by. Refer to the response schema for valid column identifiers."),
    limit: int | None = Field(None, description="The maximum number of results to return. Defaults to 1000 if not specified."),
    where: str | None = Field(None, description="A filter expression to narrow results by specific criteria. Refer to the response schema for recognized column identifiers and filter syntax."),
) -> dict[str, Any] | ToolResult:
    """Retrieve overview metrics for all tracked keywords in a Rank Tracker project on a specific date, with support for filtering, sorting, and device-specific rankings."""

    # Construct request model with validation
    try:
        _request = _models.GetV3RankTrackerOverviewRequest(
            query=_models.GetV3RankTrackerOverviewRequestQuery(project_id=project_id, date=date, device=device, select=select, volume_mode=volume_mode, order_by=order_by, limit=limit, where=where)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_rank_tracker_overview: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/rank-tracker/overview"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_rank_tracker_overview")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_rank_tracker_overview", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_rank_tracker_overview",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Rank Tracker
@mcp.tool()
async def get_serp_overview(
    project_id: int = Field(..., description="The unique identifier of your Rank Tracker project, found in the project URL on Ahrefs."),
    keyword: str = Field(..., description="The keyword to retrieve SERP data for."),
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(..., description="The target country specified as a two-letter ISO 3166-1 alpha-2 code (e.g., 'us', 'gb', 'de')."),
    device: Literal["desktop", "mobile"] = Field(..., description="The device type for ranking data: either 'desktop' or 'mobile'."),
    language_code: str | None = Field(None, description="Optional language code for the tracked keyword. Use the management/project-keywords endpoint to find the correct language code for your keyword."),
    location_id: int | None = Field(None, description="Optional location ID for the tracked keyword. Use the management/project-keywords endpoint to find the correct location ID for your keyword."),
    date: str | None = Field(None, description="Optional timestamp to retrieve historical SERP data in ISO 8601 format (YYYY-MM-DDThh:mm:ss). If omitted, returns the most recent available data."),
    top_positions: int | None = Field(None, description="Optional limit on the number of top organic positions to return. If not specified, all available positions are included."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the current SERP overview for a tracked keyword, including top organic positions and ranking data. This endpoint is free and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3RankTrackerSerpOverviewRequest(
            query=_models.GetV3RankTrackerSerpOverviewRequestQuery(project_id=project_id, keyword=keyword, country=country, device=device, language_code=language_code, location_id=location_id, date=date, top_positions=top_positions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_serp_overview: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/rank-tracker/serp-overview"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_serp_overview")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_serp_overview", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_serp_overview",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Rank Tracker
@mcp.tool()
async def list_competitor_rankings(
    project_id: int = Field(..., description="The unique identifier of your Rank Tracker project, found in the project URL within Ahrefs."),
    date: str = Field(..., description="The date for which to retrieve ranking metrics, specified in YYYY-MM-DD format."),
    device: Literal["desktop", "mobile"] = Field(..., description="The device type to report rankings for: either desktop or mobile."),
    select: str = Field(..., description="A comma-separated list of column identifiers to include in the response. Refer to the response schema for valid column names."),
    limit: int | None = Field(None, description="The maximum number of results to return in the response. Defaults to 1000 if not specified."),
    order_by: str | None = Field(None, description="The column identifier to sort results by. Refer to the response schema for valid column names."),
    where: str | None = Field(None, description="A filter expression to narrow results. Supports filtering by recognized column identifiers (which may differ from those used in the select parameter)."),
    volume_mode: Literal["monthly", "average"] | None = Field(None, description="The method for calculating search volume metrics: monthly (default) or average. This affects volume, traffic, and traffic value calculations."),
) -> dict[str, Any] | ToolResult:
    """Retrieve an overview of competitor rankings for your tracked keywords on a specific date. This endpoint is free and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3RankTrackerCompetitorsOverviewRequest(
            query=_models.GetV3RankTrackerCompetitorsOverviewRequestQuery(project_id=project_id, date=date, device=device, select=select, limit=limit, order_by=order_by, where=where, volume_mode=volume_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_competitor_rankings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/rank-tracker/competitors-overview"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_competitor_rankings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_competitor_rankings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_competitor_rankings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Rank Tracker
@mcp.tool()
async def list_competitor_pages(
    project_id: int = Field(..., description="The unique identifier of your Rank Tracker project, found in the project URL on Ahrefs."),
    date: str = Field(..., description="The date for which to retrieve metrics, specified in YYYY-MM-DD format."),
    device: Literal["desktop", "mobile"] = Field(..., description="The device type to report rankings for: either desktop or mobile."),
    select: str = Field(..., description="A comma-separated list of column identifiers to include in the response. Refer to the response schema for valid column names."),
    limit: int | None = Field(None, description="The maximum number of results to return. Defaults to 1000 if not specified."),
    order_by: str | None = Field(None, description="A column identifier to sort results by. Refer to the response schema for valid column names."),
    where: str | None = Field(None, description="A filter expression to narrow results. Supports column identifiers recognized by the API (which may differ from select parameter identifiers)."),
    target_and_tracked_competitors_only: bool | None = Field(None, description="When enabled, restricts results to only target and tracked competitors. Defaults to false."),
    volume_mode: Literal["monthly", "average"] | None = Field(None, description="The method for calculating search volume: monthly (default) or average. This affects volume, traffic, and traffic value metrics."),
) -> dict[str, Any] | ToolResult:
    """Retrieve competitor pages data for a Rank Tracker project on a specific date, filtered by device type and customizable metrics."""

    # Construct request model with validation
    try:
        _request = _models.GetV3RankTrackerCompetitorsPagesRequest(
            query=_models.GetV3RankTrackerCompetitorsPagesRequestQuery(project_id=project_id, date=date, device=device, select=select, limit=limit, order_by=order_by, where=where, target_and_tracked_competitors_only=target_and_tracked_competitors_only, volume_mode=volume_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_competitor_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/rank-tracker/competitors-pages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_competitor_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_competitor_pages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_competitor_pages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Rank Tracker
@mcp.tool()
async def list_competitor_stats(
    select: str = Field(..., description="Comma-separated list of metric columns to include in the response. Refer to the response schema for available column identifiers."),
    date: str = Field(..., description="The date for which to retrieve metrics, formatted as YYYY-MM-DD."),
    device: Literal["desktop", "mobile"] = Field(..., description="The device type to report rankings for: either desktop or mobile."),
    project_id: int = Field(..., description="The unique identifier of your Rank Tracker project, found in the project URL within Ahrefs."),
    volume_mode: Literal["monthly", "average"] | None = Field(None, description="The method for calculating search volume metrics: monthly (default) for monthly averages or average for overall average volume. This affects volume, traffic, and traffic value calculations."),
) -> dict[str, Any] | ToolResult:
    """Retrieve competitor performance metrics for tracked keywords on a specified date and device type. Use this to analyze how competitors rank for your target keywords and monitor their search visibility."""

    # Construct request model with validation
    try:
        _request = _models.GetV3RankTrackerCompetitorsStatsRequest(
            query=_models.GetV3RankTrackerCompetitorsStatsRequestQuery(select=select, date=date, device=device, project_id=project_id, volume_mode=volume_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_competitor_stats: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/rank-tracker/competitors-stats"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_competitor_stats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_competitor_stats", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_competitor_stats",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: SERP Overview
@mcp.tool()
async def get_serp_overview_keyword(
    select: str = Field(..., description="Comma-separated list of data columns to include in the response. Refer to the response schema documentation for valid column identifiers."),
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(..., description="Two-letter ISO 3166-1 country code (e.g., 'us', 'gb', 'de') indicating the search market for the SERP data."),
    keyword: str = Field(..., description="The search keyword to retrieve SERP overview data for."),
    top_positions: int | None = Field(None, description="Maximum number of top organic search results to return. If omitted, all available positions are included."),
    date: str | None = Field(None, description="Specific date and time for which to retrieve SERP data in ISO 8601 format (YYYY-MM-DDThh:mm:ss). If not provided, the most recent available data is returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieve SERP (Search Engine Results Page) overview data for a keyword in a specified country, including top organic positions and customizable metrics."""

    # Construct request model with validation
    try:
        _request = _models.GetV3SerpOverviewRequest(
            query=_models.GetV3SerpOverviewRequestQuery(select=select, top_positions=top_positions, date=date, country=country, keyword=keyword)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_serp_overview_keyword: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/serp-overview"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_serp_overview_keyword")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_serp_overview_keyword", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_serp_overview_keyword",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Batch Analysis
@mcp.tool()
async def analyze_targets_batch(
    select: list[str] = Field(..., description="Specify which SEO metrics to include in the response (e.g., url, ahrefs_rank). Refer to the response schema for all available column identifiers."),
    targets: list[_models.PostV3BatchAnalysisBodyTargetsItem] = Field(..., description="Provide a list of targets (domains, URLs, or keywords) to analyze. Each target will be evaluated for the selected metrics."),
    order_by: str | None = Field(None, description="Sort results by a specific SEO metric column. Refer to the response schema for valid column identifiers."),
    volume_mode: Literal["monthly", "average"] | None = Field(None, description="Choose how search volume is calculated: monthly (current month data) or average (historical average). This affects volume, traffic, and traffic value metrics."),
) -> dict[str, Any] | ToolResult:
    """Perform batch SEO analysis on multiple targets to retrieve comprehensive metrics including backlinks, keywords, traffic, and ranking data. Customize which metrics to return and how results are ordered."""

    # Construct request model with validation
    try:
        _request = _models.PostV3BatchAnalysisRequest(
            body=_models.PostV3BatchAnalysisRequestBody(select=select, order_by=order_by, volume_mode=volume_mode, targets=targets)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for analyze_targets_batch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/batch-analysis"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("analyze_targets_batch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("analyze_targets_batch", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="analyze_targets_batch",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Subscription Information
@mcp.tool()
async def get_subscription_limits_and_usage() -> dict[str, Any] | ToolResult:
    """Retrieve current workspace and API key limits and usage information. This request is free and does not consume any API units."""

    # Extract parameters for API call
    _http_path = "/v3/subscription-info/limits-and-usage"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_subscription_limits_and_usage")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_subscription_limits_and_usage", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_subscription_limits_and_usage",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def list_projects(
    owned_by: str | None = Field(None, description="Filter projects by the email address of the project owner."),
    access: Literal["private", "shared"] | None = Field(None, description="Filter projects by access type: either private (accessible only to you) or shared (accessible to others)."),
    has_keywords: bool | None = Field(None, description="Filter to only include projects that have Rank Tracker keywords configured."),
) -> dict[str, Any] | ToolResult:
    """Retrieve your projects with optional filtering by owner, access type, and keyword tracking status. This operation is free and does not consume any API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3ManagementProjectsRequest(
            query=_models.GetV3ManagementProjectsRequestQuery(owned_by=owned_by, access=access, has_keywords=has_keywords)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/projects"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def create_project(
    protocol: Literal["both", "http", "https"] = Field(..., description="The protocol(s) to monitor for the target: http only, https only, or both protocols."),
    url: str = Field(..., description="The URL of the target resource or service that this project will monitor or manage."),
    mode: Literal["exact", "prefix", "domain", "subdomains"] = Field(..., description="The scope matching strategy for the target URL: exact (precise URL match), prefix (URL and all subpaths), domain (entire domain), or subdomains (domain and all subdomains)."),
    project_name: str = Field(..., description="A descriptive name for this project to identify it within the workspace."),
    owned_by: str | None = Field(None, description="The email address of the user who will own this project. If not specified, ownership defaults to the workspace owner."),
    access: Literal["private", "shared"] | None = Field(None, description="The access control level for this project, either private (restricted to owner) or shared (accessible to workspace members)."),
) -> dict[str, Any] | ToolResult:
    """Create a new project by specifying a target URL, protocol, and matching scope. The project will be assigned to the specified owner or the workspace owner by default."""

    # Construct request model with validation
    try:
        _request = _models.PostV3ManagementProjectsRequest(
            body=_models.PostV3ManagementProjectsRequestBody(owned_by=owned_by, access=access, protocol=protocol, url=url, mode=mode, project_name=project_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/projects"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def update_project_access(
    access: Literal["private", "shared"] = Field(..., description="The new access level for the project. Must be either 'private' to restrict access to the project owner, or 'shared' to allow others to access it."),
    project_id: int = Field(..., description="The unique identifier of the project to update. You can find this ID in the URL of your Rank Tracker project dashboard in Ahrefs (the numeric value in the project URL)."),
) -> dict[str, Any] | ToolResult:
    """Update the access setting for a project to control whether it is private or shared. This operation is free and does not consume any API units."""

    # Construct request model with validation
    try:
        _request = _models.PatchV3ManagementUpdateProjectRequest(
            body=_models.PatchV3ManagementUpdateProjectRequestBody(access=access, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project_access: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/update-project"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project_access")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project_access", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project_access",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def list_project_keywords(project_id: int = Field(..., description="The unique identifier of the project, found in the URL of your Rank Tracker project dashboard (the numeric ID in the project URL).")) -> dict[str, Any] | ToolResult:
    """Retrieve all keywords tracked for a specific project in Rank Tracker. This operation is free and does not consume any API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3ManagementProjectKeywordsRequest(
            query=_models.GetV3ManagementProjectKeywordsRequestQuery(project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_keywords: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/project-keywords"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_keywords")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_keywords", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_keywords",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def add_keywords(
    project_id: int = Field(..., description="The unique identifier of the project you want to add keywords to. You can find this ID in the URL of your Rank Tracker project dashboard."),
    locations: list[_models.PutV3ManagementProjectKeywordsBodyLocationsItem] = Field(..., description="A list of locations where the keywords should be tracked. Use the Locations and languages endpoint to retrieve valid country codes, language codes, and location IDs for your target regions."),
    keywords: list[_models.PutV3ManagementProjectKeywordsBodyKeywordsItem] = Field(..., description="A list of keywords to add to the project. Each keyword will be assigned to all specified locations."),
) -> dict[str, Any] | ToolResult:
    """Add keywords to a project and assign them to specific locations for tracking. This operation allows you to expand your keyword monitoring across different geographic regions."""

    # Construct request model with validation
    try:
        _request = _models.PutV3ManagementProjectKeywordsRequest(
            query=_models.PutV3ManagementProjectKeywordsRequestQuery(project_id=project_id),
            body=_models.PutV3ManagementProjectKeywordsRequestBody(locations=locations, keywords=keywords)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_keywords: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/project-keywords"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_keywords")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_keywords", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_keywords",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def delete_keywords(
    project_id: int = Field(..., description="The unique identifier of the Rank Tracker project, found in the project URL within Ahrefs."),
    keywords: list[_models.PutV3ManagementProjectKeywordsDeleteBodyKeywordsItem] = Field(..., description="An array of keywords to remove from the project. Each keyword should be specified as a string value."),
) -> dict[str, Any] | ToolResult:
    """Remove one or more keywords from a Rank Tracker project. This operation is free and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.PutV3ManagementProjectKeywordsDeleteRequest(
            query=_models.PutV3ManagementProjectKeywordsDeleteRequestQuery(project_id=project_id),
            body=_models.PutV3ManagementProjectKeywordsDeleteRequestBody(keywords=keywords)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_keywords: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/project-keywords-delete"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_keywords")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_keywords", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_keywords",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def list_project_competitors(project_id: int = Field(..., description="The unique identifier of the project, found in the URL of your Rank Tracker project dashboard (the numeric ID in the project overview URL).")) -> dict[str, Any] | ToolResult:
    """Retrieve the list of competitors tracked for a specific project. This operation is free and does not consume any API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3ManagementProjectCompetitorsRequest(
            query=_models.GetV3ManagementProjectCompetitorsRequestQuery(project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_competitors: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/project-competitors"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_competitors")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_competitors", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_competitors",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def add_competitors(
    project_id: int = Field(..., description="The unique identifier of the Rank Tracker project. You can find this ID in the URL of your project dashboard (https://app.ahrefs.com/rank-tracker/overview/#project_id#)."),
    competitors: list[_models.PostV3ManagementProjectCompetitorsBodyCompetitorsItem] = Field(..., description="An array of competitor entries to add to the project. Each item represents a competitor domain or website to track."),
) -> dict[str, Any] | ToolResult:
    """Add competitors to a Rank Tracker project for monitoring and comparison. This operation is free and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.PostV3ManagementProjectCompetitorsRequest(
            query=_models.PostV3ManagementProjectCompetitorsRequestQuery(project_id=project_id),
            body=_models.PostV3ManagementProjectCompetitorsRequestBody(competitors=competitors)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_competitors: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/project-competitors"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_competitors")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_competitors", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_competitors",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def delete_competitors(
    project_id: int = Field(..., description="The unique identifier of the Rank Tracker project, found in the project URL within Ahrefs (e.g., https://app.ahrefs.com/rank-tracker/overview/#project_id#)."),
    competitors: list[_models.PostV3ManagementProjectCompetitorsDeleteBodyCompetitorsItem] = Field(..., description="An array of competitor identifiers to remove from the project. Each item should be a competitor ID."),
) -> dict[str, Any] | ToolResult:
    """Remove competitors from a Rank Tracker project. This operation is free and does not consume any API units."""

    # Construct request model with validation
    try:
        _request = _models.PostV3ManagementProjectCompetitorsDeleteRequest(
            query=_models.PostV3ManagementProjectCompetitorsDeleteRequestQuery(project_id=project_id),
            body=_models.PostV3ManagementProjectCompetitorsDeleteRequestBody(competitors=competitors)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_competitors: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/project-competitors-delete"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_competitors")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_competitors", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_competitors",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def list_locations(
    country_code: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(..., description="The two-letter ISO 3166-1 alpha-2 country code identifying the country for which to retrieve location and language information."),
    us_state: Literal["al", "ak", "az", "ar", "ca", "co", "ct", "de", "dc", "fl", "ga", "hi", "id", "il", "in", "ia", "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", "nj", "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "va", "wa", "wv", "wi", "wy"] | None = Field(None, description="The two-letter ISO 3166-2:US state code. Required only when country_code is set to 'us' to retrieve state-specific location and language data."),
) -> dict[str, Any] | ToolResult:
    """Retrieve available locations and supported languages for a specified country. This is a free operation that does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3ManagementLocationsRequest(
            query=_models.GetV3ManagementLocationsRequestQuery(country_code=country_code, us_state=us_state)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_locations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/locations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def list_keyword_list_keywords(keyword_list_id: int = Field(..., description="The unique identifier of the keyword list from which to retrieve keywords.")) -> dict[str, Any] | ToolResult:
    """Retrieve all keywords from a specified keyword list. This operation is free and does not consume any API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3ManagementKeywordListKeywordsRequest(
            query=_models.GetV3ManagementKeywordListKeywordsRequestQuery(keyword_list_id=keyword_list_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_keyword_list_keywords: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/keyword-list-keywords"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_keyword_list_keywords")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_keyword_list_keywords", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_keyword_list_keywords",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def add_keywords_to_list(
    keyword_list_id: int = Field(..., description="The unique identifier of the keyword list to update. Must reference an existing keyword list."),
    keywords: list[str] = Field(..., description="An array of keywords to add to the list. Each keyword is a string value; order is preserved as provided."),
) -> dict[str, Any] | ToolResult:
    """Add one or more keywords to an existing keyword list. The keywords will be appended to the list's current contents."""

    # Construct request model with validation
    try:
        _request = _models.PutV3ManagementKeywordListKeywordsRequest(
            query=_models.PutV3ManagementKeywordListKeywordsRequestQuery(keyword_list_id=keyword_list_id),
            body=_models.PutV3ManagementKeywordListKeywordsRequestBody(keywords=keywords)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_keywords_to_list: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/keyword-list-keywords"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_keywords_to_list")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_keywords_to_list", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_keywords_to_list",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def delete_keyword_list_keywords(
    keyword_list_id: int = Field(..., description="The unique identifier of the keyword list from which keywords will be removed."),
    keywords: list[str] = Field(..., description="An array of keywords to delete from the specified keyword list. Each keyword in the array will be removed from the list."),
) -> dict[str, Any] | ToolResult:
    """Remove one or more keywords from an existing keyword list. Specify the keyword list by its ID and provide the keywords to be deleted."""

    # Construct request model with validation
    try:
        _request = _models.PutV3ManagementKeywordListKeywordsDeleteRequest(
            query=_models.PutV3ManagementKeywordListKeywordsDeleteRequestQuery(keyword_list_id=keyword_list_id),
            body=_models.PutV3ManagementKeywordListKeywordsDeleteRequestBody(keywords=keywords)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_keyword_list_keywords: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/keyword-list-keywords-delete"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_keyword_list_keywords")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_keyword_list_keywords", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_keyword_list_keywords",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def list_brand_radar_prompts(report_id: str = Field(..., description="The unique identifier of the Brand Radar report. You can find this ID in the URL of your Brand Radar report within Ahrefs (the #report_id# segment in https://app.ahrefs.com/brand-radar/reports/#report_id#/...).")) -> dict[str, Any] | ToolResult:
    """Retrieve the Brand Radar prompts associated with a specific report. This operation is free and does not consume any API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3ManagementBrandRadarPromptsRequest(
            query=_models.GetV3ManagementBrandRadarPromptsRequestQuery(report_id=report_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_brand_radar_prompts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/brand-radar-prompts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_brand_radar_prompts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_brand_radar_prompts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_brand_radar_prompts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def create_brand_radar_prompt(
    report_id: str = Field(..., description="The unique identifier of the Brand Radar report where prompts will be applied. You can find this ID in the URL of your Brand Radar report in Ahrefs."),
    countries: list[str] = Field(..., description="A list of two-letter country codes in ISO 3166-1 alpha-2 format specifying the geographic regions for the prompts."),
    prompts: list[str] = Field(..., description="A list of custom prompts to apply to the report. Each prompt must be valid UTF-8 text and not exceed 400 characters in length."),
) -> dict[str, Any] | ToolResult:
    """Create custom prompts for Brand Radar reports to customize monitoring and analysis. This operation is free and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.PostV3ManagementBrandRadarPromptsRequest(
            query=_models.PostV3ManagementBrandRadarPromptsRequestQuery(report_id=report_id),
            body=_models.PostV3ManagementBrandRadarPromptsRequestBody(countries=countries, prompts=prompts)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_brand_radar_prompt: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/brand-radar-prompts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_brand_radar_prompt")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_brand_radar_prompt", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_brand_radar_prompt",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def delete_brand_radar_prompts(
    report_id: str = Field(..., description="The unique identifier of the Brand Radar report from which to delete prompts. You can find this ID in the URL of your Brand Radar report in Ahrefs."),
    prompts: list[str] = Field(..., description="List of custom prompts to delete. Each prompt must be valid UTF-8 encoded text and not exceed 400 characters in length."),
    countries: list[str] | None = Field(None, description="Optional list of two-letter country codes (ISO 3166-1 alpha-2 format) to scope the prompt deletion to specific countries."),
) -> dict[str, Any] | ToolResult:
    """Remove custom prompts from a Brand Radar report. This operation is free and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.PutV3ManagementBrandRadarPromptsDeleteRequest(
            query=_models.PutV3ManagementBrandRadarPromptsDeleteRequestQuery(report_id=report_id),
            body=_models.PutV3ManagementBrandRadarPromptsDeleteRequestBody(countries=countries, prompts=prompts)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_brand_radar_prompts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/brand-radar-prompts-delete"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_brand_radar_prompts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_brand_radar_prompts", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_brand_radar_prompts",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def list_brand_radar_reports() -> dict[str, Any] | ToolResult:
    """Retrieve brand radar reports to monitor brand performance and competitive insights. This endpoint is free to use and does not consume any API units."""

    # Extract parameters for API call
    _http_path = "/v3/management/brand-radar-reports"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_brand_radar_reports")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_brand_radar_reports", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_brand_radar_reports",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def create_brand_radar_report(
    data_source: Literal["chatgpt", "gemini", "perplexity", "copilot"] = Field(..., description="The AI data source to monitor for brand mentions. Choose from ChatGPT, Gemini, Perplexity, or Copilot."),
    frequency: Literal["daily", "weekly", "monthly", "off"] = Field(..., description="The update frequency for the report. Select daily for real-time monitoring, weekly for periodic summaries, monthly for long-term trends, or off to disable the report."),
    name: str | None = Field(None, description="A custom name for the report to help identify it in your dashboard."),
) -> dict[str, Any] | ToolResult:
    """Create a brand radar report that monitors brand mentions across AI-powered data sources. This operation is free and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.PostV3ManagementBrandRadarReportsRequest(
            body=_models.PostV3ManagementBrandRadarReportsRequestBody(data_source=data_source, frequency=frequency, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_brand_radar_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/brand-radar-reports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_brand_radar_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_brand_radar_report", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_brand_radar_report",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Management
@mcp.tool()
async def update_brand_radar_report(
    prompts_frequency: list[_models.PatchV3ManagementBrandRadarReportsBodyPromptsFrequencyItem] = Field(..., description="The frequency at which the report should generate prompts. Specify as an array of frequency values."),
    report_id: str = Field(..., description="The unique identifier of the Brand Radar report to update. You can find this ID in the URL of your report in Ahrefs at https://app.ahrefs.com/brand-radar/reports/#report_id#/..."),
) -> dict[str, Any] | ToolResult:
    """Update the configuration of a Brand Radar report, including its monitoring frequency. This operation is free and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.PatchV3ManagementBrandRadarReportsRequest(
            body=_models.PatchV3ManagementBrandRadarReportsRequestBody(prompts_frequency=prompts_frequency, report_id=report_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_brand_radar_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/management/brand-radar-reports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_brand_radar_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_brand_radar_report", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_brand_radar_report",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Brand Radar
@mcp.tool()
async def list_ai_responses(
    select: str = Field(..., description="Comma-separated list of columns to include in the response. Required to specify which data fields you want returned."),
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(..., description="Comma-separated list of chatbot models to query. Choose from Google AI Overviews, Google AI Mode, ChatGPT, Gemini, Perplexity, or Copilot. Note: Google models cannot be combined with each other or with non-Google models."),
    where: str | None = Field(None, description="Filter expression to narrow results using recognized column identifiers. Refer to the response schema for valid column names to use in filter conditions."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Defaults to 1000 if not specified."),
    date: str | None = Field(None, description="Specific date to search for, formatted as YYYY-MM-DD."),
    order_by: Literal["relevance", "volume"] | None = Field(None, description="Column to sort results by. Choose between relevance (default) or volume-based ordering."),
    report_id: str | None = Field(None, description="ID of a saved report to use as the base configuration. When provided, brand, competitors, market, and country settings are inherited from the report, though country and filters can be overridden."),
    prompts: Literal["ahrefs", "custom"] | None = Field(None, description="Type of prompts to use for generating responses. Choose Ahrefs prompts (standard pricing), custom prompts (free, requires report_id), or both (default). Custom prompts require a report_id to be provided."),
) -> dict[str, Any] | ToolResult:
    """Retrieve AI-generated responses from multiple chatbot models for brand-related queries. API unit consumption depends on prompt type: custom prompts are free, while Ahrefs prompts follow standard pricing."""

    # Construct request model with validation
    try:
        _request = _models.GetV3BrandRadarAiResponsesRequest(
            query=_models.GetV3BrandRadarAiResponsesRequestQuery(where=where, select=select, limit=limit, date=date, order_by=order_by, report_id=report_id, prompts=prompts, data_source=data_source)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_ai_responses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/brand-radar/ai-responses"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_ai_responses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_ai_responses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_ai_responses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Brand Radar
@mcp.tool()
async def list_cited_pages(
    select: str = Field(..., description="Comma-separated list of columns to include in the response. Required to specify which data fields you want returned."),
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(..., description="Comma-separated list of chatbot models to query. Choose from Google AI Overviews, Google AI Mode, ChatGPT, Gemini, Perplexity, or Copilot. Note: Google models cannot be combined with each other or with non-Google models in a single request."),
    where: str | None = Field(None, description="Filter expression to narrow results by specific column criteria. Refer to the response schema for valid column identifiers supported by this filter."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Defaults to 1000 if not specified."),
    date: str | None = Field(None, description="Specific date to search for in YYYY-MM-DD format. If omitted, returns results across all available dates."),
    report_id: str | None = Field(None, description="ID of a saved Brand Radar report to use as the configuration source. When provided, brand, competitors, market, and country settings are inherited from the report. You can find this ID in your Ahrefs Brand Radar report URL. Country and filter parameters will override report settings if also provided."),
    prompts: Literal["ahrefs", "custom"] | None = Field(None, description="Type of prompts to apply: 'ahrefs' for Ahrefs-generated prompts, 'custom' for your own prompts (requires report_id), or omit to use both types."),
) -> dict[str, Any] | ToolResult:
    """Retrieve pages that cite your brand across specified chatbot models and AI overviews. API unit consumption depends on the prompts parameter: custom prompt data requests are free, while requests including Ahrefs prompt data incur standard API unit charges."""

    # Construct request model with validation
    try:
        _request = _models.GetV3BrandRadarCitedPagesRequest(
            query=_models.GetV3BrandRadarCitedPagesRequestQuery(where=where, select=select, limit=limit, date=date, report_id=report_id, prompts=prompts, data_source=data_source)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_cited_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/brand-radar/cited-pages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_cited_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_cited_pages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_cited_pages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Brand Radar
@mcp.tool()
async def list_cited_domains(
    select: str = Field(..., description="Comma-separated list of column identifiers to include in the response. Required to specify which data fields you want returned."),
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(..., description="Comma-separated list of chatbot models and AI sources to query. Choose from Google AI Overviews, Google AI Mode, ChatGPT, Gemini, Perplexity, or Copilot. Note: Google models cannot be combined with each other or with non-Google models in a single request."),
    where: str | None = Field(None, description="Filter expression to narrow results using recognized column identifiers. Refer to the response schema for valid column names to use in filter conditions."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Defaults to 1000 if not specified."),
    date: str | None = Field(None, description="Specific date to retrieve data for, formatted as YYYY-MM-DD."),
    report_id: str | None = Field(None, description="ID of a saved Brand Radar report to use as the configuration source. When provided, brand, competitors, market, and country settings are inherited from the report. You can find this ID in the URL of your Brand Radar report in Ahrefs. Country and filter parameters can override report settings if provided."),
    prompts: Literal["ahrefs", "custom"] | None = Field(None, description="Type of prompts to use for analysis. Choose 'ahrefs' for Ahrefs-generated prompts, 'custom' for your own prompts (requires report_id), or omit to use both types."),
) -> dict[str, Any] | ToolResult:
    """Retrieve domains cited in AI visibility data from chatbot models and search engines. API unit consumption depends on the prompts parameter: requests using only custom prompts are free, while requests including Ahrefs prompts follow standard pricing."""

    # Construct request model with validation
    try:
        _request = _models.GetV3BrandRadarCitedDomainsRequest(
            query=_models.GetV3BrandRadarCitedDomainsRequestQuery(where=where, select=select, limit=limit, date=date, report_id=report_id, prompts=prompts, data_source=data_source)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_cited_domains: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/brand-radar/cited-domains"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_cited_domains")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_cited_domains", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_cited_domains",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Brand Radar
@mcp.tool()
async def list_brand_radar_impression_overviews(
    select: str = Field(..., description="Comma-separated list of columns to include in the response. Required parameter that determines which data fields are returned."),
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(..., description="Comma-separated list of chatbot models to query. Choose from: google_ai_overviews, google_ai_mode, chatgpt, gemini, perplexity, or copilot. Note: Google models cannot be combined with each other or with non-Google models in a single request."),
    where: str | None = Field(None, description="Filter expression to narrow results using recognized column identifiers. Refer to the response schema for valid column names to use in filter conditions."),
    report_id: str | None = Field(None, description="ID of an existing Brand Radar report to use as a configuration source. When provided, brand, competitors, market, and country settings are inherited from the report. Can be found in the URL of your Brand Radar report in Ahrefs. Country and filter parameters will override report settings if also provided."),
    prompts: Literal["ahrefs", "custom"] | None = Field(None, description="Type of prompts to use for data retrieval: 'ahrefs' for Ahrefs-generated prompts, 'custom' for user-defined prompts, or omit to use both types. Custom prompts require a report_id to be specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve impressions overview data for Brand Radar across specified chatbot models and data sources. API unit consumption depends on prompt type: custom prompts are free, while Ahrefs prompts follow standard pricing."""

    # Construct request model with validation
    try:
        _request = _models.GetV3BrandRadarImpressionsOverviewRequest(
            query=_models.GetV3BrandRadarImpressionsOverviewRequestQuery(where=where, select=select, report_id=report_id, prompts=prompts, data_source=data_source)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_brand_radar_impression_overviews: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/brand-radar/impressions-overview"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_brand_radar_impression_overviews")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_brand_radar_impression_overviews", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_brand_radar_impression_overviews",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Brand Radar
@mcp.tool()
async def list_brand_mentions_overview(
    select: str = Field(..., description="Comma-separated list of column identifiers to include in the response. Required to specify which data fields to return."),
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(..., description="Comma-separated list of AI chatbot models to query. Choose from Google AI Overviews, Google AI Mode, ChatGPT, Gemini, Perplexity, or Copilot. Note: Google models cannot be combined with each other or with non-Google models."),
    where: str | None = Field(None, description="Filter expression to narrow results using recognized column identifiers. Use this to apply conditions on the mentions data."),
    report_id: str | None = Field(None, description="The Brand Radar report ID to use as a template. When provided, brand, competitors, market, and country settings are inherited from the report. You can find this ID in your Brand Radar report URL. Country or filter parameters will override report settings if also provided."),
    prompts: Literal["ahrefs", "custom"] | None = Field(None, description="Type of prompts to apply to the data. Choose 'ahrefs' for Ahrefs-generated prompts, 'custom' for your own prompts (requires a report_id), or omit to use both types."),
) -> dict[str, Any] | ToolResult:
    """Retrieve an overview of brand mentions data across specified data sources. API unit consumption depends on prompt type: custom prompts only are free, while Ahrefs prompts follow standard pricing."""

    # Construct request model with validation
    try:
        _request = _models.GetV3BrandRadarMentionsOverviewRequest(
            query=_models.GetV3BrandRadarMentionsOverviewRequestQuery(where=where, select=select, report_id=report_id, prompts=prompts, data_source=data_source)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_brand_mentions_overview: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/brand-radar/mentions-overview"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_brand_mentions_overview")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_brand_mentions_overview", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_brand_mentions_overview",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Brand Radar
@mcp.tool()
async def get_share_of_voice_overview(
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(..., description="Comma-separated list of chatbot models to query. Google models (google_ai_overviews and google_ai_mode) cannot be combined with each other or with non-Google models. Required parameter."),
    where: str | None = Field(None, description="Filter expression to narrow results using recognized column identifiers specific to this endpoint."),
    report_id: str | None = Field(None, description="The Brand Radar report ID to use as a base configuration. When provided, brand, competitors, market, and country settings are inherited from the report, though country and filter parameters can override report settings if explicitly provided."),
    prompts: Literal["ahrefs", "custom"] | None = Field(None, description="Specify which prompt types to include: 'ahrefs' for Ahrefs-generated prompts, 'custom' for custom prompts (requires report_id), or omit to use both types."),
) -> dict[str, Any] | ToolResult:
    """Retrieve Share of Voice data for brands across specified data sources. API unit consumption depends on prompt type: custom prompts only are free, while Ahrefs prompts follow standard pricing."""

    # Construct request model with validation
    try:
        _request = _models.GetV3BrandRadarSovOverviewRequest(
            query=_models.GetV3BrandRadarSovOverviewRequestQuery(where=where, report_id=report_id, prompts=prompts, data_source=data_source)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_share_of_voice_overview: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/brand-radar/sov-overview"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_share_of_voice_overview")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_share_of_voice_overview", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_share_of_voice_overview",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Brand Radar
@mcp.tool()
async def list_brand_mention_impressions_history(
    brand: str = Field(..., description="The brand name to track for mentions and impressions."),
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(..., description="One or more AI chatbot platforms to query, provided as a comma-separated list. Google models (google_ai_overviews, google_ai_mode) cannot be combined with each other or with non-Google platforms (chatgpt, gemini, perplexity, copilot)."),
    date_from: str = Field(..., description="The start date for the historical period, formatted as YYYY-MM-DD."),
    date_to: str | None = Field(None, description="The end date for the historical period, formatted as YYYY-MM-DD. If omitted, defaults to the current date."),
    report_id: str | None = Field(None, description="The ID of a saved report to use as a template. When provided, market, country, and filter settings are inherited from the report, though country and filters can be overridden with explicit parameters."),
    prompts: Literal["ahrefs", "custom"] | None = Field(None, description="The type of prompts to include in results: 'ahrefs' for Ahrefs-generated prompts, 'custom' for user-defined prompts (requires report_id), or omit to include both types."),
    where: str | None = Field(None, description="A filter expression to narrow results. Supports recognized column identifiers for advanced filtering."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical impression data for brand mentions across AI chatbot platforms. API consumption varies based on prompt type: custom prompts are free, while Ahrefs prompts follow standard pricing."""

    # Construct request model with validation
    try:
        _request = _models.GetV3BrandRadarImpressionsHistoryRequest(
            query=_models.GetV3BrandRadarImpressionsHistoryRequestQuery(brand=brand, data_source=data_source, date_from=date_from, date_to=date_to, report_id=report_id, prompts=prompts, where=where)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_brand_mention_impressions_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/brand-radar/impressions-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_brand_mention_impressions_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_brand_mention_impressions_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_brand_mention_impressions_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Brand Radar
@mcp.tool()
async def list_brand_mention_history(
    brand: str = Field(..., description="The brand name to retrieve mention history for."),
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(..., description="One or more chatbot models to query, provided as a comma-separated list. Google models (google_ai_overviews, google_ai_mode) cannot be combined with each other or with non-Google models (chatgpt, gemini, perplexity, copilot)."),
    date_from: str = Field(..., description="The start date for the historical period in YYYY-MM-DD format (inclusive)."),
    date_to: str | None = Field(None, description="The end date for the historical period in YYYY-MM-DD format (inclusive). If omitted, defaults to the current date."),
    prompts: Literal["ahrefs", "custom"] | None = Field(None, description="Filter results to a specific prompt type: 'ahrefs' for Ahrefs-generated prompts or 'custom' for user-defined prompts. If not specified, both types are included. Custom prompts require a report_id."),
    report_id: str | None = Field(None, description="The Brand Radar report ID to use as a configuration source. When provided, market, country, and filter settings are inherited from the report, though country and filters parameters can override report settings. Find the report ID in your Ahrefs Brand Radar report URL."),
    where: str | None = Field(None, description="A filter expression to narrow results by specific columns. Refer to API documentation for recognized column identifiers."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical mention data for a brand across specified AI chatbot models and date range. API consumption varies based on prompt type: custom prompts are free, while Ahrefs prompts follow standard pricing."""

    # Construct request model with validation
    try:
        _request = _models.GetV3BrandRadarMentionsHistoryRequest(
            query=_models.GetV3BrandRadarMentionsHistoryRequestQuery(brand=brand, data_source=data_source, date_from=date_from, date_to=date_to, prompts=prompts, report_id=report_id, where=where)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_brand_mention_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/brand-radar/mentions-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_brand_mention_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_brand_mention_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_brand_mention_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Brand Radar
@mcp.tool()
async def list_brand_sov_history(
    date_from: str = Field(..., description="Start date for the historical period in YYYY-MM-DD format."),
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(..., description="Comma-separated list of chatbot models to analyze (google_ai_overviews, google_ai_mode, chatgpt, gemini, perplexity, or copilot). Google models cannot be combined with each other or with non-Google models."),
    date_to: str | None = Field(None, description="End date for the historical period in YYYY-MM-DD format. If omitted, defaults to the current date."),
    where: str | None = Field(None, description="Optional filter expression to narrow results based on specific column identifiers."),
    report_id: str | None = Field(None, description="ID of an existing Brand Radar report to use as a template. When provided, brand, competitors, market, and country settings are inherited from the report, though country and filters parameters can override report settings."),
    prompts: Literal["ahrefs", "custom"] | None = Field(None, description="Type of prompts to include in results: 'ahrefs' for Ahrefs-generated prompts, 'custom' for user-defined prompts (requires report_id), or omit to include both types."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical Share of Voice data for brands across specified chatbot models and date ranges. API unit consumption depends on prompt type: custom prompts only are free, while Ahrefs prompts follow standard pricing."""

    # Construct request model with validation
    try:
        _request = _models.GetV3BrandRadarSovHistoryRequest(
            query=_models.GetV3BrandRadarSovHistoryRequestQuery(date_from=date_from, date_to=date_to, data_source=data_source, where=where, report_id=report_id, prompts=prompts)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_brand_sov_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/brand-radar/sov-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_brand_sov_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_brand_sov_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_brand_sov_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_web_analytics_stats(
    project_id: int = Field(..., description="The unique identifier of the project for which to retrieve analytics statistics."),
    from_: str | None = Field(None, alias="from", description="Start of the date range for the analytics query, specified in ISO 8601 format. If omitted, defaults to the earliest available data."),
    to: str | None = Field(None, description="End of the date range for the analytics query, specified in ISO 8601 format. If omitted, defaults to the current date."),
    where: str | None = Field(None, description="Filter expression to narrow results by dimensions and metrics. Use standard filter syntax to specify conditions on available dimensions and metrics."),
    order_by: str | None = Field(None, description="Sort results by a metric in ascending or descending order, specified as metric_name:asc or metric_name:desc."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Useful for pagination and controlling response size."),
) -> dict[str, Any] | ToolResult:
    """Retrieve aggregated web analytics statistics for a project, with optional filtering, sorting, and date range constraints."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsStatsRequest(
            query=_models.GetV3WebAnalyticsStatsRequestQuery(project_id=project_id, from_=from_, to=to, where=where, order_by=order_by, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_web_analytics_stats: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/stats"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_web_analytics_stats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_web_analytics_stats", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_web_analytics_stats",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_web_analytics_chart(
    project_id: int = Field(..., description="The unique identifier for the project whose analytics data you want to retrieve."),
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="The time interval for aggregating data points. Choose from hourly, daily, weekly, or monthly granularity depending on the level of detail needed."),
    where: str | None = Field(None, description="Optional filter expression to narrow results by specific dimensions and metrics. Use standard filter syntax to refine the data returned."),
    from_: str | None = Field(None, alias="from", description="Optional start datetime for the query range. Specify in ISO 8601 format to define when the data collection period begins."),
    to: str | None = Field(None, description="Optional end datetime for the query range. Specify in ISO 8601 format to define when the data collection period ends."),
) -> dict[str, Any] | ToolResult:
    """Retrieve time-series chart data for web analytics metrics with configurable time granularity. Use this to visualize analytics trends across different time periods."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsChartRequest(
            query=_models.GetV3WebAnalyticsChartRequestQuery(project_id=project_id, granularity=granularity, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_web_analytics_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_web_analytics_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_web_analytics_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_web_analytics_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_source_channels(
    project_id: int = Field(..., description="The unique identifier for the project whose source channel analytics you want to retrieve."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response."),
    order_by: str | None = Field(None, description="Sort results by a metric in ascending or descending order. Supported metrics include visitors, session_bounce_rate, and avg_session_duration_sec."),
    where: str | None = Field(None, description="Filter results using expressions that reference dimensions and metrics to narrow down the data returned."),
    from_: str | None = Field(None, alias="from", description="Start of the date range for the analytics query in ISO 8601 datetime format."),
    to: str | None = Field(None, description="End of the date range for the analytics query in ISO 8601 datetime format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve web analytics data grouped by source channels, including visitor counts, bounce rates, and session duration metrics. This endpoint is free and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsSourceChannelsRequest(
            query=_models.GetV3WebAnalyticsSourceChannelsRequestQuery(project_id=project_id, limit=limit, order_by=order_by, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_source_channels: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/source-channels"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_source_channels")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_source_channels", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_source_channels",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_source_channels_chart(
    project_id: int = Field(..., description="The unique identifier for the project whose analytics data should be retrieved."),
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="The time interval for aggregating data points in the chart. Choose from hourly, daily, weekly, or monthly granularity."),
    source_channels_to_chart: str | None = Field(None, description="Comma-separated list of source channels to include in the chart. If not specified, defaults to the top 5 channels by visitor count."),
    where: str | None = Field(None, description="Filter expression to narrow results by dimensions and metrics. Use standard filter syntax to refine the dataset."),
    from_: str | None = Field(None, alias="from", description="Start datetime for the data query range. Use ISO 8601 format to define the beginning of the analysis period."),
    to: str | None = Field(None, description="End datetime for the data query range. Use ISO 8601 format to define the end of the analysis period."),
) -> dict[str, Any] | ToolResult:
    """Retrieve source channels chart data with visitor analytics and session metrics, aggregated at the specified time granularity."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsSourceChannelsChartRequest(
            query=_models.GetV3WebAnalyticsSourceChannelsChartRequestQuery(project_id=project_id, granularity=granularity, source_channels_to_chart=source_channels_to_chart, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_source_channels_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/source-channels-chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_source_channels_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_source_channels_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_source_channels_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_traffic_sources(
    project_id: int = Field(..., description="The unique identifier of the project to retrieve traffic sources for."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response."),
    order_by: str | None = Field(None, description="Sort results by a specific metric in ascending or descending order using the format metric:asc or metric:desc."),
    where: str | None = Field(None, description="Filter results using expressions that reference available dimensions and metrics to narrow down the data."),
    from_: str | None = Field(None, alias="from", description="Start of the date range for the query in ISO 8601 datetime format."),
    to: str | None = Field(None, description="End of the date range for the query in ISO 8601 datetime format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve traffic sources data for a project, showing where visitors are coming from. Results can be filtered by date range and custom criteria, with optional sorting and pagination."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsSourcesRequest(
            query=_models.GetV3WebAnalyticsSourcesRequestQuery(project_id=project_id, limit=limit, order_by=order_by, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_traffic_sources: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/sources"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_traffic_sources")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_traffic_sources", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_traffic_sources",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_traffic_sources_chart(
    project_id: int = Field(..., description="The unique identifier for the project whose traffic sources you want to analyze."),
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="The time interval for grouping data points in the chart. Choose from hourly, daily, weekly, or monthly granularity."),
    sources_to_chart: str | None = Field(None, description="Comma-separated list of traffic sources to include in the chart. If not specified, the top 5 sources by visitor count are displayed by default."),
    where: str | None = Field(None, description="Optional filter expression to narrow results by dimensions and metrics relevant to your traffic sources data."),
    from_: str | None = Field(None, alias="from", description="Start datetime for the data query range in ISO 8601 format. If omitted, data retrieval begins from the earliest available records."),
    to: str | None = Field(None, description="End datetime for the data query range in ISO 8601 format. If omitted, data retrieval extends to the most recent available records."),
) -> dict[str, Any] | ToolResult:
    """Retrieve traffic sources chart data with visitor metrics aggregated by your specified time granularity (hourly, daily, weekly, or monthly). This endpoint is free to use and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsSourcesChartRequest(
            query=_models.GetV3WebAnalyticsSourcesChartRequestQuery(project_id=project_id, granularity=granularity, sources_to_chart=sources_to_chart, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_traffic_sources_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/sources-chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_traffic_sources_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_traffic_sources_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_traffic_sources_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_referrers(
    project_id: int = Field(..., description="The unique identifier of the project for which to retrieve referrer analytics."),
    limit: int | None = Field(None, description="Maximum number of referrer records to return in the response."),
    order_by: str | None = Field(None, description="Sort results by a specific metric in ascending or descending order using the format `metric:asc` or `metric:desc`."),
    where: str | None = Field(None, description="Filter results using a filter expression that can reference available dimensions and metrics to narrow down referrer data."),
    from_: str | None = Field(None, alias="from", description="Start of the date range for the analytics query in ISO 8601 datetime format."),
    to: str | None = Field(None, description="End of the date range for the analytics query in ISO 8601 datetime format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve referrer traffic sources and their associated metrics for a project, with optional filtering, sorting, and date range selection."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsReferrersRequest(
            query=_models.GetV3WebAnalyticsReferrersRequestQuery(project_id=project_id, limit=limit, order_by=order_by, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_referrers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/referrers"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_referrers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_referrers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_referrers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_referrers_chart(
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="Time granularity for data points in the chart. Choose from hourly, daily, weekly, or monthly intervals."),
    project_id: int = Field(..., description="The unique identifier for the project whose referrers data should be retrieved."),
    source_referers_to_chart: str | None = Field(None, description="Comma-separated list of referrer values to include in the chart. If not specified, defaults to the top 5 referrers by visitor count."),
    where: str | None = Field(None, description="Filter expression to narrow results by dimensions and metrics. Use standard filter syntax to refine the data returned."),
    to: str | None = Field(None, description="End datetime for the data query range. Use ISO 8601 format for the timestamp."),
    from_: str | None = Field(None, alias="from", description="Start datetime for the data query range. Use ISO 8601 format for the timestamp."),
) -> dict[str, Any] | ToolResult:
    """Retrieve referrers chart data for web analytics, showing traffic sources over a specified time period with configurable granularity and filtering options."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsReferrersChartRequest(
            query=_models.GetV3WebAnalyticsReferrersChartRequestQuery(source_referers_to_chart=source_referers_to_chart, where=where, granularity=granularity, to=to, from_=from_, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_referrers_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/referrers-chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_referrers_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_referrers_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_referrers_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_utm_parameters(
    utm_param: Literal["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"] = Field(..., description="The UTM parameter to use as the grouping dimension. Choose from: utm_source, utm_medium, utm_campaign, utm_term, or utm_content."),
    project_id: int = Field(..., description="The unique identifier of the project for which to retrieve UTM parameter analytics."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response."),
    order_by: str | None = Field(None, description="Sort results by a metric in ascending or descending order using the format metric:asc or metric:desc."),
    where: str | None = Field(None, description="Filter results using expressions that reference available dimensions and metrics."),
    to: str | None = Field(None, description="End datetime for the data query range in ISO 8601 format."),
    from_: str | None = Field(None, alias="from", description="Start datetime for the data query range in ISO 8601 format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve UTM parameter data for web analytics, grouped by a specified UTM dimension (source, medium, campaign, term, or content) with optional filtering and time range selection."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsUtmParamsRequest(
            query=_models.GetV3WebAnalyticsUtmParamsRequestQuery(limit=limit, order_by=order_by, where=where, to=to, from_=from_, utm_param=utm_param, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_utm_parameters: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/utm-params"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_utm_parameters")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_utm_parameters", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_utm_parameters",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_utm_params_chart(
    project_id: int = Field(..., description="The unique identifier for the project whose analytics data you want to retrieve."),
    utm_param: Literal["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"] = Field(..., description="The UTM parameter to use as the primary dimension for the chart. Choose from: utm_source, utm_medium, utm_campaign, utm_term, or utm_content."),
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="The time interval for data aggregation in the chart. Choose from: hourly, daily, weekly, or monthly granularity."),
    utm_params_to_chart: str | None = Field(None, description="Optional comma-separated list of specific UTM parameter values to include in the chart. If omitted, the top 5 values by visitor count are displayed by default."),
    where: str | None = Field(None, description="Optional filter expression to refine the data. You can reference available dimensions and metrics to narrow results based on specific criteria."),
    from_: str | None = Field(None, alias="from", description="Optional start datetime for the data query range. Use ISO 8601 format to define when the analytics period begins."),
    to: str | None = Field(None, description="Optional end datetime for the data query range. Use ISO 8601 format to define when the analytics period ends."),
) -> dict[str, Any] | ToolResult:
    """Retrieve UTM parameters chart data for web analytics, visualizing traffic patterns across a specified UTM dimension over time. Use this to analyze campaign performance, traffic sources, or other UTM-tracked metrics."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsUtmParamsChartRequest(
            query=_models.GetV3WebAnalyticsUtmParamsChartRequestQuery(project_id=project_id, utm_param=utm_param, granularity=granularity, utm_params_to_chart=utm_params_to_chart, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_utm_params_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/utm-params-chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_utm_params_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_utm_params_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_utm_params_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_entry_pages(
    project_id: int = Field(..., description="The unique identifier for the project whose entry pages data should be retrieved."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Useful for pagination and controlling response size."),
    from_: str | None = Field(None, alias="from", description="Start of the date range for analytics data in ISO 8601 format. Only data from this datetime onward will be included."),
    to: str | None = Field(None, description="End of the date range for analytics data in ISO 8601 format. Only data up to this datetime will be included."),
    order_by_metric: str | None = Field(None, description="Metric to order by. Supported values: entry_page, visitors, entries, avg_session_duration_sec"),
    order_by_direction: str | None = Field(None, description="Sort direction: 'asc' for ascending or 'desc' for descending"),
    where_column: str | None = Field(None, description="Column identifier to filter on (e.g., 'backlinks', 'url_rating_source', 'domain_rating_source')"),
    where_operator: str | None = Field(None, description="Comparison operator: '>', '<', '>=', '<=', '==', '!=' (default: '==')"),
    where_value: str | None = Field(None, description="Value to compare against (will be properly escaped)"),
) -> dict[str, Any] | ToolResult:
    """Retrieve entry pages analytics data for a project, showing which pages users first land on. Supports filtering by date range and result limits."""

    # Call helper functions
    order_by = build_order_by(order_by_metric, order_by_direction)
    where = build_where_filter(where_column, where_operator, where_value)

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsEntryPagesRequest(
            query=_models.GetV3WebAnalyticsEntryPagesRequestQuery(project_id=project_id, limit=limit, from_=from_, to=to, order_by=order_by, where=where)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_entry_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/entry-pages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_entry_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_entry_pages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_entry_pages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_entry_pages_chart(
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="Set the time interval for data points on the chart: hourly, daily, weekly, or monthly granularity."),
    project_id: int = Field(..., description="The unique identifier of the project for which to retrieve entry pages chart data."),
    entry_pages_to_chart: str | None = Field(None, description="Specify which entry page metrics to display on the chart as a comma-separated list. Defaults to the top 5 pages by visitor count if not provided."),
    where: str | None = Field(None, description="Apply filters to the data using dimension and metric expressions to narrow results to specific criteria."),
    to: str | None = Field(None, description="End datetime for the data query range in ISO 8601 format."),
    from_: str | None = Field(None, alias="from", description="Start datetime for the data query range in ISO 8601 format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve entry pages chart data for a project, showing visitor traffic patterns across specified time periods. This endpoint is free and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsEntryPagesChartRequest(
            query=_models.GetV3WebAnalyticsEntryPagesChartRequestQuery(entry_pages_to_chart=entry_pages_to_chart, where=where, granularity=granularity, to=to, from_=from_, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_entry_pages_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/entry-pages-chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_entry_pages_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_entry_pages_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_entry_pages_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_exit_pages(
    project_id: int = Field(..., description="The unique identifier of the project to retrieve exit pages data for."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response."),
    order_by: str | None = Field(None, description="Sort results by a metric in ascending or descending order using the format `metric:asc` or `metric:desc`."),
    where: str | None = Field(None, description="Filter results using expressions that reference available dimensions and metrics to narrow down the data."),
    from_: str | None = Field(None, alias="from", description="Start of the date range for the query in ISO 8601 datetime format."),
    to: str | None = Field(None, description="End of the date range for the query in ISO 8601 datetime format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve exit pages analytics data for a project, showing which pages users exit from most frequently. Supports filtering, sorting, and date range specification."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsExitPagesRequest(
            query=_models.GetV3WebAnalyticsExitPagesRequestQuery(project_id=project_id, limit=limit, order_by=order_by, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_exit_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/exit-pages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_exit_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_exit_pages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_exit_pages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_exit_pages_chart(
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="Time granularity for aggregating chart data points. Choose from hourly, daily, weekly, or monthly intervals."),
    project_id: int = Field(..., description="The unique identifier of the project to retrieve exit pages data for."),
    exit_pages_to_chart: str | None = Field(None, description="Specify which exit page metrics to display on the chart as a comma-separated list. If not provided, defaults to the top 5 pages by visitor count."),
    where: str | None = Field(None, description="Filter the data using expressions that reference available dimensions and metrics to narrow results."),
    to: str | None = Field(None, description="End datetime for the data query range. Use ISO 8601 format."),
    from_: str | None = Field(None, alias="from", description="Start datetime for the data query range. Use ISO 8601 format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve exit pages chart data for a project, showing which pages visitors exit from. Supports filtering, time-based aggregation, and customizable metrics selection."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsExitPagesChartRequest(
            query=_models.GetV3WebAnalyticsExitPagesChartRequestQuery(exit_pages_to_chart=exit_pages_to_chart, where=where, granularity=granularity, to=to, from_=from_, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_exit_pages_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/exit-pages-chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_exit_pages_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_exit_pages_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_exit_pages_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_top_pages_by_pageviews(
    project_id: int = Field(..., description="The unique identifier for the project whose page analytics you want to retrieve."),
    limit: int | None = Field(None, description="Maximum number of top pages to return in the results. Defaults to a system-defined limit if not specified."),
    order_by: str | None = Field(None, description="Sort results by a specific metric in ascending or descending order. Supported metrics include pageviews, visitors, session_bounce_rate, and avg_page_visit_duration_sec. Use the format metric:asc or metric:desc."),
    where: str | None = Field(None, description="Apply filters to narrow results by dimensions and metrics. Specify filter conditions to focus on specific pages or traffic characteristics."),
    from_: str | None = Field(None, alias="from", description="Start of the date range for the analytics query. Specify as an ISO 8601 formatted datetime."),
    to: str | None = Field(None, description="End of the date range for the analytics query. Specify as an ISO 8601 formatted datetime."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the top-performing pages for a project ranked by pageviews and other engagement metrics. Use filtering and date range parameters to analyze specific traffic patterns and time periods."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsTopPagesRequest(
            query=_models.GetV3WebAnalyticsTopPagesRequestQuery(project_id=project_id, limit=limit, order_by=order_by, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_top_pages_by_pageviews: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/top-pages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_top_pages_by_pageviews")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_top_pages_by_pageviews", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_top_pages_by_pageviews",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_top_pages_chart(
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="Time granularity for data aggregation: hourly, daily, weekly, or monthly."),
    project_id: int = Field(..., description="The numeric identifier of the project to retrieve analytics for."),
    pages_to_chart: str | None = Field(None, description="Comma-separated list of values to display on the chart. If not specified, defaults to the top 5 pages by visitor count."),
    where: str | None = Field(None, description="Filter expression to narrow results by dimensions and metrics (e.g., country, device type, traffic source)."),
    to: str | None = Field(None, description="End datetime for the data query range in ISO 8601 format."),
    from_: str | None = Field(None, alias="from", description="Start datetime for the data query range in ISO 8601 format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a chart of your top-performing pages with visitor metrics and engagement statistics, aggregated at your specified time granularity."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsTopPagesChartRequest(
            query=_models.GetV3WebAnalyticsTopPagesChartRequestQuery(pages_to_chart=pages_to_chart, where=where, granularity=granularity, to=to, from_=from_, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_top_pages_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/top-pages-chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_top_pages_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_top_pages_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_top_pages_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_web_analytics_by_city(
    project_id: int = Field(..., description="The unique identifier of the project for which to retrieve city-level analytics data."),
    limit: int | None = Field(None, description="Maximum number of city results to return in the response. If not specified, a default limit applies."),
    order_by: str | None = Field(None, description="Sort results by a specific metric in ascending or descending order using the format `metric:asc` or `metric:desc`."),
    where: str | None = Field(None, description="Filter results using expressions that reference available dimensions and metrics. Allows narrowing data to specific criteria."),
    from_: str | None = Field(None, alias="from", description="Start of the date range for the analytics query in ISO 8601 datetime format. Data returned will be from this point forward."),
    to: str | None = Field(None, description="End of the date range for the analytics query in ISO 8601 datetime format. Data returned will be up to this point."),
) -> dict[str, Any] | ToolResult:
    """Retrieve web analytics metrics aggregated by city for a specified project. This endpoint is free to use and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsCitiesRequest(
            query=_models.GetV3WebAnalyticsCitiesRequestQuery(project_id=project_id, limit=limit, order_by=order_by, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_web_analytics_by_city: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/cities"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_web_analytics_by_city")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_web_analytics_by_city", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_web_analytics_by_city",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_web_analytics_cities_chart(
    project_id: int = Field(..., description="The unique identifier for the project whose analytics data you want to retrieve."),
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="The time interval for data aggregation. Choose from hourly, daily, weekly, or monthly granularity to control the resolution of your chart data points."),
    cities_to_chart: str | None = Field(None, description="Comma-separated list of specific cities to include in the chart. If not specified, the top 5 cities by visitor count are displayed by default."),
    where: str | None = Field(None, description="Optional filter expression to narrow results based on dimensions and metrics. Use this to segment data by specific criteria."),
    from_: str | None = Field(None, alias="from", description="The start datetime for the data query range. Use ISO 8601 format to specify when the analytics period begins."),
    to: str | None = Field(None, description="The end datetime for the data query range. Use ISO 8601 format to specify when the analytics period ends."),
) -> dict[str, Any] | ToolResult:
    """Retrieve cities chart data for web analytics showing visitor distribution across geographic locations. This endpoint is free to use and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsCitiesChartRequest(
            query=_models.GetV3WebAnalyticsCitiesChartRequestQuery(project_id=project_id, granularity=granularity, cities_to_chart=cities_to_chart, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_web_analytics_cities_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/cities-chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_web_analytics_cities_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_web_analytics_cities_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_web_analytics_cities_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_continent_analytics(
    project_id: int = Field(..., description="The unique identifier for the project whose analytics data you want to retrieve."),
    limit: int | None = Field(None, description="Maximum number of continent records to return in the response."),
    order_by: str | None = Field(None, description="Sort results by a specific metric in ascending or descending order using the format `metric:asc` or `metric:desc`."),
    where: str | None = Field(None, description="Filter results using expressions that reference available dimensions and metrics to narrow down the data returned."),
    from_: str | None = Field(None, alias="from", description="Start of the date range for the analytics query in ISO 8601 datetime format."),
    to: str | None = Field(None, description="End of the date range for the analytics query in ISO 8601 datetime format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve web analytics metrics aggregated by continent for a specified project and time period. This endpoint is free to use and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsContinentsRequest(
            query=_models.GetV3WebAnalyticsContinentsRequestQuery(project_id=project_id, limit=limit, order_by=order_by, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_continent_analytics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/continents"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_continent_analytics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_continent_analytics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_continent_analytics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_continents_chart(
    project_id: int = Field(..., description="The unique identifier for the project whose analytics data you want to retrieve."),
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="The time interval for data aggregation. Choose from hourly, daily, weekly, or monthly granularity."),
    continents_to_chart: str | None = Field(None, description="Comma-separated list of continents to include in the chart. If not specified, the top 5 continents by visitor count are displayed by default."),
    where: str | None = Field(None, description="Filter expression to narrow results based on dimensions and metrics. Use standard filter syntax to refine the data."),
    from_: str | None = Field(None, alias="from", description="Start of the date range for the query in ISO 8601 format. Data will be included from this datetime onwards."),
    to: str | None = Field(None, description="End of the date range for the query in ISO 8601 format. Data will be included up to this datetime."),
) -> dict[str, Any] | ToolResult:
    """Retrieve web analytics chart data aggregated by continent. This endpoint is free to use and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsContinentsChartRequest(
            query=_models.GetV3WebAnalyticsContinentsChartRequestQuery(project_id=project_id, granularity=granularity, continents_to_chart=continents_to_chart, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_continents_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/continents-chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_continents_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_continents_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_continents_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_web_analytics_by_country(
    project_id: int = Field(..., description="The unique identifier of the project for which to retrieve country-level web analytics data."),
    limit: int | None = Field(None, description="Maximum number of country records to return in the response. Use this to paginate through large result sets."),
    order_by: str | None = Field(None, description="Sort results by a specific metric in ascending or descending order using the format `metric:asc` or `metric:desc`."),
    where: str | None = Field(None, description="Filter results using expressions that reference available dimensions and metrics. Enables targeted analysis of specific geographic or performance segments."),
    to: str | None = Field(None, description="End datetime for the analytics query range in ISO 8601 format. Data will be included up to this point in time."),
    from_: str | None = Field(None, alias="from", description="Start datetime for the analytics query range in ISO 8601 format. Data will be included from this point forward."),
) -> dict[str, Any] | ToolResult:
    """Retrieve web analytics metrics aggregated by country for a specified project and time period. Results can be filtered, sorted, and paginated to analyze geographic performance data."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsCountriesRequest(
            query=_models.GetV3WebAnalyticsCountriesRequestQuery(limit=limit, order_by=order_by, where=where, to=to, from_=from_, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_web_analytics_by_country: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/countries"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_web_analytics_by_country")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_web_analytics_by_country", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_web_analytics_by_country",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_countries_chart(
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="Time granularity for data points: hourly, daily, weekly, or monthly aggregation."),
    project_id: int = Field(..., description="The numeric identifier of the project to retrieve analytics for."),
    countries_to_chart: str | None = Field(None, description="Comma-separated list of countries to include in the chart. If not specified, defaults to the top 5 countries by visitor count."),
    where: str | None = Field(None, description="Filter expression to narrow results by dimensions and metrics (e.g., visitor count thresholds, traffic source)."),
    to: str | None = Field(None, description="End datetime for the query range in ISO 8601 format. If omitted, defaults to the current time."),
    from_: str | None = Field(None, alias="from", description="Start datetime for the query range in ISO 8601 format. If omitted, defaults to a standard lookback period."),
) -> dict[str, Any] | ToolResult:
    """Retrieve web analytics chart data aggregated by country with configurable time granularity and filtering. This endpoint is free and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsCountriesChartRequest(
            query=_models.GetV3WebAnalyticsCountriesChartRequestQuery(countries_to_chart=countries_to_chart, where=where, granularity=granularity, to=to, from_=from_, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_countries_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/countries-chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_countries_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_countries_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_countries_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_language_analytics(
    project_id: int = Field(..., description="The unique identifier of the project for which to retrieve language analytics data."),
    limit: int | None = Field(None, description="Maximum number of language records to return in the response. Useful for pagination or limiting result set size."),
    order_by: str | None = Field(None, description="Sort results by a specific metric in ascending or descending order using the format metric:asc or metric:desc."),
    where: str | None = Field(None, description="Filter results using expressions that reference available dimensions and metrics to narrow down the dataset."),
    from_: str | None = Field(None, alias="from", description="Start of the date range for the analytics query in ISO 8601 datetime format. Data returned will be from this point forward."),
    to: str | None = Field(None, description="End of the date range for the analytics query in ISO 8601 datetime format. Data returned will be up to this point."),
) -> dict[str, Any] | ToolResult:
    """Retrieve browser language statistics for a project, showing how visitors are distributed across different language preferences. This endpoint is free to use and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsLanguagesRequest(
            query=_models.GetV3WebAnalyticsLanguagesRequestQuery(project_id=project_id, limit=limit, order_by=order_by, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_language_analytics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/languages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_language_analytics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_language_analytics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_language_analytics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_language_analytics_chart(
    project_id: int = Field(..., description="The unique identifier for the project whose language analytics data should be retrieved."),
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="The time interval for aggregating data points in the chart. Choose from hourly, daily, weekly, or monthly granularity."),
    browser_language_to_chart: str | None = Field(None, description="Comma-separated list of browser languages to include in the chart. If not specified, the top 5 languages by visitor count are displayed by default."),
    where: str | None = Field(None, description="Optional filter expression to narrow results based on dimensions and metrics available in the analytics dataset."),
    from_: str | None = Field(None, alias="from", description="Start datetime for the analytics query range in ISO 8601 format. If omitted, defaults to an appropriate historical starting point."),
    to: str | None = Field(None, description="End datetime for the analytics query range in ISO 8601 format. If omitted, defaults to the current time."),
) -> dict[str, Any] | ToolResult:
    """Retrieve browser language distribution data for web analytics with support for time-series charting across different granularities. This endpoint is free to use and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsLanguagesChartRequest(
            query=_models.GetV3WebAnalyticsLanguagesChartRequestQuery(project_id=project_id, granularity=granularity, browser_language_to_chart=browser_language_to_chart, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_language_analytics_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/languages-chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_language_analytics_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_language_analytics_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_language_analytics_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_browser_analytics(
    project_id: int = Field(..., description="The unique identifier of the project for which to retrieve browser analytics data."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response."),
    order_by: str | None = Field(None, description="Sort results by a specific metric in ascending or descending order. Supported metrics include browser name, visitor count, session bounce rate, and average session duration in seconds."),
    where: str | None = Field(None, description="Filter results using expressions that reference dimensions (such as browser) and metrics (such as visitors or bounce rate)."),
    from_: str | None = Field(None, alias="from", description="Start of the date range for the analytics query in ISO 8601 datetime format."),
    to: str | None = Field(None, description="End of the date range for the analytics query in ISO 8601 datetime format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve browser analytics data for a project, including visitor counts, bounce rates, and session duration metrics. This endpoint is free and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsBrowsersRequest(
            query=_models.GetV3WebAnalyticsBrowsersRequestQuery(project_id=project_id, limit=limit, order_by=order_by, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_browser_analytics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/browsers"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_browser_analytics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_browser_analytics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_browser_analytics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_browser_chart(
    project_id: int = Field(..., description="The unique identifier of the project for which to retrieve browser analytics data."),
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="The time interval for aggregating data points in the chart. Choose from hourly, daily, weekly, or monthly granularity."),
    browser_to_chart: str | None = Field(None, description="Comma-separated list of browsers to include in the chart. If not specified, the top 5 browsers by visitor count are displayed by default."),
    where: str | None = Field(None, description="Filter expression to narrow results based on dimensions and metrics. Use this to segment data by specific criteria."),
    from_: str | None = Field(None, alias="from", description="Start datetime for the data query range. Use ISO 8601 format to define when the analytics period begins."),
    to: str | None = Field(None, description="End datetime for the data query range. Use ISO 8601 format to define when the analytics period ends."),
) -> dict[str, Any] | ToolResult:
    """Retrieve browser usage chart data for a project, showing visitor distribution across different browsers over a specified time period with configurable granularity."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsBrowsersChartRequest(
            query=_models.GetV3WebAnalyticsBrowsersChartRequestQuery(project_id=project_id, granularity=granularity, browser_to_chart=browser_to_chart, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_browser_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/browsers-chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_browser_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_browser_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_browser_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_browser_versions(
    project_id: int = Field(..., description="The unique identifier for the project whose browser version data you want to retrieve."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. If not specified, a default limit applies."),
    order_by: str | None = Field(None, description="Sort results by a specific metric in ascending or descending order using the format `metric:asc` or `metric:desc`."),
    where: str | None = Field(None, description="Filter results using expressions that reference available dimensions and metrics. Allows you to narrow down the data returned."),
    from_: str | None = Field(None, alias="from", description="Start of the date range for the query in ISO 8601 datetime format. Data returned will be from this point forward."),
    to: str | None = Field(None, description="End of the date range for the query in ISO 8601 datetime format. Data returned will be up to this point."),
) -> dict[str, Any] | ToolResult:
    """Retrieve browser version statistics and metrics for web analytics. This endpoint is free to use and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsBrowserVersionsRequest(
            query=_models.GetV3WebAnalyticsBrowserVersionsRequestQuery(project_id=project_id, limit=limit, order_by=order_by, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_browser_versions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/browser-versions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_browser_versions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_browser_versions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_browser_versions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_browser_versions_chart(
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="Time interval for chart data points. Choose from hourly, daily, weekly, or monthly granularity."),
    project_id: int = Field(..., description="The unique identifier of the project to retrieve analytics data for."),
    browser_version_to_chart: str | None = Field(None, description="Comma-separated list of browser versions to include in the chart. If not specified, defaults to the top 5 browser versions by visitor count."),
    where: str | None = Field(None, description="Filter expression to narrow results by dimensions and metrics (e.g., country, device type, traffic source)."),
    to: str | None = Field(None, description="End date and time for the data query in ISO 8601 format. If omitted, defaults to the current time."),
    from_: str | None = Field(None, alias="from", description="Start date and time for the data query in ISO 8601 format. If omitted, defaults to a standard lookback period."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a chart of browser version performance metrics including visitor counts and session statistics over a specified time period."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsBrowserVersionsChartRequest(
            query=_models.GetV3WebAnalyticsBrowserVersionsChartRequestQuery(browser_version_to_chart=browser_version_to_chart, where=where, granularity=granularity, to=to, from_=from_, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_browser_versions_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/browser-versions-chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_browser_versions_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_browser_versions_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_browser_versions_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_device_analytics(
    project_id: int = Field(..., description="The unique identifier of the project for which to retrieve device analytics."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response."),
    order_by: str | None = Field(None, description="Sort results by a specific metric in ascending or descending order using the format `metric:asc` or `metric:desc`."),
    where: str | None = Field(None, description="Filter results using a filter expression that can reference available dimensions and metrics to narrow the dataset."),
    from_: str | None = Field(None, alias="from", description="Start of the time range for the query in ISO 8601 datetime format (inclusive)."),
    to: str | None = Field(None, description="End of the time range for the query in ISO 8601 datetime format (inclusive)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve device analytics data for a project, including metrics such as user counts, sessions, and engagement by device type. Results can be filtered, sorted, and scoped to a specific time range."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsDevicesRequest(
            query=_models.GetV3WebAnalyticsDevicesRequestQuery(project_id=project_id, limit=limit, order_by=order_by, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_device_analytics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/devices"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_device_analytics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_device_analytics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_device_analytics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_devices_chart(
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="Time granularity for data aggregation. Choose from hourly, daily, weekly, or monthly intervals."),
    project_id: int = Field(..., description="The unique identifier of the project for which to retrieve device analytics."),
    devices_to_chart: str | None = Field(None, description="Comma-separated list of device values to include in the chart. If not specified, defaults to the top 5 devices by visitor count."),
    where: str | None = Field(None, description="Filter expression to narrow results by dimensions and metrics (e.g., country, device type, visitor segment)."),
    to: str | None = Field(None, description="End datetime for the data query range. Use ISO 8601 format."),
    from_: str | None = Field(None, alias="from", description="Start datetime for the data query range. Use ISO 8601 format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve device analytics chart data showing visitor distribution across different devices over a specified time period. This endpoint is free and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsDevicesChartRequest(
            query=_models.GetV3WebAnalyticsDevicesChartRequestQuery(devices_to_chart=devices_to_chart, where=where, granularity=granularity, to=to, from_=from_, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_devices_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/devices-chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_devices_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_devices_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_devices_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_operating_systems_analytics(
    project_id: int = Field(..., description="The unique identifier for the project whose operating system analytics you want to retrieve."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Useful for pagination and controlling response size."),
    order_by: str | None = Field(None, description="Sort results by a specific metric in ascending or descending order. Available metrics include visitors, session_bounce_rate, and avg_session_duration_sec."),
    where: str | None = Field(None, description="Filter results using expressions that reference dimensions and metrics. Allows you to narrow down data based on specific criteria."),
    from_: str | None = Field(None, alias="from", description="Start of the date range for the analytics query in ISO 8601 datetime format. Data returned will include this date and time onward."),
    to: str | None = Field(None, description="End of the date range for the analytics query in ISO 8601 datetime format. Data returned will include results up to this date and time."),
) -> dict[str, Any] | ToolResult:
    """Retrieve analytics data for operating systems across your project. This endpoint provides insights into visitor behavior by operating system and is available at no cost."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsOperatingSystemsRequest(
            query=_models.GetV3WebAnalyticsOperatingSystemsRequestQuery(project_id=project_id, limit=limit, order_by=order_by, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_operating_systems_analytics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/operating-systems"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_operating_systems_analytics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_operating_systems_analytics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_operating_systems_analytics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_operating_systems_chart(
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="Time granularity for data points in the chart. Choose from hourly, daily, weekly, or monthly intervals."),
    project_id: int = Field(..., description="The unique identifier of the project for which to retrieve operating systems chart data."),
    os_to_chart: str | None = Field(None, description="Specify which operating systems to include in the chart as a comma-separated list. If not provided, defaults to the top 5 operating systems by visitor count."),
    where: str | None = Field(None, description="Filter the data using expressions that reference available dimensions and metrics to narrow results to specific criteria."),
    to: str | None = Field(None, description="End datetime for the data query range. Use ISO 8601 format."),
    from_: str | None = Field(None, alias="from", description="Start datetime for the data query range. Use ISO 8601 format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve operating systems chart data for web analytics across a specified time period and granularity. This endpoint is free to use and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsOperatingSystemsChartRequest(
            query=_models.GetV3WebAnalyticsOperatingSystemsChartRequestQuery(os_to_chart=os_to_chart, where=where, granularity=granularity, to=to, from_=from_, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_operating_systems_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/operating-systems-chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_operating_systems_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_operating_systems_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_operating_systems_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def list_operating_system_versions(
    project_id: int = Field(..., description="The unique identifier of the project for which to retrieve operating system versions data."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response."),
    order_by: str | None = Field(None, description="Sort results by a metric in ascending or descending order using the format metric:asc or metric:desc."),
    where: str | None = Field(None, description="Filter results using expressions that reference available dimensions and metrics to narrow the dataset."),
    from_: str | None = Field(None, alias="from", description="Start of the date range for the query in ISO 8601 datetime format."),
    to: str | None = Field(None, description="End of the date range for the query in ISO 8601 datetime format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve operating system versions analytics data for a specified project, with optional filtering, sorting, and date range selection."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsOperatingSystemsVersionsRequest(
            query=_models.GetV3WebAnalyticsOperatingSystemsVersionsRequestQuery(project_id=project_id, limit=limit, order_by=order_by, where=where, from_=from_, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_operating_system_versions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/operating-systems-versions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_operating_system_versions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_operating_system_versions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_operating_system_versions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Web Analytics
@mcp.tool()
async def get_operating_system_versions_chart(
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(..., description="Time interval for aggregating data points in the chart. Choose from hourly, daily, weekly, or monthly granularity."),
    project_id: int = Field(..., description="Unique identifier of the project to retrieve analytics data for."),
    os_versions_to_chart: str | None = Field(None, description="Comma-separated list of operating system versions to include in the chart. If not specified, defaults to the top 5 versions by visitor count."),
    where: str | None = Field(None, description="Filter expression to narrow results by dimensions and metrics (e.g., country, device type, engagement thresholds)."),
    to: str | None = Field(None, description="End datetime for the data query range in ISO 8601 format."),
    from_: str | None = Field(None, alias="from", description="Start datetime for the data query range in ISO 8601 format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a time-series chart of visitor counts and engagement metrics broken down by operating system versions. Data can be filtered, aggregated at different time intervals, and limited to specific OS versions."""

    # Construct request model with validation
    try:
        _request = _models.GetV3WebAnalyticsOperatingSystemsVersionsChartRequest(
            query=_models.GetV3WebAnalyticsOperatingSystemsVersionsChartRequestQuery(os_versions_to_chart=os_versions_to_chart, where=where, granularity=granularity, to=to, from_=from_, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_operating_system_versions_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/web-analytics/operating-systems-versions-chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_operating_system_versions_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_operating_system_versions_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_operating_system_versions_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: GSC Insights
@mcp.tool()
async def get_search_performance_history(
    date_from: str = Field(..., description="The start date for the historical period in YYYY-MM-DD format. Required to define the beginning of the data range."),
    where: str | None = Field(None, description="Filter results by specific fields using supported filter expressions to narrow down the performance data returned."),
    device: Literal["desktop", "mobile", "tablet"] | None = Field(None, description="Limit results to a specific device type: desktop, mobile, or tablet."),
    search_type: Literal["web", "image", "video", "news"] | None = Field(None, description="Specify the search result category to analyze: web, image, video, or news. Defaults to web search results."),
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(None, description="Choose the time interval for grouping historical data: daily, weekly, or monthly. Defaults to monthly grouping."),
    date_to: str | None = Field(None, description="The end date for the historical period in YYYY-MM-DD format. If not specified, defaults to the current date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve Google Search Console performance metrics over a specified historical period, with options to filter by device type, search category, and time interval grouping."""

    # Construct request model with validation
    try:
        _request = _models.GetV3GscPerformanceHistoryRequest(
            query=_models.GetV3GscPerformanceHistoryRequestQuery(where=where, device=device, search_type=search_type, history_grouping=history_grouping, date_to=date_to, date_from=date_from)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_search_performance_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/gsc/performance-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_search_performance_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_search_performance_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_search_performance_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: GSC Insights
@mcp.tool()
async def list_keyword_position_history(
    date_from: str = Field(..., description="The start date for the historical period in YYYY-MM-DD format. Required to define the beginning of your analysis window."),
    where: str | None = Field(None, description="Filter conditions to narrow results by specific criteria such as keywords, URLs, or other query parameters."),
    device: Literal["desktop", "mobile", "tablet"] | None = Field(None, description="Limit results to a specific device type: desktop, mobile, or tablet."),
    search_type: Literal["web", "image", "video", "news"] | None = Field(None, description="Specify the type of search results to analyze: web, image, video, or news. Defaults to web search results."),
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(None, description="Set the time interval for grouping historical data: daily, weekly, or monthly. Defaults to monthly aggregation."),
    date_to: str | None = Field(None, description="The end date for the historical period in YYYY-MM-DD format. If not specified, defaults to the current date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical keyword position data for a project, aggregated into position ranges over a specified time period. Use this to analyze ranking trends and performance across different time intervals."""

    # Construct request model with validation
    try:
        _request = _models.GetV3GscPositionsHistoryRequest(
            query=_models.GetV3GscPositionsHistoryRequestQuery(where=where, device=device, search_type=search_type, history_grouping=history_grouping, date_to=date_to, date_from=date_from)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_keyword_position_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/gsc/positions-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_keyword_position_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_keyword_position_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_keyword_position_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: GSC Insights
@mcp.tool()
async def list_page_history_gsc(
    date_from: str = Field(..., description="The start date for the historical period in YYYY-MM-DD format. Required to define the beginning of the data range."),
    where: str | None = Field(None, description="Filter results by supported fields using query syntax to narrow down the page history data returned."),
    device: Literal["desktop", "mobile", "tablet"] | None = Field(None, description="Limit results to a specific device type: desktop, mobile, or tablet."),
    search_type: Literal["web", "image", "video", "news"] | None = Field(None, description="Specify the search result category to analyze: web, image, video, or news. Defaults to web search results."),
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(None, description="Set the time interval for grouping historical data: daily, weekly, or monthly. Defaults to monthly grouping."),
    date_to: str | None = Field(None, description="The end date for the historical period in YYYY-MM-DD format. If not specified, defaults to the current date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical page performance metrics from Google Search Console, including impressions, clicks, and rankings over a specified time period."""

    # Construct request model with validation
    try:
        _request = _models.GetV3GscPagesHistoryRequest(
            query=_models.GetV3GscPagesHistoryRequestQuery(where=where, device=device, search_type=search_type, history_grouping=history_grouping, date_to=date_to, date_from=date_from)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_page_history_gsc: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/gsc/pages-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_page_history_gsc")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_page_history_gsc", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_page_history_gsc",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: GSC Insights
@mcp.tool()
async def list_device_performance(
    date_from: str = Field(..., description="Start date for the performance data in YYYY-MM-DD format (e.g., 2024-01-01). This is the beginning of the historical period to analyze."),
    date_to: str | None = Field(None, description="End date for the performance data in YYYY-MM-DD format (e.g., 2024-01-31). If not provided, defaults to the current date. Must be on or after the start date."),
    search_type: Literal["web", "image", "video", "news"] | None = Field(None, description="Filter results to a specific search type: web search, image search, video search, or news search. Defaults to web search if not specified."),
    where: str | None = Field(None, description="Optional filter expression to narrow results by supported fields (e.g., country, device, query). Use this to segment performance data further."),
) -> dict[str, Any] | ToolResult:
    """Retrieve Google Search Console performance metrics aggregated by device type (desktop, mobile, tablet) for a specified date range."""

    # Construct request model with validation
    try:
        _request = _models.GetV3GscPerformanceByDeviceRequest(
            query=_models.GetV3GscPerformanceByDeviceRequestQuery(date_from=date_from, date_to=date_to, search_type=search_type, where=where)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_device_performance: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/gsc/performance-by-device"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_device_performance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_device_performance", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_device_performance",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: GSC Insights
@mcp.tool()
async def list_gsc_metrics_by_country(
    date_from: str = Field(..., description="The start date for the metrics period in YYYY-MM-DD format. Required to define the historical data range."),
    where: str | None = Field(None, description="Filter results using supported field conditions to narrow down the metrics returned."),
    device: Literal["desktop", "mobile", "tablet"] | None = Field(None, description="Filter metrics by device type: desktop, mobile, or tablet."),
    search_type: Literal["web", "image", "video", "news"] | None = Field(None, description="Specify the type of search results to include in metrics: web, image, video, or news. Defaults to web search."),
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(None, description="Set the time interval for grouping historical data: daily, weekly, or monthly. Defaults to monthly aggregation."),
    date_to: str | None = Field(None, description="The end date for the metrics period in YYYY-MM-DD format. If not specified, defaults to the current date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve Google Search Console metrics aggregated by country for a specified date range. This endpoint is free to use and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3GscMetricsByCountryRequest(
            query=_models.GetV3GscMetricsByCountryRequestQuery(where=where, device=device, search_type=search_type, history_grouping=history_grouping, date_to=date_to, date_from=date_from)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_gsc_metrics_by_country: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/gsc/metrics-by-country"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_gsc_metrics_by_country")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_gsc_metrics_by_country", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_gsc_metrics_by_country",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: GSC Insights
@mcp.tool()
async def list_ctr_by_position(
    date_from: str = Field(..., description="Start date for the historical period in YYYY-MM-DD format (required)."),
    date_to: str | None = Field(None, description="End date for the historical period in YYYY-MM-DD format. If omitted, defaults to the start date."),
    device: Literal["desktop", "mobile", "tablet"] | None = Field(None, description="Filter results by device type: desktop, mobile, or tablet. If omitted, returns metrics across all device types."),
) -> dict[str, Any] | ToolResult:
    """Retrieve click-through rate (CTR) metrics aggregated by search position for a specified date range. This endpoint is free to use and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3GscCtrByPositionRequest(
            query=_models.GetV3GscCtrByPositionRequestQuery(date_from=date_from, date_to=date_to, device=device)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_ctr_by_position: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/gsc/ctr-by-position"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_ctr_by_position")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_ctr_by_position", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_ctr_by_position",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: GSC Insights
@mcp.tool()
async def list_search_performance_by_position(
    date_from: str = Field(..., description="The start date for the historical period you want to analyze, specified in YYYY-MM-DD format. This parameter is required."),
    where: str | None = Field(None, description="Filter results using supported field conditions to narrow down the performance data returned."),
    device: Literal["desktop", "mobile", "tablet"] | None = Field(None, description="Filter results by device type: desktop, mobile, or tablet."),
    search_type: Literal["web", "image", "video", "news"] | None = Field(None, description="Specify the type of search results to analyze: web, image, video, or news. Defaults to web search results."),
    date_to: str | None = Field(None, description="The end date for the historical period you want to analyze, specified in YYYY-MM-DD format."),
) -> dict[str, Any] | ToolResult:
    """Retrieve search performance metrics aggregated by search result position. This endpoint provides free access to performance data without consuming API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3GscPerformanceByPositionRequest(
            query=_models.GetV3GscPerformanceByPositionRequestQuery(where=where, device=device, search_type=search_type, date_to=date_to, date_from=date_from)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_search_performance_by_position: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/gsc/performance-by-position"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_search_performance_by_position")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_search_performance_by_position", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_search_performance_by_position",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: GSC Insights
@mcp.tool()
async def list_keyword_history_gsc(
    date_from: str = Field(..., description="Start date for the historical period in YYYY-MM-DD format (inclusive). Required to define the date range for keyword history retrieval."),
    where: str | None = Field(None, description="Filter results by supported fields using query syntax to narrow down keyword history data."),
    device: Literal["desktop", "mobile", "tablet"] | None = Field(None, description="Filter results by device type: desktop, mobile, or tablet."),
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(None, description="Group historical data by time interval: daily, weekly, or monthly. Defaults to monthly grouping."),
    date_to: str | None = Field(None, description="End date for the historical period in YYYY-MM-DD format (inclusive)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical Google Search Console keyword performance data with optional filtering by device type, country, and date range. Data can be grouped by daily, weekly, or monthly intervals."""

    # Construct request model with validation
    try:
        _request = _models.GetV3GscKeywordHistoryRequest(
            query=_models.GetV3GscKeywordHistoryRequestQuery(where=where, device=device, history_grouping=history_grouping, date_to=date_to, date_from=date_from)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_keyword_history_gsc: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/gsc/keyword-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_keyword_history_gsc")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_keyword_history_gsc", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_keyword_history_gsc",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: GSC Insights
@mcp.tool()
async def list_gsc_keywords(
    date_from: str = Field(..., description="Start date for the historical data range in YYYY-MM-DD format. Required to define the beginning of the analysis period."),
    where: str | None = Field(None, description="Filter keywords using a filter expression to narrow results by specific criteria."),
    limit: int | None = Field(None, description="Maximum number of keyword results to return in the response. Defaults to 1000 if not specified."),
    device: Literal["desktop", "mobile", "tablet"] | None = Field(None, description="Filter results by device type: desktop, mobile, or tablet."),
    search_type: Literal["web", "image", "video", "news"] | None = Field(None, description="Type of search results to include: web, image, video, or news. Defaults to web if not specified."),
    date_to: str | None = Field(None, description="End date for the historical data range in YYYY-MM-DD format. If not provided, defaults to the current date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve keywords from Google Search Console data for a specified date range. This operation is free and does not consume API units."""

    # Construct request model with validation
    try:
        _request = _models.GetV3GscKeywordsRequest(
            query=_models.GetV3GscKeywordsRequestQuery(where=where, limit=limit, device=device, search_type=search_type, date_to=date_to, date_from=date_from)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_gsc_keywords: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/gsc/keywords"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_gsc_keywords")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_gsc_keywords", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_gsc_keywords",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: GSC Insights
@mcp.tool()
async def get_page_history(
    date_from: str = Field(..., description="Start date for the historical period in YYYY-MM-DD format. Required to define the beginning of the data range."),
    pages: str | None = Field(None, description="Comma-separated list of page URLs to retrieve history data for. If not specified, data for all pages is included."),
    device: Literal["desktop", "mobile", "tablet"] | None = Field(None, description="Filter results by device type: desktop, mobile, or tablet. If not specified, data for all device types is included."),
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(None, description="Time interval for grouping historical data points. Choose from daily, weekly, or monthly granularity. Defaults to monthly if not specified."),
    date_to: str | None = Field(None, description="End date for the historical period in YYYY-MM-DD format. If not specified, defaults to the current date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve historical performance data for specified pages from Google Search Console, including metrics like clicks, impressions, and average position over a configurable time period."""

    # Construct request model with validation
    try:
        _request = _models.GetV3GscPageHistoryRequest(
            query=_models.GetV3GscPageHistoryRequestQuery(pages=pages, device=device, history_grouping=history_grouping, date_to=date_to, date_from=date_from)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_page_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/gsc/page-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_page_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_page_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_page_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: GSC Insights
@mcp.tool()
async def list_gsc_pages(
    date_from: str = Field(..., description="Start date for the historical data range in YYYY-MM-DD format; required to define the beginning of the analysis period."),
    where: str | None = Field(None, description="Filter pages by supported field criteria using query syntax to narrow results to specific pages or patterns."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response; defaults to 1000 if not specified."),
    device: Literal["desktop", "mobile", "tablet"] | None = Field(None, description="Filter results by device type: desktop, mobile, or tablet."),
    search_type: Literal["web", "image", "video", "news"] | None = Field(None, description="Type of search results to include in the data; defaults to web search and supports web, image, video, and news results."),
    date_to: str | None = Field(None, description="End date for the historical data range in YYYY-MM-DD format; if omitted, defaults to the current date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve page performance metrics from Google Search Console, including impressions, clicks, and rankings for specified date ranges and filters."""

    # Construct request model with validation
    try:
        _request = _models.GetV3GscPagesRequest(
            query=_models.GetV3GscPagesRequestQuery(where=where, limit=limit, device=device, search_type=search_type, date_to=date_to, date_from=date_from)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_gsc_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/gsc/pages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_gsc_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_gsc_pages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_gsc_pages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: GSC Insights
@mcp.tool()
async def list_anonymous_queries(
    select: str = Field(..., description="Comma-separated list of column names to include in the response. Refer to the response schema for valid column identifiers."),
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(..., description="Two-letter country code in ISO 3166-1 alpha-2 format (e.g., 'us', 'gb', 'de') to scope results to a specific country."),
    date_from: str = Field(..., description="Start date for the historical data range in YYYY-MM-DD format. Results will include data from this date onward."),
    project_id: int = Field(..., description="Unique identifier of the project for which to retrieve anonymous queries."),
    limit: int | None = Field(None, description="Maximum number of results to return in the response. Defaults to 1000 if not specified."),
    order_by: str | None = Field(None, description="Column name to sort results by. Refer to the response schema for valid column identifiers available for ordering."),
    where: str | None = Field(None, description="Filter expression to narrow results. Supports filtering by keyword (string) and url (string) columns using standard filter syntax."),
) -> dict[str, Any] | ToolResult:
    """Retrieve anonymous search queries for a specific project and country. Returns query data filtered by date range with customizable columns, sorting, and filtering options."""

    # Construct request model with validation
    try:
        _request = _models.GetV3GscAnonymousQueriesRequest(
            query=_models.GetV3GscAnonymousQueriesRequestQuery(limit=limit, order_by=order_by, where=where, select=select, country=country, date_from=date_from, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_anonymous_queries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v3/gsc/anonymous-queries"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_anonymous_queries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_anonymous_queries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_anonymous_queries",
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
        print("  python ahrefs_api_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Ahrefs API MCP Server")

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
    logger.info("Starting Ahrefs API MCP Server")
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

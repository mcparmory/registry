#!/usr/bin/env python3
"""
Miro MCP Server
Generated: 2026-05-05 15:35:26 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://api.miro.com")
SERVER_NAME = "Miro"
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
    'oAuth2AuthCode',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["oAuth2AuthCode"] = _auth.OAuth2Auth()
    logging.info("Authentication configured: oAuth2AuthCode")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for oAuth2AuthCode not configured: {error_msg}")
    _auth_handlers["oAuth2AuthCode"] = None

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

mcp = FastMCP("Miro", middleware=[_JsonCoercionMiddleware()])

# Tags: tokens
@mcp.tool()
async def get_access_token_info() -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about the current access token, including its type, assigned scopes, associated team and user, creation timestamp, and the user who created it."""

    # Extract parameters for API call
    _http_path = "/v1/oauth-token"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_access_token_info")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_access_token_info", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_access_token_info",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Audit Logs
@mcp.tool()
async def list_audit_logs(
    created_after: str = Field(..., alias="createdAfter", description="Start of the date range for audit log retrieval in UTC ISO 8601 format with milliseconds (e.g., 2023-03-30T17:26:50.000Z). Audit logs created on or after this timestamp will be included."),
    created_before: str = Field(..., alias="createdBefore", description="End of the date range for audit log retrieval in UTC ISO 8601 format with milliseconds (e.g., 2023-04-30T17:26:50.000Z). Audit logs created before this timestamp will be included."),
    limit: int | None = Field(None, description="Maximum number of audit log entries to return per request. Defaults to 100. Use pagination with the cursor from the response to retrieve additional results beyond this limit."),
    sorting: Literal["ASC", "DESC"] | None = Field(None, description="Sort order for results based on audit log creation date. Choose ASC for oldest-first or DESC for newest-first ordering. Defaults to ASC."),
) -> dict[str, Any] | ToolResult:
    """Retrieve audit events from your enterprise within a specified date range (limited to the last 90 days). Use pagination and sorting to navigate large result sets efficiently."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGetAuditLogsRequest(
            query=_models.EnterpriseGetAuditLogsRequestQuery(created_after=created_after, created_before=created_before, limit=limit, sorting=sorting)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_audit_logs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/audit/logs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_audit_logs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_audit_logs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_audit_logs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Board classification: Team level
@mcp.tool()
async def update_team_boards_classification_bulk(
    org_id: str = Field(..., description="The unique identifier of the organization. This is a numeric ID that identifies which organization owns the team."),
    team_id: str = Field(..., description="The unique identifier of the team whose boards will be updated. This is a numeric ID that identifies the specific team within the organization."),
    label_id: str | None = Field(None, alias="labelId", description="The numeric ID of the data classification label to assign to the boards. This label must be valid for the organization."),
    not_classified_only: bool | None = Field(None, alias="notClassifiedOnly", description="When true, applies the classification label only to boards that are not yet classified. When false or omitted, applies the label to all boards in the team regardless of current classification status."),
) -> dict[str, Any] | ToolResult:
    """Bulk update data classification labels for boards within a team. Optionally target only unclassified boards or apply the classification to all boards in the team."""

    _label_id = _parse_int(label_id)

    # Construct request model with validation
    try:
        _request = _models.EnterpriseDataclassificationTeamBoardsBulkRequest(
            path=_models.EnterpriseDataclassificationTeamBoardsBulkRequestPath(org_id=org_id, team_id=team_id),
            body=_models.EnterpriseDataclassificationTeamBoardsBulkRequestBody(label_id=_label_id, not_classified_only=not_classified_only)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_team_boards_classification_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/data-classification", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/data-classification"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_team_boards_classification_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_team_boards_classification_bulk", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_team_boards_classification_bulk",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Board classification: Board level
@mcp.tool()
async def get_board_data_classification(
    org_id: str = Field(..., description="The unique identifier of the organization that owns the board. Use the organization ID provided in your Enterprise account."),
    team_id: str = Field(..., description="The unique identifier of the team within the organization that contains the board."),
    board_id: str = Field(..., description="The unique identifier of the board whose data classification you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the data classification level assigned to a specific board within an organization and team. This enterprise-only endpoint requires Company Admin role and the boards:read scope."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseDataclassificationBoardGetRequest(
            path=_models.EnterpriseDataclassificationBoardGetRequestPath(org_id=org_id, team_id=team_id, board_id=board_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_board_data_classification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/boards/{board_id}/data-classification", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/boards/{board_id}/data-classification"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_board_data_classification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_board_data_classification", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_board_data_classification",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: doc formats
@mcp.tool()
async def create_markdown_doc(
    board_id: str = Field(..., description="The unique identifier of the board where the markdown document will be created."),
    content_type: Literal["markdown"] = Field(..., alias="contentType", description="The format type for the document content. Must be set to 'markdown' to specify markdown formatting."),
    content: str = Field(..., description="The markdown-formatted text content for the document."),
) -> dict[str, Any] | ToolResult:
    """Creates a new markdown document item on a board. The document is formatted as markdown text and will be added to the specified board."""

    # Construct request model with validation
    try:
        _request = _models.CreateDocFormatItemRequest(
            path=_models.CreateDocFormatItemRequestPath(board_id=board_id),
            body=_models.CreateDocFormatItemRequestBody(data=_models.CreateDocFormatItemRequestBodyData(content_type=content_type, content=content))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_markdown_doc: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/docs", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/docs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_markdown_doc")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_markdown_doc", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_markdown_doc",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: doc formats
@mcp.tool()
async def get_doc_format_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the item you want to retrieve."),
    item_id: str = Field(..., description="The unique identifier of the doc format item to retrieve."),
    text_content_type: Literal["html", "markdown"] | None = Field(None, alias="textContentType", description="Specifies the format for the returned doc's content as either HTML or Markdown. If not specified, the default format is used."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific doc format item from a board. Returns the item's metadata and content, with optional control over the content format."""

    # Construct request model with validation
    try:
        _request = _models.GetDocFormatItemRequest(
            path=_models.GetDocFormatItemRequestPath(board_id=board_id, item_id=item_id),
            query=_models.GetDocFormatItemRequestQuery(text_content_type=text_content_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_doc_format_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/docs/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/docs/{item_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_doc_format_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_doc_format_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_doc_format_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: doc formats
@mcp.tool()
async def delete_doc_format_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the item to delete."),
    item_id: str = Field(..., description="The unique identifier of the doc format item to delete from the board."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a doc format item from a board. This action cannot be undone and requires write access to the board."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDocFormatItemRequest(
            path=_models.DeleteDocFormatItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_doc_format_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/docs/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/docs/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_doc_format_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_doc_format_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_doc_format_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal holds
@mcp.tool()
async def list_cases(
    org_id: str = Field(..., description="The numeric ID of the organization containing the cases to retrieve.", pattern="^[0-9]+$"),
    limit: str | None = Field(None, description="Maximum number of cases to return in the response, between 1 and 100 items (defaults to 100)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all eDiscovery cases in an organization. Requires Enterprise Guard add-on and eDiscovery Admin role."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetAllCasesRequest(
            path=_models.GetAllCasesRequestPath(org_id=org_id),
            query=_models.GetAllCasesRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_cases: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/cases", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/cases"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_cases")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_cases", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_cases",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal holds
@mcp.tool()
async def create_case(
    org_id: str = Field(..., description="The numeric ID of the organization where the case will be created.", pattern="^[0-9]+$"),
    name: str = Field(..., description="A descriptive name for the case that identifies the legal matter or investigation."),
    description: str | None = Field(None, description="Optional additional details or context about the case to help organize and document the legal hold."),
) -> dict[str, Any] | ToolResult:
    """Create a new legal hold case in your organization to initiate the eDiscovery process. Cases serve as containers for grouping multiple legal holds together during litigation or investigations. Requires Enterprise Guard add-on and eDiscovery Admin role."""

    # Construct request model with validation
    try:
        _request = _models.CreateCaseRequest(
            path=_models.CreateCaseRequestPath(org_id=org_id),
            body=_models.CreateCaseRequestBody(name=name, description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_case: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/cases", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/cases"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_case")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_case", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_case",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal holds
@mcp.tool()
async def get_case(
    org_id: str = Field(..., description="The numeric ID of the organization containing the case. Must be a numeric string.", pattern="^[0-9]+$"),
    case_id: str = Field(..., description="The numeric ID of the case to retrieve. Must be a numeric string.", pattern="^[0-9]+$"),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific case within an organization. This operation requires Enterprise Guard add-on and appropriate admin roles (Company Admin and eDiscovery Admin)."""

    # Construct request model with validation
    try:
        _request = _models.GetCaseRequest(
            path=_models.GetCaseRequestPath(org_id=org_id, case_id=case_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_case: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/cases/{case_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/cases/{case_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_case")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_case", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_case",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal holds
@mcp.tool()
async def update_case(
    org_id: str = Field(..., description="The numeric ID of the organization containing the case to be edited.", pattern="^[0-9]+$"),
    case_id: str = Field(..., description="The numeric ID of the case to be edited.", pattern="^[0-9]+$"),
    name: str = Field(..., description="The updated name for the case. This field is required and helps maintain clarity and consistency across stakeholders."),
    description: str | None = Field(None, description="An optional description providing additional context or details about the case, such as scope, focus, or internal documentation standards."),
) -> dict[str, Any] | ToolResult:
    """Update case details such as name and description to keep case information accurate and aligned with the evolving scope of a legal matter. This operation is restricted to eDiscovery Admins and requires the Enterprise Guard add-on."""

    # Construct request model with validation
    try:
        _request = _models.EditCaseRequest(
            path=_models.EditCaseRequestPath(org_id=org_id, case_id=case_id),
            body=_models.EditCaseRequestBody(name=name, description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_case: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/cases/{case_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/cases/{case_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_case")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_case", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_case",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal holds
@mcp.tool()
async def close_case(
    org_id: str = Field(..., description="The numeric ID of the organization containing the case to close.", pattern="^[0-9]+$"),
    case_id: str = Field(..., description="The numeric ID of the case to close and delete.", pattern="^[0-9]+$"),
) -> dict[str, Any] | ToolResult:
    """Permanently close and delete a case, marking the conclusion of a legal matter or investigation. All associated legal holds must be closed before closing the case. Requires Enterprise Guard add-on with Company Admin and eDiscovery Admin roles."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCaseRequest(
            path=_models.DeleteCaseRequestPath(org_id=org_id, case_id=case_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for close_case: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/cases/{case_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/cases/{case_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("close_case")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("close_case", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="close_case",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal holds
@mcp.tool()
async def list_legal_holds_in_case(
    org_id: str = Field(..., description="The numeric ID of the organization containing the case. Must be a numeric string.", pattern="^[0-9]+$"),
    case_id: str = Field(..., description="The numeric ID of the case for which to retrieve legal holds. Must be a numeric string.", pattern="^[0-9]+$"),
    limit: str | None = Field(None, description="The maximum number of legal holds to return in the response. Accepts values between 1 and 100, with a default of 100 items."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all legal holds associated with a specific case within an organization. This operation is restricted to Enterprise Guard users with Company Admin and eDiscovery Admin roles."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetAllLegalHoldsRequest(
            path=_models.GetAllLegalHoldsRequestPath(org_id=org_id, case_id=case_id),
            query=_models.GetAllLegalHoldsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_legal_holds_in_case: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/cases/{case_id}/legal-holds", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/cases/{case_id}/legal-holds"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_legal_holds_in_case")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_legal_holds_in_case", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_legal_holds_in_case",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal holds
@mcp.tool()
async def create_legal_hold_for_case(
    org_id: str = Field(..., description="The numeric ID of the organization where the legal hold will be created.", pattern="^[0-9]+$"),
    case_id: str = Field(..., description="The numeric ID of the case within the organization where the legal hold will be applied.", pattern="^[0-9]+$"),
    name: str = Field(..., description="A descriptive name for the legal hold to identify its purpose or scope."),
    scope: _models.LegalHoldRequestScopeUsers = Field(..., description="The scope criteria for the legal hold, currently supporting only the 'users' variant. Specify a list of up to 200 users to place under hold; this list must include all users for new holds or updates, as it replaces any previous user list."),
    description: str | None = Field(None, description="An optional detailed description providing additional context or information about the legal hold."),
) -> dict[str, Any] | ToolResult:
    """Create a new legal hold within a case to preserve content owned, co-owned, created, edited, or accessed by specified users. Legal holds may take up to 24 hours to process."""

    # Construct request model with validation
    try:
        _request = _models.CreateLegalHoldRequest(
            path=_models.CreateLegalHoldRequestPath(org_id=org_id, case_id=case_id),
            body=_models.CreateLegalHoldRequestBody(name=name, description=description, scope=scope)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_legal_hold_for_case: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/cases/{case_id}/legal-holds", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/cases/{case_id}/legal-holds"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_legal_hold_for_case")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_legal_hold_for_case", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_legal_hold_for_case",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal holds
@mcp.tool()
async def list_legal_hold_export_jobs(
    org_id: str = Field(..., description="The numeric ID of the organization containing the case. Must be a valid organization ID in numeric format.", pattern="^[0-9]+$"),
    case_id: str = Field(..., description="The numeric ID of the legal hold case for which to retrieve export jobs. Must be a valid case ID in numeric format.", pattern="^[0-9]+$"),
    limit: str | None = Field(None, description="The maximum number of export jobs to return in the response. Accepts values between 1 and 100, with a default of 100 items."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all board export jobs for a specific legal hold case. This operation is available only to Enterprise Guard users with both Company Admin and eDiscovery Admin roles."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetLegalHoldExportJobsRequest(
            path=_models.GetLegalHoldExportJobsRequestPath(org_id=org_id, case_id=case_id),
            query=_models.GetLegalHoldExportJobsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_legal_hold_export_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/cases/{case_id}/export-jobs", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/cases/{case_id}/export-jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_legal_hold_export_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_legal_hold_export_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_legal_hold_export_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal holds
@mcp.tool()
async def get_legal_hold(
    org_id: str = Field(..., description="The numeric ID of the organization containing the legal hold. Must be a numeric string.", pattern="^[0-9]+$"),
    case_id: str = Field(..., description="The numeric ID of the case containing the legal hold. Must be a numeric string.", pattern="^[0-9]+$"),
    legal_hold_id: str = Field(..., description="The numeric ID of the legal hold to retrieve. Must be a numeric string.", pattern="^[0-9]+$"),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific legal hold within a case. This operation requires Enterprise Guard add-on and appropriate admin roles (Company Admin and eDiscovery Admin)."""

    # Construct request model with validation
    try:
        _request = _models.GetLegalHoldRequest(
            path=_models.GetLegalHoldRequestPath(org_id=org_id, case_id=case_id, legal_hold_id=legal_hold_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_legal_hold: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/cases/{case_id}/legal-holds/{legal_hold_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/cases/{case_id}/legal-holds/{legal_hold_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_legal_hold")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_legal_hold", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_legal_hold",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal holds
@mcp.tool()
async def update_legal_hold(
    org_id: str = Field(..., description="The numeric ID of the organization containing the legal hold. Must be a numeric string.", pattern="^[0-9]+$"),
    case_id: str = Field(..., description="The numeric ID of the case containing the legal hold. Must be a numeric string.", pattern="^[0-9]+$"),
    legal_hold_id: str = Field(..., description="The numeric ID of the legal hold to update. Must be a numeric string.", pattern="^[0-9]+$"),
    name: str = Field(..., description="The name assigned to the legal hold. Used to identify the hold within the case."),
    scope: _models.LegalHoldRequestScopeUsers = Field(..., description="The scope criteria determining which content items are preserved under this hold. Currently supports the `users` variant to place specific users under hold. Provide a complete list of all users to be preserved (up to 200 users per hold), including both newly added and previously held users. The system will ignore any unexpected scope variants for forward compatibility."),
    description: str | None = Field(None, description="Optional description providing additional context or details about the legal hold and its scope."),
) -> dict[str, Any] | ToolResult:
    """Update an existing legal hold to adjust preservation scope as case requirements evolve. Modify the hold's name, description, and add or remove users and boards to ensure accurate data preservation throughout the legal process."""

    # Construct request model with validation
    try:
        _request = _models.EditLegalHoldRequest(
            path=_models.EditLegalHoldRequestPath(org_id=org_id, case_id=case_id, legal_hold_id=legal_hold_id),
            body=_models.EditLegalHoldRequestBody(name=name, description=description, scope=scope)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_legal_hold: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/cases/{case_id}/legal-holds/{legal_hold_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/cases/{case_id}/legal-holds/{legal_hold_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_legal_hold")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_legal_hold", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_legal_hold",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal holds
@mcp.tool()
async def close_legal_hold(
    org_id: str = Field(..., description="The numeric ID of the organization containing the legal hold to close.", pattern="^[0-9]+$"),
    case_id: str = Field(..., description="The numeric ID of the case containing the legal hold to close.", pattern="^[0-9]+$"),
    legal_hold_id: str = Field(..., description="The numeric ID of the legal hold to close and permanently delete.", pattern="^[0-9]+$"),
) -> dict[str, Any] | ToolResult:
    """Close and permanently delete a legal hold in a case, releasing preserved Miro boards and custodians back to normal operations. Note: content release may take up to 24 hours to complete."""

    # Construct request model with validation
    try:
        _request = _models.DeleteLegalHoldRequest(
            path=_models.DeleteLegalHoldRequestPath(org_id=org_id, case_id=case_id, legal_hold_id=legal_hold_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for close_legal_hold: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/cases/{case_id}/legal-holds/{legal_hold_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/cases/{case_id}/legal-holds/{legal_hold_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("close_legal_hold")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("close_legal_hold", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="close_legal_hold",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Legal holds
@mcp.tool()
async def list_legal_hold_content_items(
    org_id: str = Field(..., description="The numeric ID of the organization containing the case and legal hold.", pattern="^[0-9]+$"),
    case_id: str = Field(..., description="The numeric ID of the case containing the legal hold.", pattern="^[0-9]+$"),
    legal_hold_id: str = Field(..., description="The numeric ID of the legal hold for which to retrieve preserved content items.", pattern="^[0-9]+$"),
    limit: str | None = Field(None, description="Maximum number of content items to return in a single response, between 1 and 100 items. Defaults to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all content items (Miro boards) currently under a specific legal hold within a case. Verify the legal hold is in 'ACTIVE' state to ensure all preserved content has finished processing."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetLegalHoldContentItemsRequest(
            path=_models.GetLegalHoldContentItemsRequestPath(org_id=org_id, case_id=case_id, legal_hold_id=legal_hold_id),
            query=_models.GetLegalHoldContentItemsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_legal_hold_content_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/cases/{case_id}/legal-holds/{legal_hold_id}/content-items", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/cases/{case_id}/legal-holds/{legal_hold_id}/content-items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_legal_hold_content_items")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_legal_hold_content_items", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_legal_hold_content_items",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Board Export
@mcp.tool()
async def list_board_export_jobs(
    org_id: str = Field(..., description="The unique identifier of the organization whose board export jobs you want to retrieve."),
    status: list[str] | None = Field(None, description="Filter results by job status. Accepts multiple statuses such as JOB_STATUS_CREATED, JOB_STATUS_IN_PROGRESS, JOB_STATUS_CANCELLED, or JOB_STATUS_FINISHED. If not specified, all statuses are returned."),
    creator_id: list[int] | None = Field(None, alias="creatorId", description="Filter results by the user ID of the job creator. Accepts multiple creator IDs to retrieve jobs created by specific users."),
    limit: str | None = Field(None, description="Maximum number of results to return per request, between 1 and 500. Defaults to 50. If the total results exceed this limit, a cursor is provided for pagination."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of board export jobs for an organization, filtered by status, creator, and pagination limits. Enterprise-only endpoint requiring Company Admin role with eDiscovery enabled."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.EnterpriseBoardExportJobsRequest(
            path=_models.EnterpriseBoardExportJobsRequestPath(org_id=org_id),
            query=_models.EnterpriseBoardExportJobsRequestQuery(status=status, creator_id=creator_id, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_board_export_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/boards/export/jobs", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/boards/export/jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_board_export_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_board_export_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_board_export_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Board Export
@mcp.tool()
async def create_board_export_job(
    org_id: str = Field(..., description="The unique identifier of the organization that owns the boards to be exported."),
    request_id: str = Field(..., description="A unique identifier (UUID format) for this export job request, used to track and reference the job."),
    board_ids: list[str] | None = Field(None, alias="boardIds", description="List of board IDs to include in the export. Accepts 1 to 50 board IDs. If omitted, the behavior depends on your organization's default settings.", min_length=1, max_length=50),
    board_format: Literal["SVG", "HTML", "PDF"] | None = Field(None, alias="boardFormat", description="The output file format for the exported boards. Choose from SVG (default), HTML, or PDF. Defaults to SVG if not specified."),
) -> dict[str, Any] | ToolResult:
    """Initiates an asynchronous export job for one or more boards in a specified format (SVG, HTML, or PDF). This enterprise-only operation requires Company Admin role and eDiscovery enablement."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseCreateBoardExportRequest(
            path=_models.EnterpriseCreateBoardExportRequestPath(org_id=org_id),
            query=_models.EnterpriseCreateBoardExportRequestQuery(request_id=request_id),
            body=_models.EnterpriseCreateBoardExportRequestBody(board_ids=board_ids, board_format=board_format)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_board_export_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/boards/export/jobs", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/boards/export/jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_board_export_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_board_export_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_board_export_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Board Export
@mcp.tool()
async def get_board_export_job_status(
    org_id: str = Field(..., description="The unique identifier of the organization that owns the export job."),
    job_id: str = Field(..., description="The unique identifier of the board export job, formatted as a UUID."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the current status of a board export job, including completion progress and results. Available only for Enterprise plan users with Company Admin role and eDiscovery enabled."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseBoardExportJobStatusRequest(
            path=_models.EnterpriseBoardExportJobStatusRequestPath(org_id=org_id, job_id=job_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_board_export_job_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/boards/export/jobs/{job_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/boards/export/jobs/{job_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_board_export_job_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_board_export_job_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_board_export_job_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Board Export
@mcp.tool()
async def get_board_export_job_results(
    org_id: str = Field(..., description="The unique identifier of the organization. This is a numeric string that identifies which organization's board export job to retrieve results for."),
    job_id: str = Field(..., description="The unique identifier of the export job. This is a UUID that identifies the specific board export job whose results you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the results of a completed board export job, including the S3 link to the exported files. This operation is available only for Enterprise plan users with Company Admin role and eDiscovery enabled."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseBoardExportJobResultsRequest(
            path=_models.EnterpriseBoardExportJobResultsRequestPath(org_id=org_id, job_id=job_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_board_export_job_results: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/boards/export/jobs/{job_id}/results", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/boards/export/jobs/{job_id}/results"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_board_export_job_results")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_board_export_job_results", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_board_export_job_results",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Board Export
@mcp.tool()
async def cancel_board_export_job(
    org_id: str = Field(..., description="The unique identifier of the organization that owns the export job. This is a numeric string identifier."),
    job_id: str = Field(..., description="The unique identifier of the board export job to cancel. This must be a valid UUID format."),
    status: Literal["CANCELLED"] = Field(..., description="The target status for the export job. Only CANCELLED is supported, which stops the ongoing export operation."),
) -> dict[str, Any] | ToolResult:
    """Cancel an ongoing board export job. This operation allows you to stop a board export job that is currently in progress by updating its status to CANCELLED."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseUpdateBoardExportJobRequest(
            path=_models.EnterpriseUpdateBoardExportJobRequestPath(org_id=org_id, job_id=job_id),
            body=_models.EnterpriseUpdateBoardExportJobRequestBody(status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for cancel_board_export_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/boards/export/jobs/{job_id}/status", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/boards/export/jobs/{job_id}/status"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("cancel_board_export_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("cancel_board_export_job", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="cancel_board_export_job",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Board Export
@mcp.tool()
async def list_board_export_job_tasks(
    org_id: str = Field(..., description="The unique identifier of the organization that owns the export job."),
    job_id: str = Field(..., description="The unique identifier of the board export job (UUID format)."),
    status: list[str] | None = Field(None, description="Filter tasks by one or more statuses (e.g., TASK_STATUS_CREATED, TASK_STATUS_SCHEDULED, TASK_STATUS_SUCCESS, TASK_STATUS_ERROR, TASK_STATUS_CANCELLED). Omit to return tasks of all statuses."),
    limit: str | None = Field(None, description="Maximum number of tasks to return per request, between 1 and 500. Defaults to 50. Use pagination with the cursor parameter if more results are available."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of tasks associated with a board export job. Use this to monitor the progress and status of individual export tasks within a job."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.EnterpriseBoardExportJobTasksRequest(
            path=_models.EnterpriseBoardExportJobTasksRequestPath(org_id=org_id, job_id=job_id),
            query=_models.EnterpriseBoardExportJobTasksRequestQuery(status=status, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_board_export_job_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/boards/export/jobs/{job_id}/tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/boards/export/jobs/{job_id}/tasks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_board_export_job_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_board_export_job_tasks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_board_export_job_tasks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Board Export
@mcp.tool()
async def create_board_export_task_download_link(
    org_id: str = Field(..., description="The unique identifier of the organization that owns the export job. This is a numeric ID specific to your enterprise account."),
    job_id: str = Field(..., description="The unique identifier of the board export job. This must be a valid UUID that corresponds to an existing export job."),
    task_id: str = Field(..., description="The unique identifier of the specific task within the export job for which you want to create a download link. This must be a valid UUID that corresponds to an existing task."),
) -> dict[str, Any] | ToolResult:
    """Generate a downloadable link for the results of a specific board export task within an enterprise export job. This endpoint is available only to Enterprise plan users with Company Admin role and eDiscovery enabled."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseCreateBoardExportTaskExportLinkRequest(
            path=_models.EnterpriseCreateBoardExportTaskExportLinkRequestPath(org_id=org_id, job_id=job_id, task_id=task_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_board_export_task_download_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/boards/export/jobs/{job_id}/tasks/{task_id}/export-link", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/boards/export/jobs/{job_id}/tasks/{task_id}/export-link"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_board_export_task_download_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_board_export_task_download_link", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_board_export_task_download_link",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Board Content Logs
@mcp.tool()
async def list_board_item_content_logs(
    org_id: str = Field(..., description="The unique identifier of your organization."),
    from_: str = Field(..., alias="from", description="Start of the time range (UTC, ISO 8601 format with Z offset) for filtering logs by last modification date, inclusive."),
    to: str = Field(..., description="End of the time range (UTC, ISO 8601 format with Z offset) for filtering logs by last modification date, inclusive."),
    board_ids: list[str] | None = Field(None, description="Optional list of up to 15 board IDs to filter logs. If omitted, logs for all boards are returned.", max_length=15),
    emails: list[str] | None = Field(None, description="Optional list of up to 15 user email addresses to filter logs by who created, modified, or deleted board items.", max_length=15),
    limit: str | None = Field(None, description="Maximum number of results to return per request, between 1 and 1000. Defaults to 1000. Use pagination with the cursor parameter if results exceed this limit."),
    sorting: Literal["asc", "desc"] | None = Field(None, description="Sort results by modification date in ascending (oldest first) or descending (newest first) order. Defaults to ascending."),
) -> dict[str, Any] | ToolResult:
    """Retrieve content change logs for board items within your organization over a specified time period. Filter by board IDs, user emails, and modification dates to track all updates, modifications, and deletions of board item content."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.EnterpriseBoardContentItemLogsFetchRequest(
            path=_models.EnterpriseBoardContentItemLogsFetchRequestPath(org_id=org_id),
            query=_models.EnterpriseBoardContentItemLogsFetchRequestQuery(board_ids=board_ids, emails=emails, from_=from_, to=to, limit=_limit, sorting=sorting)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_board_item_content_logs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/content-logs/items", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/content-logs/items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_board_item_content_logs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_board_item_content_logs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_board_item_content_logs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reset all sessions of a user
@mcp.tool()
async def delete_user_all_sessions(email: str = Field(..., description="The email address of the user whose sessions should be terminated. The user will be signed out from all devices and applications immediately.")) -> dict[str, Any] | ToolResult:
    """Immediately terminate all active sessions for a user across all devices, forcing them to sign in again. Use this to restrict access during security incidents, credential compromises, or when a user leaves the organization."""

    # Construct request model with validation
    try:
        _request = _models.EnterprisePostUserSessionsResetRequest(
            query=_models.EnterprisePostUserSessionsResetRequestQuery(email=email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user_all_sessions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/sessions/reset_all"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_user_all_sessions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_user_all_sessions", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_user_all_sessions",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User
@mcp.tool()
async def list_users(
    filter_: str | None = Field(None, alias="filter", description="Filter results using expressions with attribute names and operators (eq, ne, co, sw, ew, pr, gt, ge, lt, le) combined with logical operators (and, or, not). Attribute names and operators are case-insensitive. Examples: userName eq \"user@miro.com\", active eq true, displayName co \"user\", groups.value eq \"3458764577585056871\", userType ne \"Full\"."),
    start_index: int | None = Field(None, alias="startIndex", description="The starting position for paginated results (1-based indexing). Use with count to retrieve specific pages of results."),
    count: int | None = Field(None, description="Maximum number of results to return per page. Defaults to 100; maximum allowed is 1000. Use with startIndex for pagination."),
    sort_by: str | None = Field(None, alias="sortBy", description="Attribute name to sort results by. Examples: userName, emails.value."),
    sort_order: Literal["ascending", "descending"] | None = Field(None, alias="sortOrder", description="Sort direction for the sortBy attribute: ascending or descending."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of users in your organization. Note: Only returns users who are organization members, not guest users."""

    # Construct request model with validation
    try:
        _request = _models.ListUsersRequest(
            query=_models.ListUsersRequestQuery(filter_=filter_, start_index=start_index, count=count, sort_by=sort_by, sort_order=sort_order)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/Users"
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

# Tags: User
@mcp.tool()
async def create_user(
    user_name: str = Field(..., alias="userName", description="The unique email address that serves as the user's login identifier and username. This email becomes the user's full name if displayName or name attributes are not provided."),
    family_name: str = Field(..., alias="familyName", description="The user's last name. Combined with givenName, the total character count cannot exceed 60 characters. Used to construct the user's full name if displayName is not provided."),
    given_name: str = Field(..., alias="givenName", description="The user's first name. Combined with familyName, the total character count cannot exceed 60 characters. Used to construct the user's full name if displayName is not provided."),
    display_name: str | None = Field(None, alias="displayName", description="A human-readable full name for the user, up to 60 characters. When provided, this takes precedence over constructed names from givenName and familyName."),
    user_type: str | None = Field(None, alias="userType", description="The user's license type in the organization. Supported values include: Full, Free, Free Restricted, Full (Trial), and Basic. When not specified, the license is assigned automatically based on the organization's plan."),
    active: bool | None = Field(None, description="Whether the user is active or deactivated in the organization. Defaults to active when not specified."),
    photos: list[_models.CreateUserBodyPhotosItem] | None = Field(None, description="An array of profile photos for the user. Each photo must be a publicly accessible URL (jpg, jpeg, bmp, png, or gif format) with a maximum file size of 31 MB. The URL must include the file extension or the server response must include the appropriate Content-Type header."),
    roles: list[_models.CreateUserBodyRolesItem] | None = Field(None, description="An array of roles assigned to the user. Organization-level roles include ORGANIZATION_INTERNAL_ADMIN and ORGANIZATION_INTERNAL_USER. Admin roles include Content Admin, User Admin, Security Admin, or custom admin role names. Each role entry specifies the role value, display name, type, and primary flag."),
    preferred_language: str | None = Field(None, alias="preferredLanguage", description="The user's preferred language in locale format (e.g., en_US for English). This setting controls the language used in the user's interface."),
    employee_number: str | None = Field(None, alias="employeeNumber", description="An internal employee identifier for the user, up to 20 characters."),
    cost_center: str | None = Field(None, alias="costCenter", description="The cost center associated with the user, up to 120 characters."),
    organization: str | None = Field(None, description="The organization name or identifier associated with the user, up to 120 characters."),
    division: str | None = Field(None, description="The division within the organization associated with the user, up to 120 characters."),
    department: str | None = Field(None, description="The department within the organization associated with the user, up to 120 characters."),
    value: str | None = Field(None, description="The manager's identifier as a numeric value. Non-numeric values are ignored. This field maps to Miro's internal managerId field which expects a Long type."),
) -> dict[str, Any] | ToolResult:
    """Creates a new user in the organization and automatically adds them to the default team. The user's identity is established via email address provided in the userName field."""

    # Construct request model with validation
    try:
        _request = _models.CreateUserRequest(
            body=_models.CreateUserRequestBody(user_name=user_name, display_name=display_name, user_type=user_type, active=active, photos=photos, roles=roles, preferred_language=preferred_language,
                name=_models.CreateUserRequestBodyName(family_name=family_name, given_name=given_name),
                urn_ietf_params_scim_schemas_extension_enterprise_2_0_user=_models.CreateUserRequestBodyUrnIetfParamsScimSchemasExtensionEnterprise20User(employee_number=employee_number, cost_center=cost_center, organization=organization, division=division, department=department,
                    manager=_models.CreateUserRequestBodyUrnIetfParamsScimSchemasExtensionEnterprise20UserManager(value=value) if any(v is not None for v in [value]) else None) if any(v is not None for v in [employee_number, cost_center, organization, division, department, value]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/Users"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: User
@mcp.tool()
async def get_user(id_: str = Field(..., alias="id", description="The unique identifier of the user to retrieve. Must be a valid user ID for an organization member.")) -> dict[str, Any] | ToolResult:
    """Retrieves a single user resource by ID. Returns only users that are members of the organization; guest users are not included."""

    # Construct request model with validation
    try:
        _request = _models.GetUserRequest(
            path=_models.GetUserRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/Users/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/Users/{id}"
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

# Tags: User
@mcp.tool()
async def update_user(
    id_: str = Field(..., alias="id", description="The unique server-assigned identifier for the user being updated."),
    user_name: str | None = Field(None, alias="userName", description="The unique username or login identifier, typically an email address format."),
    family_name: str | None = Field(None, alias="familyName", description="The user's last name or surname."),
    given_name: str | None = Field(None, alias="givenName", description="The user's first name."),
    display_name: str | None = Field(None, alias="displayName", description="A human-readable display name for the user, typically their full name."),
    user_type: str | None = Field(None, alias="userType", description="A free-form string indicating the user's license type within the organization (e.g., 'Full'). Cannot be updated if the user is deactivated."),
    active: bool | None = Field(None, description="Boolean flag indicating whether the user is active or deactivated in the organization."),
    emails: list[_models.ReplaceUserBodyEmailsItem] | None = Field(None, description="An array of email address objects, each containing a value, display name, and primary flag. Updates to this field are ignored for deactivated users."),
    photos: list[_models.ReplaceUserBodyPhotosItem] | None = Field(None, description="An array of profile picture objects, each specifying a type."),
    groups: list[_models.ReplaceUserBodyGroupsItem] | None = Field(None, description="An array of group/team objects the user belongs to, each containing the team's id and display name."),
    roles: list[_models.ReplaceUserBodyRolesItem] | None = Field(None, description="An array of role objects assigned to the user, each containing role type, value, display name, and primary flag. Cannot be updated if the user is deactivated."),
    preferred_language: str | None = Field(None, alias="preferredLanguage", description="The user's preferred language, specified in locale format (e.g., en_US for English)."),
    employee_number: str | None = Field(None, alias="employeeNumber", description="A unique identifier for the user within the organization, up to 20 characters maximum."),
    cost_center: str | None = Field(None, alias="costCenter", description="The cost center associated with the user, up to 120 characters maximum."),
    organization: str | None = Field(None, description="The name of the organization the user belongs to, up to 120 characters maximum."),
    division: str | None = Field(None, description="The division within the organization to which the user belongs, up to 120 characters maximum."),
    department: str | None = Field(None, description="The department within the organization to which the user belongs, up to 120 characters maximum."),
    value: str | None = Field(None, description="The manager ID value. Must be numeric; non-numeric values are ignored by the system."),
) -> dict[str, Any] | ToolResult:
    """Replace an existing user resource with updated information. Note that deactivated users cannot have their userName, userType, or roles modified, and email updates for deactivated users are silently ignored. Only active organization members (non-guests) can be updated."""

    # Construct request model with validation
    try:
        _request = _models.ReplaceUserRequest(
            path=_models.ReplaceUserRequestPath(id_=id_),
            body=_models.ReplaceUserRequestBody(user_name=user_name, display_name=display_name, user_type=user_type, active=active, emails=emails, photos=photos, groups=groups, roles=roles, preferred_language=preferred_language,
                name=_models.ReplaceUserRequestBodyName(family_name=family_name, given_name=given_name) if any(v is not None for v in [family_name, given_name]) else None,
                urn_ietf_params_scim_schemas_extension_enterprise_2_0_user=_models.ReplaceUserRequestBodyUrnIetfParamsScimSchemasExtensionEnterprise20User(employee_number=employee_number, cost_center=cost_center, organization=organization, division=division, department=department,
                    manager=_models.ReplaceUserRequestBodyUrnIetfParamsScimSchemasExtensionEnterprise20UserManager(value=value) if any(v is not None for v in [value]) else None) if any(v is not None for v in [employee_number, cost_center, organization, division, department, value]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/Users/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/Users/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: User
@mcp.tool()
async def update_user_partial(
    id_: str = Field(..., alias="id", description="The unique server-assigned identifier for the user being updated."),
    schemas: list[Literal["urn:ietf:params:scim:api:messages:2.0:PatchOp"]] = Field(..., description="Schema identifier array that designates this request as a SCIM PatchOp. Must include the SCIM patch operation schema."),
    operations: list[_models.PatchUserBodyOperationsItem] = Field(..., alias="Operations", description="Array of patch operations to apply to the user. Each operation specifies an action (Replace, Add, Remove), a target path, and a value. Supports operations for: activation status, display name, user type (license upgrade only), username, primary role (ORGANIZATION_INTERNAL_ADMIN or ORGANIZATION_INTERNAL_USER only), admin roles, and enterprise attributes (department, employeeNumber, costCenter, organization, division, manager). Guest roles and license downgrades are not supported."),
) -> dict[str, Any] | ToolResult:
    """Partially update a user resource by applying SCIM patch operations. Only specified fields are modified; unmodified fields remain unchanged. The user must be an active organization member (not a guest) to be updated."""

    # Construct request model with validation
    try:
        _request = _models.PatchUserRequest(
            path=_models.PatchUserRequestPath(id_=id_),
            body=_models.PatchUserRequestBody(schemas=schemas, operations=operations)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user_partial: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/Users/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/Users/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user_partial")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user_partial", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user_partial",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: User
@mcp.tool()
async def delete_user(id_: str = Field(..., alias="id", description="The unique identifier of the user to delete, assigned by the server.")) -> dict[str, Any] | ToolResult:
    """Permanently removes a user from the organization and transfers ownership of their boards to the oldest admin team member. The user must be an organization member (not a guest) and cannot be the last admin in their team or organization."""

    # Construct request model with validation
    try:
        _request = _models.DeleteUserRequest(
            path=_models.DeleteUserRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/Users/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/Users/{id}"
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

# Tags: Group
@mcp.tool()
async def list_groups(
    filter_: str | None = Field(None, alias="filter", description="Filter results using expressions with attribute names and operators (eq, ne, co, sw, ew, pr, gt, ge, lt, le) combined with logical operators (and, or, not). Values must be enclosed in parentheses. Filtering on complex attributes is not supported. Example: displayName eq \"Product Team\""),
    start_index: int | None = Field(None, alias="startIndex", description="The starting position for paginated results (1-based indexing). Use with count to retrieve a specific page of results."),
    count: int | None = Field(None, description="Maximum number of results to return per page. Defaults to 100 with a maximum allowed value of 1000. Use with startIndex for pagination."),
    sort_by: str | None = Field(None, alias="sortBy", description="Attribute name to sort results by. Example: displayName"),
    sort_order: Literal["ascending", "descending"] | None = Field(None, alias="sortOrder", description="Sort direction for the sortBy attribute. Must be either ascending or descending."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all groups (teams) in the organization along with their member users. Only users with member role in the organization are included in the results."""

    # Construct request model with validation
    try:
        _request = _models.ListGroupsRequest(
            query=_models.ListGroupsRequestQuery(filter_=filter_, start_index=start_index, count=count, sort_by=sort_by, sort_order=sort_order)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/Groups"
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
@mcp.tool()
async def get_group(id_: str = Field(..., alias="id", description="The unique server-assigned identifier for the group (team) to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a single group (team) resource along with its member users. Only users with member role in the organization are included in the response."""

    # Construct request model with validation
    try:
        _request = _models.GetGroupRequest(
            path=_models.GetGroupRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/Groups/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/Groups/{id}"
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

# Tags: Group
@mcp.tool()
async def update_group_members_and_details(
    id_: str = Field(..., alias="id", description="The unique server-assigned identifier for the group (team) to update."),
    schemas: Literal["urn:ietf:params:scim:api:messages:2.0:PatchOp"] = Field(..., description="Must be set to the PatchOp schema identifier to indicate this is a patch operation request."),
    operations: list[_models.PatchGroupBodyOperationsItem] = Field(..., alias="Operations", description="An array of patch operations to perform on the group. Each operation specifies an action (add, remove, or replace), a target path, and values. Multiple users can be added or removed in a single request. To update the group display name, use replace operation with the new displayName value."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing group (team) by adding, removing, or replacing members, and modifying group properties like display name. Only specified attributes are updated; unchanged attributes remain as-is."""

    # Construct request model with validation
    try:
        _request = _models.PatchGroupRequest(
            path=_models.PatchGroupRequestPath(id_=id_),
            body=_models.PatchGroupRequestBody(schemas=schemas, operations=operations)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_group_members_and_details: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/Groups/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/Groups/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_group_members_and_details")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_group_members_and_details", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_group_members_and_details",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Discovery
@mcp.tool()
async def list_resource_types() -> dict[str, Any] | ToolResult:
    """Retrieve the SCIM resource types supported by Miro, including Users and Groups. Use this to discover which resources can be managed through the SCIM API."""

    # Extract parameters for API call
    _http_path = "/ResourceTypes"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_resource_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_resource_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_resource_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Discovery
@mcp.tool()
async def get_resource_type(resource: Literal["User", "Group"] = Field(..., description="The resource type to retrieve metadata for. Must be either 'User' or 'Group'.")) -> dict[str, Any] | ToolResult:
    """Retrieve metadata for a supported resource type (User or Group). Use this to understand the structure and properties of the specified resource type."""

    # Construct request model with validation
    try:
        _request = _models.GetResourceTypeRequest(
            path=_models.GetResourceTypeRequestPath(resource=resource)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_resource_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/ResourceTypes/{resource}", _request.path.model_dump(by_alias=True)) if _request.path else "/ResourceTypes/{resource}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_resource_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_resource_type", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_resource_type",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Discovery
@mcp.tool()
async def list_schemas() -> dict[str, Any] | ToolResult:
    """Retrieve metadata about supported Users, Groups, and extension attributes in the system. Use this to discover available schema definitions and their properties."""

    # Extract parameters for API call
    _http_path = "/Schemas"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_schemas")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_schemas", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_schemas",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Discovery
@mcp.tool()
async def get_schema(uri: Literal["urn:ietf:params:scim:schemas:core:2.0:User", "urn:ietf:params:scim:schemas:core:2.0:Group", "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"] = Field(..., description="The SCIM schema URI identifying the resource type: User, Group, or Enterprise User extension schema.")) -> dict[str, Any] | ToolResult:
    """Retrieve the SCIM schema definition for a specific resource type (User, Group, or Enterprise User), including details about supported attributes and their formatting requirements."""

    # Construct request model with validation
    try:
        _request = _models.GetSchemaRequest(
            path=_models.GetSchemaRequestPath(uri=uri)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_schema: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/Schemas/{uri}", _request.path.model_dump(by_alias=True)) if _request.path else "/Schemas/{uri}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_schema")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_schema", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_schema",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organizations
@mcp.tool()
async def get_organization(org_id: str = Field(..., description="The unique identifier of the organization to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about an organization. This endpoint is available only to Enterprise plan users with Company Admin role."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGetOrganizationRequest(
            path=_models.EnterpriseGetOrganizationRequestPath(org_id=org_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Organization Members
@mcp.tool()
async def enterprise_get_organization_members(
    org_id: str = Field(..., description="id of the organization"),
    emails: str | None = Field(None, description="Emails of the organization members you want to retrieve. If you specify a value for the `emails` parameter, only the `emails` parameter is considered. All other filtering parameters are ignored. Maximum emails size is 10. Example: `emails=someEmail1@miro.com,someEmail2@miro.com`"),
    role: Literal["organization_internal_admin", "organization_internal_user", "organization_external_user", "organization_team_guest_user", "unknown"] | None = Field(None, description="Filter organization members by role"),
    license_: Literal["full", "occasional", "free", "free_restricted", "full_trial", "unknown"] | None = Field(None, alias="license", description="Filter organization members by license"),
    active: bool | None = Field(None, description="Filter results based on whether the user is active or deactivated. Learn more about <a target=\"blank\" href=\"https://help.miro.com/hc/en-us/articles/360025025894-Deactivated-users\">user deactivation</a>."),
    limit: str | None = Field(None, description="Limit for the number of organization members returned in the result list."),
) -> dict[str, Any] | ToolResult:
    """Get organization members"""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGetOrganizationMembersRequest(
            path=_models.EnterpriseGetOrganizationMembersRequestPath(org_id=org_id),
            query=_models.EnterpriseGetOrganizationMembersRequestQuery(emails=emails, role=role, license_=license_, active=active, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for enterprise_get_organization_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/members", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/members"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("enterprise_get_organization_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("enterprise_get_organization_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="enterprise_get_organization_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organization Members
@mcp.tool()
async def get_organization_member(
    org_id: str = Field(..., description="The unique identifier of the organization containing the member."),
    member_id: str = Field(..., description="The unique identifier of the organization member whose information you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific member within an organization. This operation requires Enterprise plan access and Company Admin role."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGetOrganizationMemberRequest(
            path=_models.EnterpriseGetOrganizationMemberRequestPath(org_id=org_id, member_id=member_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/members/{member_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/members/{member_id}"
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

# Tags: boards
@mcp.tool()
async def list_boards(
    team_id: str | None = Field(None, description="Filter results to boards within a specific team. When provided, overrides query and owner filters for faster results."),
    query: str | None = Field(None, description="Search for boards by name or description. Supports partial text matching up to 500 characters. Can be combined with the owner parameter to narrow results.", max_length=500),
    owner: str | None = Field(None, description="Filter results to boards owned by a specific user. Provide the owner's numeric ID, not their name. Can be combined with query to narrow results; ignored if team_id is provided."),
    limit: str | None = Field(None, description="Maximum number of boards to return per request. Must be between 1 and 50 boards; defaults to 20."),
    offset: str | None = Field(None, description="Zero-based offset for pagination. Use with limit to retrieve subsequent pages of results; defaults to 0."),
    sort: Literal["default", "last_modified", "last_opened", "last_created", "alphabetically"] | None = Field(None, description="Sort results by creation date, modification date, last opened date, or alphabetically by name. Defaults to last_created when filtering by team, otherwise last_opened."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of boards accessible to the authenticated user. Filter by team, project, owner, or search query, with support for pagination and sorting. Enterprise users with Content Admin permissions can access all boards including private ones (contents remain restricted)."""

    # Construct request model with validation
    try:
        _request = _models.GetBoardsRequest(
            query=_models.GetBoardsRequestQuery(team_id=team_id, query=query, owner=owner, limit=limit, offset=offset, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_boards: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/boards"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_boards")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_boards", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_boards",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: boards
@mcp.tool()
async def create_board(
    description: str | None = Field(None, description="Optional description of the board's purpose or content. Limited to 300 characters.", min_length=0, max_length=300),
    name: str | None = Field(None, description="Display name for the board. Defaults to 'Untitled' if not provided. Must be between 1 and 60 characters.", min_length=1, max_length=60),
    collaboration_tools_start_access: Literal["all_editors", "board_owners_and_coowners"] | None = Field(None, alias="collaborationToolsStartAccess", description="Controls who can initiate or stop collaboration features like timers, voting, video chat, and screen sharing. Other users can only join these features. Defaults to allowing all editors. Contact Miro support to modify this setting."),
    copy_access: Literal["anyone", "team_members", "team_editors", "board_owner"] | None = Field(None, alias="copyAccess", description="Determines who can copy the board, duplicate objects, export images, or save as template/PDF. Defaults to allowing anyone. Options range from open access to board owner only."),
    sharing_access: Literal["team_members_with_editing_rights", "owner_and_coowners"] | None = Field(None, alias="sharingAccess", description="Controls who can modify board access permissions and invite new users. Defaults to team members with editing rights. Contact Miro support to change this setting."),
    access: Literal["private", "view", "edit", "comment"] | None = Field(None, description="Sets the public access level for the board. Defaults to private. Options include private (no public access), view-only, comment, or full edit access."),
    invite_to_account_and_board_link_access: Literal["viewer", "commenter", "editor", "no_access"] | None = Field(None, alias="inviteToAccountAndBoardLinkAccess", description="Specifies the default user role when inviting users via team and board links. Defaults to no access. Enterprise users are always set to no access regardless of this value."),
    organization_access: Literal["private", "view", "comment", "edit"] | None = Field(None, alias="organizationAccess", description="Controls organization-level access to the board. Defaults to private. Only applies if the team belongs to an organization; otherwise defaults are used."),
    team_access: Literal["private", "view", "comment", "edit"] | None = Field(None, alias="teamAccess", description="Sets team-level access to the board. Defaults to edit access on free plans and private on other plans. Options include private, view-only, comment, or edit access."),
    team_id: str | None = Field(None, alias="teamId", description="The unique identifier of the team where the board will be created. If not specified, the board is created in the default team. On Enterprise plans, board owners and admins can move boards between teams via API."),
) -> dict[str, Any] | ToolResult:
    """Creates a new board with a specified name, description, and access control policies. Configure sharing permissions, collaboration tool access, and team placement to control who can view, edit, and manage the board."""

    # Construct request model with validation
    try:
        _request = _models.CreateBoardRequest(
            body=_models.CreateBoardRequestBody(description=description, name=name, team_id=team_id,
                policy=_models.CreateBoardRequestBodyPolicy(permissions_policy=_models.CreateBoardRequestBodyPolicyPermissionsPolicy(collaboration_tools_start_access=collaboration_tools_start_access, copy_access=copy_access, sharing_access=sharing_access) if any(v is not None for v in [collaboration_tools_start_access, copy_access, sharing_access]) else None,
                    sharing_policy=_models.CreateBoardRequestBodyPolicySharingPolicy(access=access, invite_to_account_and_board_link_access=invite_to_account_and_board_link_access, organization_access=organization_access, team_access=team_access) if any(v is not None for v in [access, invite_to_account_and_board_link_access, organization_access, team_access]) else None) if any(v is not None for v in [collaboration_tools_start_access, copy_access, sharing_access, access, invite_to_account_and_board_link_access, organization_access, team_access]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_board: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/boards"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_board")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_board", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_board",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: boards
@mcp.tool()
async def create_board_copy(
    copy_from: str = Field(..., description="The unique identifier of the source board to duplicate. This board must exist and be accessible to the requesting user."),
    description: str | None = Field(None, description="Optional text describing the new board's purpose or content. Limited to 300 characters maximum.", min_length=0, max_length=300),
    name: str | None = Field(None, description="Display name for the new board. Must be between 1 and 60 characters. Defaults to 'Untitled' if not provided.", min_length=1, max_length=60),
    collaboration_tools_start_access: Literal["all_editors", "board_owners_and_coowners"] | None = Field(None, alias="collaborationToolsStartAccess", description="Controls who can initiate or stop collaboration features like timers, voting, video chat, and screen sharing. Other users can only join these features. Defaults to allowing all editors. Contact Miro support to modify this setting."),
    copy_access: Literal["anyone", "team_members", "team_editors", "board_owner"] | None = Field(None, alias="copyAccess", description="Determines who can copy the board, duplicate objects, export images, or save as template/PDF. Options range from unrestricted (anyone) to board owner only. Defaults to anyone."),
    sharing_access: Literal["team_members_with_editing_rights", "owner_and_coowners"] | None = Field(None, alias="sharingAccess", description="Controls who can modify board access settings and send invitations. Restricted to team members with editing rights or owner/co-owners only. Defaults to team members with editing rights. Contact Miro support to change this setting."),
    access: Literal["private", "view", "edit", "comment"] | None = Field(None, description="Sets the public access level for the board: private (no public access), view (read-only), edit (collaborative), or comment (feedback only). Defaults to private."),
    invite_to_account_and_board_link_access: Literal["viewer", "commenter", "editor", "no_access"] | None = Field(None, alias="inviteToAccountAndBoardLinkAccess", description="Specifies the default user role when inviting via team and board link: viewer, commenter, editor, or no access. Enterprise users are always set to no access. Defaults to no access."),
    organization_access: Literal["private", "view", "comment", "edit"] | None = Field(None, alias="organizationAccess", description="Controls organization-level access to the board if it belongs to an organization. Options: private, view, comment, or edit. Defaults to private and is ignored for teams outside an organization."),
    team_access: Literal["private", "view", "comment", "edit"] | None = Field(None, alias="teamAccess", description="Sets team-level access permissions: private (restricted), view (read-only), comment (feedback), or edit (collaborative). Defaults to edit on free plans and private on paid plans."),
    team_id: str | None = Field(None, alias="teamId", description="The unique identifier of the team where the new board should be created. If omitted, the board is placed in the default team."),
) -> dict[str, Any] | ToolResult:
    """Creates a duplicate of an existing board with optional customization of name, description, and access control policies. The new board can be placed in a specific team and configured with granular sharing and permission settings."""

    # Construct request model with validation
    try:
        _request = _models.CopyBoardRequest(
            query=_models.CopyBoardRequestQuery(copy_from=copy_from),
            body=_models.CopyBoardRequestBody(description=description, name=name, team_id=team_id,
                policy=_models.CopyBoardRequestBodyPolicy(permissions_policy=_models.CopyBoardRequestBodyPolicyPermissionsPolicy(collaboration_tools_start_access=collaboration_tools_start_access, copy_access=copy_access, sharing_access=sharing_access) if any(v is not None for v in [collaboration_tools_start_access, copy_access, sharing_access]) else None,
                    sharing_policy=_models.CopyBoardRequestBodyPolicySharingPolicy(access=access, invite_to_account_and_board_link_access=invite_to_account_and_board_link_access, organization_access=organization_access, team_access=team_access) if any(v is not None for v in [access, invite_to_account_and_board_link_access, organization_access, team_access]) else None) if any(v is not None for v in [collaboration_tools_start_access, copy_access, sharing_access, access, invite_to_account_and_board_link_access, organization_access, team_access]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_board_copy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/boards"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_board_copy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_board_copy", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_board_copy",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: boards
@mcp.tool()
async def get_board(board_id: str = Field(..., description="The unique identifier of the board to retrieve. This is a required string that identifies which board's information should be returned.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific board by its unique identifier. This operation requires boards:read scope and is rate-limited at Level 1."""

    # Construct request model with validation
    try:
        _request = _models.GetSpecificBoardRequest(
            path=_models.GetSpecificBoardRequestPath(board_id=board_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_board: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_board")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_board", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_board",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: boards
@mcp.tool()
async def update_board(
    board_id: str = Field(..., description="The unique identifier of the board to update."),
    description: str | None = Field(None, description="Board description text. Must be between 0 and 300 characters.", min_length=0, max_length=300),
    name: str | None = Field(None, description="Board display name. Must be between 1 and 60 characters. Defaults to 'Untitled' if not specified.", min_length=1, max_length=60),
    collaboration_tools_start_access: Literal["all_editors", "board_owners_and_coowners"] | None = Field(None, alias="collaborationToolsStartAccess", description="Controls who can initiate collaboration tools (timer, voting, video chat, screen sharing, attention management). Others can only join. Defaults to all editors. Contact Miro Support to change this setting."),
    copy_access: Literal["anyone", "team_members", "team_editors", "board_owner"] | None = Field(None, alias="copyAccess", description="Controls who can copy the board, copy objects, download images, and export as template or PDF. Options range from anyone to board owner only. Defaults to anyone."),
    sharing_access: Literal["team_members_with_editing_rights", "owner_and_coowners"] | None = Field(None, alias="sharingAccess", description="Controls who can modify board access and invite users. Defaults to team members with editing rights. Contact Miro Support to change this setting."),
    access: Literal["private", "view", "edit", "comment"] | None = Field(None, description="Sets public-level access to the board: private (no public access), view (public read-only), edit (public editable), or comment (public comment-only). Defaults to private."),
    invite_to_account_and_board_link_access: Literal["viewer", "commenter", "editor", "no_access"] | None = Field(None, alias="inviteToAccountAndBoardLinkAccess", description="Defines the user role assigned when inviting users via team and board link. Defaults to no_access. For Enterprise users, this is always set to no_access regardless of the value provided."),
    organization_access: Literal["private", "view", "comment", "edit"] | None = Field(None, alias="organizationAccess", description="Sets organization-level access to the board. Only applies if the board's team belongs to an organization. Defaults to private. Defaults to private if the team is not part of an organization."),
    team_access: Literal["private", "view", "comment", "edit"] | None = Field(None, alias="teamAccess", description="Sets team-level access to the board. Defaults to edit on free plans and private on other plans."),
    team_id: str | None = Field(None, alias="teamId", description="The unique identifier of the team where the board should be moved. On Enterprise plans, Board Owners, Co-Owners, and Content Admins can move boards. On non-Enterprise plans, only Board Owners can move boards."),
) -> dict[str, Any] | ToolResult:
    """Update board settings including name, description, and access control permissions. Requires boards:write scope and is subject to rate limiting at Level 2."""

    # Construct request model with validation
    try:
        _request = _models.UpdateBoardRequest(
            path=_models.UpdateBoardRequestPath(board_id=board_id),
            body=_models.UpdateBoardRequestBody(description=description, name=name, team_id=team_id,
                policy=_models.UpdateBoardRequestBodyPolicy(permissions_policy=_models.UpdateBoardRequestBodyPolicyPermissionsPolicy(collaboration_tools_start_access=collaboration_tools_start_access, copy_access=copy_access, sharing_access=sharing_access) if any(v is not None for v in [collaboration_tools_start_access, copy_access, sharing_access]) else None,
                    sharing_policy=_models.UpdateBoardRequestBodyPolicySharingPolicy(access=access, invite_to_account_and_board_link_access=invite_to_account_and_board_link_access, organization_access=organization_access, team_access=team_access) if any(v is not None for v in [access, invite_to_account_and_board_link_access, organization_access, team_access]) else None) if any(v is not None for v in [collaboration_tools_start_access, copy_access, sharing_access, access, invite_to_account_and_board_link_access, organization_access, team_access]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_board: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_board")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_board", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_board",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: boards
@mcp.tool()
async def delete_board(board_id: str = Field(..., description="The unique identifier of the board to delete. This is a required string that identifies which board will be removed.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a board, moving it to Trash on paid plans where it can be restored within 90 days. On free plans, deletion may be immediate."""

    # Construct request model with validation
    try:
        _request = _models.DeleteBoardRequest(
            path=_models.DeleteBoardRequestPath(board_id=board_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_board: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_board")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_board", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_board",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: app_cards
@mcp.tool()
async def create_app_card(
    board_id: str = Field(..., description="The unique identifier of the board where the app card will be created."),
    description: str | None = Field(None, description="A short text description providing context about the app card's purpose or content."),
    fields: list[_models.CustomField] | None = Field(None, description="An array of custom preview field objects that will be displayed in the bottom half of the app card in compact view. Each field object defines a key-value pair for the preview."),
    status: Literal["disconnected", "connected", "disabled"] | None = Field(None, description="The synchronization status of the app card with its source. Use 'disconnected' for new cards, 'connected' when synced with an active source, or 'disabled' if the source has been deleted. Defaults to 'disconnected'."),
    title: str | None = Field(None, description="A short text header identifying the app card. Defaults to 'sample app card item'."),
    fill_color: str | None = Field(None, alias="fillColor", description="The hex color code for the app card's border. Defaults to '#2d9bf0' (blue)."),
    height: float | None = Field(None, description="The height of the app card in pixels."),
    rotation: float | None = Field(None, description="The rotation angle of the app card in degrees relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation."),
    width: float | None = Field(None, description="The width of the app card in pixels."),
) -> dict[str, Any] | ToolResult:
    """Adds a new app card item to a board. App cards display custom content with optional preview fields and can be styled with colors, dimensions, and rotation."""

    # Construct request model with validation
    try:
        _request = _models.CreateAppCardItemRequest(
            path=_models.CreateAppCardItemRequestPath(board_id=board_id),
            body=_models.CreateAppCardItemRequestBody(data=_models.CreateAppCardItemRequestBodyData(description=description, fields=fields, status=status, title=title) if any(v is not None for v in [description, fields, status, title]) else None,
                style=_models.CreateAppCardItemRequestBodyStyle(fill_color=fill_color) if any(v is not None for v in [fill_color]) else None,
                geometry=_models.CreateAppCardItemRequestBodyGeometry(height=height, rotation=rotation, width=width) if any(v is not None for v in [height, rotation, width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_app_card: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/app_cards", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/app_cards"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_app_card")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_app_card", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_app_card",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: app_cards
@mcp.tool()
async def get_app_card_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the app card item you want to retrieve."),
    item_id: str = Field(..., description="The unique identifier of the specific app card item to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific app card item on a board. Use this to fetch properties and content of an individual app card."""

    # Construct request model with validation
    try:
        _request = _models.GetAppCardItemRequest(
            path=_models.GetAppCardItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_app_card_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/app_cards/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/app_cards/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_app_card_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_app_card_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_app_card_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: app_cards
@mcp.tool()
async def update_app_card_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the app card item to update."),
    item_id: str = Field(..., description="The unique identifier of the app card item to update."),
    description: str | None = Field(None, description="A short text description providing context about the app card's purpose or content."),
    fields: list[_models.CustomField] | None = Field(None, description="An array of custom preview field objects displayed in the compact view on the bottom half of the app card. Each field object defines a key-value pair shown to users."),
    status: Literal["disconnected", "connected", "disabled"] | None = Field(None, description="The connection status of the app card. Use 'connected' when synced with the source, 'disconnected' when not synced, or 'disabled' when the source has been deleted. Defaults to 'disconnected'."),
    title: str | None = Field(None, description="A short text header identifying the app card. Defaults to 'sample app card item'."),
    fill_color: str | None = Field(None, alias="fillColor", description="The hex color value for the app card's border. Specify as a six-digit hex code (e.g., #2d9bf0)."),
    height: float | None = Field(None, description="The height of the app card in pixels. Specify as a numeric value."),
    rotation: float | None = Field(None, description="The rotation angle of the app card in degrees relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation."),
    width: float | None = Field(None, description="The width of the app card in pixels. Specify as a numeric value."),
) -> dict[str, Any] | ToolResult:
    """Update an app card item on a board by modifying its content, styling, and metadata. Changes are applied to the specified item and reflected immediately on the board."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAppCardItemRequest(
            path=_models.UpdateAppCardItemRequestPath(board_id=board_id, item_id=item_id),
            body=_models.UpdateAppCardItemRequestBody(data=_models.UpdateAppCardItemRequestBodyData(description=description, fields=fields, status=status, title=title) if any(v is not None for v in [description, fields, status, title]) else None,
                style=_models.UpdateAppCardItemRequestBodyStyle(fill_color=fill_color) if any(v is not None for v in [fill_color]) else None,
                geometry=_models.UpdateAppCardItemRequestBodyGeometry(height=height, rotation=rotation, width=width) if any(v is not None for v in [height, rotation, width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_app_card_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/app_cards/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/app_cards/{item_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_app_card_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_app_card_item", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_app_card_item",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: app_cards
@mcp.tool()
async def delete_app_card_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the app card item to delete."),
    item_id: str = Field(..., description="The unique identifier of the app card item to delete from the board."),
) -> dict[str, Any] | ToolResult:
    """Removes an app card item from a specified board. Requires boards:write scope and is subject to Level 3 rate limiting."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAppCardItemRequest(
            path=_models.DeleteAppCardItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_app_card_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/app_cards/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/app_cards/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_app_card_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_app_card_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_app_card_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: cards
@mcp.tool()
async def create_card_item(
    board_id: str = Field(..., description="The unique identifier of the board where the card will be created."),
    assignee_id: str | None = Field(None, alias="assigneeId", description="The numeric user ID of the person assigned to own this card. User IDs are automatically assigned when users first sign up."),
    description: str | None = Field(None, description="A short text description providing context or details about the card's content."),
    due_date: str | None = Field(None, alias="dueDate", description="The completion deadline for the task or activity, specified in UTC using ISO 8601 format with a trailing Z offset (e.g., 2023-10-12T22:00:55.000Z)."),
    title: str | None = Field(None, description="A short text header or title for the card."),
    card_theme: str | None = Field(None, alias="cardTheme", description="The hex color code for the card's border. Defaults to #2d9bf0 (blue) if not specified."),
    height: float | None = Field(None, description="The height of the card in pixels."),
    rotation: float | None = Field(None, description="The rotation angle of the card in degrees relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation."),
    width: float | None = Field(None, description="The width of the card in pixels."),
) -> dict[str, Any] | ToolResult:
    """Creates a new card item on a specified board. Cards can include a title, description, due date, assignee, and visual styling to organize tasks and activities."""

    # Construct request model with validation
    try:
        _request = _models.CreateCardItemRequest(
            path=_models.CreateCardItemRequestPath(board_id=board_id),
            body=_models.CreateCardItemRequestBody(data=_models.CreateCardItemRequestBodyData(assignee_id=assignee_id, description=description, due_date=due_date, title=title) if any(v is not None for v in [assignee_id, description, due_date, title]) else None,
                style=_models.CreateCardItemRequestBodyStyle(card_theme=card_theme) if any(v is not None for v in [card_theme]) else None,
                geometry=_models.CreateCardItemRequestBodyGeometry(height=height, rotation=rotation, width=width) if any(v is not None for v in [height, rotation, width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_card_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/cards", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/cards"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_card_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_card_item", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_card_item",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: cards
@mcp.tool()
async def get_card_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the card item you want to retrieve."),
    item_id: str = Field(..., description="The unique identifier of the card item you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific card item on a board. Use this to fetch card properties, content, and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetCardItemRequest(
            path=_models.GetCardItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_card_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/cards/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/cards/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_card_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_card_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_card_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: cards
@mcp.tool()
async def update_card_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the card item to update."),
    item_id: str = Field(..., description="The unique identifier of the card item to update."),
    assignee_id: str | None = Field(None, alias="assigneeId", description="The numeric user ID of the person assigned to this card. This ID is automatically assigned when a user first signs up."),
    description: str | None = Field(None, description="A short text description providing context or details about the card's content."),
    due_date: str | None = Field(None, alias="dueDate", description="The date when the task or activity is due, formatted as an ISO 8601 UTC timestamp with a trailing Z offset (e.g., 2023-10-12T22:00:55.000Z)."),
    title: str | None = Field(None, description="A short text title or header for the card."),
    card_theme: str | None = Field(None, alias="cardTheme", description="The hex color code for the card's border, used to visually theme or categorize the card."),
    height: float | None = Field(None, description="The height of the card in pixels."),
    rotation: float | None = Field(None, description="The rotation angle of the card in degrees relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation."),
    width: float | None = Field(None, description="The width of the card in pixels."),
) -> dict[str, Any] | ToolResult:
    """Update a card item on a board with new content, styling, and metadata. Modify the card's title, description, due date, assignee, dimensions, rotation, and theme color."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCardItemRequest(
            path=_models.UpdateCardItemRequestPath(board_id=board_id, item_id=item_id),
            body=_models.UpdateCardItemRequestBody(data=_models.UpdateCardItemRequestBodyData(assignee_id=assignee_id, description=description, due_date=due_date, title=title) if any(v is not None for v in [assignee_id, description, due_date, title]) else None,
                style=_models.UpdateCardItemRequestBodyStyle(card_theme=card_theme) if any(v is not None for v in [card_theme]) else None,
                geometry=_models.UpdateCardItemRequestBodyGeometry(height=height, rotation=rotation, width=width) if any(v is not None for v in [height, rotation, width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_card_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/cards/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/cards/{item_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_card_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_card_item", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_card_item",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: cards
@mcp.tool()
async def delete_card_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the card item to delete."),
    item_id: str = Field(..., description="The unique identifier of the card item to delete from the board."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a card item from a board. This action cannot be undone and requires write access to the board."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCardItemRequest(
            path=_models.DeleteCardItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_card_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/cards/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/cards/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_card_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_card_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_card_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: connectors
@mcp.tool()
async def list_connectors_for_board(
    board_id: str = Field(..., description="The unique identifier of the board from which to retrieve connectors."),
    limit: str | None = Field(None, description="The maximum number of connectors to return per request, between 10 and 50. Defaults to 10. If more results exist, the response includes a cursor for fetching the next page."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of connectors for a specific board using cursor-based pagination. Use the cursor from the response to fetch subsequent pages of results."""

    # Construct request model with validation
    try:
        _request = _models.GetConnectorsRequest(
            path=_models.GetConnectorsRequestPath(board_id=board_id),
            query=_models.GetConnectorsRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_connectors_for_board: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/connectors", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/connectors"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_connectors_for_board")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_connectors_for_board", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_connectors_for_board",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: connectors
@mcp.tool()
async def create_connector(
    board_id: str = Field(..., description="The unique identifier of the board where the connector will be created."),
    start_item_id: str | None = Field(None, alias="startItemId", description="The unique identifier of the item where the connector starts. Frames are not supported."),
    end_item_id: str | None = Field(None, alias="endItemId", description="The unique identifier of the item where the connector ends. Frames are not supported."),
    start_item_snap_to: Literal["auto", "top", "right", "bottom", "left"] | None = Field(None, alias="startItemSnapTo", description="The side of the start item where the connector attaches (top, right, bottom, or left). Use 'auto' to automatically select the optimal connection point. Defaults to 'auto' if neither this nor position is specified."),
    end_item_snap_to: Literal["auto", "top", "right", "bottom", "left"] | None = Field(None, alias="endItemSnapTo", description="The side of the end item where the connector attaches (top, right, bottom, or left). Use 'auto' to automatically select the optimal connection point. Defaults to 'auto' if neither this nor position is specified."),
    shape: Literal["straight", "elbowed", "curved"] | None = Field(None, description="The visual path type of the connector line: 'straight' for direct lines, 'elbowed' for right-angle turns, or 'curved' for smooth curves. Defaults to 'curved'."),
    captions: list[_models.Caption] | None = Field(None, description="An array of text blocks to display on the connector, with a maximum of 20 captions.", max_length=20, min_length=0),
    color: str | None = Field(None, description="The hex color code for the caption text. Defaults to '#1a1a1a' (dark gray)."),
    end_stroke_cap: Literal["none", "stealth", "rounded_stealth", "diamond", "filled_diamond", "oval", "filled_oval", "arrow", "triangle", "filled_triangle", "erd_one", "erd_many", "erd_only_one", "erd_zero_or_one", "erd_one_or_many", "erd_zero_or_many", "unknown"] | None = Field(None, alias="endStrokeCap", description="The decoration style at the end of the connector line, such as arrows, circles, or ERD symbols. Defaults to 'stealth'."),
    font_size: str | None = Field(None, alias="fontSize", description="The font size for captions in density-independent pixels, ranging from 10 to 288. Defaults to 14."),
    start_stroke_cap: Literal["none", "stealth", "rounded_stealth", "diamond", "filled_diamond", "oval", "filled_oval", "arrow", "triangle", "filled_triangle", "erd_one", "erd_many", "erd_only_one", "erd_zero_or_one", "erd_one_or_many", "erd_zero_or_many", "unknown"] | None = Field(None, alias="startStrokeCap", description="The decoration style at the start of the connector line, such as arrows, circles, or ERD symbols. Defaults to 'none'."),
    stroke_color: str | None = Field(None, alias="strokeColor", description="The hex color code for the connector line. Defaults to '#000000' (black)."),
    stroke_style: Literal["normal", "dotted", "dashed"] | None = Field(None, alias="strokeStyle", description="The stroke pattern of the connector line: 'normal' for solid, 'dotted' for dots, or 'dashed' for dashes. Defaults to 'normal'."),
    stroke_width: str | None = Field(None, alias="strokeWidth", description="The thickness of the connector line in density-independent pixels, ranging from 1 to 24. Defaults to 1.0."),
    text_orientation: Literal["horizontal", "aligned"] | None = Field(None, alias="textOrientation", description="The orientation of captions relative to the connector line: 'horizontal' for fixed horizontal text or 'aligned' to follow the line's curvature. Defaults to 'aligned'."),
) -> dict[str, Any] | ToolResult:
    """Creates a connector between two items on a board, with customizable styling, line shape, and optional text captions. Connectors can be attached to specific sides of items or automatically positioned."""

    # Construct request model with validation
    try:
        _request = _models.CreateConnectorRequest(
            path=_models.CreateConnectorRequestPath(board_id=board_id),
            body=_models.CreateConnectorRequestBody(shape=shape, captions=captions,
                start_item=_models.CreateConnectorRequestBodyStartItem(id_=start_item_id, snap_to=start_item_snap_to) if any(v is not None for v in [start_item_id, start_item_snap_to]) else None,
                end_item=_models.CreateConnectorRequestBodyEndItem(id_=end_item_id, snap_to=end_item_snap_to) if any(v is not None for v in [end_item_id, end_item_snap_to]) else None,
                style=_models.CreateConnectorRequestBodyStyle(color=color, end_stroke_cap=end_stroke_cap, font_size=font_size, start_stroke_cap=start_stroke_cap, stroke_color=stroke_color, stroke_style=stroke_style, stroke_width=stroke_width, text_orientation=text_orientation) if any(v is not None for v in [color, end_stroke_cap, font_size, start_stroke_cap, stroke_color, stroke_style, stroke_width, text_orientation]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_connector: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/connectors", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/connectors"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_connector")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_connector", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_connector",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: connectors
@mcp.tool()
async def get_connector(
    board_id: str = Field(..., description="The unique identifier of the board containing the connector you want to retrieve."),
    connector_id: str = Field(..., description="The unique identifier of the connector whose information you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific connector on a board, including its configuration and properties."""

    # Construct request model with validation
    try:
        _request = _models.GetConnectorRequest(
            path=_models.GetConnectorRequestPath(board_id=board_id, connector_id=connector_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_connector: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/connectors/{connector_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/connectors/{connector_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_connector")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_connector", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_connector",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: connectors
@mcp.tool()
async def update_connector(
    board_id: str = Field(..., description="The unique identifier of the board containing the connector to update."),
    connector_id: str = Field(..., description="The unique identifier of the connector to update."),
    start_item_id: str | None = Field(None, alias="startItemId", description="The unique identifier of the item to attach the connector's start point to. Frames are not supported."),
    end_item_id: str | None = Field(None, alias="endItemId", description="The unique identifier of the item to attach the connector's end point to. Frames are not supported."),
    start_item_snap_to: Literal["auto", "top", "right", "bottom", "left"] | None = Field(None, alias="startItemSnapTo", description="Which side of the start item to attach the connector: auto (automatic placement), top, right, bottom, or left. Cannot be combined with position-based attachment. Defaults to auto if not specified."),
    end_item_snap_to: Literal["auto", "top", "right", "bottom", "left"] | None = Field(None, alias="endItemSnapTo", description="Which side of the end item to attach the connector: auto (automatic placement), top, right, bottom, or left. Cannot be combined with position-based attachment. Defaults to auto if not specified."),
    shape: Literal["straight", "elbowed", "curved"] | None = Field(None, description="The connector line path type: straight (direct line), elbowed (right angles), or curved (smooth bends). Defaults to curved."),
    captions: list[_models.Caption] | None = Field(None, description="Text labels to display on the connector. Supports up to 20 caption blocks.", max_length=20, min_length=0),
    color: str | None = Field(None, description="Hex color code for caption text (e.g., #9510ac)."),
    end_stroke_cap: Literal["none", "stealth", "rounded_stealth", "diamond", "filled_diamond", "oval", "filled_oval", "arrow", "triangle", "filled_triangle", "erd_one", "erd_many", "erd_only_one", "erd_zero_or_one", "erd_one_or_many", "erd_zero_or_many", "unknown"] | None = Field(None, alias="endStrokeCap", description="The decorative end cap style for the connector's endpoint: none, stealth, rounded_stealth, diamond, filled_diamond, oval, filled_oval, arrow, triangle, filled_triangle, or ERD notation styles (erd_one, erd_many, erd_only_one, erd_zero_or_one, erd_one_or_many, erd_zero_or_many, unknown)."),
    font_size: str | None = Field(None, alias="fontSize", description="Font size for captions in density-independent pixels, between 10 and 288."),
    start_stroke_cap: Literal["none", "stealth", "rounded_stealth", "diamond", "filled_diamond", "oval", "filled_oval", "arrow", "triangle", "filled_triangle", "erd_one", "erd_many", "erd_only_one", "erd_zero_or_one", "erd_one_or_many", "erd_zero_or_many", "unknown"] | None = Field(None, alias="startStrokeCap", description="The decorative start cap style for the connector's starting point: none, stealth, rounded_stealth, diamond, filled_diamond, oval, filled_oval, arrow, triangle, filled_triangle, or ERD notation styles (erd_one, erd_many, erd_only_one, erd_zero_or_one, erd_one_or_many, erd_zero_or_many, unknown)."),
    stroke_color: str | None = Field(None, alias="strokeColor", description="Hex color code for the connector line (e.g., #2d9bf0)."),
    stroke_style: Literal["normal", "dotted", "dashed"] | None = Field(None, alias="strokeStyle", description="The line pattern style: normal (solid), dotted, or dashed."),
    stroke_width: str | None = Field(None, alias="strokeWidth", description="Line thickness in density-independent pixels, between 1 and 24."),
    text_orientation: Literal["horizontal", "aligned"] | None = Field(None, alias="textOrientation", description="Caption orientation relative to the connector line: horizontal (fixed orientation) or aligned (follows line curvature)."),
) -> dict[str, Any] | ToolResult:
    """Modify a connector's visual styling, path shape, and attachment points on a board. Update properties like line color, stroke style, captions, and connection endpoints to customize how the connector appears and connects items."""

    # Construct request model with validation
    try:
        _request = _models.UpdateConnectorRequest(
            path=_models.UpdateConnectorRequestPath(board_id=board_id, connector_id=connector_id),
            body=_models.UpdateConnectorRequestBody(shape=shape, captions=captions,
                start_item=_models.UpdateConnectorRequestBodyStartItem(id_=start_item_id, snap_to=start_item_snap_to) if any(v is not None for v in [start_item_id, start_item_snap_to]) else None,
                end_item=_models.UpdateConnectorRequestBodyEndItem(id_=end_item_id, snap_to=end_item_snap_to) if any(v is not None for v in [end_item_id, end_item_snap_to]) else None,
                style=_models.UpdateConnectorRequestBodyStyle(color=color, end_stroke_cap=end_stroke_cap, font_size=font_size, start_stroke_cap=start_stroke_cap, stroke_color=stroke_color, stroke_style=stroke_style, stroke_width=stroke_width, text_orientation=text_orientation) if any(v is not None for v in [color, end_stroke_cap, font_size, start_stroke_cap, stroke_color, stroke_style, stroke_width, text_orientation]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_connector: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/connectors/{connector_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/connectors/{connector_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_connector")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_connector", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_connector",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: connectors
@mcp.tool()
async def delete_connector(
    board_id: str = Field(..., description="The unique identifier of the board containing the connector to delete."),
    connector_id: str = Field(..., description="The unique identifier of the connector to delete from the board."),
) -> dict[str, Any] | ToolResult:
    """Removes a connector from a board. The connector is permanently deleted and cannot be recovered."""

    # Construct request model with validation
    try:
        _request = _models.DeleteConnectorRequest(
            path=_models.DeleteConnectorRequestPath(board_id=board_id, connector_id=connector_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_connector: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/connectors/{connector_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/connectors/{connector_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_connector")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_connector", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_connector",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def add_document_to_board(
    board_id: str = Field(..., description="The unique identifier of the board where the document item will be created."),
    url: str = Field(..., description="The complete URL where the document is hosted and publicly accessible. Supports standard document formats like PDF."),
    title: str | None = Field(None, description="A short text label to identify the document on the board. If not provided, the document will be added without a custom title."),
) -> dict[str, Any] | ToolResult:
    """Adds a document item to a board by hosting it at a specified URL. The document will be displayed on the board with an optional title for identification."""

    # Construct request model with validation
    try:
        _request = _models.CreateDocumentItemUsingUrlRequest(
            path=_models.CreateDocumentItemUsingUrlRequestPath(board_id=board_id),
            body=_models.CreateDocumentItemUsingUrlRequestBody(data=_models.CreateDocumentItemUsingUrlRequestBodyData(title=title, url=url))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_document_to_board: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/documents", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/documents"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_document_to_board")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_document_to_board", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_document_to_board",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def get_document_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the document item you want to retrieve."),
    item_id: str = Field(..., description="The unique identifier of the specific document item to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific document item on a board. Use this to fetch properties and metadata for a document you've identified by its ID."""

    # Construct request model with validation
    try:
        _request = _models.GetDocumentItemRequest(
            path=_models.GetDocumentItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_document_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/documents/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/documents/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_document_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_document_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_document_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def update_document_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the document item to update."),
    item_id: str = Field(..., description="The unique identifier of the document item to update."),
    title: str | None = Field(None, description="A short text header to identify the document."),
    url: str | None = Field(None, description="The URL where the document is hosted (e.g., a link to a PDF or other document file)."),
    height: float | None = Field(None, description="The height of the item in pixels, specified as a decimal number."),
    width: float | None = Field(None, description="The width of the item in pixels, specified as a decimal number."),
    rotation: float | None = Field(None, description="The rotation angle of the item in degrees relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation."),
) -> dict[str, Any] | ToolResult:
    """Update a document item on a board by modifying its properties such as title, URL, dimensions, and rotation angle."""

    # Construct request model with validation
    try:
        _request = _models.UpdateDocumentItemUsingUrlRequest(
            path=_models.UpdateDocumentItemUsingUrlRequestPath(board_id=board_id, item_id=item_id),
            body=_models.UpdateDocumentItemUsingUrlRequestBody(data=_models.UpdateDocumentItemUsingUrlRequestBodyData(title=title, url=url) if any(v is not None for v in [title, url]) else None,
                geometry=_models.UpdateDocumentItemUsingUrlRequestBodyGeometry(height=height, width=width, rotation=rotation) if any(v is not None for v in [height, width, rotation]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_document_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/documents/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/documents/{item_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_document_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_document_item", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_document_item",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def delete_document_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the document item to delete."),
    item_id: str = Field(..., description="The unique identifier of the document item to delete from the board."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a document item from a board. This action cannot be undone and requires write access to the board."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDocumentItemRequest(
            path=_models.DeleteDocumentItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_document_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/documents/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/documents/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_document_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_document_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_document_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: embeds
@mcp.tool()
async def add_embed_item_to_board(
    board_id: str = Field(..., description="The unique identifier of the board where the embed item will be created."),
    url: str = Field(..., description="A valid URL (HTTP or HTTPS) pointing to the external content resource to embed. This is the actual content that will be displayed."),
    mode: Literal["inline", "modal"] | None = Field(None, description="Controls how the embedded content appears: 'inline' displays it directly on the board, while 'modal' shows it in an overlay. Defaults to inline if not specified."),
    preview_url: str | None = Field(None, alias="previewUrl", description="URL of an image to display as the preview thumbnail for the embed item on the board."),
    height: float | None = Field(None, description="The vertical size of the embed item in pixels. If not specified, a default height will be applied."),
    width: float | None = Field(None, description="The horizontal size of the embed item in pixels. If not specified, a default width will be applied."),
) -> dict[str, Any] | ToolResult:
    """Embeds external content on a board by creating an embed item. The content can be displayed inline on the board or in a modal overlay, with optional custom preview image and dimensions."""

    # Construct request model with validation
    try:
        _request = _models.CreateEmbedItemRequest(
            path=_models.CreateEmbedItemRequestPath(board_id=board_id),
            body=_models.CreateEmbedItemRequestBody(data=_models.CreateEmbedItemRequestBodyData(mode=mode, preview_url=preview_url, url=url),
                geometry=_models.CreateEmbedItemRequestBodyGeometry(height=height, width=width) if any(v is not None for v in [height, width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_embed_item_to_board: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/embeds", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/embeds"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_embed_item_to_board")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_embed_item_to_board", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_embed_item_to_board",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: embeds
@mcp.tool()
async def get_embed_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the embed item you want to retrieve."),
    item_id: str = Field(..., description="The unique identifier of the specific embed item to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific embed item on a board. Use this to fetch properties and metadata for an embedded content item."""

    # Construct request model with validation
    try:
        _request = _models.GetEmbedItemRequest(
            path=_models.GetEmbedItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_embed_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/embeds/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/embeds/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_embed_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_embed_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_embed_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: embeds
@mcp.tool()
async def update_embed_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the embed item to update."),
    item_id: str = Field(..., description="The unique identifier of the embed item to update."),
    mode: Literal["inline", "modal"] | None = Field(None, description="Controls how the embedded content displays on the board: 'inline' shows content directly on the board, while 'modal' displays it in an overlay."),
    preview_url: str | None = Field(None, alias="previewUrl", description="URL of an image to use as the preview thumbnail for the embedded item."),
    url: str | None = Field(None, description="A valid URL (HTTP or HTTPS) pointing to the content resource to embed on the board, such as a video or web page."),
    height: float | None = Field(None, description="The height of the embed item in pixels."),
    width: float | None = Field(None, description="The width of the embed item in pixels."),
) -> dict[str, Any] | ToolResult:
    """Updates an embed item on a board, allowing you to modify its display mode, preview image, source URL, and dimensions. Requires boards:write scope."""

    # Construct request model with validation
    try:
        _request = _models.UpdateEmbedItemRequest(
            path=_models.UpdateEmbedItemRequestPath(board_id=board_id, item_id=item_id),
            body=_models.UpdateEmbedItemRequestBody(data=_models.UpdateEmbedItemRequestBodyData(mode=mode, preview_url=preview_url, url=url) if any(v is not None for v in [mode, preview_url, url]) else None,
                geometry=_models.UpdateEmbedItemRequestBodyGeometry(height=height, width=width) if any(v is not None for v in [height, width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_embed_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/embeds/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/embeds/{item_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_embed_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_embed_item", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_embed_item",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: embeds
@mcp.tool()
async def delete_embed_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the embed item to delete."),
    item_id: str = Field(..., description="The unique identifier of the embed item to delete from the board."),
) -> dict[str, Any] | ToolResult:
    """Removes an embed item from a board. The embed item is permanently deleted and cannot be recovered."""

    # Construct request model with validation
    try:
        _request = _models.DeleteEmbedItemRequest(
            path=_models.DeleteEmbedItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_embed_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/embeds/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/embeds/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_embed_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_embed_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_embed_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: images
@mcp.tool()
async def add_image_to_board(
    board_id: str = Field(..., description="The unique identifier of the board where the image will be added."),
    url: str = Field(..., description="The URL of the image to add. Must be a valid, publicly accessible image URL."),
    title: str | None = Field(None, description="A short text label to identify the image on the board."),
    height: float | None = Field(None, description="The height of the image in pixels. If not specified, the image's original height is used."),
    width: float | None = Field(None, description="The width of the image in pixels. If not specified, the image's original width is used."),
    rotation: float | None = Field(None, description="The rotation angle in degrees. Use positive values to rotate clockwise and negative values to rotate counterclockwise."),
) -> dict[str, Any] | ToolResult:
    """Adds an image item to a board by URL. Optionally customize the image with a title, dimensions, and rotation angle."""

    # Construct request model with validation
    try:
        _request = _models.CreateImageItemUsingUrlRequest(
            path=_models.CreateImageItemUsingUrlRequestPath(board_id=board_id),
            body=_models.CreateImageItemUsingUrlRequestBody(data=_models.CreateImageItemUsingUrlRequestBodyData(title=title, url=url),
                geometry=_models.CreateImageItemUsingUrlRequestBodyGeometry(height=height, width=width, rotation=rotation) if any(v is not None for v in [height, width, rotation]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_image_to_board: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/images", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/images"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_image_to_board")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_image_to_board", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_image_to_board",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: images
@mcp.tool()
async def get_image_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the image item you want to retrieve."),
    item_id: str = Field(..., description="The unique identifier of the image item you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific image item on a board, including its properties and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetImageItemRequest(
            path=_models.GetImageItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_image_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/images/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/images/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_image_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_image_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_image_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: images
@mcp.tool()
async def update_image_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the image item to update."),
    item_id: str = Field(..., description="The unique identifier of the image item to update."),
    title: str | None = Field(None, description="A short text header to identify the image on the board."),
    url: str | None = Field(None, description="The URL pointing to the image resource to display."),
    height: float | None = Field(None, description="The height of the image item in pixels."),
    width: float | None = Field(None, description="The width of the image item in pixels."),
    rotation: float | None = Field(None, description="The rotation angle of the image in degrees relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation."),
) -> dict[str, Any] | ToolResult:
    """Update an image item on a board by modifying its URL, title, dimensions, or rotation angle. Requires boards:write scope."""

    # Construct request model with validation
    try:
        _request = _models.UpdateImageItemUsingUrlRequest(
            path=_models.UpdateImageItemUsingUrlRequestPath(board_id=board_id, item_id=item_id),
            body=_models.UpdateImageItemUsingUrlRequestBody(data=_models.UpdateImageItemUsingUrlRequestBodyData(title=title, url=url) if any(v is not None for v in [title, url]) else None,
                geometry=_models.UpdateImageItemUsingUrlRequestBodyGeometry(height=height, width=width, rotation=rotation) if any(v is not None for v in [height, width, rotation]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_image_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/images/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/images/{item_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_image_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_image_item", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_image_item",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: images
@mcp.tool()
async def delete_image_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the image item to delete."),
    item_id: str = Field(..., description="The unique identifier of the image item to delete from the board."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes an image item from a board. Requires boards:write scope and is subject to Level 3 rate limiting."""

    # Construct request model with validation
    try:
        _request = _models.DeleteImageItemRequest(
            path=_models.DeleteImageItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_image_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/images/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/images/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_image_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_image_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_image_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: items
@mcp.tool()
async def list_board_items(
    board_id: str = Field(..., description="The unique identifier of the board from which to retrieve items."),
    limit: str | None = Field(None, description="The maximum number of items to return per request, between 10 and 50. Defaults to 10. If more items exist, use the cursor from the response to fetch the next batch."),
    type_: Literal["text", "shape", "sticky_note", "image", "document", "card", "app_card", "preview", "frame", "embed", "doc_format", "data_table_format"] | None = Field(None, alias="type", description="Filter results to a specific item type (e.g., cards, sticky notes, shapes). Omit to retrieve all item types on the board."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of items on a board, with optional filtering by item type. Use cursor-based pagination to navigate through results."""

    # Construct request model with validation
    try:
        _request = _models.GetItemsRequest(
            path=_models.GetItemsRequestPath(board_id=board_id),
            query=_models.GetItemsRequestQuery(limit=limit, type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_board_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/items", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_board_items")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_board_items", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_board_items",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: items
@mcp.tool()
async def get_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the item you want to retrieve."),
    item_id: str = Field(..., description="The unique identifier of the item you want to retrieve from the board."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific item on a board. This operation requires read access to the board and is rate-limited at Level 1."""

    # Construct request model with validation
    try:
        _request = _models.GetSpecificItemRequest(
            path=_models.GetSpecificItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/items/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/items/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: items
@mcp.tool()
async def update_item_position_or_parent(
    board_id: str = Field(..., description="The unique identifier of the board containing the item to update."),
    item_id: str = Field(..., description="The unique identifier of the item whose position or parent you want to change."),
    x: float | None = Field(None, description="X-axis coordinate of the location of the item on the board.\nBy default, all items have absolute positioning to the board, not the current viewport. Default: `0`.\nThe center point of the board has `x: 0` and `y: 0` coordinates."),
    y: float | None = Field(None, description="Y-axis coordinate of the location of the item on the board.\nBy default, all items have absolute positioning to the board, not the current viewport. Default: `0`.\nThe center point of the board has `x: 0` and `y: 0` coordinates."),
    id_: str | None = Field(None, alias="id", description="Unique identifier (ID) of the parent frame for the item."),
) -> dict[str, Any] | ToolResult:
    """Reposition an item on a board or move it to a different parent container. Use this operation to reorganize board layout or change item hierarchy."""

    # Construct request model with validation
    try:
        _request = _models.UpdateItemPositionOrParentRequest(
            path=_models.UpdateItemPositionOrParentRequestPath(board_id=board_id, item_id=item_id),
            body=_models.UpdateItemPositionOrParentRequestBody(position=_models.UpdateItemPositionOrParentRequestBodyPosition(x=x, y=y) if any(v is not None for v in [x, y]) else None,
                parent=_models.UpdateItemPositionOrParentRequestBodyParent(id_=id_) if any(v is not None for v in [id_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_item_position_or_parent: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/items/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/items/{item_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_item_position_or_parent")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_item_position_or_parent", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_item_position_or_parent",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: items
@mcp.tool()
async def delete_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the item to delete."),
    item_id: str = Field(..., description="The unique identifier of the item to delete from the board."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes an item from a board. This action cannot be undone and requires boards:write scope."""

    # Construct request model with validation
    try:
        _request = _models.DeleteItemRequest(
            path=_models.DeleteItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/items/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/items/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: board_members
@mcp.tool()
async def list_board_members(
    board_id: str = Field(..., description="The unique identifier of the board whose members you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of board members to return per request, between 1 and 50. Defaults to 20 if not specified."),
    offset: str | None = Field(None, description="The zero-based starting position for retrieving results, used for pagination. Defaults to 0 to start from the first member."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a pageable list of all members assigned to a specific board. Use pagination parameters to control the number of results and navigate through large member lists."""

    # Construct request model with validation
    try:
        _request = _models.GetBoardMembersRequest(
            path=_models.GetBoardMembersRequestPath(board_id=board_id),
            query=_models.GetBoardMembersRequestQuery(limit=limit, offset=offset)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_board_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/members", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/members"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_board_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_board_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_board_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: board_members
@mcp.tool()
async def invite_members_to_board(
    board_id: str = Field(..., description="The unique identifier of the board where members will be invited."),
    emails: list[str] = Field(..., description="Email addresses of users to invite to the board. You can invite between 1 and 20 members per request.", min_length=1, max_length=20),
    role: Literal["viewer", "commenter", "editor", "coowner", "owner"] | None = Field(None, description="The role assigned to invited members. Defaults to 'commenter' if not specified. Valid roles are: viewer, commenter, editor, coowner, or owner (owner and coowner have equivalent effects)."),
    message: str | None = Field(None, description="Optional custom message to include in the invitation email sent to members."),
) -> dict[str, Any] | ToolResult:
    """Invite new members to collaborate on a board by sending invitation emails. Membership requirements depend on the board's sharing policy."""

    # Construct request model with validation
    try:
        _request = _models.ShareBoardRequest(
            path=_models.ShareBoardRequestPath(board_id=board_id),
            body=_models.ShareBoardRequestBody(emails=emails, role=role, message=message)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for invite_members_to_board: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/members", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/members"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("invite_members_to_board")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("invite_members_to_board", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="invite_members_to_board",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: board_members
@mcp.tool()
async def get_board_member(
    board_id: str = Field(..., description="The unique identifier of the board containing the member you want to retrieve."),
    board_member_id: str = Field(..., description="The unique identifier of the board member whose information you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific member of a board, including their role and permissions."""

    # Construct request model with validation
    try:
        _request = _models.GetSpecificBoardMemberRequest(
            path=_models.GetSpecificBoardMemberRequestPath(board_id=board_id, board_member_id=board_member_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_board_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/members/{board_member_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/members/{board_member_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_board_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_board_member", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_board_member",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: board_members
@mcp.tool()
async def update_board_member_role(
    board_id: str = Field(..., description="The unique identifier of the board containing the member whose role you want to update."),
    board_member_id: str = Field(..., description="The unique identifier of the board member whose role you want to change."),
    role: Literal["viewer", "commenter", "editor", "coowner", "owner"] | None = Field(None, description="The new role to assign to the board member. Valid roles are viewer (read-only access), commenter (can view and comment), editor (can view, comment, and edit), coowner (full access with administrative capabilities), or owner (full ownership). Defaults to commenter if not specified."),
) -> dict[str, Any] | ToolResult:
    """Update the role assigned to a board member, controlling their access level and permissions on the board."""

    # Construct request model with validation
    try:
        _request = _models.UpdateBoardMemberRequest(
            path=_models.UpdateBoardMemberRequestPath(board_id=board_id, board_member_id=board_member_id),
            body=_models.UpdateBoardMemberRequestBody(role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_board_member_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/members/{board_member_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/members/{board_member_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_board_member_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_board_member_role", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_board_member_role",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: board_members
@mcp.tool()
async def remove_board_member(
    board_id: str = Field(..., description="The unique identifier of the board from which you want to remove the member."),
    board_member_id: str = Field(..., description="The unique identifier of the board member you want to remove from the board."),
) -> dict[str, Any] | ToolResult:
    """Remove a member from a board. This operation deletes the specified board member's access and role from the board."""

    # Construct request model with validation
    try:
        _request = _models.RemoveBoardMemberRequest(
            path=_models.RemoveBoardMemberRequestPath(board_id=board_id, board_member_id=board_member_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_board_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/members/{board_member_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/members/{board_member_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_board_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_board_member", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_board_member",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shapes
@mcp.tool()
async def add_shape_to_board(
    board_id: str = Field(..., description="The unique identifier of the board where the shape will be created."),
    content: str | None = Field(None, description="Optional text content to display on the shape. Not supported for flow_chart_or and flow_chart_summing_junction shapes."),
    shape: str | None = Field(None, description="The geometric shape type to render. Choose from basic shapes (rectangle, circle, triangle, etc.), flowchart shapes (decision, process, terminator, etc.), or arrow/callout variants. Defaults to rectangle."),
    border_color: str | None = Field(None, alias="borderColor", description="Hex color code for the shape border. Defaults to dark gray (#1a1a1a)."),
    border_opacity: str | None = Field(None, alias="borderOpacity", description="Opacity of the border as a decimal between 0 (fully transparent) and 1 (fully opaque). Defaults to 1.0."),
    border_style: Literal["normal", "dotted", "dashed"] | None = Field(None, alias="borderStyle", description="Visual style of the border: normal (solid), dotted, or dashed. Defaults to normal."),
    border_width: str | None = Field(None, alias="borderWidth", description="Border thickness in display pixels, ranging from 1 to 24. Defaults to 2.0."),
    color: str | None = Field(None, description="Hex color code for the text content. Defaults to dark gray (#1a1a1a)."),
    fill_color: str | None = Field(None, alias="fillColor", description="Hex color code for the shape fill. Accepts predefined palette colors or custom hex values. Defaults to white (#ffffff)."),
    fill_opacity: str | None = Field(None, alias="fillOpacity", description="Opacity of the fill color as a decimal between 0 (fully transparent) and 1 (fully opaque). Defaults to 1.0 for flowchart shapes, or 1.0 if fillColor is specified for basic shapes, otherwise 0.0."),
    font_family: Literal["arial", "abril_fatface", "bangers", "eb_garamond", "georgia", "graduate", "gravitas_one", "fredoka_one", "nixie_one", "open_sans", "permanent_marker", "pt_sans", "pt_sans_narrow", "pt_serif", "rammetto_one", "roboto", "roboto_condensed", "roboto_slab", "caveat", "times_new_roman", "titan_one", "lemon_tuesday", "roboto_mono", "noto_sans", "plex_sans", "plex_serif", "plex_mono", "spoof", "tiempos_text", "formular"] | None = Field(None, alias="fontFamily", description="Font family for text rendering. Choose from standard fonts (Arial, Georgia, Times New Roman) or decorative options (Bangers, Permanent Marker, etc.). Defaults to Arial."),
    font_size: str | None = Field(None, alias="fontSize", description="Font size for text in display pixels, ranging from 10 to 288. Defaults to 14."),
    text_align: Literal["left", "right", "center", "unknown"] | None = Field(None, alias="textAlign", description="Horizontal text alignment: left, right, or center. Defaults to center for flowchart shapes, left for basic shapes."),
    text_align_vertical: Literal["top", "middle", "bottom", "unknown"] | None = Field(None, alias="textAlignVertical", description="Vertical text alignment: top, middle, or bottom. Defaults to middle for flowchart shapes, top for basic shapes."),
    height: float | None = Field(None, description="Height of the shape in pixels."),
    rotation: float | None = Field(None, description="Rotation angle in degrees relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation."),
    width: float | None = Field(None, description="Width of the shape in pixels."),
) -> dict[str, Any] | ToolResult:
    """Adds a shape item to a board with customizable geometry, styling, and text formatting. Requires boards:write scope."""

    # Construct request model with validation
    try:
        _request = _models.CreateShapeItemRequest(
            path=_models.CreateShapeItemRequestPath(board_id=board_id),
            body=_models.CreateShapeItemRequestBody(data=_models.CreateShapeItemRequestBodyData(content=content, shape=shape) if any(v is not None for v in [content, shape]) else None,
                style=_models.CreateShapeItemRequestBodyStyle(border_color=border_color, border_opacity=border_opacity, border_style=border_style, border_width=border_width, color=color, fill_color=fill_color, fill_opacity=fill_opacity, font_family=font_family, font_size=font_size, text_align=text_align, text_align_vertical=text_align_vertical) if any(v is not None for v in [border_color, border_opacity, border_style, border_width, color, fill_color, fill_opacity, font_family, font_size, text_align, text_align_vertical]) else None,
                geometry=_models.CreateShapeItemRequestBodyGeometry(height=height, rotation=rotation, width=width) if any(v is not None for v in [height, rotation, width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_shape_to_board: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/shapes", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/shapes"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_shape_to_board")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_shape_to_board", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_shape_to_board",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: shapes
@mcp.tool()
async def get_shape_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the shape item you want to retrieve."),
    item_id: str = Field(..., description="The unique identifier of the shape item you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific shape item on a board, including its properties and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetShapeItemRequest(
            path=_models.GetShapeItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_shape_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/shapes/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/shapes/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_shape_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_shape_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_shape_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: shapes
@mcp.tool()
async def update_shape_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the shape item to update."),
    item_id: str = Field(..., description="The unique identifier of the shape item to update."),
    content: str | None = Field(None, description="The text content to display on the shape. Note: Changing the shape type to flow_chart_or or flow_chart_summing_junction will clear any existing content."),
    shape: str | None = Field(None, description="The geometric shape type to render. Choose from basic shapes (rectangle, circle, triangle, etc.), flowchart shapes (flow_chart_process, flow_chart_decision, etc.), or specialized shapes (cloud, star, arrows). Defaults to rectangle."),
    border_color: str | None = Field(None, alias="borderColor", description="The hex color code for the shape's border outline."),
    border_opacity: str | None = Field(None, alias="borderOpacity", description="The transparency level of the border, from 0.0 (fully transparent) to 1.0 (fully opaque)."),
    border_style: Literal["normal", "dotted", "dashed"] | None = Field(None, alias="borderStyle", description="The visual style of the border: solid (normal), dotted, or dashed."),
    border_width: str | None = Field(None, alias="borderWidth", description="The thickness of the border in display pixels, ranging from 1 to 24."),
    color: str | None = Field(None, description="The hex color code for the text displayed within the shape."),
    fill_color: str | None = Field(None, alias="fillColor", description="The hex color code for the shape's fill background. Supports predefined palette colors or custom hex values."),
    fill_opacity: str | None = Field(None, alias="fillOpacity", description="The transparency level of the fill color, from 0.0 (fully transparent) to 1.0 (fully opaque)."),
    font_family: Literal["arial", "abril_fatface", "bangers", "eb_garamond", "georgia", "graduate", "gravitas_one", "fredoka_one", "nixie_one", "open_sans", "permanent_marker", "pt_sans", "pt_sans_narrow", "pt_serif", "rammetto_one", "roboto", "roboto_condensed", "roboto_slab", "caveat", "times_new_roman", "titan_one", "lemon_tuesday", "roboto_mono", "noto_sans", "plex_sans", "plex_serif", "plex_mono", "spoof", "tiempos_text", "formular"] | None = Field(None, alias="fontFamily", description="The typeface for text rendering. Choose from a curated set including sans-serif (Arial, Open Sans, Roboto), serif (Georgia, Times New Roman), and decorative fonts."),
    font_size: str | None = Field(None, alias="fontSize", description="The size of the text in display pixels, ranging from 10 to 288."),
    text_align: Literal["left", "right", "center"] | None = Field(None, alias="textAlign", description="The horizontal alignment of text within the shape: left, right, or center."),
    text_align_vertical: Literal["top", "middle", "bottom"] | None = Field(None, alias="textAlignVertical", description="The vertical alignment of text within the shape: top, middle, or bottom."),
    height: float | None = Field(None, description="The height of the shape in pixels."),
    rotation: float | None = Field(None, description="The rotation angle in degrees. Use positive values for clockwise rotation and negative values for counterclockwise rotation."),
    width: float | None = Field(None, description="The width of the shape in pixels."),
) -> dict[str, Any] | ToolResult:
    """Modify a shape item's geometry, styling, and text content on a board. Updates only the properties you specify; omitted properties remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.UpdateShapeItemRequest(
            path=_models.UpdateShapeItemRequestPath(board_id=board_id, item_id=item_id),
            body=_models.UpdateShapeItemRequestBody(data=_models.UpdateShapeItemRequestBodyData(content=content, shape=shape) if any(v is not None for v in [content, shape]) else None,
                style=_models.UpdateShapeItemRequestBodyStyle(border_color=border_color, border_opacity=border_opacity, border_style=border_style, border_width=border_width, color=color, fill_color=fill_color, fill_opacity=fill_opacity, font_family=font_family, font_size=font_size, text_align=text_align, text_align_vertical=text_align_vertical) if any(v is not None for v in [border_color, border_opacity, border_style, border_width, color, fill_color, fill_opacity, font_family, font_size, text_align, text_align_vertical]) else None,
                geometry=_models.UpdateShapeItemRequestBodyGeometry(height=height, rotation=rotation, width=width) if any(v is not None for v in [height, rotation, width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_shape_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/shapes/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/shapes/{item_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_shape_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_shape_item", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_shape_item",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: shapes
@mcp.tool()
async def delete_shape_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the shape item to delete."),
    item_id: str = Field(..., description="The unique identifier of the shape item to delete from the board."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a shape item from a board. This action cannot be undone and requires write access to the board."""

    # Construct request model with validation
    try:
        _request = _models.DeleteShapeItemRequest(
            path=_models.DeleteShapeItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_shape_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/shapes/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/shapes/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_shape_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_shape_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_shape_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: sticky_notes
@mcp.tool()
async def add_sticky_note(
    board_id: str = Field(..., description="The unique identifier of the board where the sticky note will be created."),
    content: str | None = Field(None, description="The text content displayed in the sticky note (e.g., 'Hello')."),
    shape: Literal["square", "rectangle"] | None = Field(None, description="The geometric shape of the sticky note: either square or rectangle. Defaults to square."),
    fill_color: Literal["gray", "light_yellow", "yellow", "orange", "light_green", "green", "dark_green", "cyan", "light_pink", "pink", "violet", "red", "light_blue", "blue", "dark_blue", "black"] | None = Field(None, alias="fillColor", description="The fill color of the sticky note. Choose from: gray, light_yellow, yellow, orange, light_green, green, dark_green, cyan, light_pink, pink, violet, red, light_blue, blue, dark_blue, or black. Defaults to light_yellow."),
    text_align: Literal["left", "right", "center"] | None = Field(None, alias="textAlign", description="Horizontal text alignment within the sticky note: left, right, or center. Defaults to center."),
    text_align_vertical: Literal["top", "middle", "bottom"] | None = Field(None, alias="textAlignVertical", description="Vertical text alignment within the sticky note: top, middle, or bottom. Defaults to top."),
    height: float | None = Field(None, description="The height of the sticky note in pixels."),
    width: float | None = Field(None, description="The width of the sticky note in pixels."),
) -> dict[str, Any] | ToolResult:
    """Adds a sticky note item to a board with customizable text content, shape, colors, and alignment. Requires boards:write scope."""

    # Construct request model with validation
    try:
        _request = _models.CreateStickyNoteItemRequest(
            path=_models.CreateStickyNoteItemRequestPath(board_id=board_id),
            body=_models.CreateStickyNoteItemRequestBody(data=_models.CreateStickyNoteItemRequestBodyData(content=content, shape=shape) if any(v is not None for v in [content, shape]) else None,
                style=_models.CreateStickyNoteItemRequestBodyStyle(fill_color=fill_color, text_align=text_align, text_align_vertical=text_align_vertical) if any(v is not None for v in [fill_color, text_align, text_align_vertical]) else None,
                geometry=_models.CreateStickyNoteItemRequestBodyGeometry(height=height, width=width) if any(v is not None for v in [height, width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_sticky_note: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/sticky_notes", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/sticky_notes"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_sticky_note")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_sticky_note", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_sticky_note",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: sticky_notes
@mcp.tool()
async def get_sticky_note_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the sticky note item you want to retrieve."),
    item_id: str = Field(..., description="The unique identifier of the sticky note item you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific sticky note item on a board. Use this to fetch the content, styling, and metadata of an individual sticky note."""

    # Construct request model with validation
    try:
        _request = _models.GetStickyNoteItemRequest(
            path=_models.GetStickyNoteItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_sticky_note_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/sticky_notes/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/sticky_notes/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_sticky_note_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_sticky_note_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_sticky_note_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: sticky_notes
@mcp.tool()
async def update_sticky_note(
    board_id: str = Field(..., description="The unique identifier of the board containing the sticky note to update."),
    item_id: str = Field(..., description="The unique identifier of the sticky note item to update."),
    content: str | None = Field(None, description="The text content to display in the sticky note."),
    shape: Literal["square", "rectangle"] | None = Field(None, description="The geometric shape of the sticky note: square (default) or rectangle, which affects the aspect ratio of the item's dimensions."),
    fill_color: Literal["gray", "light_yellow", "yellow", "orange", "light_green", "green", "dark_green", "cyan", "light_pink", "pink", "violet", "red", "light_blue", "blue", "dark_blue", "black"] | None = Field(None, alias="fillColor", description="The background color of the sticky note. Choose from 15 preset colors including gray, yellows, greens, blues, pinks, and more."),
    text_align: Literal["left", "right", "center"] | None = Field(None, alias="textAlign", description="The horizontal alignment of text within the sticky note: left, center, or right."),
    text_align_vertical: Literal["top", "middle", "bottom"] | None = Field(None, alias="textAlignVertical", description="The vertical alignment of text within the sticky note: top, middle, or bottom."),
    height: float | None = Field(None, description="The height of the sticky note in pixels."),
    width: float | None = Field(None, description="The width of the sticky note in pixels."),
) -> dict[str, Any] | ToolResult:
    """Modify the content, appearance, and layout of a sticky note item on a board. Update text, colors, alignment, shape, and dimensions as needed."""

    # Construct request model with validation
    try:
        _request = _models.UpdateStickyNoteItemRequest(
            path=_models.UpdateStickyNoteItemRequestPath(board_id=board_id, item_id=item_id),
            body=_models.UpdateStickyNoteItemRequestBody(data=_models.UpdateStickyNoteItemRequestBodyData(content=content, shape=shape) if any(v is not None for v in [content, shape]) else None,
                style=_models.UpdateStickyNoteItemRequestBodyStyle(fill_color=fill_color, text_align=text_align, text_align_vertical=text_align_vertical) if any(v is not None for v in [fill_color, text_align, text_align_vertical]) else None,
                geometry=_models.UpdateStickyNoteItemRequestBodyGeometry(height=height, width=width) if any(v is not None for v in [height, width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_sticky_note: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/sticky_notes/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/sticky_notes/{item_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_sticky_note")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_sticky_note", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_sticky_note",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: sticky_notes
@mcp.tool()
async def delete_sticky_note_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the sticky note to delete."),
    item_id: str = Field(..., description="The unique identifier of the sticky note item to delete."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a sticky note item from a board. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteStickyNoteItemRequest(
            path=_models.DeleteStickyNoteItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_sticky_note_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/sticky_notes/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/sticky_notes/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_sticky_note_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_sticky_note_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_sticky_note_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: texts
@mcp.tool()
async def add_text_to_board(
    board_id: str = Field(..., description="The unique identifier of the board where the text item will be created."),
    content: str = Field(..., description="The text content to display in the item."),
    color: str | None = Field(None, description="Hex color code for the text itself. Defaults to black (#1a1a1a)."),
    fill_color: str | None = Field(None, alias="fillColor", description="Hex color code for the background fill of the text item. Defaults to white (#ffffff)."),
    fill_opacity: str | None = Field(None, alias="fillOpacity", description="Opacity of the background color, ranging from 0.0 (fully transparent) to 1.0 (fully opaque). Defaults to 1.0 if a fill color is specified, otherwise 0.0."),
    font_family: Literal["arial", "abril_fatface", "bangers", "eb_garamond", "georgia", "graduate", "gravitas_one", "fredoka_one", "nixie_one", "open_sans", "permanent_marker", "pt_sans", "pt_sans_narrow", "pt_serif", "rammetto_one", "roboto", "roboto_condensed", "roboto_slab", "caveat", "times_new_roman", "titan_one", "lemon_tuesday", "roboto_mono", "noto_sans", "plex_sans", "plex_serif", "plex_mono", "spoof", "tiempos_text", "formular"] | None = Field(None, alias="fontFamily", description="Font family for the text. Choose from a curated set of web-safe and decorative fonts. Defaults to Arial."),
    font_size: str | None = Field(None, alias="fontSize", description="Font size in display pixels. Must be at least 1 pixel. Defaults to 14 pixels."),
    text_align: Literal["left", "right", "center"] | None = Field(None, alias="textAlign", description="Horizontal text alignment within the item: left, right, or center. Defaults to center."),
    rotation: float | None = Field(None, description="Rotation angle in degrees. Positive values rotate clockwise, negative values rotate counterclockwise."),
    width: float | None = Field(None, description="Width of the item in pixels. Must be at least 1.7 times the font size (e.g., minimum 24 pixels for 14pt font)."),
) -> dict[str, Any] | ToolResult:
    """Adds a text item to a board with customizable styling, positioning, and formatting options. Requires boards:write scope."""

    # Construct request model with validation
    try:
        _request = _models.CreateTextItemRequest(
            path=_models.CreateTextItemRequestPath(board_id=board_id),
            body=_models.CreateTextItemRequestBody(data=_models.CreateTextItemRequestBodyData(content=content),
                style=_models.CreateTextItemRequestBodyStyle(color=color, fill_color=fill_color, fill_opacity=fill_opacity, font_family=font_family, font_size=font_size, text_align=text_align) if any(v is not None for v in [color, fill_color, fill_opacity, font_family, font_size, text_align]) else None,
                geometry=_models.CreateTextItemRequestBodyGeometry(rotation=rotation, width=width) if any(v is not None for v in [rotation, width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_text_to_board: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/texts", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/texts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_text_to_board")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_text_to_board", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_text_to_board",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: texts
@mcp.tool()
async def get_text_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the text item you want to retrieve."),
    item_id: str = Field(..., description="The unique identifier of the text item you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific text item from a board by its ID. Returns the text item's properties and content."""

    # Construct request model with validation
    try:
        _request = _models.GetTextItemRequest(
            path=_models.GetTextItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_text_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/texts/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/texts/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_text_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_text_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_text_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: texts
@mcp.tool()
async def update_text_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the text item to update."),
    item_id: str = Field(..., description="The unique identifier of the text item to update."),
    content: str = Field(..., description="The text content to display in the item (e.g., 'Hello')."),
    color: str | None = Field(None, description="Hex color code for the text itself (e.g., '#1a1a1a' for dark text)."),
    fill_color: str | None = Field(None, alias="fillColor", description="Hex color code for the background fill of the text item (e.g., '#e6e6e6' for light gray)."),
    fill_opacity: str | None = Field(None, alias="fillOpacity", description="Transparency level of the background color, ranging from 0.0 (completely transparent) to 1.0 (completely opaque)."),
    font_family: Literal["arial", "abril_fatface", "bangers", "eb_garamond", "georgia", "graduate", "gravitas_one", "fredoka_one", "nixie_one", "open_sans", "permanent_marker", "pt_sans", "pt_sans_narrow", "pt_serif", "rammetto_one", "roboto", "roboto_condensed", "roboto_slab", "caveat", "times_new_roman", "titan_one", "lemon_tuesday", "roboto_mono", "noto_sans", "plex_sans", "plex_serif", "plex_mono", "spoof", "tiempos_text", "formular"] | None = Field(None, alias="fontFamily", description="Font family for the text. Choose from: arial, abril_fatface, bangers, eb_garamond, georgia, graduate, gravitas_one, fredoka_one, nixie_one, open_sans, permanent_marker, pt_sans, pt_sans_narrow, pt_serif, rammetto_one, roboto, roboto_condensed, roboto_slab, caveat, times_new_roman, titan_one, lemon_tuesday, roboto_mono, noto_sans, plex_sans, plex_serif, plex_mono, spoof, tiempos_text, or formular."),
    font_size: str | None = Field(None, alias="fontSize", description="Font size in display pixels. Must be at least 1 pixel."),
    text_align: Literal["left", "right", "center"] | None = Field(None, alias="textAlign", description="Horizontal alignment of the text content: left, right, or center."),
    rotation: float | None = Field(None, description="Rotation angle in degrees. Use positive values for clockwise rotation and negative values for counterclockwise rotation."),
    width: float | None = Field(None, description="Width of the item in pixels. Minimum width is 1.7 times the font size (e.g., font size 14 requires minimum width of 24)."),
) -> dict[str, Any] | ToolResult:
    """Modify the content, styling, and layout of a text item on a board. Update text content, colors, fonts, alignment, rotation, and dimensions as needed."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTextItemRequest(
            path=_models.UpdateTextItemRequestPath(board_id=board_id, item_id=item_id),
            body=_models.UpdateTextItemRequestBody(data=_models.UpdateTextItemRequestBodyData(content=content),
                style=_models.UpdateTextItemRequestBodyStyle(color=color, fill_color=fill_color, fill_opacity=fill_opacity, font_family=font_family, font_size=font_size, text_align=text_align) if any(v is not None for v in [color, fill_color, fill_opacity, font_family, font_size, text_align]) else None,
                geometry=_models.UpdateTextItemRequestBodyGeometry(rotation=rotation, width=width) if any(v is not None for v in [rotation, width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_text_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/texts/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/texts/{item_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_text_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_text_item", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_text_item",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: texts
@mcp.tool()
async def delete_text_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the text item to delete."),
    item_id: str = Field(..., description="The unique identifier of the text item to delete from the board."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a text item from a board. Requires boards:write scope and is subject to Level 3 rate limiting."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTextItemRequest(
            path=_models.DeleteTextItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_text_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/texts/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/texts/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_text_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_text_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_text_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Bulk operations
@mcp.tool()
async def create_items_bulk(
    board_id: str = Field(..., description="The unique identifier of the board where items will be created."),
    body: list[_models.ItemCreate] = Field(..., description="Array of item objects to create. Must contain between 1 and 20 items. Items can be of different types (cards, shapes, sticky notes, etc.) and are processed together as a single transaction.", min_length=1, max_length=20),
) -> dict[str, Any] | ToolResult:
    """Create multiple items of different types on a board in a single transactional operation. Supports up to 20 items per call (cards, shapes, sticky notes, etc.), and all items are created together or none are created if any item fails."""

    # Construct request model with validation
    try:
        _request = _models.CreateItemsRequest(
            path=_models.CreateItemsRequestPath(board_id=board_id),
            body=_models.CreateItemsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_items_bulk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/items/bulk", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/items/bulk"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_items_bulk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_items_bulk", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_items_bulk",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: frames
@mcp.tool()
async def add_frame_to_board(
    board_id: str = Field(..., description="The unique identifier of the board where the frame will be created."),
    format_: Literal["custom"] | None = Field(None, alias="format", description="The frame format type. Currently, only custom frames are supported."),
    title: str | None = Field(None, description="The title displayed at the top of the frame."),
    type_: Literal["freeform"] | None = Field(None, alias="type", description="The frame layout type. Currently, only freeform frames are supported, allowing flexible content arrangement."),
    show_content: bool | None = Field(None, alias="showContent", description="Whether to show or hide the content inside the frame. This feature is available only on Enterprise plans."),
    fill_color: str | None = Field(None, alias="fillColor", description="The background fill color for the frame, specified as a hexadecimal color code. Supports a predefined palette of colors or transparent (default)."),
    height: float | None = Field(None, description="The height of the frame in pixels."),
    width: float | None = Field(None, description="The width of the frame in pixels."),
) -> dict[str, Any] | ToolResult:
    """Adds a new frame to a board. Frames serve as containers for organizing and grouping content on a board, with customizable appearance and dimensions."""

    # Construct request model with validation
    try:
        _request = _models.CreateFrameItemRequest(
            path=_models.CreateFrameItemRequestPath(board_id=board_id),
            body=_models.CreateFrameItemRequestBody(data=_models.CreateFrameItemRequestBodyData(format_=format_, title=title, type_=type_, show_content=show_content) if any(v is not None for v in [format_, title, type_, show_content]) else None,
                style=_models.CreateFrameItemRequestBodyStyle(fill_color=fill_color) if any(v is not None for v in [fill_color]) else None,
                geometry=_models.CreateFrameItemRequestBodyGeometry(height=height, width=width) if any(v is not None for v in [height, width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_frame_to_board: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/frames", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/frames"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_frame_to_board")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_frame_to_board", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_frame_to_board",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: frames
@mcp.tool()
async def get_frame(
    board_id: str = Field(..., description="The unique identifier of the board containing the frame you want to retrieve."),
    item_id: str = Field(..., description="The unique identifier of the frame you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific frame on a board, including its properties and content."""

    # Construct request model with validation
    try:
        _request = _models.GetFrameItemRequest(
            path=_models.GetFrameItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_frame: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/frames/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/frames/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_frame")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_frame", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_frame",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: frames
@mcp.tool()
async def update_frame(
    board_id: str = Field(..., description="The unique identifier of the board containing the frame to update."),
    item_id: str = Field(..., description="The unique identifier of the frame to update."),
    format_: Literal["custom"] | None = Field(None, alias="format", description="The frame format type. Currently, only custom frames are supported."),
    title: str | None = Field(None, description="The title displayed at the top of the frame."),
    type_: Literal["freeform"] | None = Field(None, alias="type", description="The frame layout type. Currently, only freeform frames are supported."),
    show_content: bool | None = Field(None, alias="showContent", description="Whether to show or hide the content inside the frame. This feature is available on Enterprise plans only."),
    fill_color: str | None = Field(None, alias="fillColor", description="The fill color for the frame, specified as a hexadecimal color code. Supported colors include neutral grays, greens, teals, blues, purples, yellows, oranges, reds, and pinks."),
    height: float | None = Field(None, description="The height of the frame in pixels."),
    width: float | None = Field(None, description="The width of the frame in pixels."),
) -> dict[str, Any] | ToolResult:
    """Update a frame's properties on a board, including its title, appearance, dimensions, and content visibility. Requires boards:write scope."""

    # Construct request model with validation
    try:
        _request = _models.UpdateFrameItemRequest(
            path=_models.UpdateFrameItemRequestPath(board_id=board_id, item_id=item_id),
            body=_models.UpdateFrameItemRequestBody(data=_models.UpdateFrameItemRequestBodyData(format_=format_, title=title, type_=type_, show_content=show_content) if any(v is not None for v in [format_, title, type_, show_content]) else None,
                style=_models.UpdateFrameItemRequestBodyStyle(fill_color=fill_color) if any(v is not None for v in [fill_color]) else None,
                geometry=_models.UpdateFrameItemRequestBodyGeometry(height=height, width=width) if any(v is not None for v in [height, width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_frame: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/frames/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/frames/{item_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_frame")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_frame", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_frame",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: frames
@mcp.tool()
async def delete_frame(
    board_id: str = Field(..., description="The unique identifier of the board containing the frame to delete."),
    item_id: str = Field(..., description="The unique identifier of the frame to delete from the board."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a frame from a board. The frame and all its contents will be deleted and cannot be recovered."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFrameItemRequest(
            path=_models.DeleteFrameItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_frame: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/frames/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/frames/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_frame")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_frame", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_frame",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: items
@mcp.tool()
async def list_items_in_frame(
    board_id_platform_containers: str = Field(..., alias="board_id_PlatformContainers", description="The unique identifier of the board containing the frame."),
    parent_item_id: str = Field(..., description="The unique identifier of the frame (parent item) whose child items you want to retrieve."),
    limit: str | None = Field(None, description="Maximum number of items to return per request, between 10 and 50. If the total exceeds this limit, use the cursor from the response to fetch the next batch."),
    type_: str | None = Field(None, alias="type", description="Filter results to a specific item type (e.g., cards, shapes, sticky notes, images, text, embeds, documents, frames, or app cards). Omit to retrieve all item types."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all child items contained within a specific frame on a board. Results are returned using cursor-based pagination to handle large collections efficiently."""

    # Construct request model with validation
    try:
        _request = _models.GetItemsWithinFrameRequest(
            path=_models.GetItemsWithinFrameRequestPath(board_id_platform_containers=board_id_platform_containers),
            query=_models.GetItemsWithinFrameRequestQuery(parent_item_id=parent_item_id, limit=limit, type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_items_in_frame: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id_PlatformContainers}/items", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id_PlatformContainers}/items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_items_in_frame")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_items_in_frame", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_items_in_frame",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: App metrics (experimental)
@mcp.tool()
async def get_app_metrics(
    app_id: str = Field(..., description="The unique identifier of the app for which to retrieve metrics."),
    start_date: str = Field(..., alias="startDate", description="The start date for the metrics period in UTC format (YYYY-MM-DD). Metrics will be retrieved from this date onwards."),
    end_date: str = Field(..., alias="endDate", description="The end date for the metrics period in UTC format (YYYY-MM-DD). Metrics will be retrieved up to and including this date."),
    period: Literal["DAY", "WEEK", "MONTH"] | None = Field(None, description="The time period to group metrics by. Accepts 'DAY', 'WEEK', or 'MONTH'. Defaults to 'WEEK' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve usage metrics for a specific app over a specified time range, with data grouped by the requested time period (day, week, or month). Requires an app management API token generated from the Developer Hub."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricsRequest(
            path=_models.GetMetricsRequestPath(app_id=app_id),
            query=_models.GetMetricsRequestQuery(start_date=start_date, end_date=end_date, period=period)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_app_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2-experimental/apps/{app_id}/metrics", _request.path.model_dump(by_alias=True)) if _request.path else "/v2-experimental/apps/{app_id}/metrics"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_app_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_app_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_app_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: App metrics (experimental)
@mcp.tool()
async def get_app_metrics_total(app_id: str = Field(..., description="The unique identifier of the app for which to retrieve total metrics.")) -> dict[str, Any] | ToolResult:
    """Retrieve cumulative usage metrics for a specific app since its creation. Returns total metrics data for the app identified by the provided app ID."""

    # Construct request model with validation
    try:
        _request = _models.GetMetricsTotalRequest(
            path=_models.GetMetricsTotalRequestPath(app_id=app_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_app_metrics_total: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2-experimental/apps/{app_id}/metrics-total", _request.path.model_dump(by_alias=True)) if _request.path else "/v2-experimental/apps/{app_id}/metrics-total"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_app_metrics_total")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_app_metrics_total", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_app_metrics_total",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Mind map nodes (experimental)
@mcp.tool()
async def get_mindmap_node(
    board_id: str = Field(..., description="The unique identifier of the board containing the mind map node you want to retrieve."),
    item_id: str = Field(..., description="The unique identifier of the specific mind map node to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific mind map node from a board. Returns detailed information about the node including its content, position, and relationships within the mind map structure."""

    # Construct request model with validation
    try:
        _request = _models.GetMindmapNodeExperimentalRequest(
            path=_models.GetMindmapNodeExperimentalRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_mindmap_node: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2-experimental/boards/{board_id}/mindmap_nodes/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2-experimental/boards/{board_id}/mindmap_nodes/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_mindmap_node")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_mindmap_node", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_mindmap_node",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Mind map nodes (experimental)
@mcp.tool()
async def delete_mindmap_node(
    board_id: str = Field(..., description="The unique identifier of the board containing the mind map node to delete."),
    item_id: str = Field(..., description="The unique identifier of the mind map node to delete. Deleting a node also removes all of its child nodes."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a mind map node and all of its child nodes from a board. This operation requires write access to the board."""

    # Construct request model with validation
    try:
        _request = _models.DeleteMindmapNodeExperimentalRequest(
            path=_models.DeleteMindmapNodeExperimentalRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_mindmap_node: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2-experimental/boards/{board_id}/mindmap_nodes/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2-experimental/boards/{board_id}/mindmap_nodes/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_mindmap_node")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_mindmap_node", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_mindmap_node",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Mind map nodes (experimental)
@mcp.tool()
async def list_mindmap_nodes(
    board_id: str = Field(..., description="The unique identifier of the board containing the mind map nodes you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of mind map nodes to return per request. Use this with the cursor parameter to paginate through large result sets."),
) -> dict[str, Any] | ToolResult:
    """Retrieves mind map nodes for a specific board using cursor-based pagination. Use the cursor from each response to fetch subsequent pages of results."""

    # Construct request model with validation
    try:
        _request = _models.GetMindmapNodesExperimentalRequest(
            path=_models.GetMindmapNodesExperimentalRequestPath(board_id=board_id),
            query=_models.GetMindmapNodesExperimentalRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_mindmap_nodes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2-experimental/boards/{board_id}/mindmap_nodes", _request.path.model_dump(by_alias=True)) if _request.path else "/v2-experimental/boards/{board_id}/mindmap_nodes"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_mindmap_nodes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_mindmap_nodes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_mindmap_nodes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Mind map nodes (experimental)
@mcp.tool()
async def create_mindmap_node(
    board_id: str = Field(..., description="The unique identifier of the board where the mind map node will be created."),
    type_: str = Field(..., alias="type", description="The type of mind map node. Currently only 'text' is supported."),
    content: str | None = Field(None, description="The text content displayed in the mind map node."),
    width: float | None = Field(None, description="The width of the node in pixels."),
) -> dict[str, Any] | ToolResult:
    """Create a new mind map node on a board. Nodes can be root nodes (starting points) or child nodes nested under existing nodes. Node positioning uses explicit x, y coordinates; if not provided, nodes default to the board center (0, 0)."""

    # Construct request model with validation
    try:
        _request = _models.CreateMindmapNodesExperimentalRequest(
            path=_models.CreateMindmapNodesExperimentalRequestPath(board_id=board_id),
            body=_models.CreateMindmapNodesExperimentalRequestBody(data=_models.CreateMindmapNodesExperimentalRequestBodyData(
                    node_view=_models.CreateMindmapNodesExperimentalRequestBodyDataNodeView(
                        data=_models.CreateMindmapNodesExperimentalRequestBodyDataNodeViewData(type_=type_, content=content)
                    )
                ),
                geometry=_models.CreateMindmapNodesExperimentalRequestBodyGeometry(width=width) if any(v is not None for v in [width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_mindmap_node: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2-experimental/boards/{board_id}/mindmap_nodes", _request.path.model_dump(by_alias=True)) if _request.path else "/v2-experimental/boards/{board_id}/mindmap_nodes"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_mindmap_node")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_mindmap_node", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_mindmap_node",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flowchart shapes (experimental)
@mcp.tool()
async def list_board_items_experimental(
    board_id: str = Field(..., description="The unique identifier of the board from which to retrieve items."),
    limit: str | None = Field(None, description="The maximum number of items to return per request, between 10 and 50. Defaults to 10 items. Use the cursor from the response to fetch subsequent pages."),
    type_: Literal["shape"] | None = Field(None, alias="type", description="Filter results to return only items of a specific type. Currently supports 'shape' type items."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of items on a specific board. Supports filtering by item type and uses cursor-based pagination to handle large result sets efficiently."""

    # Construct request model with validation
    try:
        _request = _models.GetItemsExperimentalRequest(
            path=_models.GetItemsExperimentalRequestPath(board_id=board_id),
            query=_models.GetItemsExperimentalRequestQuery(limit=limit, type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_board_items_experimental: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2-experimental/boards/{board_id}/items", _request.path.model_dump(by_alias=True)) if _request.path else "/v2-experimental/boards/{board_id}/items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_board_items_experimental")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_board_items_experimental", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_board_items_experimental",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flowchart shapes (experimental)
@mcp.tool()
async def get_board_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the item you want to retrieve."),
    item_id: str = Field(..., description="The unique identifier of the specific item you want to retrieve from the board."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific item on a board. Use this to fetch properties and metadata for an individual item by its ID."""

    # Construct request model with validation
    try:
        _request = _models.GetSpecificItemExperimentalRequest(
            path=_models.GetSpecificItemExperimentalRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_board_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2-experimental/boards/{board_id}/items/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2-experimental/boards/{board_id}/items/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_board_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_board_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_board_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: items
@mcp.tool()
async def delete_item_beta(
    board_id: str = Field(..., description="The unique identifier of the board containing the item to delete."),
    item_id: str = Field(..., description="The unique identifier of the item to delete from the board."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes an item from a board. This action cannot be undone and requires write access to the board."""

    # Construct request model with validation
    try:
        _request = _models.DeleteItemExperimentalRequest(
            path=_models.DeleteItemExperimentalRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_item_beta: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2-experimental/boards/{board_id}/items/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2-experimental/boards/{board_id}/items/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_item_beta")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_item_beta", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_item_beta",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flowchart shapes (experimental)
@mcp.tool()
async def add_shape_to_board_flowchart(
    board_id: str = Field(..., description="The unique identifier of the board where the shape will be created."),
    content: str | None = Field(None, description="Optional text to display on the shape. Not supported for OR gates and summing junction flowchart shapes."),
    shape: str | None = Field(None, description="The geometric shape type to render. Choose from basic shapes (rectangle, circle, triangle, etc.), flowchart shapes (decision, process, terminator, etc.), or arrows. Defaults to rectangle."),
    border_color: str | None = Field(None, alias="borderColor", description="Hex color code for the shape's border. Defaults to dark gray (#1a1a1a)."),
    border_opacity: str | None = Field(None, alias="borderOpacity", description="Transparency level of the border, from 0 (fully transparent) to 1 (fully opaque). Defaults to 1."),
    border_style: Literal["normal", "dotted", "dashed"] | None = Field(None, alias="borderStyle", description="Visual style of the border: solid (normal), dotted, or dashed. Defaults to normal."),
    border_width: str | None = Field(None, alias="borderWidth", description="Thickness of the border in display pixels, ranging from 1 to 24. Defaults to 2."),
    color: str | None = Field(None, description="Hex color code for the text inside the shape. Defaults to dark gray (#1a1a1a)."),
    fill_color: str | None = Field(None, alias="fillColor", description="Hex color code for the shape's fill. Supports predefined colors like #8fd14f, #f5d128, #ff9d48, and others. Defaults to white (#ffffff)."),
    fill_opacity: str | None = Field(None, alias="fillOpacity", description="Transparency level of the fill color, from 0 (fully transparent) to 1 (fully opaque). Flowchart shapes default to 1; basic shapes default to 1 if fillColor is set, otherwise 0."),
    font_family: Literal["arial", "abril_fatface", "bangers", "eb_garamond", "georgia", "graduate", "gravitas_one", "fredoka_one", "nixie_one", "open_sans", "permanent_marker", "pt_sans", "pt_sans_narrow", "pt_serif", "rammetto_one", "roboto", "roboto_condensed", "roboto_slab", "caveat", "times_new_roman", "titan_one", "lemon_tuesday", "roboto_mono", "noto_sans", "plex_sans", "plex_serif", "plex_mono", "spoof", "tiempos_text", "formular"] | None = Field(None, alias="fontFamily", description="Font family for the shape's text. Choose from standard fonts (Arial, Georgia, Times New Roman) or decorative options (Bangers, Permanent Marker, etc.). Defaults to Arial."),
    font_size: str | None = Field(None, alias="fontSize", description="Font size for the text in display pixels, ranging from 10 to 288. Defaults to 14."),
    text_align: Literal["left", "right", "center", "unknown"] | None = Field(None, alias="textAlign", description="Horizontal text alignment: left, right, or center. Flowchart shapes default to center; basic shapes default to left."),
    text_align_vertical: Literal["top", "middle", "bottom", "unknown"] | None = Field(None, alias="textAlignVertical", description="Vertical text alignment: top, middle, or bottom. Flowchart shapes default to middle; basic shapes default to top."),
    height: float | None = Field(None, description="Height of the shape in pixels."),
    rotation: float | None = Field(None, description="Rotation angle in degrees. Use positive values for clockwise rotation and negative values for counterclockwise rotation."),
    width: float | None = Field(None, description="Width of the shape in pixels."),
) -> dict[str, Any] | ToolResult:
    """Adds a flowchart or basic shape item to a board with customizable styling, text, and dimensions. Requires boards:write scope."""

    # Construct request model with validation
    try:
        _request = _models.CreateShapeItemFlowchartRequest(
            path=_models.CreateShapeItemFlowchartRequestPath(board_id=board_id),
            body=_models.CreateShapeItemFlowchartRequestBody(data=_models.CreateShapeItemFlowchartRequestBodyData(content=content, shape=shape) if any(v is not None for v in [content, shape]) else None,
                style=_models.CreateShapeItemFlowchartRequestBodyStyle(border_color=border_color, border_opacity=border_opacity, border_style=border_style, border_width=border_width, color=color, fill_color=fill_color, fill_opacity=fill_opacity, font_family=font_family, font_size=font_size, text_align=text_align, text_align_vertical=text_align_vertical) if any(v is not None for v in [border_color, border_opacity, border_style, border_width, color, fill_color, fill_opacity, font_family, font_size, text_align, text_align_vertical]) else None,
                geometry=_models.CreateShapeItemFlowchartRequestBodyGeometry(height=height, rotation=rotation, width=width) if any(v is not None for v in [height, rotation, width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_shape_to_board_flowchart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2-experimental/boards/{board_id}/shapes", _request.path.model_dump(by_alias=True)) if _request.path else "/v2-experimental/boards/{board_id}/shapes"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_shape_to_board_flowchart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_shape_to_board_flowchart", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_shape_to_board_flowchart",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flowchart shapes (experimental)
@mcp.tool()
async def get_shape_item_experimental(
    board_id: str = Field(..., description="The unique identifier of the board containing the shape item you want to retrieve."),
    item_id: str = Field(..., description="The unique identifier of the shape item you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific shape item on a board, including its properties and positioning data."""

    # Construct request model with validation
    try:
        _request = _models.GetShapeItemFlowchartRequest(
            path=_models.GetShapeItemFlowchartRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_shape_item_experimental: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2-experimental/boards/{board_id}/shapes/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2-experimental/boards/{board_id}/shapes/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_shape_item_experimental")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_shape_item_experimental", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_shape_item_experimental",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flowchart shapes (experimental)
@mcp.tool()
async def update_shape_item_flowchart(
    board_id: str = Field(..., description="The unique identifier of the board containing the shape to update."),
    item_id: str = Field(..., description="The unique identifier of the shape item to update."),
    content: str | None = Field(None, description="The text content to display on the shape. Note that changing the shape type to flow_chart_or or flow_chart_summing_junction will clear any existing content."),
    shape: str | None = Field(None, description="The geometric shape type to render. Choose from basic shapes (rectangle, circle, triangle, etc.), flowchart-specific shapes (flow_chart_decision, flow_chart_process, etc.), or arrow/callout variants. Defaults to rectangle."),
    border_color: str | None = Field(None, alias="borderColor", description="The color of the shape's border, specified as a hex value."),
    border_opacity: str | None = Field(None, alias="borderOpacity", description="The transparency level of the border, from 0.0 (fully transparent) to 1.0 (fully opaque)."),
    border_style: Literal["normal", "dotted", "dashed"] | None = Field(None, alias="borderStyle", description="The visual style of the border: normal (solid), dotted, or dashed."),
    border_width: str | None = Field(None, alias="borderWidth", description="The thickness of the border in display pixels, ranging from 1 to 24."),
    color: str | None = Field(None, description="The color of the text within the shape, specified as a hex value."),
    fill_color: str | None = Field(None, alias="fillColor", description="The fill color of the shape, specified as a hex value. Supports standard palette colors like #8fd14f, #23bfe7, #ff9d48, and others."),
    fill_opacity: str | None = Field(None, alias="fillOpacity", description="The transparency level of the fill color, from 0.0 (fully transparent) to 1.0 (fully opaque)."),
    font_family: Literal["arial", "abril_fatface", "bangers", "eb_garamond", "georgia", "graduate", "gravitas_one", "fredoka_one", "nixie_one", "open_sans", "permanent_marker", "pt_sans", "pt_sans_narrow", "pt_serif", "rammetto_one", "roboto", "roboto_condensed", "roboto_slab", "caveat", "times_new_roman", "titan_one", "lemon_tuesday", "roboto_mono", "noto_sans", "plex_sans", "plex_serif", "plex_mono", "spoof", "tiempos_text", "formular"] | None = Field(None, alias="fontFamily", description="The font family for text within the shape. Choose from standard fonts (Arial, Georgia, Times New Roman) or design-focused options (Abril Fatface, Bangers, Permanent Marker, etc.)."),
    font_size: str | None = Field(None, alias="fontSize", description="The font size for text in the shape, in display pixels, ranging from 10 to 288."),
    text_align: Literal["left", "right", "center"] | None = Field(None, alias="textAlign", description="The horizontal alignment of text within the shape: left, right, or center."),
    text_align_vertical: Literal["top", "middle", "bottom"] | None = Field(None, alias="textAlignVertical", description="The vertical alignment of text within the shape: top, middle, or bottom."),
    height: float | None = Field(None, description="The height of the shape in pixels."),
    rotation: float | None = Field(None, description="The rotation angle of the shape in degrees, relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation."),
    width: float | None = Field(None, description="The width of the shape in pixels."),
) -> dict[str, Any] | ToolResult:
    """Update a flowchart shape item on a board by modifying its geometry, styling, content, and layout properties. Changes are applied immediately to the specified shape."""

    # Construct request model with validation
    try:
        _request = _models.UpdateShapeItemFlowchartRequest(
            path=_models.UpdateShapeItemFlowchartRequestPath(board_id=board_id, item_id=item_id),
            body=_models.UpdateShapeItemFlowchartRequestBody(data=_models.UpdateShapeItemFlowchartRequestBodyData(content=content, shape=shape) if any(v is not None for v in [content, shape]) else None,
                style=_models.UpdateShapeItemFlowchartRequestBodyStyle(border_color=border_color, border_opacity=border_opacity, border_style=border_style, border_width=border_width, color=color, fill_color=fill_color, fill_opacity=fill_opacity, font_family=font_family, font_size=font_size, text_align=text_align, text_align_vertical=text_align_vertical) if any(v is not None for v in [border_color, border_opacity, border_style, border_width, color, fill_color, fill_opacity, font_family, font_size, text_align, text_align_vertical]) else None,
                geometry=_models.UpdateShapeItemFlowchartRequestBodyGeometry(height=height, rotation=rotation, width=width) if any(v is not None for v in [height, rotation, width]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_shape_item_flowchart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2-experimental/boards/{board_id}/shapes/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2-experimental/boards/{board_id}/shapes/{item_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_shape_item_flowchart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_shape_item_flowchart", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_shape_item_flowchart",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Flowchart shapes (experimental)
@mcp.tool()
async def delete_shape_item_experimental(
    board_id: str = Field(..., description="The unique identifier of the board containing the shape item to delete."),
    item_id: str = Field(..., description="The unique identifier of the shape item to delete from the board."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a flowchart shape item from a board. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteShapeItemFlowchartRequest(
            path=_models.DeleteShapeItemFlowchartRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_shape_item_experimental: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2-experimental/boards/{board_id}/shapes/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2-experimental/boards/{board_id}/shapes/{item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_shape_item_experimental")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_shape_item_experimental", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_shape_item_experimental",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def create_document_item_from_file(
    board_id_platform_file_upload: str = Field(..., alias="board_id_PlatformFileUpload", description="The unique identifier of the board where the document item will be created."),
    resource: str = Field(..., description="The file to upload from your device. Maximum file size is 6 MB."),
    title: str | None = Field(None, description="Optional title for the document item. If not provided, the uploaded filename will be used."),
    height: float | None = Field(None, description="Optional height of the document item on the board, specified in pixels."),
    width: float | None = Field(None, description="Optional width of the document item on the board, specified in pixels."),
    rotation: float | None = Field(None, description="Optional rotation angle of the document item in degrees, relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation."),
) -> dict[str, Any] | ToolResult:
    """Uploads a document file from your device and adds it as a document item to a board. The file must not exceed 6 MB in size."""

    # Construct request model with validation
    try:
        _request = _models.CreateDocumentItemUsingFileFromDeviceRequest(
            path=_models.CreateDocumentItemUsingFileFromDeviceRequestPath(board_id_platform_file_upload=board_id_platform_file_upload),
            body=_models.CreateDocumentItemUsingFileFromDeviceRequestBody(resource=resource,
                data=_models.CreateDocumentItemUsingFileFromDeviceRequestBodyData(title=title,
                    geometry=_models.CreateDocumentItemUsingFileFromDeviceRequestBodyDataGeometry(height=height, width=width, rotation=rotation) if any(v is not None for v in [height, width, rotation]) else None) if any(v is not None for v in [title, height, width, rotation]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_document_item_from_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id_PlatformFileUpload}/documents", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id_PlatformFileUpload}/documents"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_document_item_from_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_document_item_from_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_document_item_from_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["resource"],
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def update_document_item_with_file(
    board_id_platform_file_upload: str = Field(..., alias="board_id_PlatformFileUpload", description="The unique identifier of the board containing the document item you want to update."),
    item_id: str = Field(..., description="The unique identifier of the document item you want to replace with a new file."),
    resource: str = Field(..., description="The file to upload from your device. Maximum file size is 6 MB. Provide the file as binary data."),
    title: str | None = Field(None, description="Optional title for the document (e.g., 'foo.png'). If not provided, the existing title is retained."),
    alt_text: str | None = Field(None, alias="altText", description="Optional alt-text description to improve accessibility and help viewers understand the document content."),
    height: float | None = Field(None, description="Optional height of the item in pixels. Specify as a decimal number."),
    width: float | None = Field(None, description="Optional width of the item in pixels. Specify as a decimal number."),
    rotation: float | None = Field(None, description="Optional rotation angle in degrees, relative to the board. Use positive values for clockwise rotation and negative values for counterclockwise rotation."),
) -> dict[str, Any] | ToolResult:
    """Replace a document item on a board with a new file uploaded from your device. The file must not exceed 6 MB in size."""

    # Construct request model with validation
    try:
        _request = _models.UpdateDocumentItemUsingFileFromDeviceRequest(
            path=_models.UpdateDocumentItemUsingFileFromDeviceRequestPath(board_id_platform_file_upload=board_id_platform_file_upload, item_id=item_id),
            body=_models.UpdateDocumentItemUsingFileFromDeviceRequestBody(resource=resource,
                data=_models.UpdateDocumentItemUsingFileFromDeviceRequestBodyData(title=title, alt_text=alt_text,
                    geometry=_models.UpdateDocumentItemUsingFileFromDeviceRequestBodyDataGeometry(height=height, width=width, rotation=rotation) if any(v is not None for v in [height, width, rotation]) else None) if any(v is not None for v in [title, alt_text, height, width, rotation]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_document_item_with_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id_PlatformFileUpload}/documents/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id_PlatformFileUpload}/documents/{item_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_document_item_with_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_document_item_with_file", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_document_item_with_file",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["resource"],
        headers=_http_headers,
    )

    return _response_data

# Tags: images
@mcp.tool()
async def create_image_item_from_local_file(
    board_id_platform_file_upload: str = Field(..., alias="board_id_PlatformFileUpload", description="The unique identifier of the board where the image item will be created."),
    resource: str = Field(..., description="The image file to upload from your device. Maximum file size is 6 MB."),
    title: str | None = Field(None, description="Optional display title for the image item (e.g., 'foo.png'). If not provided, the filename may be used."),
    alt_text: str | None = Field(None, alias="altText", description="Optional alt text describing the image content for accessibility purposes."),
    height: float | None = Field(None, description="Optional height of the image item in pixels. If not specified, the original image dimensions will be used."),
    width: float | None = Field(None, description="Optional width of the image item in pixels. If not specified, the original image dimensions will be used."),
    rotation: float | None = Field(None, description="Optional rotation angle in degrees. Use positive values for clockwise rotation and negative values for counterclockwise rotation."),
) -> dict[str, Any] | ToolResult:
    """Adds an image item to a board by uploading a file from your device. Supports images up to 6 MB with optional sizing, rotation, and accessibility metadata."""

    # Construct request model with validation
    try:
        _request = _models.CreateImageItemUsingLocalFileRequest(
            path=_models.CreateImageItemUsingLocalFileRequestPath(board_id_platform_file_upload=board_id_platform_file_upload),
            body=_models.CreateImageItemUsingLocalFileRequestBody(resource=resource,
                data=_models.CreateImageItemUsingLocalFileRequestBodyData(title=title, alt_text=alt_text,
                    geometry=_models.CreateImageItemUsingLocalFileRequestBodyDataGeometry(height=height, width=width, rotation=rotation) if any(v is not None for v in [height, width, rotation]) else None) if any(v is not None for v in [title, alt_text, height, width, rotation]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_image_item_from_local_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id_PlatformFileUpload}/images", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id_PlatformFileUpload}/images"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_image_item_from_local_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_image_item_from_local_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_image_item_from_local_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["resource"],
        headers=_http_headers,
    )

    return _response_data

# Tags: images
@mcp.tool()
async def update_image_item_from_file(
    board_id_platform_file_upload: str = Field(..., alias="board_id_PlatformFileUpload", description="The unique identifier of the board containing the image item you want to update."),
    item_id: str = Field(..., description="The unique identifier of the image item on the board that you want to replace or modify."),
    resource: str = Field(..., description="The image file to upload from your device. Maximum file size is 6 MB. This replaces the existing image on the item."),
    title: str | None = Field(None, description="Optional display name for the image (e.g., 'foo.png'). If not provided, the existing title is retained."),
    alt_text: str | None = Field(None, alias="altText", description="Optional alt text describing the image content for accessibility purposes. Helps users understand what the image depicts."),
    height: float | None = Field(None, description="Optional height of the image in pixels. Specify as a decimal number to set or adjust the vertical dimension."),
    width: float | None = Field(None, description="Optional width of the image in pixels. Specify as a decimal number to set or adjust the horizontal dimension."),
    rotation: float | None = Field(None, description="Optional rotation angle in degrees. Use positive values to rotate clockwise and negative values to rotate counterclockwise."),
) -> dict[str, Any] | ToolResult:
    """Replace an image on a board with a new file from your device. Supports updating the image file itself along with optional metadata like title, alt text, dimensions, and rotation."""

    # Construct request model with validation
    try:
        _request = _models.UpdateImageItemUsingFileFromDeviceRequest(
            path=_models.UpdateImageItemUsingFileFromDeviceRequestPath(board_id_platform_file_upload=board_id_platform_file_upload, item_id=item_id),
            body=_models.UpdateImageItemUsingFileFromDeviceRequestBody(resource=resource,
                data=_models.UpdateImageItemUsingFileFromDeviceRequestBodyData(title=title, alt_text=alt_text,
                    geometry=_models.UpdateImageItemUsingFileFromDeviceRequestBodyDataGeometry(height=height, width=width, rotation=rotation) if any(v is not None for v in [height, width, rotation]) else None) if any(v is not None for v in [title, alt_text, height, width, rotation]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_image_item_from_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id_PlatformFileUpload}/images/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id_PlatformFileUpload}/images/{item_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_image_item_from_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_image_item_from_file", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_image_item_from_file",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["resource"],
        headers=_http_headers,
    )

    return _response_data

# Tags: groups
@mcp.tool()
async def list_groups_on_board(
    board_id: str = Field(..., description="The unique identifier of the board from which to retrieve groups."),
    limit: str | None = Field(None, description="The maximum number of groups to return per request, between 10 and 50 items (defaults to 10). Use this with the cursor parameter to paginate through results."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all groups and their items from a specific board using cursor-based pagination. Results are returned in batches with a cursor for fetching subsequent pages."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetAllGroupsRequest(
            path=_models.GetAllGroupsRequestPath(board_id=board_id),
            query=_models.GetAllGroupsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_groups_on_board: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/groups"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_groups_on_board")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_groups_on_board", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_groups_on_board",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: groups
@mcp.tool()
async def list_items_in_group(
    board_id: str = Field(..., description="The unique identifier of the board containing the group."),
    group_item_id: str = Field(..., description="The unique identifier of the group whose items you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of items to return per request, between 10 and 50 items (defaults to 10)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all items belonging to a specific group within a board using cursor-based pagination. Results are returned in batches with a cursor for fetching subsequent pages."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetItemsByGroupIdRequest(
            path=_models.GetItemsByGroupIdRequestPath(board_id=board_id),
            query=_models.GetItemsByGroupIdRequestQuery(limit=_limit, group_item_id=group_item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_items_in_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/groups/items", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/groups/items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_items_in_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_items_in_group", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_items_in_group",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: groups
@mcp.tool()
async def get_group_by_id(
    board_id: str = Field(..., description="The unique identifier of the board containing the group. This is a required string ID that identifies which board to query."),
    group_id: str = Field(..., description="The unique identifier of the group to retrieve. This is a required numeric ID that specifies which group's items should be returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific group and its contained items from a board. Requires boards:read scope and is subject to Level 2 rate limiting."""

    # Construct request model with validation
    try:
        _request = _models.GetGroupByIdRequest(
            path=_models.GetGroupByIdRequestPath(board_id=board_id, group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_group_by_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/groups/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/groups/{group_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_group_by_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_group_by_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_group_by_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: groups
@mcp.tool()
async def update_group(
    board_id: str = Field(..., description="The unique identifier of the board containing the group to update."),
    group_id: str = Field(..., description="The unique identifier of the group to replace."),
    id_: str = Field(..., alias="id", description="The unique identifier for the new user group."),
    name: str = Field(..., description="The name of the user group."),
    type_: str = Field(..., alias="type", description="The object type, which must be set to 'user-group'."),
    description: str | None = Field(None, description="Optional description providing additional context about the user group."),
) -> dict[str, Any] | ToolResult:
    """Replaces an existing group on a board with new content. The original group is completely replaced and assigned a new ID."""

    # Construct request model with validation
    try:
        _request = _models.UpdateGroupRequest(
            path=_models.UpdateGroupRequestPath(board_id=board_id, group_id=group_id),
            body=_models.UpdateGroupRequestBody(id_=id_, name=name, description=description, type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/groups/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/groups/{group_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_group", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_group",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: groups
@mcp.tool()
async def remove_items_from_group(
    board_id: str = Field(..., description="The unique identifier of the board containing the group."),
    group_id: str = Field(..., description="The unique identifier of the group to ungroup items from."),
    delete_items: bool | None = Field(None, description="When true, removes the ungrouped items from the board entirely. When false (default), items remain on the board but are no longer grouped."),
) -> dict[str, Any] | ToolResult:
    """Ungroups items from a group on a board, optionally removing them entirely. Requires boards:write scope."""

    # Construct request model with validation
    try:
        _request = _models.UnGroupRequest(
            path=_models.UnGroupRequestPath(board_id=board_id, group_id=group_id),
            query=_models.UnGroupRequestQuery(delete_items=delete_items)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_items_from_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/groups/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/groups/{group_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_items_from_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_items_from_group", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_items_from_group",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: groups
@mcp.tool()
async def delete_group(
    board_id: str = Field(..., description="The unique identifier of the board containing the group to delete."),
    group_id: str = Field(..., description="The unique identifier of the group to delete."),
    delete_items: bool = Field(..., description="Set to true to remove all items in the group along with the group itself. Set to false to preserve items."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a group from a board, including all items contained within it. Note that this operation will delete locked items as well."""

    # Construct request model with validation
    try:
        _request = _models.DeleteGroupRequest(
            path=_models.DeleteGroupRequestPath(board_id=board_id, group_id=group_id),
            query=_models.DeleteGroupRequestQuery(delete_items=delete_items)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/groups/{group_id}?", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/groups/{group_id}?"
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

# Tags: tags
@mcp.tool()
async def list_tags_for_item(
    board_id: str = Field(..., description="The unique identifier of the board containing the item. This ID is required to locate the correct board context."),
    item_id: str = Field(..., description="The unique identifier of the item whose tags you want to retrieve. This ID must correspond to an item that exists on the specified board."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all tags associated with a specific item on a board. Use this to view the complete set of tags currently applied to an item."""

    # Construct request model with validation
    try:
        _request = _models.GetTagsFromItemRequest(
            path=_models.GetTagsFromItemRequestPath(board_id=board_id, item_id=item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tags_for_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/items/{item_id}/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/items/{item_id}/tags"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tags_for_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tags_for_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tags_for_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: tags
@mcp.tool()
async def list_tags_from_board(
    board_id: str = Field(..., description="The unique identifier of the board from which to retrieve tags."),
    limit: str | None = Field(None, description="The maximum number of tags to return in a single request. Must be between 1 and 50 items. Defaults to 20 if not specified."),
    offset: str | None = Field(None, description="The number of tags to skip before returning results, used for pagination. Defaults to 0 (starting from the first tag)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all tags associated with a specified board. Supports pagination to control the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetTagsFromBoardRequest(
            path=_models.GetTagsFromBoardRequestPath(board_id=board_id),
            query=_models.GetTagsFromBoardRequestQuery(limit=limit, offset=offset)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tags_from_board: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/tags"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tags_from_board")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tags_from_board", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tags_from_board",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: tags
@mcp.tool()
async def create_tag(
    board_id: str = Field(..., description="The unique identifier of the board where the tag will be created."),
    title: str = Field(..., description="The display text for the tag, case-sensitive and must be unique within the board. Can be up to 120 characters long.", min_length=0, max_length=120),
    fill_color: Literal["red", "light_green", "cyan", "yellow", "magenta", "green", "blue", "gray", "violet", "dark_green", "dark_blue", "black"] | None = Field(None, alias="fillColor", description="The visual color for the tag. Choose from a predefined palette of 12 colors including red, green, blue, cyan, yellow, magenta, violet, gray, black, and their variants. Defaults to red if not specified."),
) -> dict[str, Any] | ToolResult:
    """Creates a new tag on a board to organize and categorize board items. Tag titles must be unique within the board and can be assigned a color for visual distinction."""

    # Construct request model with validation
    try:
        _request = _models.CreateTagRequest(
            path=_models.CreateTagRequestPath(board_id=board_id),
            body=_models.CreateTagRequestBody(fill_color=fill_color, title=title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/tags"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_tag", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_tag",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: tags
@mcp.tool()
async def get_tag(
    board_id: str = Field(..., description="The unique identifier of the board containing the tag you want to retrieve."),
    tag_id: str = Field(..., description="The unique identifier of the tag whose information you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific tag on a board. Use this to fetch tag properties and metadata by providing the board and tag identifiers."""

    # Construct request model with validation
    try:
        _request = _models.GetTagRequest(
            path=_models.GetTagRequestPath(board_id=board_id, tag_id=tag_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/tags/{tag_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/tags/{tag_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_tag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_tag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: tags
@mcp.tool()
async def update_tag(
    board_id: str = Field(..., description="The unique identifier of the board containing the tag you want to update."),
    tag_id: str = Field(..., description="The unique identifier of the tag you want to update."),
    fill_color: Literal["red", "light_green", "cyan", "yellow", "magenta", "green", "blue", "gray", "violet", "dark_green", "dark_blue", "black"] | None = Field(None, alias="fillColor", description="The fill color for the tag. Choose from: red, light_green, cyan, yellow, magenta, green, blue, gray, violet, dark_green, dark_blue, or black."),
    title: str | None = Field(None, description="The text label for the tag, case-sensitive and must be unique within the board. Maximum 120 characters.", min_length=0, max_length=120),
) -> dict[str, Any] | ToolResult:
    """Updates an existing tag on a board by modifying its title and/or fill color. Note that changes made via the REST API will not appear in real-time on the board; you must refresh the board to see updates."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTagRequest(
            path=_models.UpdateTagRequestPath(board_id=board_id, tag_id=tag_id),
            body=_models.UpdateTagRequestBody(fill_color=fill_color, title=title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/tags/{tag_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/tags/{tag_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_tag", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_tag",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: tags
@mcp.tool()
async def delete_tag(
    board_id: str = Field(..., description="The unique identifier of the board containing the tag to delete."),
    tag_id: str = Field(..., description="The unique identifier of the tag to delete from the board."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a tag from the board and removes it from all associated cards and sticky notes. Note: Changes made via REST API may not appear in real-time on the board; refresh the board to see updates."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTagRequest(
            path=_models.DeleteTagRequestPath(board_id=board_id, tag_id=tag_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id}/tags/{tag_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id}/tags/{tag_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_tag", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_tag",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: tags
@mcp.tool()
async def list_items_by_tag(
    board_id_platform_tags: str = Field(..., alias="board_id_PlatformTags", description="The unique identifier of the board containing the items you want to retrieve."),
    tag_id: str = Field(..., description="The unique identifier of the tag used to filter items. Only items with this tag will be returned."),
    limit: str | None = Field(None, description="The maximum number of items to return in a single request. Must be between 1 and 50 items. Defaults to 20 if not specified."),
    offset: str | None = Field(None, description="The number of items to skip from the beginning of the result set, used for pagination. Defaults to 0 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all items on a board that have been assigned a specific tag. Use pagination parameters to control the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.GetItemsByTagRequest(
            path=_models.GetItemsByTagRequestPath(board_id_platform_tags=board_id_platform_tags),
            query=_models.GetItemsByTagRequestQuery(limit=limit, offset=offset, tag_id=tag_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_items_by_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id_PlatformTags}/items", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id_PlatformTags}/items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_items_by_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_items_by_tag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_items_by_tag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: tags
@mcp.tool()
async def add_tag_to_item(
    board_id_platform_tags: str = Field(..., alias="board_id_PlatformTags", description="The unique identifier of the board containing the item you want to tag."),
    item_id: str = Field(..., description="The unique identifier of the item (card or sticky note) to which you want to attach the tag."),
    tag_id: str = Field(..., description="The unique identifier of the existing tag you want to attach to the item."),
) -> dict[str, Any] | ToolResult:
    """Attach an existing tag to an item on a board. Cards and sticky notes support up to 8 tags each. Note: Tag changes via REST API require a board refresh to appear in real-time."""

    # Construct request model with validation
    try:
        _request = _models.AttachTagToItemRequest(
            path=_models.AttachTagToItemRequestPath(board_id_platform_tags=board_id_platform_tags, item_id=item_id),
            query=_models.AttachTagToItemRequestQuery(tag_id=tag_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_tag_to_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id_PlatformTags}/items/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id_PlatformTags}/items/{item_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_tag_to_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_tag_to_item", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_tag_to_item",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: tags
@mcp.tool()
async def remove_tag_from_item(
    board_id_platform_tags: str = Field(..., alias="board_id_PlatformTags", description="The unique identifier of the board containing the item from which you want to remove the tag."),
    item_id: str = Field(..., description="The unique identifier of the item from which you want to remove the tag."),
    tag_id: str = Field(..., description="The unique identifier of the tag to remove from the item."),
) -> dict[str, Any] | ToolResult:
    """Removes a tag from an item on a board. The tag remains available on the board for use with other items. Note: Tag changes via REST API require a board refresh to appear in the UI."""

    # Construct request model with validation
    try:
        _request = _models.RemoveTagFromItemRequest(
            path=_models.RemoveTagFromItemRequestPath(board_id_platform_tags=board_id_platform_tags, item_id=item_id),
            query=_models.RemoveTagFromItemRequestQuery(tag_id=tag_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_tag_from_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/boards/{board_id_PlatformTags}/items/{item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/boards/{board_id_PlatformTags}/items/{item_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_tag_from_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_tag_from_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_tag_from_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_projects_in_team(
    org_id: str = Field(..., description="The unique identifier of the organization containing the team. Required to scope the request to the correct organization."),
    team_id: str = Field(..., description="The unique identifier of the team within the organization. Required to retrieve projects from the specific team."),
    limit: str | None = Field(None, description="The maximum number of projects to return in a single response, between 1 and 100. Defaults to 100. If more projects exist than the limit, the response includes a cursor for pagination."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all projects (also called Spaces) within a specific team of an organization. With Content Admin permissions, you can access all projects including private ones not explicitly shared with you."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGetProjectsRequest(
            path=_models.EnterpriseGetProjectsRequestPath(org_id=org_id, team_id=team_id),
            query=_models.EnterpriseGetProjectsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_projects_in_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/projects", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/projects"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_projects_in_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_projects_in_team", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_projects_in_team",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def create_project_in_team(
    org_id: str = Field(..., description="The unique identifier of the organization where you want to create the project."),
    team_id: str = Field(..., description="The unique identifier of the team within the organization where you want to create the project."),
    name: str = Field(..., description="The name for the new project. Must be between 1 and 60 characters.", min_length=1, max_length=60),
) -> dict[str, Any] | ToolResult:
    """Create a new project (Space) within an existing team in your organization. Projects are organizational folders for boards that allow you to manage access and share multiple boards with a subset of team members."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseCreateProjectRequest(
            path=_models.EnterpriseCreateProjectRequestPath(org_id=org_id, team_id=team_id),
            body=_models.EnterpriseCreateProjectRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project_in_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/projects", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/projects"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_project_in_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_project_in_team", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_project_in_team",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def get_project_in_team(
    org_id: str = Field(..., description="The organization ID that contains the team and project. Use the numeric organization identifier provided in your Enterprise account."),
    team_id: str = Field(..., description="The team ID that contains the project. Use the numeric team identifier within the organization."),
    project_id: str = Field(..., description="The project ID to retrieve information for. Use the numeric project identifier within the team."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific project (Space) within a team, including its name and metadata. Enterprise-only endpoint requiring Company Admin role."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGetProjectRequest(
            path=_models.EnterpriseGetProjectRequestPath(org_id=org_id, team_id=team_id, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_in_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/projects/{project_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/projects/{project_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_in_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_in_team", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_in_team",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def update_project(
    org_id: str = Field(..., description="The unique identifier of the organization containing the project."),
    team_id: str = Field(..., description="The unique identifier of the team that owns the project."),
    project_id: str = Field(..., description="The unique identifier of the project to update."),
    name: str = Field(..., description="The new name for the project. Must be between 1 and 60 characters.", min_length=1, max_length=60),
) -> dict[str, Any] | ToolResult:
    """Update project details such as the project name. This operation is available only for Enterprise plan users with Company Admin role."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseUpdateProjectRequest(
            path=_models.EnterpriseUpdateProjectRequestPath(org_id=org_id, team_id=team_id, project_id=project_id),
            body=_models.EnterpriseUpdateProjectRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/projects/{project_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/projects/{project_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def delete_project_in_team(
    org_id: str = Field(..., description="The organization ID from which the project will be deleted. Use the numeric organization identifier."),
    team_id: str = Field(..., description="The team ID from which the project will be deleted. Use the numeric team identifier."),
    project_id: str = Field(..., description="The project ID to delete. Use the numeric project identifier."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a project (Space) from a team within an organization. Boards and users associated with the project remain in the team after deletion. Requires Enterprise plan and Company Admin role."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseDeleteProjectRequest(
            path=_models.EnterpriseDeleteProjectRequestPath(org_id=org_id, team_id=team_id, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project_in_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/projects/{project_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/projects/{project_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_project_in_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_project_in_team", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_project_in_team",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project Members
@mcp.tool()
async def list_project_members(
    org_id: str = Field(..., description="The unique identifier of the organization that contains the project."),
    team_id: str = Field(..., description="The unique identifier of the team that contains the project."),
    project_id: str = Field(..., description="The unique identifier of the project for which to retrieve members."),
    limit: str | None = Field(None, description="Maximum number of members to return per request, between 1 and 100. Defaults to 100. If the total exceeds this limit, use the cursor in the response to fetch additional results."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all members assigned to a specific project (also called a Space) within an organization and team. Requires Enterprise plan access and Company Admin role."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGetProjectMembersRequest(
            path=_models.EnterpriseGetProjectMembersRequestPath(org_id=org_id, team_id=team_id, project_id=project_id),
            query=_models.EnterpriseGetProjectMembersRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/projects/{project_id}/members", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/projects/{project_id}/members"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project Members
@mcp.tool()
async def add_project_member(
    org_id: str = Field(..., description="The unique identifier of the organization that owns the project."),
    team_id: str = Field(..., description="The unique identifier of the team that owns the project."),
    project_id: str = Field(..., description="The unique identifier of the project (Space) to which you want to add the user."),
    email: str = Field(..., description="The email address of the Miro user to add to the project."),
    role: Literal["owner", "editor", "viewer", "commentator", "coowner"] = Field(..., description="The access level for the project member. Choose from: owner, coowner, editor, commentator, or viewer."),
) -> dict[str, Any] | ToolResult:
    """Add a Miro user to a project (Space) with a specified role. This enterprise-only operation requires Company Admin privileges and the projects:write scope."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseAddProjectMemberRequest(
            path=_models.EnterpriseAddProjectMemberRequestPath(org_id=org_id, team_id=team_id, project_id=project_id),
            body=_models.EnterpriseAddProjectMemberRequestBody(email=email, role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_project_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/projects/{project_id}/members", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/projects/{project_id}/members"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_project_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_project_member", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_project_member",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project Members
@mcp.tool()
async def get_project_member(
    org_id: str = Field(..., description="The unique identifier of the organization that contains the project. Use the organization ID provided in your enterprise account."),
    team_id: str = Field(..., description="The unique identifier of the team that owns the project. Use the team ID associated with your organization."),
    project_id: str = Field(..., description="The unique identifier of the project (Space) from which you want to retrieve member information."),
    member_id: str = Field(..., description="The unique identifier of the specific member whose information you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific member within a project (Space). This enterprise-only endpoint requires Company Admin role and the projects:read scope."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGetProjectMemberRequest(
            path=_models.EnterpriseGetProjectMemberRequestPath(org_id=org_id, team_id=team_id, project_id=project_id, member_id=member_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/projects/{project_id}/members/{member_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/projects/{project_id}/members/{member_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_member", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_member",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project Members
@mcp.tool()
async def update_project_member_role(
    org_id: str = Field(..., description="The organization ID that contains the team and project. Use the numeric organization identifier (e.g., 3074457345618265000)."),
    team_id: str = Field(..., description="The team ID that owns the project. Use the numeric team identifier (e.g., 3074457345619012000)."),
    project_id: str = Field(..., description="The project (Space) ID where the member's role will be updated. Use the numeric project identifier (e.g., 3074457345618265000)."),
    member_id: str = Field(..., description="The member ID whose role you want to update. Use the numeric member identifier (e.g., 307445734562315000)."),
    role: Literal["owner", "editor", "viewer", "commentator", "coowner"] | None = Field(None, description="The new role to assign to the project member. Valid roles are: owner, coowner, editor, commentator, or viewer. Determines the member's access level and permissions within the project."),
) -> dict[str, Any] | ToolResult:
    """Update a project member's role within a team's project space. This enterprise-only operation allows Company Admins to modify member permissions such as changing them from viewer to editor or assigning ownership roles."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseUpdateProjectMemberRequest(
            path=_models.EnterpriseUpdateProjectMemberRequestPath(org_id=org_id, team_id=team_id, project_id=project_id, member_id=member_id),
            body=_models.EnterpriseUpdateProjectMemberRequestBody(role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project_member_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/projects/{project_id}/members/{member_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/projects/{project_id}/members/{member_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project_member_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project_member_role", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project_member_role",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project Members
@mcp.tool()
async def remove_project_member(
    org_id: str = Field(..., description="The unique identifier of the organization that contains the project."),
    team_id: str = Field(..., description="The unique identifier of the team that contains the project."),
    project_id: str = Field(..., description="The unique identifier of the project from which the member will be removed."),
    member_id: str = Field(..., description="The unique identifier of the member to remove from the project."),
) -> dict[str, Any] | ToolResult:
    """Remove a member from a project within a team. The member will no longer have access to the project, but remains part of the team. This operation is available only to Company Admins on Enterprise plans."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseDeleteProjectMemberRequest(
            path=_models.EnterpriseDeleteProjectMemberRequestPath(org_id=org_id, team_id=team_id, project_id=project_id, member_id=member_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_project_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/projects/{project_id}/members/{member_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/projects/{project_id}/members/{member_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_project_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_project_member", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_project_member",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def list_organization_teams(
    org_id: str = Field(..., description="The unique identifier of the organization whose teams you want to retrieve."),
    limit: str | None = Field(None, description="Maximum number of teams to return per request. Accepts values between 1 and 100, defaults to 100 if not specified."),
    name: str | None = Field(None, description="Filters teams by name using case-insensitive partial matching. For example, 'dev' will match both 'Developer's team' and 'Team for developers'."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all teams within an organization. Supports filtering by team name and pagination. Available only to Company Admins on Enterprise plans."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGetTeamsRequest(
            path=_models.EnterpriseGetTeamsRequestPath(org_id=org_id),
            query=_models.EnterpriseGetTeamsRequestQuery(limit=_limit, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_teams: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams"
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
    org_id: str = Field(..., description="The unique identifier of the organization where the team will be created."),
    name: str = Field(..., description="The name for the new team. Must be between 1 and 60 characters long.", min_length=1, max_length=60),
) -> dict[str, Any] | ToolResult:
    """Creates a new team within an existing organization. This enterprise-only operation requires Company Admin role and the organizations:teams:write scope."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseCreateTeamRequest(
            path=_models.EnterpriseCreateTeamRequestPath(org_id=org_id),
            body=_models.EnterpriseCreateTeamRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams"
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
async def get_team(
    org_id: str = Field(..., description="The unique identifier of the organization that contains the team. Use the organization ID provided during enterprise setup."),
    team_id: str = Field(..., description="The unique identifier of the team to retrieve. This must be a valid team ID within the specified organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific team within an organization. This enterprise-only endpoint requires Company Admin role and the organizations:teams:read scope."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGetTeamRequest(
            path=_models.EnterpriseGetTeamRequestPath(org_id=org_id, team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def update_team(
    org_id: str = Field(..., description="The unique identifier of the organization containing the team."),
    team_id: str = Field(..., description="The unique identifier of the team to update."),
    name: str | None = Field(None, description="The new name for the team. Must be between 1 and 60 characters long.", min_length=1, max_length=60),
) -> dict[str, Any] | ToolResult:
    """Updates an existing team's properties within an organization. Requires Enterprise plan access and Company Admin role."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseUpdateTeamRequest(
            path=_models.EnterpriseUpdateTeamRequestPath(org_id=org_id, team_id=team_id),
            body=_models.EnterpriseUpdateTeamRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_team", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_team",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def delete_team(
    org_id: str = Field(..., description="The unique identifier of the organization containing the team to delete."),
    team_id: str = Field(..., description="The unique identifier of the team to delete."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes an existing team from an organization. This operation is restricted to Enterprise plan users with Company Admin role."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseDeleteTeamRequest(
            path=_models.EnterpriseDeleteTeamRequestPath(org_id=org_id, team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}"
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

# Tags: Team Members
@mcp.tool()
async def list_team_members(
    org_id: str = Field(..., description="The unique identifier of the organization containing the team."),
    team_id: str = Field(..., description="The unique identifier of the team whose members you want to retrieve."),
    limit: str | None = Field(None, description="Maximum number of team members to return per request. Must be between 1 and 100; defaults to 100 if not specified."),
    role: str | None = Field(None, description="Filter results by member role using exact matching. Valid values are: 'member' (standard team member), 'admin' (team administrator), 'non_team' (external user without team access), or 'team_guest' (deprecated legacy guest access)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of members in a team within an organization. Supports filtering by member role and pagination via cursor-based limits."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGetTeamMembersRequest(
            path=_models.EnterpriseGetTeamMembersRequestPath(org_id=org_id, team_id=team_id),
            query=_models.EnterpriseGetTeamMembersRequestQuery(limit=_limit, role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/members", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/members"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Team Members
@mcp.tool()
async def add_team_member(
    org_id: str = Field(..., description="The unique identifier of the organization containing the team."),
    team_id: str = Field(..., description="The unique identifier of the team to which the user will be invited."),
    email: str = Field(..., description="The email address of the existing Miro organization user to invite to the team."),
    role: Literal["member", "admin"] | None = Field(None, description="The role to assign to the team member. Use 'member' for standard team member permissions or 'admin' to grant team management capabilities. Defaults to 'member' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Invite an existing Miro organization user to join a team. The user must already exist in your Miro organization; new users can be provisioned via SCIM and external identity providers like Okta or Azure Active Directory."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseInviteTeamMemberRequest(
            path=_models.EnterpriseInviteTeamMemberRequestPath(org_id=org_id, team_id=team_id),
            body=_models.EnterpriseInviteTeamMemberRequestBody(email=email, role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_team_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/members", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/members"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_team_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_team_member", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_team_member",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Team Members
@mcp.tool()
async def get_team_member(
    org_id: str = Field(..., description="The unique identifier of the organization containing the team."),
    team_id: str = Field(..., description="The unique identifier of the team containing the member."),
    member_id: str = Field(..., description="The unique identifier of the team member to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific team member by their ID within an organization and team. This enterprise-only operation requires Company Admin role and the organizations:teams:read scope."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGetTeamMemberRequest(
            path=_models.EnterpriseGetTeamMemberRequestPath(org_id=org_id, team_id=team_id, member_id=member_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/members/{member_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/members/{member_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_team_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_team_member", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_team_member",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Team Members
@mcp.tool()
async def update_team_member_role(
    org_id: str = Field(..., description="The unique identifier of the organization containing the team. Use the organization ID provided in your Enterprise account."),
    team_id: str = Field(..., description="The unique identifier of the team containing the member to update."),
    member_id: str = Field(..., description="The unique identifier of the team member whose role should be updated."),
    role: Literal["member", "admin"] | None = Field(None, description="The new role to assign to the team member. Choose 'member' for standard team member permissions or 'admin' to grant team management capabilities."),
) -> dict[str, Any] | ToolResult:
    """Update a team member's role within a team. This operation allows Company Admins to change a team member's permissions between standard member and admin roles. Available only for Enterprise plan users."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseUpdateTeamMemberRequest(
            path=_models.EnterpriseUpdateTeamMemberRequestPath(org_id=org_id, team_id=team_id, member_id=member_id),
            body=_models.EnterpriseUpdateTeamMemberRequestBody(role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_team_member_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/members/{member_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/members/{member_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_team_member_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_team_member_role", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_team_member_role",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Team Members
@mcp.tool()
async def remove_team_member(
    org_id: str = Field(..., description="The unique identifier of the organization containing the team."),
    team_id: str = Field(..., description="The unique identifier of the team from which the member will be removed."),
    member_id: str = Field(..., description="The unique identifier of the team member to be removed."),
) -> dict[str, Any] | ToolResult:
    """Remove a team member from a team by their ID. This operation is only available for Enterprise plan users with Company Admin role."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseDeleteTeamMemberRequest(
            path=_models.EnterpriseDeleteTeamMemberRequestPath(org_id=org_id, team_id=team_id, member_id=member_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_team_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/members/{member_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/members/{member_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_team_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_team_member", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_team_member",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User groups
@mcp.tool()
async def list_groups_enterprise(
    org_id: str = Field(..., description="The unique identifier of the organization whose groups you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of groups to return in a single response, between 1 and 100. Defaults to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all user groups within an organization. This operation is available only to Company Admins on Enterprise plans."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGetGroupsRequest(
            path=_models.EnterpriseGetGroupsRequestPath(org_id=org_id),
            query=_models.EnterpriseGetGroupsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_groups_enterprise: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/groups"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_groups_enterprise")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_groups_enterprise", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_groups_enterprise",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User groups
@mcp.tool()
async def create_group_organization(
    org_id: str = Field(..., description="The unique identifier of the organization where the group will be created."),
    name: str = Field(..., description="The name of the user group. Must be between 1 and 60 characters.", min_length=1, max_length=60),
    description: str | None = Field(None, description="An optional description of the user group's purpose or membership. Can be up to 300 characters.", min_length=0, max_length=300),
) -> dict[str, Any] | ToolResult:
    """Creates a new user group within an organization. This enterprise-only operation requires Company Admin role and the organizations:groups:write scope."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseCreateGroupRequest(
            path=_models.EnterpriseCreateGroupRequestPath(org_id=org_id),
            body=_models.EnterpriseCreateGroupRequestBody(name=name, description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_group_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/groups"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_group_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_group_organization", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_group_organization",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: User groups
@mcp.tool()
async def get_group_enterprise(
    org_id: str = Field(..., description="The unique identifier of the organization containing the group."),
    group_id: str = Field(..., description="The unique identifier of the user group to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific user group within an organization. This enterprise-only endpoint requires Company Admin role and the organizations:groups:read scope."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGetGroupRequest(
            path=_models.EnterpriseGetGroupRequestPath(org_id=org_id, group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_group_enterprise: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/groups/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/groups/{group_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_group_enterprise")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_group_enterprise", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_group_enterprise",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User groups
@mcp.tool()
async def update_group_org(
    org_id: str = Field(..., description="The unique identifier of the organization containing the group to update."),
    group_id: str = Field(..., description="The unique identifier of the user group to update."),
    name: str | None = Field(None, description="The new name for the group. Must be between 1 and 60 characters long.", min_length=1, max_length=60),
    description: str | None = Field(None, description="The new description for the group. Can be empty or up to 300 characters long.", min_length=0, max_length=300),
) -> dict[str, Any] | ToolResult:
    """Updates the name and/or description of a user group within an organization. This operation is restricted to Enterprise plan users with Company Admin role."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseUpdateGroupRequest(
            path=_models.EnterpriseUpdateGroupRequestPath(org_id=org_id, group_id=group_id),
            body=_models.EnterpriseUpdateGroupRequestBody(name=name, description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_group_org: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/groups/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/groups/{group_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_group_org")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_group_org", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_group_org",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: User groups
@mcp.tool()
async def delete_group_organization(
    org_id: str = Field(..., description="The unique identifier of the organization containing the group to delete."),
    group_id: str = Field(..., description="The unique identifier of the user group to delete."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a user group from an organization. This operation is restricted to Enterprise plan users with Company Admin role."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseDeleteGroupRequest(
            path=_models.EnterpriseDeleteGroupRequestPath(org_id=org_id, group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_group_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/groups/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/groups/{group_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_group_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_group_organization", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_group_organization",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User group members
@mcp.tool()
async def list_group_members(
    org_id: str = Field(..., description="The unique identifier of the organization containing the group."),
    group_id: str = Field(..., description="The unique identifier of the user group whose members you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of members to return in the response, between 1 and 100. Defaults to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all members belonging to a specific user group within an organization. This enterprise-only operation requires Company Admin role and the organizations:groups:read scope."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGetGroupMembersRequest(
            path=_models.EnterpriseGetGroupMembersRequestPath(org_id=org_id, group_id=group_id),
            query=_models.EnterpriseGetGroupMembersRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_group_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/groups/{group_id}/members", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/groups/{group_id}/members"
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

# Tags: User group members
@mcp.tool()
async def add_member_to_group(
    org_id: str = Field(..., description="The unique identifier of the organization containing the group. Use the organization ID provided in your enterprise account."),
    group_id: str = Field(..., description="The unique identifier of the user group to which the member will be added."),
    email: str = Field(..., description="The email address of the user to add to the group. Must be a valid email format associated with an existing user in the organization."),
) -> dict[str, Any] | ToolResult:
    """Adds a user to a group within an organization. This enterprise-only operation requires Company Admin role and the organizations:groups:write scope."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseCreateGroupMemberRequest(
            path=_models.EnterpriseCreateGroupMemberRequestPath(org_id=org_id, group_id=group_id),
            body=_models.EnterpriseCreateGroupMemberRequestBody(email=email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_member_to_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/groups/{group_id}/members", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/groups/{group_id}/members"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_member_to_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_member_to_group", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_member_to_group",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: User group members
@mcp.tool()
async def update_group_members(
    org_id: str = Field(..., description="The unique identifier of the organization containing the group."),
    group_id: str = Field(..., description="The unique identifier of the user group to modify."),
    members_to_add: list[str] | None = Field(None, alias="membersToAdd", description="List of user email addresses to add to the group. Each email must correspond to an existing user in the organization."),
    members_to_remove: list[str] | None = Field(None, alias="membersToRemove", description="List of user email addresses to remove from the group. Each email must correspond to a current member of the group."),
) -> dict[str, Any] | ToolResult:
    """Bulk add and remove members from a user group in a single request. Specify users to add and/or remove by email address."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseUpdateGroupMembersRequest(
            path=_models.EnterpriseUpdateGroupMembersRequestPath(org_id=org_id, group_id=group_id),
            body=_models.EnterpriseUpdateGroupMembersRequestBody(members_to_add=members_to_add, members_to_remove=members_to_remove)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_group_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/groups/{group_id}/members", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/groups/{group_id}/members"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_group_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_group_members", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_group_members",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: User group members
@mcp.tool()
async def get_group_member(
    org_id: str = Field(..., description="The unique identifier of the organization containing the group."),
    group_id: str = Field(..., description="The unique identifier of the user group from which to retrieve the member."),
    member_id: str = Field(..., description="The unique identifier of the group member whose information should be retrieved."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific user within a group in an organization. This operation requires Enterprise plan access and Company Admin role."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGetGroupMemberRequest(
            path=_models.EnterpriseGetGroupMemberRequestPath(org_id=org_id, group_id=group_id, member_id=member_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_group_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/groups/{group_id}/members/{member_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/groups/{group_id}/members/{member_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_group_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_group_member", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_group_member",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User group members
@mcp.tool()
async def remove_group_member(
    org_id: str = Field(..., description="The unique identifier of the organization containing the group."),
    group_id: str = Field(..., description="The unique identifier of the user group from which the member will be removed."),
    member_id: str = Field(..., description="The unique identifier of the group member to be removed."),
) -> dict[str, Any] | ToolResult:
    """Remove a member from a user group within an organization. This operation is restricted to Enterprise plan users with Company Admin role."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseDeleteGroupMemberRequest(
            path=_models.EnterpriseDeleteGroupMemberRequestPath(org_id=org_id, group_id=group_id, member_id=member_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_group_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/groups/{group_id}/members/{member_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/groups/{group_id}/members/{member_id}"
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

# Tags: User group to teams
@mcp.tool()
async def list_teams_for_group(
    org_id: str = Field(..., description="The unique identifier of the organization containing the group."),
    group_id: str = Field(..., description="The unique identifier of the user group whose team memberships you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of teams to return in the response, between 1 and 100. Defaults to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all teams that a user group is a member of within an organization. This operation is available only to Company Admins on Enterprise plans."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGroupsGetTeamsRequest(
            path=_models.EnterpriseGroupsGetTeamsRequestPath(org_id=org_id, group_id=group_id),
            query=_models.EnterpriseGroupsGetTeamsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_teams_for_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/groups/{group_id}/teams", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/groups/{group_id}/teams"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_teams_for_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_teams_for_group", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_teams_for_group",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: User group to teams
@mcp.tool()
async def get_group_team(
    org_id: str = Field(..., description="The unique identifier of the organization containing the group and team."),
    group_id: str = Field(..., description="The unique identifier of the user group within the organization."),
    team_id: str = Field(..., description="The unique identifier of the team to retrieve information for."),
) -> dict[str, Any] | ToolResult:
    """Retrieve details about a specific team that a user group belongs to within an organization. This enterprise-only operation requires Company Admin role and appropriate organizational scopes."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseGroupsGetTeamRequest(
            path=_models.EnterpriseGroupsGetTeamRequestPath(org_id=org_id, group_id=group_id, team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_group_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/groups/{group_id}/teams/{team_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/groups/{group_id}/teams/{team_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_group_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_group_team", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_group_team",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Team user groups
@mcp.tool()
async def list_groups_for_team(
    org_id: str = Field(..., description="The unique identifier of the organization containing the team."),
    team_id: str = Field(..., description="The unique identifier of the team whose connected groups you want to retrieve."),
    limit: str | None = Field(None, description="The maximum number of user groups to return in the response, between 1 and 100. Defaults to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all user groups that are connected to a specific team within an organization. This operation is available only for Enterprise plan users with Company Admin role."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.EnterpriseTeamsGetGroupsRequest(
            path=_models.EnterpriseTeamsGetGroupsRequestPath(org_id=org_id, team_id=team_id),
            query=_models.EnterpriseTeamsGetGroupsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_groups_for_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/groups"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_groups_for_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_groups_for_team", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_groups_for_team",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Team user groups
@mcp.tool()
async def add_user_group_to_team(
    org_id: str = Field(..., description="The unique identifier of the organization where the team resides."),
    team_id: str = Field(..., description="The unique identifier of the team to which the user group will be added."),
    user_group_id: str = Field(..., alias="userGroupId", description="The unique identifier of the user group to be added to the team."),
    role: Literal["member"] = Field(..., description="The role assigned to the user group within the team. Currently supports member role."),
) -> dict[str, Any] | ToolResult:
    """Adds a user group to a team within an organization, establishing the group's membership and role. This enterprise-only operation requires Company Admin privileges."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseTeamsCreateGroupRequest(
            path=_models.EnterpriseTeamsCreateGroupRequestPath(org_id=org_id, team_id=team_id),
            body=_models.EnterpriseTeamsCreateGroupRequestBody(user_group_id=user_group_id, role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_user_group_to_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/groups"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_user_group_to_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_user_group_to_team", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_user_group_to_team",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Team user groups
@mcp.tool()
async def get_team_group(
    org_id: str = Field(..., description="The unique identifier of the organization. Use the organization ID provided in your Enterprise account."),
    team_id: str = Field(..., description="The unique identifier of the team. Use the team ID to scope the group lookup within a specific team."),
    group_id: str = Field(..., description="The unique identifier of the user group. Use the group ID to retrieve information about a specific group within the team."),
) -> dict[str, Any] | ToolResult:
    """Retrieve details about a specific user group within a team. This operation requires Enterprise plan access and Company Admin role."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseTeamsGetGroupRequest(
            path=_models.EnterpriseTeamsGetGroupRequestPath(org_id=org_id, team_id=team_id, group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/groups/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/groups/{group_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_team_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_team_group", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_team_group",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Team user groups
@mcp.tool()
async def remove_group_from_team(
    org_id: str = Field(..., description="The unique identifier of the organization containing the team. Use the organization ID provided during setup (a numeric string)."),
    team_id: str = Field(..., description="The unique identifier of the team from which the group will be removed. Use the team ID provided during setup (a numeric string)."),
    group_id: str = Field(..., description="The unique identifier of the user group to remove from the team. Use the group ID provided during setup (a numeric string)."),
) -> dict[str, Any] | ToolResult:
    """Remove a user group from a team within an organization. This operation disconnects the group's access to the team and is only available for Enterprise plan users with Company Admin role."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseTeamsDeleteGroupRequest(
            path=_models.EnterpriseTeamsDeleteGroupRequestPath(org_id=org_id, team_id=team_id, group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_group_from_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/teams/{team_id}/groups/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/teams/{team_id}/groups/{group_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_group_from_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_group_from_team", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_group_from_team",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Share boards with groups
@mcp.tool()
async def list_board_groups(
    org_id: str = Field(..., description="The unique identifier of the organization containing the board."),
    board_id: str = Field(..., description="The unique identifier of the board for which to retrieve group assignments."),
    limit: str | None = Field(None, description="The maximum number of user groups to return in the response, between 1 and 100. Defaults to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all user groups that have been invited to a specific board. This operation is available only for Enterprise plan users with Company Admin role."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.EnterpriseBoardsGetGroupsRequest(
            path=_models.EnterpriseBoardsGetGroupsRequestPath(org_id=org_id, board_id=board_id),
            query=_models.EnterpriseBoardsGetGroupsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_board_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/boards/{board_id}/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/boards/{board_id}/groups"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_board_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_board_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_board_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Share boards with groups
@mcp.tool()
async def share_board_with_groups(
    org_id: str = Field(..., description="The unique identifier of the organization. Format: numeric string (e.g., '3074457345618265000')."),
    board_id: str = Field(..., description="The unique identifier of the board to share. Format: alphanumeric string (e.g., 'uXjVOfjm6tI=')."),
    user_group_ids: list[str] = Field(..., alias="userGroupIds", description="One or more user group IDs to grant access to the board. Provide as an array of group identifiers."),
    role: Literal["VIEWER", "COMMENTER", "EDITOR"] = Field(..., description="The permission level for the user groups on the board. Choose from: VIEWER (read-only access), COMMENTER (can view and comment), or EDITOR (full editing access). Defaults to VIEWER if not specified."),
) -> dict[str, Any] | ToolResult:
    """Grant user groups access to a board with a specified role. If a group already has access, this operation updates their role. Enterprise-only operation requiring Company Admin privileges."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseBoardsCreateGroupRequest(
            path=_models.EnterpriseBoardsCreateGroupRequestPath(org_id=org_id, board_id=board_id),
            body=_models.EnterpriseBoardsCreateGroupRequestBody(user_group_ids=user_group_ids, role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for share_board_with_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/boards/{board_id}/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/boards/{board_id}/groups"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("share_board_with_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("share_board_with_groups", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="share_board_with_groups",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Share boards with groups
@mcp.tool()
async def remove_group_from_board(
    org_id: str = Field(..., description="The unique identifier of the organization that contains the board."),
    board_id: str = Field(..., description="The unique identifier of the board from which the user group will be removed."),
    group_id: str = Field(..., description="The unique identifier of the user group to be removed from the board."),
) -> dict[str, Any] | ToolResult:
    """Remove a user group's access from a board. This operation revokes the specified user group's assignment to the board within an organization."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseBoardsDeleteGroupsRequest(
            path=_models.EnterpriseBoardsDeleteGroupsRequestPath(org_id=org_id, board_id=board_id, group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_group_from_board: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/boards/{board_id}/groups/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/boards/{board_id}/groups/{group_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_group_from_board")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_group_from_board", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_group_from_board",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Share projects with groups
@mcp.tool()
async def list_project_groups(
    org_id: str = Field(..., description="The unique identifier of the organization containing the project."),
    project_id: str = Field(..., description="The unique identifier of the project for which to retrieve group assignments."),
    limit: str | None = Field(None, description="Maximum number of groups to return in the response, between 1 and 100. Defaults to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve user groups that have been invited to a specific project. Returns a paginated list of group assignments within the project."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.EnterpriseProjectsGetGroupsRequest(
            path=_models.EnterpriseProjectsGetGroupsRequestPath(org_id=org_id, project_id=project_id),
            query=_models.EnterpriseProjectsGetGroupsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/projects/{project_id}/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/projects/{project_id}/groups"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Share projects with groups
@mcp.tool()
async def share_project_with_groups(
    org_id: str = Field(..., description="The unique identifier of the organization containing the project."),
    project_id: str = Field(..., description="The unique identifier of the project to share with user groups."),
    user_group_ids: list[str] = Field(..., alias="userGroupIds", description="List of user group identifiers to grant or update access for. Each ID must be a valid group within the organization."),
    role: Literal["VIEWER", "COMMENTER", "EDITOR"] = Field(..., description="The access level to assign to the user groups. Choose from: VIEWER (read-only access), COMMENTER (read and comment), or EDITOR (full edit access). Defaults to VIEWER if not specified."),
) -> dict[str, Any] | ToolResult:
    """Grant user groups access to a project with a specified role. If a group already has access, this operation updates their role assignment."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseProjectCreateGroupRequest(
            path=_models.EnterpriseProjectCreateGroupRequestPath(org_id=org_id, project_id=project_id),
            body=_models.EnterpriseProjectCreateGroupRequestBody(user_group_ids=user_group_ids, role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for share_project_with_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/projects/{project_id}/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/projects/{project_id}/groups"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("share_project_with_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("share_project_with_groups", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="share_project_with_groups",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Share projects with groups
@mcp.tool()
async def remove_group_from_project(
    org_id: str = Field(..., description="The organization ID that contains the project. Use the numeric organization identifier."),
    project_id: str = Field(..., description="The project ID from which to remove the group. Use the numeric project identifier."),
    group_id: str = Field(..., description="The user group ID to remove from the project. Use the numeric group identifier."),
) -> dict[str, Any] | ToolResult:
    """Remove a user group from a project. This operation unassigns the specified group from the project, revoking group members' access to the project resources."""

    # Construct request model with validation
    try:
        _request = _models.EnterpriseProjectDeleteGroupsRequest(
            path=_models.EnterpriseProjectDeleteGroupsRequestPath(org_id=org_id, project_id=project_id, group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_group_from_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/orgs/{org_id}/projects/{project_id}/groups/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/orgs/{org_id}/projects/{project_id}/groups/{group_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_group_from_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_group_from_project", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_group_from_project",
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
        print("  python miro_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Miro MCP Server")

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
    logger.info("Starting Miro MCP Server")
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

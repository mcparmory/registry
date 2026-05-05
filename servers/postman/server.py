#!/usr/bin/env python3
"""
Postman MCP Server
Generated: 2026-05-05 16:01:50 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://api.getpostman.com")
SERVER_NAME = "Postman"
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
    'ApiKeyAuth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["ApiKeyAuth"] = _auth.APIKeyAuth(env_var="API_KEY", location="header", param_name="X-API-Key")
    logging.info("Authentication configured: ApiKeyAuth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for ApiKeyAuth not configured: {error_msg}")
    _auth_handlers["ApiKeyAuth"] = None

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

mcp = FastMCP("Postman", middleware=[_JsonCoercionMiddleware()])

# Tags: API
@mcp.tool()
async def list_apis(
    workspace: str | None = Field(None, description="Filter results to APIs within a specific workspace. Provide the workspace ID to scope the query."),
    since: str | None = Field(None, description="Filter results to APIs updated on or after this timestamp. Use ISO 8601 date-time format."),
    until: str | None = Field(None, description="Filter results to APIs updated on or before this timestamp. Use ISO 8601 date-time format."),
    created_by: str | None = Field(None, alias="createdBy", description="Filter results to APIs created by a specific user. Provide the user ID."),
    updated_by: str | None = Field(None, alias="updatedBy", description="Filter results to APIs last updated by a specific user. Provide the user ID."),
    is_public: str | None = Field(None, alias="isPublic", description="Filter results by privacy state: use true for public APIs or false for private APIs."),
    name: str | None = Field(None, description="Filter results to APIs whose name contains this value. Matching is case-insensitive."),
    summary: str | None = Field(None, description="Filter results to APIs whose summary contains this value. Matching is case-insensitive."),
    description: str | None = Field(None, description="Filter results to APIs whose description contains this value. Matching is case-insensitive."),
    sort: str | None = Field(None, description="Sort results by a specific field name from the response. Combine with direction parameter to control sort order."),
    direction: str | None = Field(None, description="Set sort order to ascending (asc) or descending (desc). Defaults to descending for timestamps and numeric fields, ascending otherwise."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all APIs in a workspace with optional filtering by metadata, timestamps, privacy state, and text search. Results can be sorted by any response field in ascending or descending order."""

    # Construct request model with validation
    try:
        _request = _models.GetAllApIsRequest(
            query=_models.GetAllApIsRequestQuery(workspace=workspace, since=since, until=until, created_by=created_by, updated_by=updated_by, is_public=is_public, name=name, summary=summary, description=description, sort=sort, direction=direction)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_apis: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/apis"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_apis")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_apis", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_apis",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: API
@mcp.tool()
async def create_api(
    workspace: str | None = Field(None, description="The workspace ID where the API will be created. If not specified, the API is created in the default workspace."),
    description: str | None = Field(None, description="A detailed description of the API's purpose and functionality."),
    name: str | None = Field(None, description="The name of the API. This is a required field and must be provided in the request body."),
    summary: str | None = Field(None, description="A short summary of the API's purpose. Should be concise and suitable for display in API listings."),
) -> dict[str, Any] | ToolResult:
    """Creates a new API with a default API Version. The request must include an `api` object with at least a `name` property, and returns the created API with full details including id, name, summary, and description."""

    # Construct request model with validation
    try:
        _request = _models.CreateApiRequest(
            query=_models.CreateApiRequestQuery(workspace=workspace),
            body=_models.CreateApiRequestBody(api=_models.CreateApiRequestBodyApi(description=description, name=name, summary=summary) if any(v is not None for v in [description, name, summary]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_api: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/apis"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_api")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_api", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_api",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: API
@mcp.tool()
async def get_api(api_id: str = Field(..., alias="apiId", description="The unique identifier of the API to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific API by its ID, including metadata such as name, summary, and description."""

    # Construct request model with validation
    try:
        _request = _models.SingleApiRequest(
            path=_models.SingleApiRequestPath(api_id=api_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_api: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_api")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_api", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_api",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: API
@mcp.tool()
async def update_api(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API to update."),
    description: str | None = Field(None, description="The updated description for the API. Provide a clear, concise explanation of what the API does."),
    name: str | None = Field(None, description="The updated name for the API. Use a descriptive title that identifies the API's purpose."),
) -> dict[str, Any] | ToolResult:
    """Update an existing API by modifying its name, summary, or description. Returns the complete updated API object with all current details."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAnApiRequest(
            path=_models.UpdateAnApiRequestPath(api_id=api_id),
            body=_models.UpdateAnApiRequestBody(api=_models.UpdateAnApiRequestBodyApi(description=description, name=name) if any(v is not None for v in [description, name]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_api: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_api")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_api", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_api",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: API
@mcp.tool()
async def delete_api(api_id: str = Field(..., alias="apiId", description="The unique identifier of the API to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an API by its ID. Returns the deleted API object with its ID for confirmation."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnApiRequest(
            path=_models.DeleteAnApiRequestPath(api_id=api_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_api: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_api")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_api", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_api",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, API Version
@mcp.tool()
async def list_api_versions(api_id: str = Field(..., alias="apiId", description="The unique identifier of the API for which to retrieve all versions.")) -> dict[str, Any] | ToolResult:
    """Retrieve all versions of a specified API, including detailed metadata for each version."""

    # Construct request model with validation
    try:
        _request = _models.GetAllApiVersionsRequest(
            path=_models.GetAllApiVersionsRequestPath(api_id=api_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_api_versions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_api_versions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_api_versions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_api_versions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, API Version
@mcp.tool()
async def create_api_version(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API in which to create the new version."),
    name: str | None = Field(None, description="The name for the new API version (e.g., '1.0', '2.0-beta'). Required when creating a version from scratch."),
    id_: str | None = Field(None, alias="id", description="The unique identifier of an existing API version to copy configuration and resources from. When specified, the new version will inherit selected schema and relations from this source version."),
    documentation: bool | None = Field(None, description="When true, copies the API schema (specification/definition) from the source API version to the new version."),
    mock: bool | None = Field(None, description="When true, copies mock server configurations from the source API version to the new version."),
    monitor: bool | None = Field(None, description="When true, copies monitoring configurations from the source API version to the new version."),
) -> dict[str, Any] | ToolResult:
    """Creates a new API version within the specified API. Optionally copies schema and related resources (mocks, monitors, documentation, tests, etc.) from an existing API version."""

    # Construct request model with validation
    try:
        _request = _models.CreateApiVersionRequest(
            path=_models.CreateApiVersionRequestPath(api_id=api_id),
            body=_models.CreateApiVersionRequestBody(version=_models.CreateApiVersionRequestBodyVersion(name=name,
                    source=_models.CreateApiVersionRequestBodyVersionSource(id_=id_,
                        relations=_models.CreateApiVersionRequestBodyVersionSourceRelations(documentation=documentation, mock=mock, monitor=monitor) if any(v is not None for v in [documentation, mock, monitor]) else None) if any(v is not None for v in [id_, documentation, mock, monitor]) else None) if any(v is not None for v in [name, id_, documentation, mock, monitor]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_api_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_api_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_api_version", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_api_version",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, API Version
@mcp.tool()
async def get_api_version(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API containing the version to retrieve."),
    api_version_id: str = Field(..., alias="apiVersionId", description="The unique identifier of the specific API version to fetch."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific API version, including its configuration and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetAnApiVersionRequest(
            path=_models.GetAnApiVersionRequestPath(api_id=api_id, api_version_id=api_version_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_api_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions/{apiVersionId}", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions/{apiVersionId}"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_api_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_api_version", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_api_version",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, API Version
@mcp.tool()
async def update_api_version(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API containing the version to update."),
    api_version_id: str = Field(..., alias="apiVersionId", description="The unique identifier of the API version to update."),
    name: str | None = Field(None, description="The new name for the API version (e.g., '2.0'). This is the only field that can be updated."),
) -> dict[str, Any] | ToolResult:
    """Update the name of an existing API version. Provide the API ID and version ID, along with the new name in the request body."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAnApiVersionRequest(
            path=_models.UpdateAnApiVersionRequestPath(api_id=api_id, api_version_id=api_version_id),
            body=_models.UpdateAnApiVersionRequestBody(version=_models.UpdateAnApiVersionRequestBodyVersion(name=name) if any(v is not None for v in [name]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_api_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions/{apiVersionId}", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions/{apiVersionId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_api_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_api_version", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_api_version",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, API Version
@mcp.tool()
async def delete_api_version(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API containing the version to delete."),
    api_version_id: str = Field(..., alias="apiVersionId", description="The unique identifier of the API version to delete."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific API version. Returns the id of the deleted API version."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnApiVersionRequest(
            path=_models.DeleteAnApiVersionRequestPath(api_id=api_id, api_version_id=api_version_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_api_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions/{apiVersionId}", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions/{apiVersionId}"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_api_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_api_version", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_api_version",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, Relations
@mcp.tool()
async def list_contract_test_relations(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API for which to fetch contract test relations."),
    api_version_id: str = Field(..., alias="apiVersionId", description="The unique identifier of the specific API version for which to fetch contract test relations."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all contract test relations linked to a specific API version, organized by relation type with complete details for each relation."""

    # Construct request model with validation
    try:
        _request = _models.GetContractTestRelationsRequest(
            path=_models.GetContractTestRelationsRequestPath(api_id=api_id, api_version_id=api_version_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_contract_test_relations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions/{apiVersionId}/contracttest", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions/{apiVersionId}/contracttest"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_contract_test_relations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_contract_test_relations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_contract_test_relations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, Relations
@mcp.tool()
async def get_documentation_relations(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API for which to fetch documentation relations."),
    api_version_id: str = Field(..., alias="apiVersionId", description="The unique identifier of the API version for which to fetch documentation relations."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all documentation relations linked to a specific API version, organized by relation type with complete details for each relation."""

    # Construct request model with validation
    try:
        _request = _models.GetDocumentationRelationsRequest(
            path=_models.GetDocumentationRelationsRequestPath(api_id=api_id, api_version_id=api_version_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_documentation_relations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions/{apiVersionId}/documentation", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions/{apiVersionId}/documentation"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_documentation_relations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_documentation_relations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_documentation_relations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, Relations
@mcp.tool()
async def get_environment_relations_for_api_version(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API for which to retrieve environment relations."),
    api_version_id: str = Field(..., alias="apiVersionId", description="The unique identifier of the specific API version for which to retrieve environment relations."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all environment relations linked to a specific API version, organized by relation type with complete details for each relation."""

    # Construct request model with validation
    try:
        _request = _models.GetEnvironmentRelationsRequest(
            path=_models.GetEnvironmentRelationsRequestPath(api_id=api_id, api_version_id=api_version_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_environment_relations_for_api_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions/{apiVersionId}/environment", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions/{apiVersionId}/environment"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_environment_relations_for_api_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_environment_relations_for_api_version", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_environment_relations_for_api_version",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, Relations
@mcp.tool()
async def list_integration_test_relations(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API for which to fetch integration test relations."),
    api_version_id: str = Field(..., alias="apiVersionId", description="The unique identifier of the API version for which to fetch integration test relations."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all integration test relations linked to a specific API version, organized by relation type with complete details for each relation."""

    # Construct request model with validation
    try:
        _request = _models.GetIntegrationTestRelationsRequest(
            path=_models.GetIntegrationTestRelationsRequestPath(api_id=api_id, api_version_id=api_version_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_integration_test_relations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions/{apiVersionId}/integrationtest", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions/{apiVersionId}/integrationtest"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_integration_test_relations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_integration_test_relations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_integration_test_relations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, Relations
@mcp.tool()
async def list_monitor_relations(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API."),
    api_version_id: str = Field(..., alias="apiVersionId", description="The unique identifier of the API version for which to fetch monitor relations."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all monitor relations linked to a specific API version, organized by relation type with complete details for each relation."""

    # Construct request model with validation
    try:
        _request = _models.GetMonitorRelationsRequest(
            path=_models.GetMonitorRelationsRequestPath(api_id=api_id, api_version_id=api_version_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_monitor_relations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions/{apiVersionId}/monitor", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions/{apiVersionId}/monitor"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_monitor_relations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_monitor_relations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_monitor_relations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, Relations
@mcp.tool()
async def list_linked_relations(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API for which to retrieve linked relations."),
    api_version_id: str = Field(..., alias="apiVersionId", description="The unique identifier of the API version for which to retrieve linked relations."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all relations linked to a specific API version, including detailed information about each relation type and its associated relations."""

    # Construct request model with validation
    try:
        _request = _models.GetLinkedRelationsRequest(
            path=_models.GetLinkedRelationsRequestPath(api_id=api_id, api_version_id=api_version_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_linked_relations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions/{apiVersionId}/relations", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions/{apiVersionId}/relations"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_linked_relations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_linked_relations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_linked_relations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, Relations
@mcp.tool()
async def add_relations_to_api_version(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API to which relations will be added."),
    api_version_id: str = Field(..., alias="apiVersionId", description="The unique identifier of the API version to which relations will be added."),
    contracttest: list[str] | None = Field(None, description="Array of Collection UIDs to associate as contract tests with this API version."),
    documentation: list[str] | None = Field(None, description="Array of Collection UIDs to associate as documentation with this API version."),
    mock: list[str] | None = Field(None, description="Array of Mock IDs to associate with this API version."),
    testsuite: list[str] | None = Field(None, description="Array of Collection UIDs to associate as test suites with this API version."),
) -> dict[str, Any] | ToolResult:
    """Link existing Postman entities (collections, environments, mocks, monitors) to an API version as relations. Specify which entity types to associate by providing their corresponding UIDs or IDs in the request body."""

    # Construct request model with validation
    try:
        _request = _models.CreateRelationsRequest(
            path=_models.CreateRelationsRequestPath(api_id=api_id, api_version_id=api_version_id),
            body=_models.CreateRelationsRequestBody(contracttest=contracttest, documentation=documentation, mock=mock, testsuite=testsuite)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_relations_to_api_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions/{apiVersionId}/relations", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions/{apiVersionId}/relations"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_relations_to_api_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_relations_to_api_version", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_relations_to_api_version",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, Schema
@mcp.tool()
async def create_schema(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API to which the schema will be added."),
    api_version_id: str = Field(..., alias="apiVersionId", description="The unique identifier of the API version under which the schema will be created."),
    language: str | None = Field(None, description="The schema language format. Use 'json' or 'yaml' for OpenAPI and RAML schemas; use 'graphql' exclusively for GraphQL schemas."),
    type_: str | None = Field(None, alias="type", description="The schema type specification. Supported types are 'openapi3', 'openapi2', 'openapi1', 'raml', and 'graphql'."),
) -> dict[str, Any] | ToolResult:
    """Creates a new schema for an API version. The schema can be defined in OpenAPI (v1, v2, v3), RAML, or GraphQL format with corresponding language specification."""

    # Construct request model with validation
    try:
        _request = _models.CreateSchemaRequest(
            path=_models.CreateSchemaRequestPath(api_id=api_id, api_version_id=api_version_id),
            body=_models.CreateSchemaRequestBody(schema_=_models.CreateSchemaRequestBodySchema(language=language, type_=type_) if any(v is not None for v in [language, type_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_schema: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions/{apiVersionId}/schemas", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions/{apiVersionId}/schemas"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_schema")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_schema", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_schema",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, Schema
@mcp.tool()
async def get_schema(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API containing the schema."),
    api_version_id: str = Field(..., alias="apiVersionId", description="The unique identifier of the API version containing the schema."),
    schema_id: str = Field(..., alias="schemaId", description="The unique identifier of the schema to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single schema by its ID. Returns a schema object containing metadata including id, language, type, and schema definition."""

    # Construct request model with validation
    try:
        _request = _models.GetSchemaRequest(
            path=_models.GetSchemaRequestPath(api_id=api_id, api_version_id=api_version_id, schema_id=schema_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_schema: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions/{apiVersionId}/schemas/{schemaId}", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions/{apiVersionId}/schemas/{schemaId}"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

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

# Tags: API, Schema
@mcp.tool()
async def update_schema(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API containing the schema to update."),
    api_version_id: str = Field(..., alias="apiVersionId", description="The unique identifier of the API version containing the schema to update."),
    schema_id: str = Field(..., alias="schemaId", description="The unique identifier of the schema to update."),
    language: str | None = Field(None, description="The schema language format. Use `json` or `yaml` for OpenAPI and RAML schemas; use `graphql` for GraphQL schemas."),
    type_: str | None = Field(None, alias="type", description="The schema type being updated. Allowed values are `openapi3`, `openapi2`, `openapi1`, `raml`, or `graphql`."),
) -> dict[str, Any] | ToolResult:
    """Update an existing API schema by replacing its content and metadata. Supports OpenAPI (v1, v2, v3), RAML, and GraphQL schema types in their respective formats."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSchemaRequest(
            path=_models.UpdateSchemaRequestPath(api_id=api_id, api_version_id=api_version_id, schema_id=schema_id),
            body=_models.UpdateSchemaRequestBody(schema_=_models.UpdateSchemaRequestBodySchema(language=language, type_=type_) if any(v is not None for v in [language, type_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_schema: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions/{apiVersionId}/schemas/{schemaId}", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions/{apiVersionId}/schemas/{schemaId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_schema")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_schema", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_schema",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, Schema
@mcp.tool()
async def create_collection_from_schema(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API to which the collection will be linked."),
    api_version_id: str = Field(..., alias="apiVersionId", description="The unique identifier of the API version to which the collection will be linked."),
    schema_id: str = Field(..., alias="schemaId", description="The unique identifier of the schema from which the collection will be created."),
    workspace: str | None = Field(None, description="The workspace ID where the collection will be created. Use the workspace identifier to scope the collection to a specific workspace context."),
    name: str | None = Field(None, description="The display name for the new collection. This is a human-readable identifier for organizing and referencing the collection."),
    relations: list[_models.CreateCollectionFromSchemaBodyRelationsItem] | None = Field(None, description="An array of relation types to associate with the collection. Valid relation types are: contracttest, integrationtest, testsuite, and documentation. At least one relation type should be specified to define the collection's purpose."),
) -> dict[str, Any] | ToolResult:
    """Create a new collection linked to an API schema with one or more relation types (contract test, integration test, test suite, or documentation). The collection serves as an organizational container for API-related artifacts."""

    # Construct request model with validation
    try:
        _request = _models.CreateCollectionFromSchemaRequest(
            path=_models.CreateCollectionFromSchemaRequestPath(api_id=api_id, api_version_id=api_version_id, schema_id=schema_id),
            query=_models.CreateCollectionFromSchemaRequestQuery(workspace=workspace),
            body=_models.CreateCollectionFromSchemaRequestBody(name=name, relations=relations)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_collection_from_schema: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions/{apiVersionId}/schemas/{schemaId}/collections", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions/{apiVersionId}/schemas/{schemaId}/collections"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_collection_from_schema")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_collection_from_schema", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_collection_from_schema",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, Relations
@mcp.tool()
async def list_test_suite_relations(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API for which to retrieve test suite relations."),
    api_version_id: str = Field(..., alias="apiVersionId", description="The unique identifier of the API version for which to retrieve test suite relations."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all test suite relations linked to a specific API version, organized by relation type with complete details for each relation."""

    # Construct request model with validation
    try:
        _request = _models.GetTestSuiteRelationsRequest(
            path=_models.GetTestSuiteRelationsRequestPath(api_id=api_id, api_version_id=api_version_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_test_suite_relations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions/{apiVersionId}/testsuite", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions/{apiVersionId}/testsuite"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_test_suite_relations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_test_suite_relations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_test_suite_relations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: API, Relations
@mcp.tool()
async def sync_relation_with_schema(
    api_id: str = Field(..., alias="apiId", description="The unique identifier of the API containing the relation to synchronize."),
    api_version_id: str = Field(..., alias="apiVersionId", description="The unique identifier of the specific API version whose schema will be used for synchronization."),
    entity_type: str = Field(..., alias="entityType", description="The type of relation to sync, such as documentation, contracttest, integrationtest, testsuite, mock, or monitor."),
    entity_id: str = Field(..., alias="entityId", description="The unique identifier of the specific relation instance to synchronize with the schema."),
) -> dict[str, Any] | ToolResult:
    """Synchronize a relation (such as documentation, contract test, or monitor) with the current API schema to ensure consistency and alignment with schema changes."""

    # Construct request model with validation
    try:
        _request = _models.SyncRelationsWithSchemaRequest(
            path=_models.SyncRelationsWithSchemaRequestPath(api_id=api_id, api_version_id=api_version_id, entity_type=entity_type, entity_id=entity_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for sync_relation_with_schema: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/apis/{apiId}/versions/{apiVersionId}/{entityType}/{entityId}/syncWithSchema", _request.path.model_dump(by_alias=True)) if _request.path else "/apis/{apiId}/versions/{apiVersionId}/{entityType}/{entityId}/syncWithSchema"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Accept"] = "application/vnd.api.v10+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("sync_relation_with_schema")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("sync_relation_with_schema", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="sync_relation_with_schema",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def list_collections() -> dict[str, Any] | ToolResult:
    """Retrieve all collections accessible to you, including your own collections and those you have subscribed to. Each collection includes its name, ID, owner, and UID."""

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

# Tags: Collections
@mcp.tool()
async def create_collection(
    description: str | None = Field(None, description="A descriptive label for the collection (e.g., 'This is just a sample collection.'). Helps identify the collection's purpose."),
    name: str | None = Field(None, description="The name of the collection. Supports dynamic variables like {{$randomInt}} for generating unique names."),
    item: list[_models.CreateCollectionBodyCollectionItemItem] | None = Field(None, description="An array of request items to include in the collection. Items define the API requests and folder structure within the collection."),
    schema_: str | None = Field(None, alias="schema"),
) -> dict[str, Any] | ToolResult:
    """Create a new Postman collection in Postman Collection v2 format. Returns the created collection's name, ID, and UID. Optionally specify a workspace via query parameter to create the collection in a specific workspace."""

    # Construct request model with validation
    try:
        _request = _models.CreateCollectionRequest(
            body=_models.CreateCollectionRequestBody(collection=_models.CreateCollectionRequestBodyCollection(item=item,
                    info=_models.CreateCollectionRequestBodyCollectionInfo(description=description, name=name, schema_=schema_) if any(v is not None for v in [description, name, schema_]) else None) if any(v is not None for v in [description, name, item, schema_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_collection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_collection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def create_fork_of_collection(
    collection_uid: str = Field(..., description="The unique identifier of the collection to fork."),
    workspace: str | None = Field(None, description="The ID of the workspace where the forked collection should be created. If not specified, the fork will be created in the default workspace."),
) -> dict[str, Any] | ToolResult:
    """Create a fork of an existing collection. The response includes the forked collection's name, ID, UID, and fork metadata. You can optionally specify a target workspace for the fork. Note: The fork is created with a default label 'Forked Collection' (Postman v10 API requires 'label', and the schema-declared 'name' field is rejected)."""

    # Construct request model with validation
    try:
        _request = _models.CreateAForkRequest(
            path=_models.CreateAForkRequestPath(collection_uid=collection_uid),
            query=_models.CreateAForkRequestQuery(workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_fork_of_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/collections/fork/{collection_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/collections/fork/{collection_uid}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body: dict[str, Any] = {}
    # Constant body fields (from schemas.patch.json add_constant_body_fields) — fixed values, not agent-configurable.
    # If the original schema has a body but it's null/scalar (body_is_whole_body case), coerce to empty dict first.
    if not isinstance(_http_body, dict):
        _http_body = {}
    _http_body["label"] = 'Forked Collection'
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_fork_of_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_fork_of_collection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_fork_of_collection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def merge_fork_to_collection(
    destination: str | None = Field(None, description="The UID of the destination collection where the fork will be merged into. Required for the merge operation."),
    source: str | None = Field(None, description="The UID of the forked collection to merge. This is the source collection that will be merged into the destination."),
    strategy: str | None = Field(None, description="The merge strategy to apply: `deleteSource` removes the forked collection after merging, or `updateSourceWithDestination` syncs the forked collection with any changes made to the destination. Defaults to standard merge behavior if not specified."),
) -> dict[str, Any] | ToolResult:
    """Merge a forked collection back into its destination collection. Optionally specify a merge strategy to control whether the source fork is deleted or updated with destination changes after the merge."""

    # Construct request model with validation
    try:
        _request = _models.MergeAForkRequest(
            body=_models.MergeAForkRequestBody(destination=destination, source=source, strategy=strategy)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for merge_fork_to_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/collections/merge"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("merge_fork_to_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("merge_fork_to_collection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="merge_fork_to_collection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def get_collection(collection_uid: str = Field(..., description="The unique identifier (uid) of the collection to retrieve. This is a required string value that uniquely identifies the collection within the system.")) -> dict[str, Any] | ToolResult:
    """Retrieve the full contents of a specific collection by its unique identifier. You must have access permissions to the collection to retrieve it."""

    # Construct request model with validation
    try:
        _request = _models.SingleCollectionRequest(
            path=_models.SingleCollectionRequestPath(collection_uid=collection_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/collections/{collection_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/collections/{collection_uid}"
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

# Tags: Collections
@mcp.tool()
async def update_collection(
    collection_uid: str = Field(..., description="The unique identifier of the collection to update. This is a required path parameter that specifies which collection will be replaced."),
    postman_id: str | None = Field(None, description="The Postman internal identifier for the collection, typically a UUID format. Used to maintain collection identity across systems."),
    description: str | None = Field(None, description="A text description of the collection's purpose and contents. Supports dynamic variables in the format."),
    name: str | None = Field(None, description="The display name of the collection. Supports dynamic variables (e.g., {{$randomInt}}) for generating unique names."),
    item: list[_models.UpdateCollectionBodyCollectionItemItem] | None = Field(None, description="An array of request items and folders that comprise the collection. Items are processed in the order provided and define the collection's structure and endpoints."),
    schema_: str | None = Field(None, alias="schema"),
) -> dict[str, Any] | ToolResult:
    """Replace an existing collection with updated content in Postman Collection v2 format. Returns the updated collection's name, id, and uid. Requires API Key authentication."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCollectionRequest(
            path=_models.UpdateCollectionRequestPath(collection_uid=collection_uid),
            body=_models.UpdateCollectionRequestBody(collection=_models.UpdateCollectionRequestBodyCollection(item=item,
                    info=_models.UpdateCollectionRequestBodyCollectionInfo(postman_id=postman_id, description=description, name=name, schema_=schema_) if any(v is not None for v in [postman_id, description, name, schema_]) else None) if any(v is not None for v in [postman_id, description, name, item, schema_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/collections/{collection_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/collections/{collection_uid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_collection", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_collection",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Collections
@mcp.tool()
async def delete_collection(collection_uid: str = Field(..., description="The unique identifier of the collection to delete. This identifier is required to specify which collection should be removed.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a collection by its unique identifier. Returns the deleted collection's id and uid upon successful deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCollectionRequest(
            path=_models.DeleteCollectionRequestPath(collection_uid=collection_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_collection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/collections/{collection_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/collections/{collection_uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_collection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_collection", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_collection",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def list_environments() -> dict[str, Any] | ToolResult:
    """Retrieve a list of all environments you own, including their names, IDs, owners, and UIDs. Requires API Key authentication."""

    # Extract parameters for API call
    _http_path = "/environments"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_environments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_environments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_environments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def create_environment(
    name: str | None = Field(None, description="The name of the environment to create. Must be between 1 and 254 characters long."),
    values: list[_models.CreateEnvironmentBodyEnvironmentValuesItem] | None = Field(None, description="An array of environment variables to initialize with the environment. Each variable must have a key and value; the enabled flag is optional. Up to 100 variables can be specified per environment."),
) -> dict[str, Any] | ToolResult:
    """Create a new environment with configuration variables. Optionally specify a workspace context via query parameter. Returns the created environment's name and unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.CreateEnvironmentRequest(
            body=_models.CreateEnvironmentRequestBody(environment=_models.CreateEnvironmentRequestBodyEnvironment(name=name, values=values) if any(v is not None for v in [name, values]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/environments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_environment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_environment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_environment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def get_environment(environment_uid: str = Field(..., description="The unique identifier of the environment to retrieve. This is a required string value that identifies which environment's contents to access.")) -> dict[str, Any] | ToolResult:
    """Retrieve the full contents of a specific environment by its unique identifier. This operation requires authentication via API Key."""

    # Construct request model with validation
    try:
        _request = _models.SingleEnvironmentRequest(
            path=_models.SingleEnvironmentRequestPath(environment_uid=environment_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/environments/{environment_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/environments/{environment_uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_environment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_environment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_environment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def update_environment(
    environment_uid: str = Field(..., description="The unique identifier of the environment to update."),
    name: str | None = Field(None, description="The new name for the environment. Must be between 1 and 254 characters."),
    values: list[_models.UpdateEnvironmentBodyEnvironmentValuesItem] | None = Field(None, description="An array of environment variables (up to 100 items). Each variable must have a key and value (both 1-254 characters), and may optionally include a type and enabled status. Variables are applied in the order provided."),
) -> dict[str, Any] | ToolResult:
    """Replace an existing environment with updated configuration. Specify the environment to modify by its unique identifier and provide the new environment name and variable values."""

    # Construct request model with validation
    try:
        _request = _models.UpdateEnvironmentRequest(
            path=_models.UpdateEnvironmentRequestPath(environment_uid=environment_uid),
            body=_models.UpdateEnvironmentRequestBody(environment=_models.UpdateEnvironmentRequestBodyEnvironment(name=name, values=values) if any(v is not None for v in [name, values]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/environments/{environment_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/environments/{environment_uid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_environment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_environment", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_environment",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def delete_environment(environment_uid: str = Field(..., description="The unique identifier of the environment to delete. This is a required string value that uniquely identifies the environment within the system.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a single environment by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteEnvironmentRequest(
            path=_models.DeleteEnvironmentRequestPath(environment_uid=environment_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/environments/{environment_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/environments/{environment_uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_environment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_environment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_environment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User
@mcp.tool()
async def get_authenticated_user() -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about the authenticated user, including username, full name, email address, and other profile data. Requires API Key authentication via X-Api-Key header or apikey query parameter."""

    # Extract parameters for API call
    _http_path = "/me"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_authenticated_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_authenticated_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_authenticated_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Mocks
@mcp.tool()
async def list_mocks() -> dict[str, Any] | ToolResult:
    """Retrieve all mocks you have created. Returns a complete list of your mock configurations for managing and testing API responses."""

    # Extract parameters for API call
    _http_path = "/mocks"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_mocks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_mocks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_mocks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Mocks
@mcp.tool()
async def create_mock(
    collection: str | None = Field(None, description="The unique identifier of the collection for which to create the mock. Format is a UUID string."),
    environment: str | None = Field(None, description="The unique identifier of an environment to use for resolving variables within the collection. Format is a UUID string. If provided, environment variables will be substituted in the mock."),
) -> dict[str, Any] | ToolResult:
    """Create a mock server for a collection, optionally resolving environment variables. You can specify a workspace context via query parameter to determine where the mock is created."""

    # Construct request model with validation
    try:
        _request = _models.CreateMockRequest(
            body=_models.CreateMockRequestBody(mock=_models.CreateMockRequestBodyMock(collection=collection, environment=environment) if any(v is not None for v in [collection, environment]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_mock: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/mocks"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_mock")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_mock", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_mock",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Mocks
@mcp.tool()
async def get_mock(mock_uid: str = Field(..., description="The unique identifier of the mock to retrieve. This is a required string value that uniquely identifies the mock resource.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific mock by its unique identifier. Requires API Key authentication via X-Api-Key header or apikey query parameter."""

    # Construct request model with validation
    try:
        _request = _models.SingleMockRequest(
            path=_models.SingleMockRequestPath(mock_uid=mock_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_mock: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/mocks/{mock_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/mocks/{mock_uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_mock")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_mock", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_mock",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Mocks
@mcp.tool()
async def update_mock(
    mock_uid: str = Field(..., description="The unique identifier of the mock server to update."),
    description: str | None = Field(None, description="A descriptive text explaining the purpose or details of the mock server."),
    environment: str | None = Field(None, description="The unique identifier of the environment where this mock server operates."),
    name: str | None = Field(None, description="A human-readable name for the mock server."),
    private: bool | None = Field(None, description="Whether the mock server is private (true) or publicly accessible (false)."),
    version_tag: str | None = Field(None, alias="versionTag", description="The unique identifier of the version tag associated with this mock server."),
) -> dict[str, Any] | ToolResult:
    """Update an existing mock server by its unique identifier. Modify properties such as name, description, environment, privacy settings, and version tag."""

    # Construct request model with validation
    try:
        _request = _models.UpdateMockRequest(
            path=_models.UpdateMockRequestPath(mock_uid=mock_uid),
            body=_models.UpdateMockRequestBody(mock=_models.UpdateMockRequestBodyMock(description=description, environment=environment, name=name, private=private, version_tag=version_tag) if any(v is not None for v in [description, environment, name, private, version_tag]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_mock: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/mocks/{mock_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/mocks/{mock_uid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_mock")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_mock", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_mock",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Mocks
@mcp.tool()
async def delete_mock(mock_uid: str = Field(..., description="The unique identifier of the mock to delete. This is a required string value that identifies which mock should be removed.")) -> dict[str, Any] | ToolResult:
    """Permanently delete an existing mock by its unique identifier. This operation removes the mock and all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteMockRequest(
            path=_models.DeleteMockRequestPath(mock_uid=mock_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_mock: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/mocks/{mock_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/mocks/{mock_uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_mock")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_mock", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_mock",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Mocks
@mcp.tool()
async def publish_mock(mock_uid: str = Field(..., description="The unique identifier of the mock to publish. This is the uid assigned to the mock when it was created.")) -> dict[str, Any] | ToolResult:
    """Publishes a mock that you have created, making it available for use. Requires the mock's unique identifier (uid) and API key authentication."""

    # Construct request model with validation
    try:
        _request = _models.PublishMockRequest(
            path=_models.PublishMockRequestPath(mock_uid=mock_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for publish_mock: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/mocks/{mock_uid}/publish", _request.path.model_dump(by_alias=True)) if _request.path else "/mocks/{mock_uid}/publish"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("publish_mock")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("publish_mock", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="publish_mock",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Mocks
@mcp.tool()
async def delete_mock_publication(mock_uid: str = Field(..., description="The unique identifier of the mock to unpublish. This is a required string value that identifies which mock should be removed from published state.")) -> dict[str, Any] | ToolResult:
    """Unpublish a mock by its unique identifier. This removes the mock from published state, making it unavailable for use."""

    # Construct request model with validation
    try:
        _request = _models.UnpublishMockRequest(
            path=_models.UnpublishMockRequestPath(mock_uid=mock_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_mock_publication: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/mocks/{mock_uid}/unpublish", _request.path.model_dump(by_alias=True)) if _request.path else "/mocks/{mock_uid}/unpublish"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_mock_publication")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_mock_publication", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_mock_publication",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def list_monitors() -> dict[str, Any] | ToolResult:
    """Retrieve a list of all monitors accessible to you, including their name, ID, owner, and unique identifier. Requires API Key authentication."""

    # Extract parameters for API call
    _http_path = "/monitors"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_monitors")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_monitors", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_monitors",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def create_monitor(
    collection: str | None = Field(None, description="The unique identifier of the Postman collection to monitor. This collection contains the API tests that will be executed on schedule."),
    environment: str | None = Field(None, description="The unique identifier of the Postman environment to use when running the monitor. This provides variables and configuration for the collection execution."),
    name: str | None = Field(None, description="A descriptive name for the monitor to help identify it in your workspace."),
    cron: str | None = Field(None, description="A cron expression defining the monitor's execution schedule (e.g., '*/5 * * * *' for every 5 minutes, '0 17 * * *' for daily at 5pm). Only limited schedules are supported; check Postman Monitors for allowed values."),
    timezone_: str | None = Field(None, alias="timezone", description="The timezone for interpreting the cron schedule (e.g., 'Asia/Kolkata', 'America/New_York'). Use IANA timezone database format. Defaults to UTC if not specified."),
) -> dict[str, Any] | ToolResult:
    """Create a new monitor that runs API tests on a specified schedule. The monitor will execute a Postman collection in a given environment at intervals defined by a cron expression and timezone."""

    # Construct request model with validation
    try:
        _request = _models.CreateMonitorRequest(
            body=_models.CreateMonitorRequestBody(monitor=_models.CreateMonitorRequestBodyMonitor(collection=collection, environment=environment, name=name,
                    schedule=_models.CreateMonitorRequestBodyMonitorSchedule(cron=cron, timezone_=timezone_) if any(v is not None for v in [cron, timezone_]) else None) if any(v is not None for v in [collection, environment, name, cron, timezone_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_monitor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/monitors"
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

# Tags: Monitors
@mcp.tool()
async def get_monitor(monitor_uid: str = Field(..., description="The unique identifier of the monitor to retrieve. This is a required string value that uniquely identifies the monitor in the system.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific monitor using its unique identifier. This operation requires authentication via API key."""

    # Construct request model with validation
    try:
        _request = _models.SingleMonitorRequest(
            path=_models.SingleMonitorRequestPath(monitor_uid=monitor_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_monitor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/monitors/{monitor_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/monitors/{monitor_uid}"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Monitors
@mcp.tool()
async def update_monitor(
    monitor_uid: str = Field(..., description="The unique identifier of the monitor to update. This is a required path parameter that specifies which monitor will be modified."),
    name: str | None = Field(None, description="The new display name for the monitor. Use this to give the monitor a more descriptive or updated label."),
    cron: str | None = Field(None, description="A cron expression defining the monitor's execution schedule (e.g., `*/5 * * * *` for every 5 minutes, `0 17 * * *` for daily at 5pm). Only certain predefined schedules are supported—verify your desired frequency is available in Postman Monitors before use."),
    timezone_: str | None = Field(None, alias="timezone", description="The timezone for interpreting the cron schedule (e.g., `America/Chicago`). Use IANA timezone database identifiers to ensure the monitor runs at the intended local time."),
) -> dict[str, Any] | ToolResult:
    """Update an existing monitor's name and execution schedule. Modify the monitor identified by its unique identifier to change its display name and/or cron-based execution frequency and timezone."""

    # Construct request model with validation
    try:
        _request = _models.UpdateMonitorRequest(
            path=_models.UpdateMonitorRequestPath(monitor_uid=monitor_uid),
            body=_models.UpdateMonitorRequestBody(monitor=_models.UpdateMonitorRequestBodyMonitor(name=name,
                    schedule=_models.UpdateMonitorRequestBodyMonitorSchedule(cron=cron, timezone_=timezone_) if any(v is not None for v in [cron, timezone_]) else None) if any(v is not None for v in [name, cron, timezone_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_monitor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/monitors/{monitor_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/monitors/{monitor_uid}"
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

# Tags: Monitors
@mcp.tool()
async def delete_monitor(monitor_uid: str = Field(..., description="The unique identifier of the monitor to delete. This is a required string value that identifies which monitor to remove.")) -> dict[str, Any] | ToolResult:
    """Permanently delete an existing monitor by its unique identifier. This operation removes the monitor and all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteMonitorRequest(
            path=_models.DeleteMonitorRequestPath(monitor_uid=monitor_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_monitor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/monitors/{monitor_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/monitors/{monitor_uid}"
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

# Tags: Monitors
@mcp.tool()
async def run_monitor(monitor_uid: str = Field(..., description="The unique identifier of the monitor to execute.")) -> dict[str, Any] | ToolResult:
    """Executes a monitor immediately and waits for completion, returning the run results. This is a synchronous operation that blocks until the monitor finishes executing."""

    # Construct request model with validation
    try:
        _request = _models.RunAMonitorRequest(
            path=_models.RunAMonitorRequestPath(monitor_uid=monitor_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for run_monitor: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/monitors/{monitor_uid}/run", _request.path.model_dump(by_alias=True)) if _request.path else "/monitors/{monitor_uid}/run"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("run_monitor")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("run_monitor", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="run_monitor",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def create_webhook(
    workspace: str | None = Field(None, description="The workspace ID where the webhook will be created. Required to scope the webhook to the correct workspace context."),
    collection: str | None = Field(None, description="The ID of the collection that will be triggered when this webhook is invoked. This determines which collection executes when the webhook URL is called."),
    name: str | None = Field(None, description="A descriptive name for the webhook to help identify its purpose and distinguish it from other webhooks in your workspace."),
) -> dict[str, Any] | ToolResult:
    """Create a webhook that automatically triggers a specified collection when the webhook URL is called. The webhook URL is returned in the response for use in external systems."""

    # Construct request model with validation
    try:
        _request = _models.CreateWebhookRequest(
            query=_models.CreateWebhookRequestQuery(workspace=workspace),
            body=_models.CreateWebhookRequestBody(webhook=_models.CreateWebhookRequestBodyWebhook(collection=collection, name=name) if any(v is not None for v in [collection, name]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/webhooks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_webhook", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_webhook",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool()
async def list_workspaces() -> dict[str, Any] | ToolResult:
    """Retrieve a list of all workspaces accessible to you, including your own workspaces and those shared with you. Each workspace entry includes its name, ID, and type."""

    # Extract parameters for API call
    _http_path = "/workspaces"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspaces")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspaces", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspaces",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool()
async def create_workspace(
    collections_: list[_models.CreateWorkspaceBodyWorkspaceCollectionsItem] | None = Field(None, alias="collections", description="Array of collection UIDs to include in the workspace. Order is preserved as provided."),
    description: str | None = Field(None, description="A descriptive text for the workspace to explain its purpose or contents."),
    environments: list[_models.CreateWorkspaceBodyWorkspaceEnvironmentsItem] | None = Field(None, description="Array of environment UIDs to include in the workspace. Order is preserved as provided."),
    mocks: list[_models.CreateWorkspaceBodyWorkspaceMocksItem] | None = Field(None, description="Array of mock server UIDs to include in the workspace. Order is preserved as provided."),
    monitors: list[_models.CreateWorkspaceBodyWorkspaceMonitorsItem] | None = Field(None, description="Array of monitor UIDs to include in the workspace. Order is preserved as provided."),
    name: str | None = Field(None, description="The display name for the workspace. Use a descriptive name that identifies the workspace purpose or project."),
    type_: str | None = Field(None, alias="type", description="The workspace type, such as 'personal' for individual workspaces or other organizational types."),
) -> dict[str, Any] | ToolResult:
    """Create a new workspace and optionally populate it with collections, environments, mocks, and monitors by their unique identifiers. Returns the created workspace name and ID."""

    # Construct request model with validation
    try:
        _request = _models.CreateWorkspaceRequest(
            body=_models.CreateWorkspaceRequestBody(workspace=_models.CreateWorkspaceRequestBodyWorkspace(collections_=collections_, description=description, environments=environments, mocks=mocks, monitors=monitors, name=name, type_=type_) if any(v is not None for v in [collections_, description, environments, mocks, monitors, name, type_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_workspace: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/workspaces"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_workspace")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_workspace", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_workspace",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool()
async def get_workspace(workspace_id: str = Field(..., description="The unique identifier of the workspace to retrieve. Must be a valid workspace ID that you have access to.")) -> dict[str, Any] | ToolResult:
    """Retrieve a workspace by its ID, including all associated collections, environments, mocks, and monitors that you have access to."""

    # Construct request model with validation
    try:
        _request = _models.SingleWorkspaceRequest(
            path=_models.SingleWorkspaceRequestPath(workspace_id=workspace_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workspace: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workspace")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workspace", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workspace",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool()
async def update_workspace(
    workspace_id: str = Field(..., description="The unique identifier of the workspace to update."),
    collections_: list[_models.UpdateWorkspaceBodyWorkspaceCollectionsItem] | None = Field(None, alias="collections", description="Array of collection UIDs to associate with this workspace. Replaces all existing collections—only specified collections will remain associated after the update."),
    description: str | None = Field(None, description="A text description for the workspace to help identify its purpose or contents."),
    environments: list[_models.UpdateWorkspaceBodyWorkspaceEnvironmentsItem] | None = Field(None, description="Array of environment UIDs to associate with this workspace. Replaces all existing environments—only specified environments will remain associated after the update."),
    mocks: list[_models.UpdateWorkspaceBodyWorkspaceMocksItem] | None = Field(None, description="Array of mock UIDs to associate with this workspace. Replaces all existing mocks—only specified mocks will remain associated after the update."),
    monitors: list[_models.UpdateWorkspaceBodyWorkspaceMonitorsItem] | None = Field(None, description="Array of monitor UIDs to associate with this workspace. Replaces all existing monitors—only specified monitors will remain associated after the update."),
    name: str | None = Field(None, description="The display name for the workspace."),
) -> dict[str, Any] | ToolResult:
    """Update a workspace's properties and manage its associations with collections, environments, mocks, and monitors. The endpoint replaces all associated entities with those specified in the request, so omitted entities will be removed from the workspace."""

    # Construct request model with validation
    try:
        _request = _models.UpdateWorkspaceRequest(
            path=_models.UpdateWorkspaceRequestPath(workspace_id=workspace_id),
            body=_models.UpdateWorkspaceRequestBody(workspace=_models.UpdateWorkspaceRequestBodyWorkspace(collections_=collections_, description=description, environments=environments, mocks=mocks, monitors=monitors, name=name) if any(v is not None for v in [collections_, description, environments, mocks, monitors, name]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_workspace: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_workspace")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_workspace", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_workspace",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool()
async def delete_workspace(workspace_id: str = Field(..., description="The unique identifier of the workspace to delete. This ID is required to specify which workspace should be removed.")) -> dict[str, Any] | ToolResult:
    """Permanently delete an existing workspace by its ID. Returns the ID of the deleted workspace upon successful completion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWorkspaceRequest(
            path=_models.DeleteWorkspaceRequestPath(workspace_id=workspace_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_workspace: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_workspace")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_workspace", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_workspace",
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
        print("  python postman_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Postman MCP Server")

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
    logger.info("Starting Postman MCP Server")
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

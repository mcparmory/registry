#!/usr/bin/env python3
"""
Figma MCP Server

API Info:
- Terms of Service: https://www.figma.com/developer-terms/

Generated: 2026-05-05 14:55:51 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://api.figma.com")
SERVER_NAME = "Figma"
SERVER_VERSION = "1.0.5"

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
    'OAuth2',
    'OrgOAuth2',
    'PersonalAccessToken',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["OAuth2"] = _auth.OAuth2Auth()
    logging.info("Authentication configured: OAuth2")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for OAuth2 not configured: {error_msg}")
    _auth_handlers["OAuth2"] = None
try:
    _auth_handlers["OrgOAuth2"] = _auth.OrgOAuth2Auth()
    logging.info("Authentication configured: OrgOAuth2")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for OrgOAuth2 not configured: {error_msg}")
    _auth_handlers["OrgOAuth2"] = None
try:
    _auth_handlers["PersonalAccessToken"] = _auth.APIKeyAuth(env_var="API_KEY", location="header", param_name="X-Figma-Token")
    logging.info("Authentication configured: PersonalAccessToken")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for PersonalAccessToken not configured: {error_msg}")
    _auth_handlers["PersonalAccessToken"] = None

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

mcp = FastMCP("Figma", middleware=[_JsonCoercionMiddleware()])

# Tags: Files
@mcp.tool()
async def export_file_json(
    file_key: str = Field(..., description="The unique identifier of the file to export. Can be extracted from the Figma file URL (https://www.figma.com/file/{file_key}/{title}) or obtained as a branch key using the branch_data parameter."),
    ids: str | None = Field(None, description="Comma-separated list of node IDs to include in the export. When specified, returns only the requested nodes, their children, and ancestor chains. Top-level canvas nodes are always included regardless of this parameter."),
    depth: float | None = Field(None, description="Controls traversal depth into the document tree. A value of 1 returns only pages; 2 returns pages and top-level objects; omitting returns the entire tree."),
    geometry: str | None = Field(None, description="Set to include vector path data in the export for shape and vector nodes."),
    plugin_data: str | None = Field(None, description="Comma-separated list of plugin IDs and/or the string 'shared' to include plugin data written to the document. Plugin data will appear in pluginData and sharedPluginData properties."),
    branch_data: bool | None = Field(None, description="Include branch metadata in the response, showing the main file key if this is a branch, or branch metadata if the file has branches."),
) -> dict[str, Any] | ToolResult:
    """Export a Figma file as JSON, including document structure, components, and optional metadata. Supports partial exports by node ID and configurable depth traversal."""

    # Construct request model with validation
    try:
        _request = _models.GetFileRequest(
            path=_models.GetFileRequestPath(file_key=file_key),
            query=_models.GetFileRequestQuery(ids=ids, depth=depth, geometry=geometry, plugin_data=plugin_data, branch_data=branch_data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_file_json: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_file_json")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_file_json", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_file_json",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Files
@mcp.tool()
async def get_file_nodes(
    file_key: str = Field(..., description="The Figma file identifier to query. Can be either a file key or branch key (obtain branch key via GET /v1/files/:key with branch_data parameter)."),
    ids: str = Field(..., description="Comma-separated list of node IDs to retrieve. The API will return data for each specified node, though some values may be null if a node ID does not exist in the file."),
    depth: float | None = Field(None, description="How many levels deep to traverse the node tree from each specified node. A value of 1 returns only direct children; omitting this parameter returns the entire subtree."),
    geometry: str | None = Field(None, description="Include vector path data in the response. Set to 'paths' to export vector geometry; omit to exclude vector data."),
    plugin_data: str | None = Field(None, description="Comma-separated list of plugin IDs and/or the string 'shared' to include plugin data written to the document. Plugin data will be returned in pluginData and sharedPluginData properties."),
) -> dict[str, Any] | ToolResult:
    """Retrieve specific nodes from a Figma file as JSON objects. Extract node data by providing node IDs, with optional support for vector geometry, nested traversal depth, and plugin data."""

    # Construct request model with validation
    try:
        _request = _models.GetFileNodesRequest(
            path=_models.GetFileNodesRequestPath(file_key=file_key),
            query=_models.GetFileNodesRequestQuery(ids=ids, depth=depth, geometry=geometry, plugin_data=plugin_data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_nodes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/nodes", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/nodes"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_nodes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_nodes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_nodes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Files
@mcp.tool()
async def render_node_images(
    file_key: str = Field(..., description="The file to export images from. Accepts either a file key or branch key. Use GET /v1/files/:key with the branch_data query parameter to retrieve a branch key."),
    ids: str = Field(..., description="Comma-separated list of node IDs to render. Multiple node IDs can be specified to render multiple images from the same file."),
    scale: float | None = Field(None, description="Scaling factor for the rendered image. Values between 0.01 and 4 are supported, where 1.0 represents the original size.", ge=0.01, le=4),
    format_: Literal["jpg", "png", "svg", "pdf"] | None = Field(None, alias="format", description="Output format for the rendered image."),
    svg_include_id: bool | None = Field(None, description="Whether to include id attributes for all SVG elements. When enabled, adds the layer name to the id attribute of each SVG element."),
) -> dict[str, Any] | ToolResult:
    """Render images from specified nodes in a file. Returns a map of node IDs to image URLs, with null values indicating failed renders. Rendered images expire after 30 days."""

    # Construct request model with validation
    try:
        _request = _models.GetImagesRequest(
            path=_models.GetImagesRequestPath(file_key=file_key),
            query=_models.GetImagesRequestQuery(ids=ids, scale=scale, format_=format_, svg_include_id=svg_include_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for render_node_images: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/images/{file_key}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/images/{file_key}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("render_node_images")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("render_node_images", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="render_node_images",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Files
@mcp.tool()
async def list_image_fills(file_key: str = Field(..., description="The Figma file identifier to retrieve images from. Accepts either a file key or branch key; use GET /v1/files/:key with branch_data query parameter to obtain a branch key.")) -> dict[str, Any] | ToolResult:
    """Retrieve download URLs for all images used in image fills within a Figma document. Image URLs are valid for up to 14 days and can be located by their imageRef attribute in Paint objects from the file endpoint."""

    # Construct request model with validation
    try:
        _request = _models.GetImageFillsRequest(
            path=_models.GetImageFillsRequestPath(file_key=file_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_image_fills: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/images", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/images"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_image_fills")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_image_fills", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_image_fills",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Files
@mcp.tool()
async def get_file_metadata(file_key: str = Field(..., description="The unique identifier for the file or branch. Use a file key for standard file metadata or a branch key for branch-specific metadata.")) -> dict[str, Any] | ToolResult:
    """Retrieve metadata for a file or branch. Provide either a file key or branch key to access file information."""

    # Construct request model with validation
    try:
        _request = _models.GetFileMetaRequest(
            path=_models.GetFileMetaRequestPath(file_key=file_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/meta", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/meta"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_team_projects(team_id: str = Field(..., description="The unique identifier of the team. You can find the team ID in the URL of your team page, positioned after 'team' and before your team name.")) -> dict[str, Any] | ToolResult:
    """Retrieve all projects within a specified team that are visible to the authenticated user. Only projects accessible to the token owner or authenticated user will be returned."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamProjectsRequest(
            path=_models.GetTeamProjectsRequestPath(team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/teams/{team_id}/projects", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/teams/{team_id}/projects"
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
async def list_project_files(
    project_id: str = Field(..., description="The unique identifier of the project from which to retrieve files."),
    branch_data: bool | None = Field(None, description="Include branch metadata in the response for each main file that contains branches within the project."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all files within a specified project. Optionally include branch metadata for files that contain branches."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectFilesRequest(
            path=_models.GetProjectFilesRequestPath(project_id=project_id),
            query=_models.GetProjectFilesRequestQuery(branch_data=branch_data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_files: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/projects/{project_id}/files", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/projects/{project_id}/files"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_files")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_files", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_files",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Files
@mcp.tool()
async def list_file_versions(
    file_key: str = Field(..., description="The file or branch key identifying which file's version history to retrieve. Obtain the branch key using GET /v1/files/:key with the branch_data query parameter."),
    page_size: float | None = Field(None, description="Number of version records to return per page. Defaults to 30 if not specified.", le=50),
) -> dict[str, Any] | ToolResult:
    """Retrieve the version history of a file to see how it has evolved over time. Use the returned version information to render a specific version via another endpoint."""

    # Construct request model with validation
    try:
        _request = _models.GetFileVersionsRequest(
            path=_models.GetFileVersionsRequestPath(file_key=file_key),
            query=_models.GetFileVersionsRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_versions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/versions", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/versions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_versions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_versions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_versions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def list_file_comments(
    file_key: str = Field(..., description="The file or branch identifier to retrieve comments from. Use the file key for the main file, or obtain a branch key via GET /v1/files/:key with the branch_data query parameter to access comments on a specific branch."),
    as_md: bool | None = Field(None, description="When enabled, converts comments to their markdown equivalents where applicable for better formatting compatibility."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all comments left on a file. Supports both file keys and branch keys for accessing comments across different file versions."""

    # Construct request model with validation
    try:
        _request = _models.GetCommentsRequest(
            path=_models.GetCommentsRequestPath(file_key=file_key),
            query=_models.GetCommentsRequestQuery(as_md=as_md)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/comments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_comments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_comments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_comments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def add_file_comment(
    file_key: str = Field(..., description="The file identifier to add the comment to. Can be a file key or branch key; use GET /v1/files/:key with the branch_data query parameter to retrieve a branch key."),
    message: str = Field(..., description="The text content of the comment to post."),
    comment_id: str | None = Field(None, description="The ID of the root comment to reply to. Replies to replies are not supported; only root-level comments can be replied to."),
    client_meta: _models.Vector | _models.FrameOffset | _models.Region | _models.FrameOffsetRegion | None = Field(None, description="Metadata specifying the position or location where the comment should be placed within the file."),
) -> dict[str, Any] | ToolResult:
    """Posts a new comment on a file or replies to an existing root comment. Use the comment_id parameter to reply to a specific comment."""

    # Construct request model with validation
    try:
        _request = _models.PostCommentRequest(
            path=_models.PostCommentRequestPath(file_key=file_key),
            body=_models.PostCommentRequestBody(message=message, comment_id=comment_id, client_meta=client_meta)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_file_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/comments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_file_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_file_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_file_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def delete_comment(
    file_key: str = Field(..., description="The file or branch key identifying the file containing the comment. Retrieve the branch key using GET /v1/files/:key with the branch_data query parameter."),
    comment_id: str = Field(..., description="The unique identifier of the comment to delete."),
) -> dict[str, Any] | ToolResult:
    """Deletes a specific comment from a file. Only the comment author is permitted to delete their own comments."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCommentRequest(
            path=_models.DeleteCommentRequestPath(file_key=file_key, comment_id=comment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/comments/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/comments/{comment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_comment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_comment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comment Reactions
@mcp.tool()
async def list_comment_reactions(
    file_key: str = Field(..., description="The file identifier to retrieve the comment from. Can be either a file key or branch key; use `GET /v1/files/:key` with the `branch_data` query parameter to obtain a branch key if needed."),
    comment_id: str = Field(..., description="The unique identifier of the comment to retrieve reactions from."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of reactions left on a specific comment. Use this to see all emoji reactions and their authors for a given comment."""

    # Construct request model with validation
    try:
        _request = _models.GetCommentReactionsRequest(
            path=_models.GetCommentReactionsRequestPath(file_key=file_key, comment_id=comment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_comment_reactions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/comments/{comment_id}/reactions", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/comments/{comment_id}/reactions"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_comment_reactions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_comment_reactions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_comment_reactions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comment Reactions
@mcp.tool()
async def add_comment_reaction(
    file_key: str = Field(..., description="The file identifier to add the reaction to. Can be a file key or branch key; use GET /v1/files/:key with the branch_data query parameter to retrieve a branch key."),
    comment_id: str = Field(..., description="The unique identifier of the comment to react to."),
    emoji: str = Field(..., description="The emoji reaction as a shortcode format. Supports optional skin tone modifiers for applicable emoji. Valid shortcodes are defined in the emoji-mart native set."),
) -> dict[str, Any] | ToolResult:
    """Add an emoji reaction to a file comment. Reactions allow users to quickly respond to comments with emoji expressions."""

    # Construct request model with validation
    try:
        _request = _models.PostCommentReactionRequest(
            path=_models.PostCommentReactionRequestPath(file_key=file_key, comment_id=comment_id),
            body=_models.PostCommentReactionRequestBody(emoji=emoji)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_comment_reaction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/comments/{comment_id}/reactions", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/comments/{comment_id}/reactions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_comment_reaction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_comment_reaction", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_comment_reaction",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comment Reactions
@mcp.tool()
async def remove_comment_reaction(
    file_key: str = Field(..., description="The file or branch key containing the comment. Retrieve the branch key using GET /v1/files/:key with the branch_data query parameter."),
    comment_id: str = Field(..., description="The unique identifier of the comment from which to remove the reaction."),
    emoji: str = Field(..., description="The emoji reaction to remove, specified as a shortcode format. Skin tone modifiers are supported where applicable."),
) -> dict[str, Any] | ToolResult:
    """Remove a reaction from a comment. Only the user who added the reaction can delete it."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCommentReactionRequest(
            path=_models.DeleteCommentReactionRequestPath(file_key=file_key, comment_id=comment_id),
            query=_models.DeleteCommentReactionRequestQuery(emoji=emoji)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_comment_reaction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/comments/{comment_id}/reactions", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/comments/{comment_id}/reactions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_comment_reaction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_comment_reaction", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_comment_reaction",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def get_current_user() -> dict[str, Any] | ToolResult:
    """Retrieve the profile and account information for the currently authenticated user. This endpoint requires valid authentication credentials."""

    # Extract parameters for API call
    _http_path = "/v1/me"
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

# Tags: Components
@mcp.tool()
async def list_team_components(
    team_id: str = Field(..., description="The unique identifier of the team whose components you want to list."),
    page_size: float | None = Field(None, description="The number of components to return per page. Specify a value between 1 and 1000 to control result set size."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of published components available in a team's component library. Use pagination to manage large result sets efficiently."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamComponentsRequest(
            path=_models.GetTeamComponentsRequestPath(team_id=team_id),
            query=_models.GetTeamComponentsRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_components: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/teams/{team_id}/components", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/teams/{team_id}/components"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_team_components")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_team_components", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_team_components",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Components
@mcp.tool()
async def list_file_components(file_key: str = Field(..., description="The main file key identifying the file library to retrieve components from. Branch keys are not supported for this operation.")) -> dict[str, Any] | ToolResult:
    """Retrieve a list of published components available in a file library. Only main file keys are supported, as components cannot be published from branch files."""

    # Construct request model with validation
    try:
        _request = _models.GetFileComponentsRequest(
            path=_models.GetFileComponentsRequestPath(file_key=file_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_components: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/components", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/components"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_components")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_components", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_components",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Components
@mcp.tool()
async def get_component(key: str = Field(..., description="The unique identifier that uniquely identifies the component within the system.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed metadata for a specific component using its unique identifier. This operation returns comprehensive information about the component's configuration and properties."""

    # Construct request model with validation
    try:
        _request = _models.GetComponentRequest(
            path=_models.GetComponentRequestPath(key=key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_component: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/components/{key}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/components/{key}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_component")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_component", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_component",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Component Sets
@mcp.tool()
async def list_component_sets(
    team_id: str = Field(..., description="The unique identifier of the team whose component sets you want to retrieve."),
    page_size: float | None = Field(None, description="The number of component sets to return per page. Useful for controlling response size and implementing pagination."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of published component sets available in a team's library. Use pagination to manage large result sets efficiently."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamComponentSetsRequest(
            path=_models.GetTeamComponentSetsRequestPath(team_id=team_id),
            query=_models.GetTeamComponentSetsRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_component_sets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/teams/{team_id}/component_sets", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/teams/{team_id}/component_sets"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_component_sets")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_component_sets", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_component_sets",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Component Sets
@mcp.tool()
async def list_component_sets_file(file_key: str = Field(..., description="The main file key identifying the library file. Branch keys are not supported as component sets can only be published from main files.")) -> dict[str, Any] | ToolResult:
    """Retrieve all published component sets available in a file library. This operation requires a main file key and cannot be used with branch keys."""

    # Construct request model with validation
    try:
        _request = _models.GetFileComponentSetsRequest(
            path=_models.GetFileComponentSetsRequestPath(file_key=file_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_component_sets_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/component_sets", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/component_sets"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_component_sets_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_component_sets_file", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_component_sets_file",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Component Sets
@mcp.tool()
async def get_component_set(key: str = Field(..., description="The unique identifier that uniquely identifies the component set to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve metadata for a published component set using its unique identifier. Returns detailed information about the component set configuration and properties."""

    # Construct request model with validation
    try:
        _request = _models.GetComponentSetRequest(
            path=_models.GetComponentSetRequestPath(key=key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_component_set: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/component_sets/{key}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/component_sets/{key}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_component_set")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_component_set", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_component_set",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Styles
@mcp.tool()
async def list_team_styles(
    team_id: str = Field(..., description="The unique identifier of the team whose styles you want to retrieve."),
    page_size: float | None = Field(None, description="The number of styles to return per page. Adjust this value to control result set size."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of published styles from a team's design library. Use pagination to control the number of results returned per request."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamStylesRequest(
            path=_models.GetTeamStylesRequestPath(team_id=team_id),
            query=_models.GetTeamStylesRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_styles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/teams/{team_id}/styles", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/teams/{team_id}/styles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_team_styles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_team_styles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_team_styles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Styles
@mcp.tool()
async def list_file_styles(file_key: str = Field(..., description="The main file key containing the styles to retrieve. Branch keys are not supported since style publishing is only available for main files.")) -> dict[str, Any] | ToolResult:
    """Retrieve a list of published styles available in a file library. Styles can only be published from main files, not from branches."""

    # Construct request model with validation
    try:
        _request = _models.GetFileStylesRequest(
            path=_models.GetFileStylesRequestPath(file_key=file_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_styles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/styles", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/styles"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_styles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_styles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_styles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Styles
@mcp.tool()
async def get_style(key: str = Field(..., description="The unique identifier that references the specific style to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed metadata for a specific style using its unique identifier. Use this to fetch style configuration and properties."""

    # Construct request model with validation
    try:
        _request = _models.GetStyleRequest(
            path=_models.GetStyleRequestPath(key=key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_style: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/styles/{key}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/styles/{key}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_style")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_style", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_style",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def list_webhooks(
    context_id: str | None = Field(None, description="The unique identifier of the context to retrieve webhooks for. Cannot be used together with plan_api_id."),
    plan_api_id: str | None = Field(None, description="The unique identifier of your plan to retrieve all webhooks across all accessible contexts. Cannot be used together with context_id. Results are paginated when using this parameter."),
) -> dict[str, Any] | ToolResult:
    """Retrieve webhooks filtered by context or plan. Use context_id to get webhooks for a specific context, or plan_api_id to retrieve all webhooks across all accessible contexts with pagination support."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhooksRequest(
            query=_models.GetWebhooksRequestQuery(context_id=context_id, plan_api_id=plan_api_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/webhooks"
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

# Tags: Webhooks
@mcp.tool()
async def get_webhook(webhook_id: str = Field(..., description="The unique identifier of the webhook to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a webhook configuration by its ID. Use this to fetch details about a specific webhook including its URL, events, and status."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhookRequest(
            path=_models.GetWebhookRequestPath(webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v2/webhooks/{webhook_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v2/webhooks/{webhook_id}"
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

# Tags: Activity Logs
@mcp.tool()
async def list_activity_logs(
    events: str | None = Field(None, description="Filter results to include only specified event types. Accepts comma-separated values to include multiple event types; all events are returned if unspecified."),
    start_time: float | None = Field(None, description="Unix timestamp marking the start of the time range (inclusive). Defaults to one year ago if unspecified."),
    end_time: float | None = Field(None, description="Unix timestamp marking the end of the time range (inclusive). Defaults to the current timestamp if unspecified."),
    limit: float | None = Field(None, description="Maximum number of events to return in the response. Defaults to 1000 if unspecified."),
    order: Literal["asc", "desc"] | None = Field(None, description="Sort order for events by timestamp. Use ascending order to show oldest events first, or descending order to show newest events first."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of activity log events filtered by type, time range, and ordering. Useful for auditing, monitoring system changes, and tracking user actions."""

    # Construct request model with validation
    try:
        _request = _models.GetActivityLogsRequest(
            query=_models.GetActivityLogsRequestQuery(events=events, start_time=start_time, end_time=end_time, limit=limit, order=order)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_activity_logs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/activity_logs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_activity_logs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_activity_logs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_activity_logs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Payments
@mcp.tool()
async def list_payments(
    user_id: str | None = Field(None, description="The ID of the user whose payment information you want to retrieve. Obtain this by having the user authenticate via OAuth2 to the Figma REST API."),
    community_file_id: str | None = Field(None, description="The ID of the Community file to query. Find this in the file's Community page URL (the number after 'file/'). Provide exactly one of: community_file_id, plugin_id, or widget_id."),
    plugin_id: str | None = Field(None, description="The ID of the plugin to query. Find this in the plugin's manifest or Community page URL (the number after 'plugin/'). Provide exactly one of: community_file_id, plugin_id, or widget_id."),
    widget_id: str | None = Field(None, description="The ID of the widget to query. Find this in the widget's manifest or Community page URL (the number after 'widget/'). Provide exactly one of: community_file_id, plugin_id, or widget_id."),
) -> dict[str, Any] | ToolResult:
    """Retrieve payment information for a user on a specific Community file, plugin, or widget. You can only query resources that you own."""

    # Construct request model with validation
    try:
        _request = _models.GetPaymentsRequest(
            query=_models.GetPaymentsRequestQuery(user_id=user_id, community_file_id=community_file_id, plugin_id=plugin_id, widget_id=widget_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_payments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/payments"
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

# Tags: Variables
@mcp.tool()
async def list_local_variables(file_key: str = Field(..., description="The file or branch identifier to retrieve variables from. Use the branch key obtained from GET /v1/files/:key with the branch_data query parameter to access branch-specific variables.")) -> dict[str, Any] | ToolResult:
    """Retrieve all local variables created in a file and remote variables referenced within it. This operation is restricted to full members of Enterprise organizations and supports examining variable modes and bound variable details."""

    # Construct request model with validation
    try:
        _request = _models.GetLocalVariablesRequest(
            path=_models.GetLocalVariablesRequestPath(file_key=file_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_local_variables: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/variables/local", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/variables/local"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_local_variables")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_local_variables", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_local_variables",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Variables
@mcp.tool()
async def list_published_variables(file_key: str = Field(..., description="The main file key to retrieve published variables from. Branch keys are not supported as variables cannot be published from branches.")) -> dict[str, Any] | ToolResult:
    """Retrieve all variables published from a file, including their subscription IDs and last published timestamps. Available only to full members of Enterprise organizations."""

    # Construct request model with validation
    try:
        _request = _models.GetPublishedVariablesRequest(
            path=_models.GetPublishedVariablesRequestPath(file_key=file_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_published_variables: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/variables/published", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/variables/published"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_published_variables")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_published_variables", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_published_variables",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Variables
@mcp.tool()
async def bulk_modify_variables(
    file_key: str = Field(..., description="The file to modify variables in. Can be a file key or branch key obtained from GET /v1/files/:key with the branch_data query parameter."),
    variable_collections: list[_models.VariableCollectionChange] | None = Field(None, alias="variableCollections", description="Array of variable collection objects to create, update, or delete. Each object must include an action property (create, update, or delete). Processed first in the request."),
    variable_modes: list[_models.VariableModeChange] | None = Field(None, alias="variableModes", description="Array of variable mode objects to create, update, or delete within collections. Each collection supports a maximum of 40 modes with names up to 40 characters. Processed second in the request."),
    variables: list[_models.VariableChange] | None = Field(None, description="Array of variable objects to create, update, or delete. Each collection supports a maximum of 5000 variables. Variable names must be unique within a collection and cannot contain special characters such as . { }. Processed third in the request."),
    variable_mode_values: list[_models.VariableModeValue] | None = Field(None, alias="variableModeValues", description="Array of variable mode value assignments to set specific values for variables under particular modes. Variables cannot be aliased to themselves or form alias cycles. Processed last in the request."),
) -> dict[str, Any] | ToolResult:
    """Bulk create, update, and delete variables, variable collections, modes, and mode values in a file. Changes are applied atomically in a defined order: collections, then modes, then variables, then mode values."""

    # Construct request model with validation
    try:
        _request = _models.PostVariablesRequest(
            path=_models.PostVariablesRequestPath(file_key=file_key),
            body=_models.PostVariablesRequestBody(variable_collections=variable_collections, variable_modes=variable_modes, variables=variables, variable_mode_values=variable_mode_values)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_modify_variables: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/variables", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/variables"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_modify_variables")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_modify_variables", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_modify_variables",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dev Resources
@mcp.tool()
async def list_dev_resources(
    file_key: str = Field(..., description="The main file key to retrieve dev resources from. Branch keys are not supported."),
    node_ids: str | None = Field(None, description="Comma-separated list of node identifiers to filter results. When specified, only dev resources attached to these nodes are returned. Omit to retrieve all dev resources in the file."),
) -> dict[str, Any] | ToolResult:
    """Retrieve development resources associated with a file. Optionally filter results to specific nodes within the file."""

    # Construct request model with validation
    try:
        _request = _models.GetDevResourcesRequest(
            path=_models.GetDevResourcesRequestPath(file_key=file_key),
            query=_models.GetDevResourcesRequestQuery(node_ids=node_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dev_resources: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/dev_resources", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/dev_resources"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dev_resources")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dev_resources", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dev_resources",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dev Resources
@mcp.tool()
async def create_dev_resources(dev_resources: list[_models.PostDevResourcesBodyDevResourcesItem] = Field(..., description="An array of dev resource objects to create. Each resource must reference a valid file_key, have a unique URL per node, and not exceed the 10 dev resource limit per node.")) -> dict[str, Any] | ToolResult:
    """Bulk create dev resources across multiple files. Successfully created resources are returned in the links_created array, while any resources that fail validation appear in the errors array with failure reasons."""

    # Construct request model with validation
    try:
        _request = _models.PostDevResourcesRequest(
            body=_models.PostDevResourcesRequestBody(dev_resources=dev_resources)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_dev_resources: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/dev_resources"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_dev_resources")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_dev_resources", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_dev_resources",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dev Resources
@mcp.tool()
async def update_dev_resources(dev_resources: list[_models.PutDevResourcesBodyDevResourcesItem] = Field(..., description="An array of dev resource objects to update. Each resource in the array will be processed, and results will be returned indicating which resources were successfully updated and which encountered errors.")) -> dict[str, Any] | ToolResult:
    """Bulk update dev resources across multiple files. Successfully updated resource IDs are returned in the response, while any resources that fail to update are included in an errors array."""

    # Construct request model with validation
    try:
        _request = _models.PutDevResourcesRequest(
            body=_models.PutDevResourcesRequestBody(dev_resources=dev_resources)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_dev_resources: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/dev_resources"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_dev_resources")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_dev_resources", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_dev_resources",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dev Resources
@mcp.tool()
async def remove_dev_resource(
    file_key: str = Field(..., description="The main file key containing the dev resource to delete. Must be a main file key, not a branch key."),
    dev_resource_id: str = Field(..., description="The unique identifier of the dev resource to delete."),
) -> dict[str, Any] | ToolResult:
    """Remove a dev resource from a file. This operation permanently deletes the specified dev resource and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDevResourceRequest(
            path=_models.DeleteDevResourceRequestPath(file_key=file_key, dev_resource_id=dev_resource_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_dev_resource: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/files/{file_key}/dev_resources/{dev_resource_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/files/{file_key}/dev_resources/{dev_resource_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_dev_resource")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_dev_resource", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_dev_resource",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Library Analytics
@mcp.tool()
async def list_library_component_actions(
    file_key: str = Field(..., description="The unique identifier of the library file for which to retrieve analytics data."),
    group_by: Literal["component", "team"] = Field(..., description="The dimension by which to aggregate the returned analytics data."),
    start_date: str | None = Field(None, description="The earliest week to include in the analytics results, specified as an ISO 8601 date. The date will be rounded back to the nearest start of a week. Defaults to one year prior to the end date."),
    end_date: str | None = Field(None, description="The latest week to include in the analytics results, specified as an ISO 8601 date. The date will be rounded forward to the nearest end of a week. Defaults to the most recently computed week."),
) -> dict[str, Any] | ToolResult:
    """Retrieve analytics data for component actions within a library, aggregated by the specified dimension (component or team). Use this to analyze usage patterns and activity metrics across your design library."""

    # Construct request model with validation
    try:
        _request = _models.GetLibraryAnalyticsComponentActionsRequest(
            path=_models.GetLibraryAnalyticsComponentActionsRequestPath(file_key=file_key),
            query=_models.GetLibraryAnalyticsComponentActionsRequestQuery(group_by=group_by, start_date=start_date, end_date=end_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_library_component_actions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/analytics/libraries/{file_key}/component/actions", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/analytics/libraries/{file_key}/component/actions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_library_component_actions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_library_component_actions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_library_component_actions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Library Analytics
@mcp.tool()
async def list_library_component_usages(
    file_key: str = Field(..., description="The unique identifier of the library file for which to retrieve component usage analytics."),
    group_by: Literal["component", "file"] = Field(..., description="The dimension by which to group the returned usage analytics data."),
) -> dict[str, Any] | ToolResult:
    """Retrieves analytics data on how components from a library are being used, with results grouped by the specified dimension (component or file)."""

    # Construct request model with validation
    try:
        _request = _models.GetLibraryAnalyticsComponentUsagesRequest(
            path=_models.GetLibraryAnalyticsComponentUsagesRequestPath(file_key=file_key),
            query=_models.GetLibraryAnalyticsComponentUsagesRequestQuery(group_by=group_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_library_component_usages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/analytics/libraries/{file_key}/component/usages", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/analytics/libraries/{file_key}/component/usages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_library_component_usages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_library_component_usages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_library_component_usages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Library Analytics
@mcp.tool()
async def list_library_style_actions(
    file_key: str = Field(..., description="The unique identifier of the library for which to fetch style action analytics."),
    group_by: Literal["style", "team"] = Field(..., description="The dimension to group analytics results by. Choose 'style' to aggregate by individual styles or 'team' to aggregate by team."),
    start_date: str | None = Field(None, description="The earliest week to include in results, specified as an ISO 8601 date. The date will be rounded back to the nearest week start. Defaults to one year prior to the end date."),
    end_date: str | None = Field(None, description="The latest week to include in results, specified as an ISO 8601 date. The date will be rounded forward to the nearest week end. Defaults to the most recently computed week."),
) -> dict[str, Any] | ToolResult:
    """Retrieve analytics data for style actions in a library, aggregated by the specified dimension (style or team). Use date parameters to filter results to a specific time range."""

    # Construct request model with validation
    try:
        _request = _models.GetLibraryAnalyticsStyleActionsRequest(
            path=_models.GetLibraryAnalyticsStyleActionsRequestPath(file_key=file_key),
            query=_models.GetLibraryAnalyticsStyleActionsRequestQuery(group_by=group_by, start_date=start_date, end_date=end_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_library_style_actions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/analytics/libraries/{file_key}/style/actions", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/analytics/libraries/{file_key}/style/actions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_library_style_actions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_library_style_actions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_library_style_actions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Library Analytics
@mcp.tool()
async def list_library_style_usages(
    file_key: str = Field(..., description="The unique identifier of the library file for which to retrieve style usage analytics."),
    group_by: Literal["style", "file"] = Field(..., description="The dimension by which to group the returned analytics data. Choose 'style' to see usage broken down by individual styles, or 'file' to see usage broken down by the files that consume those styles."),
) -> dict[str, Any] | ToolResult:
    """Retrieves analytics data on how styles are used within a library, aggregated by the specified dimension (style or file). Use this to understand style adoption and usage patterns across your design library."""

    # Construct request model with validation
    try:
        _request = _models.GetLibraryAnalyticsStyleUsagesRequest(
            path=_models.GetLibraryAnalyticsStyleUsagesRequestPath(file_key=file_key),
            query=_models.GetLibraryAnalyticsStyleUsagesRequestQuery(group_by=group_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_library_style_usages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/analytics/libraries/{file_key}/style/usages", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/analytics/libraries/{file_key}/style/usages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_library_style_usages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_library_style_usages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_library_style_usages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Library Analytics
@mcp.tool()
async def list_library_variable_actions(
    file_key: str = Field(..., description="The unique identifier of the library for which to fetch variable action analytics."),
    group_by: Literal["variable", "team"] = Field(..., description="The dimension by which to group the returned analytics data."),
    start_date: str | None = Field(None, description="ISO 8601 date marking the start of the analytics period. Dates are rounded back to the nearest week start. Defaults to one year prior to the end date."),
    end_date: str | None = Field(None, description="ISO 8601 date marking the end of the analytics period. Dates are rounded forward to the nearest week end. Defaults to the latest computed week."),
) -> dict[str, Any] | ToolResult:
    """Retrieve analytics data for variable actions within a library, aggregated by the specified dimension (variable or team). Use date parameters to filter results to a specific time range."""

    # Construct request model with validation
    try:
        _request = _models.GetLibraryAnalyticsVariableActionsRequest(
            path=_models.GetLibraryAnalyticsVariableActionsRequestPath(file_key=file_key),
            query=_models.GetLibraryAnalyticsVariableActionsRequestQuery(group_by=group_by, start_date=start_date, end_date=end_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_library_variable_actions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/analytics/libraries/{file_key}/variable/actions", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/analytics/libraries/{file_key}/variable/actions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_library_variable_actions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_library_variable_actions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_library_variable_actions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Library Analytics
@mcp.tool()
async def list_library_variable_usages(
    file_key: str = Field(..., description="The unique identifier of the library file for which to retrieve variable usage analytics."),
    group_by: Literal["variable", "file"] = Field(..., description="The dimension by which to aggregate the returned variable usage data. Choose 'variable' to group by individual variables, or 'file' to group by source files."),
) -> dict[str, Any] | ToolResult:
    """Retrieves analytics data on how variables are used within a library, aggregated by the specified dimension (variable or file). Use this to understand variable usage patterns and dependencies."""

    # Construct request model with validation
    try:
        _request = _models.GetLibraryAnalyticsVariableUsagesRequest(
            path=_models.GetLibraryAnalyticsVariableUsagesRequestPath(file_key=file_key),
            query=_models.GetLibraryAnalyticsVariableUsagesRequestQuery(group_by=group_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_library_variable_usages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/analytics/libraries/{file_key}/variable/usages", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/analytics/libraries/{file_key}/variable/usages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_library_variable_usages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_library_variable_usages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_library_variable_usages",
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
        print("  python figma_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Figma MCP Server")

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
    logger.info("Starting Figma MCP Server")
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

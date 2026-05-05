#!/usr/bin/env python3
"""
Ragie MCP Server
Generated: 2026-05-05 16:03:55 UTC
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
from typing import Annotated, Any, Literal, cast

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

BASE_URL = os.getenv("BASE_URL", "https://api.ragie.ai")
SERVER_NAME = "Ragie"
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
    'auth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["auth"] = _auth.BearerTokenAuth(env_var="BEARER_TOKEN", token_format="Bearer")
    logging.info("Authentication configured: auth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for auth not configured: {error_msg}")
    _auth_handlers["auth"] = None

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

mcp = FastMCP("Ragie", middleware=[_JsonCoercionMiddleware()])

# Tags: documents
@mcp.tool()
async def list_documents(
    page_size: int | None = Field(None, description="Number of documents to return per page. Must be between 1 and 100 items. Defaults to 10 if not specified.", ge=1, le=100),
    filter_: str | None = Field(None, alias="filter", description="Metadata filter expression to narrow results. Supports operators like $eq (equal), $ne (not equal), $gt/$gte (greater than), $lt/$lte (less than), $in/$nin (array membership), and logical AND/OR combinations. See documentation for syntax and examples."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of all documents sorted by creation date (newest first). Use the page_size parameter to control results per page and the filter parameter to search by metadata. When more results are available, a cursor will be provided for fetching the next page."""

    # Construct request model with validation
    try:
        _request = _models.ListDocumentsRequest(
            query=_models.ListDocumentsRequestQuery(page_size=page_size, filter_=filter_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_documents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_documents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_documents", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_documents",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def create_document(
    file_: str = Field(..., alias="file", description="The binary file to upload and index. Supported formats include plain text (.txt, .md, .json, .html, .xml, .eml, .msg, .rst, .rtf), images (.png, .jpg, .jpeg, .webp, .tiff, .bmp, .heic), and documents (.pdf, .docx, .xlsx, .pptx, .csv, .epub, and others). PDF files exceeding 2000 pages are not supported in hi_res mode."),
    mode: _models.CreateDocumentBodyMode | None = Field(None, description="Processing mode configuration for document ingestion. Accepts either an object with detailed mode settings or a scalar shorthand value."),
    metadata: dict[str, str | float | bool | list[str]] | None = Field(None, description="Custom metadata key-value pairs to attach to the document. Keys must be strings; values can be strings, numbers (integers or floats), booleans, or lists of strings. Up to 1000 total values are allowed across all metadata (each array item counts separately). Reserved keys like document_id, document_type, document_source, document_name, document_uploaded_at, start_time, end_time, and chunk_content_type are for internal use only."),
    external_id: str | None = Field(None, description="Optional external identifier for the document, such as an ID from an external system or the source URL where the file originates."),
    name: str | None = Field(None, description="Optional display name for the document. If provided, this name will be used; otherwise, the uploaded file's name will be used as the document name."),
    workflow: Literal["parse", "index"] | None = Field(None, description="Processing workflow to apply to the document. Choose 'parse' for document parsing or 'index' for indexing operations."),
) -> dict[str, Any] | ToolResult:
    """Upload and ingest a document for processing and retrieval. The document progresses through multiple processing stages (pending → partitioning → indexed → ready) and becomes available for retrieval once it reaches the ready state."""

    # Construct request model with validation
    try:
        _request = _models.CreateDocumentRequest(
            body=_models.CreateDocumentRequestBody(mode=mode, metadata=metadata, file_=file_, external_id=external_id, name=name, workflow=workflow)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def create_document_from_text(
    data: str | dict[str, Any] = Field(..., description="The document content as raw text or JSON. Must contain at least 1 character.", min_length=1),
    name: str | None = Field(None, description="Optional human-readable name for the document. If not provided, defaults to the current timestamp."),
    metadata: dict[str, str | int | float | bool | list[str]] | None = Field(None, description="Optional key-value metadata to attach to the document. Keys must be strings; values can be strings, numbers, booleans, or lists of strings. Up to 1000 total values are allowed (each array item counts separately). Reserved keys like document_id, document_type, and document_source are for internal use only."),
    external_id: str | None = Field(None, description="Optional external identifier for cross-referencing with other systems, such as a database ID or source URL."),
    workflow: Literal["parse", "index"] | None = Field(None, description="Optional processing stage to stop at. Use 'parse' to extract elements only, or 'index' (or omit) to run the full processing pipeline including chunking and indexing."),
) -> dict[str, Any] | ToolResult:
    """Ingest a document as raw text for processing through an automated pipeline. The document progresses through multiple stages (pending → partitioning → indexed → ready) and becomes available for retrieval once it reaches the ready state."""

    # Construct request model with validation
    try:
        _request = _models.CreateDocumentRawRequest(
            body=_models.CreateDocumentRawRequestBody(name=name, metadata=metadata, external_id=external_id, workflow=workflow, data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_document_from_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents/raw"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_document_from_text")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_document_from_text", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_document_from_text",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def ingest_document_from_url(
    url: str = Field(..., description="URL of the file to ingest. Must be publicly accessible via HTTP or HTTPS, between 1 and 2083 characters in length, and a valid URI format.", min_length=1, max_length=2083),
    name: str | None = Field(None, description="Optional human-readable name for the document. If not provided, a default name will be assigned."),
    metadata: dict[str, str | int | float | bool | list[str]] | None = Field(None, description="Optional key-value metadata to attach to the document. Keys must be strings; values can be strings, numbers, booleans, or lists of strings. Up to 1000 total values are allowed (each array item counts separately). Reserved keys like `document_id`, `document_type`, and `document_source` are for internal use only."),
    mode: Literal["hi_res", "fast", "agentic_ocr"] | _models.MediaModeParam | None = Field(None, description="Partition strategy controlling how the document is processed. For text documents, use `'hi_res'` to extract images and tables (slower, ~20x), or `'fast'` for text only. For audio/video, specify processing preferences as a JSON object with keys like `'static'` (text), `'audio'`, and `'video'`. Use `'all'` for highest quality across all media types, or `'agentic_ocr'` for vision-model-based extraction (early access)."),
    external_id: str | None = Field(None, description="Optional external identifier for the document, such as an ID from an external system or the source URL where the file originates."),
    workflow: Literal["parse", "index"] | None = Field(None, description="Optional processing stage to stop at. Set to `'parse'` to extract elements only, or `'index'` (default) to complete the full processing pipeline including indexing and summarization."),
) -> dict[str, Any] | ToolResult:
    """Ingest a document from a publicly accessible URL for processing and retrieval. The document progresses through multiple processing stages (pending → partitioning → indexed → ready) before becoming available for retrieval, with optional extraction of images, tables, and media content based on the selected partition strategy."""

    # Construct request model with validation
    try:
        _request = _models.CreateDocumentFromUrlRequest(
            body=_models.CreateDocumentFromUrlRequestBody(name=name, metadata=metadata, mode=mode, external_id=external_id, workflow=workflow, url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for ingest_document_from_url: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/documents/url"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("ingest_document_from_url")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("ingest_document_from_url", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="ingest_document_from_url",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def get_document(document_id: str = Field(..., description="The unique identifier of the document to retrieve, formatted as a UUID (universally unique identifier).")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific document by its unique identifier. Returns the full document details including metadata and content."""

    # Construct request model with validation
    try:
        _request = _models.GetDocumentRequest(
            path=_models.GetDocumentRequestPath(document_id=document_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/documents/{document_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/documents/{document_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_document", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_document",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def delete_document(
    document_id: str = Field(..., description="The unique identifier of the document to delete, formatted as a UUID."),
    async_: bool | None = Field(None, alias="async", description="When true, the deletion is performed asynchronously and returns immediately without waiting for completion. Defaults to false for synchronous deletion."),
) -> dict[str, Any] | ToolResult:
    """Permanently delete a document by its unique identifier. Supports both synchronous and asynchronous deletion modes."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDocumentRequest(
            path=_models.DeleteDocumentRequestPath(document_id=document_id),
            query=_models.DeleteDocumentRequestQuery(async_=async_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/documents/{document_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/documents/{document_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_document", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_document",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def update_document_file(
    document_id: str = Field(..., description="The unique identifier of the document to update, formatted as a UUID."),
    file_: str = Field(..., alias="file", description="The binary file to upload and process. Supported formats include text files (.txt, .md, .json, .html, .xml, .eml, .msg, .rst, .rtf), images (.png, .jpg, .jpeg, .webp, .tiff, .bmp, .heic), and documents (.pdf, .doc, .docx, .xlsx, .xls, .csv, .ppt, .pptx, .epub, .odt, .tsv). PDF files must not exceed 2000 pages."),
    mode: _models.UpdateDocumentFileBodyMode | None = Field(None, description="Optional processing mode configuration that controls how the file is extracted and indexed. Accepts either an object with detailed settings or a scalar shorthand value."),
) -> dict[str, Any] | ToolResult:
    """Replace the file content of an existing document. The uploaded file will be extracted, processed, and indexed for retrieval. Supports text formats (plain text, markdown, email, HTML, XML, JSON, RST, RTF), images (PNG, WebP, JPEG, TIFF, BMP, HEIC), and documents (PDF, Word, Excel, PowerPoint, CSV, EPUB, ODT)."""

    # Construct request model with validation
    try:
        _request = _models.UpdateDocumentFileRequest(
            path=_models.UpdateDocumentFileRequestPath(document_id=document_id),
            body=_models.UpdateDocumentFileRequestBody(mode=mode, file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_document_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/documents/{document_id}/file", _request.path.model_dump(by_alias=True)) if _request.path else "/documents/{document_id}/file"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_document_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_document_file", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_document_file",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def update_document_raw(
    document_id: str = Field(..., description="The unique identifier of the document to update, formatted as a UUID."),
    data: str | dict[str, Any] = Field(..., description="The new document content as text or JSON. Must contain at least one character.", min_length=1),
) -> dict[str, Any] | ToolResult:
    """Replace the raw content of an existing document with new text or JSON data. This operation overwrites the entire document content."""

    # Construct request model with validation
    try:
        _request = _models.UpdateDocumentRawRequest(
            path=_models.UpdateDocumentRawRequestPath(document_id=document_id),
            body=_models.UpdateDocumentRawRequestBody(data=data)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_document_raw: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/documents/{document_id}/raw", _request.path.model_dump(by_alias=True)) if _request.path else "/documents/{document_id}/raw"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_document_raw")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_document_raw", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_document_raw",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def update_document_from_url(
    document_id: str = Field(..., description="The unique identifier of the document to update, formatted as a UUID."),
    url: str = Field(..., description="Public HTTP or HTTPS URL of the file to ingest. Must be publicly accessible and between 1 and 2083 characters in length.", min_length=1, max_length=2083),
    mode: Literal["hi_res", "fast", "agentic_ocr"] | _models.MediaModeParam | None = Field(None, description="Processing strategy for document ingestion. For text documents, use 'hi_res' to extract images and tables (slower, ~20x) or 'fast' for text-only extraction. For audio, use true/false to enable processing. For video, use 'audio_only', 'video_only', or 'audio_video'. For mixed media, provide a JSON object with keys 'static' (text), 'audio' (boolean), and/or 'video' (strategy). Use 'all' for highest quality across all media types. Defaults to 'fast'."),
) -> dict[str, Any] | ToolResult:
    """Update a document by ingesting content from a publicly accessible URL. The document progresses through multiple processing states (pending → indexed → ready) before becoming available for retrieval, with optional high-resolution processing for extracting images and tables."""

    # Construct request model with validation
    try:
        _request = _models.UpdateDocumentFromUrlRequest(
            path=_models.UpdateDocumentFromUrlRequestPath(document_id=document_id),
            body=_models.UpdateDocumentFromUrlRequestBody(mode=mode, url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_document_from_url: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/documents/{document_id}/url", _request.path.model_dump(by_alias=True)) if _request.path else "/documents/{document_id}/url"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_document_from_url")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_document_from_url", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_document_from_url",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def update_document_metadata(
    document_id: str = Field(..., description="The UUID identifier of the document to update."),
    metadata: dict[str, Any] = Field(..., description="A partial metadata object with string keys and values that are strings, numbers, booleans, or lists of strings. Set a key to null to delete it. Up to 1000 total values are allowed across all metadata (each array item counts separately). Numbers are converted to 64-bit floating point."),
    async_: bool | None = Field(None, alias="async", description="If true, the update runs asynchronously in the background and returns a 202 response; if false (default), it runs synchronously and returns a 200 response."),
) -> dict[str, Any] | ToolResult:
    """Partially update a document's metadata with new or modified key-value pairs. Reserved keys (document_id, document_type, document_source, document_name, document_uploaded_at) cannot be modified. For connection-managed documents, updates create a metadata overlay applied on each sync."""

    # Construct request model with validation
    try:
        _request = _models.PatchDocumentMetadataRequest(
            path=_models.PatchDocumentMetadataRequestPath(document_id=document_id),
            body=_models.PatchDocumentMetadataRequestBody(metadata=metadata, async_=async_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_document_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/documents/{document_id}/metadata", _request.path.model_dump(by_alias=True)) if _request.path else "/documents/{document_id}/metadata"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_document_metadata")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_document_metadata", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_document_metadata",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def list_document_chunks(
    document_id: str = Field(..., description="The unique identifier (UUID) of the document to retrieve chunks from."),
    start_index: int | None = Field(None, description="The inclusive starting index for filtering chunks by range. If specified alone, returns only the chunk at this index. If both start_index and end_index are omitted, all chunks are returned without index filtering."),
    end_index: int | None = Field(None, description="The inclusive ending index for filtering chunks by range. If specified alone, returns only the chunk at this index. If both start_index and end_index are omitted, all chunks are returned without index filtering."),
    page_size: int | None = Field(None, description="Number of chunks to return per page, between 1 and 100 (defaults to 10). Use this with the cursor parameter to control pagination.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieve all chunks from a document, sorted by index in ascending order. Results are paginated with a maximum of 100 chunks per page; use the cursor parameter to fetch subsequent pages. Documents created before September 18, 2024 that haven't been updated may have chunks with index -1, sorted by ID instead."""

    # Construct request model with validation
    try:
        _request = _models.GetDocumentChunksRequest(
            path=_models.GetDocumentChunksRequestPath(document_id=document_id),
            query=_models.GetDocumentChunksRequestQuery(start_index=start_index, end_index=end_index, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_document_chunks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/documents/{document_id}/chunks", _request.path.model_dump(by_alias=True)) if _request.path else "/documents/{document_id}/chunks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_document_chunks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_document_chunks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_document_chunks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def get_document_chunk(
    document_id: str = Field(..., description="The unique identifier of the document containing the chunk, formatted as a UUID."),
    chunk_id: str = Field(..., description="The unique identifier of the specific chunk to retrieve, formatted as a UUID."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific chunk from a document using both the document ID and chunk ID. Use this to fetch individual content segments within a larger document."""

    # Construct request model with validation
    try:
        _request = _models.GetDocumentChunkRequest(
            path=_models.GetDocumentChunkRequestPath(document_id=document_id, chunk_id=chunk_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_document_chunk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/documents/{document_id}/chunks/{chunk_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/documents/{document_id}/chunks/{chunk_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_document_chunk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_document_chunk", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_document_chunk",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def get_document_chunk_content(
    document_id: str = Field(..., description="The unique identifier (UUID) of the document containing the chunk."),
    chunk_id: str = Field(..., description="The unique identifier (UUID) of the specific chunk within the document."),
    media_type: Literal["text/plain", "audio/mpeg", "video/mp4", "image/webp", "image/heic", "image/bmp", "image/png", "image/jpeg", "image/tiff"] | None = Field(None, description="The desired format for the returned content as a MIME type (e.g., text/plain, audio/mpeg, video/mp4, or various image formats). The requested format must be supported by the document type, or an error will be returned."),
    download: bool | None = Field(None, description="Whether to return the content as a downloadable file attachment or as a raw stream. Defaults to false (raw stream)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the content of a specific document chunk in the requested format. Supports streaming media content for audio and video documents, with optional file download capability."""

    # Construct request model with validation
    try:
        _request = _models.GetDocumentChunkContentRequest(
            path=_models.GetDocumentChunkContentRequestPath(document_id=document_id, chunk_id=chunk_id),
            query=_models.GetDocumentChunkContentRequestQuery(media_type=media_type, download=download)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_document_chunk_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/documents/{document_id}/chunks/{chunk_id}/content", _request.path.model_dump(by_alias=True)) if _request.path else "/documents/{document_id}/chunks/{chunk_id}/content"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_document_chunk_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_document_chunk_content", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_document_chunk_content",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def get_document_content(
    document_id: str = Field(..., description="The unique identifier of the document to retrieve, formatted as a UUID."),
    media_type: str | None = Field(None, description="The desired format for the returned content, specified as a MIME type (e.g., application/json, text/plain, audio/mpeg, video/mp4). If the document doesn't support the requested type, an error will be returned."),
    download: bool | None = Field(None, description="When true, the content is returned as a downloadable file with its original filename. When false (default), the content is returned as a raw stream."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the content of a document in your preferred format. Supports multiple media types including JSON (with metadata), plain text, and streaming formats for audio/video content. Non-textual media like images are returned as text descriptions."""

    # Construct request model with validation
    try:
        _request = _models.GetDocumentContentRequest(
            path=_models.GetDocumentContentRequestPath(document_id=document_id),
            query=_models.GetDocumentContentRequestQuery(media_type=media_type, download=download)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_document_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/documents/{document_id}/content", _request.path.model_dump(by_alias=True)) if _request.path else "/documents/{document_id}/content"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_document_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_document_content", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_document_content",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def get_document_source(document_id: str = Field(..., description="The unique identifier of the document, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve the original source file of a document. The source varies by origin: uploaded files are returned as-is, URL-sourced documents return the fetched content, and connection-synced documents return the format specific to that connection type (e.g., file from Google Drive, JSON from Salesforce)."""

    # Construct request model with validation
    try:
        _request = _models.GetDocumentSourceRequest(
            path=_models.GetDocumentSourceRequestPath(document_id=document_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_document_source: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/documents/{document_id}/source", _request.path.model_dump(by_alias=True)) if _request.path else "/documents/{document_id}/source"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_document_source")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_document_source", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_document_source",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: retrievals
@mcp.tool()
async def search_document_chunks(
    query: str = Field(..., description="The search query used to find semantically relevant document chunks. Can be a natural language question or statement."),
    top_k: int | None = Field(None, description="Maximum number of chunks to return in the results. Defaults to 8 chunks."),
    filter_: dict[str, Any] | None = Field(None, alias="filter", description="Metadata filter to narrow results to documents matching specific criteria. Supports equality, inequality, comparison, and array membership operators that can be combined with AND/OR logic."),
    rerank: bool | None = Field(None, description="Enable semantic reranking of results for higher relevancy, improving accuracy and reducing hallucinations. Processing will be slower but returns a more focused set of highly relevant chunks."),
    max_chunks_per_document: int | None = Field(None, description="Limit the number of chunks retrieved from any single document. Use this to diversify results across multiple documents rather than concentrating chunks from one source."),
    recency_bias: bool | None = Field(None, description="Prioritize more recent documents over older ones in the ranking. Useful when document freshness is important for accuracy."),
) -> dict[str, Any] | ToolResult:
    """Search and retrieve relevant document chunks based on a semantic query, with optional filtering, reranking, and recency bias to support accurate LLM-based generation and reduce hallucinations."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveRequest(
            body=_models.RetrieveRequestBody(query=query, top_k=top_k, filter_=filter_, rerank=rerank, max_chunks_per_document=max_chunks_per_document, recency_bias=recency_bias)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_document_chunks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/retrievals"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_document_chunks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_document_chunks", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_document_chunks",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: documents
@mcp.tool()
async def get_document_summary(document_id: str = Field(..., description="The unique identifier of the document, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieve an LLM-generated summary of a document. The summary is automatically created when the document is first uploaded or updated. Note: This feature is in beta and may change; data files (xls, xlsx, csv, json) and documents exceeding 1M tokens are not supported."""

    # Construct request model with validation
    try:
        _request = _models.GetDocumentSummaryRequest(
            path=_models.GetDocumentSummaryRequestPath(document_id=document_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_document_summary: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/documents/{document_id}/summary", _request.path.model_dump(by_alias=True)) if _request.path else "/documents/{document_id}/summary"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_document_summary")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_document_summary", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_document_summary",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: entities
@mcp.tool()
async def list_instructions() -> dict[str, Any] | ToolResult:
    """Retrieve all instructions available in the system. Use this operation to discover and review the complete set of instructions."""

    # Extract parameters for API call
    _http_path = "/instructions"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_instructions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_instructions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_instructions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: entities
@mcp.tool()
async def create_instruction(
    name: str = Field(..., description="A unique name for the instruction that identifies its purpose (e.g., 'Find all pizzas'). Must not duplicate existing instruction names."),
    prompt: str = Field(..., description="A natural language instruction describing what data to extract from documents. This prompt is applied to document content and results are stored as entities matching the entity_schema."),
    entity_schema: dict[str, Any] = Field(..., description="A JSON schema defining the structure of extracted entities. Must be an object type at the root. For multiple items, use an array property (e.g., 'emails' as an array of strings). For single values, wrap in an object with a single key (e.g., 'summary' as a string)."),
    active: bool | None = Field(None, description="Whether this instruction is immediately active and applied to new and updated documents. Defaults to true."),
    scope: Literal["document", "chunk"] | None = Field(None, description="Determines the granularity of analysis: 'document' analyzes the entire document (useful for summaries or sentiment), while 'chunk' analyzes individual document sections (useful for fine-grained search). Defaults to 'chunk'."),
    context_template: str | None = Field(None, description="An optional Mustache template that prepends document context (name, type, source, metadata) to the content before extraction. Use variables like {{document.name}} and {{document.metadata.key_name}} to include document details."),
    filter_: dict[str, Any] | None = Field(None, alias="filter", description="An optional metadata filter that restricts instruction application to matching documents. Supports operators like $eq, $ne, $gt, $gte, $lt, $lte, $in, $nin, and can combine conditions with AND/OR logic."),
) -> dict[str, Any] | ToolResult:
    """Create a new instruction that automatically extracts structured data from documents as they are created or updated. Instructions apply natural language prompts to documents and store results according to a defined JSON schema."""

    # Construct request model with validation
    try:
        _request = _models.CreateInstructionRequest(
            body=_models.CreateInstructionRequestBody(name=name, active=active, scope=scope, prompt=prompt, context_template=context_template, entity_schema=entity_schema, filter_=filter_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_instruction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/instructions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_instruction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_instruction", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_instruction",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: entities
@mcp.tool()
async def update_instruction(
    instruction_id: str = Field(..., description="The unique identifier (UUID) of the instruction to update."),
    name: str | None = Field(None, description="A unique name for the instruction. Must not conflict with existing instruction names."),
    active: bool | None = Field(None, description="Whether the instruction is active. Active instructions are automatically applied when documents are created or their files are updated."),
    scope: Literal["document", "chunk"] | None = Field(None, description="The scope determines how the instruction is applied: 'document' analyzes the entire document (ideal for summaries or sentiment analysis), while 'chunk' analyzes individual document chunks (ideal for fine-grained search or extraction)."),
    prompt: str | None = Field(None, description="A natural language instruction that defines what entities or information to extract from documents. Results are stored as entities matching the schema defined in entity_schema."),
    context_template: str | None = Field(None, description="An optional Mustache template that prepends document context to the content sent for extraction. Supports variables like document.name, document.type, document.source, and nested metadata values (e.g., {{document.metadata.key_name}})."),
    entity_schema: dict[str, Any] | None = Field(None, description="A JSON schema (object type at root) that defines the structure of entities extracted by this instruction. For multiple items, use an array property. For single values, wrap in an object with a single key. All required fields must be listed in the schema's required array."),
    filter_: dict[str, Any] | None = Field(None, alias="filter", description="An optional metadata filter that restricts instruction application to documents matching the filter criteria. Supports operators: $eq, $ne, $gt, $gte, $lt, $lte, $in, $nin, and can be combined with AND/OR logic."),
) -> dict[str, Any] | ToolResult:
    """Update an instruction's configuration, including its name, active status, scope, prompt, context template, entity schema, and metadata filters. Changes apply to documents created or updated after the patch is applied."""

    # Construct request model with validation
    try:
        _request = _models.PatchInstructionRequest(
            path=_models.PatchInstructionRequestPath(instruction_id=instruction_id),
            body=_models.PatchInstructionRequestBody(name=name, active=active, scope=scope, prompt=prompt, context_template=context_template, entity_schema=entity_schema, filter_=filter_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_instruction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/instructions/{instruction_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/instructions/{instruction_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_instruction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_instruction", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_instruction",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: entities
@mcp.tool()
async def delete_instruction(instruction_id: str = Field(..., description="The unique identifier of the instruction to delete, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Permanently delete an instruction and all entities it generated. This operation cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteInstructionRequest(
            path=_models.DeleteInstructionRequestPath(instruction_id=instruction_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_instruction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/instructions/{instruction_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/instructions/{instruction_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_instruction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_instruction", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_instruction",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: entities
@mcp.tool()
async def list_entities_by_instruction(
    instruction_id: str = Field(..., description="The unique identifier (UUID) of the instruction whose extracted entities you want to retrieve."),
    page_size: int | None = Field(None, description="The number of entities to return per page, between 1 and 100 items. Defaults to 10 if not specified.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieve all entities that were extracted from a specific instruction. Results are paginated to allow efficient browsing of large entity sets."""

    # Construct request model with validation
    try:
        _request = _models.ListEntitiesByInstructionRequest(
            path=_models.ListEntitiesByInstructionRequestPath(instruction_id=instruction_id),
            query=_models.ListEntitiesByInstructionRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_entities_by_instruction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/instructions/{instruction_id}/entities", _request.path.model_dump(by_alias=True)) if _request.path else "/instructions/{instruction_id}/entities"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_entities_by_instruction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_entities_by_instruction", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_entities_by_instruction",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: entities
@mcp.tool()
async def list_instruction_entity_extraction_logs(
    instruction_id: str = Field(..., description="The UUID of the instruction for which to retrieve entity extraction logs."),
    page_size: int | None = Field(None, description="Number of results to return per page. Must be between 1 and 100 items. Defaults to 10 if not specified.", ge=1, le=100),
    document_ids: list[str] | None = Field(None, description="Optional list of document IDs to filter extraction logs. Only logs matching these document IDs will be included in results."),
    status: Literal["extracted", "not_found", "error"] | None = Field(None, description="Optional filter by extraction outcome status. Valid values are `extracted` (successful extraction), `not_found` (entity not found), or `error` (extraction failed)."),
    created_after: str | None = Field(None, description="Optional ISO 8601 timestamp to include only logs created on or after this date and time."),
    created_before: str | None = Field(None, description="Optional ISO 8601 timestamp to include only logs created before this date and time."),
) -> dict[str, Any] | ToolResult:
    """Retrieve entity extraction logs for a specific instruction, showing attempt-level results with both successful and unsuccessful outcomes. Results are sorted by creation date in descending order and paginated, with historical data available only from March 6, 2026 onwards."""

    # Construct request model with validation
    try:
        _request = _models.ListInstructionEntityExtractionLogsRequest(
            path=_models.ListInstructionEntityExtractionLogsRequestPath(instruction_id=instruction_id),
            query=_models.ListInstructionEntityExtractionLogsRequestQuery(page_size=page_size, document_ids=document_ids, status=status, created_after=created_after, created_before=created_before)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_instruction_entity_extraction_logs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/instructions/{instruction_id}/entity-extraction-logs", _request.path.model_dump(by_alias=True)) if _request.path else "/instructions/{instruction_id}/entity-extraction-logs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_instruction_entity_extraction_logs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_instruction_entity_extraction_logs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_instruction_entity_extraction_logs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: entities
@mcp.tool()
async def list_entities_by_document(
    document_id: str = Field(..., description="The unique identifier (UUID) of the document from which to retrieve extracted entities."),
    page_size: int | None = Field(None, description="Number of entities to return per page, between 1 and 100 items. Defaults to 10 if not specified.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieve all entities extracted from a specific document. Returns a paginated list of entities identified during document processing."""

    # Construct request model with validation
    try:
        _request = _models.ListEntitiesByDocumentRequest(
            path=_models.ListEntitiesByDocumentRequestPath(document_id=document_id),
            query=_models.ListEntitiesByDocumentRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_entities_by_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/documents/{document_id}/entities", _request.path.model_dump(by_alias=True)) if _request.path else "/documents/{document_id}/entities"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_entities_by_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_entities_by_document", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_entities_by_document",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: connections, beta, enterprise
@mcp.tool()
async def create_connection(
    connection: Annotated[_models.PublicBackblazeConnection | _models.PublicGcsConnection | _models.PublicFreshdeskConnection | _models.PublicIntercomConnection | _models.PublicS3CompatibleConnection | _models.PublicWebcrawlerConnection | _models.PublicZendeskConnection, Field(discriminator="provider")] = Field(..., description="Connection configuration object specifying the data source type and authentication details."),
    static: Literal["hi_res", "fast", "agentic_ocr"] | None = Field(None, description="Processing mode for document extraction: 'hi_res' for high-resolution processing, 'fast' for quick processing, or 'agentic_ocr' for advanced OCR-based extraction."),
    audio: bool | None = Field(None, description="Enable audio processing for documents that contain audio content."),
    video: Literal["audio_only", "video_only", "audio_video"] | None = Field(None, description="Video processing mode: 'audio_only' to extract audio tracks, 'video_only' to process video frames, or 'audio_video' to process both."),
    page_limit: int | None = Field(None, description="Maximum number of pages to process from each document. Omit or set to null for no limit."),
    config: dict[str, Any] | None = Field(None, description="Source-specific configuration object containing connection details and credentials required by the data source type."),
    metadata: dict[str, str | int | float | bool | list[str]] | None = Field(None, description="Custom metadata to attach to documents processed through this connection. Keys must be strings; values can be strings, numbers, booleans, or lists of strings. Up to 1000 total values allowed (each array item counts separately). Reserved keys like 'document_id', 'document_type', 'document_source', 'document_name', 'document_uploaded_at', 'start_time', 'end_time', and 'chunk_content_type' are for internal use only."),
    workflow: Literal["parse", "index"] | None = Field(None, description="Processing workflow: 'parse' to extract and structure document content, or 'index' to prepare documents for search and retrieval."),
) -> dict[str, Any] | ToolResult:
    """Create a new connection for non-OAuth data sources such as S3-compatible storage, Freshdesk, or Zendesk. Configure the connection with source-specific settings and optional processing parameters."""

    # Construct request model with validation
    try:
        _request = _models.CreateConnectionRequest(
            body=_models.CreateConnectionRequestBody(page_limit=page_limit, config=config, metadata=metadata, workflow=workflow, connection=connection,
                partition_strategy=_models.CreateConnectionRequestBodyPartitionStrategy(static=static, audio=audio, video=video) if any(v is not None for v in [static, audio, video]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_connection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/connection"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_connection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_connection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_connection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: connections
@mcp.tool()
async def list_connections(
    page_size: int | None = Field(None, description="Number of connections to return per page. Must be between 1 and 100 items; defaults to 10 if not specified.", ge=1, le=100),
    filter_: str | None = Field(None, alias="filter", description="Filter connections by metadata using comparison operators ($eq, $ne, $gt, $gte, $lt, $lte, $in, $nin) combined with AND/OR logic. Returns only connections matching the filter criteria. Refer to the Metadata & Filters guide for syntax and examples."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all connections sorted by creation date in descending order. Results are paginated with a maximum of 100 items per page; use the cursor parameter to fetch subsequent pages when available."""

    # Construct request model with validation
    try:
        _request = _models.ListConnectionsConnectionsGetRequest(
            query=_models.ListConnectionsConnectionsGetRequestQuery(page_size=page_size, filter_=filter_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_connections: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/connections"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_connections")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_connections", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_connections",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: connections
@mcp.tool()
async def create_oauth_redirect_url(
    redirect_uri: str = Field(..., description="The URI where the user will be redirected after completing OAuth authentication. This must be a valid, accessible endpoint in your application."),
    source_type: Literal["backblaze", "confluence", "dropbox", "freshdesk", "onedrive", "google_drive", "gmail", "intercom", "notion", "salesforce", "sharepoint", "jira", "slack", "s3", "gcs", "hubspot", "webcrawler", "zendesk"] | None = Field(None, description="The connector type to initialize (e.g., google_drive, notion, hubspot). Defaults to google_drive if not specified. Choose from supported connectors like cloud storage (S3, GCS, Dropbox), productivity tools (Notion, Slack), CRM systems (Salesforce, HubSpot), and others."),
    metadata: dict[str, str | int | float | bool | list[str]] | None = Field(None, description="Custom key-value metadata to attach to synced documents. Keys must be strings; values can be strings, numbers, booleans, or lists of strings. Up to 1000 total values allowed (each array item counts separately). Reserved keys like document_id and document_source are managed internally."),
    mode: Literal["hi_res", "fast", "agentic_ocr"] | _models.MediaModeParam | None = Field(None, description="Operational mode for the connector (specific behavior determined by connector type)."),
    theme: Literal["light", "dark", "system"] | None = Field(None, description="Visual theme for the Ragie Web UI presented to the user. Choose 'light' for light mode, 'dark' for dark mode, or 'system' to match the user's system preference. Defaults to system."),
    page_limit: int | None = Field(None, description="Maximum number of pages the connection will sync before being automatically disabled. Must be at least 1 if specified. Set to null to remove any limit. In-progress documents may continue processing after the limit is reached.", ge=1),
    config: dict[str, Any] | None = Field(None, description="Connector-specific configuration options provided as a JSON object. Structure varies by connector type."),
    authenticator_id: str | None = Field(None, description="UUID of the authenticator to use for this OAuth flow. Links the redirect URL to a specific authentication context."),
    workflow: Literal["parse", "index"] | None = Field(None, description="The workflow type for processing synced content. Choose 'parse' to extract and structure document content, or 'index' to prepare content for search and retrieval."),
) -> dict[str, Any] | ToolResult:
    """Generates an OAuth redirect URL for initializing an embedded connector, allowing users to authenticate with third-party services like Google Drive, Notion, Salesforce, and others."""

    # Construct request model with validation
    try:
        _request = _models.CreateOauthRedirectUrlConnectionsOauthPostRequest(
            body=_models.CreateOauthRedirectUrlConnectionsOauthPostRequestBody(redirect_uri=redirect_uri, source_type=source_type, metadata=metadata, mode=mode, theme=theme, page_limit=page_limit, config=config, authenticator_id=authenticator_id, workflow=workflow)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_oauth_redirect_url: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/connections/oauth"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_oauth_redirect_url")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_oauth_redirect_url", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_oauth_redirect_url",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: connections
@mcp.tool()
async def list_connection_source_types() -> dict[str, Any] | ToolResult:
    """Retrieve all available connection source types (such as Google Drive, Notion, etc.) along with their metadata to understand what integrations can be configured."""

    # Extract parameters for API call
    _http_path = "/connections/source-type"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_connection_source_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_connection_source_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_connection_source_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: connections
@mcp.tool()
async def update_connection_enabled_status(
    connection_id: str = Field(..., description="The unique identifier (UUID format) of the connection to modify."),
    enabled: bool = Field(..., description="Boolean flag to enable (true) or disable (false) the connection."),
    reason: Literal["connection_over_total_page_limit", "authentication_failed"] | None = Field(None, description="Optional reason for disabling the connection. Valid values indicate specific failure conditions: 'connection_over_total_page_limit' when the connection exceeds page limits, or 'authentication_failed' when authentication credentials are invalid."),
) -> dict[str, Any] | ToolResult:
    """Enable or disable a connection to control whether it syncs data. Disabled connections will not perform synchronization operations."""

    # Construct request model with validation
    try:
        _request = _models.SetConnectionEnabledConnectionsConnectionIdEnabledPutRequest(
            path=_models.SetConnectionEnabledConnectionsConnectionIdEnabledPutRequestPath(connection_id=connection_id),
            body=_models.SetConnectionEnabledConnectionsConnectionIdEnabledPutRequestBody(enabled=enabled, reason=reason)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_connection_enabled_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/connections/{connection_id}/enabled", _request.path.model_dump(by_alias=True)) if _request.path else "/connections/{connection_id}/enabled"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_connection_enabled_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_connection_enabled_status", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_connection_enabled_status",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: connections
@mcp.tool()
async def get_connection(connection_id: str = Field(..., description="The unique identifier (UUID) of the connection to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific connection by its unique identifier. Returns the full connection details including configuration and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetConnectionConnectionsConnectionIdGetRequest(
            path=_models.GetConnectionConnectionsConnectionIdGetRequestPath(connection_id=connection_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_connection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/connections/{connection_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/connections/{connection_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_connection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_connection", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_connection",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: connections
@mcp.tool()
async def update_connection(
    connection_id: str = Field(..., description="The unique identifier (UUID) of the connection to update."),
    partition_strategy: Literal["hi_res", "fast", "agentic_ocr"] | _models.MediaModeParam = Field(..., description="The strategy for partitioning data during sync operations."),
    metadata: dict[str, str | int | float | bool | list[str]] | None = Field(None, description="Custom metadata as key-value pairs where keys are strings and values are strings, numbers, booleans, or lists of strings. Up to 1000 total values allowed (each array item counts separately). Reserved keys like `document_id`, `document_type`, `document_source`, `document_name`, `document_uploaded_at`, `start_time`, `end_time`, and `chunk_content_type` are for internal use only."),
    page_limit: int | None = Field(None, description="Maximum number of pages to sync for this connection; the connection will be disabled once this limit is reached. Set to `null` to remove any existing limit. Must be at least 1 if specified.", ge=1),
) -> dict[str, Any] | ToolResult:
    """Update a connection's metadata or partition strategy. Changes take effect after the next sync operation."""

    # Construct request model with validation
    try:
        _request = _models.UpdateConnectionConnectionsConnectionIdPutRequest(
            path=_models.UpdateConnectionConnectionsConnectionIdPutRequestPath(connection_id=connection_id),
            body=_models.UpdateConnectionConnectionsConnectionIdPutRequestBody(partition_strategy=partition_strategy, metadata=metadata, page_limit=page_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_connection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/connections/{connection_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/connections/{connection_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_connection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_connection", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_connection",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: connections
@mcp.tool()
async def get_connection_stats(connection_id: str = Field(..., description="The unique identifier (UUID) of the connection to retrieve statistics for.")) -> dict[str, Any] | ToolResult:
    """Retrieves aggregated statistics for a specific connection, including total documents, active documents, and total active pages."""

    # Construct request model with validation
    try:
        _request = _models.GetConnectionStatsConnectionsConnectionIdStatsGetRequest(
            path=_models.GetConnectionStatsConnectionsConnectionIdStatsGetRequestPath(connection_id=connection_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_connection_stats: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/connections/{connection_id}/stats", _request.path.model_dump(by_alias=True)) if _request.path else "/connections/{connection_id}/stats"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_connection_stats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_connection_stats", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_connection_stats",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: connections
@mcp.tool()
async def update_connection_page_limit(
    connection_id: str = Field(..., description="The unique identifier of the connection to configure limits for."),
    page_limit: int | None = Field(None, description="The maximum number of pages this connection will synchronize before being disabled. Must be at least 1 if specified. Set to null to remove any existing limit.", ge=1),
) -> dict[str, Any] | ToolResult:
    """Set or remove page synchronization limits for a connection. When a limit is set, the connection automatically disables after syncing the specified number of pages, though some in-process documents may continue processing."""

    # Construct request model with validation
    try:
        _request = _models.SetConnectionLimitsConnectionsConnectionIdLimitPutRequest(
            path=_models.SetConnectionLimitsConnectionsConnectionIdLimitPutRequestPath(connection_id=connection_id),
            body=_models.SetConnectionLimitsConnectionsConnectionIdLimitPutRequestBody(page_limit=page_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_connection_page_limit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/connections/{connection_id}/limit", _request.path.model_dump(by_alias=True)) if _request.path else "/connections/{connection_id}/limit"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_connection_page_limit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_connection_page_limit", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_connection_page_limit",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: connections
@mcp.tool()
async def delete_connection(
    connection_id: str = Field(..., description="The unique identifier (UUID) of the connection to delete."),
    keep_files: bool = Field(..., description="Whether to retain files associated with this connection. If true, files are preserved but disassociated; if false, all files are deleted with the connection."),
) -> dict[str, Any] | ToolResult:
    """Schedules a connection for deletion. Optionally preserve associated files (they will be disassociated from the connection) or delete them along with the connection. Deletion is asynchronous and files may remain visible briefly after the request completes."""

    # Construct request model with validation
    try:
        _request = _models.DeleteConnectionConnectionsConnectionIdDeletePostRequest(
            path=_models.DeleteConnectionConnectionsConnectionIdDeletePostRequestPath(connection_id=connection_id),
            body=_models.DeleteConnectionConnectionsConnectionIdDeletePostRequestBody(keep_files=keep_files)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_connection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/connections/{connection_id}/delete", _request.path.model_dump(by_alias=True)) if _request.path else "/connections/{connection_id}/delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_connection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_connection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_connection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: connections
@mcp.tool()
async def trigger_connection_sync(connection_id: str = Field(..., description="The unique identifier of the connection to sync, formatted as a UUID.")) -> dict[str, Any] | ToolResult:
    """Immediately schedules a connector to begin syncing data. This operation queues the sync to run as soon as possible."""

    # Construct request model with validation
    try:
        _request = _models.SyncConnectionRequest(
            path=_models.SyncConnectionRequestPath(connection_id=connection_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for trigger_connection_sync: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/connections/{connection_id}/sync", _request.path.model_dump(by_alias=True)) if _request.path else "/connections/{connection_id}/sync"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("trigger_connection_sync")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("trigger_connection_sync", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="trigger_connection_sync",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: webhook_endpoints
@mcp.tool()
async def list_webhook_endpoints(page_size: int | None = Field(None, description="Number of webhook endpoints to return per page. Must be between 1 and 100 items. Defaults to 10 if not specified.", ge=1, le=100)) -> dict[str, Any] | ToolResult:
    """Retrieve all webhook endpoints sorted by creation date in descending order. Results are paginated with a maximum of 100 items per page, and a cursor is provided when additional endpoints are available."""

    # Construct request model with validation
    try:
        _request = _models.ListWebhookEndpointsRequest(
            query=_models.ListWebhookEndpointsRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhook_endpoints: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/webhook_endpoints"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_webhook_endpoints")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_webhook_endpoints", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_webhook_endpoints",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: webhook_endpoints
@mcp.tool()
async def get_webhook_endpoint(endpoint_id: str = Field(..., description="The unique identifier (UUID) of the webhook endpoint to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific webhook endpoint by its unique identifier. Use this to fetch configuration and status details for a registered webhook."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhookEndpointRequest(
            path=_models.GetWebhookEndpointRequestPath(endpoint_id=endpoint_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook_endpoint: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/webhook_endpoints/{endpoint_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/webhook_endpoints/{endpoint_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_webhook_endpoint")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_webhook_endpoint", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_webhook_endpoint",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: webhook_endpoints
@mcp.tool()
async def update_webhook_endpoint(
    endpoint_id: str = Field(..., description="The unique identifier of the webhook endpoint to update, formatted as a UUID."),
    name: str | None = Field(None, description="A new display name for the webhook endpoint."),
    url: str | None = Field(None, description="A new delivery URL for the webhook endpoint. Must be a valid URI between 1 and 2083 characters.", min_length=1, max_length=2083),
    active: bool | None = Field(None, description="Whether the webhook endpoint is active and should receive event deliveries. Set to false to temporarily disable delivery without deleting the endpoint."),
    partition_pattern: str | None = Field(None, description="A pattern to partition webhook events for this endpoint."),
) -> dict[str, Any] | ToolResult:
    """Update a webhook endpoint's configuration including its name, URL, or active status. Use this operation to rotate endpoints, change delivery URLs, or temporarily disable webhook delivery without deleting the endpoint."""

    # Construct request model with validation
    try:
        _request = _models.UpdateWebhookEndpointRequest(
            path=_models.UpdateWebhookEndpointRequestPath(endpoint_id=endpoint_id),
            body=_models.UpdateWebhookEndpointRequestBody(name=name, url=url, active=active, partition_pattern=partition_pattern)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_webhook_endpoint: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/webhook_endpoints/{endpoint_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/webhook_endpoints/{endpoint_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_webhook_endpoint")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_webhook_endpoint", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_webhook_endpoint",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: partitions
@mcp.tool()
async def list_partitions(page_size: int | None = Field(None, description="Number of partitions to return per page. Must be between 1 and 100 items; defaults to 10 if not specified.", ge=1, le=100)) -> dict[str, Any] | ToolResult:
    """Retrieve all partitions sorted alphabetically in ascending order. Results are paginated with a maximum of 100 items per page; use the cursor parameter to fetch subsequent pages when available."""

    # Construct request model with validation
    try:
        _request = _models.ListPartitionsPartitionsGetRequest(
            query=_models.ListPartitionsPartitionsGetRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_partitions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/partitions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_partitions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_partitions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_partitions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: partitions
@mcp.tool()
async def create_partition(
    name: str = Field(..., description="Unique identifier for the partition. Must be lowercase alphanumeric and may only contain underscores and hyphens."),
    description: str | None = Field(None, description="Human-readable description of the partition's purpose. Automatic description generation can be enabled in the web dashboard."),
    pages_hosted_limit_max: int | None = Field(None, description="Maximum number of pages allowed for hosted documents in this partition. Must be at least 1.", ge=1),
    pages_processed_limit_max: int | None = Field(None, description="Maximum number of pages allowed for processed documents in this partition. Must be at least 1.", ge=1),
    audio_processed_limit_max: int | None = Field(None, description="Maximum duration in minutes for audio processing in this partition. Must be at least 1.", ge=1),
    video_processed_limit_max: int | None = Field(None, description="Maximum duration in minutes for video processing in this partition. Must be at least 1.", ge=1),
    media_streamed_limit_max: int | None = Field(None, description="Maximum size in megabytes for media streamed from this partition. Must be at least 1.", ge=1),
    media_hosted_limit_max: int | None = Field(None, description="Maximum size in megabytes for media hosted in this partition. Must be at least 1.", ge=1),
    metadata_schema: dict[str, str | int | bool | list[str] | dict[str, Any]] | None = Field(None, description="JSON Schema defining optional metadata fields for documents in this partition. Include detailed field descriptions to assist LLMs in generating dynamic filters."),
) -> dict[str, Any] | ToolResult:
    """Create a new partition to scope documents, connections, and instructions. Partition names must be lowercase alphanumeric with only underscores and hyphens allowed. Optional resource limits can be defined at creation time."""

    # Construct request model with validation
    try:
        _request = _models.CreatePartitionPartitionsPostRequest(
            body=_models.CreatePartitionPartitionsPostRequestBody(name=name, description=description, pages_hosted_limit_max=pages_hosted_limit_max, pages_processed_limit_max=pages_processed_limit_max, audio_processed_limit_max=audio_processed_limit_max, video_processed_limit_max=video_processed_limit_max, media_streamed_limit_max=media_streamed_limit_max, media_hosted_limit_max=media_hosted_limit_max, metadata_schema=metadata_schema)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_partition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/partitions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_partition")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_partition", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_partition",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: partitions
@mcp.tool()
async def get_partition(partition_id: str = Field(..., description="The unique identifier of the partition to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific partition, including its usage metrics (document and page counts) and configured limits."""

    # Construct request model with validation
    try:
        _request = _models.GetPartitionPartitionsPartitionIdGetRequest(
            path=_models.GetPartitionPartitionsPartitionIdGetRequestPath(partition_id=partition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_partition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/partitions/{partition_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/partitions/{partition_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_partition")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_partition", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_partition",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: partitions
@mcp.tool()
async def update_partition(
    partition_id: str = Field(..., description="The unique identifier of the partition to update."),
    context_aware: bool | None = Field(None, description="Enable context-aware descriptions that provide additional semantic context for the partition to improve LLM understanding and filter generation."),
    description: str | None = Field(None, description="A human-readable description of the partition's purpose and contents."),
    metadata_schema: dict[str, str | int | bool | list[str] | dict[str, Any]] | None = Field(None, description="A JSON Schema definition describing the structure and types of metadata fields available in documents within this partition. Include detailed field descriptions to assist LLMs in generating accurate dynamic filters."),
) -> dict[str, Any] | ToolResult:
    """Update a partition's configuration, including its description and metadata schema. The metadata schema defines an optional subset of document metadata as JSON Schema, useful for LLM-based filter generation."""

    # Construct request model with validation
    try:
        _request = _models.UpdatePartitionPartitionsPartitionIdPatchRequest(
            path=_models.UpdatePartitionPartitionsPartitionIdPatchRequestPath(partition_id=partition_id),
            body=_models.UpdatePartitionPartitionsPartitionIdPatchRequestBody(context_aware=context_aware, description=description, metadata_schema=metadata_schema)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_partition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/partitions/{partition_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/partitions/{partition_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_partition")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_partition", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_partition",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: partitions
@mcp.tool()
async def delete_partition(
    partition_id: str = Field(..., description="The unique identifier of the partition to delete."),
    async_: bool | None = Field(None, alias="async", description="When set to true, the partition deletion is performed asynchronously, allowing the request to return immediately while the deletion completes in the background. Defaults to false for synchronous deletion."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a partition and all associated data, including connections, documents, and partition-specific instructions. This operation cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeletePartitionPartitionsPartitionIdDeleteRequest(
            path=_models.DeletePartitionPartitionsPartitionIdDeleteRequestPath(partition_id=partition_id),
            query=_models.DeletePartitionPartitionsPartitionIdDeleteRequestQuery(async_=async_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_partition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/partitions/{partition_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/partitions/{partition_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_partition")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_partition", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_partition",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: partitions
@mcp.tool()
async def update_partition_limits(
    partition_id: str = Field(..., description="The unique identifier of the partition to configure limits for."),
    pages_hosted_limit_max: int | None = Field(None, description="Maximum number of pages allowed for hosted documents in the partition. Must be at least 1 page.", ge=1),
    pages_processed_limit_max: int | None = Field(None, description="Maximum number of pages allowed for processed documents in the partition. Must be at least 1 page.", ge=1),
    video_processed_limit_max: int | None = Field(None, description="Maximum duration in minutes for video processing in the partition. Must be at least 1 minute.", ge=1),
    audio_processed_limit_max: int | None = Field(None, description="Maximum duration in minutes for audio processing in the partition. Must be at least 1 minute.", ge=1),
    media_streamed_limit_max: int | None = Field(None, description="Maximum size in megabytes for media streamed from the partition. Must be at least 1 MB.", ge=1),
    media_hosted_limit_max: int | None = Field(None, description="Maximum size in megabytes for media hosted in the partition. Must be at least 1 MB.", ge=1),
) -> dict[str, Any] | ToolResult:
    """Configure resource limits for a partition, including document hosting/processing capacity and media streaming/hosting quotas. When a limit is reached, the partition will be automatically disabled. Set any limit to null to remove it."""

    # Construct request model with validation
    try:
        _request = _models.SetPartitionLimitsPartitionsPartitionIdLimitsPutRequest(
            path=_models.SetPartitionLimitsPartitionsPartitionIdLimitsPutRequestPath(partition_id=partition_id),
            body=_models.SetPartitionLimitsPartitionsPartitionIdLimitsPutRequestBody(pages_hosted_limit_max=pages_hosted_limit_max, pages_processed_limit_max=pages_processed_limit_max, video_processed_limit_max=video_processed_limit_max, audio_processed_limit_max=audio_processed_limit_max, media_streamed_limit_max=media_streamed_limit_max, media_hosted_limit_max=media_hosted_limit_max)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_partition_limits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/partitions/{partition_id}/limits", _request.path.model_dump(by_alias=True)) if _request.path else "/partitions/{partition_id}/limits"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_partition_limits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_partition_limits", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_partition_limits",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: authenticators, beta, enterprise
@mcp.tool()
async def list_authenticators(page_size: int | None = Field(None, description="Number of authenticators to return per page. Must be between 1 and 100 items; defaults to 10 if not specified.", ge=1, le=100)) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of all authenticators sorted by creation date in descending order. Use the cursor parameter to navigate through pages when more results are available."""

    # Construct request model with validation
    try:
        _request = _models.ListAuthenticatorsRequest(
            query=_models.ListAuthenticatorsRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_authenticators: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/authenticators"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_authenticators")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_authenticators", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_authenticators",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: authenticators, beta, enterprise
@mcp.tool()
async def create_authenticator(
    provider: Literal["atlassian", "dropbox", "hubspot", "microsoft", "salesforce", "slack"] = Field(..., description="The provider service to authenticate with. Must be one of: Atlassian, Dropbox, HubSpot, Microsoft, Salesforce, or Slack."),
    name: str = Field(..., description="A unique identifier for this authenticator configuration. This name is used to reference and distinguish the authenticator from others. Names must be globally unique within your account."),
    client_id: str = Field(..., description="The OAuth 2.0 client ID issued by the provider's application registration or developer console."),
    client_secret: str = Field(..., description="The OAuth 2.0 client secret issued by the provider's application registration or developer console. Keep this value secure."),
    domain: str | None = Field(None, description="The domain or workspace identifier for the provider, if applicable. Required for certain providers that use domain-based authentication."),
    project_number: str | None = Field(None, description="The project number identifier for the provider, if applicable. Required for certain providers that use project-based authentication."),
) -> dict[str, Any] | ToolResult:
    """Create white-labeled connector credentials for integrating with third-party services. This establishes authentication configuration that enables secure API access to supported providers."""

    # Construct request model with validation
    try:
        _request = _models.CreateAuthenticatorRequest(
            body=_models.CreateAuthenticatorRequestBody(provider=provider, name=name, client_id=client_id, client_secret=client_secret, domain=domain, project_number=project_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_authenticator: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/authenticators"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_authenticator")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_authenticator", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_authenticator",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: authenticators, beta, enterprise
@mcp.tool()
async def create_authenticator_connection(
    authenticator_id: str = Field(..., description="The unique identifier (UUID) of the authenticator to create a connection for."),
    connection: Annotated[_models.AuthenticatorConfluenceConnection | _models.AuthenticatorDropboxConnection | _models.AuthenticatorGoogleDriveConnection | _models.AuthenticatorGmailConnection | _models.AuthenticatorHubspotConnection | _models.AuthenticatorJiraConnection | _models.AuthenticatorNotionConnection | _models.AuthenticatorOnedriveConnection | _models.AuthenticatorSalesforceConnection | _models.AuthenticatorSharepointConnection | _models.AuthenticatorSlackConnection, Field(discriminator="provider")] = Field(..., description="Connection credentials object. Structure and required fields depend on the authenticator provider type."),
    static: Literal["hi_res", "fast", "agentic_ocr"] | None = Field(None, description="OCR processing mode for static documents: 'hi_res' for high-resolution processing, 'fast' for quick processing, or 'agentic_ocr' for intelligent OCR."),
    audio: bool | None = Field(None, description="Enable audio extraction and processing from documents."),
    video: Literal["audio_only", "video_only", "audio_video"] | None = Field(None, description="Video processing mode: 'audio_only' to extract audio, 'video_only' to process video frames, or 'audio_video' to process both."),
    page_limit: int | None = Field(None, description="Maximum number of pages to process from the source. Omit or set to null for no limit."),
    config: dict[str, Any] | None = Field(None, description="Provider-specific configuration object. Structure depends on the authenticator type."),
    metadata: dict[str, str | int | float | bool | list[str]] | None = Field(None, description="Custom metadata key-value pairs for document classification and filtering. Keys must be strings; values can be strings, numbers, booleans, or lists of strings. Up to 1000 total values allowed (each array item counts separately). Reserved keys: document_id, document_type, document_source, document_name, document_uploaded_at, start_time, end_time, chunk_content_type."),
    workflow: Literal["parse", "index"] | None = Field(None, description="Processing workflow: 'parse' to extract and structure content, or 'index' to prepare for search and retrieval."),
) -> dict[str, Any] | ToolResult:
    """Establish a connector for a specified authenticator with provider-specific credentials (e.g., Google Drive refresh token). Configure document processing options like OCR mode, media handling, and metadata."""

    # Construct request model with validation
    try:
        _request = _models.CreateAuthenticatorConnectionRequest(
            path=_models.CreateAuthenticatorConnectionRequestPath(authenticator_id=authenticator_id),
            body=_models.CreateAuthenticatorConnectionRequestBody(page_limit=page_limit, config=config, metadata=metadata, workflow=workflow, connection=connection,
                partition_strategy=_models.CreateAuthenticatorConnectionRequestBodyPartitionStrategy(static=static, audio=audio, video=video) if any(v is not None for v in [static, audio, video]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_authenticator_connection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/authenticators/{authenticator_id}/connection", _request.path.model_dump(by_alias=True)) if _request.path else "/authenticators/{authenticator_id}/connection"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_authenticator_connection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_authenticator_connection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_authenticator_connection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: authenticators, beta, enterprise
@mcp.tool()
async def delete_authenticator(authenticator_id: str = Field(..., description="The unique identifier (UUID) of the authenticator to delete.")) -> dict[str, Any] | ToolResult:
    """Delete an authenticator connection method. All connections created by this authenticator must be deleted before this operation can succeed."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAuthenticatorConnectionRequest(
            path=_models.DeleteAuthenticatorConnectionRequestPath(authenticator_id=authenticator_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_authenticator: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/authenticators/{authenticator_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/authenticators/{authenticator_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_authenticator")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_authenticator", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_authenticator",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: responses
@mcp.tool()
async def create_response(
    input_: str = Field(..., alias="input", description="The query or question to generate a response for. This text is processed by the LLM agent to produce relevant answers."),
    effort: Literal["low", "medium", "high"] = Field(..., description="The computational effort level for generating the response. Choose low for quick responses, medium for balanced quality and speed, or high for more thorough analysis."),
    instructions: str | None = Field(None, description="Custom instructions to inject into the agent's prompt, particularly during search and retrieval steps. Use this to guide the agent's behavior and response style."),
    tools: list[_models.Tool] | None = Field(None, description="Array of tools available to the agent for generating responses. Currently supports the retrieve tool for document search. Each tool can specify which partitions to search; if omitted, the default partition is used. Defaults to retrieve tool with the default partition."),
    model: Literal["deep-search"] | None = Field(None, description="The LLM model powering the agent. Currently only deep-search is supported."),
    stream: bool | None = Field(None, description="Whether to stream the response as it's generated (true) or wait for the complete response (false). Streaming allows real-time consumption of results."),
) -> dict[str, Any] | ToolResult:
    """Generate an LLM-powered response to a query using the deep-search model. Responses can be streamed in real-time or returned synchronously, with optional access to document retrieval tools across specified partitions."""

    # Construct request model with validation
    try:
        _request = _models.CreateResponseResponsesPostRequest(
            body=_models.CreateResponseResponsesPostRequestBody(input_=input_, instructions=instructions, tools=tools, model=model, stream=stream,
                reasoning=_models.CreateResponseResponsesPostRequestBodyReasoning(effort=effort))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_response: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/responses"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_response")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_response", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_response",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: responses
@mcp.tool()
async def get_response(response_id: str = Field(..., description="The unique identifier (UUID) of the response to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a response by its unique identifier. Returns the response data along with its current status: `in_progress` for ongoing processing, `completed` for finished responses, or `failed` for responses that encountered an error."""

    # Construct request model with validation
    try:
        _request = _models.GetResponseResponsesResponseIdGetRequest(
            path=_models.GetResponseResponsesResponseIdGetRequestPath(response_id=response_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_response: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/responses/{response_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/responses/{response_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_response")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_response", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_response",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: elements
@mcp.tool()
async def list_document_elements(
    document_id: str = Field(..., description="The unique identifier (UUID) of the document containing the elements to retrieve."),
    page_size: int | None = Field(None, description="Number of elements to return per page. Must be between 1 and 100 items (defaults to 10 if not specified).", ge=1, le=100),
    type_: list[Literal["Caption", "Title", "Text", "UncategorizedText", "NarrativeText", "Image", "FigureCaption", "TableCaption", "ListItem", "Address", "EmailAddress", "PageBreak", "Formula", "Table", "Header", "Footer", "Json", "AudioTranscriptionSegment", "VideoSegment", "SubHeader", "SectionHeader", "Author", "CalendarDate", "Quote", "Comment", "UnorderedList", "OrderedList", "DefinitionList", "Figure", "Stamp", "Logo", "Watermark", "Barcode", "QrCode", "Signature", "KeyValue", "FormField", "Code", "Bibliography", "TableOfContents", "Footnote", "Time", "Button", "Video"]] | None = Field(None, alias="type", description="Filter results by element type(s). Accepts an array of type values to match against."),
    index_start: int | None = Field(None, description="Filter results to include only elements at or after this index position (inclusive)."),
    index_end: int | None = Field(None, description="Filter results to include only elements at or before this index position (inclusive)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve paginated elements from a document, sorted by index in ascending order. Results are limited to 100 items per page, with cursor-based pagination for accessing subsequent pages."""

    # Construct request model with validation
    try:
        _request = _models.ListElementsRequest(
            path=_models.ListElementsRequestPath(document_id=document_id),
            query=_models.ListElementsRequestQuery(page_size=page_size, type_=type_, index_start=index_start, index_end=index_end)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_document_elements: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/documents/{document_id}/elements", _request.path.model_dump(by_alias=True)) if _request.path else "/documents/{document_id}/elements"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_document_elements")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_document_elements", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_document_elements",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: elements
@mcp.tool()
async def get_element(element_id: str = Field(..., description="The unique identifier (UUID) of the element to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific element from a document by its unique identifier. Use this to fetch detailed information about an individual element."""

    # Construct request model with validation
    try:
        _request = _models.GetElementRequest(
            path=_models.GetElementRequestPath(element_id=element_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_element: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/elements/{element_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/elements/{element_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_element")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_element", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_element",
        method="GET",
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
        print("  python ragie_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Ragie MCP Server")

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
    logger.info("Starting Ragie MCP Server")
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

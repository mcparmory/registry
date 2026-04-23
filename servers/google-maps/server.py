#!/usr/bin/env python3
"""
Google Maps Platform MCP Server
Generated: 2026-04-23 21:21:53 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://maps.googleapis.com")
OPERATION_URL_MAP: dict[str, str] = {
    "locate_device": os.getenv("SERVER_URL_LOCATE_DEVICE", "https://www.googleapis.com"),
    "snap_coordinates_to_roads": os.getenv("SERVER_URL_SNAP_COORDINATES_TO_ROADS", "https://roads.googleapis.com"),
    "snap_points_to_roads": os.getenv("SERVER_URL_SNAP_POINTS_TO_ROADS", "https://roads.googleapis.com"),
}
SERVER_NAME = "Google Maps Platform"
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

    last_error: httpx.HTTPStatusError | Exception | None = None
    _auth_retried = False  # Guard: only attempt one auth refresh per request
    for attempt in range(max_attempts):
        try:
            # Dispatch body to correct httpx kwarg based on content type
            _json = body if body_content_type is None or body_content_type == "application/json" else None
            _form_content = None
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
            _content = None
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
                url=path,
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


def _serialize_query(params: dict[str, Any], styles: dict[str, tuple[str, bool]]) -> dict[str, Any]:
    """Serialize query params per OAS style/explode rules."""
    result: dict[str, Any] = {}
    for key, value in params.items():
        if key not in styles:
            result[key] = value
            continue
        style, explode = styles[key]
        if isinstance(value, list):
            if style == "pipeDelimited":
                result[key] = "|".join(str(v) for v in value)
            elif style == "spaceDelimited":
                result[key] = " ".join(str(v) for v in value)
            elif not explode:
                result[key] = ",".join(str(v) for v in value)
            else:
                result[key] = value
        elif isinstance(value, dict):
            if style == "deepObject":
                for k, v in value.items():
                    result[f"{key}[{k}]"] = v
            elif not explode:
                result[key] = ",".join(f"{k},{v}" for k, v in value.items())
            else:
                result.update(value)
        else:
            result[key] = value
    return result

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
    _auth_handlers["ApiKeyAuth"] = _auth.APIKeyAuth(env_var="API_KEY", location="query", param_name="key")
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

mcp = FastMCP("Google Maps Platform", middleware=[_JsonCoercionMiddleware()])

# Tags: Geolocation API
@mcp.tool()
async def locate_device(
    home_mobile_country_code: int | None = Field(None, alias="homeMobileCountryCode", description="The Mobile Country Code (MCC) of the primary cell tower. Used to identify the country of the cellular network."),
    home_mobile_network_code: int | None = Field(None, alias="homeMobileNetworkCode", description="The Mobile Network Code (MNC) of the primary cell tower. For GSM and WCDMA networks this is the MNC; for CDMA networks this is the System ID (SID)."),
    radio_type: str | None = Field(None, alias="radioType", description="The type of mobile radio technology in use. Supported values are lte, gsm, cdma, and wcdma. Including this value improves location accuracy when available."),
    carrier: str | None = Field(None, description="The name of the cellular carrier or network operator."),
    consider_ip: str | None = Field(None, alias="considerIp", description="Whether to use IP address geolocation as a fallback when cell tower and WiFi signals are unavailable. Defaults to true; set to false to disable IP-based fallback."),
    cell_towers: list[_models.CellTower] | None = Field(None, alias="cellTowers", description="An array of cell tower objects detected by the device. Each object should contain signal strength and tower identification data. Order does not affect results."),
    wifi_access_points: list[_models.WiFiAccessPoint] | None = Field(None, alias="wifiAccessPoints", description="An array of at least two WiFi access point objects detected by the device. Each object should contain BSSID and signal strength data. More access points improve accuracy."),
) -> dict[str, Any] | ToolResult:
    """Determines a device's geographic location based on detected cell towers and WiFi access points. Returns coordinates with an accuracy radius, with optional fallback to IP-based geolocation."""

    # Construct request model with validation
    try:
        _request = _models.GeolocateRequest(
            body=_models.GeolocateRequestBody(home_mobile_country_code=home_mobile_country_code, home_mobile_network_code=home_mobile_network_code, radio_type=radio_type, carrier=carrier, consider_ip=consider_ip, cell_towers=cell_towers, wifi_access_points=wifi_access_points)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for locate_device: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/geolocation/v1/geolocate"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("locate_device")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("locate_device", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="locate_device",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
    )

    return _response_data

# Tags: Directions API
@mcp.tool()
async def calculate_directions(
    destination: str = Field(..., description="The destination location as a place ID (prefixed with 'place_id:'), street address, latitude/longitude coordinates, or plus code. Place IDs are recommended for accuracy and performance."),
    origin: str = Field(..., description="The starting location as a place ID (prefixed with 'place_id:'), street address, latitude/longitude coordinates, or plus code. Place IDs are recommended for accuracy and performance over addresses or raw coordinates."),
    alternatives: bool | None = Field(None, description="Allow the service to return multiple alternative routes. Only available for requests without intermediate waypoints. Note that providing alternatives may increase response time."),
    avoid: str | None = Field(None, description="Specify route features to avoid, such as tolls, highways, ferries, or indoor steps. Multiple restrictions can be combined using the pipe character separator."),
    units: Literal["imperial", "metric"] | None = Field(None, description="The unit system for displaying distances in results. Choose 'metric' for kilometers and meters, or 'imperial' for miles and feet. Defaults to the origin country's standard system."),
    waypoints: str | None = Field(None, description="Intermediate locations to route through or stop at between origin and destination. Supports up to 25 waypoints using place IDs, addresses, coordinates, or encoded polylines separated by pipes. Use 'via:' prefix to route through without stopping, or 'optimize:true' to reorder waypoints for efficiency. Requests with 11+ waypoints or optimization incur higher billing."),
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(None, description="The language for returned results. Defaults to the Accept-Language header preference. Supports 40+ languages including regional variants like en-GB and pt-BR."),
    mode: Literal["driving", "bicycling", "transit", "walking"] | None = Field(None, description="The transportation mode for calculating directions. Choose 'driving' (default), 'walking', 'bicycling', or 'transit'. Transit directions support optional departure/arrival times and transit preferences."),
    region: Literal["ac", "ad", "ae", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "eh", "en", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy", "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "za", "zm", "zw"] | None = Field(None, description="The region code as a two-character ccTLD to bias results toward a specific country. Defaults to 'en'. Use country-specific codes like 'uk' for United Kingdom or 'au' for Australia."),
    traffic_model: Literal["best_guess", "pessimistic", "optimistic"] | None = Field(None, description="Traffic prediction model for driving directions with a departure time. Choose 'best_guess' (default) for balanced predictions, 'pessimistic' for longer estimates, or 'optimistic' for shorter estimates."),
    transit_mode: str | None = Field(None, description="Preferred transit modes to prioritize in the route calculation. Supports 'bus', 'subway', 'train', 'tram', or 'rail' (combines train, tram, and subway). Multiple modes can be combined using pipe separators."),
    transit_routing_preference: Literal["less_walking", "fewer_transfers"] | None = Field(None, description="Transit routing preference to bias results. Choose 'less_walking' to minimize walking distance or 'fewer_transfers' to reduce the number of transit transfers."),
) -> dict[str, Any] | ToolResult:
    """Calculate directions and distances between locations using various transportation modes. Supports multiple routes, waypoints, and real-time traffic data for driving directions."""

    # Construct request model with validation
    try:
        _request = _models.DirectionsRequest(
            query=_models.DirectionsRequestQuery(alternatives=alternatives, avoid=avoid, destination=destination, origin=origin, units=units, waypoints=waypoints, language=language, mode=mode, region=region, traffic_model=traffic_model, transit_mode=transit_mode, transit_routing_preference=transit_routing_preference)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_directions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/maps/api/directions/json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_directions")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_directions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_directions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Elevation API
@mcp.tool()
async def get_elevation(samples: float | None = Field(None, description="Number of elevation samples to return along a path. Required when querying elevation along a path instead of discrete locations. Specifies how many evenly-distributed points along the path should be sampled for elevation data.")) -> dict[str, Any] | ToolResult:
    """Retrieve elevation data for specific locations or sample elevation along a path. The API returns elevation values relative to local mean sea level, with interpolated values for locations where exact measurements aren't available."""

    # Construct request model with validation
    try:
        _request = _models.ElevationRequest(
            query=_models.ElevationRequestQuery(samples=samples)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_elevation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/maps/api/elevation/json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_elevation")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_elevation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_elevation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Geocoding API
@mcp.tool()
async def geocode_address(
    address: str | None = Field(None, description="Street address or plus code to geocode. Use standard postal service format for the country (e.g., '24 Sussex Drive Ottawa ON'). Plus codes should be formatted as global codes (4-character area + 6+ character local code) or compound codes (6+ character local code with location). At least one of address or components is required."),
    bounds: list[str] | None = Field(None, description="Bounding box to bias results toward a specific viewport region. Specified as an array of two coordinate pairs [southwest, northeast] in latitude,longitude format. Results are influenced but not strictly restricted to this area."),
    components: list[str] | None = Field(None, description="Component filters to restrict results by address elements (postal_code, country, route, locality, administrative_area). Use pipe-separated key:value pairs. Country codes should be ISO 3166-1 format. Do not repeat country, postal_code, or route filters. At least one of address or components is required."),
    location_type: list[Literal["APPROXIMATE", "GEOMETRIC_CENTER", "RANGE_INTERPOLATED", "ROOFTOP"]] | None = Field(None, description="Filter results by location precision type using pipe-separated values. Options include ROOFTOP (street address precision), RANGE_INTERPOLATED (approximated between intersections), GEOMETRIC_CENTER (polyline/polygon centers), and APPROXIMATE (characterized as approximate). Acts as a post-search filter on returned results."),
    place_id: str | None = Field(None, description="Unique textual identifier for a place returned from Place Search. Use this to retrieve the address for a known place ID instead of searching by address or coordinates."),
    result_type: list[Literal["administrative_area_level_1", "administrative_area_level_2", "administrative_area_level_3", "administrative_area_level_4", "administrative_area_level_5", "airport", "colloquial_area", "country", "intersection", "locality", "natural_feature", "neighborhood", "park", "plus_code", "political", "postal_code", "premise", "route", "street_address", "sublocality", "subpremise"]] | None = Field(None, description="Filter results by address type using pipe-separated values. Supported types include street_address, route, intersection, locality, administrative areas (level 1-5), postal_code, country, airport, park, point_of_interest, and others. Acts as a post-search filter on returned results."),
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(None, description="Language code for result formatting. Defaults to English. Supports ISO 639-1 language codes with optional region variants (e.g., en-GB, pt-BR). Street addresses are returned in local language when possible; other components use the preferred language."),
    region: Literal["ac", "ad", "ae", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "eh", "en", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy", "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "za", "zm", "zw"] | None = Field(None, description="Region code (ccTLD format) to bias results toward a specific country or region. Uses two-character country code top-level domains (e.g., 'uk' for United Kingdom, 'us' for United States). Influences result selection and ordering."),
) -> dict[str, Any] | ToolResult:
    """Convert addresses to geographic coordinates (geocoding) or coordinates to human-readable addresses (reverse geocoding). Supports street addresses, plus codes, and place IDs across multiple countries with varying accuracy levels."""

    # Construct request model with validation
    try:
        _request = _models.GeocodeRequest(
            query=_models.GeocodeRequestQuery(address=address, bounds=bounds, components=components, location_type=location_type, place_id=place_id, result_type=result_type, language=language, region=region)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for geocode_address: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/maps/api/geocode/json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "components": ("pipeDelimited", False),
        "location_type": ("pipeDelimited", False),
        "result_type": ("pipeDelimited", False),
    })

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("geocode_address")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("geocode_address", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="geocode_address",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Time Zone API
@mcp.tool()
async def get_timezone(
    location: str = Field(..., description="The geographic coordinates as a comma-separated latitude,longitude pair (e.g., 39.6034810,-119.6822510). Required to identify the location for time zone lookup."),
    timestamp: float = Field(..., description="The target date and time as a Unix timestamp (seconds since January 1, 1970 UTC). Used to determine whether daylight savings time applies at the specified location. Historical time zone changes are not considered."),
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(None, description="The language for the time zone name and results. Supports 40+ languages including major variants like English, Spanish, Chinese, and others. Defaults to English if not specified or falls back to the Accept-Language header preference."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the time zone information for a specific geographic location, including the time zone name, UTC offset, and daylight savings offset for a given date and time."""

    # Construct request model with validation
    try:
        _request = _models.TimezoneRequest(
            query=_models.TimezoneRequestQuery(language=language, location=location, timestamp=timestamp)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_timezone: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/maps/api/timezone/json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_timezone")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_timezone", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_timezone",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Roads API
@mcp.tool()
async def snap_coordinates_to_roads(
    path: list[str] = Field(..., description="A sequence of latitude/longitude coordinate pairs representing the GPS path to be snapped. Coordinates are formatted as comma-separated lat/lon values and separated by pipe characters (e.g., lat1,lon1|lat2,lon2). For best results, consecutive points should be within 300 meters of each other to ensure accurate snapping and handle GPS signal loss or noise."),
    interpolate: bool | None = Field(None, description="When enabled, generates additional interpolated points along the snapped road geometry to create a smooth, continuous path that follows road curves and geometry. The resulting path will typically contain more points than the original input. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Snaps GPS coordinates to the most likely road geometry, returning corrected points that align with actual road paths. Optionally interpolates additional points to create a smooth path following road geometry."""

    # Construct request model with validation
    try:
        _request = _models.SnapToRoadsRequest(
            query=_models.SnapToRoadsRequestQuery(path=path, interpolate=interpolate)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for snap_coordinates_to_roads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/snaptoroads"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "path": ("pipeDelimited", False),
    })

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("snap_coordinates_to_roads")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("snap_coordinates_to_roads", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="snap_coordinates_to_roads",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Roads API
@mcp.tool()
async def snap_points_to_roads(points: list[str] = Field(..., description="A list of GPS coordinates to snap to roads, provided as latitude/longitude pairs separated by pipes. Each coordinate pair should be comma-separated (e.g., latitude,longitude|latitude,longitude). Supports up to 100 points; the points do not need to form a continuous path.")) -> dict[str, Any] | ToolResult:
    """Snaps GPS coordinates to the nearest road segments. Accepts up to 100 latitude/longitude points and returns the closest matching road for each point, useful for map matching and route analysis."""

    # Construct request model with validation
    try:
        _request = _models.NearestRoadsRequest(
            query=_models.NearestRoadsRequestQuery(points=points)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for snap_points_to_roads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/nearestRoads"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "points": ("pipeDelimited", False),
    })

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("snap_points_to_roads")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("snap_points_to_roads", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="snap_points_to_roads",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Distance Matrix API
@mcp.tool()
async def calculate_distance_matrix(
    destinations: list[str] = Field(..., description="One or more destination locations where travel ends. Accepts place IDs (prefixed with 'place_id:'), addresses, latitude/longitude coordinates, plus codes, or encoded polylines. Place IDs are preferred for accuracy."),
    origins: list[str] = Field(..., description="One or more starting locations for travel calculation. Accepts place IDs (prefixed with 'place_id:'), addresses, latitude/longitude coordinates, plus codes, or encoded polylines. Multiple origins can be separated by pipe characters or provided as encoded polylines. Place IDs are preferred for accuracy."),
    avoid: str | None = Field(None, description="Specify route restrictions to avoid. Supports tolls, highways, ferries, and indoor steps. Note that restrictions bias results toward favorable routes but do not guarantee avoidance."),
    units: Literal["imperial", "metric"] | None = Field(None, description="Unit system for displaying distance results. Choose between imperial (miles/feet) or metric (kilometers/meters). Note that distance values are always returned in meters regardless of this setting."),
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(None, description="Language for result text. Defaults to English. Supports 40+ languages including regional variants. The API returns street addresses in the local language when available, transliterated to the preferred language if necessary."),
    mode: Literal["driving", "bicycling", "transit", "walking"] | None = Field(None, description="Transportation mode for route calculation. Defaults to driving. Walking and bicycling may lack clear pedestrian or bicycle paths and will include warnings. Transit mode supports optional departure/arrival times and transit preferences."),
    region: Literal["ac", "ad", "ae", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "eh", "en", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy", "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "za", "zm", "zw"] | None = Field(None, description="Region bias using two-character country code (ccTLD format). Influences result selection and ordering. Defaults to 'en'. Use country-specific codes like 'uk' for United Kingdom or 'gb' for ISO standard."),
    traffic_model: Literal["best_guess", "pessimistic", "optimistic"] | None = Field(None, description="Traffic prediction model for driving directions with departure times. 'best_guess' (default) balances historical and live traffic; 'pessimistic' estimates longer times; 'optimistic' estimates shorter times. Only applies to driving mode with specified departure_time."),
    transit_mode: str | None = Field(None, description="Preferred transit modes to favor in route calculation. Supports bus, subway, train, tram, and rail (combination of train/tram/subway). Multiple modes can be specified separated by pipe characters. Only applies to transit mode."),
    transit_routing_preference: Literal["less_walking", "fewer_transfers"] | None = Field(None, description="Transit route preferences to bias results. Choose 'less_walking' to minimize walking distance or 'fewer_transfers' to reduce transfer count. Only applies to transit mode."),
) -> dict[str, Any] | ToolResult:
    """Calculate travel distances and durations between multiple origin and destination points using various transportation modes. Returns a matrix of distance and time values for each origin-destination pair based on Google Maps routing."""

    # Construct request model with validation
    try:
        _request = _models.DistanceMatrixRequest(
            query=_models.DistanceMatrixRequestQuery(avoid=avoid, destinations=destinations, origins=origins, units=units, language=language, mode=mode, region=region, traffic_model=traffic_model, transit_mode=transit_mode, transit_routing_preference=transit_routing_preference)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_distance_matrix: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/maps/api/distancematrix/json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "destinations": ("pipeDelimited", False),
        "origins": ("pipeDelimited", False),
    })

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_distance_matrix")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_distance_matrix", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_distance_matrix",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Places API
@mcp.tool()
async def get_place_details(
    place_id: str = Field(..., description="Unique identifier for the place, obtained from a Place Search request. This ID is required to retrieve the place's detailed information."),
    fields: list[str] | None = Field(None, description="Comma-separated list of specific place data fields to return (e.g., formatted_address,name,geometry). Use forward slashes for nested fields (e.g., opening_hours/open_now). Omit to return default fields, or use '*' for all available fields. Fields are categorized as Basic (no extra charge), Contact, or Atmosphere (higher billing rates).", min_length=1),
    sessiontoken: str | None = Field(None, description="Unique session identifier for grouping related autocomplete and details requests for billing optimization. Generate a fresh UUID for each new user session and reuse it across multiple requests within the same session."),
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(None, description="Language code for returned results (e.g., en, es, fr, ja). Defaults to English. The API will attempt to use the Accept-Language header if not specified. Affects address formatting and review translation preferences."),
    region: Literal["ac", "ad", "ae", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "eh", "en", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy", "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "za", "zm", "zw"] | None = Field(None, description="Two-character country/region code (ccTLD format, e.g., us, gb, de) to bias results toward a specific region. Defaults to 'en'. Influences address interpretation and result prioritization."),
    reviews_sort: str | None = Field(None, description="Sort order for returned reviews: 'most_relevant' (default, language-aware) or 'newest' (chronological). Recommend displaying the sort method to end users."),
    reviews_no_translations: bool | None = Field(None, description="Set to true to return reviews in their original language without translation, or false/omitted to enable translation using the specified or preferred language."),
) -> dict[str, Any] | ToolResult:
    """Retrieve comprehensive information about a specific place including address, contact details, opening hours, ratings, and reviews. Use a place ID from a prior search to fetch detailed establishment or location data."""

    # Construct request model with validation
    try:
        _request = _models.PlaceDetailsRequest(
            query=_models.PlaceDetailsRequestQuery(place_id=place_id, fields=fields, sessiontoken=sessiontoken, language=language, region=region, reviews_sort=reviews_sort, reviews_no_translations=reviews_no_translations)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_place_details: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/maps/api/place/details/json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields": ("form", False),
    })

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_place_details")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_place_details", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_place_details",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Places API
@mcp.tool()
async def search_place_by_text(
    input_: str = Field(..., alias="input", description="The search text input, which can be a place name, street address, or phone number. The API returns candidate matches ordered by perceived relevance based on this input."),
    inputtype: Literal["textquery", "phonenumber"] = Field(..., description="The type of input being searched: 'textquery' for place names and addresses, or 'phonenumber' for phone numbers in international E.164 format (e.g., +1-555-0123)."),
    fields: list[str] | None = Field(None, description="Comma-separated list of place data fields to return in the response. Omitting this parameter returns only the place_id. Fields are categorized as Basic (no additional charge), Contact, or Atmosphere (higher billing rates). Use forward slash notation for compound fields (e.g., opening_hours/open_now). Specify '*' to request all available fields.", min_length=1),
    locationbias: str | None = Field(None, description="Optional geographic bias to prefer results in a specific area. Specify 'ipbias' to use IP-based biasing, a circular area using 'circle:radius_meters@latitude,longitude', or a rectangular area using 'rectangle:south,west|north,east'. If omitted, IP address biasing is applied by default."),
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(None, description="The language for returned results. Defaults to English. Affects how addresses and place names are displayed, with the API attempting to provide locally-readable transliterations when applicable. Supports 40+ language codes including regional variants (e.g., en-GB, pt-BR)."),
) -> dict[str, Any] | ToolResult:
    """Search for a place using text input such as a name, address, or phone number. Returns matching places with optional detailed information based on requested fields."""

    # Construct request model with validation
    try:
        _request = _models.FindPlaceFromTextRequest(
            query=_models.FindPlaceFromTextRequestQuery(fields=fields, input_=input_, inputtype=inputtype, locationbias=locationbias, language=language)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_place_by_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/maps/api/place/findplacefromtext/json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_query = _serialize_query(_http_query, {
        "fields": ("form", False),
    })

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_place_by_text")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_place_by_text", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_place_by_text",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Places API
@mcp.tool()
async def search_nearby_places(
    location: str = Field(..., description="Center point for the search area, specified as latitude and longitude separated by a comma (e.g., 40,-110)."),
    radius: float = Field(..., description="Search radius in meters around the location. Maximum values vary by search type: up to 50,000 meters for keyword or name searches, dynamically adjusted for searches without keywords or names. When rankby is set to 'distance', this parameter is not allowed."),
    keyword: str | None = Field(None, description="Search term for places, such as a business name, address, or category (e.g., 'restaurant', '123 Main Street'). Combining location information in this parameter may conflict with the location and radius parameters. Omitting this parameter will exclude temporarily or permanently closed places from results."),
    opennow: bool | None = Field(None, description="When enabled, returns only places currently open for business. Places without specified opening hours in the Google Places database will be excluded."),
    rankby: Literal["prominence", "distance"] | None = Field(None, description="Determines result ordering: 'prominence' (default) ranks by importance and requires the radius parameter, while 'distance' orders by proximity and requires at least one of keyword, name, or type but disallows radius."),
    type_: str | None = Field(None, alias="type", description="Restrict results to a single place type (e.g., 'hospital', 'pharmacy'). Only the first type is used if multiple are provided. Combining the same value as both keyword and type may return no results."),
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(None, description="Language for result content, supporting 40+ languages including regional variants (e.g., 'en', 'es', 'zh-CN'). Defaults to 'en' if not specified. The API uses the Accept-Language header as a fallback and returns street addresses in the local language when possible."),
) -> dict[str, Any] | ToolResult:
    """Search for places within a specified geographic area. Refine results by keywords, place types, or business status to discover relevant locations near a given coordinate."""

    # Construct request model with validation
    try:
        _request = _models.NearbySearchRequest(
            query=_models.NearbySearchRequestQuery(keyword=keyword, location=location, opennow=opennow, rankby=rankby, radius=radius, type_=type_, language=language)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_nearby_places: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/maps/api/place/nearbysearch/json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_nearby_places")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_nearby_places", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_nearby_places",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Places API
@mcp.tool()
async def search_places_by_text(
    query: str = Field(..., description="The search query string, such as a place name (e.g., 'pizza'), address (e.g., '123 Main Street'), or category (e.g., 'restaurants'). Results are ranked by perceived relevance to this query."),
    radius: float = Field(..., description="Search radius in meters, up to a maximum of 50,000 meters. Results within this circle are preferred, though places outside may still be returned. The API may adjust this radius based on result density."),
    opennow: bool | None = Field(None, description="Filter results to only include places currently open for business. Places without specified opening hours in the database will be excluded when this filter is applied."),
    type_: str | None = Field(None, alias="type", description="Restrict results to a single place type from the supported types list. If multiple types are provided, only the first is used; others are ignored."),
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(None, description="Language code for result content. Defaults to English. Affects how addresses and place names are returned and transliterated. The API uses the Accept-Language header if not specified."),
    region: Literal["ac", "ad", "ae", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "eh", "en", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy", "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "za", "zm", "zw"] | None = Field(None, description="Two-character region code (ccTLD format, e.g., 'us', 'gb', 'uk') to bias results to a specific country or region. Defaults to 'en'."),
) -> dict[str, Any] | ToolResult:
    """Search for places using a text query string, optionally filtered by location radius, type, and opening status. Returns a ranked list of matching places with basic information."""

    # Construct request model with validation
    try:
        _request = _models.TextSearchRequest(
            query=_models.TextSearchRequestQuery(opennow=opennow, query=query, radius=radius, type_=type_, language=language, region=region)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_places_by_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/maps/api/place/textsearch/json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_places_by_text")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_places_by_text", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_places_by_text",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Places API
@mcp.tool()
async def get_place_photo(photo_reference: str = Field(..., description="A unique identifier for the photo, obtained from Place Search, Nearby Search, Text Search, or Place Details requests. This reference is required to retrieve the actual photo image.")) -> dict[str, Any] | ToolResult:
    """Retrieve a high-quality photo for a place using a photo reference. Returns the image data that can be resized and displayed in your application, with attribution requirements included when necessary."""

    # Construct request model with validation
    try:
        _request = _models.PlacePhotoRequest(
            query=_models.PlacePhotoRequestQuery(photo_reference=photo_reference)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_place_photo: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/maps/api/place/photo"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_place_photo")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_place_photo", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_place_photo",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Places API
@mcp.tool()
async def get_query_suggestions(
    input_: str = Field(..., alias="input", description="The search text to get predictions for. The service matches this string against both full words and substrings to return relevant suggestions ordered by perceived relevance."),
    radius: float = Field(..., description="The search radius in meters within which to prefer returning results. Maximum of 50,000 meters. Results outside this radius may still be returned. Helps bias suggestions to a geographic area when combined with a location."),
    offset: float | None = Field(None, description="Optional character position in the input text where matching should stop. Useful for matching against partial input (e.g., matching \"Goo\" when input is \"Google\"). Typically set to the text caret position. If omitted, the entire input term is used for matching."),
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(None, description="The language for returned results. Defaults to English. Supports 40+ languages including regional variants (e.g., en-GB, pt-BR). If not specified, the API attempts to use the language from the Accept-Language header."),
) -> dict[str, Any] | ToolResult:
    """Get autocomplete suggestions for geographic queries as users type. Returns predicted queries based on categorical searches like "pizza near New York", matching both full words and substrings."""

    # Construct request model with validation
    try:
        _request = _models.QueryAutocompleteRequest(
            query=_models.QueryAutocompleteRequestQuery(input_=input_, offset=offset, radius=radius, language=language)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_query_suggestions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/maps/api/place/queryautocomplete/json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_query_suggestions")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_query_suggestions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_query_suggestions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Places API
@mcp.tool()
async def autocomplete_place(
    input_: str = Field(..., alias="input", description="The search text to match against place names, addresses, and plus codes. The service returns predictions ordered by perceived relevance to this input."),
    radius: float = Field(..., description="The search radius in meters within which to prefer results. Maximum 50,000 meters for autocomplete. Results outside this radius may still be returned if they match the input."),
    sessiontoken: str | None = Field(None, description="A unique identifier for this autocomplete session used for billing optimization. Generate a fresh UUID for each new user search session. All requests within a session must use the same API key and project."),
    components: str | None = Field(None, description="Restrict results to specific countries using ISO 3166-1 Alpha-2 country codes. Separate multiple countries with a pipe character (e.g., country:us|country:ca). Up to 5 countries can be specified."),
    strictbounds: bool | None = Field(None, description="When enabled, returns only places strictly within the region defined by location and radius, excluding any matches outside the boundary."),
    offset: float | None = Field(None, description="The character position in the input text where matching should end. Useful for matching against partial words as the user types. If omitted, the entire input term is used for matching."),
    origin: str | None = Field(None, description="The starting point for calculating straight-line distance to results. Specify as latitude,longitude in decimal degrees. Distance is returned in the response as distance_meters."),
    locationbias: str | None = Field(None, description="Prefer results in a specified area using IP-based biasing, a circular radius, or a rectangular bounding box. Circular format: circle:radius_in_meters@latitude,longitude. Rectangular format: rectangle:south,west|north,east."),
    locationrestriction: str | None = Field(None, description="Strictly limit results to a specified area using a circular radius or rectangular bounding box. Unlike location bias, results outside this area will not be returned. Circular format: circle:radius_in_meters@latitude,longitude. Rectangular format: rectangle:south,west|north,east."),
    types: str | None = Field(None, description="Filter results to specific place types. Specify up to 5 types separated by pipe characters (e.g., book_store|cafe), or use a single type collection filter. See supported types documentation for valid values."),
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(None, description="The language for returned results. Defaults to English. Affects how place names and addresses are translated and formatted. See supported languages list for valid codes."),
    region: Literal["ac", "ad", "ae", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "eh", "en", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy", "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "za", "zm", "zw"] | None = Field(None, description="The region code as a ccTLD (country code top-level domain) to bias results and interpretation. Defaults to 'en'. Use two-character codes like 'uk' for United Kingdom or 'de' for Germany."),
) -> dict[str, Any] | ToolResult:
    """Get place predictions as a user types a geographic search query. Returns matching businesses, addresses, and points of interest based on the input text, with optional geographic filtering and biasing."""

    # Construct request model with validation
    try:
        _request = _models.AutocompleteRequest(
            query=_models.AutocompleteRequestQuery(input_=input_, sessiontoken=sessiontoken, components=components, strictbounds=strictbounds, offset=offset, origin=origin, locationbias=locationbias, locationrestriction=locationrestriction, radius=radius, types=types, language=language, region=region)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for autocomplete_place: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/maps/api/place/autocomplete/json"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("autocomplete_place")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("autocomplete_place", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="autocomplete_place",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Street View API
@mcp.tool()
async def get_street_view(
    size: str = Field(..., description="Specifies the output image dimensions as width by height in pixels. Both dimensions must not exceed 640 pixels; larger values default to 640. Use the format widthxheight (for example, 600x400)."),
    fov: float | None = Field(None, description="Controls the horizontal zoom level of the image in degrees. Accepts values from 0 to 120, where smaller values provide higher zoom. Defaults to 90 degrees if not specified."),
    heading: float | None = Field(None, description="Sets the compass direction the camera faces, using values from 0 to 360 degrees where 0 and 360 represent North, 90 represents East, and 180 represents South. If omitted, the camera automatically orients toward the specified location from the nearest available photograph."),
    pano: str | None = Field(None, description="Targets a specific panorama by its unique identifier. Panorama IDs are generally persistent but may change as Street View imagery is updated."),
    pitch: float | None = Field(None, description="Adjusts the vertical camera angle relative to the Street View vehicle. Positive values tilt upward (90 degrees points straight up), negative values tilt downward (-90 degrees points straight down). Defaults to 0 for horizontal orientation."),
    source: Literal["default", "outdoor"] | None = Field(None, description="Restricts Street View results to specific imagery sources. Use 'default' to search all available sources, or 'outdoor' to exclude indoor collections. Note that outdoor panoramas may not exist for all locations, and PhotoSpheres are excluded from outdoor searches due to unknown indoor/outdoor classification."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a static Street View image for a specified location or panorama. Returns a static image without interactive elements, useful for embedding Street View imagery in web pages."""

    # Construct request model with validation
    try:
        _request = _models.StreetViewRequest(
            query=_models.StreetViewRequestQuery(fov=fov, heading=heading, pano=pano, pitch=pitch, size=size, source=source)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_street_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/maps/api/streetview"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_street_view")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_street_view", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_street_view",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: Street View API
@mcp.tool()
async def get_street_view_metadata(
    heading: float | None = Field(None, description="The compass heading of the camera in degrees, ranging from 0 to 360 where 0 and 360 indicate North, 90 indicates East, and 180 indicates South. If not specified, the heading will be automatically calculated to point toward the location from the nearest available photograph."),
    pano: str | None = Field(None, description="A specific panorama ID to retrieve metadata for. Panorama IDs are generally stable identifiers, though they may change as Street View imagery is updated."),
    pitch: float | None = Field(None, description="The vertical angle of the camera relative to the Street View vehicle, ranging from -90 degrees (straight down) to 90 degrees (straight up), with 0 as the default horizontal position."),
    size: str | None = Field(None, description="The output image dimensions specified as width by height in pixels (e.g., 600x400 for a 600-pixel wide by 400-pixel high image)."),
    source: Literal["default", "outdoor"] | None = Field(None, description="Limits Street View searches to specific sources: use 'default' to search all available sources, or 'outdoor' to search only outdoor collections and exclude indoor panoramas. Note that outdoor panoramas may not exist for all locations, and PhotoSpheres are excluded from outdoor searches since their indoor/outdoor status cannot be determined."),
) -> dict[str, Any] | ToolResult:
    """Retrieve metadata about a Street View panorama at a specific location or panorama ID, including availability, coordinates, panorama ID, capture date, and copyright information to customize error handling in your application."""

    # Construct request model with validation
    try:
        _request = _models.StreetViewMetadataRequest(
            query=_models.StreetViewMetadataRequestQuery(heading=heading, pano=pano, pitch=pitch, size=size, source=source)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_street_view_metadata: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/maps/api/streetview/metadata"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_street_view_metadata")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_street_view_metadata", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_street_view_metadata",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
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
        print("  python google_maps_platform_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Google Maps Platform MCP Server")

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
    logger.info("Starting Google Maps Platform MCP Server")
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

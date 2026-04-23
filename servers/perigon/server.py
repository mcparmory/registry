#!/usr/bin/env python3
"""
Perigon API MCP Server

API Info:
- Contact: Perigon Support <data@perigon.io> (https://docs.perigon.io/)

Generated: 2026-04-23 21:36:15 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://api.perigon.io")
SERVER_NAME = "Perigon API"
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
    'apiKeyAuth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["apiKeyAuth"] = _auth.APIKeyAuth(env_var="API_KEY", location="query", param_name="apiKey")
    logging.info("Authentication configured: apiKeyAuth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for apiKeyAuth not configured: {error_msg}")
    _auth_handlers["apiKeyAuth"] = None

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

mcp = FastMCP("Perigon API", middleware=[_JsonCoercionMiddleware()])

# Tags: v1
@mcp.tool()
async def search_articles(
    title: str | None = Field(None, description="Search within article headlines and titles. Supports Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (*) for pattern variations."),
    desc: str | None = Field(None, description="Search within article description fields. Supports Boolean expressions, exact phrase matching with quotes, and wildcards for flexible pattern matching."),
    content: str | None = Field(None, description="Search within the full article body content. Supports Boolean logic, exact phrase matching with quotes, and wildcards for comprehensive content searching."),
    summary: str | None = Field(None, description="Search within article summary fields. Supports Boolean expressions, exact phrase matching with quotes, and wildcards for flexible pattern matching."),
    url: str | None = Field(None, description="Search query on the URL field. Useful for filtering articles from specific website sections or domains (e.g., source=cnn.com&url=travel)."),
    article_id: list[str] | None = Field(None, alias="articleId", description="Retrieve specific articles by their unique identifiers. Provide one or more article IDs to return a targeted collection."),
    cluster_id: list[str] | None = Field(None, alias="clusterId", description="Filter results to articles within a specific related content cluster. Returns articles grouped together as part of Perigon Stories based on topic relevance."),
    sort_by: Literal["relevance", "date", "reverseDate", "reverseAddDate", "addDate", "pubDate", "refreshDate"] | None = Field(None, alias="sortBy", description="Determines result ordering. Choose from relevance (default), date/pubDate (newest first), reverseDate (oldest first), addDate (newest ingestion first), reverseAddDate (oldest ingestion first), or refreshDate (most recently updated first)."),
    page: str | None = Field(None, description="The page number of results to retrieve in paginated responses. Starts at 0 and supports up to page 10000."),
    size: str | None = Field(None, description="Number of articles to return per page. Accepts values from 0 to 1000."),
    add_date_from: str | None = Field(None, alias="addDateFrom", description="Filter for articles added to Perigon's system after this date. Accepts ISO 8601 format (e.g., 2022-02-01T00:00:00) or simple date format (yyyy-mm-dd)."),
    add_date_to: str | None = Field(None, alias="addDateTo", description="Filter for articles added to Perigon's system before this date. Accepts ISO 8601 format (e.g., 2022-02-01T23:59:59) or simple date format (yyyy-mm-dd)."),
    refresh_date_from: str | None = Field(None, alias="refreshDateFrom", description="Filter for articles refreshed or updated in Perigon's system after this date. May differ from addDateFrom for updated content. Accepts ISO 8601 or simple date format."),
    refresh_date_to: str | None = Field(None, alias="refreshDateTo", description="Filter for articles refreshed or updated in Perigon's system before this date. May differ from addDateTo for updated content. Accepts ISO 8601 or simple date format."),
    medium: list[str] | None = Field(None, description="Filter by content medium type. Choose Article for written content or Video for video-based stories. Multiple values create an OR filter."),
    source: list[str] | None = Field(None, description="Filter by specific publisher domains or subdomains. Supports wildcards (* and ?) for pattern matching (e.g., *.cnn.com). Multiple values create an OR filter."),
    source_group: list[str] | None = Field(None, alias="sourceGroup", description="Filter using Perigon's curated publisher bundles (e.g., top100, top25crypto). Multiple values create an OR filter to include articles from any specified bundle."),
    exclude_source_group: list[str] | None = Field(None, alias="excludeSourceGroup", description="Exclude articles from specified Perigon source groups. Multiple values create an AND-exclude filter, removing content from publishers in any specified bundle."),
    exclude_source: list[str] | None = Field(None, alias="excludeSource", description="Exclude articles from specific publisher domains or subdomains. Supports wildcards (* and ?) for pattern matching. Multiple values create an AND-exclude filter."),
    watchlist: list[str] | None = Field(None, description="Filter articles using watchlists of people and companies. Multiple values create an OR filter to include articles mentioning any entity from specified watchlists."),
    exclude_watchlist: list[str] | None = Field(None, alias="excludeWatchlist", description="Exclude articles mentioning entities from specified watchlists. Multiple values create an AND-exclude filter, removing content about any entity in the specified watchlists."),
    paywall: bool | None = Field(None, description="Filter by paywall status. Set to true to show only paywalled sources, or false to show only free sources."),
    author: list[str] | None = Field(None, description="Filter articles by specific author names using exact matching. Multiple values create an OR filter to find articles by any specified author."),
    exclude_author: list[str] | None = Field(None, alias="excludeAuthor", description="Exclude articles written by specific authors. Any article with an author name matching an entry will be omitted. Multiple values create an AND-exclude filter."),
    journalist_id: list[str] | None = Field(None, alias="journalistId", description="Filter by unique journalist identifiers (available via the Journalist API or matchedAuthors field). Multiple values create an OR filter."),
    exclude_journalist_id: list[str] | None = Field(None, alias="excludeJournalistId", description="Exclude articles written by specific journalists identified by their unique IDs. Multiple values create an AND-exclude filter."),
    language: list[str] | None = Field(None, description="Filter articles by language using ISO 639 two-letter codes (e.g., en, es, fr). Multiple values create an OR filter."),
    exclude_language: list[str] | None = Field(None, alias="excludeLanguage", description="Exclude articles in specific languages using ISO 639 two-letter codes. Multiple values create an AND-exclude filter."),
    search_translation: bool | None = Field(None, alias="searchTranslation", description="Expand search to include translated content fields for non-English articles. When enabled, searches translated title, description, and content fields."),
    label: list[str] | None = Field(None, description="Filter articles by editorial labels such as Opinion, Paid-news, Non-news, Fact Check, or Press Release. Multiple values create an OR filter."),
    exclude_label: list[str] | None = Field(None, alias="excludeLabel", description="Exclude articles with specific editorial labels. Multiple values create an AND-exclude filter, removing all content with any specified label."),
    category: list[str] | None = Field(None, description="Filter by general article categories (e.g., Tech, Politics). Use 'none' to search uncategorized articles. Multiple values create an OR filter."),
    exclude_category: list[str] | None = Field(None, alias="excludeCategory", description="Exclude articles with specific categories. Multiple values create an AND-exclude filter, removing all content with any specified category."),
    topic: list[str] | None = Field(None, description="Filter by specific topics (e.g., Markets, Crime, Cryptocurrency, College Sports). Topics are more granular than categories and articles can have multiple topics. Multiple values create an OR filter."),
    exclude_topic: list[str] | None = Field(None, alias="excludeTopic", description="Exclude articles with specific topics. Multiple values create an AND-exclude filter, removing all content with any specified topic."),
    link_to: str | None = Field(None, alias="linkTo", description="Returns only articles that contain links to the specified URL pattern. Matches against the links field in article responses."),
    show_reprints: bool | None = Field(None, alias="showReprints", description="Controls whether to include reprinted content in results. When true (default), shows syndicated articles from wire services like AP or Reuters that appear on multiple sites."),
    reprint_group_id: str | None = Field(None, alias="reprintGroupId", description="Returns all articles in a specific reprint group, including the original article and all known reprints. Use to see all versions of the same content."),
    city: list[str] | None = Field(None, description="Filter articles where a specified city plays a central role in the content, beyond mere mentions. Multiple values create an OR filter."),
    exclude_city: list[str] | None = Field(None, alias="excludeCity", description="Exclude articles associated with specified cities. Articles tagged with any specified city will be filtered out."),
    state: list[str] | None = Field(None, description="Filter articles where a specified state plays a central role in the content, beyond mere mentions. Multiple values create an OR filter."),
    exclude_state: list[str] | None = Field(None, alias="excludeState", description="Exclude articles associated with specified states. Articles tagged with any specified state will be filtered out."),
    county: list[str] | None = Field(None, description="Filter articles by specific counties. Only articles tagged with one of these counties will be included."),
    exclude_county: list[str] | None = Field(None, alias="excludeCounty", description="Exclude articles from specific counties or administrative divisions. County names should match the format used in article metadata (e.g., 'Los Angeles County', 'Cook County')."),
    country: list[str] | None = Field(None, description="Filter articles by country code. Multiple values create an OR filter."),
    location: list[str] | None = Field(None, description="Return articles with specified location attributes. Location format uses ':' between key and value, and '::' between attributes (e.g., 'city:New York::state:NY')."),
    lat: float | None = Field(None, description="Latitude of the center point for geographic search. Must be between -90 and 90 degrees.", ge=-90, le=90),
    lon: float | None = Field(None, description="Longitude of the center point for geographic search. Must be between -180 and 180 degrees.", ge=-180, le=180),
    max_distance: float | None = Field(None, alias="maxDistance", description="Maximum distance in kilometers from the center point for geographic search. Must be between 1 and 300 km.", ge=1, le=300),
    source_city: list[str] | None = Field(None, alias="sourceCity", description="Find articles published by sources located within specified cities."),
    exclude_source_city: list[str] | None = Field(None, alias="excludeSourceCity", description="Exclude articles published by sources located within specified cities."),
    source_county: list[str] | None = Field(None, alias="sourceCounty", description="Find articles published by sources located within specified counties."),
    exclude_source_county: list[str] | None = Field(None, alias="excludeSourceCounty", description="Exclude articles published by sources located within specified counties."),
    source_country: list[str] | None = Field(None, alias="sourceCountry", description="Find articles published by sources located within specified countries. Use 2-character country codes (e.g., us, gb)."),
    exclude_source_country: list[str] | None = Field(None, alias="excludeSourceCountry", description="Exclude articles published by sources located within specified countries. Use 2-character country codes (e.g., us, gb)."),
    source_state: list[str] | None = Field(None, alias="sourceState", description="Find articles published by sources located within specified states."),
    exclude_source_state: list[str] | None = Field(None, alias="excludeSourceState", description="Exclude articles published by sources located within specified states."),
    person_wikidata_id: list[str] | None = Field(None, alias="personWikidataId", description="Filter articles by Wikidata IDs of mentioned people. Refer to the /people endpoint for available tracked individuals. Multiple values create an OR filter."),
    exclude_person_wikidata_id: list[str] | None = Field(None, alias="excludePersonWikidataId", description="Exclude articles mentioning people with specific Wikidata IDs. Uses precise identifiers to avoid name ambiguity. Multiple values create an AND-exclude filter."),
    exclude_person_name: list[str] | None = Field(None, alias="excludePersonName", description="Exclude articles mentioning specific people by name. Multiple values create an AND-exclude filter."),
    company_id: list[str] | None = Field(None, alias="companyId", description="Filter articles by company identifiers. Refer to the /companies endpoint for available tracked companies. Multiple values create an OR filter."),
    exclude_company_id: list[str] | None = Field(None, alias="excludeCompanyId", description="Exclude articles mentioning companies with specific identifiers. Multiple values create an AND-exclude filter."),
    company_domain: list[str] | None = Field(None, alias="companyDomain", description="Filter articles by company domains (e.g., apple.com). Consult the /companies endpoint for available company entities. Multiple values create an OR filter."),
    exclude_company_domain: list[str] | None = Field(None, alias="excludeCompanyDomain", description="Exclude articles related to companies with specific domains. Multiple values create an AND-exclude filter."),
    company_symbol: list[str] | None = Field(None, alias="companySymbol", description="Filter articles by company stock symbols (ticker symbols). Consult the /companies endpoint for available symbols. Multiple values create an OR filter."),
    exclude_company_symbol: list[str] | None = Field(None, alias="excludeCompanySymbol", description="Exclude articles related to companies with specific stock symbols. Multiple values create an AND-exclude filter."),
    positive_sentiment_from: float | None = Field(None, alias="positiveSentimentFrom", description="Filter articles with positive sentiment score greater than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger positive tone."),
    positive_sentiment_to: float | None = Field(None, alias="positiveSentimentTo", description="Filter articles with positive sentiment score less than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger positive tone."),
    neutral_sentiment_from: float | None = Field(None, alias="neutralSentimentFrom", description="Filter articles with neutral sentiment score greater than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger neutral tone."),
    neutral_sentiment_to: float | None = Field(None, alias="neutralSentimentTo", description="Filter articles with neutral sentiment score less than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger neutral tone."),
    negative_sentiment_from: float | None = Field(None, alias="negativeSentimentFrom", description="Filter articles with negative sentiment score greater than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger negative tone."),
    negative_sentiment_to: float | None = Field(None, alias="negativeSentimentTo", description="Filter articles with negative sentiment score less than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger negative tone."),
    taxonomy: list[str] | None = Field(None, description="Filter by Google Content Categories using full category names (e.g., /Finance/Banking/Other, /Finance/Investing/Funds). Refer to Google's category list for complete options. Multiple values create an OR filter."),
    prefix_taxonomy: str | None = Field(None, alias="prefixTaxonomy", description="Filter by Google Content Categories using category prefix only (e.g., /Finance). Matches all categories starting with the specified prefix."),
) -> dict[str, Any] | ToolResult:
    """Search and filter news articles across Perigon's database using flexible query parameters. Returns paginated results with support for text search, date ranges, geographic filters, entity mentions, sentiment analysis, and content categorization."""

    _page = _parse_int(page)
    _size = _parse_int(size)

    # Construct request model with validation
    try:
        _request = _models.SearchArticlesRequest(
            query=_models.SearchArticlesRequestQuery(title=title, desc=desc, content=content, summary=summary, url=url, article_id=article_id, cluster_id=cluster_id, sort_by=sort_by, page=_page, size=_size, add_date_from=add_date_from, add_date_to=add_date_to, refresh_date_from=refresh_date_from, refresh_date_to=refresh_date_to, medium=medium, source=source, source_group=source_group, exclude_source_group=exclude_source_group, exclude_source=exclude_source, watchlist=watchlist, exclude_watchlist=exclude_watchlist, paywall=paywall, author=author, exclude_author=exclude_author, journalist_id=journalist_id, exclude_journalist_id=exclude_journalist_id, language=language, exclude_language=exclude_language, search_translation=search_translation, label=label, exclude_label=exclude_label, category=category, exclude_category=exclude_category, topic=topic, exclude_topic=exclude_topic, link_to=link_to, show_reprints=show_reprints, reprint_group_id=reprint_group_id, city=city, exclude_city=exclude_city, state=state, exclude_state=exclude_state, county=county, exclude_county=exclude_county, country=country, location=location, lat=lat, lon=lon, max_distance=max_distance, source_city=source_city, exclude_source_city=exclude_source_city, source_county=source_county, exclude_source_county=exclude_source_county, source_country=source_country, exclude_source_country=exclude_source_country, source_state=source_state, exclude_source_state=exclude_source_state, person_wikidata_id=person_wikidata_id, exclude_person_wikidata_id=exclude_person_wikidata_id, exclude_person_name=exclude_person_name, company_id=company_id, exclude_company_id=exclude_company_id, company_domain=company_domain, exclude_company_domain=exclude_company_domain, company_symbol=company_symbol, exclude_company_symbol=exclude_company_symbol, positive_sentiment_from=positive_sentiment_from, positive_sentiment_to=positive_sentiment_to, neutral_sentiment_from=neutral_sentiment_from, neutral_sentiment_to=neutral_sentiment_to, negative_sentiment_from=negative_sentiment_from, negative_sentiment_to=negative_sentiment_to, taxonomy=taxonomy, prefix_taxonomy=prefix_taxonomy)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_articles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/articles/all"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_articles")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_articles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_articles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: v1
@mcp.tool()
async def search_companies(
    id_: list[str] | None = Field(None, alias="id", description="Filter results to companies with specific unique identifiers. Accepts multiple IDs as an OR filter (returns companies matching any ID in the list)."),
    symbol: list[str] | None = Field(None, description="Filter results to companies with specific stock ticker symbols (e.g., AAPL, MSFT). Accepts multiple symbols as an OR filter."),
    domain: list[str] | None = Field(None, description="Filter results to companies with specific domain names or websites (e.g., apple.com, microsoft.com). Accepts multiple domains as an OR filter."),
    country: list[str] | None = Field(None, description="Filter results to companies headquartered in specific countries. Accepts multiple countries as an OR filter."),
    exchange: list[str] | None = Field(None, description="Filter results to companies listed on specific stock exchanges (e.g., NASDAQ, NYSE). Accepts multiple exchanges as an OR filter."),
    num_employees_from: str | None = Field(None, alias="numEmployeesFrom", description="Filter for companies with at least this minimum number of employees. Must be a positive integer."),
    num_employees_to: str | None = Field(None, alias="numEmployeesTo", description="Filter for companies with no more than this maximum number of employees. Must be a positive integer."),
    ipo_from: str | None = Field(None, alias="ipoFrom", description="Filter for companies that went public on or after this date. Accepts ISO 8601 format (e.g., 2023-01-01T00:00:00) or yyyy-mm-dd format."),
    ipo_to: str | None = Field(None, alias="ipoTo", description="Filter for companies that went public on or before this date. Accepts ISO 8601 format (e.g., 2023-12-31T23:59:59) or yyyy-mm-dd format."),
    name: str | None = Field(None, description="Search within company names using Boolean operators (AND, OR, NOT), exact phrases with quotes, and wildcards (* for multiple characters, ? for single character)."),
    industry: str | None = Field(None, description="Filter by company industry classifications using Boolean operators (AND, OR, NOT), exact phrases with quotes, and wildcards (* for multiple characters, ? for single character)."),
    sector: str | None = Field(None, description="Filter by company sector classifications using Boolean operators (AND, OR, NOT), exact phrases with quotes, and wildcards (* for multiple characters, ? for single character)."),
    size: str | None = Field(None, description="Number of companies to return per page. Must be between 1 and 100 inclusive."),
    page: str | None = Field(None, description="Zero-indexed page number to retrieve from the paginated results. Must be 0 or greater."),
) -> dict[str, Any] | ToolResult:
    """Search and filter companies tracked by Perigon using multiple criteria including name, domain, ticker symbol, industry, sector, and company metadata. Supports Boolean search logic for flexible querying across company attributes."""

    _num_employees_from = _parse_int(num_employees_from)
    _num_employees_to = _parse_int(num_employees_to)
    _size = _parse_int(size)
    _page = _parse_int(page)

    # Construct request model with validation
    try:
        _request = _models.SearchCompaniesRequest(
            query=_models.SearchCompaniesRequestQuery(id_=id_, symbol=symbol, domain=domain, country=country, exchange=exchange, num_employees_from=_num_employees_from, num_employees_to=_num_employees_to, ipo_from=ipo_from, ipo_to=ipo_to, name=name, industry=industry, sector=sector, size=_size, page=_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_companies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/companies/all"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_companies")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_companies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_companies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: v1
@mcp.tool()
async def search_journalists(
    id_: list[str] | None = Field(None, alias="id", description="Filter by one or more journalist IDs. Matches any journalist whose ID is in the provided list (OR operation)."),
    name: str | None = Field(None, description="Search journalist names using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (* and ?) for pattern matching."),
    twitter: str | None = Field(None, description="Filter by exact Twitter handle (without the @ symbol)."),
    size: str | None = Field(None, description="Number of results to return per page. Must be between 0 and 1,000."),
    page: str | None = Field(None, description="Zero-indexed page number for pagination. Use 0 for the first page."),
    source: list[str] | None = Field(None, description="Filter by publisher domains where journalists write. Supports wildcards (* and ?) for pattern matching (e.g., *.cnn.com). Matches any domain in the list (OR operation)."),
    topic: list[str] | None = Field(None, description="Filter by specific topics journalists cover (e.g., 'Economy', 'Real Estate', 'Cryptocurrency'). Matches any topic in the list (OR operation)."),
    category: list[str] | None = Field(None, description="Filter by general content categories journalists cover (e.g., 'Tech', 'Politics'). Matches any category in the list (OR operation)."),
    label: list[str] | None = Field(None, description="Filter by article labels most commonly associated with journalists' work (e.g., 'Opinion', 'Pop Culture'). Matches any label in the list (OR operation)."),
    country: list[str] | None = Field(None, description="Filter by countries journalists commonly cover. Use ISO 3166-1 alpha-2 country codes in lowercase (e.g., us, gb, jp). Matches any country in the list (OR operation)."),
    updated_at_from: str | None = Field(None, alias="updatedAtFrom", description="Filter for journalist profiles updated on or after this date. Accepts ISO 8601 format (e.g., 2023-03-01T00:00:00) or yyyy-mm-dd format."),
    updated_at_to: str | None = Field(None, alias="updatedAtTo", description="Filter for journalist profiles updated on or before this date. Accepts ISO 8601 format (e.g., 2023-03-01T23:59:59) or yyyy-mm-dd format."),
) -> dict[str, Any] | ToolResult:
    """Search and filter journalists from a global database of over 230,000 profiles. Use multiple filter criteria to find journalists by name, coverage topics, publication sources, and other attributes."""

    _size = _parse_int(size)
    _page = _parse_int(page)

    # Construct request model with validation
    try:
        _request = _models.SearchJournalistsRequest(
            query=_models.SearchJournalistsRequestQuery(id_=id_, name=name, twitter=twitter, size=_size, page=_page, source=source, topic=topic, category=category, label=label, country=country, updated_at_from=updated_at_from, updated_at_to=updated_at_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_journalists: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/journalists/all"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_journalists")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_journalists", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_journalists",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: v1
@mcp.tool()
async def get_journalist(id_: str = Field(..., alias="id", description="The unique identifier of the journalist. This ID is provided in article response objects and is used to fetch the journalist's full profile.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific journalist using their unique identifier. Use this to access journalist profiles and biographical details referenced in article responses."""

    # Construct request model with validation
    try:
        _request = _models.GetJournalistByIdRequest(
            path=_models.GetJournalistByIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_journalist: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/journalists/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/journalists/{id}"
    _http_query = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_journalist")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_journalist", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_journalist",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: v1
@mcp.tool()
async def search_people(
    name: str | None = Field(None, description="Search by person's full or partial name using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (* for multiple characters, ? for single character) for flexible name-based lookups."),
    wikidata_id: list[str] | None = Field(None, alias="wikidataId", description="Filter results by one or more Wikidata entity IDs (e.g., Q7747, Q937) to precisely identify specific individuals and eliminate name ambiguity. Multiple IDs are combined with OR logic."),
    occupation_label: str | None = Field(None, alias="occupationLabel", description="Search by occupation or profession (e.g., politician, actor, CEO, athlete) using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (* and ?) for flexible occupation-based filtering."),
    page: str | None = Field(None, description="Specify which page of results to retrieve in the paginated response, starting from page 0. Use with size parameter to navigate through large result sets."),
    size: str | None = Field(None, description="Set the number of people to return per page, between 1 and 100 results. Combine with page parameter to control pagination through results."),
) -> dict[str, Any] | ToolResult:
    """Search and retrieve detailed information on known persons from Perigon's database of over 650,000 people worldwide. Results include Wikidata identifiers for cross-referencing additional biographical data."""

    _page = _parse_int(page)
    _size = _parse_int(size)

    # Construct request model with validation
    try:
        _request = _models.SearchPeopleRequest(
            query=_models.SearchPeopleRequestQuery(name=name, wikidata_id=wikidata_id, occupation_label=occupation_label, page=_page, size=_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_people: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/people/all"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_people")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_people", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_people",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: v1
@mcp.tool()
async def search_media_sources(
    domain: list[str] | None = Field(None, description="Filter by publisher domain or subdomain using wildcard patterns (* for any characters, ? for single character). Supports multiple domains with OR logic (e.g., *.cnn.com, us?.nytimes.com)."),
    name: str | None = Field(None, description="Search source names using Boolean operators (AND, OR, NOT), quoted exact phrases, and wildcards (* and ?) for flexible matching."),
    source_group: str | None = Field(None, alias="sourceGroup", description="Filter by predefined publisher bundles or collections (e.g., top100, top50tech). Returns all sources within the specified group."),
    sort_by: Literal["createdAt", "updatedAt", "relevance", "count", "totalCount"] | None = Field(None, alias="sortBy", description="Sort results by relevance to your query (default), overall traffic rank, monthly visitor count, or publication frequency. Choose the metric most relevant to your use case."),
    page: str | None = Field(None, description="Retrieve a specific page of results (0-indexed). Use with size parameter for pagination through large result sets."),
    size: str | None = Field(None, description="Number of sources per page (1-100). Adjust based on your needs; larger values reduce pagination requests but increase response size."),
    country: list[str] | None = Field(None, description="Filter sources by countries they frequently cover in reporting. Use ISO 3166-1 alpha-2 country codes (lowercase, e.g., us, gb, jp). Multiple values use OR logic."),
    source_country: list[str] | None = Field(None, alias="sourceCountry", description="Filter for local publications based in specific countries. Use ISO 3166-1 alpha-2 country codes (lowercase). Multiple values use OR logic."),
    source_state: list[str] | None = Field(None, alias="sourceState", description="Filter for local publications based in specific states or regions. Use standard two-letter state codes (lowercase, e.g., ca, ny, tx). Multiple values use OR logic."),
    source_county: list[str] | None = Field(None, alias="sourceCounty", description="Filter for local publications based in specific counties. Multiple values use OR logic."),
    source_city: list[str] | None = Field(None, alias="sourceCity", description="Filter for local publications based in specific cities. Multiple values use OR logic."),
    category: list[str] | None = Field(None, description="Filter sources by primary content categories (e.g., Politics, Tech, Sports, Business, Finance). Returns sources that frequently cover these topics. Multiple values use OR logic."),
    topic: list[str] | None = Field(None, description="Filter sources by frequently covered topics (e.g., Markets, Cryptocurrency, Climate Change). Returns sources where the topic ranks in their top 10 coverage areas. Multiple values use OR logic."),
    label: list[str] | None = Field(None, description="Filter sources by content label patterns (e.g., Opinion, Paid-news, Non-news). Returns sources where the label commonly appears in published content. Multiple values use OR logic."),
    paywall: bool | None = Field(None, description="Filter by paywall status: true for sources with paywalls, false for sources without paywalls."),
    show_subdomains: bool | None = Field(None, alias="showSubdomains", description="Control subdomain handling in results. When true (default), subdomains appear as separate sources. When false, results consolidate to parent domains only."),
) -> dict[str, Any] | ToolResult:
    """Search and filter from 200,000+ media sources to find publishers matching your criteria. Results include detailed source information with flexible filtering by domain, geography, content focus, and publication characteristics."""

    _page = _parse_int(page)
    _size = _parse_int(size)

    # Construct request model with validation
    try:
        _request = _models.SearchSourcesRequest(
            query=_models.SearchSourcesRequestQuery(domain=domain, name=name, source_group=source_group, sort_by=sort_by, page=_page, size=_size, country=country, source_country=source_country, source_state=source_state, source_county=source_county, source_city=source_city, category=category, topic=topic, label=label, paywall=paywall, show_subdomains=show_subdomains)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_media_sources: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/sources/all"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_media_sources")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_media_sources", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_media_sources",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: v1
@mcp.tool()
async def search_stories(
    name: str | None = Field(None, description="Search story names using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (*) for pattern variations."),
    cluster_id: list[str] | None = Field(None, alias="clusterId", description="Filter results to specific stories by their unique cluster identifiers. Multiple values return stories matching any of the specified IDs (OR logic)."),
    exclude_cluster_id: list[str] | None = Field(None, alias="excludeClusterId", description="Exclude specific stories from results by their unique cluster identifiers. Multiple values exclude stories matching any of the specified IDs."),
    sort_by: Literal["createdAt", "updatedAt", "relevance", "count", "totalCount"] | None = Field(None, alias="sortBy", description="Sort results by story creation date (default), last update time (best for tracking developing events), relevance to query, unique article count, or total article count including reprints."),
    page: str | None = Field(None, description="Retrieve a specific page of paginated results, starting from page 0. Maximum page value is 10,000."),
    size: str | None = Field(None, description="Number of stories to return per page. Must be between 0 and 100."),
    updated_from: str | None = Field(None, alias="updatedFrom", description="Return only stories that received new articles on or after this date (ISO 8601 format). Useful for tracking recently developing events."),
    updated_to: str | None = Field(None, alias="updatedTo", description="Return only stories that received new articles on or before this date (ISO 8601 format). Useful for tracking recently developing events."),
    topic: list[str] | None = Field(None, description="Filter stories by granular topics (e.g., Markets, Crime, Cryptocurrency, College Sports). Stories can match multiple topics. Multiple values return stories matching any topic (OR logic)."),
    category: list[str] | None = Field(None, description="Filter stories by broad content categories (e.g., Politics, Tech, Sports, Business, Finance). Use 'none' to find uncategorized stories. Multiple values return stories matching any category (OR logic)."),
    taxonomy: list[str] | None = Field(None, description="Filter stories by Google Content Categories using full hierarchical paths (e.g., /Finance/Banking/Other). Multiple values return stories matching any taxonomy path (OR logic)."),
    source: list[str] | None = Field(None, description="Filter stories containing articles from specific publisher domains or subdomains. Supports wildcard patterns (* and ?) for flexible matching. A story matches if it contains at least one article from any specified source. Multiple values use OR logic."),
    source_group: list[str] | None = Field(None, alias="sourceGroup", description="Filter stories containing articles from publishers in Perigon's curated source bundles (e.g., top100, top25crypto). A story matches if it contains at least one article from any publisher in the specified bundles. Multiple values use OR logic."),
    min_unique_sources: str | None = Field(None, alias="minUniqueSources", description="Return only stories covered by at least this many unique sources. Higher values identify more significant stories with broader coverage. Minimum value is 1; defaults to 3."),
    person_wikidata_id: list[str] | None = Field(None, alias="personWikidataId", description="Filter stories by Wikidata IDs of prominently mentioned people. Returns stories where these individuals appear as key entities. Multiple values use OR logic."),
    company_id: list[str] | None = Field(None, alias="companyId", description="Filter stories by company identifiers of prominently mentioned companies. Returns stories where these companies appear as key entities. Multiple values use OR logic."),
    company_domain: list[str] | None = Field(None, alias="companyDomain", description="Filter stories by domains of prominently mentioned companies (e.g., apple.com). Returns stories where companies with these domains appear as key entities. Multiple values use OR logic."),
    company_symbol: list[str] | None = Field(None, alias="companySymbol", description="Filter stories by stock symbols of prominently mentioned companies. Returns stories where companies with these symbols appear as key entities. Multiple values use OR logic."),
    country: list[str] | None = Field(None, description="Filter stories by country code. Multiple values return stories matching any country (OR logic)."),
    state: list[str] | None = Field(None, description="Filter local news by state. When applied, only local news from specified states is returned; non-local news is excluded. Multiple values use OR logic."),
    city: list[str] | None = Field(None, description="Filter local news by city. When applied, only local news from specified cities is returned; non-local news is excluded. Multiple values use OR logic."),
    min_cluster_size: str | None = Field(None, alias="minClusterSize", description="Return only stories with at least this many unique articles. Minimum value is 1."),
    max_cluster_size: str | None = Field(None, alias="maxClusterSize", description="Return only stories with at most this many unique articles."),
    name_exists: bool | None = Field(None, alias="nameExists", description="Return only stories that have been assigned names. Stories receive names after accumulating at least 5 unique articles. Defaults to true."),
    positive_sentiment_from: float | None = Field(None, alias="positiveSentimentFrom", description="Filter stories with aggregate positive sentiment score at or above this threshold. Scores range from 0 to 1, with higher values indicating stronger positive tone."),
    positive_sentiment_to: float | None = Field(None, alias="positiveSentimentTo", description="Filter stories with aggregate positive sentiment score at or below this threshold. Scores range from 0 to 1, with higher values indicating stronger positive tone."),
    neutral_sentiment_from: float | None = Field(None, alias="neutralSentimentFrom", description="Filter stories with aggregate neutral sentiment score at or above this threshold. Scores range from 0 to 1, with higher values indicating stronger neutral tone."),
    neutral_sentiment_to: float | None = Field(None, alias="neutralSentimentTo", description="Filter stories with aggregate neutral sentiment score at or below this threshold. Scores range from 0 to 1, with higher values indicating stronger neutral tone."),
    negative_sentiment_from: float | None = Field(None, alias="negativeSentimentFrom", description="Filter stories with aggregate negative sentiment score at or above this threshold. Scores range from 0 to 1, with higher values indicating stronger negative tone."),
    negative_sentiment_to: float | None = Field(None, alias="negativeSentimentTo", description="Filter stories with aggregate negative sentiment score at or below this threshold. Scores range from 0 to 1, with higher values indicating stronger negative tone."),
) -> dict[str, Any] | ToolResult:
    """Search and filter news story clusters to track evolving narratives, monitor sentiment trends, and identify coverage patterns across global publishers. Returns structured story metadata including summaries, key entities, sentiment scores, and article counts."""

    _page = _parse_int(page)
    _size = _parse_int(size)
    _min_unique_sources = _parse_int(min_unique_sources)
    _min_cluster_size = _parse_int(min_cluster_size)
    _max_cluster_size = _parse_int(max_cluster_size)

    # Construct request model with validation
    try:
        _request = _models.SearchStoriesRequest(
            query=_models.SearchStoriesRequestQuery(name=name, cluster_id=cluster_id, exclude_cluster_id=exclude_cluster_id, sort_by=sort_by, page=_page, size=_size, updated_from=updated_from, updated_to=updated_to, topic=topic, category=category, taxonomy=taxonomy, source=source, source_group=source_group, min_unique_sources=_min_unique_sources, person_wikidata_id=person_wikidata_id, company_id=company_id, company_domain=company_domain, company_symbol=company_symbol, country=country, state=state, city=city, min_cluster_size=_min_cluster_size, max_cluster_size=_max_cluster_size, name_exists=name_exists, positive_sentiment_from=positive_sentiment_from, positive_sentiment_to=positive_sentiment_to, neutral_sentiment_from=neutral_sentiment_from, neutral_sentiment_to=neutral_sentiment_to, negative_sentiment_from=negative_sentiment_from, negative_sentiment_to=negative_sentiment_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_stories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/stories/all"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_stories")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_stories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_stories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: v1
@mcp.tool()
async def list_story_history(
    cluster_id: list[str] | None = Field(None, alias="clusterId", description="Filter results to specific clusters by providing one or more cluster IDs. Only stories within the specified clusters will be returned."),
    sort_by: Literal["createdAt", "triggeredAt"] | None = Field(None, alias="sortBy", description="Sort results by creation date or the date the story was last refreshed/triggered. Defaults to creation date if not specified."),
    page: str | None = Field(None, description="Zero-based page number for pagination, ranging from 0 to 10000. Use this to navigate through large result sets."),
    size: str | None = Field(None, description="Number of story results to return per page, ranging from 0 to 100. Larger values reduce the number of requests needed but increase response size."),
    changelog_exists: bool | None = Field(None, alias="changelogExists", description="Filter to include only clusters that have a changelog (true) or exclude clusters with changelogs (false). Omit to return all clusters regardless of changelog status."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of story history records with optional filtering by cluster, sorting, and changelog status. Use this to track story creation and refresh events across your clusters."""

    _page = _parse_int(page)
    _size = _parse_int(size)

    # Construct request model with validation
    try:
        _request = _models.GetStoryHistoryRequest(
            query=_models.GetStoryHistoryRequestQuery(cluster_id=cluster_id, sort_by=sort_by, page=_page, size=_size, changelog_exists=changelog_exists)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_story_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/stories/history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_story_history")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_story_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_story_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: v1
@mcp.tool()
async def get_story_counts_by_time_interval(
    split_by: Literal["hour", "day", "week", "month", "none"] = Field(..., alias="splitBy", description="Required. Specify the time interval for grouping story count statistics: HOUR (hourly breakdown), DAY (daily breakdown), WEEK (weekly breakdown), MONTH (monthly breakdown), or NONE (no time-based grouping)."),
    name: str | None = Field(None, description="Search for stories by name using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcard patterns (* and ?) for flexible name matching."),
    cluster_id: list[str] | None = Field(None, alias="clusterId", description="Filter results to include only stories with specific cluster IDs. Multiple IDs are combined with OR logic, returning stories matching any of the provided identifiers."),
    exclude_cluster_id: list[str] | None = Field(None, alias="excludeClusterId", description="Exclude stories by their cluster IDs. Multiple IDs are combined with OR logic, filtering out stories matching any of the provided identifiers."),
    sort_by: Literal["createdAt", "updatedAt", "relevance", "count", "totalCount"] | None = Field(None, alias="sortBy", description="Sort results by story creation date (default), last update date (best for tracking developing stories), relevance to query, unique article count, or total article count including reprints."),
    page: str | None = Field(None, description="Specify which page of results to retrieve in the paginated response, starting from page 0. Maximum page number is 10,000."),
    size: str | None = Field(None, description="Set the number of results per page. Must be between 0 and 100 results per page."),
    updated_from: str | None = Field(None, alias="updatedFrom", description="Filter for stories that received new articles on or after this date (ISO 8601 format). Useful for tracking recently developing news events."),
    updated_to: str | None = Field(None, alias="updatedTo", description="Filter for stories that received new articles on or before this date (ISO 8601 format). Useful for tracking recently developing news events."),
    topic: list[str] | None = Field(None, description="Filter stories by specific topics (e.g., Markets, Crime, Cryptocurrency, College Sports). Multiple topics are combined with OR logic. Consult the /topics endpoint for available options."),
    category: list[str] | None = Field(None, description="Filter stories by broad content categories (e.g., Politics, Tech, Sports, Business, Finance). Use 'none' to find uncategorized stories. Multiple categories are combined with OR logic."),
    taxonomy: list[str] | None = Field(None, description="Filter stories by Google Content Categories using full hierarchical paths (e.g., /Finance/Banking/Other). Multiple paths are combined with OR logic."),
    source: list[str] | None = Field(None, description="Filter stories containing articles from specific publisher domains or subdomains. Supports wildcard patterns (* and ?) for flexible matching. A story matches if it contains at least one article from any specified source. Multiple sources are combined with OR logic."),
    source_group: list[str] | None = Field(None, alias="sourceGroup", description="Filter stories containing articles from publishers in Perigon's curated source bundles (e.g., top100, top25crypto). A story matches if it contains at least one article from any publisher in the specified bundles. Multiple bundles are combined with OR logic."),
    min_unique_sources: str | None = Field(None, alias="minUniqueSources", description="Require stories to be covered by a minimum number of unique sources. Higher values return more significant stories with broader coverage. Minimum value is 1; defaults to 3."),
    person_wikidata_id: list[str] | None = Field(None, alias="personWikidataId", description="Filter stories by Wikidata IDs of prominently mentioned people. Multiple IDs are combined with OR logic. Refer to the /people endpoint for available individuals."),
    company_id: list[str] | None = Field(None, alias="companyId", description="Filter stories by company identifiers of prominently mentioned companies. Multiple IDs are combined with OR logic. Refer to the /companies endpoint for available companies."),
    company_domain: list[str] | None = Field(None, alias="companyDomain", description="Filter stories by domains of prominently mentioned companies (e.g., apple.com). Multiple domains are combined with OR logic. Refer to the /companies endpoint for available options."),
    company_symbol: list[str] | None = Field(None, alias="companySymbol", description="Filter stories by stock symbols of prominently mentioned companies. Multiple symbols are combined with OR logic. Refer to the /companies endpoint for available symbols."),
    country: list[str] | None = Field(None, description="Filter stories by country using ISO country codes. Multiple countries are combined with OR logic."),
    state: list[str] | None = Field(None, description="Filter local news by state. When applied, only local news from specified states is returned; non-local news is excluded. Multiple states are combined with OR logic."),
    city: list[str] | None = Field(None, description="Filter local news by city. When applied, only local news from specified cities is returned; non-local news is excluded. Multiple cities are combined with OR logic."),
    min_cluster_size: str | None = Field(None, alias="minClusterSize", description="Filter stories by minimum cluster size based on unique article count. Minimum value is 1."),
    max_cluster_size: str | None = Field(None, alias="maxClusterSize", description="Filter stories by maximum cluster size based on unique article count."),
    name_exists: bool | None = Field(None, alias="nameExists", description="Include only stories that have been assigned names. Stories receive names after accumulating at least 5 unique articles. Defaults to true."),
    positive_sentiment_from: float | None = Field(None, alias="positiveSentimentFrom", description="Filter stories with aggregate positive sentiment score at or above the specified threshold. Scores range from 0 to 1, with higher values indicating stronger positive tone."),
    positive_sentiment_to: float | None = Field(None, alias="positiveSentimentTo", description="Filter stories with aggregate positive sentiment score at or below the specified threshold. Scores range from 0 to 1, with higher values indicating stronger positive tone."),
    neutral_sentiment_from: float | None = Field(None, alias="neutralSentimentFrom", description="Filter stories with aggregate neutral sentiment score at or above the specified threshold. Scores range from 0 to 1, with higher values indicating stronger neutral tone."),
    neutral_sentiment_to: float | None = Field(None, alias="neutralSentimentTo", description="Filter stories with aggregate neutral sentiment score at or below the specified threshold. Scores range from 0 to 1, with higher values indicating stronger neutral tone."),
    negative_sentiment_from: float | None = Field(None, alias="negativeSentimentFrom", description="Filter stories with aggregate negative sentiment score at or above the specified threshold. Scores range from 0 to 1, with higher values indicating stronger negative tone."),
    negative_sentiment_to: float | None = Field(None, alias="negativeSentimentTo", description="Filter stories with aggregate negative sentiment score at or below the specified threshold. Scores range from 0 to 1, with higher values indicating stronger negative tone."),
) -> dict[str, Any] | ToolResult:
    """Retrieve aggregated story count statistics grouped by specified time intervals (hour, day, week, or month). Supports comprehensive filtering by story attributes, entities, sentiment, and geographic location to analyze news trends and story evolution over time."""

    _page = _parse_int(page)
    _size = _parse_int(size)
    _min_unique_sources = _parse_int(min_unique_sources)
    _min_cluster_size = _parse_int(min_cluster_size)
    _max_cluster_size = _parse_int(max_cluster_size)

    # Construct request model with validation
    try:
        _request = _models.GetStoryCountsRequest(
            query=_models.GetStoryCountsRequestQuery(name=name, cluster_id=cluster_id, exclude_cluster_id=exclude_cluster_id, sort_by=sort_by, page=_page, size=_size, updated_from=updated_from, updated_to=updated_to, topic=topic, category=category, taxonomy=taxonomy, source=source, source_group=source_group, min_unique_sources=_min_unique_sources, person_wikidata_id=person_wikidata_id, company_id=company_id, company_domain=company_domain, company_symbol=company_symbol, country=country, state=state, city=city, min_cluster_size=_min_cluster_size, max_cluster_size=_max_cluster_size, name_exists=name_exists, positive_sentiment_from=positive_sentiment_from, positive_sentiment_to=positive_sentiment_to, neutral_sentiment_from=neutral_sentiment_from, neutral_sentiment_to=neutral_sentiment_to, negative_sentiment_from=negative_sentiment_from, negative_sentiment_to=negative_sentiment_to, split_by=split_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_story_counts_by_time_interval: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/stories/stats"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_story_counts_by_time_interval")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_story_counts_by_time_interval", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_story_counts_by_time_interval",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: v1
@mcp.tool()
async def search_and_summarize_articles(
    title: str | None = Field(None, description="Search article titles using Boolean operators (AND, OR, NOT), exact phrases with quotes, and wildcards for pattern matching."),
    desc: str | None = Field(None, description="Search article descriptions using Boolean expressions, exact phrase matching with quotes, and wildcards for flexible pattern matching."),
    content: str | None = Field(None, description="Search full article body content using Boolean logic, exact phrase matching with quotes, and wildcards for comprehensive searching."),
    summary: str | None = Field(None, description="Search article summary fields using Boolean expressions, exact phrase matching with quotes, and wildcards for flexible pattern matching."),
    url: str | None = Field(None, description="Search by URL patterns to filter articles from specific website sections or domains."),
    article_id: list[str] | None = Field(None, alias="articleId", description="Retrieve specific articles by their unique identifiers. Provide one or more article IDs to return a targeted collection."),
    cluster_id: list[str] | None = Field(None, alias="clusterId", description="Filter results to articles within a specific related content cluster. Returns articles grouped by topic relevance as Perigon Stories."),
    sort_by: Literal["relevance", "date", "reverseDate", "reverseAddDate", "addDate", "pubDate", "refreshDate"] | None = Field(None, alias="sortBy", description="Determine article sort order: relevance (default), date/pubDate (newest first), reverseDate (oldest first), addDate (newest ingestion first), reverseAddDate (oldest ingestion first), or refreshDate (most recently updated first)."),
    page: str | None = Field(None, description="Specify which page of results to retrieve, starting from page 0. Supports up to 10,000 pages."),
    size: str | None = Field(None, description="Number of articles to return per page. Range: 0–1,000 articles."),
    add_date_from: str | None = Field(None, alias="addDateFrom", description="Filter for articles added to the system after this date. Accepts ISO 8601 format (e.g., 2022-02-01T00:00:00) or yyyy-mm-dd format."),
    add_date_to: str | None = Field(None, alias="addDateTo", description="Filter for articles added to the system before this date. Accepts ISO 8601 format (e.g., 2022-02-01T23:59:59) or yyyy-mm-dd format."),
    refresh_date_from: str | None = Field(None, alias="refreshDateFrom", description="Filter for articles refreshed or updated in the system after this date. Accepts ISO 8601 format (e.g., 2022-02-01T00:00:00) or yyyy-mm-dd format."),
    refresh_date_to: str | None = Field(None, alias="refreshDateTo", description="Filter for articles refreshed or updated in the system before this date. Accepts ISO 8601 format (e.g., 2022-02-01T23:59:59) or yyyy-mm-dd format."),
    medium: list[str] | None = Field(None, description="Filter by content medium: Article (written content) or Video (video-based stories). Multiple values create an OR filter."),
    source: list[str] | None = Field(None, description="Filter by specific publisher domains or subdomains. Supports wildcards (* and ?) for pattern matching. Multiple values create an OR filter."),
    source_group: list[str] | None = Field(None, alias="sourceGroup", description="Filter using Perigon's curated publisher bundles (e.g., top100, top25crypto). Multiple values create an OR filter."),
    exclude_source_group: list[str] | None = Field(None, alias="excludeSourceGroup", description="Exclude articles from specified Perigon source groups. Multiple values create an AND-exclude filter, removing content from any matching bundle."),
    exclude_source: list[str] | None = Field(None, alias="excludeSource", description="Exclude articles from specific publisher domains or subdomains. Supports wildcards (* and ?) for pattern matching. Multiple values create an AND-exclude filter."),
    watchlist: list[str] | None = Field(None, description="Filter articles using watchlists of people and companies. Multiple values create an OR filter to include articles mentioning any entity from specified watchlists."),
    exclude_watchlist: list[str] | None = Field(None, alias="excludeWatchlist", description="Exclude articles mentioning entities from specified watchlists. Multiple values create an AND-exclude filter, removing content about any matching entity."),
    paywall: bool | None = Field(None, description="Filter by paywall status: true for sources with paywalls, false for sources without paywalls."),
    author: list[str] | None = Field(None, description="Filter articles by specific author names using exact matching. Multiple values create an OR filter to find articles by any specified author."),
    exclude_author: list[str] | None = Field(None, alias="excludeAuthor", description="Exclude articles written by specific authors using exact name matching. Multiple values create an AND-exclude filter."),
    journalist_id: list[str] | None = Field(None, alias="journalistId", description="Filter articles by unique journalist identifiers (available via the Journalist API or matchedAuthors field). Multiple values create an OR filter."),
    exclude_journalist_id: list[str] | None = Field(None, alias="excludeJournalistId", description="Exclude articles written by specific journalists identified by their unique IDs. Multiple values create an AND-exclude filter."),
    language: list[str] | None = Field(None, description="Filter articles by language using ISO 639 two-letter codes (e.g., en, es, fr). Multiple values create an OR filter."),
    exclude_language: list[str] | None = Field(None, alias="excludeLanguage", description="Exclude articles in specific languages using ISO 639 two-letter codes. Multiple values create an AND-exclude filter."),
    search_translation: bool | None = Field(None, alias="searchTranslation", description="When true, expands search to include translated title, description, and content fields for non-English articles."),
    label: list[str] | None = Field(None, description="Filter articles by editorial labels such as Opinion, Paid-news, Non-news, Fact Check, or Press Release. Multiple values create an OR filter."),
    exclude_label: list[str] | None = Field(None, alias="excludeLabel", description="Exclude articles with specific editorial labels. Multiple values create an AND-exclude filter."),
    category: list[str] | None = Field(None, description="Filter by general article categories (e.g., Tech, Politics). Use 'none' to search uncategorized articles. Multiple values create an OR filter."),
    exclude_category: list[str] | None = Field(None, alias="excludeCategory", description="Exclude articles with specific categories. Multiple values create an AND-exclude filter."),
    topic: list[str] | None = Field(None, description="Filter by specific topics (e.g., Markets, Crime, Cryptocurrency, College Sports). Topics are more granular than categories. Multiple values create an OR filter. Consult the /topics endpoint for available topics."),
    exclude_topic: list[str] | None = Field(None, alias="excludeTopic", description="Exclude articles with specific topics. Multiple values create an AND-exclude filter."),
    link_to: str | None = Field(None, alias="linkTo", description="Return only articles containing links to the specified URL pattern."),
    show_reprints: bool | None = Field(None, alias="showReprints", description="When true (default), includes reprinted content from wire services like AP or Reuters that appear on multiple sites."),
    reprint_group_id: str | None = Field(None, alias="reprintGroupId", description="Return all articles in a specific reprint group, including the original article and all known reprints."),
    city: list[str] | None = Field(None, description="Filter articles where a specified city plays a central role in the content. Multiple values create an OR filter."),
    exclude_city: list[str] | None = Field(None, alias="excludeCity", description="Exclude articles associated with specified cities. Multiple values create an AND-exclude filter."),
    state: list[str] | None = Field(None, description="Filter articles where a specified state plays a central role in the content. Multiple values create an OR filter."),
    exclude_state: list[str] | None = Field(None, alias="excludeState", description="Exclude articles associated with specified states. Multiple values create an AND-exclude filter."),
    county: list[str] | None = Field(None, description="Filter articles by county. Only articles tagged with one of these counties will be included. Multiple values create an OR filter."),
    exclude_county: list[str] | None = Field(None, alias="excludeCounty", description="Exclude articles from specific counties or administrative divisions. County names should match the format used in article metadata (e.g., 'Los Angeles County', 'Cook County'). Multiple values create an AND-exclude filter."),
    country: list[str] | None = Field(None, description="Filter articles by country code. Multiple values create an OR filter."),
    location: list[str] | None = Field(None, description="Return articles with specified location attributes. Format: 'city:New York::state:NY' with ':' between key and value, '::' between attributes."),
    lat: float | None = Field(None, description="Latitude of the center point for geographic search. Range: -90 to 90 degrees.", ge=-90, le=90),
    lon: float | None = Field(None, description="Longitude of the center point for geographic search. Range: -180 to 180 degrees.", ge=-180, le=180),
    max_distance: float | None = Field(None, alias="maxDistance", description="Maximum distance in kilometers from the center point for geographic search. Range: 1–300 km.", ge=1, le=300),
    source_city: list[str] | None = Field(None, alias="sourceCity", description="Filter articles published by sources located within specified cities. Multiple values create an OR filter."),
    exclude_source_city: list[str] | None = Field(None, alias="excludeSourceCity", description="Exclude articles published by sources located within specified cities. Multiple values create an AND-exclude filter."),
    source_county: list[str] | None = Field(None, alias="sourceCounty", description="Filter articles published by sources located within specified counties. Multiple values create an OR filter."),
    exclude_source_county: list[str] | None = Field(None, alias="excludeSourceCounty", description="Exclude articles published by sources located within specified counties. Multiple values create an AND-exclude filter."),
    source_country: list[str] | None = Field(None, alias="sourceCountry", description="Filter articles published by sources located within specified countries. Use 2-character country codes (e.g., us, gb). Multiple values create an OR filter."),
    exclude_source_country: list[str] | None = Field(None, alias="excludeSourceCountry", description="Exclude articles published by sources located within specified countries. Use 2-character country codes (e.g., us, gb). Multiple values create an AND-exclude filter."),
    source_state: list[str] | None = Field(None, alias="sourceState", description="Filter articles published by sources located within specified states. Multiple values create an OR filter."),
    exclude_source_state: list[str] | None = Field(None, alias="excludeSourceState", description="Exclude articles published by sources located within specified states. Multiple values create an AND-exclude filter."),
    person_wikidata_id: list[str] | None = Field(None, alias="personWikidataId", description="Filter articles by Wikidata IDs of mentioned people. Refer to the /people endpoint for tracked individuals. Multiple values create an OR filter."),
    exclude_person_wikidata_id: list[str] | None = Field(None, alias="excludePersonWikidataId", description="Exclude articles mentioning people with specific Wikidata IDs. Multiple values create an AND-exclude filter."),
    exclude_person_name: list[str] | None = Field(None, alias="excludePersonName", description="Exclude articles mentioning specific people by name. Multiple values create an AND-exclude filter."),
    company_id: list[str] | None = Field(None, alias="companyId", description="Filter articles by company identifiers. Refer to the /companies endpoint for tracked companies. Multiple values create an OR filter."),
    exclude_company_id: list[str] | None = Field(None, alias="excludeCompanyId", description="Exclude articles mentioning companies with specific identifiers. Multiple values create an AND-exclude filter."),
    company_domain: list[str] | None = Field(None, alias="companyDomain", description="Filter articles by company domains (e.g., apple.com). Consult the /companies endpoint for available entities. Multiple values create an OR filter."),
    exclude_company_domain: list[str] | None = Field(None, alias="excludeCompanyDomain", description="Exclude articles related to companies with specific domains. Multiple values create an AND-exclude filter."),
    company_symbol: list[str] | None = Field(None, alias="companySymbol", description="Filter articles by company stock symbols (ticker symbols). Consult the /companies endpoint for available symbols. Multiple values create an OR filter."),
    exclude_company_symbol: list[str] | None = Field(None, alias="excludeCompanySymbol", description="Exclude articles related to companies with specific stock symbols. Multiple values create an AND-exclude filter."),
    positive_sentiment_from: float | None = Field(None, alias="positiveSentimentFrom", description="Filter articles with positive sentiment score greater than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger positive tone."),
    positive_sentiment_to: float | None = Field(None, alias="positiveSentimentTo", description="Filter articles with positive sentiment score less than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger positive tone."),
    neutral_sentiment_from: float | None = Field(None, alias="neutralSentimentFrom", description="Filter articles with neutral sentiment score greater than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger neutral tone."),
    neutral_sentiment_to: float | None = Field(None, alias="neutralSentimentTo", description="Filter articles with neutral sentiment score less than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger neutral tone."),
    negative_sentiment_from: float | None = Field(None, alias="negativeSentimentFrom", description="Filter articles with negative sentiment score greater than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger negative tone."),
    negative_sentiment_to: float | None = Field(None, alias="negativeSentimentTo", description="Filter articles with negative sentiment score less than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger negative tone."),
    taxonomy: list[str] | None = Field(None, description="Filter by Google Content Categories using full category names (e.g., /Finance/Banking/Other, /Finance/Investing/Funds). Refer to the Google Content Categories documentation for the complete list. Multiple values create an OR filter."),
    prefix_taxonomy: str | None = Field(None, alias="prefixTaxonomy", description="Filter by Google Content Categories using category prefix only (e.g., /Finance). Matches all categories starting with the specified prefix."),
    prompt: str | None = Field(None, description="Custom instructions guiding how the summary should be written. Maximum 2,048 characters. Defaults to a casual, natural tone synthesis in one paragraph (no more than 125 words)."),
    max_article_count: str | None = Field(None, alias="maxArticleCount", description="Maximum number of articles to factor into the summary. Range: 1–100 articles. Default: 10."),
    returned_article_count: str | None = Field(None, alias="returnedArticleCount", description="Maximum number of articles to return in the response. Can be less than maxArticleCount. Range: 1–100 articles. Default: 10."),
    summarize_fields: list[Literal["TITLE", "CONTENT", "SUMMARY"]] | None = Field(None, alias="summarizeFields", description="Which article fields to include when generating the summary. Choose up to three values from: TITLE, CONTENT, SUMMARY. Default: all three."),
    method: Literal["ARTICLES", "CLUSTERS"] | None = Field(None, description="Method for selecting articles: ARTICLES (include all matches) or CLUSTERS (one article per cluster). Default: ARTICLES."),
    model: Literal["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "llama-3.3-70b-versatile", "openai/gpt-oss-120b"] | None = Field(None, description="Underlying LLM model for generation. Options: gpt-4o, gpt-4o-mini, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, llama-3.3-70b-versatile, openai/gpt-oss-120b. Default: gpt-4.1."),
    temperature: float | None = Field(None, description="Sampling temperature for the LLM controlling randomness. Range: 0.0 (deterministic) to 2.0 (very creative). Default: 0.7.", ge=0, le=2),
    top_p: float | None = Field(None, alias="topP", description="Nucleus sampling (top-p) parameter for the LLM controlling diversity. Range: 0.0 to 1.0. Default: 1.0.", ge=0, le=1),
    max_tokens: str | None = Field(None, alias="maxTokens", description="Maximum number of tokens to generate in the summary. Default: 2,048 tokens."),
) -> dict[str, Any] | ToolResult:
    """Generate a single, concise summary synthesizing insights from articles matching your search filters and criteria. Use custom prompts to guide which themes and findings to highlight in the summary."""

    _page = _parse_int(page)
    _size = _parse_int(size)
    _max_article_count = _parse_int(max_article_count)
    _returned_article_count = _parse_int(returned_article_count)
    _max_tokens = _parse_int(max_tokens)

    # Construct request model with validation
    try:
        _request = _models.SearchSummarizerRequest(
            query=_models.SearchSummarizerRequestQuery(title=title, desc=desc, content=content, summary=summary, url=url, article_id=article_id, cluster_id=cluster_id, sort_by=sort_by, page=_page, size=_size, add_date_from=add_date_from, add_date_to=add_date_to, refresh_date_from=refresh_date_from, refresh_date_to=refresh_date_to, medium=medium, source=source, source_group=source_group, exclude_source_group=exclude_source_group, exclude_source=exclude_source, watchlist=watchlist, exclude_watchlist=exclude_watchlist, paywall=paywall, author=author, exclude_author=exclude_author, journalist_id=journalist_id, exclude_journalist_id=exclude_journalist_id, language=language, exclude_language=exclude_language, search_translation=search_translation, label=label, exclude_label=exclude_label, category=category, exclude_category=exclude_category, topic=topic, exclude_topic=exclude_topic, link_to=link_to, show_reprints=show_reprints, reprint_group_id=reprint_group_id, city=city, exclude_city=exclude_city, state=state, exclude_state=exclude_state, county=county, exclude_county=exclude_county, country=country, location=location, lat=lat, lon=lon, max_distance=max_distance, source_city=source_city, exclude_source_city=exclude_source_city, source_county=source_county, exclude_source_county=exclude_source_county, source_country=source_country, exclude_source_country=exclude_source_country, source_state=source_state, exclude_source_state=exclude_source_state, person_wikidata_id=person_wikidata_id, exclude_person_wikidata_id=exclude_person_wikidata_id, exclude_person_name=exclude_person_name, company_id=company_id, exclude_company_id=exclude_company_id, company_domain=company_domain, exclude_company_domain=exclude_company_domain, company_symbol=company_symbol, exclude_company_symbol=exclude_company_symbol, positive_sentiment_from=positive_sentiment_from, positive_sentiment_to=positive_sentiment_to, neutral_sentiment_from=neutral_sentiment_from, neutral_sentiment_to=neutral_sentiment_to, negative_sentiment_from=negative_sentiment_from, negative_sentiment_to=negative_sentiment_to, taxonomy=taxonomy, prefix_taxonomy=prefix_taxonomy),
            body=_models.SearchSummarizerRequestBody(prompt=prompt, max_article_count=_max_article_count, returned_article_count=_returned_article_count, summarize_fields=summarize_fields, method=method, model=model, temperature=temperature, top_p=top_p, max_tokens=_max_tokens)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_and_summarize_articles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/summarize"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_and_summarize_articles")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_and_summarize_articles", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_and_summarize_articles",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
    )

    return _response_data

# Tags: v1
@mcp.tool()
async def search_topics(
    name: str | None = Field(None, description="Filter topics by exact name match or partial text search. Supports partial matching but does not accept wildcard patterns."),
    category: str | None = Field(None, description="Filter results to a specific broad category such as Politics, Tech, Sports, Business, Finance, or Entertainment."),
    subcategory: str | None = Field(None, description="Narrow results to a specific subcategory within the selected category for more granular topic classification."),
    page: str | None = Field(None, description="Specify which page of results to retrieve in the paginated response. Page numbering starts at 0."),
    size: str | None = Field(None, description="Set the maximum number of topics to return per page. Must be a non-negative integer."),
) -> dict[str, Any] | ToolResult:
    """Search and browse all available topics in the Perigon database, with filtering by name, category, and subcategory. Results are paginated for efficient data retrieval."""

    _page = _parse_int(page)
    _size = _parse_int(size)

    # Construct request model with validation
    try:
        _request = _models.SearchTopicsRequest(
            query=_models.SearchTopicsRequestQuery(name=name, category=category, subcategory=subcategory, page=_page, size=_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_topics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/topics/all"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_topics")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_topics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_topics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
    )

    return _response_data

# Tags: v1
@mcp.tool()
async def search_news_articles(
    prompt: str = Field(..., description="Natural language query describing what you want to find in news articles. Accepts up to 1024 characters.", min_length=0, max_length=1024),
    filter_: _models.VectorSearchArticlesBodyFilter | None = Field(None, alias="filter", description="Filter criteria to narrow search results (specific filter structure not documented)."),
    pub_date_from: str | None = Field(None, alias="pubDateFrom", description="Earliest publication date to include in results. Accepts ISO 8601 format (e.g., 2024-01-01T00:00:00Z) or simple date format (yyyy-mm-dd). Defaults to articles from the last 30 days if not specified."),
    pub_date_to: str | None = Field(None, alias="pubDateTo", description="Latest publication date to include in results. Accepts ISO 8601 format (e.g., 2024-12-31T23:59:59Z) or simple date format (yyyy-mm-dd)."),
    show_reprints: bool | None = Field(None, alias="showReprints", description="Include or exclude reprinted articles (wire service content from sources like AP or Reuters that appear across multiple outlets). Defaults to including reprints."),
    size: str | None = Field(None, description="Number of results to return per page. Must be between 1 and 100 articles. Defaults to 10."),
    page: str | None = Field(None, description="Page number to retrieve for paginated results. Must be between 0 and 10000. Defaults to the first page (0)."),
) -> dict[str, Any] | ToolResult:
    """Search news articles from the past 6 months using natural language queries with semantic relevance matching. Returns a ranked list of articles most closely aligned with your search intent, with optional filtering by publication date and content type."""

    _size = _parse_int(size)
    _page = _parse_int(page)

    # Construct request model with validation
    try:
        _request = _models.VectorSearchArticlesRequest(
            body=_models.VectorSearchArticlesRequestBody(prompt=prompt, filter_=filter_, pub_date_from=pub_date_from, pub_date_to=pub_date_to, show_reprints=show_reprints, size=_size, page=_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_news_articles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/vector/news/all"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_news_articles")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_news_articles", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_news_articles",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
    )

    return _response_data

# Tags: v1
@mcp.tool()
async def search_wikipedia(
    prompt: str = Field(..., description="Natural language query describing what you want to find. Supports up to 1024 characters.", min_length=0, max_length=1024),
    filter_: _models.VectorSearchWikipediaBodyFilter | None = Field(None, alias="filter", description="Optional filter to narrow search results by specific criteria."),
    size: str | None = Field(None, description="Number of results to return per page, between 1 and 100 items. Defaults to 10."),
    page: str | None = Field(None, description="Page number for pagination, starting from 0 up to 10000. Defaults to 0 for the first page."),
) -> dict[str, Any] | ToolResult:
    """Search Wikipedia using natural language queries to find page sections ranked by semantic relevance to your search intent."""

    _size = _parse_int(size)
    _page = _parse_int(page)

    # Construct request model with validation
    try:
        _request = _models.VectorSearchWikipediaRequest(
            body=_models.VectorSearchWikipediaRequestBody(prompt=prompt, filter_=filter_, size=_size, page=_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_wikipedia: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/vector/wikipedia/all"
    _http_query = {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_wikipedia")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_wikipedia", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_wikipedia",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
    )

    return _response_data

# Tags: v1
@mcp.tool()
async def search_wikipedia_pages(
    title: str | None = Field(None, description="Search within page titles using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (*) for pattern matching."),
    summary: str | None = Field(None, description="Search within page summaries using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (*) for pattern matching."),
    text: str | None = Field(None, description="Search across all page content and sections using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (*) for pattern matching."),
    reference: str | None = Field(None, description="Search across page references and citations using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (*) for pattern matching."),
    id_: list[str] | None = Field(None, alias="id", description="Retrieve specific pages by their unique Perigon identifiers. Provide one or more IDs as an array to return a targeted collection of pages."),
    wiki_namespace: list[int] | None = Field(None, alias="wikiNamespace", description="Filter pages by wiki namespace. Currently only the main namespace (0) is supported."),
    wikidata_id: list[str] | None = Field(None, alias="wikidataId", description="Retrieve pages by their corresponding Wikidata entity identifiers. Provide one or more Wikidata IDs as an array."),
    wikidata_instance_of_id: list[str] | None = Field(None, alias="wikidataInstanceOfId", description="Retrieve pages whose Wikidata entities are instances of the specified Wikidata IDs. Provide one or more IDs as an array."),
    wikidata_instance_of_label: list[str] | None = Field(None, alias="wikidataInstanceOfLabel", description="Retrieve pages whose Wikidata entities are instances of the specified labels. Provide one or more Wikidata entity labels as an array."),
    category: list[str] | None = Field(None, description="Filter pages by Wikipedia categories. Provide one or more category names as an array."),
    section_id: list[str] | None = Field(None, alias="sectionId", description="Retrieve pages containing specific section identifiers. Each section ID is unique within the Wikipedia dataset; provide one or more as an array."),
    with_pageviews: bool | None = Field(None, alias="withPageviews", description="When enabled, return only pages that have viewership statistics available. Defaults to false, which returns all matching pages regardless of viewership data."),
    page: str | None = Field(None, description="Specify which page of results to retrieve in the paginated response, starting from 0. Maximum page number is 10000."),
    size: str | None = Field(None, description="Set the number of articles to return per page in the paginated response. Maximum is 1000 results per page."),
    sort_by: Literal["relevance", "revisionTsDesc", "revisionTsAsc", "pageViewsDesc", "pageViewsAsc", "scrapedAtDesc", "scrapedAtAsc"] | None = Field(None, alias="sortBy", description="Sort results by relevance (default), revision timestamp (ascending or descending for recently edited), page views (ascending or descending for viewership), or scrape timestamp (ascending or descending for recently updated)."),
) -> dict[str, Any] | ToolResult:
    """Search and retrieve Wikipedia pages from the Perigon API using flexible filtering criteria across titles, summaries, content, and references. Results are returned as paginated collections that can be sorted by relevance, recency, or viewership."""

    _page = _parse_int(page)
    _size = _parse_int(size)

    # Construct request model with validation
    try:
        _request = _models.SearchWikipediaRequest(
            query=_models.SearchWikipediaRequestQuery(title=title, summary=summary, text=text, reference=reference, id_=id_, wiki_namespace=wiki_namespace, wikidata_id=wikidata_id, wikidata_instance_of_id=wikidata_instance_of_id, wikidata_instance_of_label=wikidata_instance_of_label, category=category, section_id=section_id, with_pageviews=with_pageviews, page=_page, size=_size, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_wikipedia_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/wikipedia/all"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_wikipedia_pages")
    _http_query.update(_auth.get("params", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_wikipedia_pages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_wikipedia_pages",
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
        print("  python perigon_api_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Perigon API MCP Server")

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
    logger.info("Starting Perigon API MCP Server")
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

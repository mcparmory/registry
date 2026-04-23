#!/usr/bin/env python3
"""
CircleCI MCP Server

API Info:
- API License: MIT (https://opensource.org/license/MIT)

Generated: 2026-04-23 21:07:50 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://circleci.com/api/v2")
SERVER_NAME = "CircleCI"
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
                            if isinstance(_value, str):
                                _file_content = _value.encode("utf-8")
                            elif isinstance(_value, (bytes, bytearray)):
                                _file_content = bytes(_value)
                            else:
                                raise ValueError(
                                    f"Unsupported multipart file field '{_key}': "
                                    f"expected str or bytes, got {type(_value).__name__}"
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
    'api_key_header',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["api_key_header"] = _auth.APIKeyAuth(env_var="API_KEY", location="header", param_name="Circle-Token")
    logging.info("Authentication configured: api_key_header")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for api_key_header not configured: {error_msg}")
    _auth_handlers["api_key_header"] = None

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

mcp = FastMCP("CircleCI", middleware=[_JsonCoercionMiddleware()])

# Tags: Insights
@mcp.tool()
async def get_project_workflow_summary(
    project_slug: str = Field(..., alias="project-slug", description="The project slug identifying the target project, formed as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID as org-name, and the project ID as repo-name. Forward slashes may be URL-escaped."),
    reporting_window: Literal["last-7-days", "last-90-days", "last-24-hours", "last-30-days", "last-60-days"] | None = Field(None, alias="reporting-window", description="The time window over which summary metrics are calculated. Trends are only supported for windows up to 30 days; defaults to last-90-days if omitted."),
    branches: dict[str, Any] | None = Field(None, description="One or more VCS branch names to filter branch-level workflow metrics. Multiple branches can be specified by repeating the query parameter."),
    workflow_names: dict[str, Any] | None = Field(None, alias="workflow-names", description="One or more workflow names to filter workflow-level metrics. Multiple workflow names can be specified by repeating the query parameter."),
) -> dict[str, Any] | ToolResult:
    """Retrieves aggregated summary metrics and trends for a project across its workflows and branches, covering up to 90 days of workflow run history. Note: Insights data is not suitable for precise credit reporting; use the CircleCI Plan Overview page for billing accuracy."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectWorkflowsPageDataRequest(
            path=_models.GetProjectWorkflowsPageDataRequestPath(project_slug=project_slug),
            query=_models.GetProjectWorkflowsPageDataRequestQuery(reporting_window=reporting_window, branches=branches, workflow_names=workflow_names)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_workflow_summary: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/insights/pages/{project-slug}/summary", _request.path.model_dump(by_alias=True)) if _request.path else "/insights/pages/{project-slug}/summary"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_workflow_summary")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_workflow_summary", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_workflow_summary",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights
@mcp.tool()
async def list_job_timeseries(
    project_slug: str = Field(..., alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`, where slashes may be URL-escaped. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID as org-name, and the project ID as repo-name."),
    workflow_name: str = Field(..., alias="workflow-name", description="The exact name of the workflow for which to retrieve job timeseries data."),
    branch: str | None = Field(None, description="The name of the VCS branch to scope results to. Defaults to the repository's default branch if omitted."),
    granularity: Literal["daily", "hourly"] | None = Field(None, description="The time resolution for the returned timeseries data, either per hour or per day. Hourly data is only available for the past 48 hours; daily data is available for up to 90 days."),
    start_date: str | None = Field(None, alias="start-date", description="The inclusive start of the time range filter, in ISO 8601 date-time format. Must be provided if an end-date is specified."),
    end_date: str | None = Field(None, alias="end-date", description="The exclusive end of the time range filter, in ISO 8601 date-time format. Must be no more than 90 days after the start-date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve timeseries performance data for all jobs within a specified workflow, supporting hourly or daily granularity. Hourly data is retained for 48 hours and daily data for 90 days."""

    # Construct request model with validation
    try:
        _request = _models.GetJobTimeseriesRequest(
            path=_models.GetJobTimeseriesRequestPath(project_slug=project_slug, workflow_name=workflow_name),
            query=_models.GetJobTimeseriesRequestQuery(branch=branch, granularity=granularity, start_date=start_date, end_date=end_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_job_timeseries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/insights/time-series/{project-slug}/workflows/{workflow-name}/jobs", _request.path.model_dump(by_alias=True)) if _request.path else "/insights/time-series/{project-slug}/workflows/{workflow-name}/jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_job_timeseries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_job_timeseries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_job_timeseries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights
@mcp.tool()
async def get_org_summary(
    org_slug: str = Field(..., alias="org-slug", description="The organization slug identifying the target org, combining the VCS provider slug and organization name separated by a forward slash (which may be URL-encoded)."),
    reporting_window: Literal["last-7-days", "last-90-days", "last-24-hours", "last-30-days", "last-60-days"] | None = Field(None, alias="reporting-window", description="The time window over which summary metrics are calculated and trends are derived. Defaults to the last 90 days if not specified."),
    project_names: dict[str, Any] | None = Field(None, alias="project-names", description="An optional list of project names used to filter results to specific projects within the org. Provide the parameter multiple times to include multiple projects."),
) -> dict[str, Any] | ToolResult:
    """Retrieves aggregated performance metrics and trends for an entire organization and each of its projects. Supports filtering by a specific reporting window and an optional subset of projects."""

    # Construct request model with validation
    try:
        _request = _models.GetOrgSummaryDataRequest(
            path=_models.GetOrgSummaryDataRequestPath(org_slug=org_slug),
            query=_models.GetOrgSummaryDataRequestQuery(reporting_window=reporting_window, project_names=project_names)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_org_summary: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/insights/{org-slug}/summary", _request.path.model_dump(by_alias=True)) if _request.path else "/insights/{org-slug}/summary"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_org_summary")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_org_summary", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_org_summary",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights
@mcp.tool()
async def list_project_branches(
    project_slug: str = Field(..., alias="project-slug", description="Unique identifier for the project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID as org-name, and the project ID as repo-name. Forward slashes may be URL-escaped."),
    workflow_name: str | None = Field(None, alias="workflow-name", description="Filters the returned branches to only those associated with the specified workflow name. When omitted, branches are scoped to the entire project across all workflows."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all branches currently tracked within Insights for a specified project. Returns up to 5,000 branches, optionally scoped to a specific workflow."""

    # Construct request model with validation
    try:
        _request = _models.GetAllInsightsBranchesRequest(
            path=_models.GetAllInsightsBranchesRequestPath(project_slug=project_slug),
            query=_models.GetAllInsightsBranchesRequestQuery(workflow_name=workflow_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_branches: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/insights/{project-slug}/branches", _request.path.model_dump(by_alias=True)) if _request.path else "/insights/{project-slug}/branches"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_branches")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_branches", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_branches",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights
@mcp.tool()
async def list_flaky_tests(project_slug: str = Field(..., alias="project-slug", description="Unique identifier for the project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-escaped.")) -> dict[str, Any] | ToolResult:
    """Retrieves all flaky tests for a given project, where a flaky test is defined as one that both passed and failed within the same commit. Results are branch-agnostic."""

    # Construct request model with validation
    try:
        _request = _models.GetFlakyTestsRequest(
            path=_models.GetFlakyTestsRequestPath(project_slug=project_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_flaky_tests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/insights/{project-slug}/flaky-tests", _request.path.model_dump(by_alias=True)) if _request.path else "/insights/{project-slug}/flaky-tests"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_flaky_tests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_flaky_tests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_flaky_tests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights
@mcp.tool()
async def list_workflow_metrics(
    project_slug: str = Field(..., alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the Organization ID (from Organization Settings) as org-name, and the Project ID (from Project Settings) as repo-name. Forward slashes may be URL-encoded."),
    branch: str | None = Field(None, description="Filters metrics to a specific VCS branch by name. If omitted, metrics are scoped to the project's default branch."),
    reporting_window: Literal["last-7-days", "last-90-days", "last-24-hours", "last-30-days", "last-60-days"] | None = Field(None, alias="reporting-window", description="Defines the time window over which summary metrics are calculated. Accepts predefined window values; if omitted, defaults to the last 90 days."),
) -> dict[str, Any] | ToolResult:
    """Retrieves aggregated summary metrics for all workflows in a project, covering up to the last 90 days. Metrics are refreshed daily and are intended for performance insights, not precise credit or billing reporting."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectWorkflowMetricsRequest(
            path=_models.GetProjectWorkflowMetricsRequestPath(project_slug=project_slug),
            query=_models.GetProjectWorkflowMetricsRequestQuery(branch=branch, reporting_window=reporting_window)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflow_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/insights/{project-slug}/workflows", _request.path.model_dump(by_alias=True)) if _request.path else "/insights/{project-slug}/workflows"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflow_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflow_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflow_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights
@mcp.tool()
async def list_workflow_runs(
    project_slug: str = Field(..., alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`, where slashes may be URL-escaped. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the Organization ID as org-name, and the Project ID as repo-name."),
    workflow_name: str = Field(..., alias="workflow-name", description="The exact name of the workflow whose runs you want to retrieve, as defined in the project's pipeline configuration."),
    all_branches: bool | None = Field(None, alias="all-branches", description="When set to true, aggregates data across all branches. Use either this parameter or the branch parameter, but not both simultaneously."),
    branch: str | None = Field(None, description="Filters results to a specific VCS branch by name. Defaults to the repository's default branch if omitted; cannot be used together with all-branches."),
    start_date: str | None = Field(None, alias="start-date", description="Filters results to only include workflow runs that started at or after this ISO 8601 datetime. Required when an end-date is specified."),
    end_date: str | None = Field(None, alias="end-date", description="Filters results to only include workflow runs that started before this ISO 8601 datetime. Must be no more than 90 days after the start-date."),
) -> dict[str, Any] | ToolResult:
    """Retrieves recent runs of a specific workflow within a project, covering executions up to 90 days in the past. Note that Insights data is not suitable for precise credit reporting; use the CircleCI UI Plan Overview page for accurate billing information."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectWorkflowRunsRequest(
            path=_models.GetProjectWorkflowRunsRequestPath(project_slug=project_slug, workflow_name=workflow_name),
            query=_models.GetProjectWorkflowRunsRequestQuery(all_branches=all_branches, branch=branch, start_date=start_date, end_date=end_date)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflow_runs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/insights/{project-slug}/workflows/{workflow-name}", _request.path.model_dump(by_alias=True)) if _request.path else "/insights/{project-slug}/workflows/{workflow-name}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflow_runs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflow_runs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflow_runs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights
@mcp.tool()
async def list_workflow_job_metrics(
    project_slug: str = Field(..., alias="project-slug", description="Unique identifier for the project in the form `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-encoded."),
    workflow_name: str = Field(..., alias="workflow-name", description="The exact name of the workflow whose job metrics you want to retrieve."),
    all_branches: bool | None = Field(None, alias="all-branches", description="When set to true, aggregates metrics across all branches. Use either this parameter or the branch parameter, not both."),
    branch: str | None = Field(None, description="Filters metrics to a specific VCS branch by name. Defaults to the repository's default branch if neither this nor all-branches is provided."),
    reporting_window: Literal["last-7-days", "last-90-days", "last-24-hours", "last-30-days", "last-60-days"] | None = Field(None, alias="reporting-window", description="Defines the time window over which summary metrics are calculated. Defaults to the last 90 days if not specified."),
    job_name: str | None = Field(None, alias="job-name", description="Filters results to jobs whose names match the provided string, either as a full job name or a substring. Returns metrics for all jobs in the workflow if omitted."),
) -> dict[str, Any] | ToolResult:
    """Retrieves aggregated summary metrics for all jobs within a specific project workflow, covering up to the last 90 days. Metrics are refreshed daily and are intended for performance analysis, not precise credit or billing reporting."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectWorkflowJobMetricsRequest(
            path=_models.GetProjectWorkflowJobMetricsRequestPath(project_slug=project_slug, workflow_name=workflow_name),
            query=_models.GetProjectWorkflowJobMetricsRequestQuery(all_branches=all_branches, branch=branch, reporting_window=reporting_window, job_name=job_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflow_job_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/insights/{project-slug}/workflows/{workflow-name}/jobs", _request.path.model_dump(by_alias=True)) if _request.path else "/insights/{project-slug}/workflows/{workflow-name}/jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflow_job_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflow_job_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflow_job_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights
@mcp.tool()
async def get_workflow_summary(
    project_slug: str = Field(..., alias="project-slug", description="Unique identifier for the project, formatted as vcs-slug/org-name/repo-name. For GitLab or GitHub App projects, use 'circleci' as the vcs-slug, the organization ID as org-name, and the project ID as repo-name."),
    workflow_name: str = Field(..., alias="workflow-name", description="The exact name of the workflow for which to retrieve summary metrics."),
    all_branches: bool | None = Field(None, alias="all-branches", description="When set to true, aggregates metrics across all branches instead of a single branch. Use either this parameter or the branch parameter, not both."),
    branch: str | None = Field(None, description="The name of the VCS branch to scope metrics to. If omitted and all-branches is not set, results default to the repository's default branch."),
) -> dict[str, Any] | ToolResult:
    """Retrieves aggregated metrics and trends for a specific workflow within a project, such as duration, success rate, and run frequency. Results can be scoped to a single branch or aggregated across all branches."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkflowSummaryRequest(
            path=_models.GetWorkflowSummaryRequestPath(project_slug=project_slug, workflow_name=workflow_name),
            query=_models.GetWorkflowSummaryRequestQuery(all_branches=all_branches, branch=branch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workflow_summary: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/insights/{project-slug}/workflows/{workflow-name}/summary", _request.path.model_dump(by_alias=True)) if _request.path else "/insights/{project-slug}/workflows/{workflow-name}/summary"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workflow_summary")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workflow_summary", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workflow_summary",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Insights
@mcp.tool()
async def get_workflow_test_metrics(
    project_slug: str = Field(..., alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-escaped."),
    workflow_name: str = Field(..., alias="workflow-name", description="The exact name of the workflow for which test metrics should be retrieved."),
    branch: str | None = Field(None, description="Scopes results to a specific VCS branch name. Defaults to the repository's default branch if omitted. Mutually exclusive with the all-branches parameter."),
    all_branches: bool | None = Field(None, alias="all-branches", description="When set to true, aggregates test metrics across all branches rather than a single branch. Mutually exclusive with the branch parameter; use one or the other, not both."),
) -> dict[str, Any] | ToolResult:
    """Retrieves test metrics for a specific workflow within a project, calculated from the 10 most recent workflow runs. Results can be scoped to a specific branch or aggregated across all branches."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectWorkflowTestMetricsRequest(
            path=_models.GetProjectWorkflowTestMetricsRequestPath(project_slug=project_slug, workflow_name=workflow_name),
            query=_models.GetProjectWorkflowTestMetricsRequestQuery(branch=branch, all_branches=all_branches)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workflow_test_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/insights/{project-slug}/workflows/{workflow-name}/test-metrics", _request.path.model_dump(by_alias=True)) if _request.path else "/insights/{project-slug}/workflows/{workflow-name}/test-metrics"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workflow_test_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workflow_test_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workflow_test_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Job
@mcp.tool()
async def cancel_job(job_id: str = Field(..., alias="job-id", description="The unique identifier of the job to cancel, in UUID format.")) -> dict[str, Any] | ToolResult:
    """Cancels an active job identified by its unique job ID. Use this to stop a job that is pending or in progress before it completes."""

    # Construct request model with validation
    try:
        _request = _models.CancelJobByJobIdRequest(
            path=_models.CancelJobByJobIdRequestPath(job_id=job_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for cancel_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/jobs/{job-id}/cancel", _request.path.model_dump(by_alias=True)) if _request.path else "/jobs/{job-id}/cancel"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("cancel_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("cancel_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="cancel_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User
@mcp.tool()
async def get_current_user() -> dict[str, Any] | ToolResult:
    """Retrieves profile and account information for the currently authenticated user. Useful for identifying who is signed in and accessing their associated details."""

    # Extract parameters for API call
    _http_path = "/me"
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

# Tags: User
@mcp.tool()
async def list_collaborations() -> dict[str, Any] | ToolResult:
    """Retrieves all organizations where the current user is a member or collaborator, spanning multiple VCS providers (e.g., GitHub, BitBucket), parent organizations of accessible repositories, and the user's own account organization."""

    # Extract parameters for API call
    _http_path = "/me/collaborations"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_collaborations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_collaborations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_collaborations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organization
@mcp.tool()
async def create_organization(
    name: str | None = Field(None, description="The display name for the organization being created."),
    vcs_type: Literal["github", "bitbucket", "circleci"] | None = Field(None, description="The version control system associated with the organization, or 'circleci' for a standalone organization not tied to a VCS provider."),
) -> dict[str, Any] | ToolResult:
    """Creates a new organization, either by validating access and syncing data for a VCS provider (GitHub or Bitbucket), or by provisioning a standalone CircleCI organization."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrganizationRequest(
            body=_models.CreateOrganizationRequestBody(name=name, vcs_type=vcs_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/organization"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_organization", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_organization",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organization
@mcp.tool()
async def get_organization(org_slug_or_id: str = Field(..., alias="org-slug-or-id", description="The organization identifier, either as a UUID or a VCS slug in the format `vcs-slug/org-name` (e.g., `gh/` for GitHub, `bb/` for Bitbucket). For GitLab or GitHub App integrations, use `circleci` as the VCS slug and provide the numeric organization ID (found in Organization Settings) in place of the org name.")) -> dict[str, Any] | ToolResult:
    """Retrieves details for a specific organization by its slug or UUID. Supports organizations across GitHub, Bitbucket, and GitLab (via CircleCI VCS slug)."""

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationRequest(
            path=_models.GetOrganizationRequestPath(org_slug_or_id=org_slug_or_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organization/{org-slug-or-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/organization/{org-slug-or-id}"
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

# Tags: Organization
@mcp.tool()
async def delete_organization(org_slug_or_id: str = Field(..., alias="org-slug-or-id", description="The unique identifier for the organization, either as a UUID or a VCS-prefixed slug in the format `vcs-slug/org-name`. For organizations using GitLab or GitHub App, use `circleci` as the VCS slug and the organization ID (found in Organization Settings) as the org name.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an organization and all associated projects and build data. This action is irreversible and will remove all resources tied to the organization."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOrganizationRequest(
            path=_models.DeleteOrganizationRequestPath(org_slug_or_id=org_slug_or_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organization/{org-slug-or-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/organization/{org-slug-or-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_organization", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_organization",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project
@mcp.tool()
async def create_project(
    org_slug_or_id: str = Field(..., alias="org-slug-or-id", description="The unique identifier for the organization, either as a UUID or a VCS-based slug in the format `vcs-slug/org-name`. For organizations using GitLab or GitHub App integrations, use `circleci` as the VCS slug and provide the numeric organization ID (available in Organization Settings) in place of the org name."),
    name: str | None = Field(None, description="The display name for the new project. Should be unique within the organization and clearly identify the project."),
) -> dict[str, Any] | ToolResult:
    """Creates a new project within the specified organization. Works across all organization types including GitHub, GitLab, and CircleCI-managed organizations."""

    # Construct request model with validation
    try:
        _request = _models.CreateProjectRequest(
            path=_models.CreateProjectRequestPath(org_slug_or_id=org_slug_or_id),
            body=_models.CreateProjectRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organization/{org-slug-or-id}/project", _request.path.model_dump(by_alias=True)) if _request.path else "/organization/{org-slug-or-id}/project"
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

# Tags: Organization
@mcp.tool()
async def list_url_orb_allow_list_entries(org_slug_or_id: str = Field(..., alias="org-slug-or-id", description="The organization identifier, either as a UUID or a slug in the format `vcs-slug/org-name`. For organizations using GitLab or GitHub App, use `circleci` as the VCS slug and provide the organization ID (available in Organization Settings) in place of the org name.")) -> dict[str, Any] | ToolResult:
    """Retrieves all entries in the URL Orb allow-list for the specified organization. Use this to review which URLs are permitted under the org's URL Orb configuration."""

    # Construct request model with validation
    try:
        _request = _models.ListUrlOrbAllowListEntriesRequest(
            path=_models.ListUrlOrbAllowListEntriesRequestPath(org_slug_or_id=org_slug_or_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_url_orb_allow_list_entries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organization/{org-slug-or-id}/url-orb-allow-list", _request.path.model_dump(by_alias=True)) if _request.path else "/organization/{org-slug-or-id}/url-orb-allow-list"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_url_orb_allow_list_entries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_url_orb_allow_list_entries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_url_orb_allow_list_entries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organization
@mcp.tool()
async def create_url_orb_allow_list_entry(
    org_slug_or_id: str = Field(..., alias="org-slug-or-id", description="The organization identifier, either as a UUID or a slug in the form `vcs-slug/org-name`. For organizations using GitLab or GitHub App, use `circleci` as the vcs-slug and the organization ID (found in Organization Settings) as the org-name."),
    name: str | None = Field(None, description="A human-readable label for this allow-list entry to help identify its purpose within the organization."),
    prefix: Any | None = Field(None, description="The URL prefix that defines which URL orb references are permitted; any orb reference URL beginning with this prefix will be allowed by this entry."),
) -> dict[str, Any] | ToolResult:
    """Adds a new URL prefix entry to an organization's URL Orb allow-list, permitting orb references that begin with the specified URL prefix to be used in pipelines."""

    # Construct request model with validation
    try:
        _request = _models.CreateUrlOrbAllowListEntryRequest(
            path=_models.CreateUrlOrbAllowListEntryRequestPath(org_slug_or_id=org_slug_or_id),
            body=_models.CreateUrlOrbAllowListEntryRequestBody(name=name, prefix=prefix)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_url_orb_allow_list_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organization/{org-slug-or-id}/url-orb-allow-list", _request.path.model_dump(by_alias=True)) if _request.path else "/organization/{org-slug-or-id}/url-orb-allow-list"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_url_orb_allow_list_entry")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_url_orb_allow_list_entry", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_url_orb_allow_list_entry",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Organization
@mcp.tool()
async def delete_url_orb_allow_list_entry(
    org_slug_or_id: str = Field(..., alias="org-slug-or-id", description="The organization identifier, either as a UUID or a slug in the format `vcs-slug/org-name`. For GitLab or GitHub App projects, use `circleci` as the `vcs-slug` and provide the organization ID (found in Organization Settings) as the `org-name`."),
    allow_list_entry_id: str = Field(..., alias="allow-list-entry-id", description="The UUID of the URL orb allow-list entry to remove. This uniquely identifies the specific allow-list entry to be deleted."),
) -> dict[str, Any] | ToolResult:
    """Removes a specific entry from the organization's URL orb allow-list by its unique ID. Use this to revoke previously permitted URLs from the allow-list."""

    # Construct request model with validation
    try:
        _request = _models.RemoveUrlOrbAllowListEntryRequest(
            path=_models.RemoveUrlOrbAllowListEntryRequestPath(org_slug_or_id=org_slug_or_id, allow_list_entry_id=allow_list_entry_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_url_orb_allow_list_entry: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organization/{org-slug-or-id}/url-orb-allow-list/{allow-list-entry-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/organization/{org-slug-or-id}/url-orb-allow-list/{allow-list-entry-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_url_orb_allow_list_entry")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_url_orb_allow_list_entry", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_url_orb_allow_list_entry",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipeline
@mcp.tool()
async def list_pipelines(
    org_slug: str | None = Field(None, alias="org-slug", description="The organization slug identifying the target organization, formatted as vcs-slug/org-name. For GitLab or GitHub App projects, use 'circleci' as the vcs-slug and supply the organization ID (found in Organization Settings) as the org-name."),
    mine: bool | None = Field(None, description="When set to true, restricts results to only pipelines triggered by the authenticated user."),
) -> dict[str, Any] | ToolResult:
    """Retrieves up to 250 pipelines from the most recently built projects you follow within an organization. Optionally filter by organization or limit results to pipelines triggered by your user."""

    # Construct request model with validation
    try:
        _request = _models.ListPipelinesRequest(
            query=_models.ListPipelinesRequestQuery(org_slug=org_slug, mine=mine)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pipelines: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/pipeline"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pipelines")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pipelines", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pipelines",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipeline
@mcp.tool()
async def continue_pipeline(
    continuation_key: str | None = Field(None, alias="continuation-key", description="The unique continuation key that identifies the paused pipeline to resume, obtained from the pipeline setup phase."),
    configuration: str | None = Field(None, description="The full pipeline configuration string to apply when continuing the pipeline, used to supply dynamic configuration at runtime."),
    parameters: dict[str, int | str | bool] | None = Field(None, description="A key-value map of pipeline parameter names to their values, subject to limits of 100 max entries, 128-character maximum key length, and 512-character maximum value length."),
) -> dict[str, Any] | ToolResult:
    """Resumes a pipeline from the setup phase using a continuation key, allowing dynamic configuration and parameter injection. Refer to the Pipeline values and parameters documentation for guidance on using pipeline parameters with dynamic configuration."""

    # Construct request model with validation
    try:
        _request = _models.ContinuePipelineRequest(
            body=_models.ContinuePipelineRequestBody(continuation_key=continuation_key, configuration=configuration, parameters=parameters)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for continue_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/pipeline/continue"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("continue_pipeline")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("continue_pipeline", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="continue_pipeline",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipeline
@mcp.tool()
async def get_pipeline(pipeline_id: str = Field(..., alias="pipeline-id", description="The unique identifier of the pipeline to retrieve, provided as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific pipeline using its unique identifier. Returns the full pipeline configuration and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetPipelineByIdRequest(
            path=_models.GetPipelineByIdRequestPath(pipeline_id=pipeline_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/pipeline/{pipeline-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/pipeline/{pipeline-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pipeline")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pipeline", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pipeline",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipeline
@mcp.tool()
async def get_pipeline_config(pipeline_id: str = Field(..., alias="pipeline-id", description="The unique identifier of the pipeline whose configuration you want to retrieve. Must be a valid UUID corresponding to an existing pipeline.")) -> dict[str, Any] | ToolResult:
    """Retrieves the full configuration for a specific pipeline by its unique ID. Useful for inspecting pipeline settings, stages, and parameters without modifying them."""

    # Construct request model with validation
    try:
        _request = _models.GetPipelineConfigByIdRequest(
            path=_models.GetPipelineConfigByIdRequestPath(pipeline_id=pipeline_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pipeline_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/pipeline/{pipeline-id}/config", _request.path.model_dump(by_alias=True)) if _request.path else "/pipeline/{pipeline-id}/config"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pipeline_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pipeline_config", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pipeline_config",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipeline
@mcp.tool()
async def get_pipeline_values(pipeline_id: str = Field(..., alias="pipeline-id", description="The unique identifier of the pipeline whose values you want to retrieve, in UUID format.")) -> dict[str, Any] | ToolResult:
    """Retrieves a map of built-in pipeline values (such as pipeline number, trigger parameters, and VCS metadata) for a specific pipeline. Useful for inspecting runtime context associated with a pipeline execution."""

    # Construct request model with validation
    try:
        _request = _models.GetPipelineValuesByIdRequest(
            path=_models.GetPipelineValuesByIdRequestPath(pipeline_id=pipeline_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pipeline_values: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/pipeline/{pipeline-id}/values", _request.path.model_dump(by_alias=True)) if _request.path else "/pipeline/{pipeline-id}/values"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pipeline_values")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pipeline_values", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pipeline_values",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipeline
@mcp.tool()
async def list_pipeline_workflows(pipeline_id: str = Field(..., alias="pipeline-id", description="The unique identifier of the pipeline whose workflows you want to retrieve. Must be a valid UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of workflows associated with a specific pipeline. Use this to inspect all workflows belonging to a given pipeline by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.ListWorkflowsByPipelineIdRequest(
            path=_models.ListWorkflowsByPipelineIdRequestPath(pipeline_id=pipeline_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pipeline_workflows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/pipeline/{pipeline-id}/workflow", _request.path.model_dump(by_alias=True)) if _request.path else "/pipeline/{pipeline-id}/workflow"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pipeline_workflows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pipeline_workflows", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pipeline_workflows",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project
@mcp.tool()
async def get_project(project_slug: str = Field(..., alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`, where slashes may be URL-escaped. For GitLab or GitHub App projects, use `circleci` as the VCS slug, the organization ID (from Organization Settings) as the org name, and the project ID (from Project Settings) as the repo name.")) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific CircleCI project using its unique project slug. Supports projects hosted on GitHub, GitLab, and Bitbucket, including those using the GitHub App integration."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectBySlugRequest(
            path=_models.GetProjectBySlugRequestPath(project_slug=project_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}"
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

# Tags: Project
@mcp.tool()
async def delete_project(project_slug: str = Field(..., alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-encoded.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a project from CircleCI using its unique project slug. This action is irreversible and removes all associated project data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteProjectBySlugRequest(
            path=_models.DeleteProjectBySlugRequestPath(project_slug=project_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}"
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

# Tags: Project
@mcp.tool()
async def list_checkout_keys(
    project_slug: str = Field(..., alias="project-slug", description="The project slug uniquely identifying the project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID in place of org-name, and the project ID in place of repo-name; forward slashes may be URL-encoded."),
    digest: Literal["sha256", "md5"] | None = Field(None, description="The hashing algorithm used to format the returned key fingerprints; accepted values are `md5` or `sha256`, defaulting to `md5` if omitted."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all checkout keys associated with a specified project, returning their fingerprints and metadata. Useful for auditing or managing SSH keys used during CI/CD checkout steps."""

    # Construct request model with validation
    try:
        _request = _models.ListCheckoutKeysRequest(
            path=_models.ListCheckoutKeysRequestPath(project_slug=project_slug),
            query=_models.ListCheckoutKeysRequestQuery(digest=digest)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_checkout_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/checkout-key", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/checkout-key"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_checkout_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_checkout_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_checkout_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project
@mcp.tool()
async def create_checkout_key(
    project_slug: str = Field(..., alias="project-slug", description="The project slug identifying the target project, formed as vcs-slug/org-name/repo-name. For GitLab or GitHub App projects, use 'circleci' as the vcs-slug with the organization ID and project ID in place of org-name and repo-name respectively."),
    type_: Literal["user-key", "deploy-key"] | None = Field(None, alias="type", description="The type of checkout key to create: 'deploy-key' grants read-only repository access for deployments, while 'user-key' grants access tied to a specific GitHub user account."),
) -> dict[str, Any] | ToolResult:
    """Creates a new checkout key (deploy key or user key) for a specified project. Only available for GitHub and Bitbucket projects using a user API token; requires GitHub account authorization before creating user keys."""

    # Construct request model with validation
    try:
        _request = _models.CreateCheckoutKeyRequest(
            path=_models.CreateCheckoutKeyRequestPath(project_slug=project_slug),
            body=_models.CreateCheckoutKeyRequestBody(type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_checkout_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/checkout-key", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/checkout-key"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_checkout_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_checkout_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_checkout_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project
@mcp.tool()
async def get_checkout_key(
    project_slug: str = Field(..., alias="project-slug", description="The project slug identifying the target project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-escaped."),
    fingerprint: str = Field(..., description="The SSH key fingerprint used to uniquely identify the checkout key, accepted in either MD5 or SHA256 format. SHA256 fingerprints must be URL-encoded."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific checkout key for a project using its MD5 or SHA256 fingerprint. SHA256 fingerprints must be URL-encoded before being passed as the fingerprint parameter."""

    # Construct request model with validation
    try:
        _request = _models.GetCheckoutKeyRequest(
            path=_models.GetCheckoutKeyRequestPath(project_slug=project_slug, fingerprint=fingerprint)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_checkout_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/checkout-key/{fingerprint}", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/checkout-key/{fingerprint}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_checkout_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_checkout_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_checkout_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project
@mcp.tool()
async def delete_checkout_key(
    project_slug: str = Field(..., alias="project-slug", description="The project slug identifying the target project, formed as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-escaped."),
    fingerprint: str = Field(..., description="The MD5 or SHA256 fingerprint of the SSH checkout key to delete. SHA256 fingerprints must be URL-encoded."),
) -> dict[str, Any] | ToolResult:
    """Deletes a specific checkout key for a project using its MD5 or SHA256 fingerprint. SHA256 fingerprints must be URL-encoded before being passed as the fingerprint parameter."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCheckoutKeyRequest(
            path=_models.DeleteCheckoutKeyRequestPath(project_slug=project_slug, fingerprint=fingerprint)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_checkout_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/checkout-key/{fingerprint}", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/checkout-key/{fingerprint}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_checkout_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_checkout_key", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_checkout_key",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project
@mcp.tool()
async def list_env_vars(project_slug: str = Field(..., alias="project-slug", description="Unique identifier for the project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-encoded.")) -> dict[str, Any] | ToolResult:
    """Retrieves all environment variables for a specified CircleCI project. Values are masked, returning only the last four characters prefixed with four 'x' characters, matching the display behavior on the CircleCI website."""

    # Construct request model with validation
    try:
        _request = _models.ListEnvVarsRequest(
            path=_models.ListEnvVarsRequestPath(project_slug=project_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_env_vars: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/envvar", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/envvar"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_env_vars")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_env_vars", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_env_vars",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project
@mcp.tool()
async def create_env_var(
    project_slug: str = Field(..., alias="project-slug", description="The project slug uniquely identifying the target project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-escaped."),
    name: str | None = Field(None, description="The name of the environment variable to create, which must be unique within the project and will be used to reference the variable in pipeline configurations."),
    value: str | None = Field(None, description="The value to assign to the environment variable; once stored, this value will be masked and not returned in plaintext by the API."),
) -> dict[str, Any] | ToolResult:
    """Creates a new environment variable for a specified CircleCI project, making it available to pipelines and jobs running within that project."""

    # Construct request model with validation
    try:
        _request = _models.CreateEnvVarRequest(
            path=_models.CreateEnvVarRequestPath(project_slug=project_slug),
            body=_models.CreateEnvVarRequestBody(name=name, value=value)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_env_var: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/envvar", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/envvar"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_env_var")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_env_var", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_env_var",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project
@mcp.tool()
async def get_env_var(
    project_slug: str = Field(..., alias="project-slug", description="The project slug identifying the target project, formed as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID as org-name, and the project ID as repo-name. Forward slashes may be URL-escaped."),
    name: str = Field(..., description="The exact name of the environment variable to retrieve, matching the name as defined in the project's environment variable settings."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the masked value of a specific environment variable for a given project. The returned value is masked for security purposes."""

    # Construct request model with validation
    try:
        _request = _models.GetEnvVarRequest(
            path=_models.GetEnvVarRequestPath(project_slug=project_slug, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_env_var: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/envvar/{name}", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/envvar/{name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_env_var")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_env_var", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_env_var",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project
@mcp.tool()
async def delete_env_var(
    project_slug: str = Field(..., alias="project-slug", description="The project slug uniquely identifying the target project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name; forward slashes may be URL-encoded."),
    name: str = Field(..., description="The exact name of the environment variable to delete, matching the variable's name as it appears in the project's environment variable settings."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific environment variable from a CircleCI project. This action is irreversible and immediately removes the variable from the project's configuration."""

    # Construct request model with validation
    try:
        _request = _models.DeleteEnvVarRequest(
            path=_models.DeleteEnvVarRequestPath(project_slug=project_slug, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_env_var: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/envvar/{name}", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/envvar/{name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_env_var")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_env_var", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_env_var",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Job
@mcp.tool()
async def get_job_details(
    job_number: Any = Field(..., alias="job-number", description="The unique numeric identifier of the job to retrieve details for."),
    project_slug: str = Field(..., alias="project-slug", description="Project slug identifying the target project in the format `vcs-slug/org-name/repo-name`, where slashes may be URL-escaped. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID as org-name, and the project ID as repo-name."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific job within a project, including its status, timing, and configuration. Use this to inspect the outcome or metadata of a particular job run."""

    # Construct request model with validation
    try:
        _request = _models.GetJobDetailsRequest(
            path=_models.GetJobDetailsRequestPath(job_number=job_number, project_slug=project_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_job_details: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/job/{job-number}", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/job/{job-number}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_job_details")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_job_details", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_job_details",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Job
@mcp.tool()
async def cancel_job_by_number(
    job_number: Any = Field(..., alias="job-number", description="The unique numeric identifier of the job to cancel within the project."),
    project_slug: str = Field(..., alias="project-slug", description="Project slug identifying the target project, formatted as vcs-slug/org-name/repo-name. For GitLab or GitHub App projects, use circleci as the vcs-slug, the organization ID as org-name, and the project ID as repo-name; forward slashes may be URL-escaped."),
) -> dict[str, Any] | ToolResult:
    """Cancels a running job in a specified project using its job number. Useful for stopping unwanted or erroneous builds mid-execution."""

    # Construct request model with validation
    try:
        _request = _models.CancelJobByJobNumberRequest(
            path=_models.CancelJobByJobNumberRequestPath(job_number=job_number, project_slug=project_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for cancel_job_by_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/job/{job-number}/cancel", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/job/{job-number}/cancel"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("cancel_job_by_number")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("cancel_job_by_number", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="cancel_job_by_number",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipeline
@mcp.tool()
async def list_project_pipelines(
    project_slug: str = Field(..., alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-encoded."),
    branch: str | None = Field(None, description="Filters returned pipelines to only those triggered on the specified branch name. When omitted, pipelines from all branches are returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all pipelines for a specified project, optionally filtered by branch. Useful for monitoring CI/CD activity and pipeline history across a project."""

    # Construct request model with validation
    try:
        _request = _models.ListPipelinesForProjectRequest(
            path=_models.ListPipelinesForProjectRequestPath(project_slug=project_slug),
            query=_models.ListPipelinesForProjectRequestQuery(branch=branch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_pipelines: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/pipeline", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/pipeline"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_pipelines")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_pipelines", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_pipelines",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipeline
@mcp.tool()
async def trigger_pipeline(
    project_slug: str = Field(..., alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`, where forward slashes may be URL-encoded. For GitLab or GitHub App projects, use `circleci` as the vcs-slug with the organization ID and project ID in place of org and repo names."),
    branch: str | None = Field(None, description="The branch to run the pipeline against, using the HEAD commit of that branch. Mutually exclusive with `tag`; only one may be provided. To target a pull request, use `pull/<number>/head` for the PR ref or `pull/<number>/merge` for the merge ref (GitHub only)."),
    tag: str | None = Field(None, description="A Git tag whose pointed-to commit will be used for the pipeline run. Mutually exclusive with `branch`; only one may be provided."),
    parameters: dict[str, int | str | bool] | None = Field(None, description="A key-value map of pipeline parameter names to their values, used to customize the pipeline run. Limited to 100 entries, with keys up to 128 characters and values up to 512 characters each."),
) -> dict[str, Any] | ToolResult:
    """Triggers a new pipeline run on a specified project using a branch, tag, or custom parameters. Note: this endpoint does not support GitLab or GitHub App projects — use the Trigger Pipeline Run API for those."""

    # Construct request model with validation
    try:
        _request = _models.TriggerPipelineRequest(
            path=_models.TriggerPipelineRequestPath(project_slug=project_slug),
            body=_models.TriggerPipelineRequestBody(branch=branch, tag=tag, parameters=parameters)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for trigger_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/pipeline", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/pipeline"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("trigger_pipeline")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("trigger_pipeline", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="trigger_pipeline",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipeline
@mcp.tool()
async def list_my_pipelines(project_slug: str = Field(..., alias="project-slug", description="Unique identifier for the project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-encoded.")) -> dict[str, Any] | ToolResult:
    """Retrieves all pipelines for a specified project that were triggered by the authenticated user. Returns results as a sequence ordered by trigger time."""

    # Construct request model with validation
    try:
        _request = _models.ListMyPipelinesRequest(
            path=_models.ListMyPipelinesRequestPath(project_slug=project_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_my_pipelines: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/pipeline/mine", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/pipeline/mine"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_my_pipelines")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_my_pipelines", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_my_pipelines",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipeline
@mcp.tool()
async def get_pipeline_by_number(
    project_slug: str = Field(..., alias="project-slug", description="The project slug identifying the target project, formatted as `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID as org-name, and the project ID as repo-name."),
    pipeline_number: Any = Field(..., alias="pipeline-number", description="The sequential number assigned to the pipeline within the project, uniquely identifying it among all pipelines for that project."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific pipeline by its number within a given project. Returns full pipeline details including status, configuration, and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetPipelineByNumberRequest(
            path=_models.GetPipelineByNumberRequestPath(project_slug=project_slug, pipeline_number=pipeline_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pipeline_by_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/pipeline/{pipeline-number}", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/pipeline/{pipeline-number}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pipeline_by_number")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pipeline_by_number", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pipeline_by_number",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Schedule
@mcp.tool()
async def list_project_schedules(project_slug: str = Field(..., alias="project-slug", description="Unique identifier for the project in the format `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID (from Organization Settings) as org-name, and the project ID (from Project Settings) as repo-name. Forward slashes may be URL-encoded.")) -> dict[str, Any] | ToolResult:
    """Retrieves all schedule triggers associated with GitHub OAuth or Bitbucket Cloud pipeline definitions for a given project. Note: schedules for GitHub App pipelines are not included and must be fetched via the List Pipeline Definition Triggers endpoint."""

    # Construct request model with validation
    try:
        _request = _models.ListSchedulesForProjectRequest(
            path=_models.ListSchedulesForProjectRequestPath(project_slug=project_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_schedules: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/schedule", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/schedule"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_schedules")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_schedules", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_schedules",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Schedule
@mcp.tool()
async def create_schedule(
    project_slug: str = Field(..., alias="project-slug", description="The project identifier in the format `vcs-slug/org-name/repo-name`, where forward slashes may be URL-escaped. For GitLab or GitHub App projects, use `circleci` as the vcs-slug with the organization ID and project ID in place of org and repo names."),
    name: str | None = Field(None, description="A human-readable name for the schedule used to identify it within the project."),
    timetable: _models.CreateScheduleBodyTimetableV0 | _models.CreateScheduleBodyTimetableV1 | None = Field(None, description="The timetable definition specifying when the schedule should trigger, including frequency, days, and time settings."),
    attribution_actor: Literal["current", "system"] | None = Field(None, alias="attribution-actor", description="Determines which actor's permissions are used when the scheduled pipeline runs — `current` uses the token owner's permissions, while `system` uses neutral system-level permissions."),
    parameters: dict[str, int | str | bool] | None = Field(None, description="Key-value pairs of pipeline parameters passed to each triggered pipeline run; must include at least a `branch` or `tag` key to specify the target ref."),
    description: str | None = Field(None, description="An optional human-readable description providing additional context about the schedule's purpose or behavior."),
) -> dict[str, Any] | ToolResult:
    """Creates a recurring pipeline schedule for a project and returns the created schedule. Available only for Bitbucket and GitHub OAuth organizations; for GitHub App or CircleCI project types, use the Create Trigger endpoint instead."""

    # Construct request model with validation
    try:
        _request = _models.CreateScheduleRequest(
            path=_models.CreateScheduleRequestPath(project_slug=project_slug),
            body=_models.CreateScheduleRequestBody(name=name, timetable=timetable, attribution_actor=attribution_actor, parameters=parameters, description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_schedule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/schedule", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/schedule"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_schedule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_schedule", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_schedule",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Job
@mcp.tool()
async def list_job_artifacts(
    job_number: Any = Field(..., alias="job-number", description="The unique number identifying the job within the project whose artifacts you want to retrieve."),
    project_slug: str = Field(..., alias="project-slug", description="Project slug uniquely identifying the project in the format `vcs-slug/org-name/repo-name`. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID as org-name, and the project ID as repo-name. Forward slashes may be URL-escaped."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all artifacts produced by a specific job in a CircleCI project. Useful for accessing build outputs such as test reports, binaries, or logs."""

    # Construct request model with validation
    try:
        _request = _models.GetJobArtifactsRequest(
            path=_models.GetJobArtifactsRequestPath(job_number=job_number, project_slug=project_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_job_artifacts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/{job-number}/artifacts", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/{job-number}/artifacts"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_job_artifacts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_job_artifacts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_job_artifacts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Job
@mcp.tool()
async def list_job_tests(
    job_number: Any = Field(..., alias="job-number", description="The unique numeric identifier of the job whose test metadata you want to retrieve."),
    project_slug: str = Field(..., alias="project-slug", description="Project slug identifying the target project in the format `vcs-slug/org-name/repo-name`, where URL-escaping of `/` is supported. For GitLab or GitHub App projects, use `circleci` as the vcs-slug, the organization ID as org-name, and the project ID as repo-name."),
) -> dict[str, Any] | ToolResult:
    """Retrieves test metadata for a specific job within a project, including results and timing information. Returns no results if test data exceeds 250MB for the job."""

    # Construct request model with validation
    try:
        _request = _models.GetTestsRequest(
            path=_models.GetTestsRequestPath(job_number=job_number, project_slug=project_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_job_tests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{project-slug}/{job-number}/tests", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{project-slug}/{job-number}/tests"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_job_tests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_job_tests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_job_tests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Schedule
@mcp.tool()
async def get_schedule(schedule_id: str = Field(..., alias="schedule-id", description="The unique identifier of the schedule to retrieve, in UUID format.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific pipeline schedule by its unique ID. Only available for schedules associated with GitHub OAuth or Bitbucket Cloud pipeline definitions."""

    # Construct request model with validation
    try:
        _request = _models.GetScheduleByIdRequest(
            path=_models.GetScheduleByIdRequestPath(schedule_id=schedule_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_schedule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/schedule/{schedule-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/schedule/{schedule-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_schedule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_schedule", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_schedule",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Schedule
@mcp.tool()
async def update_schedule(
    schedule_id: str = Field(..., alias="schedule-id", description="The unique UUID identifying the schedule to update."),
    description: str | None = Field(None, description="A human-readable description of the schedule's purpose or behavior."),
    name: str | None = Field(None, description="The display name of the schedule."),
    per_hour: str | None = Field(None, alias="per-hour", description="How many times the schedule triggers per hour; must be a whole number between 1 and 60. Mutually exclusive with hour-based scheduling fields."),
    hours_of_day: list[int] | None = Field(None, alias="hours-of-day", description="List of hours within a day (0–23) during which the schedule triggers; order is not significant."),
    days_of_week: list[Literal["TUE", "SAT", "SUN", "MON", "THU", "WED", "FRI"]] | None = Field(None, alias="days-of-week", description="List of days of the week on which the schedule triggers (e.g., MON, TUE); mutually exclusive with days-of-month."),
    days_of_month: list[int] | None = Field(None, alias="days-of-month", description="List of calendar days of the month (1–31) on which the schedule triggers; mutually exclusive with days-of-week."),
    months: list[Literal["MAR", "NOV", "DEC", "JUN", "MAY", "OCT", "FEB", "APR", "SEP", "AUG", "JAN", "JUL"]] | None = Field(None, description="List of months in which the schedule triggers (e.g., JAN, FEB); order is not significant."),
    attribution_actor: Literal["current", "system"] | None = Field(None, alias="attribution-actor", description="Determines whose permissions are used when the scheduled pipeline runs: 'current' uses the token owner's permissions, 'system' uses a neutral system actor."),
    parameters: dict[str, int | str | bool] | None = Field(None, description="Key-value pairs of pipeline parameters to pass when the schedule triggers; must include either a branch or tag key to specify the target ref."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing pipeline schedule by ID and returns the updated schedule. Only available for schedules associated with GitHub OAuth or Bitbucket Cloud pipeline definitions; use the Update Trigger endpoint for GitHub App pipeline definitions."""

    _per_hour = _parse_int(per_hour)

    # Construct request model with validation
    try:
        _request = _models.UpdateScheduleRequest(
            path=_models.UpdateScheduleRequestPath(schedule_id=schedule_id),
            body=_models.UpdateScheduleRequestBody(description=description, name=name, attribution_actor=attribution_actor, parameters=parameters,
                timetable=_models.UpdateScheduleRequestBodyTimetable(per_hour=_per_hour, hours_of_day=hours_of_day, days_of_week=days_of_week, days_of_month=days_of_month, months=months) if any(v is not None for v in [per_hour, hours_of_day, days_of_week, days_of_month, months]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_schedule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/schedule/{schedule-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/schedule/{schedule-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_schedule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_schedule", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_schedule",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Schedule
@mcp.tool()
async def delete_schedule(schedule_id: str = Field(..., alias="schedule-id", description="The unique identifier of the schedule to delete, in UUID format.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a pipeline schedule by its unique ID. Only available for schedules associated with GitHub OAuth or Bitbucket Cloud pipeline definitions."""

    # Construct request model with validation
    try:
        _request = _models.DeleteScheduleByIdRequest(
            path=_models.DeleteScheduleByIdRequestPath(schedule_id=schedule_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_schedule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/schedule/{schedule-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/schedule/{schedule-id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_schedule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_schedule", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_schedule",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: User
@mcp.tool()
async def get_user(id_: str = Field(..., alias="id", description="The unique identifier of the user whose information should be retrieved, provided as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieves profile and account information for a specific user. Use this to look up user details by their unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetUserRequest(
            path=_models.GetUserRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/user/{id}"
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

# Tags: Webhook
@mcp.tool()
async def list_webhooks(
    scope_id: str = Field(..., alias="scope-id", description="The unique identifier of the scope entity to filter webhooks by. Currently only project IDs are supported."),
    scope_type: Literal["project"] = Field(..., alias="scope-type", description="The type of scope used to filter webhooks. Determines how the scope-id is interpreted; currently only 'project' is supported."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all outbound webhooks associated with a given scope. Currently supports project-level scoping by providing a project ID."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhooksRequest(
            query=_models.GetWebhooksRequestQuery(scope_id=scope_id, scope_type=scope_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/webhook"
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

# Tags: Webhook
@mcp.tool()
async def create_webhook(
    name: str | None = Field(None, description="Human-readable name to identify the webhook."),
    events: list[Literal["workflow-completed", "job-completed"]] | None = Field(None, description="List of event types that will trigger this webhook; order is not significant and each item should be a valid event type string."),
    url: str | None = Field(None, description="The destination URL where webhook payloads will be delivered; must include the protocol prefix and only HTTPS is supported."),
    verify_tls: bool | None = Field(None, alias="verify-tls", description="When set to true, enforces strict TLS certificate verification on the destination URL before delivering the webhook payload."),
    signing_secret: str | None = Field(None, alias="signing-secret", description="A secret string used to generate an HMAC hash of the outgoing payload, which is passed as a header so the receiver can verify authenticity."),
    id_: str | None = Field(None, alias="id", description="The UUID of the scope (e.g., a project) this webhook is associated with; currently only project IDs are supported."),
    type_: Literal["project"] | None = Field(None, alias="type", description="The type of scope the provided ID refers to; currently only project-level scopes are supported."),
) -> dict[str, Any] | ToolResult:
    """Creates an outbound webhook that listens for specified events and delivers payloads to a designated HTTPS URL. Supports TLS verification enforcement and HMAC payload signing for secure delivery."""

    # Construct request model with validation
    try:
        _request = _models.CreateWebhookRequest(
            body=_models.CreateWebhookRequestBody(name=name, events=events, url=url, verify_tls=verify_tls, signing_secret=signing_secret,
                scope=_models.CreateWebhookRequestBodyScope(id_=id_, type_=type_) if any(v is not None for v in [id_, type_]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/webhook"
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
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhook
@mcp.tool()
async def get_webhook(webhook_id: str = Field(..., alias="webhook-id", description="The unique identifier of the outbound webhook to retrieve, provided as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieves the configuration and details of a specific outbound webhook by its unique identifier. Use this to inspect webhook settings such as target URL, events, and status."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhookByIdRequest(
            path=_models.GetWebhookByIdRequestPath(webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/webhook/{webhook-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/webhook/{webhook-id}"
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

# Tags: Webhook
@mcp.tool()
async def update_webhook(
    webhook_id: str = Field(..., alias="webhook-id", description="The unique identifier of the webhook to update."),
    name: str | None = Field(None, description="A human-readable label for the webhook, used to identify it in listings and logs."),
    events: list[Literal["workflow-completed", "job-completed"]] | None = Field(None, description="List of event types that will trigger this webhook; order is not significant and each item should be a valid event type string supported by the platform."),
    url: str | None = Field(None, description="The destination URL where webhook payloads will be delivered; must use the HTTPS protocol (HTTP is not supported)."),
    signing_secret: str | None = Field(None, alias="signing-secret", description="A secret string used to generate an HMAC signature of the payload, which is passed as a request header so the receiver can verify the webhook's authenticity."),
    verify_tls: bool | None = Field(None, alias="verify-tls", description="When set to true, enforces strict TLS certificate validation on the destination URL; set to false only if delivering to an endpoint with a self-signed or otherwise unverifiable certificate."),
) -> dict[str, Any] | ToolResult:
    """Updates the configuration of an existing outbound webhook, allowing changes to its name, target URL, triggered events, signing secret, and TLS verification behavior. Only fields provided in the request will be updated."""

    # Construct request model with validation
    try:
        _request = _models.UpdateWebhookRequest(
            path=_models.UpdateWebhookRequestPath(webhook_id=webhook_id),
            body=_models.UpdateWebhookRequestBody(name=name, events=events, url=url, signing_secret=signing_secret, verify_tls=verify_tls)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/webhook/{webhook-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/webhook/{webhook-id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_webhook", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_webhook",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhook
@mcp.tool()
async def delete_webhook(webhook_id: str = Field(..., alias="webhook-id", description="The unique identifier of the outbound webhook to delete, provided as a UUID.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an outbound webhook, stopping all future event deliveries to its configured endpoint. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWebhookRequest(
            path=_models.DeleteWebhookRequestPath(webhook_id=webhook_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/webhook/{webhook-id}", _request.path.model_dump(by_alias=True)) if _request.path else "/webhook/{webhook-id}"
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

# Tags: Workflow
@mcp.tool()
async def get_workflow(id_: str = Field(..., alias="id", description="The unique identifier of the workflow to retrieve, in UUID format.")) -> dict[str, Any] | ToolResult:
    """Retrieves summary fields for a specific workflow by its unique identifier. Useful for checking workflow metadata such as name, status, and configuration details."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkflowByIdRequest(
            path=_models.GetWorkflowByIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workflow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workflow/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/workflow/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workflow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workflow", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workflow",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflow
@mcp.tool()
async def approve_workflow_job(
    approval_request_id: str = Field(..., description="The unique identifier of the pending approval job to approve, in UUID format."),
    id_: str = Field(..., alias="id", description="The unique identifier of the workflow containing the pending approval job, in UUID format."),
) -> dict[str, Any] | ToolResult:
    """Approves a pending approval job within a specified workflow, allowing the workflow to continue past the approval gate."""

    # Construct request model with validation
    try:
        _request = _models.ApprovePendingApprovalJobByIdRequest(
            path=_models.ApprovePendingApprovalJobByIdRequestPath(approval_request_id=approval_request_id, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for approve_workflow_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workflow/{id}/approve/{approval_request_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/workflow/{id}/approve/{approval_request_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("approve_workflow_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("approve_workflow_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="approve_workflow_job",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflow
@mcp.tool()
async def cancel_workflow(id_: str = Field(..., alias="id", description="The unique identifier of the workflow to cancel. Must correspond to an existing, currently running workflow.")) -> dict[str, Any] | ToolResult:
    """Cancels a currently running workflow, halting any further execution. Use this to stop a workflow that is in progress before it completes naturally."""

    # Construct request model with validation
    try:
        _request = _models.CancelWorkflowRequest(
            path=_models.CancelWorkflowRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for cancel_workflow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workflow/{id}/cancel", _request.path.model_dump(by_alias=True)) if _request.path else "/workflow/{id}/cancel"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("cancel_workflow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("cancel_workflow", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="cancel_workflow",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflow
@mcp.tool()
async def list_workflow_jobs(id_: str = Field(..., alias="id", description="The unique identifier of the workflow whose jobs you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the ordered sequence of jobs associated with a specific workflow. Use this to inspect all jobs belonging to a workflow and their current states."""

    # Construct request model with validation
    try:
        _request = _models.ListWorkflowJobsRequest(
            path=_models.ListWorkflowJobsRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflow_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workflow/{id}/job", _request.path.model_dump(by_alias=True)) if _request.path else "/workflow/{id}/job"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflow_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflow_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflow_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflow
@mcp.tool()
async def rerun_workflow(
    id_: str = Field(..., alias="id", description="The unique identifier of the workflow to rerun."),
    enable_ssh: bool | None = Field(None, description="When true, enables SSH access for the triggering user on the newly rerun job. Requires the jobs parameter to be specified and is mutually exclusive with from_failed."),
    from_failed: bool | None = Field(None, description="When true, reruns the workflow starting from the first failed job rather than the beginning. Mutually exclusive with the jobs and sparse_tree parameters."),
    jobs: list[str] | None = Field(None, description="A list of specific job IDs (UUIDs) to rerun within the workflow. Order is not significant. Mutually exclusive with from_failed."),
    sparse_tree: bool | None = Field(None, description="When true, applies sparse tree optimization logic during the rerun, improving performance for workflows containing disconnected subgraphs. Requires the jobs parameter and is mutually exclusive with from_failed."),
) -> dict[str, Any] | ToolResult:
    """Reruns an existing workflow by its ID, with options to rerun from the first failed job, target specific jobs, or apply sparse tree optimization for complex workflow graphs."""

    # Construct request model with validation
    try:
        _request = _models.RerunWorkflowRequest(
            path=_models.RerunWorkflowRequestPath(id_=id_),
            body=_models.RerunWorkflowRequestBody(enable_ssh=enable_ssh, from_failed=from_failed, jobs=jobs, sparse_tree=sparse_tree)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rerun_workflow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workflow/{id}/rerun", _request.path.model_dump(by_alias=True)) if _request.path else "/workflow/{id}/rerun"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("rerun_workflow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("rerun_workflow", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="rerun_workflow",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: OIDC Token Management
@mcp.tool()
async def list_org_oidc_custom_claims(org_id: str = Field(..., alias="orgID", description="The unique identifier of the organization whose OIDC custom claims should be retrieved.")) -> dict[str, Any] | ToolResult:
    """Retrieves the org-level custom claims configured for OIDC identity tokens. Use this to inspect which additional claims are included in tokens issued for the specified organization."""

    # Construct request model with validation
    try:
        _request = _models.GetOrgClaimsRequest(
            path=_models.GetOrgClaimsRequestPath(org_id=org_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_org_oidc_custom_claims: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/org/{orgID}/oidc-custom-claims", _request.path.model_dump(by_alias=True)) if _request.path else "/org/{orgID}/oidc-custom-claims"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_org_oidc_custom_claims")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_org_oidc_custom_claims", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_org_oidc_custom_claims",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: OIDC Token Management
@mcp.tool()
async def update_org_oidc_claims(
    org_id: str = Field(..., alias="orgID", description="The unique identifier of the organization whose OIDC custom claims will be updated."),
    audience: list[str] | None = Field(None, description="List of intended recipients (audiences) for the OIDC token; order is not significant and each item should be a valid audience identifier string."),
    ttl: str | None = Field(None, description="Token time-to-live duration specifying how long the OIDC token remains valid; composed of one to seven time unit segments using milliseconds (ms), seconds (s), minutes (m), hours (h), days (d), or weeks (w).", pattern="^([0-9]+(ms|s|m|h|d|w)){1,7}$"),
) -> dict[str, Any] | ToolResult:
    """Creates or updates org-level custom claims on OIDC identity tokens for the specified organization. Use this to configure audience restrictions and token time-to-live settings."""

    # Construct request model with validation
    try:
        _request = _models.PatchOrgClaimsRequest(
            path=_models.PatchOrgClaimsRequestPath(org_id=org_id),
            body=_models.PatchOrgClaimsRequestBody(audience=audience, ttl=ttl)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_org_oidc_claims: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/org/{orgID}/oidc-custom-claims", _request.path.model_dump(by_alias=True)) if _request.path else "/org/{orgID}/oidc-custom-claims"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_org_oidc_claims")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_org_oidc_claims", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_org_oidc_claims",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: OIDC Token Management
@mcp.tool()
async def delete_org_oidc_claims(
    org_id: str = Field(..., alias="orgID", description="The unique identifier of the organization whose custom OIDC claims will be deleted."),
    claims: str = Field(..., description="Comma-separated list of custom OIDC claim names to delete. Valid values are 'audience' and 'ttl'; multiple values may be combined in a single request."),
) -> dict[str, Any] | ToolResult:
    """Deletes one or more custom OIDC identity token claims configured at the organization level. Supports removing the 'audience' and/or 'ttl' claim overrides."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOrgClaimsRequest(
            path=_models.DeleteOrgClaimsRequestPath(org_id=org_id),
            query=_models.DeleteOrgClaimsRequestQuery(claims=claims)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_org_oidc_claims: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/org/{orgID}/oidc-custom-claims", _request.path.model_dump(by_alias=True)) if _request.path else "/org/{orgID}/oidc-custom-claims"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_org_oidc_claims")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_org_oidc_claims", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_org_oidc_claims",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: OIDC Token Management
@mcp.tool()
async def get_project_oidc_claims(
    org_id: str = Field(..., alias="orgID", description="The unique identifier of the organization that owns the project."),
    project_id: str = Field(..., alias="projectID", description="The unique identifier of the project whose custom OIDC claims are being retrieved."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the custom OIDC identity token claims configured at the project level. Use this to inspect which additional claims are included in tokens issued for a specific project."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectClaimsRequest(
            path=_models.GetProjectClaimsRequestPath(org_id=org_id, project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_oidc_claims: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/org/{orgID}/project/{projectID}/oidc-custom-claims", _request.path.model_dump(by_alias=True)) if _request.path else "/org/{orgID}/project/{projectID}/oidc-custom-claims"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_oidc_claims")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_oidc_claims", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_oidc_claims",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: OIDC Token Management
@mcp.tool()
async def update_project_oidc_claims(
    org_id: str = Field(..., alias="orgID", description="Unique identifier of the organization that owns the project."),
    project_id: str = Field(..., alias="projectID", description="Unique identifier of the project whose OIDC custom claims are being created or updated."),
    audience: list[str] | None = Field(None, description="List of intended audiences for the OIDC token. Order is not significant; each item should be a valid audience string identifying a recipient that the token is intended for."),
    ttl: str | None = Field(None, description="Time-to-live duration for the OIDC token, specifying how long it remains valid. Accepts a compound duration string composed of up to seven unit segments in descending order, using units: weeks (w), days (d), hours (h), minutes (m), seconds (s), and milliseconds (ms).", pattern="^([0-9]+(ms|s|m|h|d|w)){1,7}$"),
) -> dict[str, Any] | ToolResult:
    """Creates or updates project-level custom claims on OIDC identity tokens for the specified project. Use this to configure audience restrictions and token time-to-live at the project scope."""

    # Construct request model with validation
    try:
        _request = _models.PatchProjectClaimsRequest(
            path=_models.PatchProjectClaimsRequestPath(org_id=org_id, project_id=project_id),
            body=_models.PatchProjectClaimsRequestBody(audience=audience, ttl=ttl)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project_oidc_claims: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/org/{orgID}/project/{projectID}/oidc-custom-claims", _request.path.model_dump(by_alias=True)) if _request.path else "/org/{orgID}/project/{projectID}/oidc-custom-claims"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project_oidc_claims")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project_oidc_claims", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project_oidc_claims",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: OIDC Token Management
@mcp.tool()
async def delete_project_oidc_claims(
    org_id: str = Field(..., alias="orgID", description="Unique identifier of the organization that owns the project."),
    project_id: str = Field(..., alias="projectID", description="Unique identifier of the project whose OIDC custom claims will be deleted."),
    claims: str = Field(..., description="Comma-separated list of custom claim names to delete. Valid values are 'audience' and 'ttl'; multiple values may be combined in a single request."),
) -> dict[str, Any] | ToolResult:
    """Deletes one or more custom claims from the OIDC identity token configuration at the project level. Only the 'audience' and 'ttl' claims are eligible for deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteProjectClaimsRequest(
            path=_models.DeleteProjectClaimsRequestPath(org_id=org_id, project_id=project_id),
            query=_models.DeleteProjectClaimsRequestQuery(claims=claims)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project_oidc_claims: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/org/{orgID}/project/{projectID}/oidc-custom-claims", _request.path.model_dump(by_alias=True)) if _request.path else "/org/{orgID}/project/{projectID}/oidc-custom-claims"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_project_oidc_claims")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_project_oidc_claims", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_project_oidc_claims",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Policy Management
@mcp.tool()
async def list_decision_logs(
    owner_id: str = Field(..., alias="ownerID", description="The unique identifier of the owner whose policy decision logs are being retrieved."),
    context: str = Field(..., description="The policy context scope under which decisions were evaluated and logged."),
    status: str | None = Field(None, description="Filters results to only include decisions that match the specified decision status (e.g., approved or rejected)."),
    after: str | None = Field(None, description="Filters results to only include decisions made after this timestamp. Must be a valid ISO 8601 date-time string."),
    before: str | None = Field(None, description="Filters results to only include decisions made before this timestamp. Must be a valid ISO 8601 date-time string."),
    branch: str | None = Field(None, description="Filters results to only include decisions made on the specified branch name."),
    project_id: str | None = Field(None, description="Filters results to only include decisions associated with the specified project identifier."),
    build_number: str | None = Field(None, description="Filters results to only include decisions associated with the specified build number."),
    offset: int | None = Field(None, description="The number of records to skip before returning results, enabling pagination through large result sets."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of policy decision audit logs for the specified owner and context. Results can be filtered by status, date range, branch, project, or build number."""

    # Construct request model with validation
    try:
        _request = _models.GetDecisionLogsRequest(
            path=_models.GetDecisionLogsRequestPath(owner_id=owner_id, context=context),
            query=_models.GetDecisionLogsRequestQuery(status=status, after=after, before=before, branch=branch, project_id=project_id, build_number=build_number, offset=offset)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_decision_logs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/owner/{ownerID}/context/{context}/decision", _request.path.model_dump(by_alias=True)) if _request.path else "/owner/{ownerID}/context/{context}/decision"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_decision_logs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_decision_logs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_decision_logs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Policy Management
@mcp.tool()
async def get_decision_log(
    owner_id: str = Field(..., alias="ownerID", description="The unique identifier of the owner whose decision audit log is being retrieved."),
    context: str = Field(..., description="The context scope under which the decision was recorded, used to namespace or categorize decisions for the given owner."),
    decision_id: str = Field(..., alias="decisionID", description="The unique identifier of the specific decision log entry to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific decision audit log entry for a given owner and context. Use this to inspect the details and outcome of a previously recorded decision by its unique ID."""

    # Construct request model with validation
    try:
        _request = _models.GetDecisionLogRequest(
            path=_models.GetDecisionLogRequestPath(owner_id=owner_id, context=context, decision_id=decision_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_decision_log: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/owner/{ownerID}/context/{context}/decision/{decisionID}", _request.path.model_dump(by_alias=True)) if _request.path else "/owner/{ownerID}/context/{context}/decision/{decisionID}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_decision_log")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_decision_log", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_decision_log",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Policy Management
@mcp.tool()
async def get_decision_policy_bundle(
    owner_id: str = Field(..., alias="ownerID", description="The unique identifier of the owner (organization or user) whose decision log is being queried."),
    context: str = Field(..., description="The policy context scope under which the decision was evaluated, used to namespace and organize policies."),
    decision_id: str = Field(..., alias="decisionID", description="The unique identifier of the decision log entry for which the associated policy bundle should be retrieved."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the policy bundle associated with a specific decision log entry. Useful for auditing which policies were evaluated at the time a given decision was made."""

    # Construct request model with validation
    try:
        _request = _models.GetDecisionLogPolicyBundleRequest(
            path=_models.GetDecisionLogPolicyBundleRequestPath(owner_id=owner_id, context=context, decision_id=decision_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_decision_policy_bundle: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/owner/{ownerID}/context/{context}/decision/{decisionID}/policy-bundle", _request.path.model_dump(by_alias=True)) if _request.path else "/owner/{ownerID}/context/{context}/decision/{decisionID}/policy-bundle"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_decision_policy_bundle")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_decision_policy_bundle", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_decision_policy_bundle",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Policy Management
@mcp.tool()
async def get_policy_bundle(
    owner_id: str = Field(..., alias="ownerID", description="The unique identifier of the owner whose policy bundle is being retrieved."),
    context: str = Field(..., description="The context scope under which the policy bundle is organized, used to namespace or categorize policies for the specified owner."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the complete policy bundle associated with a specific context for a given owner. Returns all policies grouped within that bundle for review or enforcement purposes."""

    # Construct request model with validation
    try:
        _request = _models.GetPolicyBundleRequest(
            path=_models.GetPolicyBundleRequestPath(owner_id=owner_id, context=context)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_policy_bundle: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/owner/{ownerID}/context/{context}/policy-bundle", _request.path.model_dump(by_alias=True)) if _request.path else "/owner/{ownerID}/context/{context}/policy-bundle"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_policy_bundle")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_policy_bundle", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_policy_bundle",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Context
@mcp.tool()
async def list_contexts(
    owner_id: str | None = Field(None, alias="owner-id", description="The unique UUID of the organization that owns the contexts. Use this or owner-slug to identify the organization — find both in CircleCI web app under Organization Settings > Overview."),
    owner_slug: str | None = Field(None, alias="owner-slug", description="The slug identifier for the organization that owns the contexts. Use this or owner-id to identify the organization — find both in CircleCI web app under Organization Settings > Overview. Not supported on CircleCI server."),
    owner_type: Literal["account", "organization"] | None = Field(None, alias="owner-type", description="Specifies whether the owner is an organization or an individual account. Defaults to 'organization'; use 'account' when working with CircleCI server."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all contexts belonging to a specified organization or owner, enabling management of shared environment variables and secrets across projects."""

    # Construct request model with validation
    try:
        _request = _models.ListContextsRequest(
            query=_models.ListContextsRequestQuery(owner_id=owner_id, owner_slug=owner_slug, owner_type=owner_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_contexts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/context"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_contexts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_contexts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_contexts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Context
@mcp.tool()
async def create_context(
    name: str | None = Field(None, description="The human-readable name to assign to the new context, used to identify it within the organization."),
    owner: _models.CreateContextBodyOwnerV0 | _models.CreateContextBodyOwnerV1 | None = Field(None, description="The owner of the context, typically representing the organization or account under which the context will be created."),
) -> dict[str, Any] | ToolResult:
    """Creates a new named context within a specified organization, allowing you to group and manage related environment variables or secrets."""

    # Construct request model with validation
    try:
        _request = _models.CreateContextRequest(
            body=_models.CreateContextRequestBody(name=name, owner=owner)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_context: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/context"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_context")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_context", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_context",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Context
@mcp.tool()
async def get_context(context_id: str = Field(..., description="The unique identifier of the context to retrieve, provided as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieves basic information about a specific context by its unique identifier. Use this to look up context details when you have a known context ID."""

    # Construct request model with validation
    try:
        _request = _models.GetContextRequest(
            path=_models.GetContextRequestPath(context_id=context_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_context: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/context/{context_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/context/{context_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_context")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_context", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_context",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Context
@mcp.tool()
async def delete_context(context_id: str = Field(..., description="The unique identifier of the context to delete. Deleting a context will also remove all environment variables stored within it.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a context and all of its associated environment variables by context ID. This action is irreversible."""

    # Construct request model with validation
    try:
        _request = _models.DeleteContextRequest(
            path=_models.DeleteContextRequestPath(context_id=context_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_context: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/context/{context_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/context/{context_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_context")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_context", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_context",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Context
@mcp.tool()
async def list_context_environment_variables(context_id: str = Field(..., description="The unique identifier of the context whose environment variables should be listed.")) -> dict[str, Any] | ToolResult:
    """Retrieves a list of environment variables defined within a specified context, returning metadata such as names but excluding their values for security."""

    # Construct request model with validation
    try:
        _request = _models.ListEnvironmentVariablesFromContextRequest(
            path=_models.ListEnvironmentVariablesFromContextRequestPath(context_id=context_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_context_environment_variables: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/context/{context_id}/environment-variable", _request.path.model_dump(by_alias=True)) if _request.path else "/context/{context_id}/environment-variable"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_context_environment_variables")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_context_environment_variables", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_context_environment_variables",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Context
@mcp.tool()
async def set_context_environment_variable(
    context_id: str = Field(..., description="The unique identifier of the context in which to create or update the environment variable."),
    env_var_name: str = Field(..., description="The name of the environment variable to create or update within the context."),
    value: str | None = Field(None, description="The value to assign to the environment variable; treated as a secret and not returned in responses."),
) -> dict[str, Any] | ToolResult:
    """Creates or updates a named environment variable within a specified context. Returns metadata about the variable after the operation, excluding its value."""

    # Construct request model with validation
    try:
        _request = _models.AddEnvironmentVariableToContextRequest(
            path=_models.AddEnvironmentVariableToContextRequestPath(context_id=context_id, env_var_name=env_var_name),
            body=_models.AddEnvironmentVariableToContextRequestBody(value=value)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_context_environment_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/context/{context_id}/environment-variable/{env_var_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/context/{context_id}/environment-variable/{env_var_name}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_context_environment_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_context_environment_variable", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_context_environment_variable",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Context
@mcp.tool()
async def delete_context_environment_variable(
    context_id: str = Field(..., description="The unique identifier of the context from which the environment variable will be deleted."),
    env_var_name: str = Field(..., description="The exact name of the environment variable to delete, matching the name as it was originally stored in the context."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a named environment variable from the specified context. This action cannot be undone and will immediately make the variable unavailable to pipelines using that context."""

    # Construct request model with validation
    try:
        _request = _models.DeleteEnvironmentVariableFromContextRequest(
            path=_models.DeleteEnvironmentVariableFromContextRequestPath(context_id=context_id, env_var_name=env_var_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_context_environment_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/context/{context_id}/environment-variable/{env_var_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/context/{context_id}/environment-variable/{env_var_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_context_environment_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_context_environment_variable", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_context_environment_variable",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Context
@mcp.tool()
async def list_context_restrictions(context_id: str = Field(..., description="The unique identifier of the context whose restrictions should be retrieved, provided as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieves all project and expression restrictions associated with a specific context. Returns the complete list of restrictions currently applied to the given context."""

    # Construct request model with validation
    try:
        _request = _models.GetContextRestrictionsRequest(
            path=_models.GetContextRestrictionsRequestPath(context_id=context_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_context_restrictions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/context/{context_id}/restrictions", _request.path.model_dump(by_alias=True)) if _request.path else "/context/{context_id}/restrictions"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_context_restrictions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_context_restrictions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_context_restrictions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Context
@mcp.tool()
async def add_context_restriction(
    context_id: str = Field(..., description="The unique identifier of the context to which the restriction will be added."),
    restriction_type: Literal["project", "expression", "group"] | None = Field(None, description="The category of restriction to apply: 'project' limits access to a specific project, 'expression' applies a rule-based condition, and 'group' restricts access to a specific group."),
    restriction_value: str | None = Field(None, description="The value that defines the restriction rule, interpreted based on the restriction type: a project UUID for 'project' restrictions, or an expression rule string for 'expression' restrictions."),
) -> dict[str, Any] | ToolResult:
    """Adds an access restriction to a context, limiting its use to specific projects, groups, or expression-based rules. Use this to control which projects or conditions are permitted to access the context."""

    # Construct request model with validation
    try:
        _request = _models.CreateContextRestrictionRequest(
            path=_models.CreateContextRestrictionRequestPath(context_id=context_id),
            body=_models.CreateContextRestrictionRequestBody(restriction_type=restriction_type, restriction_value=restriction_value)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_context_restriction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/context/{context_id}/restrictions", _request.path.model_dump(by_alias=True)) if _request.path else "/context/{context_id}/restrictions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_context_restriction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_context_restriction", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_context_restriction",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Context
@mcp.tool()
async def delete_context_restriction(
    context_id: str = Field(..., description="The unique identifier of the context from which the restriction will be deleted."),
    restriction_id: str = Field(..., description="The unique identifier of the specific restriction to delete within the given context."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a specific restriction (project, expression, or group) from a context. This action cannot be undone and immediately revokes the associated access control rule."""

    # Construct request model with validation
    try:
        _request = _models.DeleteContextRestrictionRequest(
            path=_models.DeleteContextRestrictionRequestPath(context_id=context_id, restriction_id=restriction_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_context_restriction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/context/{context_id}/restrictions/{restriction_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/context/{context_id}/restrictions/{restriction_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_context_restriction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_context_restriction", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_context_restriction",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project
@mcp.tool()
async def get_project_settings(
    provider: Literal["github", "gh", "bitbucket", "bb", "circleci"] = Field(..., description="The version control or CI provider portion of the project slug, identifying which platform hosts the project."),
    organization: str = Field(..., description="The organization segment of the project slug, which may be an organization name or a unique organization ID depending on the account type."),
    project: str = Field(..., description="The project segment of the project slug, which may be a project name or a unique project ID depending on the account type."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the advanced settings for a specified CircleCI project, returning each setting with a boolean indicating whether it is enabled or disabled."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectSettingsRequest(
            path=_models.GetProjectSettingsRequestPath(provider=provider, organization=organization, project=project)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{provider}/{organization}/{project}/settings", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{provider}/{organization}/{project}/settings"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Project
@mcp.tool()
async def update_project_settings(
    provider: Literal["github", "gh", "bitbucket", "bb", "circleci"] = Field(..., description="The version control provider for the project, corresponding to the first segment of the project slug visible in Project Settings > Overview."),
    organization: str = Field(..., description="The organization identifier, corresponding to the second segment of the project slug visible in Project Settings > Overview. May be an org name or an org ID depending on the organization type."),
    project: str = Field(..., description="The project identifier, corresponding to the third segment of the project slug visible in Project Settings > Overview. May be a project name or a project ID depending on the organization type."),
    autocancel_builds: bool | None = Field(None, description="When enabled, any running pipelines on a non-default branch are automatically cancelled when a new pipeline starts on that same branch."),
    build_fork_prs: bool | None = Field(None, description="When enabled, CircleCI will run builds triggered by pull requests that originate from forked repositories."),
    build_prs_only: bool | None = Field(None, description="When enabled, CircleCI will only build branches that have at least one associated open pull request."),
    disable_ssh: bool | None = Field(None, description="When set to true, disables the ability to re-run jobs with SSH debugging access for this project."),
    forks_receive_secret_env_vars: bool | None = Field(None, description="When enabled, builds triggered by forked pull requests will have access to this project's environment variables and secrets."),
    oss: bool | None = Field(None, description="When enabled, marks the project as Free and Open Source, granting additional build credits and making builds publicly visible via the web UI and API."),
    set_github_status: bool | None = Field(None, description="When enabled, CircleCI reports the build status of every pushed commit to GitHub's status API, with updates provided per job."),
    setup_workflows: bool | None = Field(None, description="When enabled, allows pipeline configurations to be conditionally triggered from directories outside the primary `.circleci` parent directory using setup workflows."),
    write_settings_requires_admin: bool | None = Field(None, description="When enabled, only organization administrators can update project settings; when disabled, any project member may update settings."),
    pr_only_branch_overrides: list[str] | None = Field(None, description="A list of branch names that will always trigger a build regardless of the `build_prs_only` setting. The provided list completely overwrites the existing value; order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Updates one or more advanced settings for a CircleCI project, such as build behavior, fork policies, SSH access, and GitHub status reporting. Only the settings fields provided in the request body will be modified."""

    # Construct request model with validation
    try:
        _request = _models.PatchProjectSettingsRequest(
            path=_models.PatchProjectSettingsRequestPath(provider=provider, organization=organization, project=project),
            body=_models.PatchProjectSettingsRequestBody(advanced=_models.PatchProjectSettingsRequestBodyAdvanced(autocancel_builds=autocancel_builds, build_fork_prs=build_fork_prs, build_prs_only=build_prs_only, disable_ssh=disable_ssh, forks_receive_secret_env_vars=forks_receive_secret_env_vars, oss=oss, set_github_status=set_github_status, setup_workflows=setup_workflows, write_settings_requires_admin=write_settings_requires_admin, pr_only_branch_overrides=pr_only_branch_overrides) if any(v is not None for v in [autocancel_builds, build_fork_prs, build_prs_only, disable_ssh, forks_receive_secret_env_vars, oss, set_github_status, setup_workflows, write_settings_requires_admin, pr_only_branch_overrides]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{provider}/{organization}/{project}/settings", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{provider}/{organization}/{project}/settings"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project_settings", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project_settings",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def list_organization_groups(
    org_id: str = Field(..., description="The unique identifier of the organization whose groups you want to retrieve."),
    limit: int | None = Field(None, description="The maximum number of group results to return per page. Use this to control pagination when an organization has many groups."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all groups belonging to a specified organization. Supports pagination to control the number of results returned per page."""

    # Construct request model with validation
    try:
        _request = _models.GetOrganizationGroupsRequest(
            path=_models.GetOrganizationGroupsRequestPath(org_id=org_id),
            query=_models.GetOrganizationGroupsRequestQuery(limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{org_id}/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{org_id}/groups"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def create_group(
    org_id: str = Field(..., description="The unique opaque identifier of the organization under which the group will be created."),
    name: str = Field(..., description="The display name for the new group, used to identify it within the organization."),
    description: str | None = Field(None, description="An optional human-readable description providing additional context or purpose for the group."),
) -> dict[str, Any] | ToolResult:
    """Creates a new group within a standalone organization, allowing members and resources to be organized under a named group. Only supported for standalone organizations."""

    # Construct request model with validation
    try:
        _request = _models.CreateOrganizationGroupRequest(
            path=_models.CreateOrganizationGroupRequestPath(org_id=org_id),
            body=_models.CreateOrganizationGroupRequestBody(name=name, description=description)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{org_id}/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{org_id}/groups"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Groups
@mcp.tool()
async def get_group(
    org_id: str = Field(..., description="The unique opaque identifier of the organization that contains the group."),
    group_id: str = Field(..., description="The unique identifier of the group to retrieve, provided as a UUID."),
) -> dict[str, Any] | ToolResult:
    """Retrieves details for a specific group within an organization. Currently only supported for standalone organizations."""

    # Construct request model with validation
    try:
        _request = _models.GetGroupRequest(
            path=_models.GetGroupRequestPath(org_id=org_id, group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{org_id}/groups/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{org_id}/groups/{group_id}"
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

# Tags: Groups
@mcp.tool()
async def delete_group(
    org_id: str = Field(..., description="The unique opaque identifier of the organization that contains the group to be deleted."),
    group_id: str = Field(..., description="The unique UUID identifier of the group to delete. All members and associated role grants will be removed upon deletion."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a group from a standalone organization, removing all its members and revoking any role grants associated with the group."""

    # Construct request model with validation
    try:
        _request = _models.DeleteGroupRequest(
            path=_models.DeleteGroupRequestPath(org_id=org_id, group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{org_id}/groups/{group_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{org_id}/groups/{group_id}"
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

# Tags: Usage
@mcp.tool()
async def create_usage_export(
    org_id: str = Field(..., description="The unique identifier of the organization for which the usage export will be generated."),
    start: str = Field(..., description="The start date and time (inclusive) of the export range in ISO 8601 format. Must be no more than one year in the past."),
    end: str = Field(..., description="The end date and time (inclusive) of the export range in ISO 8601 format. Must be no more than 31 days after the start date."),
    shared_org_ids: list[str] | None = Field(None, description="A list of additional organization IDs whose usage data should be included in the export, useful for aggregating usage across shared or linked organizations. Order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Submits a job to export usage data for an organization within a specified date range. The export covers up to 31 days of data and can optionally include usage from shared organizations."""

    # Construct request model with validation
    try:
        _request = _models.CreateUsageExportRequest(
            path=_models.CreateUsageExportRequestPath(org_id=org_id),
            body=_models.CreateUsageExportRequestBody(start=start, end=end, shared_org_ids=shared_org_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_usage_export: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{org_id}/usage_export_job", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{org_id}/usage_export_job"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_usage_export")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_usage_export", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_usage_export",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Usage
@mcp.tool()
async def get_usage_export_job(
    org_id: str = Field(..., description="The unique opaque identifier of the organization whose usage export job is being retrieved."),
    usage_export_job_id: str = Field(..., description="The unique UUID identifier of the usage export job to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the status and details of a specific usage export job for an organization, including download information once the export is complete."""

    # Construct request model with validation
    try:
        _request = _models.GetUsageExportRequest(
            path=_models.GetUsageExportRequestPath(org_id=org_id, usage_export_job_id=usage_export_job_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_usage_export_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/organizations/{org_id}/usage_export_job/{usage_export_job_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/organizations/{org_id}/usage_export_job/{usage_export_job_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_usage_export_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_usage_export_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_usage_export_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipeline
@mcp.tool()
async def trigger_pipeline_run(
    provider: Literal["github", "gh", "bitbucket", "bb", "circleci"] = Field(..., description="The VCS or platform provider, corresponding to the first segment of the slash-separated project slug found in Project Settings > Overview."),
    organization: str = Field(..., description="The second segment of the slash-separated project slug, representing either a human-readable organization name or an opaque organization ID, as shown in Project Settings > Overview."),
    project: str = Field(..., description="The third segment of the slash-separated project slug, representing either a human-readable project name or an opaque project ID, as shown in Project Settings > Overview."),
    definition_id: str | None = Field(None, description="The UUID of the pipeline definition to run, found in Project Settings > Pipelines. If omitted, the default pipeline definition is used."),
    config_branch: str | None = Field(None, alias="configBranch", description="The branch from which the pipeline config file should be fetched. Mutually exclusive with the config tag field. For GitHub PRs, use pull/<number>/head or pull/<number>/merge."),
    checkout_branch: str | None = Field(None, alias="checkoutBranch", description="The branch to check out source code from during a checkout step. Mutually exclusive with the checkout tag field. For GitHub PRs, use pull/<number>/head or pull/<number>/merge."),
    config_tag: str | None = Field(None, alias="configTag", description="The tag used to fetch the pipeline config file; the pipeline runs against the commit the tag points to. Mutually exclusive with the config branch field."),
    checkout_tag: str | None = Field(None, alias="checkoutTag", description="The tag used to check out source code during a checkout step; the pipeline runs against the commit the tag points to. Mutually exclusive with the checkout branch field."),
    parameters: dict[str, Any] | None = Field(None, description="A key-value map of pipeline parameter names to their values. Limited to 100 entries, with keys up to 128 characters and values up to 512 characters. Values may be strings, booleans, or integers."),
) -> dict[str, Any] | ToolResult:
    """Trigger a new pipeline run for a project using a specific pipeline definition. Supports GitHub, Bitbucket, and CircleCI integrations (GitLab not supported)."""

    # Construct request model with validation
    try:
        _request = _models.TriggerPipelineRunRequest(
            path=_models.TriggerPipelineRunRequestPath(provider=provider, organization=organization, project=project),
            body=_models.TriggerPipelineRunRequestBody(definition_id=definition_id, parameters=parameters,
                config=_models.TriggerPipelineRunRequestBodyConfig(branch=config_branch, tag=config_tag) if any(v is not None for v in [config_branch, config_tag]) else None,
                checkout=_models.TriggerPipelineRunRequestBodyCheckout(branch=checkout_branch, tag=checkout_tag) if any(v is not None for v in [checkout_branch, checkout_tag]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for trigger_pipeline_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/project/{provider}/{organization}/{project}/pipeline/run", _request.path.model_dump(by_alias=True)) if _request.path else "/project/{provider}/{organization}/{project}/pipeline/run"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("trigger_pipeline_run")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("trigger_pipeline_run", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="trigger_pipeline_run",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipeline Definition
@mcp.tool()
async def list_pipeline_definitions(project_id: str = Field(..., description="The unique identifier of the project whose pipeline definitions should be listed.")) -> dict[str, Any] | ToolResult:
    """Retrieves all pipeline definitions associated with a specified project. Pipeline definitions describe the structure and configuration of pipelines available within the project."""

    # Construct request model with validation
    try:
        _request = _models.ListPipelineDefinitionsRequest(
            path=_models.ListPipelineDefinitionsRequestPath(project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pipeline_definitions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_id}/pipeline-definitions", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_id}/pipeline-definitions"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pipeline_definitions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pipeline_definitions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pipeline_definitions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipeline Definition
@mcp.tool()
async def create_pipeline_definition(
    project_id: str = Field(..., description="The unique opaque identifier of the project under which the pipeline definition will be created."),
    name: str | None = Field(None, description="A human-readable name for the pipeline definition to distinguish it within the project."),
    description: str | None = Field(None, description="An optional description providing additional context or details about the purpose of this pipeline definition."),
    config_source: _models.CreatePipelineDefinitionBodyConfigSourceV0 | _models.CreatePipelineDefinitionBodyConfigSourceV1 | None = Field(None, description="The configuration source object that specifies where and how the pipeline configuration is sourced, including the provider and repository details."),
    provider: Literal["github_app"] | None = Field(None, description="The version control integration provider for the pipeline definition's configuration source. Currently only 'github_app' is supported."),
    external_id: str | None = Field(None, description="The external identifier for the repository as defined by the version control provider, used to link the pipeline definition to the correct repository."),
) -> dict[str, Any] | ToolResult:
    """Creates a new pipeline definition for a specified project, allowing you to define the configuration source and metadata. Currently only supported for projects using the GitHub App integration provider."""

    # Construct request model with validation
    try:
        _request = _models.CreatePipelineDefinitionRequest(
            path=_models.CreatePipelineDefinitionRequestPath(project_id=project_id),
            body=_models.CreatePipelineDefinitionRequestBody(name=name, description=description, config_source=config_source,
                checkout_source=_models.CreatePipelineDefinitionRequestBodyCheckoutSource(provider=provider,
                    repo=_models.CreatePipelineDefinitionRequestBodyCheckoutSourceRepo(external_id=external_id) if any(v is not None for v in [external_id]) else None) if any(v is not None for v in [provider, external_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_pipeline_definition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_id}/pipeline-definitions", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_id}/pipeline-definitions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_pipeline_definition")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_pipeline_definition", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_pipeline_definition",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipeline Definition
@mcp.tool()
async def get_pipeline_definition(
    project_id: str = Field(..., description="The unique opaque identifier of the project containing the pipeline definition."),
    pipeline_definition_id: str = Field(..., description="The unique opaque identifier of the pipeline definition to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed configuration metadata for a specific pipeline definition within a project. Supported for pipeline definitions using GitHub App, GitHub OAuth, Bitbucket DC, Bitbucket OAuth, or GitLab as the config source provider."""

    # Construct request model with validation
    try:
        _request = _models.GetPipelineDefinitionRequest(
            path=_models.GetPipelineDefinitionRequestPath(project_id=project_id, pipeline_definition_id=pipeline_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pipeline_definition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_id}/pipeline-definitions/{pipeline_definition_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_id}/pipeline-definitions/{pipeline_definition_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pipeline_definition")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pipeline_definition", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pipeline_definition",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipeline Definition
@mcp.tool()
async def update_pipeline_definition(
    project_id: str = Field(..., description="The unique opaque identifier of the project containing the pipeline definition to update."),
    pipeline_definition_id: str = Field(..., description="The unique opaque identifier of the pipeline definition to update."),
    name: str | None = Field(None, description="A human-readable display name for the pipeline definition."),
    description: str | None = Field(None, description="A brief explanation of the pipeline definition's purpose or behavior."),
    file_path: str | None = Field(None, description="The relative path within the repository to the CircleCI YAML configuration file that this pipeline definition should use."),
    provider: str | None = Field(None, description="The version control integration provider for the pipeline definition's config source. Currently only 'github_app' is supported."),
    external_id: str | None = Field(None, description="The repository identifier as defined by the version control provider, used to associate the pipeline definition with a specific external repository."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing pipeline definition for a project, allowing changes to its name, description, config file path, or version control source settings. Currently supported only for pipeline definitions using GitHub App or Bitbucket Data Center as the config source provider."""

    # Construct request model with validation
    try:
        _request = _models.UpdatePipelineDefinitionRequest(
            path=_models.UpdatePipelineDefinitionRequestPath(project_id=project_id, pipeline_definition_id=pipeline_definition_id),
            body=_models.UpdatePipelineDefinitionRequestBody(name=name, description=description,
                config_source=_models.UpdatePipelineDefinitionRequestBodyConfigSource(file_path=file_path) if any(v is not None for v in [file_path]) else None,
                checkout_source=_models.UpdatePipelineDefinitionRequestBodyCheckoutSource(provider=provider,
                    repo=_models.UpdatePipelineDefinitionRequestBodyCheckoutSourceRepo(external_id=external_id) if any(v is not None for v in [external_id]) else None) if any(v is not None for v in [provider, external_id]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_pipeline_definition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_id}/pipeline-definitions/{pipeline_definition_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_id}/pipeline-definitions/{pipeline_definition_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_pipeline_definition")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_pipeline_definition", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_pipeline_definition",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipeline Definition
@mcp.tool()
async def delete_pipeline_definition(
    project_id: str = Field(..., description="The unique opaque identifier of the project containing the pipeline definition to delete."),
    pipeline_definition_id: str = Field(..., description="The unique opaque identifier of the pipeline definition to delete."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a pipeline definition from a project. Currently only supported for pipeline definitions using GitHub App or Bitbucket Data Center as the config source provider."""

    # Construct request model with validation
    try:
        _request = _models.DeletePipelineDefinitionRequest(
            path=_models.DeletePipelineDefinitionRequestPath(project_id=project_id, pipeline_definition_id=pipeline_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_pipeline_definition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_id}/pipeline-definitions/{pipeline_definition_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_id}/pipeline-definitions/{pipeline_definition_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_pipeline_definition")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_pipeline_definition", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_pipeline_definition",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Trigger
@mcp.tool()
async def list_pipeline_definition_triggers(
    project_id: str = Field(..., description="The unique identifier of the project containing the pipeline definition."),
    pipeline_definition_id: str = Field(..., description="The unique identifier of the pipeline definition whose triggers you want to list."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all triggers configured for a specific pipeline definition within a project. Supported only for pipeline definitions using GitHub OAuth, GitHub App, or Bitbucket Data Center as the config source provider."""

    # Construct request model with validation
    try:
        _request = _models.ListPipelineDefinitionTriggersRequest(
            path=_models.ListPipelineDefinitionTriggersRequestPath(project_id=project_id, pipeline_definition_id=pipeline_definition_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pipeline_definition_triggers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_id}/pipeline-definitions/{pipeline_definition_id}/triggers", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_id}/pipeline-definitions/{pipeline_definition_id}/triggers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pipeline_definition_triggers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pipeline_definition_triggers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pipeline_definition_triggers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Trigger
@mcp.tool()
async def create_pipeline_trigger(
    project_id: str = Field(..., description="The unique opaque identifier of the project in which the pipeline definition resides."),
    pipeline_definition_id: str = Field(..., description="The unique opaque identifier of the pipeline definition for which the trigger will be created."),
    provider: str | None = Field(None, description="The version control or integration provider for the trigger's event source. Accepted values are `github_app`, `github_oauth`, and `webhook`."),
    external_id: str | None = Field(None, description="The repository identifier as defined by the version control provider, used to associate the trigger with a specific repository."),
    sender: str | None = Field(None, description="Identifies the entity sending the webhook event; only applicable when the provider is `webhook`."),
    event_preset: Literal["all-pushes", "only-tags", "default-branch-pushes", "only-build-prs", "only-open-prs", "only-labeled-prs", "only-merged-prs", "only-ready-for-review-prs", "only-branch-delete", "only-build-pushes-to-non-draft-prs", "only-merged-or-closed-prs", "pr-comment-equals-run-ci", "non-draft-pr-opened", "pushes-to-merge-queues"] | None = Field(None, description="Specifies which category of events will activate this trigger using a named preset. Only applicable when `event_source.provider` is `github_app`; choose from the supported preset values to control which push, PR, or branch events fire the trigger."),
    checkout_ref: str | None = Field(None, description="The Git ref used to check out source code for pipeline runs created by this trigger. Required when the provider is `webhook`; for `github_app`, only provide this if the event source repository differs from the pipeline definition's checkout source repository."),
    config_ref: str | None = Field(None, description="The Git ref used to fetch the pipeline configuration for runs created by this trigger. Required when the provider is `webhook`; for `github_app`, only provide this if the event source repository differs from the pipeline definition's config source repository."),
    event_name: str | None = Field(None, description="The name of the event that activates this trigger. Should only be set when the provider is `webhook`."),
    disabled: bool | None = Field(None, description="When set to `true`, the trigger is created in a disabled state and will not fire until explicitly enabled. Not supported for pipeline definitions using `github_oauth` as the config source provider."),
) -> dict[str, Any] | ToolResult:
    """Creates a trigger for a specified pipeline definition, enabling automated pipeline runs in response to events. Currently supported only for pipeline definitions using GitHub OAuth or GitHub App as the config source provider."""

    # Construct request model with validation
    try:
        _request = _models.CreateTriggerRequest(
            path=_models.CreateTriggerRequestPath(project_id=project_id, pipeline_definition_id=pipeline_definition_id),
            body=_models.CreateTriggerRequestBody(event_preset=event_preset, checkout_ref=checkout_ref, config_ref=config_ref, event_name=event_name, disabled=disabled,
                event_source=_models.CreateTriggerRequestBodyEventSource(provider=provider,
                    repo=_models.CreateTriggerRequestBodyEventSourceRepo(external_id=external_id) if any(v is not None for v in [external_id]) else None,
                    webhook=_models.CreateTriggerRequestBodyEventSourceWebhook(sender=sender) if any(v is not None for v in [sender]) else None) if any(v is not None for v in [provider, external_id, sender]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_pipeline_trigger: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_id}/pipeline-definitions/{pipeline_definition_id}/triggers", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_id}/pipeline-definitions/{pipeline_definition_id}/triggers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_pipeline_trigger")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_pipeline_trigger", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_pipeline_trigger",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Trigger
@mcp.tool()
async def get_trigger(
    project_id: str = Field(..., description="The unique opaque identifier of the project that owns the trigger."),
    trigger_id: str = Field(..., description="The unique opaque identifier of the trigger to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed configuration and metadata for a specific project trigger. Currently supported for triggers with GitHub OAuth, GitHub App, Bitbucket Data Center, or webhook event sources."""

    # Construct request model with validation
    try:
        _request = _models.GetTriggerRequest(
            path=_models.GetTriggerRequestPath(project_id=project_id, trigger_id=trigger_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_trigger: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_id}/triggers/{trigger_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_id}/triggers/{trigger_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_trigger")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_trigger", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_trigger",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Trigger
@mcp.tool()
async def update_trigger(
    project_id: str = Field(..., description="The unique opaque identifier of the project that owns the trigger."),
    trigger_id: str = Field(..., description="The unique opaque identifier of the trigger to update."),
    event_preset: Literal["all-pushes", "only-tags", "default-branch-pushes", "only-build-prs", "only-open-prs", "only-labeled-prs", "only-merged-prs", "only-ready-for-review-prs", "only-branch-delete", "only-build-pushes-to-non-draft-prs", "only-merged-or-closed-prs", "pr-comment-equals-run-ci", "non-draft-pr-opened", "pushes-to-merge-queues"] | None = Field(None, description="A predefined event filtering preset that determines which GitHub events activate this trigger. Only applicable when the trigger's provider is `github_app`."),
    checkout_ref: str | None = Field(None, description="The Git ref (branch, tag, or commit SHA) used to check out source code when pipeline runs are created from this trigger."),
    config_ref: str | None = Field(None, description="The Git ref used to fetch the pipeline configuration file when pipeline runs are created from this trigger."),
    event_name: str | None = Field(None, description="The name of the event that activates this trigger. Only settable for triggers where the provider is `webhook`."),
    disabled: bool | None = Field(None, description="Whether the trigger is disabled and should not create pipeline runs when events occur. Only settable for triggers where the provider is `github_oauth`, `github_app`, or `webhook`."),
    sender: str | None = Field(None, description="The identity of the entity sending the webhook payload. Only settable for triggers where the provider is `webhook`."),
) -> dict[str, Any] | ToolResult:
    """Update configuration for an existing pipeline trigger on a project. Currently supported for triggers with a provider of `github_oauth`, `github_app`, `bitbucket_dc`, or `webhook`."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTriggerRequest(
            path=_models.UpdateTriggerRequestPath(project_id=project_id, trigger_id=trigger_id),
            body=_models.UpdateTriggerRequestBody(event_preset=event_preset, checkout_ref=checkout_ref, config_ref=config_ref, event_name=event_name, disabled=disabled,
                event_source=_models.UpdateTriggerRequestBodyEventSource(webhook=_models.UpdateTriggerRequestBodyEventSourceWebhook(sender=sender) if any(v is not None for v in [sender]) else None) if any(v is not None for v in [sender]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_trigger: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_id}/triggers/{trigger_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_id}/triggers/{trigger_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_trigger")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_trigger", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_trigger",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Trigger
@mcp.tool()
async def delete_trigger(
    project_id: str = Field(..., description="The unique opaque identifier of the project from which the trigger will be deleted."),
    trigger_id: str = Field(..., description="The unique opaque identifier of the trigger to be deleted."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a trigger from the specified project. Supported only for triggers with an event source provider of GitHub OAuth, GitHub App, Bitbucket Data Center, or webhook."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTriggerRequest(
            path=_models.DeleteTriggerRequestPath(project_id=project_id, trigger_id=trigger_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_trigger: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_id}/triggers/{trigger_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_id}/triggers/{trigger_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_trigger")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_trigger", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_trigger",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Rollback
@mcp.tool()
async def rollback_project(
    project_id: str = Field(..., description="The unique opaque identifier of the project in which the rollback will be performed."),
    component_name: str = Field(..., description="The name of the component within the project to be rolled back."),
    current_version: str = Field(..., description="The version of the component currently deployed, which will be replaced by the rollback."),
    environment_name: str = Field(..., description="The name of the environment in which the rollback will be executed (e.g., production, staging)."),
    target_version: str = Field(..., description="The version to roll back to, which should be a previously stable and deployed version of the component."),
    namespace: str | None = Field(None, description="The Kubernetes or deployment namespace where the component resides. Defaults to the project's default namespace if not specified."),
    parameters: dict[str, Any] | None = Field(None, description="A key-value map of additional parameters to pass to the rollback pipeline, allowing customization of pipeline behavior beyond standard inputs."),
    reason: str | None = Field(None, description="A human-readable explanation for why the rollback is being performed, useful for audit trails and incident tracking."),
) -> dict[str, Any] | ToolResult:
    """Rolls back a specific component in a project to a target version by triggering a rollback pipeline. Use this to recover from a bad deployment by reverting a component from its current version to a previously stable version."""

    # Construct request model with validation
    try:
        _request = _models.RollbackProjectRequest(
            path=_models.RollbackProjectRequestPath(project_id=project_id),
            body=_models.RollbackProjectRequestBody(component_name=component_name, current_version=current_version, environment_name=environment_name, namespace=namespace, parameters=parameters, reason=reason, target_version=target_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rollback_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{project_id}/rollback", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{project_id}/rollback"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("rollback_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("rollback_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="rollback_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deploy
@mcp.tool()
async def list_environments(
    org_id: str = Field(..., alias="org-id", description="The unique identifier of the organization whose environments you want to list, provided as a UUID."),
    page_size: int = Field(..., alias="page-size", description="The maximum number of environments to return per page. Use this alongside pagination controls to iterate through large result sets."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of deployment environments belonging to a specified organization. Use this to browse available environments for deployment targeting or configuration management."""

    # Construct request model with validation
    try:
        _request = _models.ListEnvironmentsRequest(
            query=_models.ListEnvironmentsRequestQuery(org_id=org_id, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_environments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/deploy/environments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deploy
@mcp.tool()
async def get_environment(environment_id: str = Field(..., description="The unique UUID identifying the deployment environment to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific deployment environment by its unique identifier. Use this to inspect environment configuration, status, or metadata for a known environment."""

    # Construct request model with validation
    try:
        _request = _models.GetEnvironmentRequest(
            path=_models.GetEnvironmentRequestPath(environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/deploy/environments/{environment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/deploy/environments/{environment_id}"
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

# Tags: Deploy
@mcp.tool()
async def list_components(
    org_id: str = Field(..., alias="org-id", description="The unique identifier of the organization whose components will be listed."),
    page_size: int = Field(..., alias="page-size", description="The maximum number of components to return in a single page of results. Use in combination with pagination tokens to iterate through all components."),
    project_id: str | None = Field(None, alias="project-id", description="The unique identifier of a project used to filter components to only those belonging to that project."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of deployed components belonging to a specified organization. Optionally filter results by project to narrow the scope of returned components."""

    # Construct request model with validation
    try:
        _request = _models.ListComponentsRequest(
            query=_models.ListComponentsRequestQuery(org_id=org_id, project_id=project_id, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_components: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/deploy/components"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_components")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_components", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_components",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deploy
@mcp.tool()
async def get_component(component_id: str = Field(..., description="The unique opaque identifier of the component to retrieve, as returned when the component was created or listed.")) -> dict[str, Any] | ToolResult:
    """Retrieves the full details of a deployed component by its unique identifier. Use this to inspect configuration, status, or metadata for a specific component."""

    # Construct request model with validation
    try:
        _request = _models.GetComponentRequest(
            path=_models.GetComponentRequestPath(component_id=component_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_component: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/deploy/components/{component_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/deploy/components/{component_id}"
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

# Tags: Deploy
@mcp.tool()
async def list_component_versions(
    component_id: str = Field(..., description="The unique identifier of the component whose versions you want to retrieve."),
    environment_id: str | None = Field(None, alias="environment-id", description="The unique identifier of an environment to filter component versions by, returning only versions relevant to that environment. Must be a valid UUID."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all available versions for a specified component. Optionally filter results by environment to see versions relevant to a particular deployment context."""

    # Construct request model with validation
    try:
        _request = _models.ListComponentVersionsRequest(
            path=_models.ListComponentVersionsRequestPath(component_id=component_id),
            query=_models.ListComponentVersionsRequestQuery(environment_id=environment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_component_versions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/deploy/components/{component_id}/versions", _request.path.model_dump(by_alias=True)) if _request.path else "/deploy/components/{component_id}/versions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_component_versions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_component_versions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_component_versions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: OTel
@mcp.tool()
async def list_otel_exporters(org_id: str = Field(..., alias="org-id", description="The unique identifier of the organization whose OTLP exporter configurations should be retrieved, provided as a UUID.")) -> dict[str, Any] | ToolResult:
    """Retrieves all OpenTelemetry (OTLP) exporter configurations associated with the specified organization. This is an experimental feature and may be subject to change."""

    # Construct request model with validation
    try:
        _request = _models.ListOtelExportersRequest(
            query=_models.ListOtelExportersRequestQuery(org_id=org_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_otel_exporters: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/otel/exporters"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_otel_exporters")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_otel_exporters", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_otel_exporters",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: OTel
@mcp.tool()
async def create_otlp_exporter(
    org_id: str = Field(..., description="The unique identifier of the organization for which the OTLP exporter will be created."),
    endpoint: str = Field(..., description="The destination OTLP collector endpoint, specified as hostname and port only — omit any scheme prefix such as https:// or grpc://."),
    protocol: Literal["grpc", "http"] = Field(..., description="The transport protocol used when exporting telemetry data; choose grpc for gRPC transport or http for HTTP/protobuf transport."),
    insecure: bool | None = Field(None, description="When set to true, the exporter connects to the endpoint without TLS encryption; defaults to false for secure connections."),
    headers: dict[str, str] | None = Field(None, description="A key-value map of additional HTTP or gRPC headers to include with every export request, useful for authentication tokens or routing metadata."),
) -> dict[str, Any] | ToolResult:
    """Creates a new OTLP exporter configuration for a specified organization, defining how telemetry spans are exported to an external observability backend. This is an experimental feature supporting both gRPC and HTTP transport protocols."""

    # Construct request model with validation
    try:
        _request = _models.CreateOtelExporterRequest(
            body=_models.CreateOtelExporterRequestBody(org_id=org_id, endpoint=endpoint, protocol=protocol, insecure=insecure, headers=headers)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_otlp_exporter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/otel/exporters"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_otlp_exporter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_otlp_exporter", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_otlp_exporter",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: OTel
@mcp.tool()
async def delete_otlp_exporter(otel_exporter_id: str = Field(..., description="The unique identifier of the OTLP exporter configuration to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an OTLP exporter configuration by its unique identifier. This is an experimental feature and the behavior may change in future releases."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOtelExporterRequest(
            path=_models.DeleteOtelExporterRequestPath(otel_exporter_id=otel_exporter_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_otlp_exporter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/otel/exporters/{otel_exporter_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/otel/exporters/{otel_exporter_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_otlp_exporter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_otlp_exporter", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_otlp_exporter",
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
        print("  python circle_ci_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="CircleCI MCP Server")

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
    logger.info("Starting CircleCI MCP Server")
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

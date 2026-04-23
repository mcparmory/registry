#!/usr/bin/env python3
"""
Google Analytics MCP Server

API Info:
- API License: Creative Commons Attribution 3.0 (http://creativecommons.org/licenses/by/3.0/)
- Contact: Google (https://google.com)
- Terms of Service: https://developers.google.com/terms/

Generated: 2026-04-23 21:20:34 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://analyticsdata.googleapis.com")
SERVER_NAME = "Google Analytics"
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
    'OAuth2',
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

mcp = FastMCP("Google Analytics", middleware=[_JsonCoercionMiddleware()])

# Tags: properties
@mcp.tool()
async def run_pivot_reports_batch(
    property_: str = Field(..., alias="property", description="The Google Analytics property identifier whose events are tracked. Specified in the URL path. This property applies to all reports in the batch, though individual requests may omit or match this value."),
    requests: list[_models.RunPivotReportRequest] | None = Field(None, description="Array of individual pivot report requests to execute. Each request generates a separate pivot report response. Maximum of 5 requests allowed per batch."),
) -> dict[str, Any] | ToolResult:
    """Execute multiple pivot reports in a single batch request for a Google Analytics property. All reports must belong to the same property, with support for up to 5 requests per batch."""

    # Construct request model with validation
    try:
        _request = _models.BatchRunPivotReportsRequest(
            path=_models.BatchRunPivotReportsRequestPath(property_=property_),
            body=_models.BatchRunPivotReportsRequestBody(requests=requests)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for run_pivot_reports_batch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1beta/{property}:batchRunPivotReports", _request.path.model_dump(by_alias=True)) if _request.path else "/v1beta/{property}:batchRunPivotReports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("run_pivot_reports_batch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("run_pivot_reports_batch", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="run_pivot_reports_batch",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def run_reports_batch(
    property_: str = Field(..., alias="property", description="The Google Analytics property identifier whose events are tracked. Specified in the URL path. The property must be consistent across all batch requests."),
    requests: list[_models.RunReportRequest] | None = Field(None, description="Array of individual report requests to execute. Each request generates a separate report response. Order is preserved in the response. Maximum of 5 requests allowed per batch."),
) -> dict[str, Any] | ToolResult:
    """Execute multiple analytics reports in a single batch request for a Google Analytics property. All reports must belong to the same property, with support for up to 5 requests per batch."""

    # Construct request model with validation
    try:
        _request = _models.BatchRunReportsRequest(
            path=_models.BatchRunReportsRequestPath(property_=property_),
            body=_models.BatchRunReportsRequestBody(requests=requests)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for run_reports_batch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1beta/{property}:batchRunReports", _request.path.model_dump(by_alias=True)) if _request.path else "/v1beta/{property}:batchRunReports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("run_reports_batch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("run_reports_batch", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="run_reports_batch",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def validate_report_compatibility(
    property_: str = Field(..., alias="property", description="The Google Analytics property identifier (format: properties/PROPERTY_ID) whose events are tracked. Must match the property used in your runReport request."),
    compatibility_filter: Literal["COMPATIBILITY_UNSPECIFIED", "COMPATIBLE", "INCOMPATIBLE"] | None = Field(None, alias="compatibilityFilter", description="Filters the response to return only dimensions and metrics matching this compatibility status."),
    dimension_filter_or_group_expressions: list[_models.FilterExpression] | None = Field(None, alias="dimensionFilterOrGroupExpressions", description="A list of dimension filter expressions combined with OR logic. All expressions in this list are evaluated and combined."),
    metric_filter_and_group_expressions: list[_models.FilterExpression] | None = Field(None, alias="metricFilterAndGroupExpressions", description="A list of metric filter expressions combined with AND logic. All expressions in this list must be satisfied."),
    metric_filter_or_group_expressions: list[_models.FilterExpression] | None = Field(None, alias="metricFilterOrGroupExpressions", description="A list of metric filter expressions combined with OR logic. All expressions in this list are evaluated and combined."),
    from_value: dict[str, Any] | None = Field(None, alias="fromValue", description="The lower bound (inclusive) for a between filter on metrics. Accepts numeric or date values."),
    dimension_filter_filter_between_filter_to_value: dict[str, Any] | None = Field(None, alias="dimensionFilterFilterBetweenFilterToValue", description="The upper bound (inclusive) for a between filter on dimensions. Accepts numeric or date values."),
    metric_filter_filter_between_filter_to_value: dict[str, Any] | None = Field(None, alias="metricFilterFilterBetweenFilterToValue", description="The upper bound (inclusive) for a between filter on metrics. Accepts numeric or date values."),
    dimension_filter_filter_empty_filter: dict[str, Any] | None = Field(None, alias="dimensionFilterFilterEmptyFilter", description="Filters dimension values that are empty, such as \"(not set)\" or empty strings."),
    metric_filter_filter_empty_filter: dict[str, Any] | None = Field(None, alias="metricFilterFilterEmptyFilter", description="Filters metric values that are empty, such as \"(not set)\" or empty strings."),
    field_name: str | None = Field(None, alias="fieldName", description="The dimension or metric name to filter on. In pivot reports, this field must also be specified in the dimensions or metrics array."),
    dimension_filter_filter_string_filter_case_sensitive: bool | None = Field(None, alias="dimensionFilterFilterStringFilterCaseSensitive", description="If true, string matching for dimension filters is case-sensitive."),
    metric_filter_filter_in_list_filter_case_sensitive: bool | None = Field(None, alias="metricFilterFilterInListFilterCaseSensitive", description="If true, string matching for metric in-list filters is case-sensitive."),
    metric_filter_filter_string_filter_case_sensitive: bool | None = Field(None, alias="metricFilterFilterStringFilterCaseSensitive", description="If true, string matching for metric filters is case-sensitive."),
    dimension_filter_filter_in_list_filter_values: list[str] | None = Field(None, alias="dimensionFilterFilterInListFilterValues", description="A non-empty list of string values to match against dimension values using the in-list filter."),
    metric_filter_filter_in_list_filter_values: list[str] | None = Field(None, alias="metricFilterFilterInListFilterValues", description="A non-empty list of string values to match against metric values using the in-list filter."),
    dimension_filter_filter_numeric_filter_operation: Literal["OPERATION_UNSPECIFIED", "EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL"] | None = Field(None, alias="dimensionFilterFilterNumericFilterOperation", description="The comparison operation to apply for numeric dimension filtering."),
    metric_filter_filter_numeric_filter_operation: Literal["OPERATION_UNSPECIFIED", "EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL"] | None = Field(None, alias="metricFilterFilterNumericFilterOperation", description="The comparison operation to apply for numeric metric filtering."),
    dimension_filter_filter_numeric_filter_value: dict[str, Any] | None = Field(None, alias="dimensionFilterFilterNumericFilterValue", description="The numeric or date value to compare against for dimension filtering."),
    dimension_filter_filter_string_filter_value: str | None = Field(None, alias="dimensionFilterFilterStringFilterValue", description="The string value to match against dimension values."),
    metric_filter_filter_numeric_filter_value: dict[str, Any] | None = Field(None, alias="metricFilterFilterNumericFilterValue", description="The numeric or date value to compare against for metric filtering."),
    metric_filter_filter_string_filter_value: str | None = Field(None, alias="metricFilterFilterStringFilterValue", description="The string value to match against metric values."),
    dimension_filter_filter_string_filter_match_type: Literal["MATCH_TYPE_UNSPECIFIED", "EXACT", "BEGINS_WITH", "ENDS_WITH", "CONTAINS", "FULL_REGEXP", "PARTIAL_REGEXP"] | None = Field(None, alias="dimensionFilterFilterStringFilterMatchType", description="The string matching type for dimension filters (e.g., exact match, contains, regex)."),
    metric_filter_filter_string_filter_match_type: Literal["MATCH_TYPE_UNSPECIFIED", "EXACT", "BEGINS_WITH", "ENDS_WITH", "CONTAINS", "FULL_REGEXP", "PARTIAL_REGEXP"] | None = Field(None, alias="metricFilterFilterStringFilterMatchType", description="The string matching type for metric filters (e.g., exact match, contains, regex)."),
    dimension_filter_not_expression: _models.FilterExpression | None = Field(None, alias="dimensionFilterNotExpression", description="A NOT expression that inverts the logic of the dimension filter."),
    metric_filter_not_expression: _models.FilterExpression | None = Field(None, alias="metricFilterNotExpression", description="A NOT expression that inverts the logic of the metric filter."),
    dimensions: list[_models.Dimension] | None = Field(None, description="The list of dimension names to validate for compatibility. Must match the dimensions used in your runReport request."),
    metrics: list[_models.Metric] | None = Field(None, description="The list of metric names to validate for compatibility. Must match the metrics used in your runReport request."),
) -> dict[str, Any] | ToolResult:
    """Validates whether a set of dimensions and metrics can be used together in a Core report, and returns compatible or incompatible dimensions and metrics. Use this to identify which dimensions and metrics need to be removed to create a valid report."""

    # Construct request model with validation
    try:
        _request = _models.CheckCompatibilityRequest(
            path=_models.CheckCompatibilityRequestPath(property_=property_),
            body=_models.CheckCompatibilityRequestBody(compatibility_filter=compatibility_filter, dimensions=dimensions, metrics=metrics,
                dimension_filter=_models.CheckCompatibilityRequestBodyDimensionFilter(not_expression=dimension_filter_not_expression,
                    or_group=_models.CheckCompatibilityRequestBodyDimensionFilterOrGroup(expressions=dimension_filter_or_group_expressions) if any(v is not None for v in [dimension_filter_or_group_expressions]) else None,
                    filter_=_models.CheckCompatibilityRequestBodyDimensionFilterFilter(empty_filter=dimension_filter_filter_empty_filter,
                        between_filter=_models.CheckCompatibilityRequestBodyDimensionFilterFilterBetweenFilter(to_value=dimension_filter_filter_between_filter_to_value) if any(v is not None for v in [dimension_filter_filter_between_filter_to_value]) else None,
                        string_filter=_models.CheckCompatibilityRequestBodyDimensionFilterFilterStringFilter(case_sensitive=dimension_filter_filter_string_filter_case_sensitive, value=dimension_filter_filter_string_filter_value, match_type=dimension_filter_filter_string_filter_match_type) if any(v is not None for v in [dimension_filter_filter_string_filter_case_sensitive, dimension_filter_filter_string_filter_value, dimension_filter_filter_string_filter_match_type]) else None,
                        in_list_filter=_models.CheckCompatibilityRequestBodyDimensionFilterFilterInListFilter(values=dimension_filter_filter_in_list_filter_values) if any(v is not None for v in [dimension_filter_filter_in_list_filter_values]) else None,
                        numeric_filter=_models.CheckCompatibilityRequestBodyDimensionFilterFilterNumericFilter(operation=dimension_filter_filter_numeric_filter_operation, value=dimension_filter_filter_numeric_filter_value) if any(v is not None for v in [dimension_filter_filter_numeric_filter_operation, dimension_filter_filter_numeric_filter_value]) else None) if any(v is not None for v in [dimension_filter_filter_between_filter_to_value, dimension_filter_filter_empty_filter, dimension_filter_filter_string_filter_case_sensitive, dimension_filter_filter_in_list_filter_values, dimension_filter_filter_numeric_filter_operation, dimension_filter_filter_numeric_filter_value, dimension_filter_filter_string_filter_value, dimension_filter_filter_string_filter_match_type]) else None) if any(v is not None for v in [dimension_filter_or_group_expressions, dimension_filter_filter_between_filter_to_value, dimension_filter_filter_empty_filter, dimension_filter_filter_string_filter_case_sensitive, dimension_filter_filter_in_list_filter_values, dimension_filter_filter_numeric_filter_operation, dimension_filter_filter_numeric_filter_value, dimension_filter_filter_string_filter_value, dimension_filter_filter_string_filter_match_type, dimension_filter_not_expression]) else None,
                metric_filter=_models.CheckCompatibilityRequestBodyMetricFilter(not_expression=metric_filter_not_expression,
                    and_group=_models.CheckCompatibilityRequestBodyMetricFilterAndGroup(expressions=metric_filter_and_group_expressions) if any(v is not None for v in [metric_filter_and_group_expressions]) else None,
                    or_group=_models.CheckCompatibilityRequestBodyMetricFilterOrGroup(expressions=metric_filter_or_group_expressions) if any(v is not None for v in [metric_filter_or_group_expressions]) else None,
                    filter_=_models.CheckCompatibilityRequestBodyMetricFilterFilter(empty_filter=metric_filter_filter_empty_filter, field_name=field_name,
                        between_filter=_models.CheckCompatibilityRequestBodyMetricFilterFilterBetweenFilter(from_value=from_value, to_value=metric_filter_filter_between_filter_to_value) if any(v is not None for v in [from_value, metric_filter_filter_between_filter_to_value]) else None,
                        in_list_filter=_models.CheckCompatibilityRequestBodyMetricFilterFilterInListFilter(case_sensitive=metric_filter_filter_in_list_filter_case_sensitive, values=metric_filter_filter_in_list_filter_values) if any(v is not None for v in [metric_filter_filter_in_list_filter_case_sensitive, metric_filter_filter_in_list_filter_values]) else None,
                        string_filter=_models.CheckCompatibilityRequestBodyMetricFilterFilterStringFilter(case_sensitive=metric_filter_filter_string_filter_case_sensitive, value=metric_filter_filter_string_filter_value, match_type=metric_filter_filter_string_filter_match_type) if any(v is not None for v in [metric_filter_filter_string_filter_case_sensitive, metric_filter_filter_string_filter_value, metric_filter_filter_string_filter_match_type]) else None,
                        numeric_filter=_models.CheckCompatibilityRequestBodyMetricFilterFilterNumericFilter(operation=metric_filter_filter_numeric_filter_operation, value=metric_filter_filter_numeric_filter_value) if any(v is not None for v in [metric_filter_filter_numeric_filter_operation, metric_filter_filter_numeric_filter_value]) else None) if any(v is not None for v in [from_value, metric_filter_filter_between_filter_to_value, metric_filter_filter_empty_filter, field_name, metric_filter_filter_in_list_filter_case_sensitive, metric_filter_filter_string_filter_case_sensitive, metric_filter_filter_in_list_filter_values, metric_filter_filter_numeric_filter_operation, metric_filter_filter_numeric_filter_value, metric_filter_filter_string_filter_value, metric_filter_filter_string_filter_match_type]) else None) if any(v is not None for v in [metric_filter_and_group_expressions, metric_filter_or_group_expressions, from_value, metric_filter_filter_between_filter_to_value, metric_filter_filter_empty_filter, field_name, metric_filter_filter_in_list_filter_case_sensitive, metric_filter_filter_string_filter_case_sensitive, metric_filter_filter_in_list_filter_values, metric_filter_filter_numeric_filter_operation, metric_filter_filter_numeric_filter_value, metric_filter_filter_string_filter_value, metric_filter_filter_string_filter_match_type, metric_filter_not_expression]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for validate_report_compatibility: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1beta/{property}:checkCompatibility", _request.path.model_dump(by_alias=True)) if _request.path else "/v1beta/{property}:checkCompatibility"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("validate_report_compatibility")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("validate_report_compatibility", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="validate_report_compatibility",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def get_audience_export(name: str = Field(..., description="The resource identifier for the audience export in the format properties/{property}/audienceExports/{audience_export}, where property is your Google Analytics property ID and audience_export is the unique export identifier.")) -> dict[str, Any] | ToolResult:
    """Retrieves configuration metadata for a specific audience export, including its status and settings. Use this to inspect an audience export after creation or to monitor its progress."""

    # Construct request model with validation
    try:
        _request = _models.AudienceExportsGetRequest(
            path=_models.AudienceExportsGetRequestPath(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_audience_export: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1beta/{name}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1beta/{name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_audience_export")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_audience_export", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_audience_export",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def generate_pivot_report(
    property_: str = Field(..., alias="property", description="The Google Analytics property identifier whose events are tracked. Found in your Google Analytics account settings."),
    accumulate: bool | None = Field(None, description="If true, accumulates results from the first touch day through the end date. Not supported for standard reports."),
    cohorts: list[_models.Cohort] | None = Field(None, description="Defines selection criteria to group users into cohorts for cohort analysis. Most cohort reports use a single cohort; multiple cohorts are distinguished by their assigned names."),
    end_offset: str | None = Field(None, alias="endOffset", description="The end offset for the extended reporting date range in a cohort report, specified as a positive integer. The actual end date is calculated by multiplying this offset by the granularity unit (days, weeks, or months)."),
    granularity: Literal["GRANULARITY_UNSPECIFIED", "DAILY", "WEEKLY", "MONTHLY"] | None = Field(None, description="The time unit granularity used to interpret start and end offsets in cohort reports (daily, weekly, or monthly)."),
    start_offset: str | None = Field(None, alias="startOffset", description="The start offset for the extended reporting date range in a cohort report, specified as a positive integer. Commonly set to 0 to include data from cohort acquisition forward. The actual start date is calculated by multiplying this offset by the granularity unit."),
    comparisons: list[_models.Comparison] | None = Field(None, description="Configuration for comparison columns in the report. Requires both this field and a comparisons dimension to display comparison data."),
    currency_code: str | None = Field(None, alias="currencyCode", description="ISO 4217 currency code for monetary values in the report. If unspecified, uses the property's default currency."),
    date_ranges: list[_models.DateRange] | None = Field(None, alias="dateRanges", description="Date ranges for retrieving event data. Multiple ranges can be specified to compare data across periods. Include the special 'dateRange' dimension in pivots to compare between ranges. Omit for cohort requests."),
    dimension_filter_and_group_expressions: list[_models.FilterExpression] | None = Field(None, alias="dimensionFilterAndGroupExpressions", description="Dimension filter expressions combined with AND logic. All expressions must be satisfied for a row to be included."),
    dimension_filter_or_group_expressions: list[_models.FilterExpression] | None = Field(None, alias="dimensionFilterOrGroupExpressions", description="Dimension filter expressions combined with OR logic. At least one expression must be satisfied for a row to be included."),
    metric_filter_and_group_expressions: list[_models.FilterExpression] | None = Field(None, alias="metricFilterAndGroupExpressions", description="Metric filter expressions combined with AND logic. All expressions must be satisfied for a row to be included."),
    metric_filter_or_group_expressions: list[_models.FilterExpression] | None = Field(None, alias="metricFilterOrGroupExpressions", description="Metric filter expressions combined with OR logic. At least one expression must be satisfied for a row to be included."),
    dimension_filter_filter_between_filter_from_value: dict[str, Any] | None = Field(None, alias="dimensionFilterFilterBetweenFilterFromValue", description="The lower bound (inclusive) for a between filter on dimensions. Specifies where the range begins."),
    metric_filter_filter_between_filter_from_value: dict[str, Any] | None = Field(None, alias="metricFilterFilterBetweenFilterFromValue", description="The lower bound (inclusive) for a between filter on metrics. Specifies where the range begins."),
    dimension_filter_filter_between_filter_to_value: dict[str, Any] | None = Field(None, alias="dimensionFilterFilterBetweenFilterToValue", description="The upper bound (inclusive) for a between filter on dimensions. Specifies where the range ends."),
    metric_filter_filter_between_filter_to_value: dict[str, Any] | None = Field(None, alias="metricFilterFilterBetweenFilterToValue", description="The upper bound (inclusive) for a between filter on metrics. Specifies where the range ends."),
    dimension_filter_filter_empty_filter: dict[str, Any] | None = Field(None, alias="dimensionFilterFilterEmptyFilter", description="Filters dimension values that are empty, such as '(not set)' or blank strings."),
    metric_filter_filter_empty_filter: dict[str, Any] | None = Field(None, alias="metricFilterFilterEmptyFilter", description="Filters metric values that are empty, such as '(not set)' or blank strings."),
    dimension_filter_filter_field_name: str | None = Field(None, alias="dimensionFilterFilterFieldName", description="The dimension or metric name to filter. In pivot reports, this field must also be explicitly included in the dimensions or metrics array."),
    metric_filter_filter_field_name: str | None = Field(None, alias="metricFilterFilterFieldName", description="The dimension or metric name to filter. In pivot reports, this field must also be explicitly included in the dimensions or metrics array."),
    dimension_filter_filter_in_list_filter_case_sensitive: bool | None = Field(None, alias="dimensionFilterFilterInListFilterCaseSensitive", description="If true, dimension filter string matching is case-sensitive. If false, matching is case-insensitive."),
    dimension_filter_filter_string_filter_case_sensitive: bool | None = Field(None, alias="dimensionFilterFilterStringFilterCaseSensitive", description="If true, dimension filter string matching is case-sensitive. If false, matching is case-insensitive."),
    metric_filter_filter_in_list_filter_case_sensitive: bool | None = Field(None, alias="metricFilterFilterInListFilterCaseSensitive", description="If true, metric filter string matching is case-sensitive. If false, matching is case-insensitive."),
    metric_filter_filter_string_filter_case_sensitive: bool | None = Field(None, alias="metricFilterFilterStringFilterCaseSensitive", description="If true, metric filter string matching is case-sensitive. If false, matching is case-insensitive."),
    dimension_filter_filter_in_list_filter_values: list[str] | None = Field(None, alias="dimensionFilterFilterInListFilterValues", description="List of string values for dimension in-list filtering. At least one value must be provided."),
    metric_filter_filter_in_list_filter_values: list[str] | None = Field(None, alias="metricFilterFilterInListFilterValues", description="List of string values for metric in-list filtering. At least one value must be provided."),
    dimension_filter_filter_numeric_filter_operation: Literal["OPERATION_UNSPECIFIED", "EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL"] | None = Field(None, alias="dimensionFilterFilterNumericFilterOperation", description="The comparison operation for numeric dimension filtering (equal, less than, greater than, etc.)."),
    metric_filter_filter_numeric_filter_operation: Literal["OPERATION_UNSPECIFIED", "EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL"] | None = Field(None, alias="metricFilterFilterNumericFilterOperation", description="The comparison operation for numeric metric filtering (equal, less than, greater than, etc.)."),
    dimension_filter_filter_numeric_filter_value: dict[str, Any] | None = Field(None, alias="dimensionFilterFilterNumericFilterValue", description="The numeric or date value to compare against in dimension filters."),
    dimension_filter_filter_string_filter_value: str | None = Field(None, alias="dimensionFilterFilterStringFilterValue", description="The string value to match in dimension filters."),
    metric_filter_filter_numeric_filter_value: dict[str, Any] | None = Field(None, alias="metricFilterFilterNumericFilterValue", description="The numeric or date value to compare against in metric filters."),
    metric_filter_filter_string_filter_value: str | None = Field(None, alias="metricFilterFilterStringFilterValue", description="The string value to match in metric filters."),
    dimension_filter_filter_string_filter_match_type: Literal["MATCH_TYPE_UNSPECIFIED", "EXACT", "BEGINS_WITH", "ENDS_WITH", "CONTAINS", "FULL_REGEXP", "PARTIAL_REGEXP"] | None = Field(None, alias="dimensionFilterFilterStringFilterMatchType", description="The string matching strategy for dimension filters (exact match, begins with, contains, regex, etc.)."),
    metric_filter_filter_string_filter_match_type: Literal["MATCH_TYPE_UNSPECIFIED", "EXACT", "BEGINS_WITH", "ENDS_WITH", "CONTAINS", "FULL_REGEXP", "PARTIAL_REGEXP"] | None = Field(None, alias="metricFilterFilterStringFilterMatchType", description="The string matching strategy for metric filters (exact match, begins with, contains, regex, etc.)."),
    dimension_filter_not_expression: _models.FilterExpression | None = Field(None, alias="dimensionFilterNotExpression", description="Negates the dimension filter expression. The filter matches rows where the expression is false."),
    metric_filter_not_expression: _models.FilterExpression | None = Field(None, alias="metricFilterNotExpression", description="Negates the metric filter expression. The filter matches rows where the expression is false."),
    dimensions: list[_models.Dimension] | None = Field(None, description="The dimensions to include in the report. All specified dimensions must be used in at least one pivot, dimension filter, or order by clause."),
    keep_empty_rows: bool | None = Field(None, alias="keepEmptyRows", description="If false, rows with all metrics equal to zero are excluded from results. If true, zero-value rows are included unless removed by filters. Only data actually recorded by the property appears in the report."),
    metrics: list[_models.Metric] | None = Field(None, description="The metrics to include in the report. At least one metric is required. All specified metrics must be used in a metric filter, order by clause, or metric expression."),
    pivots: list[_models.Pivot] | None = Field(None, description="Defines how dimensions are organized visually as rows or columns in the pivot report. All dimension names in pivots must be declared in the dimensions array. Each dimension can appear in only one pivot."),
    return_property_quota: bool | None = Field(None, alias="returnPropertyQuota", description="If true, returns the current quota status for this Google Analytics property, including usage and limits."),
) -> dict[str, Any] | ToolResult:
    """Generate a customized pivot report of Google Analytics event data with advanced dimensional analysis. Pivot reports allow dimensions to be organized in rows or columns, with support for multiple pivots to further segment and analyze your data."""

    _end_offset = _parse_int(end_offset)
    _start_offset = _parse_int(start_offset)

    # Construct request model with validation
    try:
        _request = _models.RunPivotReportRequest(
            path=_models.RunPivotReportRequestPath(property_=property_),
            body=_models.RunPivotReportRequestBody(comparisons=comparisons, currency_code=currency_code, date_ranges=date_ranges, dimensions=dimensions, keep_empty_rows=keep_empty_rows, metrics=metrics, pivots=pivots, return_property_quota=return_property_quota,
                cohort_spec=_models.RunPivotReportRequestBodyCohortSpec(cohorts=cohorts,
                    cohort_report_settings=_models.RunPivotReportRequestBodyCohortSpecCohortReportSettings(accumulate=accumulate) if any(v is not None for v in [accumulate]) else None,
                    cohorts_range=_models.RunPivotReportRequestBodyCohortSpecCohortsRange(end_offset=_end_offset, granularity=granularity, start_offset=_start_offset) if any(v is not None for v in [end_offset, granularity, start_offset]) else None) if any(v is not None for v in [accumulate, cohorts, end_offset, granularity, start_offset]) else None,
                dimension_filter=_models.RunPivotReportRequestBodyDimensionFilter(not_expression=dimension_filter_not_expression,
                    and_group=_models.RunPivotReportRequestBodyDimensionFilterAndGroup(expressions=dimension_filter_and_group_expressions) if any(v is not None for v in [dimension_filter_and_group_expressions]) else None,
                    or_group=_models.RunPivotReportRequestBodyDimensionFilterOrGroup(expressions=dimension_filter_or_group_expressions) if any(v is not None for v in [dimension_filter_or_group_expressions]) else None,
                    filter_=_models.RunPivotReportRequestBodyDimensionFilterFilter(empty_filter=dimension_filter_filter_empty_filter, field_name=dimension_filter_filter_field_name,
                        between_filter=_models.RunPivotReportRequestBodyDimensionFilterFilterBetweenFilter(from_value=dimension_filter_filter_between_filter_from_value, to_value=dimension_filter_filter_between_filter_to_value) if any(v is not None for v in [dimension_filter_filter_between_filter_from_value, dimension_filter_filter_between_filter_to_value]) else None,
                        in_list_filter=_models.RunPivotReportRequestBodyDimensionFilterFilterInListFilter(case_sensitive=dimension_filter_filter_in_list_filter_case_sensitive, values=dimension_filter_filter_in_list_filter_values) if any(v is not None for v in [dimension_filter_filter_in_list_filter_case_sensitive, dimension_filter_filter_in_list_filter_values]) else None,
                        string_filter=_models.RunPivotReportRequestBodyDimensionFilterFilterStringFilter(case_sensitive=dimension_filter_filter_string_filter_case_sensitive, value=dimension_filter_filter_string_filter_value, match_type=dimension_filter_filter_string_filter_match_type) if any(v is not None for v in [dimension_filter_filter_string_filter_case_sensitive, dimension_filter_filter_string_filter_value, dimension_filter_filter_string_filter_match_type]) else None,
                        numeric_filter=_models.RunPivotReportRequestBodyDimensionFilterFilterNumericFilter(operation=dimension_filter_filter_numeric_filter_operation, value=dimension_filter_filter_numeric_filter_value) if any(v is not None for v in [dimension_filter_filter_numeric_filter_operation, dimension_filter_filter_numeric_filter_value]) else None) if any(v is not None for v in [dimension_filter_filter_between_filter_from_value, dimension_filter_filter_between_filter_to_value, dimension_filter_filter_empty_filter, dimension_filter_filter_field_name, dimension_filter_filter_in_list_filter_case_sensitive, dimension_filter_filter_string_filter_case_sensitive, dimension_filter_filter_in_list_filter_values, dimension_filter_filter_numeric_filter_operation, dimension_filter_filter_numeric_filter_value, dimension_filter_filter_string_filter_value, dimension_filter_filter_string_filter_match_type]) else None) if any(v is not None for v in [dimension_filter_and_group_expressions, dimension_filter_or_group_expressions, dimension_filter_filter_between_filter_from_value, dimension_filter_filter_between_filter_to_value, dimension_filter_filter_empty_filter, dimension_filter_filter_field_name, dimension_filter_filter_in_list_filter_case_sensitive, dimension_filter_filter_string_filter_case_sensitive, dimension_filter_filter_in_list_filter_values, dimension_filter_filter_numeric_filter_operation, dimension_filter_filter_numeric_filter_value, dimension_filter_filter_string_filter_value, dimension_filter_filter_string_filter_match_type, dimension_filter_not_expression]) else None,
                metric_filter=_models.RunPivotReportRequestBodyMetricFilter(not_expression=metric_filter_not_expression,
                    and_group=_models.RunPivotReportRequestBodyMetricFilterAndGroup(expressions=metric_filter_and_group_expressions) if any(v is not None for v in [metric_filter_and_group_expressions]) else None,
                    or_group=_models.RunPivotReportRequestBodyMetricFilterOrGroup(expressions=metric_filter_or_group_expressions) if any(v is not None for v in [metric_filter_or_group_expressions]) else None,
                    filter_=_models.RunPivotReportRequestBodyMetricFilterFilter(empty_filter=metric_filter_filter_empty_filter, field_name=metric_filter_filter_field_name,
                        between_filter=_models.RunPivotReportRequestBodyMetricFilterFilterBetweenFilter(from_value=metric_filter_filter_between_filter_from_value, to_value=metric_filter_filter_between_filter_to_value) if any(v is not None for v in [metric_filter_filter_between_filter_from_value, metric_filter_filter_between_filter_to_value]) else None,
                        in_list_filter=_models.RunPivotReportRequestBodyMetricFilterFilterInListFilter(case_sensitive=metric_filter_filter_in_list_filter_case_sensitive, values=metric_filter_filter_in_list_filter_values) if any(v is not None for v in [metric_filter_filter_in_list_filter_case_sensitive, metric_filter_filter_in_list_filter_values]) else None,
                        string_filter=_models.RunPivotReportRequestBodyMetricFilterFilterStringFilter(case_sensitive=metric_filter_filter_string_filter_case_sensitive, value=metric_filter_filter_string_filter_value, match_type=metric_filter_filter_string_filter_match_type) if any(v is not None for v in [metric_filter_filter_string_filter_case_sensitive, metric_filter_filter_string_filter_value, metric_filter_filter_string_filter_match_type]) else None,
                        numeric_filter=_models.RunPivotReportRequestBodyMetricFilterFilterNumericFilter(operation=metric_filter_filter_numeric_filter_operation, value=metric_filter_filter_numeric_filter_value) if any(v is not None for v in [metric_filter_filter_numeric_filter_operation, metric_filter_filter_numeric_filter_value]) else None) if any(v is not None for v in [metric_filter_filter_between_filter_from_value, metric_filter_filter_between_filter_to_value, metric_filter_filter_empty_filter, metric_filter_filter_field_name, metric_filter_filter_in_list_filter_case_sensitive, metric_filter_filter_string_filter_case_sensitive, metric_filter_filter_in_list_filter_values, metric_filter_filter_numeric_filter_operation, metric_filter_filter_numeric_filter_value, metric_filter_filter_string_filter_value, metric_filter_filter_string_filter_match_type]) else None) if any(v is not None for v in [metric_filter_and_group_expressions, metric_filter_or_group_expressions, metric_filter_filter_between_filter_from_value, metric_filter_filter_between_filter_to_value, metric_filter_filter_empty_filter, metric_filter_filter_field_name, metric_filter_filter_in_list_filter_case_sensitive, metric_filter_filter_string_filter_case_sensitive, metric_filter_filter_in_list_filter_values, metric_filter_filter_numeric_filter_operation, metric_filter_filter_numeric_filter_value, metric_filter_filter_string_filter_value, metric_filter_filter_string_filter_match_type, metric_filter_not_expression]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_pivot_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1beta/{property}:runPivotReport", _request.path.model_dump(by_alias=True)) if _request.path else "/v1beta/{property}:runPivotReport"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_pivot_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_pivot_report", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_pivot_report",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def get_realtime_report(
    property_: str = Field(..., alias="property", description="The Google Analytics property identifier whose events are tracked. Format: properties/{propertyId}. Find your Property ID in your Google Analytics account settings."),
    dimension_filter_or_group_expressions: list[_models.FilterExpression] | None = Field(None, alias="dimensionFilterOrGroupExpressions", description="Filter expressions to apply to dimensions. Multiple expressions are combined with OR logic."),
    metric_filter_and_group_expressions: list[_models.FilterExpression] | None = Field(None, alias="metricFilterAndGroupExpressions", description="Filter expressions to apply to metrics. Multiple expressions are combined with AND logic."),
    metric_filter_or_group_expressions: list[_models.FilterExpression] | None = Field(None, alias="metricFilterOrGroupExpressions", description="Filter expressions to apply to metrics. Multiple expressions are combined with OR logic."),
    from_value: dict[str, Any] | None = Field(None, alias="fromValue", description="The lower bound (inclusive) for a numeric range filter on metrics."),
    to_value: dict[str, Any] | None = Field(None, alias="toValue", description="The upper bound (inclusive) for a numeric range filter on metrics."),
    empty_filter: dict[str, Any] | None = Field(None, alias="emptyFilter", description="Filter to match empty or unset values in a dimension or metric."),
    field_name: str | None = Field(None, alias="fieldName", description="The name of the dimension or metric to filter on. Must be a valid Google Analytics dimension or metric name."),
    in_list_filter_case_sensitive: bool | None = Field(None, alias="inListFilterCaseSensitive", description="Whether string matching in the in-list filter is case-sensitive. Defaults to false."),
    string_filter_case_sensitive: bool | None = Field(None, alias="stringFilterCaseSensitive", description="Whether string matching in the string filter is case-sensitive. Defaults to false."),
    values: list[str] | None = Field(None, description="A list of string values to match against. At least one value is required."),
    operation: Literal["OPERATION_UNSPECIFIED", "EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL"] | None = Field(None, description="The comparison operation to apply for numeric filtering."),
    numeric_filter_value: dict[str, Any] | None = Field(None, alias="numericFilterValue", description="The numeric or date value to compare against in the filter operation."),
    string_filter_value: str | None = Field(None, alias="stringFilterValue", description="The string value to match against in the filter."),
    match_type: Literal["MATCH_TYPE_UNSPECIFIED", "EXACT", "BEGINS_WITH", "ENDS_WITH", "CONTAINS", "FULL_REGEXP", "PARTIAL_REGEXP"] | None = Field(None, alias="matchType", description="The matching strategy for the string filter."),
    not_expression: _models.FilterExpression | None = Field(None, alias="notExpression", description="Logical NOT expression to negate the filter condition."),
    dimensions: list[_models.Dimension] | None = Field(None, description="The dimensions to include in the report. Dimensions break down metrics by categorical values (e.g., country, device type, page path)."),
    limit: str | None = Field(None, description="Maximum number of rows to return. Defaults to 10,000 if unspecified. API maximum is 250,000 rows per request. Must be a positive integer."),
    metric_aggregations: list[Literal["METRIC_AGGREGATION_UNSPECIFIED", "TOTAL", "MINIMUM", "MAXIMUM", "COUNT"]] | None = Field(None, alias="metricAggregations", description="Aggregation methods for metrics. Aggregated values appear in rows with dimension values set to the aggregation type (e.g., RESERVED_TOTAL)."),
    metrics: list[_models.Metric] | None = Field(None, description="The metrics to include in the report. Metrics are quantitative measurements (e.g., activeUsers, eventCount, screenPageViews)."),
    minute_ranges: list[_models.MinuteRange] | None = Field(None, alias="minuteRanges", description="Time ranges in minutes to retrieve data from. If unspecified, defaults to the last 30 minutes. Multiple ranges can be requested; overlapping minutes appear in results for each range."),
    order_bys: list[_models.OrderBy] | None = Field(None, alias="orderBys", description="Specifies the sort order for report rows. Can sort by dimension values or metric values in ascending or descending order."),
    return_property_quota: bool | None = Field(None, alias="returnPropertyQuota", description="Whether to include the current quota status for this property in the response. Useful for monitoring API quota consumption."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a customized report of real-time event data for a Google Analytics property, showing events and usage from the present moment up to 30 minutes ago (60 minutes for GA360). Data appears in reports within seconds of being sent to Google Analytics."""

    # Construct request model with validation
    try:
        _request = _models.RunRealtimeReportRequest(
            path=_models.RunRealtimeReportRequestPath(property_=property_),
            body=_models.RunRealtimeReportRequestBody(dimensions=dimensions, limit=limit, metric_aggregations=metric_aggregations, metrics=metrics, minute_ranges=minute_ranges, order_bys=order_bys, return_property_quota=return_property_quota,
                dimension_filter=_models.RunRealtimeReportRequestBodyDimensionFilter(or_group=_models.RunRealtimeReportRequestBodyDimensionFilterOrGroup(expressions=dimension_filter_or_group_expressions) if any(v is not None for v in [dimension_filter_or_group_expressions]) else None) if any(v is not None for v in [dimension_filter_or_group_expressions]) else None,
                metric_filter=_models.RunRealtimeReportRequestBodyMetricFilter(not_expression=not_expression,
                    and_group=_models.RunRealtimeReportRequestBodyMetricFilterAndGroup(expressions=metric_filter_and_group_expressions) if any(v is not None for v in [metric_filter_and_group_expressions]) else None,
                    or_group=_models.RunRealtimeReportRequestBodyMetricFilterOrGroup(expressions=metric_filter_or_group_expressions) if any(v is not None for v in [metric_filter_or_group_expressions]) else None,
                    filter_=_models.RunRealtimeReportRequestBodyMetricFilterFilter(empty_filter=empty_filter, field_name=field_name,
                        between_filter=_models.RunRealtimeReportRequestBodyMetricFilterFilterBetweenFilter(from_value=from_value, to_value=to_value) if any(v is not None for v in [from_value, to_value]) else None,
                        in_list_filter=_models.RunRealtimeReportRequestBodyMetricFilterFilterInListFilter(case_sensitive=in_list_filter_case_sensitive, values=values) if any(v is not None for v in [in_list_filter_case_sensitive, values]) else None,
                        string_filter=_models.RunRealtimeReportRequestBodyMetricFilterFilterStringFilter(case_sensitive=string_filter_case_sensitive, value=string_filter_value, match_type=match_type) if any(v is not None for v in [string_filter_case_sensitive, string_filter_value, match_type]) else None,
                        numeric_filter=_models.RunRealtimeReportRequestBodyMetricFilterFilterNumericFilter(operation=operation, value=numeric_filter_value) if any(v is not None for v in [operation, numeric_filter_value]) else None) if any(v is not None for v in [from_value, to_value, empty_filter, field_name, in_list_filter_case_sensitive, string_filter_case_sensitive, values, operation, numeric_filter_value, string_filter_value, match_type]) else None) if any(v is not None for v in [metric_filter_and_group_expressions, metric_filter_or_group_expressions, from_value, to_value, empty_filter, field_name, in_list_filter_case_sensitive, string_filter_case_sensitive, values, operation, numeric_filter_value, string_filter_value, match_type, not_expression]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_realtime_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1beta/{property}:runRealtimeReport", _request.path.model_dump(by_alias=True)) if _request.path else "/v1beta/{property}:runRealtimeReport"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_realtime_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_realtime_report", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_realtime_report",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def run_report(
    property_: str = Field(..., alias="property", description="A Google Analytics property identifier whose events are tracked. Specified in the URL path and not the body. To learn more, see [where to find your Property ID](https://developers.google.com/analytics/devguides/reporting/data/v1/property-id). Within a batch request, this property should either be unspecified or consistent with the batch-level property. Example: properties/1234"),
    accumulate: bool | None = Field(None, description="If true, accumulates the result from first touch day to the end day. Not supported in `RunReportRequest`."),
    cohorts: list[_models.Cohort] | None = Field(None, description="Defines the selection criteria to group users into cohorts. Most cohort reports define only a single cohort. If multiple cohorts are specified, each cohort can be recognized in the report by their name."),
    end_offset: str | None = Field(None, alias="endOffset", description="Required. `endOffset` specifies the end date of the extended reporting date range for a cohort report. `endOffset` can be any positive integer but is commonly set to 5 to 10 so that reports contain data on the cohort for the next several granularity time periods. If `granularity` is `DAILY`, the `endDate` of the extended reporting date range is `endDate` of the cohort plus `endOffset` days. If `granularity` is `WEEKLY`, the `endDate` of the extended reporting date range is `endDate` of the cohort plus `endOffset * 7` days. If `granularity` is `MONTHLY`, the `endDate` of the extended reporting date range is `endDate` of the cohort plus `endOffset * 30` days."),
    granularity: Literal["GRANULARITY_UNSPECIFIED", "DAILY", "WEEKLY", "MONTHLY"] | None = Field(None, description="Required. The granularity used to interpret the `startOffset` and `endOffset` for the extended reporting date range for a cohort report."),
    start_offset: str | None = Field(None, alias="startOffset", description="`startOffset` specifies the start date of the extended reporting date range for a cohort report. `startOffset` is commonly set to 0 so that reports contain data from the acquisition of the cohort forward. If `granularity` is `DAILY`, the `startDate` of the extended reporting date range is `startDate` of the cohort plus `startOffset` days. If `granularity` is `WEEKLY`, the `startDate` of the extended reporting date range is `startDate` of the cohort plus `startOffset * 7` days. If `granularity` is `MONTHLY`, the `startDate` of the extended reporting date range is `startDate` of the cohort plus `startOffset * 30` days."),
    comparisons: list[_models.Comparison] | None = Field(None, description="Optional. The configuration of comparisons requested and displayed. The request only requires a comparisons field in order to receive a comparison column in the response."),
    currency_code: str | None = Field(None, alias="currencyCode", description="A currency code in ISO4217 format, such as \"AED\", \"USD\", \"JPY\". If the field is empty, the report uses the property's default currency."),
    date_ranges: list[_models.DateRange] | None = Field(None, alias="dateRanges", description="Date ranges of data to read. If multiple date ranges are requested, each response row will contain a zero based date range index. If two date ranges overlap, the event data for the overlapping days is included in the response rows for both date ranges. In a cohort request, this `dateRanges` must be unspecified."),
    dimension_filter_filter_between_filter_from_value: dict[str, Any] | None = Field(None, alias="dimensionFilterFilterBetweenFilterFromValue", description="Begins with this number."),
    metric_filter_filter_between_filter_from_value: dict[str, Any] | None = Field(None, alias="metricFilterFilterBetweenFilterFromValue", description="Begins with this number."),
    dimension_filter_filter_between_filter_to_value: dict[str, Any] | None = Field(None, alias="dimensionFilterFilterBetweenFilterToValue", description="Ends with this number."),
    metric_filter_filter_between_filter_to_value: dict[str, Any] | None = Field(None, alias="metricFilterFilterBetweenFilterToValue", description="Ends with this number."),
    dimension_filter_filter_empty_filter: dict[str, Any] | None = Field(None, alias="dimensionFilterFilterEmptyFilter", description="A filter for empty values such as \"(not set)\" and \"\" values."),
    metric_filter_filter_empty_filter: dict[str, Any] | None = Field(None, alias="metricFilterFilterEmptyFilter", description="A filter for empty values such as \"(not set)\" and \"\" values."),
    dimension_filter_filter_field_name: str | None = Field(None, alias="dimensionFilterFilterFieldName", description="The dimension name or metric name. In most methods, dimensions & metrics can be used for the first time in this field. However in a RunPivotReportRequest, this field must be additionally specified by name in the RunPivotReportRequest's dimensions or metrics."),
    metric_filter_filter_field_name: str | None = Field(None, alias="metricFilterFilterFieldName", description="The dimension name or metric name. In most methods, dimensions & metrics can be used for the first time in this field. However in a RunPivotReportRequest, this field must be additionally specified by name in the RunPivotReportRequest's dimensions or metrics."),
    dimension_filter_filter_in_list_filter_case_sensitive: bool | None = Field(None, alias="dimensionFilterFilterInListFilterCaseSensitive", description="If true, the string value is case sensitive."),
    dimension_filter_filter_string_filter_case_sensitive: bool | None = Field(None, alias="dimensionFilterFilterStringFilterCaseSensitive", description="If true, the string value is case sensitive."),
    metric_filter_filter_in_list_filter_case_sensitive: bool | None = Field(None, alias="metricFilterFilterInListFilterCaseSensitive", description="If true, the string value is case sensitive."),
    metric_filter_filter_string_filter_case_sensitive: bool | None = Field(None, alias="metricFilterFilterStringFilterCaseSensitive", description="If true, the string value is case sensitive."),
    dimension_filter_filter_in_list_filter_values: list[str] | None = Field(None, alias="dimensionFilterFilterInListFilterValues", description="The list of string values. Must be non-empty."),
    metric_filter_filter_in_list_filter_values: list[str] | None = Field(None, alias="metricFilterFilterInListFilterValues", description="The list of string values. Must be non-empty."),
    dimension_filter_filter_numeric_filter_operation: Literal["OPERATION_UNSPECIFIED", "EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL"] | None = Field(None, alias="dimensionFilterFilterNumericFilterOperation", description="The operation type for this filter."),
    metric_filter_filter_numeric_filter_operation: Literal["OPERATION_UNSPECIFIED", "EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL"] | None = Field(None, alias="metricFilterFilterNumericFilterOperation", description="The operation type for this filter."),
    dimension_filter_filter_numeric_filter_value: dict[str, Any] | None = Field(None, alias="dimensionFilterFilterNumericFilterValue", description="A numeric value or a date value."),
    dimension_filter_filter_string_filter_value: str | None = Field(None, alias="dimensionFilterFilterStringFilterValue", description="The string value used for the matching."),
    metric_filter_filter_numeric_filter_value: dict[str, Any] | None = Field(None, alias="metricFilterFilterNumericFilterValue", description="A numeric value or a date value."),
    metric_filter_filter_string_filter_value: str | None = Field(None, alias="metricFilterFilterStringFilterValue", description="The string value used for the matching."),
    dimension_filter_filter_string_filter_match_type: Literal["MATCH_TYPE_UNSPECIFIED", "EXACT", "BEGINS_WITH", "ENDS_WITH", "CONTAINS", "FULL_REGEXP", "PARTIAL_REGEXP"] | None = Field(None, alias="dimensionFilterFilterStringFilterMatchType", description="The match type for this filter."),
    metric_filter_filter_string_filter_match_type: Literal["MATCH_TYPE_UNSPECIFIED", "EXACT", "BEGINS_WITH", "ENDS_WITH", "CONTAINS", "FULL_REGEXP", "PARTIAL_REGEXP"] | None = Field(None, alias="metricFilterFilterStringFilterMatchType", description="The match type for this filter."),
    dimension_filter_not_expression: _models.FilterExpression | None = Field(None, alias="dimensionFilterNotExpression"),
    metric_filter_not_expression: _models.FilterExpression | None = Field(None, alias="metricFilterNotExpression"),
    dimensions: list[_models.Dimension] | None = Field(None, description="The dimensions requested and displayed."),
    keep_empty_rows: bool | None = Field(None, alias="keepEmptyRows", description="If false or unspecified, each row with all metrics equal to 0 will not be returned. If true, these rows will be returned if they are not separately removed by a filter. Regardless of this `keep_empty_rows` setting, only data recorded by the Google Analytics property can be displayed in a report. For example if a property never logs a `purchase` event, then a query for the `eventName` dimension and `eventCount` metric will not have a row eventName: \"purchase\" and eventCount: 0."),
    limit: str | None = Field(None, description="The number of rows to return. If unspecified, 10,000 rows are returned. The API returns a maximum of 250,000 rows per request, no matter how many you ask for. `limit` must be positive. The API can also return fewer rows than the requested `limit`, if there aren't as many dimension values as the `limit`. For instance, there are fewer than 300 possible values for the dimension `country`, so when reporting on only `country`, you can't get more than 300 rows, even if you set `limit` to a higher value. To learn more about this pagination parameter, see [Pagination](https://developers.google.com/analytics/devguides/reporting/data/v1/basics#pagination)."),
    metric_aggregations: list[Literal["METRIC_AGGREGATION_UNSPECIFIED", "TOTAL", "MINIMUM", "MAXIMUM", "COUNT"]] | None = Field(None, alias="metricAggregations", description="Aggregation of metrics. Aggregated metric values will be shown in rows where the dimension_values are set to \"RESERVED_(MetricAggregation)\". Aggregates including both comparisons and multiple date ranges will be aggregated based on the date ranges."),
    metrics: list[_models.Metric] | None = Field(None, description="The metrics requested and displayed."),
    offset: str | None = Field(None, description="The row count of the start row. The first row is counted as row 0. When paging, the first request does not specify offset; or equivalently, sets offset to 0; the first request returns the first `limit` of rows. The second request sets offset to the `limit` of the first request; the second request returns the second `limit` of rows. To learn more about this pagination parameter, see [Pagination](https://developers.google.com/analytics/devguides/reporting/data/v1/basics#pagination)."),
    order_bys: list[_models.OrderBy] | None = Field(None, alias="orderBys", description="Specifies how rows are ordered in the response. Requests including both comparisons and multiple date ranges will have order bys applied on the comparisons."),
    return_property_quota: bool | None = Field(None, alias="returnPropertyQuota", description="Toggles whether to return the current state of this Google Analytics property's quota. Quota is returned in [PropertyQuota](#PropertyQuota)."),
) -> dict[str, Any] | ToolResult:
    """Returns a customized report of your Google Analytics event data. Reports contain statistics derived from data collected by the Google Analytics tracking code. The data returned from the API is as a table with columns for the requested dimensions and metrics. Metrics are individual measurements of user activity on your property, such as active users or event count. Dimensions break down metrics across some common criteria, such as country or event name. For a guide to constructing requests & understanding responses, see [Creating a Report](https://developers.google.com/analytics/devguides/reporting/data/v1/basics)."""

    _end_offset = _parse_int(end_offset)
    _start_offset = _parse_int(start_offset)

    # Construct request model with validation
    try:
        _request = _models.RunReportRequest(
            path=_models.RunReportRequestPath(property_=property_),
            body=_models.RunReportRequestBody(comparisons=comparisons, currency_code=currency_code, date_ranges=date_ranges, dimensions=dimensions, keep_empty_rows=keep_empty_rows, limit=limit, metric_aggregations=metric_aggregations, metrics=metrics, offset=offset, order_bys=order_bys, return_property_quota=return_property_quota,
                cohort_spec=_models.RunReportRequestBodyCohortSpec(cohorts=cohorts,
                    cohort_report_settings=_models.RunReportRequestBodyCohortSpecCohortReportSettings(accumulate=accumulate) if any(v is not None for v in [accumulate]) else None,
                    cohorts_range=_models.RunReportRequestBodyCohortSpecCohortsRange(end_offset=_end_offset, granularity=granularity, start_offset=_start_offset) if any(v is not None for v in [end_offset, granularity, start_offset]) else None) if any(v is not None for v in [accumulate, cohorts, end_offset, granularity, start_offset]) else None,
                dimension_filter=_models.RunReportRequestBodyDimensionFilter(not_expression=dimension_filter_not_expression,
                    filter_=_models.RunReportRequestBodyDimensionFilterFilter(empty_filter=dimension_filter_filter_empty_filter, field_name=dimension_filter_filter_field_name,
                        between_filter=_models.RunReportRequestBodyDimensionFilterFilterBetweenFilter(from_value=dimension_filter_filter_between_filter_from_value, to_value=dimension_filter_filter_between_filter_to_value) if any(v is not None for v in [dimension_filter_filter_between_filter_from_value, dimension_filter_filter_between_filter_to_value]) else None,
                        in_list_filter=_models.RunReportRequestBodyDimensionFilterFilterInListFilter(case_sensitive=dimension_filter_filter_in_list_filter_case_sensitive, values=dimension_filter_filter_in_list_filter_values) if any(v is not None for v in [dimension_filter_filter_in_list_filter_case_sensitive, dimension_filter_filter_in_list_filter_values]) else None,
                        string_filter=_models.RunReportRequestBodyDimensionFilterFilterStringFilter(case_sensitive=dimension_filter_filter_string_filter_case_sensitive, value=dimension_filter_filter_string_filter_value, match_type=dimension_filter_filter_string_filter_match_type) if any(v is not None for v in [dimension_filter_filter_string_filter_case_sensitive, dimension_filter_filter_string_filter_value, dimension_filter_filter_string_filter_match_type]) else None,
                        numeric_filter=_models.RunReportRequestBodyDimensionFilterFilterNumericFilter(operation=dimension_filter_filter_numeric_filter_operation, value=dimension_filter_filter_numeric_filter_value) if any(v is not None for v in [dimension_filter_filter_numeric_filter_operation, dimension_filter_filter_numeric_filter_value]) else None) if any(v is not None for v in [dimension_filter_filter_between_filter_from_value, dimension_filter_filter_between_filter_to_value, dimension_filter_filter_empty_filter, dimension_filter_filter_field_name, dimension_filter_filter_in_list_filter_case_sensitive, dimension_filter_filter_string_filter_case_sensitive, dimension_filter_filter_in_list_filter_values, dimension_filter_filter_numeric_filter_operation, dimension_filter_filter_numeric_filter_value, dimension_filter_filter_string_filter_value, dimension_filter_filter_string_filter_match_type]) else None) if any(v is not None for v in [dimension_filter_filter_between_filter_from_value, dimension_filter_filter_between_filter_to_value, dimension_filter_filter_empty_filter, dimension_filter_filter_field_name, dimension_filter_filter_in_list_filter_case_sensitive, dimension_filter_filter_string_filter_case_sensitive, dimension_filter_filter_in_list_filter_values, dimension_filter_filter_numeric_filter_operation, dimension_filter_filter_numeric_filter_value, dimension_filter_filter_string_filter_value, dimension_filter_filter_string_filter_match_type, dimension_filter_not_expression]) else None,
                metric_filter=_models.RunReportRequestBodyMetricFilter(not_expression=metric_filter_not_expression,
                    filter_=_models.RunReportRequestBodyMetricFilterFilter(empty_filter=metric_filter_filter_empty_filter, field_name=metric_filter_filter_field_name,
                        between_filter=_models.RunReportRequestBodyMetricFilterFilterBetweenFilter(from_value=metric_filter_filter_between_filter_from_value, to_value=metric_filter_filter_between_filter_to_value) if any(v is not None for v in [metric_filter_filter_between_filter_from_value, metric_filter_filter_between_filter_to_value]) else None,
                        in_list_filter=_models.RunReportRequestBodyMetricFilterFilterInListFilter(case_sensitive=metric_filter_filter_in_list_filter_case_sensitive, values=metric_filter_filter_in_list_filter_values) if any(v is not None for v in [metric_filter_filter_in_list_filter_case_sensitive, metric_filter_filter_in_list_filter_values]) else None,
                        string_filter=_models.RunReportRequestBodyMetricFilterFilterStringFilter(case_sensitive=metric_filter_filter_string_filter_case_sensitive, value=metric_filter_filter_string_filter_value, match_type=metric_filter_filter_string_filter_match_type) if any(v is not None for v in [metric_filter_filter_string_filter_case_sensitive, metric_filter_filter_string_filter_value, metric_filter_filter_string_filter_match_type]) else None,
                        numeric_filter=_models.RunReportRequestBodyMetricFilterFilterNumericFilter(operation=metric_filter_filter_numeric_filter_operation, value=metric_filter_filter_numeric_filter_value) if any(v is not None for v in [metric_filter_filter_numeric_filter_operation, metric_filter_filter_numeric_filter_value]) else None) if any(v is not None for v in [metric_filter_filter_between_filter_from_value, metric_filter_filter_between_filter_to_value, metric_filter_filter_empty_filter, metric_filter_filter_field_name, metric_filter_filter_in_list_filter_case_sensitive, metric_filter_filter_string_filter_case_sensitive, metric_filter_filter_in_list_filter_values, metric_filter_filter_numeric_filter_operation, metric_filter_filter_numeric_filter_value, metric_filter_filter_string_filter_value, metric_filter_filter_string_filter_match_type]) else None) if any(v is not None for v in [metric_filter_filter_between_filter_from_value, metric_filter_filter_between_filter_to_value, metric_filter_filter_empty_filter, metric_filter_filter_field_name, metric_filter_filter_in_list_filter_case_sensitive, metric_filter_filter_string_filter_case_sensitive, metric_filter_filter_in_list_filter_values, metric_filter_filter_numeric_filter_operation, metric_filter_filter_numeric_filter_value, metric_filter_filter_string_filter_value, metric_filter_filter_string_filter_match_type, metric_filter_not_expression]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for run_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1beta/{property}:runReport", _request.path.model_dump(by_alias=True)) if _request.path else "/v1beta/{property}:runReport"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("run_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("run_report", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="run_report",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def list_audience_exports(
    parent: str = Field(..., description="The property for which to list audience exports. Format: properties/{property}"),
    page_size: int | None = Field(None, alias="pageSize", description="Maximum number of audience exports to return per page. The service may return fewer than specified. Higher values are coerced to the maximum allowed."),
    page_token: str | None = Field(None, alias="pageToken", description="Page token from a previous ListAudienceExports call to retrieve the next page of results. When paginating, all other parameters must match the original request."),
) -> dict[str, Any] | ToolResult:
    """Lists all audience exports for a property, allowing you to find and reuse existing exports rather than creating duplicates. The same audience can have multiple exports representing user snapshots from different dates."""

    # Construct request model with validation
    try:
        _request = _models.AudienceExportsListRequest(
            path=_models.AudienceExportsListRequestPath(parent=parent),
            query=_models.AudienceExportsListRequestQuery(page_size=page_size, page_token=page_token)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_audience_exports: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1beta/{parent}/audienceExports", _request.path.model_dump(by_alias=True)) if _request.path else "/v1beta/{parent}/audienceExports"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_audience_exports")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_audience_exports", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_audience_exports",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def create_audience_export(
    parent: str = Field(..., description="The parent property resource where this audience export will be created. Format: properties/{property}"),
    audience: str | None = Field(None, description="The audience resource to export. This identifies which audience's users will be included in the export. Format: properties/{property}/audiences/{audience}"),
    dimensions: list[_models.V1betaAudienceDimension] | None = Field(None, description="The dimensions to include in the audience export response. Specifies which user attributes or characteristics will be returned in the exported data."),
) -> dict[str, Any] | ToolResult:
    """Creates a snapshot of users currently in an audience and initiates an asynchronous export process. Use QueryAudienceExport to retrieve the exported audience data after creation."""

    # Construct request model with validation
    try:
        _request = _models.AudienceExportsCreateRequest(
            path=_models.AudienceExportsCreateRequestPath(parent=parent),
            body=_models.AudienceExportsCreateRequestBody(audience=audience, dimensions=dimensions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_audience_export: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1beta/{parent}/audienceExports", _request.path.model_dump(by_alias=True)) if _request.path else "/v1beta/{parent}/audienceExports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_audience_export")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_audience_export", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_audience_export",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def query_audience_export(
    name: str = Field(..., description="The resource name of the audience export to query. Format: properties/{property}/audienceExports/{audience_export}"),
    limit: str | None = Field(None, description="Maximum number of rows to return per request. Defaults to 10,000 if unspecified. The API returns a maximum of 250,000 rows regardless of the requested limit. Must be a positive integer."),
    offset: str | None = Field(None, description="The zero-indexed row number to start from for pagination. Omit or set to 0 for the first request. For subsequent requests, set to the limit value from the previous response to retrieve the next batch of rows."),
) -> dict[str, Any] | ToolResult:
    """Retrieves user data from a previously created audience export. Users must first be exported via CreateAudienceExport before they can be queried using this method."""

    # Construct request model with validation
    try:
        _request = _models.AudienceExportsQueryRequest(
            path=_models.AudienceExportsQueryRequestPath(name=name),
            body=_models.AudienceExportsQueryRequestBody(limit=limit, offset=offset)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for query_audience_export: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1beta/{name}:query", _request.path.model_dump(by_alias=True)) if _request.path else "/v1beta/{name}:query"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("query_audience_export")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("query_audience_export", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="query_audience_export",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
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
        print("  python google_analytics_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Google Analytics MCP Server")

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
    logger.info("Starting Google Analytics MCP Server")
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

#!/usr/bin/env python3
"""
Rootly MCP Server
Generated: 2026-04-23 21:09:28 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://api.rootly.com")
SERVER_NAME = "Rootly"
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
    'bearer_auth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["bearer_auth"] = _auth.BearerTokenAuth(env_var="BEARER_TOKEN", token_format="Bearer")
    logging.info("Authentication configured: bearer_auth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for bearer_auth not configured: {error_msg}")
    _auth_handlers["bearer_auth"] = None

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

mcp = FastMCP("Rootly", middleware=[_JsonCoercionMiddleware()])

# Tags: AlertEvents
@mcp.tool()
async def list_alert_events(
    alert_id: str = Field(..., description="The unique identifier of the alert for which to retrieve events."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., actor, metadata). Reduces need for additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of events to return per page. Adjust to balance response size and number of requests needed."),
    filter_kind: str | None = Field(None, alias="filterkind", description="Filter results by event kind (e.g., created, updated, resolved). Narrows results to specific event types."),
    filter_action: str | None = Field(None, alias="filteraction", description="Filter results by action type (e.g., triggered, acknowledged, dismissed). Narrows results to specific actions performed on the alert."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of events associated with a specific alert, with optional filtering by event kind and action type."""

    # Construct request model with validation
    try:
        _request = _models.ListAlertEventsRequest(
            path=_models.ListAlertEventsRequestPath(alert_id=alert_id),
            query=_models.ListAlertEventsRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_kind=filter_kind, filter_action=filter_action)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_alert_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alerts/{alert_id}/events", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alerts/{alert_id}/events"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_alert_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_alert_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_alert_events",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertEvents
@mcp.tool()
async def create_alert_event(
    alert_id: str = Field(..., description="The unique identifier of the alert to which this event will be attached."),
    type_: Literal["alert_events"] = Field(..., alias="type", description="The category of event being created. Must be 'alert_events' to classify this as an alert event."),
    kind: Literal["note"] = Field(..., description="The type of event content being added. Must be 'note' to indicate this is a note-type event."),
    details: str = Field(..., description="The text content of the note being added to the alert. This message will be stored as part of the alert's event history."),
    user_id: int | None = Field(None, description="The user ID of the person creating this note. If not provided, the event will be created without an explicit author attribution."),
) -> dict[str, Any] | ToolResult:
    """Creates a new note event attached to an alert. This allows adding contextual notes or updates to track alert activity and history."""

    # Construct request model with validation
    try:
        _request = _models.CreateAlertEventRequest(
            path=_models.CreateAlertEventRequestPath(alert_id=alert_id),
            body=_models.CreateAlertEventRequestBody(data=_models.CreateAlertEventRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateAlertEventRequestBodyDataAttributes(kind=kind, user_id=user_id, details=details)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_alert_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alerts/{alert_id}/events", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alerts/{alert_id}/events"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_alert_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_alert_event", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_alert_event",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertEvents
@mcp.tool()
async def get_alert_event(id_: str = Field(..., alias="id", description="The unique identifier of the alert event to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific alert event by its unique identifier. Use this to fetch detailed information about a single alert event."""

    # Construct request model with validation
    try:
        _request = _models.GetAlertEventRequest(
            path=_models.GetAlertEventRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_alert_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alert_events/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alert_events/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_alert_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_alert_event", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_alert_event",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertEvents
@mcp.tool()
async def update_alert_event(
    id_: str = Field(..., alias="id", description="The unique identifier of the alert event to update."),
    type_: Literal["alert_events"] = Field(..., alias="type", description="The resource type, which must be 'alert_events' to identify this as an alert event resource."),
    details: str = Field(..., description="The text content of the note to add or update for this alert event."),
    user_id: int | None = Field(None, description="The user ID of the person authoring the note. Optional if the note is being added by the system or current authenticated user."),
) -> dict[str, Any] | ToolResult:
    """Update a specific alert event by adding or modifying a note. Requires the alert event ID, resource type identifier, and note content."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAlertEventRequest(
            path=_models.UpdateAlertEventRequestPath(id_=id_),
            body=_models.UpdateAlertEventRequestBody(data=_models.UpdateAlertEventRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateAlertEventRequestBodyDataAttributes(user_id=user_id, details=details)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_alert_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alert_events/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alert_events/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_alert_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_alert_event", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_alert_event",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertEvents
@mcp.tool()
async def delete_alert_event(id_: str = Field(..., alias="id", description="The unique identifier of the alert event to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific alert event by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAlertEventRequest(
            path=_models.DeleteAlertEventRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_alert_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alert_events/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alert_events/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_alert_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_alert_event", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_alert_event",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertGroups
@mcp.tool()
async def list_alert_groups(include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., rules, notifications). Omit to return only alert group core data.")) -> dict[str, Any] | ToolResult:
    """Retrieve a list of all alert groups. Use the include parameter to expand related resources in the response."""

    # Construct request model with validation
    try:
        _request = _models.ListAlertGroupsRequest(
            query=_models.ListAlertGroupsRequestQuery(include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_alert_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/alert_groups"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_alert_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_alert_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_alert_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertGroups
@mcp.tool()
async def create_alert_group(
    type_: Literal["alert_groups"] = Field(..., alias="type", description="The resource type identifier; must be set to 'alert_groups' to specify this is an alert group resource."),
    name: str = Field(..., description="A human-readable name for the alert group used for identification and display purposes."),
    targets: list[_models.CreateAlertGroupBodyDataAttributesTargetsItem] = Field(..., description="An array of target destinations where alerts in this group will be routed or delivered. Specify targets as an ordered list of destination objects or identifiers."),
    description: str | None = Field(None, description="An optional description explaining the purpose or context of the alert group."),
    time_window: int | None = Field(None, description="The duration in seconds that an alert group remains open and continues accepting new matching alerts before closing."),
    group_by_alert_title: Literal[1, 0] | None = Field(None, description="Set to 1 to group alerts by their title, or 0 to disable title-based grouping. Alerts with identical titles will be consolidated together."),
    group_by_alert_urgency: Literal[1, 0] | None = Field(None, description="Set to 1 to group alerts by their urgency level, or 0 to disable urgency-based grouping. Alerts with matching urgency will be consolidated together."),
    condition_type: Literal["all", "any"] | None = Field(None, description="Determines the matching logic for conditions: use 'all' to require all conditions to match, or 'any' to group alerts when at least one condition matches."),
    conditions: list[_models.CreateAlertGroupBodyDataAttributesConditionsItem] | None = Field(None, description="An array of condition objects that define which alerts should be included in this group. Each condition specifies a field and value to match against incoming alerts."),
) -> dict[str, Any] | ToolResult:
    """Creates a new alert group to automatically organize and correlate incoming alerts based on specified criteria. Alert groups help reduce noise by bundling related alerts together within a configurable time window."""

    # Construct request model with validation
    try:
        _request = _models.CreateAlertGroupRequest(
            body=_models.CreateAlertGroupRequestBody(data=_models.CreateAlertGroupRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateAlertGroupRequestBodyDataAttributes(name=name, description=description, time_window=time_window, targets=targets, group_by_alert_title=group_by_alert_title, group_by_alert_urgency=group_by_alert_urgency, condition_type=condition_type, conditions=conditions)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_alert_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/alert_groups"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_alert_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_alert_group", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_alert_group",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertGroups
@mcp.tool()
async def get_alert_group(id_: str = Field(..., alias="id", description="The unique identifier of the alert group to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific alert group by its unique identifier. Use this operation to fetch detailed information about a single alert group."""

    # Construct request model with validation
    try:
        _request = _models.GetAlertGroupRequest(
            path=_models.GetAlertGroupRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_alert_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alert_groups/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alert_groups/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_alert_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_alert_group", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_alert_group",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertGroups
@mcp.tool()
async def update_alert_group(
    id_: str = Field(..., alias="id", description="The unique identifier of the alert group to update."),
    type_: Literal["alert_groups"] = Field(..., alias="type", description="The resource type identifier; must be set to 'alert_groups'."),
    description: str | None = Field(None, description="A human-readable description of the alert group's purpose and scope."),
    time_window: int | None = Field(None, description="The duration in seconds that an alert group remains open to accept new alerts before closing."),
    targets: list[_models.UpdateAlertGroupBodyDataAttributesTargetsItem] | None = Field(None, description="An array of notification targets (e.g., email addresses, webhook URLs, or team identifiers) where alerts in this group should be sent."),
    group_by_alert_title: Literal[1, 0] | None = Field(None, description="Enable grouping of alerts by their title; set to 1 to enable or 0 to disable."),
    group_by_alert_urgency: Literal[1, 0] | None = Field(None, description="Enable grouping of alerts by their urgency level; set to 1 to enable or 0 to disable."),
    condition_type: Literal["all", "any"] | None = Field(None, description="Determines whether alerts must match ALL specified conditions or ANY of them to be grouped together."),
    conditions: list[_models.UpdateAlertGroupBodyDataAttributesConditionsItem] | None = Field(None, description="An array of matching conditions that define which alerts should be grouped together; each condition specifies a field and value to match against incoming alerts."),
) -> dict[str, Any] | ToolResult:
    """Update an existing alert group's configuration, including grouping rules, time window, description, and notification targets."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAlertGroupRequest(
            path=_models.UpdateAlertGroupRequestPath(id_=id_),
            body=_models.UpdateAlertGroupRequestBody(data=_models.UpdateAlertGroupRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateAlertGroupRequestBodyDataAttributes(description=description, time_window=time_window, targets=targets, group_by_alert_title=group_by_alert_title, group_by_alert_urgency=group_by_alert_urgency, condition_type=condition_type, conditions=conditions) if any(v is not None for v in [description, time_window, targets, group_by_alert_title, group_by_alert_urgency, condition_type, conditions]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_alert_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alert_groups/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alert_groups/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_alert_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_alert_group", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_alert_group",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertGroups
@mcp.tool()
async def delete_alert_group(id_: str = Field(..., alias="id", description="The unique identifier of the alert group to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific alert group by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAlertGroupRequest(
            path=_models.DeleteAlertGroupRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_alert_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alert_groups/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alert_groups/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_alert_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_alert_group", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_alert_group",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertUrgencies
@mcp.tool()
async def list_alert_urgencies(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., alerts, rules). Reduces the need for additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve for pagination, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of results per page. Adjust to balance between response size and number of requests needed."),
    sort: str | None = Field(None, description="Sort results by one or more fields using comma-separated values. Prefix field names with a minus sign (-) for descending order (e.g., -created_at,name)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of alert urgency levels. Use this to understand the available urgency classifications for alerts in your system."""

    # Construct request model with validation
    try:
        _request = _models.ListAlertUrgenciesRequest(
            query=_models.ListAlertUrgenciesRequestQuery(include=include, page_number=page_number, page_size=page_size, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_alert_urgencies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/alert_urgencies"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_alert_urgencies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_alert_urgencies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_alert_urgencies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertUrgencies
@mcp.tool()
async def create_alert_urgency(
    type_: Literal["alert_urgencies"] = Field(..., alias="type", description="The resource type identifier, must be set to 'alert_urgencies' to specify the resource being created."),
    name: str = Field(..., description="The display name for this alert urgency level (e.g., 'Critical', 'High', 'Medium', 'Low')."),
    description: str = Field(..., description="A detailed explanation of when this alert urgency level should be used and what it represents."),
    position: int | None = Field(None, description="The display order of this alert urgency relative to others, with lower numbers appearing first. Optional; if not provided, the system will assign a default position."),
) -> dict[str, Any] | ToolResult:
    """Creates a new alert urgency level that can be assigned to alerts. Alert urgencies help categorize and prioritize alerts based on their importance."""

    # Construct request model with validation
    try:
        _request = _models.CreateAlertUrgencyRequest(
            body=_models.CreateAlertUrgencyRequestBody(data=_models.CreateAlertUrgencyRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateAlertUrgencyRequestBodyDataAttributes(name=name, description=description, position=position)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_alert_urgency: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/alert_urgencies"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_alert_urgency")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_alert_urgency", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_alert_urgency",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertUrgencies
@mcp.tool()
async def get_alert_urgency(id_: str = Field(..., alias="id", description="The unique identifier of the alert urgency to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific alert urgency configuration by its unique identifier. Use this to fetch details about how urgent a particular alert level is classified."""

    # Construct request model with validation
    try:
        _request = _models.GetAlertUrgencyRequest(
            path=_models.GetAlertUrgencyRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_alert_urgency: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alert_urgencies/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alert_urgencies/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_alert_urgency")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_alert_urgency", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_alert_urgency",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertUrgencies
@mcp.tool()
async def update_alert_urgency(
    id_: str = Field(..., alias="id", description="The unique identifier of the alert urgency to update."),
    type_: Literal["alert_urgencies"] = Field(..., alias="type", description="The resource type identifier, which must be 'alert_urgencies' to specify this is an alert urgency resource."),
    description: str | None = Field(None, description="A human-readable description of what this alert urgency level represents and when it should be used."),
    position: int | None = Field(None, description="The display order of this alert urgency relative to others, used for sorting in user interfaces."),
) -> dict[str, Any] | ToolResult:
    """Update the properties of a specific alert urgency level, including its description and display position."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAlertUrgencyRequest(
            path=_models.UpdateAlertUrgencyRequestPath(id_=id_),
            body=_models.UpdateAlertUrgencyRequestBody(data=_models.UpdateAlertUrgencyRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateAlertUrgencyRequestBodyDataAttributes(description=description, position=position) if any(v is not None for v in [description, position]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_alert_urgency: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alert_urgencies/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alert_urgencies/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_alert_urgency")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_alert_urgency", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_alert_urgency",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertUrgencies
@mcp.tool()
async def delete_alert_urgency(id_: str = Field(..., alias="id", description="The unique identifier of the alert urgency to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a specific alert urgency by its unique identifier. This operation permanently removes the alert urgency configuration from the system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAlertUrgencyRequest(
            path=_models.DeleteAlertUrgencyRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_alert_urgency: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alert_urgencies/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alert_urgencies/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_alert_urgency")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_alert_urgency", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_alert_urgency",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertSources
@mcp.tool()
async def list_alert_sources(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., configuration details, metadata)."),
    page_number: int | None = Field(None, alias="pagenumber", description="Page number for pagination, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of alert sources to return per page. Defines the maximum results in each paginated response."),
    filter_statuses: str | None = Field(None, alias="filterstatuses", description="Comma-separated list of alert source statuses to filter by (e.g., active, inactive, disabled)."),
    filter_source_types: str | None = Field(None, alias="filtersource_types", description="Comma-separated list of source types to filter by (e.g., webhook, email, api, monitoring_tool)."),
    sort: str | None = Field(None, description="Field name and direction to sort results by, formatted as field_name or field_name:asc/desc (e.g., created_at:desc)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of alert sources with optional filtering by status and source type, and customizable sorting."""

    # Construct request model with validation
    try:
        _request = _models.ListAlertsSourcesRequest(
            query=_models.ListAlertsSourcesRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_statuses=filter_statuses, filter_source_types=filter_source_types, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_alert_sources: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/alert_sources"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_alert_sources")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_alert_sources", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_alert_sources",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertSources
@mcp.tool()
async def create_alert_source(
    type_: Literal["alert_sources"] = Field(..., alias="type", description="The resource type identifier; must be set to 'alert_sources'."),
    name: str = Field(..., description="A human-readable name for this alert source to identify it in your system."),
    source_type: Literal["email", "app_dynamics", "catchpoint", "datadog", "alertmanager", "google_cloud", "grafana", "sentry", "generic_webhook", "cloud_watch", "checkly", "azure", "new_relic", "splunk", "chronosphere", "app_optics", "bug_snag", "honeycomb", "monte_carlo", "nagios", "prtg"] | None = Field(None, description="The monitoring or alerting platform this source integrates with, such as Datadog, Grafana, PagerDuty, or a generic webhook. Choose from supported integrations like email, app_dynamics, catchpoint, datadog, alertmanager, google_cloud, grafana, sentry, generic_webhook, cloud_watch, checkly, azure, new_relic, splunk, chronosphere, app_optics, bug_snag, honeycomb, monte_carlo, nagios, or prtg."),
    alert_urgency_id: str | None = Field(None, description="The default urgency level assigned to alerts from this source. Specify the urgency ID to set baseline severity for incoming alerts."),
    owner_group_ids: list[str] | None = Field(None, description="One or more team IDs that will own and manage this alert source. Ownership determines who can modify the source configuration and handle its alerts."),
    title: str | None = Field(None, description="A short title displayed for alerts originating from this source."),
    description: str | None = Field(None, description="A detailed explanation of the alert source's purpose and configuration."),
    external_url: str | None = Field(None, description="A URL link to the external system or dashboard where the alert originated, providing context and traceability."),
    alert_source_urgency_rules_attributes: list[_models.CreateAlertsSourceBodyDataAttributesAlertSourceUrgencyRulesAttributesItem] | None = Field(None, description="An ordered list of rules that automatically assign urgency levels to alerts based on conditions evaluated against the alert payload. Rules are evaluated in sequence; the first matching rule determines the alert's urgency."),
    auto_resolve: bool | None = Field(None, description="Enable automatic resolution of alerts when conditions defined in field_mappings_attributes are met. Set to true to automatically close alerts based on payload matching."),
    resolve_state: str | None = Field(None, description="The expected value in the alert payload that indicates an alert should be resolved. This value is extracted using the JSON path specified in field_mappings_attributes and compared to determine if auto-resolution should trigger."),
    accept_threaded_emails: bool | None = Field(None, description="Set to false to reject email alerts that are part of a threaded conversation. By default, threaded emails are accepted."),
    field_mappings_attributes: list[_models.CreateAlertsSourceBodyDataAttributesSourceableAttributesFieldMappingsAttributesItem] | None = Field(None, description="An ordered list of field mapping rules that extract data from alert payloads and define conditions for auto-resolving alerts. Each mapping specifies how to identify and match alerts for resolution."),
    enabled: bool | None = Field(None, description="Set to true to activate the auto-resolution rule. When false, the rule is defined but not applied to incoming alerts."),
    condition_type: Literal["all", "any"] | None = Field(None, description="Determines how multiple conditions are evaluated: 'all' requires all conditions to be true, 'any' requires at least one condition to be true."),
    identifier_matchable_type: Literal["AlertField"] | None = Field(None, description="The type of object being referenced for alert identification. Currently supports 'AlertField' to reference a predefined alert field."),
    identifier_matchable_id: str | None = Field(None, description="The unique identifier of the object specified in identifier_matchable_type. When the type is 'AlertField', this is the ID of the alert field used for matching."),
    identifier_reference_kind: Literal["payload", "alert_field"] | None = Field(None, description="Specifies where the identifier value comes from: 'payload' extracts it directly from the alert JSON, 'alert_field' references a predefined alert field."),
    identifier_json_path: str | None = Field(None, description="A JSON path expression (e.g., $.alert.id or $.incident.key) that extracts the unique identifier from the alert payload. This identifier is used to correlate triggered alerts with their corresponding resolve alerts."),
    identifier_value_regex: str | None = Field(None, description="A regular expression pattern with capture groups to extract a specific portion of the identifier string. Use this to refine the identifier when the full extracted value contains extra characters."),
    conditions_attributes: list[_models.CreateAlertsSourceBodyDataAttributesResolutionRuleAttributesConditionsAttributesItem] | None = Field(None, description="An ordered list of conditions that must be evaluated to determine if an alert qualifies for auto-resolution. Conditions are combined using the logic specified in condition_type."),
    alert_source_fields_attributes: list[_models.CreateAlertsSourceBodyDataAttributesAlertSourceFieldsAttributesItem] | None = Field(None, description="An ordered list of custom alert fields to be created and associated with this alert source. These fields can be used for field mappings, urgency rules, and alert enrichment."),
) -> dict[str, Any] | ToolResult:
    """Creates a new alert source to receive and process alerts from external monitoring systems. Configure the source type, auto-resolution rules, field mappings, and ownership to integrate alerts into your incident management workflow."""

    # Construct request model with validation
    try:
        _request = _models.CreateAlertsSourceRequest(
            body=_models.CreateAlertsSourceRequestBody(data=_models.CreateAlertsSourceRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateAlertsSourceRequestBodyDataAttributes(
                        name=name, source_type=source_type, alert_urgency_id=alert_urgency_id, owner_group_ids=owner_group_ids, alert_source_urgency_rules_attributes=alert_source_urgency_rules_attributes, alert_source_fields_attributes=alert_source_fields_attributes,
                        alert_template_attributes=_models.CreateAlertsSourceRequestBodyDataAttributesAlertTemplateAttributes(title=title, description=description, external_url=external_url) if any(v is not None for v in [title, description, external_url]) else None,
                        sourceable_attributes=_models.CreateAlertsSourceRequestBodyDataAttributesSourceableAttributes(auto_resolve=auto_resolve, resolve_state=resolve_state, accept_threaded_emails=accept_threaded_emails, field_mappings_attributes=field_mappings_attributes) if any(v is not None for v in [auto_resolve, resolve_state, accept_threaded_emails, field_mappings_attributes]) else None,
                        resolution_rule_attributes=_models.CreateAlertsSourceRequestBodyDataAttributesResolutionRuleAttributes(enabled=enabled, condition_type=condition_type, identifier_matchable_type=identifier_matchable_type, identifier_matchable_id=identifier_matchable_id, identifier_reference_kind=identifier_reference_kind, identifier_json_path=identifier_json_path, identifier_value_regex=identifier_value_regex, conditions_attributes=conditions_attributes) if any(v is not None for v in [enabled, condition_type, identifier_matchable_type, identifier_matchable_id, identifier_reference_kind, identifier_json_path, identifier_value_regex, conditions_attributes]) else None
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_alert_source: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/alert_sources"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_alert_source")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_alert_source", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_alert_source",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertSources
@mcp.tool()
async def get_alert_source(id_: str = Field(..., alias="id", description="The unique identifier of the alert source to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific alert source by its unique identifier. Use this to fetch detailed configuration and settings for a particular alert source."""

    # Construct request model with validation
    try:
        _request = _models.GetAlertsSourceRequest(
            path=_models.GetAlertsSourceRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_alert_source: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alert_sources/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alert_sources/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_alert_source")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_alert_source", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_alert_source",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertSources
@mcp.tool()
async def update_alert_source(
    id_: str = Field(..., alias="id", description="The unique identifier of the alert source to update."),
    type_: Literal["alert_sources"] = Field(..., alias="type", description="The resource type identifier; must be set to 'alert_sources'."),
    source_type: Literal["email", "app_dynamics", "catchpoint", "datadog", "alertmanager", "google_cloud", "grafana", "sentry", "generic_webhook", "cloud_watch", "checkly", "azure", "new_relic", "splunk", "chronosphere", "app_optics", "bug_snag", "honeycomb", "monte_carlo", "nagios", "prtg"] | None = Field(None, description="The integration type for this alert source. Choose from supported platforms including email, monitoring tools (Datadog, New Relic, Grafana), cloud providers (AWS CloudWatch, Azure, Google Cloud), and webhook-based integrations."),
    alert_urgency_id: str | None = Field(None, description="The ID of the default urgency level to assign to alerts from this source when no urgency rules apply."),
    owner_group_ids: list[str] | None = Field(None, description="List of team IDs that will have ownership and management permissions for this alert source."),
    title: str | None = Field(None, description="A human-readable name for the alert source."),
    description: str | None = Field(None, description="A detailed explanation of the alert source's purpose and configuration."),
    external_url: str | None = Field(None, description="The external URL where alerts from this source can be viewed or managed in the originating system."),
    alert_source_urgency_rules_attributes: list[_models.UpdateAlertsSourceBodyDataAttributesAlertSourceUrgencyRulesAttributesItem] | None = Field(None, description="Array of urgency assignment rules that automatically set alert urgency based on conditions extracted from the alert payload. Rules are evaluated in order."),
    auto_resolve: bool | None = Field(None, description="Enable automatic resolution of alerts when matching resolve conditions are detected in incoming alert payloads."),
    resolve_state: str | None = Field(None, description="The expected value in the alert payload that indicates an alert should be resolved. This value is extracted using the JSON path specified in field mappings."),
    accept_threaded_emails: bool | None = Field(None, description="Set to false to reject email alerts that are part of threaded conversations; set to true to accept them."),
    field_mappings_attributes: list[_models.UpdateAlertsSourceBodyDataAttributesSourceableAttributesFieldMappingsAttributesItem] | None = Field(None, description="Array of field mapping rules that define how to extract values from alert payloads for matching, resolution, and identifier extraction."),
    enabled: bool | None = Field(None, description="Set to true to enable the auto-resolution rule; set to false to disable it."),
    condition_type: Literal["all", "any"] | None = Field(None, description="Determines how multiple conditions are evaluated: 'all' requires all conditions to be true, 'any' requires at least one condition to be true."),
    identifier_json_path: str | None = Field(None, description="A JSON path expression used to extract the unique identifier from alert payloads for matching triggered alerts with their corresponding resolve alerts."),
    identifier_value_regex: str | None = Field(None, description="A regex pattern with capture groups to extract a specific portion of the identifier value for more precise matching."),
    identifier_matchable_type: Literal["AlertField"] | None = Field(None, description="The type of object being referenced for identifier matching; currently supports 'AlertField'."),
    identifier_matchable_id: str | None = Field(None, description="The ID of the referenced object. When identifier_matchable_type is 'AlertField', this is the ID of the alert field definition."),
    identifier_reference_kind: Literal["payload", "alert_field"] | None = Field(None, description="Specifies whether the identifier is extracted from the raw alert payload or from a predefined alert field: 'payload' for direct JSON extraction, 'alert_field' for field-based extraction."),
    conditions_attributes: list[_models.UpdateAlertsSourceBodyDataAttributesResolutionRuleAttributesConditionsAttributesItem] | None = Field(None, description="Array of conditions that must be satisfied for auto-resolution to trigger. Each condition specifies a field, operator, and expected value."),
    alert_source_fields_attributes: list[_models.UpdateAlertsSourceBodyDataAttributesAlertSourceFieldsAttributesItem] | None = Field(None, description="Array of custom alert fields to be created or associated with this alert source for enhanced alert enrichment and filtering."),
) -> dict[str, Any] | ToolResult:
    """Update an existing alert source configuration, including its type, routing rules, auto-resolution settings, and field mappings. This operation allows you to modify how alerts are ingested, processed, and automatically resolved."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAlertsSourceRequest(
            path=_models.UpdateAlertsSourceRequestPath(id_=id_),
            body=_models.UpdateAlertsSourceRequestBody(data=_models.UpdateAlertsSourceRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateAlertsSourceRequestBodyDataAttributes(source_type=source_type, alert_urgency_id=alert_urgency_id, owner_group_ids=owner_group_ids, alert_source_urgency_rules_attributes=alert_source_urgency_rules_attributes, alert_source_fields_attributes=alert_source_fields_attributes,
                        alert_template_attributes=_models.UpdateAlertsSourceRequestBodyDataAttributesAlertTemplateAttributes(title=title, description=description, external_url=external_url) if any(v is not None for v in [title, description, external_url]) else None,
                        sourceable_attributes=_models.UpdateAlertsSourceRequestBodyDataAttributesSourceableAttributes(auto_resolve=auto_resolve, resolve_state=resolve_state, accept_threaded_emails=accept_threaded_emails, field_mappings_attributes=field_mappings_attributes) if any(v is not None for v in [auto_resolve, resolve_state, accept_threaded_emails, field_mappings_attributes]) else None,
                        resolution_rule_attributes=_models.UpdateAlertsSourceRequestBodyDataAttributesResolutionRuleAttributes(enabled=enabled, condition_type=condition_type, identifier_json_path=identifier_json_path, identifier_value_regex=identifier_value_regex, identifier_matchable_type=identifier_matchable_type, identifier_matchable_id=identifier_matchable_id, identifier_reference_kind=identifier_reference_kind, conditions_attributes=conditions_attributes) if any(v is not None for v in [enabled, condition_type, identifier_json_path, identifier_value_regex, identifier_matchable_type, identifier_matchable_id, identifier_reference_kind, conditions_attributes]) else None) if any(v is not None for v in [source_type, alert_urgency_id, owner_group_ids, title, description, external_url, alert_source_urgency_rules_attributes, auto_resolve, resolve_state, accept_threaded_emails, field_mappings_attributes, enabled, condition_type, identifier_json_path, identifier_value_regex, identifier_matchable_type, identifier_matchable_id, identifier_reference_kind, conditions_attributes, alert_source_fields_attributes]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_alert_source: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alert_sources/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alert_sources/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_alert_source")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_alert_source", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_alert_source",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: AlertSources
@mcp.tool()
async def delete_alert_source(id_: str = Field(..., alias="id", description="The unique identifier of the alert source to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific alert source by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAlertsSourceRequest(
            path=_models.DeleteAlertsSourceRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_alert_source: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alert_sources/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alert_sources/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_alert_source")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_alert_source", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_alert_source",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Alerts
@mcp.tool()
async def list_incident_alerts(
    incident_id: str = Field(..., description="The unique identifier of the incident for which to retrieve alerts."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., incident details, source metadata)."),
    filter_source: str | None = Field(None, alias="filtersource", description="Filter alerts by their source system or origin (e.g., monitoring tool, integration name)."),
    filter_groups: str | None = Field(None, alias="filtergroups", description="Filter alerts by one or more group identifiers. Specify as comma-separated values to match alerts in any of the specified groups."),
    filter_labels: str | None = Field(None, alias="filterlabels", description="Filter alerts by one or more label keys or key-value pairs. Specify as comma-separated values to match alerts with any of the specified labels."),
    filter_started_at__gte: str | None = Field(None, alias="filterstarted_atgte", description="Filter alerts by start time (inclusive). Specify as an ISO 8601 timestamp to include only alerts that started at or after this time."),
    filter_started_at__lte: str | None = Field(None, alias="filterstarted_atlte", description="Filter alerts by start time (inclusive). Specify as an ISO 8601 timestamp to include only alerts that started at or before this time."),
    filter_ended_at__gte: str | None = Field(None, alias="filterended_atgte", description="Filter alerts by end time (inclusive). Specify as an ISO 8601 timestamp to include only alerts that ended at or after this time."),
    filter_ended_at__lte: str | None = Field(None, alias="filterended_atlte", description="Filter alerts by end time (inclusive). Specify as an ISO 8601 timestamp to include only alerts that ended at or before this time."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page size to retrieve specific result sets."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of alerts to return per page. Adjust to control result set size for pagination."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of alerts associated with a specific incident. Supports filtering by source, groups, labels, and time ranges to narrow results."""

    # Construct request model with validation
    try:
        _request = _models.ListIncidentAlertsRequest(
            path=_models.ListIncidentAlertsRequestPath(incident_id=incident_id),
            query=_models.ListIncidentAlertsRequestQuery(include=include, filter_source=filter_source, filter_groups=filter_groups, filter_labels=filter_labels, filter_started_at__gte=filter_started_at__gte, filter_started_at__lte=filter_started_at__lte, filter_ended_at__gte=filter_ended_at__gte, filter_ended_at__lte=filter_ended_at__lte, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_incident_alerts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{incident_id}/alerts", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{incident_id}/alerts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_incident_alerts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_incident_alerts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_incident_alerts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Alerts
@mcp.tool()
async def attach_alerts_to_incident(
    incident_id: str = Field(..., description="The unique identifier of the incident to which alerts will be attached."),
    type_: Literal["alerts"] = Field(..., alias="type", description="The resource type being attached, which must be 'alerts' to specify that alert resources are being linked to this incident."),
    alert_ids: list[str] = Field(..., description="An array of alert identifiers to attach to the incident. Each ID references an existing alert that will be linked to this incident."),
) -> dict[str, Any] | ToolResult:
    """Attach one or more alerts to an incident. This operation links existing alerts to an incident record for consolidated monitoring and tracking."""

    # Construct request model with validation
    try:
        _request = _models.AttachAlertRequest(
            path=_models.AttachAlertRequestPath(incident_id=incident_id),
            body=_models.AttachAlertRequestBody(data=_models.AttachAlertRequestBodyData(
                    type_=type_,
                    attributes=_models.AttachAlertRequestBodyDataAttributes(alert_ids=alert_ids)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for attach_alerts_to_incident: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{incident_id}/alerts", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{incident_id}/alerts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("attach_alerts_to_incident")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("attach_alerts_to_incident", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="attach_alerts_to_incident",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Alerts
@mcp.tool()
async def list_alerts(
    include: str | None = Field(None, description="Comma-separated list of fields to include in the response. Specify which alert properties should be returned to optimize payload size."),
    filter_status: str | None = Field(None, alias="filterstatus", description="Filter alerts by their current status (e.g., active, resolved, acknowledged). Only alerts matching the specified status will be returned."),
    page_number: int | None = Field(None, alias="pagenumber", description="Page number for pagination, starting from 1. Use this to navigate through multiple pages of results."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of alerts to return per page. Controls the size of each paginated response."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of alerts with optional filtering by status and field inclusion. Use this to monitor and review all alerts in the system."""

    # Construct request model with validation
    try:
        _request = _models.ListAlertsRequest(
            query=_models.ListAlertsRequestQuery(include=include, filter_status=filter_status, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_alerts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/alerts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_alerts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_alerts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_alerts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Alerts
@mcp.tool()
async def create_alert(
    type_: Literal["alerts"] = Field(..., alias="type", description="The alert type; must be 'alerts' to indicate this is an alert resource."),
    source: Literal["rootly", "manual", "api", "web", "slack", "email", "workflow", "live_call_routing", "pagerduty", "opsgenie", "victorops", "pagertree", "datadog", "nobl9", "zendesk", "asana", "clickup", "sentry", "rollbar", "jira", "honeycomb", "service_now", "linear", "grafana", "alertmanager", "google_cloud", "generic_webhook", "cloud_watch", "azure", "splunk", "chronosphere", "app_optics", "bug_snag", "monte_carlo", "nagios", "prtg", "catchpoint", "app_dynamics", "checkly", "new_relic", "gitlab"] = Field(..., description="The origin system or channel that generated the alert, such as monitoring tools (Datadog, Grafana, New Relic), incident platforms (PagerDuty, OpsGenie), ticketing systems (Jira, Linear), or manual/API entry."),
    summary: str = Field(..., description="A brief, descriptive title for the alert that summarizes the incident or issue."),
    noise: Literal["noise", "not_noise"] | None = Field(None, description="Marks whether the alert should be classified as noise or legitimate; use 'noise' to suppress or 'not_noise' to treat as actionable."),
    status: Literal["open", "triggered"] | None = Field(None, description="The alert state; 'open' for active alerts or 'triggered' for alerts that have fired. Only available if your organization has Rootly On-Call enabled."),
    description: str | None = Field(None, description="Extended details about the alert, providing context beyond the summary."),
    service_ids: list[str] | None = Field(None, description="IDs of services to associate with this alert. Automatically populated if On-Call is enabled and the notification target is a service."),
    group_ids: list[str] | None = Field(None, description="IDs of groups to associate with this alert. Automatically populated if On-Call is enabled and the notification target is a group."),
    environment_ids: list[str] | None = Field(None, description="IDs of environments where this alert applies, such as production, staging, or development."),
    ended_at: str | None = Field(None, description="The date and time when the alert resolved or ended, in ISO 8601 format."),
    external_id: str | None = Field(None, description="An external identifier to correlate this alert with systems outside Rootly, enabling deduplication and cross-system tracking."),
    external_url: str | None = Field(None, description="A URL linking to the external system or dashboard where the alert originated or can be viewed."),
    alert_urgency_id: str | None = Field(None, description="The ID of the alert urgency level, determining priority and escalation behavior."),
    notification_target_type: Literal["User", "Group", "EscalationPolicy", "Service"] | None = Field(None, description="The type of on-call target to notify: a user, group, escalation policy, or service. Only available if your organization has Rootly On-Call enabled."),
    notification_target_id: str | None = Field(None, description="The identifier of the specific on-call target (user, group, escalation policy, or service) to notify. Only available if your organization has Rootly On-Call enabled."),
    data: dict[str, Any] | None = Field(None, description="A flexible object for storing additional custom metadata or attributes associated with the alert."),
) -> dict[str, Any] | ToolResult:
    """Creates a new alert in the system with details about the incident source, status, and affected services. Automatically associates the alert with services or groups if On-Call is enabled and a notification target is specified."""

    # Construct request model with validation
    try:
        _request = _models.CreateAlertRequest(
            body=_models.CreateAlertRequestBody(data=_models.CreateAlertRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateAlertRequestBodyDataAttributes(noise=noise, source=source, status=status, summary=summary, description=description, service_ids=service_ids, group_ids=group_ids, environment_ids=environment_ids, ended_at=ended_at, external_id=external_id, external_url=external_url, alert_urgency_id=alert_urgency_id, notification_target_type=notification_target_type, notification_target_id=notification_target_id, data=data)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_alert: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/alerts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_alert")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_alert", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_alert",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Alerts
@mcp.tool()
async def get_alert(id_: str = Field(..., alias="id", description="The unique identifier of the alert to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific alert by its unique identifier. Use this operation to fetch detailed information about a single alert."""

    # Construct request model with validation
    try:
        _request = _models.GetAlertRequest(
            path=_models.GetAlertRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_alert: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alerts/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alerts/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_alert")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_alert", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_alert",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Alerts
@mcp.tool()
async def update_alert(
    id_: str = Field(..., alias="id", description="The unique identifier of the alert to update."),
    noise: Literal["noise", "not_noise"] | None = Field(None, description="Mark the alert as noise or not noise to help filter false positives and relevant alerts."),
    source: Literal["rootly", "manual", "api", "web", "slack", "email", "workflow", "live_call_routing", "pagerduty", "opsgenie", "victorops", "pagertree", "datadog", "nobl9", "zendesk", "asana", "clickup", "sentry", "rollbar", "jira", "honeycomb", "service_now", "linear", "grafana", "alertmanager", "google_cloud", "generic_webhook", "cloud_watch", "azure", "splunk", "chronosphere", "app_optics", "bug_snag", "monte_carlo", "nagios", "prtg", "catchpoint", "app_dynamics", "checkly", "new_relic", "gitlab"] | None = Field(None, description="The originating system or channel that generated the alert, such as monitoring tools (Datadog, Grafana, New Relic), incident platforms (PagerDuty, OpsGenie), or internal sources (manual, API, web, Slack)."),
    summary: str | None = Field(None, description="A brief title or headline summarizing the alert's primary issue."),
    description: str | None = Field(None, description="Detailed information about the alert, including context, symptoms, or troubleshooting steps."),
    service_ids: list[str] | None = Field(None, description="List of service identifiers to associate with this alert, linking it to specific services or applications."),
    group_ids: list[str] | None = Field(None, description="List of group identifiers to associate with this alert, linking it to specific teams or organizational groups."),
    environment_ids: list[str] | None = Field(None, description="List of environment identifiers to associate with this alert, such as production, staging, or development."),
    ended_at: str | None = Field(None, description="The date and time when the alert should be marked as resolved or ended, in ISO 8601 format."),
    external_id: str | None = Field(None, description="An external identifier from the source system, useful for tracking and deduplication across integrations."),
    external_url: str | None = Field(None, description="A URL pointing to the original alert or related resource in the source system for quick reference."),
    alert_urgency_id: str | None = Field(None, description="The identifier of the alert urgency level, determining the priority and severity classification of the alert."),
    data: dict[str, Any] | None = Field(None, description="Custom metadata or additional structured data associated with the alert for extensibility and integration purposes."),
) -> dict[str, Any] | ToolResult:
    """Update an existing alert with new metadata, classifications, or associations. Modify alert properties such as noise status, summary, description, urgency, and linked resources."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAlertRequest(
            path=_models.UpdateAlertRequestPath(id_=id_),
            body=_models.UpdateAlertRequestBody(data=_models.UpdateAlertRequestBodyData(attributes=_models.UpdateAlertRequestBodyDataAttributes(noise=noise, source=source, summary=summary, description=description, service_ids=service_ids, group_ids=group_ids, environment_ids=environment_ids, ended_at=ended_at, external_id=external_id, external_url=external_url, alert_urgency_id=alert_urgency_id, data=data) if any(v is not None for v in [noise, source, summary, description, service_ids, group_ids, environment_ids, ended_at, external_id, external_url, alert_urgency_id, data]) else None) if any(v is not None for v in [noise, source, summary, description, service_ids, group_ids, environment_ids, ended_at, external_id, external_url, alert_urgency_id, data]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_alert: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alerts/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alerts/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_alert")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_alert", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_alert",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Alerts
@mcp.tool()
async def acknowledge_alert(id_: str = Field(..., alias="id", description="The unique identifier of the alert to acknowledge.")) -> dict[str, Any] | ToolResult:
    """Marks a specific alert as acknowledged, indicating that it has been reviewed and noted by the user."""

    # Construct request model with validation
    try:
        _request = _models.AcknowledgeAlertRequest(
            path=_models.AcknowledgeAlertRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for acknowledge_alert: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alerts/{id}/acknowledge", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alerts/{id}/acknowledge"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("acknowledge_alert")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("acknowledge_alert", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="acknowledge_alert",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Alerts
@mcp.tool()
async def resolve_alert(
    id_: str = Field(..., alias="id", description="The unique identifier of the alert to resolve."),
    resolution_message: str | None = Field(None, description="Optional explanation describing how or why the alert was resolved."),
    resolve_related_incidents: bool | None = Field(None, description="When true, resolves all incidents associated with this alert in addition to the alert itself."),
) -> dict[str, Any] | ToolResult:
    """Resolves a specific alert and optionally its associated incidents. Use this operation to mark an alert as resolved with an optional explanation of how it was addressed."""

    # Construct request model with validation
    try:
        _request = _models.ResolveAlertRequest(
            path=_models.ResolveAlertRequestPath(id_=id_),
            body=_models.ResolveAlertRequestBody(data=_models.ResolveAlertRequestBodyData(attributes=_models.ResolveAlertRequestBodyDataAttributes(resolution_message=resolution_message, resolve_related_incidents=resolve_related_incidents) if any(v is not None for v in [resolution_message, resolve_related_incidents]) else None) if any(v is not None for v in [resolution_message, resolve_related_incidents]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for resolve_alert: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/alerts/{id}/resolve", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/alerts/{id}/resolve"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("resolve_alert")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("resolve_alert", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="resolve_alert",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Audits
@mcp.tool()
async def list_audits(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., user details, API key information)."),
    page_number: int | None = Field(None, alias="pagenumber", description="Page number for pagination, starting from 1. Use with page[size] to control result set boundaries."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of audit records to return per page. Determines the maximum results in each paginated response."),
    filter_user_id: str | None = Field(None, alias="filteruser_id", description="Filter results to audits performed by a specific user ID."),
    filter_api_key_id: str | None = Field(None, alias="filterapi_key_id", description="Filter results to audits associated with a specific API key ID."),
    filter_source: str | None = Field(None, alias="filtersource", description="Filter results by the source of the audit action (e.g., api, dashboard, webhook)."),
    filter_item_type: str | None = Field(None, alias="filteritem_type", description="Filter results by the type of item that was audited (e.g., user, api_key, organization)."),
    sort: str | None = Field(None, description="Sort results by a specified field in ascending or descending order (format: field or -field for descending)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of audit logs with optional filtering by user, API key, source, or item type, and configurable sorting."""

    # Construct request model with validation
    try:
        _request = _models.ListAuditsRequest(
            query=_models.ListAuditsRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_user_id=filter_user_id, filter_api_key_id=filter_api_key_id, filter_source=filter_source, filter_item_type=filter_item_type, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_audits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/audits"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_audits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_audits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_audits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Authorizations
@mcp.tool()
async def get_authorization(id_: str = Field(..., alias="id", description="The unique identifier of the authorization to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific authorization by its unique identifier. Use this to fetch details about an existing authorization."""

    # Construct request model with validation
    try:
        _request = _models.GetAuthorizationRequest(
            path=_models.GetAuthorizationRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_authorization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/authorizations/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/authorizations/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_authorization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_authorization", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_authorization",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Authorizations
@mcp.tool()
async def delete_authorization(id_: str = Field(..., alias="id", description="The unique identifier of the authorization to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific authorization by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAuthorizationRequest(
            path=_models.DeleteAuthorizationRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_authorization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/authorizations/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/authorizations/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_authorization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_authorization", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_authorization",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: CatalogEntities
@mcp.tool()
async def list_catalog_entities(
    catalog_id: str = Field(..., description="The unique identifier of the catalog containing the entities to list."),
    include: Literal["catalog", "properties"] | None = Field(None, description="Comma-separated list of related data to include in the response. Options are 'catalog' (parent catalog details) and 'properties' (entity properties)."),
    sort: Literal["created_at", "-created_at", "updated_at", "-updated_at", "position", "-position"] | None = Field(None, description="Comma-separated list of fields to sort results by. Use 'created_at' or 'updated_at' for chronological sorting, 'position' for custom ordering. Prefix with '-' for descending order (e.g., '-created_at' for newest first)."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of entities to return per page. Use with page[number] to control result set size."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of entities within a specific catalog, with optional filtering to include related catalog and property information."""

    # Construct request model with validation
    try:
        _request = _models.ListCatalogEntitiesRequest(
            path=_models.ListCatalogEntitiesRequestPath(catalog_id=catalog_id),
            query=_models.ListCatalogEntitiesRequestQuery(include=include, sort=sort, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_catalog_entities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalogs/{catalog_id}/entities", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalogs/{catalog_id}/entities"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_catalog_entities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_catalog_entities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_catalog_entities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: CatalogEntities
@mcp.tool()
async def create_catalog_entity(
    catalog_id: str = Field(..., description="The unique identifier of the catalog where the entity will be created."),
    type_: Literal["catalog_entities"] = Field(..., alias="type", description="The type classification for this entity. Must be set to 'catalog_entities'."),
    name: str = Field(..., description="The display name for the catalog entity."),
    description: str | None = Field(None, description="A detailed explanation or summary of the catalog entity's purpose and content."),
    position: int | None = Field(None, description="The default ordering position for this entity when displayed in a list view. Lower values appear first."),
) -> dict[str, Any] | ToolResult:
    """Creates a new catalog entity with the specified metadata. The entity will be added to the catalog and can be positioned within list displays."""

    # Construct request model with validation
    try:
        _request = _models.CreateCatalogEntityRequest(
            path=_models.CreateCatalogEntityRequestPath(catalog_id=catalog_id),
            body=_models.CreateCatalogEntityRequestBody(data=_models.CreateCatalogEntityRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateCatalogEntityRequestBodyDataAttributes(name=name, description=description, position=position)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_catalog_entity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalogs/{catalog_id}/entities", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalogs/{catalog_id}/entities"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_catalog_entity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_catalog_entity", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_catalog_entity",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: CatalogEntities
@mcp.tool()
async def get_catalog_entity(
    id_: str = Field(..., alias="id", description="The unique identifier of the Catalog Entity to retrieve."),
    include: Literal["catalog", "properties"] | None = Field(None, description="Optional comma-separated list of related data to include in the response. Valid options are 'catalog' (to include parent catalog information) and 'properties' (to include entity properties)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific Catalog Entity by its unique identifier, with optional inclusion of related catalog and properties data."""

    # Construct request model with validation
    try:
        _request = _models.GetCatalogEntityRequest(
            path=_models.GetCatalogEntityRequestPath(id_=id_),
            query=_models.GetCatalogEntityRequestQuery(include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_catalog_entity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalog_entities/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalog_entities/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_catalog_entity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_catalog_entity", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_catalog_entity",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: CatalogEntities
@mcp.tool()
async def update_catalog_entity(
    id_: str = Field(..., alias="id", description="The unique identifier of the Catalog Entity to update."),
    type_: Literal["catalog_entities"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'catalog_entities' to specify this is a Catalog Entity resource."),
    description: str | None = Field(None, description="A text description of the Catalog Entity. Provides additional context or details about the entity."),
    position: int | None = Field(None, description="The default position (order) in which this item appears when displayed in a list. Lower numbers appear first."),
) -> dict[str, Any] | ToolResult:
    """Update an existing Catalog Entity by its unique identifier. Modify the entity's description and display position within catalog lists."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCatalogEntityRequest(
            path=_models.UpdateCatalogEntityRequestPath(id_=id_),
            body=_models.UpdateCatalogEntityRequestBody(data=_models.UpdateCatalogEntityRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateCatalogEntityRequestBodyDataAttributes(description=description, position=position) if any(v is not None for v in [description, position]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_catalog_entity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalog_entities/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalog_entities/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_catalog_entity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_catalog_entity", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_catalog_entity",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: CatalogEntities
@mcp.tool()
async def delete_catalog_entity(id_: str = Field(..., alias="id", description="The unique identifier of the Catalog Entity to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific Catalog Entity by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCatalogEntityRequest(
            path=_models.DeleteCatalogEntityRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_catalog_entity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalog_entities/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalog_entities/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_catalog_entity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_catalog_entity", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_catalog_entity",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: CatalogEntityProperties
@mcp.tool()
async def list_catalog_entity_properties(
    catalog_entity_id: str = Field(..., description="The unique identifier of the catalog entity whose properties you want to list."),
    include: Literal["catalog_entity", "catalog_field"] | None = Field(None, description="Comma-separated list of related entities to include in the response. Valid options are 'catalog_entity' and 'catalog_field'."),
    sort: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Field(None, description="Comma-separated list of fields to sort results by. Use 'created_at' or 'updated_at' for ascending order, or prefix with '-' for descending order (e.g., '-created_at')."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination (1-indexed). Use with page[size] to retrieve specific result pages."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of results per page for pagination. Defines how many properties are returned in each page."),
    filter_catalog_field_id: str | None = Field(None, alias="filtercatalog_field_id", description="Filter results by catalog field ID to return only properties associated with a specific field."),
    filter_key: str | None = Field(None, alias="filterkey", description="Filter results by property key to find properties matching a specific key name."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of properties for a specific catalog entity, with optional filtering, sorting, and related entity inclusion."""

    # Construct request model with validation
    try:
        _request = _models.ListCatalogEntityPropertiesRequest(
            path=_models.ListCatalogEntityPropertiesRequestPath(catalog_entity_id=catalog_entity_id),
            query=_models.ListCatalogEntityPropertiesRequestQuery(include=include, sort=sort, page_number=page_number, page_size=page_size, filter_catalog_field_id=filter_catalog_field_id, filter_key=filter_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_catalog_entity_properties: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalog_entities/{catalog_entity_id}/properties", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalog_entities/{catalog_entity_id}/properties"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_catalog_entity_properties")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_catalog_entity_properties", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_catalog_entity_properties",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: CatalogEntityProperties
@mcp.tool()
async def create_catalog_entity_property(
    catalog_entity_id: str = Field(..., description="The unique identifier of the catalog entity to which this property will be added."),
    type_: Literal["catalog_entity_properties"] = Field(..., alias="type", description="The resource type identifier for this operation, which must be 'catalog_entity_properties'."),
    catalog_field_id: str = Field(..., description="The unique identifier of the catalog field that this property references."),
    key: Literal["text", "catalog_entity"] = Field(..., description="The property key type, which determines the value format: 'text' for string values or 'catalog_entity' for entity references."),
    value: str = Field(..., description="The property value, formatted according to the specified key type (plain text for 'text' keys, entity identifier for 'catalog_entity' keys)."),
) -> dict[str, Any] | ToolResult:
    """Creates a new property for a catalog entity, associating a catalog field with a typed value. This establishes a key-value relationship within the catalog entity's property structure."""

    # Construct request model with validation
    try:
        _request = _models.CreateCatalogEntityPropertyRequest(
            path=_models.CreateCatalogEntityPropertyRequestPath(catalog_entity_id=catalog_entity_id),
            body=_models.CreateCatalogEntityPropertyRequestBody(data=_models.CreateCatalogEntityPropertyRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateCatalogEntityPropertyRequestBodyDataAttributes(catalog_field_id=catalog_field_id, key=key, value=value)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_catalog_entity_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalog_entities/{catalog_entity_id}/properties", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalog_entities/{catalog_entity_id}/properties"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_catalog_entity_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_catalog_entity_property", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_catalog_entity_property",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: CatalogEntityProperties
@mcp.tool()
async def get_catalog_entity_property(
    id_: str = Field(..., alias="id", description="The unique identifier of the Catalog Entity Property to retrieve."),
    include: Literal["catalog_entity", "catalog_field"] | None = Field(None, description="Comma-separated list of related resources to include in the response. Valid options are 'catalog_entity' and 'catalog_field'."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific Catalog Entity Property by its unique identifier. Optionally include related Catalog Entity or Catalog Field data in the response."""

    # Construct request model with validation
    try:
        _request = _models.GetCatalogEntityPropertyRequest(
            path=_models.GetCatalogEntityPropertyRequestPath(id_=id_),
            query=_models.GetCatalogEntityPropertyRequestQuery(include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_catalog_entity_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalog_entity_properties/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalog_entity_properties/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_catalog_entity_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_catalog_entity_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_catalog_entity_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: CatalogEntityProperties
@mcp.tool()
async def update_catalog_entity_property(
    id_: str = Field(..., alias="id", description="The unique identifier of the catalog entity property to update."),
    type_: Literal["catalog_entity_properties"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'catalog_entity_properties' to specify the entity being updated."),
    key: Literal["text", "catalog_entity"] | None = Field(None, description="The property key type, which determines whether the property stores plain text or references another catalog entity. Valid options are 'text' for string values or 'catalog_entity' for entity references."),
    value: str | None = Field(None, description="The property value to store, formatted according to the specified key type (plain text for 'text' keys, or an entity identifier for 'catalog_entity' keys)."),
) -> dict[str, Any] | ToolResult:
    """Update a specific catalog entity property by its identifier. Modify the property's key type and associated value to reflect changes in how catalog entities are characterized."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCatalogEntityPropertyRequest(
            path=_models.UpdateCatalogEntityPropertyRequestPath(id_=id_),
            body=_models.UpdateCatalogEntityPropertyRequestBody(data=_models.UpdateCatalogEntityPropertyRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateCatalogEntityPropertyRequestBodyDataAttributes(key=key, value=value) if any(v is not None for v in [key, value]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_catalog_entity_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalog_entity_properties/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalog_entity_properties/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_catalog_entity_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_catalog_entity_property", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_catalog_entity_property",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: CatalogEntityProperties
@mcp.tool()
async def delete_catalog_entity_property(id_: str = Field(..., alias="id", description="The unique identifier of the Catalog Entity Property to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific Catalog Entity Property by its unique identifier. This operation removes the property and all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCatalogEntityPropertyRequest(
            path=_models.DeleteCatalogEntityPropertyRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_catalog_entity_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalog_entity_properties/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalog_entity_properties/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_catalog_entity_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_catalog_entity_property", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_catalog_entity_property",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: CatalogFields
@mcp.tool()
async def list_catalog_fields(
    catalog_id: str = Field(..., description="The unique identifier of the catalog whose fields you want to list."),
    include: Literal["catalog"] | None = Field(None, description="Comma-separated list of related resources to include in the response. Use 'catalog' to include the parent catalog data."),
    sort: Literal["created_at", "-created_at", "updated_at", "-updated_at", "position", "-position"] | None = Field(None, description="Comma-separated list of fields to sort by. Prefix with a hyphen (e.g., '-created_at') to sort in descending order. Available fields: created_at, updated_at, and position."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination (1-indexed). Use with page[size] to retrieve specific result pages."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of results per page for pagination. Use with page[number] to control result set size."),
    filter_kind: str | None = Field(None, alias="filterkind", description="Filter results by field kind. Specify the desired field type to narrow the returned fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of fields within a specific catalog. Optionally filter by field kind, include related catalog data, and sort results by creation date, update date, or field position."""

    # Construct request model with validation
    try:
        _request = _models.ListCatalogFieldsRequest(
            path=_models.ListCatalogFieldsRequestPath(catalog_id=catalog_id),
            query=_models.ListCatalogFieldsRequestQuery(include=include, sort=sort, page_number=page_number, page_size=page_size, filter_kind=filter_kind)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_catalog_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalogs/{catalog_id}/fields", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalogs/{catalog_id}/fields"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_catalog_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_catalog_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_catalog_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: CatalogFields
@mcp.tool()
async def create_catalog_field(
    catalog_id: str = Field(..., description="The unique identifier of the catalog where the field will be created."),
    type_: Literal["catalog_fields"] = Field(..., alias="type", description="The resource type identifier; must be set to 'catalog_fields'."),
    name: str = Field(..., description="The display name of the catalog field."),
    kind: Literal["text", "reference"] = Field(..., description="The data type of the field; either 'text' for string values or 'reference' to link to items in another catalog."),
    kind_catalog_id: str | None = Field(None, description="When the field kind is 'reference', specifies which catalog the referenced items must belong to. Required for reference-type fields."),
    multiple: bool | None = Field(None, description="If true, the field can store multiple values; if false or omitted, only a single value is allowed."),
    position: int | None = Field(None, description="The default display order of this field in list views; lower numbers appear first."),
) -> dict[str, Any] | ToolResult:
    """Creates a new field within a catalog to define custom attributes for catalog items. Fields can store text values or references to items in other catalogs, and can be configured to accept single or multiple values."""

    # Construct request model with validation
    try:
        _request = _models.CreateCatalogFieldRequest(
            path=_models.CreateCatalogFieldRequestPath(catalog_id=catalog_id),
            body=_models.CreateCatalogFieldRequestBody(data=_models.CreateCatalogFieldRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateCatalogFieldRequestBodyDataAttributes(name=name, kind=kind, kind_catalog_id=kind_catalog_id, multiple=multiple, position=position)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_catalog_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalogs/{catalog_id}/fields", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalogs/{catalog_id}/fields"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_catalog_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_catalog_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_catalog_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: CatalogFields
@mcp.tool()
async def get_catalog_field(
    id_: str = Field(..., alias="id", description="The unique identifier of the Catalog Field to retrieve."),
    include: Literal["catalog"] | None = Field(None, description="Optional comma-separated list of related resources to include in the response. Specify 'catalog' to include the parent catalog information."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific Catalog Field by its unique identifier. Optionally include related catalog information in the response."""

    # Construct request model with validation
    try:
        _request = _models.GetCatalogFieldRequest(
            path=_models.GetCatalogFieldRequestPath(id_=id_),
            query=_models.GetCatalogFieldRequestQuery(include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_catalog_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalog_fields/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalog_fields/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_catalog_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_catalog_field", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_catalog_field",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: CatalogFields
@mcp.tool()
async def update_catalog_field(
    id_: str = Field(..., alias="id", description="The unique identifier of the catalog field to update."),
    type_: Literal["catalog_fields"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'catalog_fields' to specify this is a catalog field resource."),
    slug: str | None = Field(None, description="A URL-friendly identifier for the catalog field used in references and lookups."),
    kind: Literal["text", "reference"] | None = Field(None, description="The data type of the field. Choose 'text' for string values or 'reference' to link to items in another catalog."),
    kind_catalog_id: str | None = Field(None, description="When kind is set to 'reference', specify the catalog ID to restrict field values to items from that catalog."),
    position: int | None = Field(None, description="The default display order position when this field appears in a list view. Lower numbers appear first."),
) -> dict[str, Any] | ToolResult:
    """Update a specific catalog field by its ID. Modify field properties such as slug, kind, associated catalog reference, and display position."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCatalogFieldRequest(
            path=_models.UpdateCatalogFieldRequestPath(id_=id_),
            body=_models.UpdateCatalogFieldRequestBody(data=_models.UpdateCatalogFieldRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateCatalogFieldRequestBodyDataAttributes(slug=slug, kind=kind, kind_catalog_id=kind_catalog_id, position=position) if any(v is not None for v in [slug, kind, kind_catalog_id, position]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_catalog_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalog_fields/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalog_fields/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_catalog_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_catalog_field", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_catalog_field",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: CatalogFields
@mcp.tool()
async def delete_catalog_field(id_: str = Field(..., alias="id", description="The unique identifier of the catalog field to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a catalog field by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCatalogFieldRequest(
            path=_models.DeleteCatalogFieldRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_catalog_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalog_fields/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalog_fields/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_catalog_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_catalog_field", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_catalog_field",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def list_catalogs(
    include: Literal["fields", "entities"] | None = Field(None, description="Comma-separated list of related data to include in the response. Choose from 'fields' to include field definitions or 'entities' to include entity information."),
    sort: Literal["created_at", "-created_at", "updated_at", "-updated_at", "position", "-position"] | None = Field(None, description="Comma-separated list of fields to sort results by. Use 'created_at', 'updated_at', or 'position' for ascending order, or prefix with a hyphen (e.g., '-created_at') for descending order."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of catalogs to return per page."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of catalogs with optional inclusion of related data and sorting capabilities."""

    # Construct request model with validation
    try:
        _request = _models.ListCatalogsRequest(
            query=_models.ListCatalogsRequestQuery(include=include, sort=sort, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_catalogs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/catalogs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_catalogs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_catalogs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_catalogs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def create_catalog(
    type_: Literal["catalogs"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'catalogs' to indicate this is a catalog resource."),
    name: str = Field(..., description="The display name for the catalog. This is the primary identifier users will see when viewing catalogs."),
    description: str | None = Field(None, description="An optional detailed description of the catalog's purpose or contents."),
    icon: Literal["globe-alt", "server-stack", "users", "user-group", "chart-bar", "shapes", "light-bulb", "cursor-arrow-ripple"] | None = Field(None, description="An optional visual icon to represent the catalog. Choose from predefined icons: globe-alt, server-stack, users, user-group, chart-bar, shapes, light-bulb, or cursor-arrow-ripple."),
    position: int | None = Field(None, description="An optional numeric position that determines the catalog's order when displayed in lists. Lower numbers appear first."),
) -> dict[str, Any] | ToolResult:
    """Creates a new catalog with the specified name, description, and display settings. The catalog will be added to your catalog collection and can be organized with an icon and position."""

    # Construct request model with validation
    try:
        _request = _models.CreateCatalogRequest(
            body=_models.CreateCatalogRequestBody(data=_models.CreateCatalogRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateCatalogRequestBodyDataAttributes(name=name, description=description, icon=icon, position=position)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_catalog: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/catalogs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_catalog")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_catalog", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_catalog",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def get_catalog(id_: str = Field(..., alias="id", description="The unique identifier of the catalog to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific catalog by its unique identifier. Use this operation to fetch detailed information about a catalog."""

    # Construct request model with validation
    try:
        _request = _models.GetCatalogRequest(
            path=_models.GetCatalogRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_catalog: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalogs/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalogs/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_catalog")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_catalog", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_catalog",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def update_catalog(
    id_: str = Field(..., alias="id", description="The unique identifier of the catalog to update."),
    type_: Literal["catalogs"] = Field(..., alias="type", description="The resource type, which must be set to 'catalogs' to identify this as a catalog resource."),
    description: str | None = Field(None, description="A text description of the catalog's purpose or contents."),
    icon: Literal["globe-alt", "server-stack", "users", "user-group", "chart-bar", "shapes", "light-bulb", "cursor-arrow-ripple"] | None = Field(None, description="A visual icon representing the catalog. Choose from predefined icon options: globe-alt, server-stack, users, user-group, chart-bar, shapes, light-bulb, or cursor-arrow-ripple."),
    position: int | None = Field(None, description="The display order position of the catalog when shown in a list. Lower numbers appear first."),
) -> dict[str, Any] | ToolResult:
    """Update an existing catalog's metadata including its description, visual icon, and display position. Modify any combination of catalog properties by providing the catalog ID and updated values."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCatalogRequest(
            path=_models.UpdateCatalogRequestPath(id_=id_),
            body=_models.UpdateCatalogRequestBody(data=_models.UpdateCatalogRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateCatalogRequestBodyDataAttributes(description=description, icon=icon, position=position) if any(v is not None for v in [description, icon, position]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_catalog: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalogs/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalogs/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_catalog")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_catalog", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_catalog",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Catalogs
@mcp.tool()
async def delete_catalog(id_: str = Field(..., alias="id", description="The unique identifier of the catalog to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a catalog and all its associated data. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCatalogRequest(
            path=_models.DeleteCatalogRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_catalog: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/catalogs/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/catalogs/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_catalog")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_catalog", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_catalog",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Causes
@mcp.tool()
async def list_causes(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., organizations, campaigns). Reduces the need for additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of causes to return per page. Adjust to balance between response size and number of requests needed."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of all causes. Use pagination parameters to control the number of results and navigate through pages."""

    # Construct request model with validation
    try:
        _request = _models.ListCausesRequest(
            query=_models.ListCausesRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_causes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/causes"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_causes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_causes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_causes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Causes
@mcp.tool()
async def create_cause(
    type_: Literal["causes"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'causes' for this operation."),
    name: str = Field(..., description="The display name for the cause. This is a required field that identifies the cause."),
    description: str | None = Field(None, description="An optional detailed description providing context or additional information about the cause."),
    position: int | None = Field(None, description="An optional numeric position value that determines the ordering or display sequence of the cause relative to others."),
) -> dict[str, Any] | ToolResult:
    """Creates a new cause with the provided name, description, and optional positioning. The cause type is fixed as 'causes'."""

    # Construct request model with validation
    try:
        _request = _models.CreateCauseRequest(
            body=_models.CreateCauseRequestBody(data=_models.CreateCauseRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateCauseRequestBodyDataAttributes(name=name, description=description, position=position)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_cause: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/causes"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_cause")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_cause", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_cause",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Causes
@mcp.tool()
async def get_cause(id_: str = Field(..., alias="id", description="The unique identifier of the cause to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific cause by its unique identifier. Use this operation to fetch detailed information about a single cause."""

    # Construct request model with validation
    try:
        _request = _models.GetCauseRequest(
            path=_models.GetCauseRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_cause: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/causes/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/causes/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_cause")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_cause", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_cause",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Causes
@mcp.tool()
async def update_cause(
    id_: str = Field(..., alias="id", description="The unique identifier of the cause to update."),
    type_: Literal["causes"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'causes' to specify this is a cause resource."),
    description: str | None = Field(None, description="A text description of the cause, explaining its purpose or context."),
    position: int | None = Field(None, description="The ordinal position of the cause in a list or sequence, used for sorting or display ordering."),
) -> dict[str, Any] | ToolResult:
    """Update an existing cause by its ID, allowing modification of its description and position in the list."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCauseRequest(
            path=_models.UpdateCauseRequestPath(id_=id_),
            body=_models.UpdateCauseRequestBody(data=_models.UpdateCauseRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateCauseRequestBodyDataAttributes(description=description, position=position) if any(v is not None for v in [description, position]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_cause: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/causes/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/causes/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_cause")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_cause", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_cause",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Causes
@mcp.tool()
async def delete_cause(id_: str = Field(..., alias="id", description="The unique identifier of the cause to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a cause by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCauseRequest(
            path=_models.DeleteCauseRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_cause: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/causes/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/causes/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_cause")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_cause", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_cause",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: CustomForms
@mcp.tool()
async def list_custom_forms(
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve for pagination, starting from 1."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of custom forms to return per page."),
    filter_command: str | None = Field(None, alias="filtercommand", description="Filter custom forms by command type or name."),
    sort: str | None = Field(None, description="Sort the results by a specified field in ascending or descending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of custom forms with optional filtering and sorting capabilities."""

    # Construct request model with validation
    try:
        _request = _models.ListCustomFormsRequest(
            query=_models.ListCustomFormsRequestQuery(page_number=page_number, page_size=page_size, filter_command=filter_command, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_forms: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_forms"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_forms")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_forms", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_forms",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: CustomForms
@mcp.tool()
async def create_custom_form(
    type_: Literal["custom_forms"] = Field(..., alias="type", description="The form type identifier; must be set to 'custom_forms' to indicate this is a custom form resource."),
    name: str = Field(..., description="The display name for the custom form; used to identify the form in the UI and logs."),
    command: str = Field(..., description="The Slack slash command (e.g., '/mycommand') that users invoke to trigger and display this form."),
    slug: str | None = Field(None, description="A URL-friendly identifier for the custom form; use this slug value in form_field.shown or form_field.required to associate specific fields with this form."),
    description: str | None = Field(None, description="An optional description providing additional context or instructions for the custom form."),
    enabled: bool | None = Field(None, description="Whether the custom form is active and available for use; defaults to false if not specified."),
) -> dict[str, Any] | ToolResult:
    """Creates a new custom form that can be triggered via a Slack command. The form can include custom fields by referencing the form slug in field associations."""

    # Construct request model with validation
    try:
        _request = _models.CreateCustomFormRequest(
            body=_models.CreateCustomFormRequestBody(data=_models.CreateCustomFormRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateCustomFormRequestBodyDataAttributes(name=name, slug=slug, description=description, enabled=enabled, command=command)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_custom_form: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_forms"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_custom_form")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_custom_form", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_custom_form",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: CustomForms
@mcp.tool()
async def get_custom_form(id_: str = Field(..., alias="id", description="The unique identifier of the custom form to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific custom form by its unique identifier. Use this operation to fetch the complete details and configuration of a custom form."""

    # Construct request model with validation
    try:
        _request = _models.GetCustomFormRequest(
            path=_models.GetCustomFormRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_custom_form: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_forms/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_forms/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_custom_form")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_custom_form", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_custom_form",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: CustomForms
@mcp.tool()
async def update_custom_form(
    id_: str = Field(..., alias="id", description="The unique identifier of the custom form to update."),
    type_: Literal["custom_forms"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'custom_forms' to specify this is a custom form resource."),
    slug: str | None = Field(None, description="A URL-friendly identifier for the custom form. Use this slug value in form_field.shown or form_field.required to associate specific form fields with this custom form."),
    description: str | None = Field(None, description="A human-readable description of the custom form's purpose or usage."),
    enabled: bool | None = Field(None, description="Whether the custom form is active and available for use."),
    command: str | None = Field(None, description="The Slack slash command that triggers this custom form when invoked by users."),
) -> dict[str, Any] | ToolResult:
    """Update an existing custom form configuration by its ID. Modify form metadata, slug, description, enabled status, or associated Slack command trigger."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCustomFormRequest(
            path=_models.UpdateCustomFormRequestPath(id_=id_),
            body=_models.UpdateCustomFormRequestBody(data=_models.UpdateCustomFormRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateCustomFormRequestBodyDataAttributes(slug=slug, description=description, enabled=enabled, command=command) if any(v is not None for v in [slug, description, enabled, command]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_custom_form: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_forms/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_forms/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_custom_form")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_custom_form", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_custom_form",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: CustomForms
@mcp.tool()
async def delete_custom_form(id_: str = Field(..., alias="id", description="The unique identifier of the custom form to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a custom form by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCustomFormRequest(
            path=_models.DeleteCustomFormRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_custom_form: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/custom_forms/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/custom_forms/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_custom_form")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_custom_form", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_custom_form",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: DashboardPanels
@mcp.tool()
async def list_dashboard_panels(
    dashboard_id: str = Field(..., description="The unique identifier of the dashboard containing the panels to retrieve."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., metadata, configuration details). Reduces need for additional requests."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through large result sets."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of panels to return per page. Adjust to balance response size and number of requests needed."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of panels configured within a specific dashboard. Use this to display dashboard contents or manage panel organization."""

    # Construct request model with validation
    try:
        _request = _models.ListDashboardPanelsRequest(
            path=_models.ListDashboardPanelsRequestPath(dashboard_id=dashboard_id),
            query=_models.ListDashboardPanelsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dashboard_panels: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dashboards/{dashboard_id}/panels", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dashboards/{dashboard_id}/panels"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dashboard_panels")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dashboard_panels", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dashboard_panels",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: DashboardPanels
@mcp.tool()
async def create_dashboard_panel(
    dashboard_id: str = Field(..., description="The unique identifier of the dashboard where the panel will be created."),
    type_: Literal["dashboard_panels"] = Field(..., alias="type", description="The resource type identifier for dashboard panels; must be set to 'dashboard_panels'."),
    x: float = Field(..., description="The horizontal grid position (column) where the panel is placed on the dashboard."),
    y: float = Field(..., description="The vertical grid position (row) where the panel is placed on the dashboard."),
    w: float = Field(..., description="The width of the panel measured in grid units."),
    h: float = Field(..., description="The height of the panel measured in grid units."),
    display: Literal["line_chart", "line_stepped_chart", "column_chart", "stacked_column_chart", "monitoring_chart", "pie_chart", "table", "aggregate_value"] | None = Field(None, description="The visualization format for the panel. Choose from line charts, stepped line charts, column charts, stacked columns, monitoring charts, pie charts, tables, or aggregate value displays."),
    description: str | None = Field(None, description="A human-readable label or explanation for the panel's purpose and content."),
    table_fields: list[str] | None = Field(None, description="An ordered list of field names to display in table-format panels. Field order in this array determines column order in the rendered table."),
    groups: Literal["all", "charted"] | None = Field(None, description="Controls which data groups are included in the visualization. Use 'all' to include all available groups, or 'charted' to include only groups that are actively charted. Defaults to 'all'."),
    enabled: bool | None = Field(None, description="Whether the panel is active and visible on the dashboard. When disabled, the panel is hidden but retained."),
    datasets: list[_models.CreateDashboardPanelBodyDataAttributesParamsDatasetsItem] | None = Field(None, description="An array of dataset configurations that define the data sources and metrics to visualize in this panel."),
) -> dict[str, Any] | ToolResult:
    """Creates a new panel on a dashboard with specified visualization type, position, and data configuration. Panels are positioned using grid coordinates and can display various chart types or tables."""

    # Construct request model with validation
    try:
        _request = _models.CreateDashboardPanelRequest(
            path=_models.CreateDashboardPanelRequestPath(dashboard_id=dashboard_id),
            body=_models.CreateDashboardPanelRequestBody(data=_models.CreateDashboardPanelRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateDashboardPanelRequestBodyDataAttributes(
                        params=_models.CreateDashboardPanelRequestBodyDataAttributesParams(display=display, description=description, table_fields=table_fields, datasets=datasets,
                            legend=_models.CreateDashboardPanelRequestBodyDataAttributesParamsLegend(groups=groups) if any(v is not None for v in [groups]) else None,
                            datalabels=_models.CreateDashboardPanelRequestBodyDataAttributesParamsDatalabels(enabled=enabled) if any(v is not None for v in [enabled]) else None) if any(v is not None for v in [display, description, table_fields, groups, enabled, datasets]) else None,
                        position=_models.CreateDashboardPanelRequestBodyDataAttributesPosition(x=x, y=y, w=w, h=h)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_dashboard_panel: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dashboards/{dashboard_id}/panels", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dashboards/{dashboard_id}/panels"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_dashboard_panel")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_dashboard_panel", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_dashboard_panel",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: DashboardPanels
@mcp.tool()
async def duplicate_dashboard_panel(id_: str = Field(..., alias="id", description="The unique identifier of the dashboard panel to duplicate.")) -> dict[str, Any] | ToolResult:
    """Creates a duplicate copy of an existing dashboard panel, preserving its configuration and settings. The duplicated panel is added to the same dashboard as the original."""

    # Construct request model with validation
    try:
        _request = _models.DuplicateDashboardPanelRequest(
            path=_models.DuplicateDashboardPanelRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for duplicate_dashboard_panel: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dashboard_panels/{id}/duplicate", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dashboard_panels/{id}/duplicate"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("duplicate_dashboard_panel")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("duplicate_dashboard_panel", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="duplicate_dashboard_panel",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: DashboardPanels
@mcp.tool()
async def get_dashboard_panel(
    id_: str = Field(..., alias="id", description="The unique identifier of the dashboard panel to retrieve."),
    range_: str | None = Field(None, alias="range", description="Optional date range for filtering panel data, specified as two ISO 8601 timestamps separated by the word 'to' (e.g., start timestamp to end timestamp)."),
    period: str | None = Field(None, description="Optional time period for grouping data within the panel. Valid values are 'day', 'week', or 'month'."),
    time_zone: str | None = Field(None, description="Optional time zone identifier to apply when grouping data by the specified period. Use standard IANA time zone names."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific dashboard panel by its unique identifier, with optional filtering by date range and time-based aggregation."""

    # Construct request model with validation
    try:
        _request = _models.GetDashboardPanelRequest(
            path=_models.GetDashboardPanelRequestPath(id_=id_),
            query=_models.GetDashboardPanelRequestQuery(range_=range_, period=period, time_zone=time_zone)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_dashboard_panel: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dashboard_panels/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dashboard_panels/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_dashboard_panel")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_dashboard_panel", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_dashboard_panel",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: DashboardPanels
@mcp.tool()
async def update_dashboard_panel(
    id_: str = Field(..., alias="id", description="The unique identifier of the dashboard panel to update."),
    x: float = Field(..., description="The horizontal position (x-coordinate) of the panel on the dashboard grid."),
    y: float = Field(..., description="The vertical position (y-coordinate) of the panel on the dashboard grid."),
    w: float = Field(..., description="The width of the panel on the dashboard grid."),
    h: float = Field(..., description="The height of the panel on the dashboard grid."),
    display: Literal["line_chart", "line_stepped_chart", "column_chart", "stacked_column_chart", "monitoring_chart", "pie_chart", "table", "aggregate_value"] | None = Field(None, description="The visualization type for the panel. Choose from line chart, stepped line chart, column chart, stacked column chart, monitoring chart, pie chart, table, or aggregate value display."),
    description: str | None = Field(None, description="A text description of the panel's purpose or content."),
    table_fields: list[str] | None = Field(None, description="An array of field names to display when using table visualization. Order determines column sequence."),
    groups: Literal["all", "charted"] | None = Field(None, description="Controls which data groups to include in the visualization. Use 'all' to include all groups or 'charted' to include only charted groups. Defaults to 'all'."),
    enabled: bool | None = Field(None, description="Whether the panel is active and visible on the dashboard."),
    datasets: list[_models.UpdateDashboardPanelBodyDataAttributesParamsDatasetsItem] | None = Field(None, description="An array of dataset configurations that define the data sources and metrics for the panel."),
) -> dict[str, Any] | ToolResult:
    """Update a dashboard panel's configuration, including its display type, data sources, layout position, and visibility settings."""

    # Construct request model with validation
    try:
        _request = _models.UpdateDashboardPanelRequest(
            path=_models.UpdateDashboardPanelRequestPath(id_=id_),
            body=_models.UpdateDashboardPanelRequestBody(data=_models.UpdateDashboardPanelRequestBodyData(
                    attributes=_models.UpdateDashboardPanelRequestBodyDataAttributes(
                        params=_models.UpdateDashboardPanelRequestBodyDataAttributesParams(display=display, description=description, table_fields=table_fields, datasets=datasets,
                            legend=_models.UpdateDashboardPanelRequestBodyDataAttributesParamsLegend(groups=groups) if any(v is not None for v in [groups]) else None,
                            datalabels=_models.UpdateDashboardPanelRequestBodyDataAttributesParamsDatalabels(enabled=enabled) if any(v is not None for v in [enabled]) else None) if any(v is not None for v in [display, description, table_fields, groups, enabled, datasets]) else None,
                        position=_models.UpdateDashboardPanelRequestBodyDataAttributesPosition(x=x, y=y, w=w, h=h)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_dashboard_panel: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dashboard_panels/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dashboard_panels/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_dashboard_panel")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_dashboard_panel", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_dashboard_panel",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: DashboardPanels
@mcp.tool()
async def delete_dashboard_panel(id_: str = Field(..., alias="id", description="The unique identifier of the dashboard panel to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific dashboard panel by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDashboardPanelRequest(
            path=_models.DeleteDashboardPanelRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_dashboard_panel: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dashboard_panels/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dashboard_panels/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_dashboard_panel")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_dashboard_panel", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_dashboard_panel",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def list_dashboards(
    include: Literal["panels"] | None = Field(None, description="Comma-separated list of related resources to include in the response. Use 'panels' to include panel data for each dashboard."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to control which dashboards are returned."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of dashboards to return per page. Use with page[number] to paginate through results."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of dashboards. Optionally include related panel data for each dashboard."""

    # Construct request model with validation
    try:
        _request = _models.ListDashboardsRequest(
            query=_models.ListDashboardsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dashboards: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/dashboards"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dashboards")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dashboards", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dashboards",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def create_dashboard(
    type_: Literal["dashboards"] = Field(..., alias="type", description="The resource type identifier; must be set to 'dashboards' to indicate this is a dashboard resource."),
    name: str = Field(..., description="A human-readable name for the dashboard that appears in the UI and search results."),
    owner: Literal["user", "team"] = Field(..., description="Specifies who owns the dashboard: either a 'user' (individual ownership) or 'team' (shared team ownership)."),
    description: str | None = Field(None, description="An optional description providing context or details about the dashboard's purpose and contents."),
    public: bool | None = Field(None, description="When enabled, the dashboard is visible to all users; when disabled, access is restricted to the owner and explicitly granted users."),
    range_: str | None = Field(None, alias="range", description="Sets the time window for which dashboard panels display data (e.g., last 7 days, last 30 days). Format as an ISO 8601 duration or relative time expression."),
    auto_refresh: bool | None = Field(None, description="When enabled, the dashboard automatically refreshes panel data in the UI at regular intervals without requiring manual refresh."),
    color: Literal["#FCF2CF", "#D7F5E1", "#E9E2FF", "#FAE6E8", "#FAEEE6"] | None = Field(None, description="A hex color code that customizes the dashboard's visual theme. Choose from: light yellow (#FCF2CF), light green (#D7F5E1), light purple (#E9E2FF), light pink (#FAE6E8), or light orange (#FAEEE6)."),
    icon: str | None = Field(None, description="An optional emoji icon displayed alongside the dashboard name for quick visual identification."),
    period: Literal["day", "week", "month"] | None = Field(None, description="Defines the time-based grouping for aggregating panel data: 'day' for daily buckets, 'week' for weekly buckets, or 'month' for monthly buckets."),
) -> dict[str, Any] | ToolResult:
    """Creates a new dashboard with customizable settings for data visualization and sharing. Configure the dashboard's appearance, refresh behavior, and data aggregation period."""

    # Construct request model with validation
    try:
        _request = _models.CreateDashboardRequest(
            body=_models.CreateDashboardRequestBody(data=_models.CreateDashboardRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateDashboardRequestBodyDataAttributes(name=name, description=description, owner=owner, public=public, range_=range_, auto_refresh=auto_refresh, color=color, icon=icon, period=period)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/dashboards"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_dashboard", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_dashboard",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def duplicate_dashboard(id_: str = Field(..., alias="id", description="The unique identifier of the dashboard to duplicate.")) -> dict[str, Any] | ToolResult:
    """Creates a copy of an existing dashboard with all its configuration, layout, and widgets. The duplicated dashboard will be a complete independent instance."""

    # Construct request model with validation
    try:
        _request = _models.DuplicateDashboardRequest(
            path=_models.DuplicateDashboardRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for duplicate_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dashboards/{id}/duplicate", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dashboards/{id}/duplicate"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("duplicate_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("duplicate_dashboard", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="duplicate_dashboard",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def set_dashboard_as_default(id_: str = Field(..., alias="id", description="The unique identifier of the dashboard to set as default.")) -> dict[str, Any] | ToolResult:
    """Sets the specified dashboard as the default dashboard for the current user. The default dashboard is displayed when the user first accesses the dashboard interface."""

    # Construct request model with validation
    try:
        _request = _models.SetDefaultDashboardRequest(
            path=_models.SetDefaultDashboardRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_dashboard_as_default: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dashboards/{id}/set_default", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dashboards/{id}/set_default"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_dashboard_as_default")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_dashboard_as_default", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_dashboard_as_default",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def get_dashboard(
    id_: str = Field(..., alias="id", description="The unique identifier of the dashboard to retrieve."),
    include: Literal["panels"] | None = Field(None, description="Comma-separated list of related resources to include in the response. Supports 'panels' to include dashboard panel definitions."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific dashboard by its unique identifier. Optionally include related resources such as panels in the response."""

    # Construct request model with validation
    try:
        _request = _models.GetDashboardRequest(
            path=_models.GetDashboardRequestPath(id_=id_),
            query=_models.GetDashboardRequestQuery(include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dashboards/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dashboards/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_dashboard", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_dashboard",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def update_dashboard(
    id_: str = Field(..., alias="id", description="The unique identifier of the dashboard to update."),
    description: str | None = Field(None, description="A text description of the dashboard's purpose or content."),
    owner: Literal["user", "team"] | None = Field(None, description="The ownership model of the dashboard: either 'user' for individual ownership or 'team' for shared team ownership."),
    public: bool | None = Field(None, description="Controls whether the dashboard is publicly accessible or restricted to authorized users."),
    range_: str | None = Field(None, alias="range", description="The time window for which dashboard panels display data (e.g., last 7 days, last 30 days)."),
    auto_refresh: bool | None = Field(None, description="Enables automatic UI updates when new data becomes available, keeping the dashboard current without manual refresh."),
    color: Literal["#FCF2CF", "#D7F5E1", "#E9E2FF", "#FAE6E8", "#FAEEE6"] | None = Field(None, description="A hex color code for the dashboard's visual theme. Choose from: light yellow (#FCF2CF), light green (#D7F5E1), light purple (#E9E2FF), light pink (#FAE6E8), or light orange (#FAEEE6)."),
    icon: str | None = Field(None, description="An emoji icon that visually represents the dashboard in navigation and listings."),
    period: Literal["day", "week", "month"] | None = Field(None, description="The time-based grouping period for aggregating dashboard panel data: 'day' for daily granularity, 'week' for weekly, or 'month' for monthly."),
) -> dict[str, Any] | ToolResult:
    """Update an existing dashboard's configuration, including its metadata, visibility settings, display preferences, and data refresh behavior."""

    # Construct request model with validation
    try:
        _request = _models.UpdateDashboardRequest(
            path=_models.UpdateDashboardRequestPath(id_=id_),
            body=_models.UpdateDashboardRequestBody(data=_models.UpdateDashboardRequestBodyData(attributes=_models.UpdateDashboardRequestBodyDataAttributes(description=description, owner=owner, public=public, range_=range_, auto_refresh=auto_refresh, color=color, icon=icon, period=period) if any(v is not None for v in [description, owner, public, range_, auto_refresh, color, icon, period]) else None) if any(v is not None for v in [description, owner, public, range_, auto_refresh, color, icon, period]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dashboards/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dashboards/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_dashboard", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_dashboard",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Dashboards
@mcp.tool()
async def delete_dashboard(id_: str = Field(..., alias="id", description="The unique identifier of the dashboard to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a dashboard by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDashboardRequest(
            path=_models.DeleteDashboardRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dashboards/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dashboards/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_dashboard", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_dashboard",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def list_environments(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., metadata, configuration details)."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve for pagination, starting from 1."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of environments to return per page; controls pagination size."),
    filter_color: str | None = Field(None, alias="filtercolor", description="Filter environments by color attribute; specify the exact color value to match."),
    sort: str | None = Field(None, description="Sort results by specified field(s) in ascending or descending order; use format like 'field' or 'field:desc'."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of environments with optional filtering and sorting capabilities."""

    # Construct request model with validation
    try:
        _request = _models.ListEnvironmentsRequest(
            query=_models.ListEnvironmentsRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_color=filter_color, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_environments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/environments"
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

# Tags: Environments
@mcp.tool()
async def create_environment(
    type_: Literal["environments"] = Field(..., alias="type", description="The resource type identifier; must be set to 'environments' to specify this is an environment resource."),
    name: str = Field(..., description="A human-readable name for the environment (e.g., 'Production', 'Staging', 'Development')."),
    description: str | None = Field(None, description="An optional description providing additional context or details about the environment's purpose."),
    color: str | None = Field(None, description="An optional hex color code (e.g., '#FF5733') for visual identification of the environment in UI displays."),
    position: int | None = Field(None, description="An optional numeric position value that determines the display order of this environment relative to others."),
    notify_emails: list[str] | None = Field(None, description="An optional list of email addresses that should receive notifications related to this environment. Each entry should be a valid email address."),
    slack_channels: list[_models.CreateEnvironmentBodyDataAttributesSlackChannelsItem] | None = Field(None, description="An optional list of Slack channel identifiers or names to associate with this environment for automated notifications and alerts."),
    slack_aliases: list[_models.CreateEnvironmentBodyDataAttributesSlackAliasesItem] | None = Field(None, description="An optional list of Slack user aliases or handles to associate with this environment for direct messaging and notifications."),
) -> dict[str, Any] | ToolResult:
    """Creates a new environment with optional notification and messaging integrations. The environment serves as a deployment or organizational context that can be associated with Slack channels, email notifications, and visual styling."""

    # Construct request model with validation
    try:
        _request = _models.CreateEnvironmentRequest(
            body=_models.CreateEnvironmentRequestBody(data=_models.CreateEnvironmentRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateEnvironmentRequestBodyDataAttributes(name=name, description=description, color=color, position=position, notify_emails=notify_emails, slack_channels=slack_channels, slack_aliases=slack_aliases)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/environments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

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
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def get_environment(id_: str = Field(..., alias="id", description="The unique identifier of the environment to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific environment by its unique identifier. Use this operation to fetch detailed information about a single environment."""

    # Construct request model with validation
    try:
        _request = _models.GetEnvironmentRequest(
            path=_models.GetEnvironmentRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/environments/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/environments/{id}"
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
    id_: str = Field(..., alias="id", description="The unique identifier of the environment to update."),
    type_: Literal["environments"] = Field(..., alias="type", description="The resource type, which must be 'environments' to identify this as an environment resource."),
    description: str | None = Field(None, description="A human-readable description of the environment's purpose or usage."),
    color: str | None = Field(None, description="A hexadecimal color code (e.g., #FF5733) used to visually represent the environment in the UI."),
    position: int | None = Field(None, description="The display order of the environment in lists and dashboards, where lower numbers appear first."),
    notify_emails: list[str] | None = Field(None, description="A list of email addresses that should receive notifications related to this environment."),
    slack_channels: list[_models.UpdateEnvironmentBodyDataAttributesSlackChannelsItem] | None = Field(None, description="A list of Slack channel identifiers or names to integrate with this environment for notifications and updates."),
    slack_aliases: list[_models.UpdateEnvironmentBodyDataAttributesSlackAliasesItem] | None = Field(None, description="A list of Slack user aliases or handles to associate with this environment for direct messaging and mentions."),
) -> dict[str, Any] | ToolResult:
    """Update an existing environment's configuration, including its description, visual appearance, notification settings, and associated Slack integrations."""

    # Construct request model with validation
    try:
        _request = _models.UpdateEnvironmentRequest(
            path=_models.UpdateEnvironmentRequestPath(id_=id_),
            body=_models.UpdateEnvironmentRequestBody(data=_models.UpdateEnvironmentRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateEnvironmentRequestBodyDataAttributes(description=description, color=color, position=position, notify_emails=notify_emails, slack_channels=slack_channels, slack_aliases=slack_aliases) if any(v is not None for v in [description, color, position, notify_emails, slack_channels, slack_aliases]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/environments/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/environments/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

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
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Environments
@mcp.tool()
async def delete_environment(id_: str = Field(..., alias="id", description="The unique identifier of the environment to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific environment by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteEnvironmentRequest(
            path=_models.DeleteEnvironmentRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/environments/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/environments/{id}"
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

# Tags: EscalationPolicies
@mcp.tool()
async def list_escalation_policies(
    include: Literal["escalation_policy_levels", "escalation_policy_paths", "groups", "services"] | None = Field(None, description="Comma-separated list of related resources to include in the response. Valid options are escalation_policy_levels (the escalation steps), escalation_policy_paths (the routing paths), groups (associated groups), or services (associated services)."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use this to navigate through results when the total count exceeds the page size."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of escalation policies to return per page. Controls the size of each paginated result set."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of escalation policies. Optionally include related resources such as escalation levels, paths, groups, or services to enrich the response."""

    # Construct request model with validation
    try:
        _request = _models.ListEscalationPoliciesRequest(
            query=_models.ListEscalationPoliciesRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_escalation_policies: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/escalation_policies"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_escalation_policies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_escalation_policies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_escalation_policies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: EscalationPolicies
@mcp.tool()
async def create_escalation_policy(
    type_: Literal["escalation_policies"] = Field(..., alias="type", description="The resource type identifier; must be set to 'escalation_policies' to indicate this is an escalation policy resource."),
    name: str = Field(..., description="A human-readable name for the escalation policy used for identification and display purposes."),
    description: str | None = Field(None, description="An optional detailed description explaining the purpose and scope of this escalation policy."),
    repeat_count: int | None = Field(None, description="The number of escalation cycles to execute before the policy stops escalating; determines how many times responders are notified before manual intervention is required."),
    group_ids: list[str] | None = Field(None, description="Optional list of group IDs whose alerts will trigger this escalation policy; when any associated group receives an alert, the escalation chain activates."),
    service_ids: list[str] | None = Field(None, description="Optional list of service IDs whose alerts will trigger this escalation policy; when any associated service receives an alert, the escalation chain activates."),
    time_zone: str | None = Field(None, description="Optional time zone identifier (e.g., 'America/New_York') used to interpret business hours for scheduling escalations during specific times."),
    days: list[Literal["M", "T", "W", "R", "F", "U", "S"]] | None = Field(None, description="Optional list of business days (e.g., ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']) when this escalation policy is active; used in conjunction with time_zone to restrict escalations to business hours."),
) -> dict[str, Any] | ToolResult:
    """Creates a new escalation policy that automatically escalates alerts to additional responders after a specified number of cycles without acknowledgment. The policy can be triggered by alerts from associated groups or services."""

    # Construct request model with validation
    try:
        _request = _models.CreateEscalationPolicyRequest(
            body=_models.CreateEscalationPolicyRequestBody(data=_models.CreateEscalationPolicyRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateEscalationPolicyRequestBodyDataAttributes(
                        name=name, description=description, repeat_count=repeat_count, group_ids=group_ids, service_ids=service_ids,
                        business_hours=_models.CreateEscalationPolicyRequestBodyDataAttributesBusinessHours(time_zone=time_zone, days=days) if any(v is not None for v in [time_zone, days]) else None
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_escalation_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/escalation_policies"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_escalation_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_escalation_policy", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_escalation_policy",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: EscalationPolicies
@mcp.tool()
async def get_escalation_policy(
    id_: str = Field(..., alias="id", description="The unique identifier of the escalation policy to retrieve."),
    include: Literal["escalation_policy_levels", "escalation_policy_paths", "groups", "services"] | None = Field(None, description="Comma-separated list of related resources to include in the response. Valid options are escalation_policy_levels, escalation_policy_paths, groups, and services."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific escalation policy by its unique identifier. Optionally include related resources such as escalation levels, paths, groups, or services."""

    # Construct request model with validation
    try:
        _request = _models.GetEscalationPolicyRequest(
            path=_models.GetEscalationPolicyRequestPath(id_=id_),
            query=_models.GetEscalationPolicyRequestQuery(include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_escalation_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/escalation_policies/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/escalation_policies/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_escalation_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_escalation_policy", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_escalation_policy",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: EscalationPolicies
@mcp.tool()
async def update_escalation_policy(
    id_: str = Field(..., alias="id", description="The unique identifier of the escalation policy to update."),
    type_: Literal["escalation_policies"] = Field(..., alias="type", description="The resource type identifier; must be set to 'escalation_policies' to specify this is an escalation policy resource."),
    description: str | None = Field(None, description="A human-readable description of the escalation policy's purpose and behavior."),
    repeat_count: int | None = Field(None, description="The number of times the escalation policy will cycle through its escalation steps before stopping, allowing multiple retry attempts before requiring manual acknowledgment."),
    group_ids: list[str] | None = Field(None, description="List of group identifiers that will trigger this escalation policy when alerts are routed to them. Order is not significant."),
    service_ids: list[str] | None = Field(None, description="List of service identifiers that will trigger this escalation policy when alerts are generated for those services. Order is not significant."),
    time_zone: str | None = Field(None, description="The time zone identifier (e.g., 'America/New_York') used to interpret business hours and schedule-based escalation rules."),
    days: list[Literal["M", "T", "W", "R", "F", "U", "S"]] | None = Field(None, description="List of business days (e.g., 'Monday', 'Tuesday') when this escalation policy is active; days not listed are treated as non-business hours."),
) -> dict[str, Any] | ToolResult:
    """Update an existing escalation policy to modify its escalation behavior, associated resources, and scheduling rules. Changes apply to future alert escalations using this policy."""

    # Construct request model with validation
    try:
        _request = _models.UpdateEscalationPolicyRequest(
            path=_models.UpdateEscalationPolicyRequestPath(id_=id_),
            body=_models.UpdateEscalationPolicyRequestBody(data=_models.UpdateEscalationPolicyRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateEscalationPolicyRequestBodyDataAttributes(description=description, repeat_count=repeat_count, group_ids=group_ids, service_ids=service_ids,
                        business_hours=_models.UpdateEscalationPolicyRequestBodyDataAttributesBusinessHours(time_zone=time_zone, days=days) if any(v is not None for v in [time_zone, days]) else None) if any(v is not None for v in [description, repeat_count, group_ids, service_ids, time_zone, days]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_escalation_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/escalation_policies/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/escalation_policies/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_escalation_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_escalation_policy", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_escalation_policy",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: EscalationPolicies
@mcp.tool()
async def delete_escalation_policy(id_: str = Field(..., alias="id", description="The unique identifier of the escalation policy to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete an escalation policy by its unique identifier. This action cannot be undone and will remove the policy from the system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteEscalationPolicyRequest(
            path=_models.DeleteEscalationPolicyRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_escalation_policy: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/escalation_policies/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/escalation_policies/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_escalation_policy")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_escalation_policy", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_escalation_policy",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: EscalationLevelsPolicies
@mcp.tool()
async def list_escalation_levels(
    escalation_policy_id: str = Field(..., description="The unique identifier of the escalation policy whose levels you want to retrieve."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., users, schedules). Reduces the need for additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for paginated results, starting from 1. Use with page[size] to navigate through large result sets."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of escalation levels to return per page. Adjust to balance response size and number of requests needed."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all escalation levels configured for a specific escalation policy. Escalation levels define the sequence of on-call responders and timing for incident escalation."""

    # Construct request model with validation
    try:
        _request = _models.ListEscalationLevelsRequest(
            path=_models.ListEscalationLevelsRequestPath(escalation_policy_id=escalation_policy_id),
            query=_models.ListEscalationLevelsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_escalation_levels: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/escalation_policies/{escalation_policy_id}/escalation_levels", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/escalation_policies/{escalation_policy_id}/escalation_levels"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_escalation_levels")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_escalation_levels", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_escalation_levels",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: EscalationLevelsPolicies
@mcp.tool()
async def create_escalation_level(
    escalation_policy_id: str = Field(..., description="The unique identifier of the escalation policy to which this escalation level will be added."),
    type_: Literal["escalation_levels"] = Field(..., alias="type", description="The resource type identifier for this escalation level. Must be set to 'escalation_levels'."),
    position: int = Field(..., description="The sequential position of this escalation level within the policy (e.g., 1 for first level, 2 for second). Determines the order in which escalation levels are triggered."),
    notification_target_params: list[_models.CreateEscalationLevelBodyDataAttributesNotificationTargetParamsItem] = Field(..., description="Array of notification targets (users, teams, or schedules) to be alerted at this escalation level. Order may be significant depending on the paging strategy selected."),
    delay: int | None = Field(None, description="The number of minutes to wait before notifying targets at this escalation level. Allows time for lower-level escalations to resolve the alert."),
    paging_strategy_configuration_strategy: Literal["default", "random", "cycle", "alert"] | None = Field(None, description="The strategy for distributing notifications among targets at this level. Use 'default' for standard behavior, 'random' to select targets randomly, 'cycle' to rotate through targets, or 'alert' to notify all targets simultaneously."),
    paging_strategy_configuration_schedule_strategy: Literal["on_call_only", "everyone"] | None = Field(None, description="Determines which users receive notifications at this level. Use 'on_call_only' to notify only currently on-call users, or 'everyone' to notify all assigned targets regardless of on-call status."),
) -> dict[str, Any] | ToolResult:
    """Creates a new escalation level within an escalation policy to define notification targets and timing for alert escalation. Each level specifies who gets notified and when, with configurable paging strategies."""

    # Construct request model with validation
    try:
        _request = _models.CreateEscalationLevelRequest(
            path=_models.CreateEscalationLevelRequestPath(escalation_policy_id=escalation_policy_id),
            body=_models.CreateEscalationLevelRequestBody(data=_models.CreateEscalationLevelRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateEscalationLevelRequestBodyDataAttributes(delay=delay, position=position, paging_strategy_configuration_strategy=paging_strategy_configuration_strategy, paging_strategy_configuration_schedule_strategy=paging_strategy_configuration_schedule_strategy, notification_target_params=notification_target_params)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_escalation_level: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/escalation_policies/{escalation_policy_id}/escalation_levels", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/escalation_policies/{escalation_policy_id}/escalation_levels"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_escalation_level")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_escalation_level", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_escalation_level",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: EscalationLevelsPath
@mcp.tool()
async def list_escalation_levels_for_escalation_path(
    escalation_policy_path_id: str = Field(..., description="The unique identifier of the escalation path whose escalation levels you want to retrieve."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., users, teams, schedules). Reduces the need for additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through large result sets."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of escalation levels to return per page. Adjust to balance response size and number of requests needed."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all escalation levels defined within a specific escalation path. Escalation levels determine the sequence and conditions for notifying responders when an incident requires escalation."""

    # Construct request model with validation
    try:
        _request = _models.ListEscalationLevelsPathsRequest(
            path=_models.ListEscalationLevelsPathsRequestPath(escalation_policy_path_id=escalation_policy_path_id),
            query=_models.ListEscalationLevelsPathsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_escalation_levels_for_escalation_path: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/escalation_paths/{escalation_policy_path_id}/escalation_levels", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/escalation_paths/{escalation_policy_path_id}/escalation_levels"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_escalation_levels_for_escalation_path")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_escalation_levels_for_escalation_path", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_escalation_levels_for_escalation_path",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: EscalationLevelsPath
@mcp.tool()
async def create_escalation_level_path(
    escalation_policy_path_id: str = Field(..., description="The unique identifier of the escalation path to which this escalation level will be added."),
    type_: Literal["escalation_levels"] = Field(..., alias="type", description="The resource type identifier; must be set to 'escalation_levels'."),
    position: int = Field(..., description="The sequential position of this escalation level within the path (e.g., 1 for first level, 2 for second). Determines the order in which escalation levels are triggered."),
    notification_target_params: list[_models.CreateEscalationLevelPathsBodyDataAttributesNotificationTargetParamsItem] = Field(..., description="An ordered list of notification targets to alert at this escalation level. Order may affect notification sequence depending on the paging strategy."),
    delay: int | None = Field(None, description="The number of minutes to wait before notifying targets at this escalation level. Allows time for lower-level escalations to resolve the issue."),
    paging_strategy_configuration_strategy: Literal["default", "random", "cycle", "alert"] | None = Field(None, description="The strategy for selecting which notification targets receive alerts: 'default' uses standard selection, 'random' picks targets randomly, 'cycle' rotates through targets, and 'alert' notifies all targets simultaneously."),
    paging_strategy_configuration_schedule_strategy: Literal["on_call_only", "everyone"] | None = Field(None, description="Determines whether notifications are sent only to currently on-call personnel ('on_call_only') or to all configured targets ('everyone')."),
) -> dict[str, Any] | ToolResult:
    """Creates a new escalation level within an escalation path, defining notification targets and timing for the next tier of alert recipients."""

    # Construct request model with validation
    try:
        _request = _models.CreateEscalationLevelPathsRequest(
            path=_models.CreateEscalationLevelPathsRequestPath(escalation_policy_path_id=escalation_policy_path_id),
            body=_models.CreateEscalationLevelPathsRequestBody(data=_models.CreateEscalationLevelPathsRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateEscalationLevelPathsRequestBodyDataAttributes(delay=delay, position=position, paging_strategy_configuration_strategy=paging_strategy_configuration_strategy, paging_strategy_configuration_schedule_strategy=paging_strategy_configuration_schedule_strategy, notification_target_params=notification_target_params)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_escalation_level_path: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/escalation_paths/{escalation_policy_path_id}/escalation_levels", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/escalation_paths/{escalation_policy_path_id}/escalation_levels"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_escalation_level_path")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_escalation_level_path", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_escalation_level_path",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: EscalationLevels
@mcp.tool()
async def get_escalation_level(id_: str = Field(..., alias="id", description="The unique identifier of the escalation level to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific escalation level by its unique identifier. Use this to fetch details about a particular escalation level configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetEscalationLevelRequest(
            path=_models.GetEscalationLevelRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_escalation_level: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/escalation_levels/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/escalation_levels/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_escalation_level")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_escalation_level", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_escalation_level",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: EscalationLevels
@mcp.tool()
async def update_escalation_level(
    id_: str = Field(..., alias="id", description="The unique identifier of the escalation level to update."),
    type_: Literal["escalation_levels"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'escalation_levels' to specify this is an escalation level resource."),
    delay: int | None = Field(None, description="The number of minutes to wait before notifying targets at this escalation level. Allows time for lower-level escalations to resolve issues before escalating further."),
    position: int | None = Field(None, description="The sequential position of this escalation level within the escalation policy. Lower numbers represent earlier escalation stages."),
    paging_strategy_configuration_strategy: Literal["default", "random", "cycle", "alert"] | None = Field(None, description="The strategy for selecting which notification targets receive alerts: 'default' uses standard ordering, 'random' selects targets randomly, 'cycle' rotates through targets, and 'alert' notifies all targets simultaneously."),
    paging_strategy_configuration_schedule_strategy: Literal["on_call_only", "everyone"] | None = Field(None, description="Determines whether notifications are sent only to currently on-call personnel ('on_call_only') or to all configured targets ('everyone')."),
    notification_target_params: list[_models.UpdateEscalationLevelBodyDataAttributesNotificationTargetParamsItem] | None = Field(None, description="Array of notification target configurations for this escalation level. Each target specifies who should be alerted and how. Order may affect notification sequence depending on the paging strategy."),
) -> dict[str, Any] | ToolResult:
    """Update an existing escalation level within an escalation policy. Modify notification timing, position in the escalation sequence, and paging strategy to control how and when alerts are routed to notification targets."""

    # Construct request model with validation
    try:
        _request = _models.UpdateEscalationLevelRequest(
            path=_models.UpdateEscalationLevelRequestPath(id_=id_),
            body=_models.UpdateEscalationLevelRequestBody(data=_models.UpdateEscalationLevelRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateEscalationLevelRequestBodyDataAttributes(delay=delay, position=position, paging_strategy_configuration_strategy=paging_strategy_configuration_strategy, paging_strategy_configuration_schedule_strategy=paging_strategy_configuration_schedule_strategy, notification_target_params=notification_target_params) if any(v is not None for v in [delay, position, paging_strategy_configuration_strategy, paging_strategy_configuration_schedule_strategy, notification_target_params]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_escalation_level: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/escalation_levels/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/escalation_levels/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_escalation_level")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_escalation_level", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_escalation_level",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: EscalationLevels
@mcp.tool()
async def delete_escalation_level(id_: str = Field(..., alias="id", description="The unique identifier of the escalation level to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete an escalation level by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteEscalationLevelRequest(
            path=_models.DeleteEscalationLevelRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_escalation_level: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/escalation_levels/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/escalation_levels/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_escalation_level")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_escalation_level", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_escalation_level",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: EscalationPaths
@mcp.tool()
async def list_escalation_paths(
    escalation_policy_id: str = Field(..., description="The unique identifier of the escalation policy containing the escalation paths to retrieve."),
    include: Literal["escalation_policy_levels"] | None = Field(None, description="Optional comma-separated list of related resources to include in the response. Specify 'escalation_policy_levels' to include the policy levels associated with each escalation path."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, used to retrieve a specific set of results when the total number of escalation paths exceeds the page size."),
    page_size: int | None = Field(None, alias="pagesize", description="The maximum number of escalation paths to return per page for pagination purposes."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all escalation paths defined within a specific escalation policy. Optionally include related escalation policy level details."""

    # Construct request model with validation
    try:
        _request = _models.ListEscalationPathsRequest(
            path=_models.ListEscalationPathsRequestPath(escalation_policy_id=escalation_policy_id),
            query=_models.ListEscalationPathsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_escalation_paths: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/escalation_policies/{escalation_policy_id}/escalation_paths", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/escalation_policies/{escalation_policy_id}/escalation_paths"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_escalation_paths")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_escalation_paths", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_escalation_paths",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: EscalationPaths
@mcp.tool()
async def get_escalation_path(
    id_: str = Field(..., alias="id", description="The unique identifier of the escalation path to retrieve."),
    include: Literal["escalation_policy_levels"] | None = Field(None, description="Optional comma-separated list of related resources to include in the response. Supports including escalation_policy_levels to fetch the policy levels associated with this escalation path."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific escalation path by its unique identifier. Optionally include related escalation policy levels in the response."""

    # Construct request model with validation
    try:
        _request = _models.GetEscalationPathRequest(
            path=_models.GetEscalationPathRequestPath(id_=id_),
            query=_models.GetEscalationPathRequestQuery(include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_escalation_path: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/escalation_paths/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/escalation_paths/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_escalation_path")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_escalation_path", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_escalation_path",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: EscalationPaths
@mcp.tool()
async def update_escalation_path(
    id_: str = Field(..., alias="id", description="The unique identifier of the escalation path to update."),
    type_: Literal["escalation_paths"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'escalation_paths'."),
    notification_type: Literal["audible", "quiet"] | None = Field(None, description="Notification style for this escalation level. Choose 'audible' for sound alerts or 'quiet' for silent notifications. Defaults to 'audible'."),
    default: bool | None = Field(None, description="Whether this escalation path should be used as the default when no other paths match."),
    match_mode: Literal["match-all-rules", "match-any-rule"] | None = Field(None, description="Rule matching strategy: 'match-all-rules' requires all conditions to be met, while 'match-any-rule' triggers if any condition matches. Defaults to 'match-all-rules'."),
    position: int | None = Field(None, description="The ordinal position of this path within the escalation policy's path sequence."),
    repeat: bool | None = Field(None, description="Whether this path should continue repeating until someone acknowledges the alert."),
    repeat_count: int | None = Field(None, description="The maximum number of times this path will execute before stopping, even if unacknowledged."),
    initial_delay: int | None = Field(None, description="Initial delay before escalation begins, specified in minutes. Maximum allowed is 10080 minutes (one week)."),
    rules: list[_models.UpdateEscalationPathBodyDataAttributesRulesItemV0 | _models.UpdateEscalationPathBodyDataAttributesRulesItemV1 | _models.UpdateEscalationPathBodyDataAttributesRulesItemV2] | None = Field(None, description="Array of escalation path conditions that determine when this path is triggered. Order and structure depend on the match_mode setting."),
    time_restriction_time_zone: Literal["International Date Line West", "Etc/GMT+12", "American Samoa", "Pacific/Pago_Pago", "Midway Island", "Pacific/Midway", "Hawaii", "Pacific/Honolulu", "Alaska", "America/Juneau", "Pacific Time (US & Canada)", "America/Los_Angeles", "Tijuana", "America/Tijuana", "Arizona", "America/Phoenix", "Mazatlan", "America/Mazatlan", "Mountain Time (US & Canada)", "America/Denver", "Central America", "America/Guatemala", "Central Time (US & Canada)", "America/Chicago", "Chihuahua", "America/Chihuahua", "Guadalajara", "America/Mexico_City", "Mexico City", "Monterrey", "America/Monterrey", "Saskatchewan", "America/Regina", "Bogota", "America/Bogota", "Eastern Time (US & Canada)", "America/New_York", "Indiana (East)", "America/Indiana/Indianapolis", "Lima", "America/Lima", "Quito", "Atlantic Time (Canada)", "America/Halifax", "Caracas", "America/Caracas", "Georgetown", "America/Guyana", "La Paz", "America/La_Paz", "Puerto Rico", "America/Puerto_Rico", "Santiago", "America/Santiago", "Newfoundland", "America/St_Johns", "Brasilia", "America/Sao_Paulo", "Buenos Aires", "America/Argentina/Buenos_Aires", "Montevideo", "America/Montevideo", "Greenland", "America/Godthab", "Mid-Atlantic", "Atlantic/South_Georgia", "Azores", "Atlantic/Azores", "Cape Verde Is.", "Atlantic/Cape_Verde", "Edinburgh", "Europe/London", "Lisbon", "Europe/Lisbon", "London", "Monrovia", "Africa/Monrovia", "UTC", "Etc/UTC", "Amsterdam", "Europe/Amsterdam", "Belgrade", "Europe/Belgrade", "Berlin", "Europe/Berlin", "Bern", "Europe/Zurich", "Bratislava", "Europe/Bratislava", "Brussels", "Europe/Brussels", "Budapest", "Europe/Budapest", "Casablanca", "Africa/Casablanca", "Copenhagen", "Europe/Copenhagen", "Dublin", "Europe/Dublin", "Ljubljana", "Europe/Ljubljana", "Madrid", "Europe/Madrid", "Paris", "Europe/Paris", "Prague", "Europe/Prague", "Rome", "Europe/Rome", "Sarajevo", "Europe/Sarajevo", "Skopje", "Europe/Skopje", "Stockholm", "Europe/Stockholm", "Vienna", "Europe/Vienna", "Warsaw", "Europe/Warsaw", "West Central Africa", "Africa/Algiers", "Zagreb", "Europe/Zagreb", "Zurich", "Athens", "Europe/Athens", "Bucharest", "Europe/Bucharest", "Cairo", "Africa/Cairo", "Harare", "Africa/Harare", "Helsinki", "Europe/Helsinki", "Jerusalem", "Asia/Jerusalem", "Kaliningrad", "Europe/Kaliningrad", "Kyiv", "Europe/Kiev", "Pretoria", "Africa/Johannesburg", "Riga", "Europe/Riga", "Sofia", "Europe/Sofia", "Tallinn", "Europe/Tallinn", "Vilnius", "Europe/Vilnius", "Baghdad", "Asia/Baghdad", "Istanbul", "Europe/Istanbul", "Kuwait", "Asia/Kuwait", "Minsk", "Europe/Minsk", "Moscow", "Europe/Moscow", "Nairobi", "Africa/Nairobi", "Riyadh", "Asia/Riyadh", "St. Petersburg", "Volgograd", "Europe/Volgograd", "Tehran", "Asia/Tehran", "Abu Dhabi", "Asia/Muscat", "Baku", "Asia/Baku", "Muscat", "Samara", "Europe/Samara", "Tbilisi", "Asia/Tbilisi", "Yerevan", "Asia/Yerevan", "Kabul", "Asia/Kabul", "Almaty", "Asia/Almaty", "Astana", "Ekaterinburg", "Asia/Yekaterinburg", "Islamabad", "Asia/Karachi", "Karachi", "Tashkent", "Asia/Tashkent", "Chennai", "Asia/Kolkata", "Kolkata", "Mumbai", "New Delhi", "Sri Jayawardenepura", "Asia/Colombo", "Kathmandu", "Asia/Kathmandu", "Dhaka", "Asia/Dhaka", "Urumqi", "Asia/Urumqi", "Rangoon", "Asia/Rangoon", "Bangkok", "Asia/Bangkok", "Hanoi", "Jakarta", "Asia/Jakarta", "Krasnoyarsk", "Asia/Krasnoyarsk", "Novosibirsk", "Asia/Novosibirsk", "Beijing", "Asia/Shanghai", "Chongqing", "Asia/Chongqing", "Hong Kong", "Asia/Hong_Kong", "Irkutsk", "Asia/Irkutsk", "Kuala Lumpur", "Asia/Kuala_Lumpur", "Perth", "Australia/Perth", "Singapore", "Asia/Singapore", "Taipei", "Asia/Taipei", "Ulaanbaatar", "Asia/Ulaanbaatar", "Osaka", "Asia/Tokyo", "Sapporo", "Seoul", "Asia/Seoul", "Tokyo", "Yakutsk", "Asia/Yakutsk", "Adelaide", "Australia/Adelaide", "Darwin", "Australia/Darwin", "Brisbane", "Australia/Brisbane", "Canberra", "Australia/Canberra", "Guam", "Pacific/Guam", "Hobart", "Australia/Hobart", "Melbourne", "Australia/Melbourne", "Port Moresby", "Pacific/Port_Moresby", "Sydney", "Australia/Sydney", "Vladivostok", "Asia/Vladivostok", "Magadan", "Asia/Magadan", "New Caledonia", "Pacific/Noumea", "Solomon Is.", "Pacific/Guadalcanal", "Srednekolymsk", "Asia/Srednekolymsk", "Auckland", "Pacific/Auckland", "Fiji", "Pacific/Fiji", "Kamchatka", "Asia/Kamchatka", "Marshall Is.", "Pacific/Majuro", "Wellington", "Chatham Is.", "Pacific/Chatham", "Nuku'alofa", "Pacific/Tongatapu", "Samoa", "Pacific/Apia", "Tokelau Is.", "Pacific/Fakaofo"] | None = Field(None, description="Time zone for evaluating time-based restrictions. Accepts standard IANA time zone identifiers (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo')."),
    time_restrictions: list[_models.UpdateEscalationPathBodyDataAttributesTimeRestrictionsItem] | None = Field(None, description="Array of time windows during which this escalation path is active. Alerts arriving outside these windows will not follow this path."),
) -> dict[str, Any] | ToolResult:
    """Update an escalation path configuration by ID, including notification settings, matching rules, repetition behavior, delays, and time-based restrictions."""

    # Construct request model with validation
    try:
        _request = _models.UpdateEscalationPathRequest(
            path=_models.UpdateEscalationPathRequestPath(id_=id_),
            body=_models.UpdateEscalationPathRequestBody(data=_models.UpdateEscalationPathRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateEscalationPathRequestBodyDataAttributes(notification_type=notification_type, default=default, match_mode=match_mode, position=position, repeat=repeat, repeat_count=repeat_count, initial_delay=initial_delay, rules=rules, time_restriction_time_zone=time_restriction_time_zone, time_restrictions=time_restrictions) if any(v is not None for v in [notification_type, default, match_mode, position, repeat, repeat_count, initial_delay, rules, time_restriction_time_zone, time_restrictions]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_escalation_path: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/escalation_paths/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/escalation_paths/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_escalation_path")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_escalation_path", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_escalation_path",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: EscalationPaths
@mcp.tool()
async def delete_escalation_path(id_: str = Field(..., alias="id", description="The unique identifier of the escalation path to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific escalation path by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteEscalationPathRequest(
            path=_models.DeleteEscalationPathRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_escalation_path: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/escalation_paths/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/escalation_paths/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_escalation_path")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_escalation_path", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_escalation_path",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFieldOptions
@mcp.tool()
async def list_form_field_options(
    form_field_id: str = Field(..., description="The unique identifier of the form field whose options you want to list."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., metadata, dependencies). Specify which associations should be populated."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to control which subset of results is returned."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of options to return per page. Controls the maximum number of results in a single response."),
    filter_value: str | None = Field(None, alias="filtervalue", description="Filter options by their display value or label. Supports partial matching to find options containing the specified text."),
    filter_color: str | None = Field(None, alias="filtercolor", description="Filter options by their associated color value. Useful for filtering visually-coded options."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of options available for a specific form field. Use filtering and pagination parameters to narrow results and control response size."""

    # Construct request model with validation
    try:
        _request = _models.ListFormFieldOptionsRequest(
            path=_models.ListFormFieldOptionsRequestPath(form_field_id=form_field_id),
            query=_models.ListFormFieldOptionsRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_value=filter_value, filter_color=filter_color)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_form_field_options: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_fields/{form_field_id}/options", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_fields/{form_field_id}/options"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_form_field_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_form_field_options", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_form_field_options",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFieldOptions
@mcp.tool()
async def add_form_field_option(
    form_field_id: str = Field(..., description="The unique identifier of the form field to which this option will be added."),
    attributes_form_field_id: str = Field(..., alias="attributesForm_field_id", description="The unique identifier of the form field that this option belongs to; must match the form_field_id in the path."),
    type_: Literal["form_field_options"] = Field(..., alias="type", description="The resource type identifier; must be set to 'form_field_options'."),
    value: str = Field(..., description="The display value or label for this form field option that users will see when selecting from the field."),
    color: str | None = Field(None, description="Optional hex color code to visually distinguish this option in the form interface."),
    default: bool | None = Field(None, description="Optional flag to designate this option as the default selection for the form field."),
    position: int | None = Field(None, description="Optional numeric position to control the display order of this option relative to other options in the form field."),
) -> dict[str, Any] | ToolResult:
    """Creates a new option for a form field, allowing you to define selectable values with optional styling and positioning."""

    # Construct request model with validation
    try:
        _request = _models.CreateFormFieldOptionRequest(
            path=_models.CreateFormFieldOptionRequestPath(form_field_id=form_field_id),
            body=_models.CreateFormFieldOptionRequestBody(data=_models.CreateFormFieldOptionRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateFormFieldOptionRequestBodyDataAttributes(form_field_id=attributes_form_field_id, value=value, color=color, default=default, position=position)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_form_field_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_fields/{form_field_id}/options", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_fields/{form_field_id}/options"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_form_field_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_form_field_option", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_form_field_option",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFieldOptions
@mcp.tool()
async def get_form_field_option(id_: str = Field(..., alias="id", description="The unique identifier of the form field option to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific form field option by its unique identifier. Use this to fetch details about a single option available for a form field."""

    # Construct request model with validation
    try:
        _request = _models.GetFormFieldOptionRequest(
            path=_models.GetFormFieldOptionRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_form_field_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_field_options/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_field_options/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_form_field_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_form_field_option", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_form_field_option",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFieldOptions
@mcp.tool()
async def update_form_field_option(
    id_: str = Field(..., alias="id", description="The unique identifier of the form field option to update."),
    type_: Literal["form_field_options"] = Field(..., alias="type", description="The resource type identifier, which must be 'form_field_options' to specify the resource being updated."),
    value: str | None = Field(None, description="The display value or label for this form field option."),
    color: str | None = Field(None, description="The hex color code for visual representation of this form field option."),
    default: bool | None = Field(None, description="Whether this option should be selected by default when the form field is displayed."),
    position: int | None = Field(None, description="The ordinal position of this option within the form field's list of options, used to control display order."),
) -> dict[str, Any] | ToolResult:
    """Update a specific form field option by its ID, allowing modification of its display value, color, default status, and position within the form field."""

    # Construct request model with validation
    try:
        _request = _models.UpdateFormFieldOptionRequest(
            path=_models.UpdateFormFieldOptionRequestPath(id_=id_),
            body=_models.UpdateFormFieldOptionRequestBody(data=_models.UpdateFormFieldOptionRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateFormFieldOptionRequestBodyDataAttributes(value=value, color=color, default=default, position=position) if any(v is not None for v in [value, color, default, position]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_form_field_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_field_options/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_field_options/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_form_field_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_form_field_option", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_form_field_option",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFieldOptions
@mcp.tool()
async def delete_form_field_option(id_: str = Field(..., alias="id", description="The unique identifier of the form field option to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a specific form field option by its unique identifier. This operation permanently removes the option from the form field."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFormFieldOptionRequest(
            path=_models.DeleteFormFieldOptionRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_form_field_option: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_field_options/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_field_options/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_form_field_option")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_form_field_option", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_form_field_option",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFieldPlacementConditions
@mcp.tool()
async def list_form_field_placement_conditions(
    form_field_placement_id: str = Field(..., description="The unique identifier of the form field placement whose conditions you want to retrieve."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response for expanded context (e.g., condition details, field metadata)."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use this to navigate through multiple pages of results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of conditions to return per page. Adjust this to control the size of each paginated response."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of conditions associated with a specific form field placement. Conditions define the rules that determine when a form field should be displayed or hidden."""

    # Construct request model with validation
    try:
        _request = _models.ListFormFieldPlacementConditionsRequest(
            path=_models.ListFormFieldPlacementConditionsRequestPath(form_field_placement_id=form_field_placement_id),
            query=_models.ListFormFieldPlacementConditionsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_form_field_placement_conditions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_field_placements/{form_field_placement_id}/conditions", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_field_placements/{form_field_placement_id}/conditions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_form_field_placement_conditions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_form_field_placement_conditions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_form_field_placement_conditions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFieldPlacementConditions
@mcp.tool()
async def delete_form_field_placement_condition(id_: str = Field(..., alias="id", description="The unique identifier of the form field placement condition to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a specific form field placement condition by its unique identifier. This removes the condition rule that controls when a form field should be displayed or hidden."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFormFieldPlacementConditionRequest(
            path=_models.DeleteFormFieldPlacementConditionRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_form_field_placement_condition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_field_placement_conditions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_field_placement_conditions/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_form_field_placement_condition")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_form_field_placement_condition", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_form_field_placement_condition",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFieldPlacements
@mcp.tool()
async def list_form_field_placements(
    form_field_id: str = Field(..., description="The unique identifier of the form field for which to list placements."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., form, placement_context)."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of results to return per page."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all placements for a specific form field, with support for pagination and optional relationship inclusion."""

    # Construct request model with validation
    try:
        _request = _models.ListFormFieldPlacementsRequest(
            path=_models.ListFormFieldPlacementsRequestPath(form_field_id=form_field_id),
            query=_models.ListFormFieldPlacementsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_form_field_placements: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_fields/{form_field_id}/placements", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_fields/{form_field_id}/placements"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_form_field_placements")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_form_field_placements", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_form_field_placements",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFieldPlacements
@mcp.tool()
async def create_form_field_placement(
    form_field_id: str = Field(..., description="The unique identifier of the form field being placed."),
    type_: Literal["form_field_placements"] = Field(..., alias="type", description="The resource type identifier; must be set to 'form_field_placements' to indicate this is a form field placement resource."),
    form_set_id: str = Field(..., description="The unique identifier of the form set that contains this field placement."),
    form: str = Field(..., description="The unique identifier of the form where this field will be placed."),
    position: int | None = Field(None, description="The display order of this field on the form; lower values appear first. If not specified, the field is appended to the end."),
    required: bool | None = Field(None, description="Whether this field must always be completed on the form, regardless of any conditional logic."),
    required_operator: Literal["and", "or"] | None = Field(None, description="The logical operator (AND or OR) used when evaluating multiple conditions that determine if this field is required. Use AND when all conditions must be met, or OR when any condition can trigger the requirement."),
    placement_operator: Literal["and", "or"] | None = Field(None, description="The logical operator (AND or OR) used when evaluating multiple conditions that determine if this field should be displayed. Use AND when all conditions must be met, or OR when any condition can trigger visibility."),
) -> dict[str, Any] | ToolResult:
    """Creates a new placement of a form field within a specific form and form set. This establishes where and how a field appears on a form, including its position, requirement status, and conditional logic rules."""

    # Construct request model with validation
    try:
        _request = _models.CreateFormFieldPlacementRequest(
            path=_models.CreateFormFieldPlacementRequestPath(form_field_id=form_field_id),
            body=_models.CreateFormFieldPlacementRequestBody(data=_models.CreateFormFieldPlacementRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateFormFieldPlacementRequestBodyDataAttributes(form_set_id=form_set_id, form=form, position=position, required=required, required_operator=required_operator, placement_operator=placement_operator)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_form_field_placement: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_fields/{form_field_id}/placements", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_fields/{form_field_id}/placements"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_form_field_placement")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_form_field_placement", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_form_field_placement",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFieldPositions
@mcp.tool()
async def list_form_field_positions(
    form_field_id: str = Field(..., description="The unique identifier of the form field for which to retrieve positions."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., form details, metadata)."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of positions to return per page. Defines the maximum number of results in each paginated response."),
    filter_form: str | None = Field(None, alias="filterform", description="Filter positions by the form they belong to, specified by form identifier."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all positions associated with a specific form field. Positions represent locations or instances where the form field appears within forms."""

    # Construct request model with validation
    try:
        _request = _models.ListFormFieldPositionsRequest(
            path=_models.ListFormFieldPositionsRequestPath(form_field_id=form_field_id),
            query=_models.ListFormFieldPositionsRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_form=filter_form)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_form_field_positions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_fields/{form_field_id}/positions", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_fields/{form_field_id}/positions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_form_field_positions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_form_field_positions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_form_field_positions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFieldPositions
@mcp.tool()
async def create_form_field_position(
    form_field_id: str = Field(..., description="The unique identifier of the form field to position."),
    attributes_form_field_id: str = Field(..., alias="attributesForm_field_id", description="The unique identifier of the form field being positioned. Must match the form_field_id in the path parameter."),
    type_: Literal["form_field_positions"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'form_field_positions'."),
    form: Literal["web_new_incident_form", "web_update_incident_form", "web_incident_post_mortem_form", "web_incident_mitigation_form", "web_incident_resolution_form", "web_incident_cancellation_form", "web_scheduled_incident_form", "web_update_scheduled_incident_form", "incident_post_mortem", "slack_new_incident_form", "slack_update_incident_form", "slack_update_incident_status_form", "slack_incident_mitigation_form", "slack_incident_resolution_form", "slack_incident_cancellation_form", "slack_scheduled_incident_form", "slack_update_scheduled_incident_form"] = Field(..., description="The target form where this field will be positioned. Choose from web-based forms (new incident, update incident, post-mortem, mitigation, resolution, cancellation, or scheduled incident) or Slack-based forms (with equivalent operations)."),
    position: int = Field(..., description="The numeric position (order) where this field should appear within the selected form. Lower numbers appear first."),
) -> dict[str, Any] | ToolResult:
    """Creates a new position assignment for a form field, determining where the field appears within a specific incident management form (web or Slack-based)."""

    # Construct request model with validation
    try:
        _request = _models.CreateFormFieldPositionRequest(
            path=_models.CreateFormFieldPositionRequestPath(form_field_id=form_field_id),
            body=_models.CreateFormFieldPositionRequestBody(data=_models.CreateFormFieldPositionRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateFormFieldPositionRequestBodyDataAttributes(form_field_id=attributes_form_field_id, form=form, position=position)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_form_field_position: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_fields/{form_field_id}/positions", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_fields/{form_field_id}/positions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_form_field_position")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_form_field_position", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_form_field_position",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFieldPositions
@mcp.tool()
async def get_form_field_position(id_: str = Field(..., alias="id", description="The unique identifier of the form field position to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the position and layout details of a specific form field by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetFormFieldPositionRequest(
            path=_models.GetFormFieldPositionRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_form_field_position: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_field_positions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_field_positions/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_form_field_position")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_form_field_position", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_form_field_position",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFields
@mcp.tool()
async def list_form_fields(
    include: Literal["options", "positions"] | None = Field(None, description="Comma-separated list of related data to include in the response. Valid options are 'options' (field choices/values) and 'positions' (field ordering/layout information)."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to retrieve specific result sets."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of form fields to return per page. Use with page[number] to control pagination."),
    filter_kind: str | None = Field(None, alias="filterkind", description="Filter results by the type or category of form field (e.g., text, checkbox, dropdown)."),
    filter_enabled: bool | None = Field(None, alias="filterenabled", description="Filter results to show only enabled form fields (true) or disabled form fields (false)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of form fields with optional filtering by kind and enabled status. Optionally include related data such as field options or position information."""

    # Construct request model with validation
    try:
        _request = _models.ListFormFieldsRequest(
            query=_models.ListFormFieldsRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_kind=filter_kind, filter_enabled=filter_enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_form_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/form_fields"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_form_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_form_fields", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_form_fields",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFields
@mcp.tool()
async def create_form_field(
    type_: Literal["form_fields"] = Field(..., alias="type", description="The resource type identifier; must be set to 'form_fields' to indicate this is a form field resource."),
    kind: Literal["custom", "title", "summary", "mitigation_message", "resolution_message", "severity", "environments", "types", "services", "causes", "functionalities", "teams", "visibility", "mark_as_test", "mark_as_backfilled", "labels", "notify_emails", "trigger_manual_workflows", "show_ongoing_incidents", "attach_alerts", "mark_as_in_triage", "in_triage_at", "started_at", "detected_at", "acknowledged_at", "mitigated_at", "resolved_at", "closed_at", "manual_starting_datetime_field"] = Field(..., description="The category of form field being created. Choose from predefined types like 'custom' for user-defined fields, 'title' and 'summary' for incident metadata, message fields for communication, standard incident attributes (severity, environments, types, services, causes, functionalities, teams, visibility), workflow controls (mark_as_test, mark_as_backfilled, trigger_manual_workflows), triage management (mark_as_in_triage, in_triage_at), or timestamp fields (started_at, detected_at, acknowledged_at, mitigated_at, resolved_at, closed_at, manual_starting_datetime_field)."),
    name: str = Field(..., description="The display name of the form field. Used in UI labels and incident details."),
    input_kind: Literal["text", "textarea", "select", "multi_select", "date", "datetime", "number", "checkbox", "tags", "rich_text"] | None = Field(None, description="The UI input control type for this field. Determines how users interact with the field: 'text' for single-line input, 'textarea' for multi-line text, 'select' for dropdown selection, 'multi_select' for multiple choices, 'date' or 'datetime' for temporal values, 'number' for numeric input, 'checkbox' for boolean toggles, 'tags' for comma-separated values, or 'rich_text' for formatted content."),
    value_kind: Literal["inherit", "group", "service", "functionality", "user", "catalog_entity"] | None = Field(None, description="The semantic type of values this field accepts. Use 'inherit' to derive from context, 'group' for team/group references, 'service' for service catalog items, 'functionality' for functionality references, 'user' for user assignments, or 'catalog_entity' for custom catalog items (requires value_kind_catalog_id)."),
    value_kind_catalog_id: str | None = Field(None, description="The catalog identifier to use when value_kind is set to 'catalog_entity'. Specifies which custom catalog this field's values are sourced from."),
    description: str | None = Field(None, description="Optional explanatory text describing the purpose and usage of this form field."),
    shown: list[str] | None = Field(None, description="Conditions determining when this field is visible in the incident form. Specify as an array of condition objects."),
    required: list[str] | None = Field(None, description="Conditions determining when this field is required for incident creation or updates. Specify as an array of condition objects."),
    show_on_incident_details: bool | None = Field(None, description="Whether this form field appears in the incident details panel when viewing incident information."),
    enabled: bool | None = Field(None, description="Whether this form field is active and available for use in incident workflows."),
    default_values: list[str] | None = Field(None, description="Pre-populated values for this field when creating new incidents. Specify as an array of values matching the field's value_kind type."),
) -> dict[str, Any] | ToolResult:
    """Creates a new form field for incident management workflows. Form fields define custom data collection, display, and validation rules for incidents."""

    # Construct request model with validation
    try:
        _request = _models.CreateFormFieldRequest(
            body=_models.CreateFormFieldRequestBody(data=_models.CreateFormFieldRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateFormFieldRequestBodyDataAttributes(kind=kind, input_kind=input_kind, value_kind=value_kind, value_kind_catalog_id=value_kind_catalog_id, name=name, description=description, shown=shown, required=required, show_on_incident_details=show_on_incident_details, enabled=enabled, default_values=default_values)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_form_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/form_fields"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_form_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_form_field", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_form_field",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFields
@mcp.tool()
async def get_form_field(
    id_: str = Field(..., alias="id", description="The unique identifier of the form field to retrieve."),
    include: Literal["options", "positions"] | None = Field(None, description="Comma-separated list of related resources to include in the response. Supported values are 'options' (field choices/values) and 'positions' (field layout positioning)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific form field by its unique identifier, with optional related data expansion."""

    # Construct request model with validation
    try:
        _request = _models.GetFormFieldRequest(
            path=_models.GetFormFieldRequestPath(id_=id_),
            query=_models.GetFormFieldRequestQuery(include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_form_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_fields/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_fields/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_form_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_form_field", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_form_field",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFields
@mcp.tool()
async def update_form_field(
    id_: str = Field(..., alias="id", description="The unique identifier of the form field to update."),
    type_: Literal["form_fields"] = Field(..., alias="type", description="The resource type, which must be 'form_fields' to identify this as a form field resource."),
    kind: Literal["custom", "title", "summary", "mitigation_message", "resolution_message", "severity", "environments", "types", "services", "causes", "functionalities", "teams", "visibility", "mark_as_test", "mark_as_backfilled", "labels", "notify_emails", "trigger_manual_workflows", "show_ongoing_incidents", "attach_alerts", "mark_as_in_triage", "in_triage_at", "started_at", "detected_at", "acknowledged_at", "mitigated_at", "resolved_at", "closed_at", "manual_starting_datetime_field"] | None = Field(None, description="The category of form field, such as custom fields or predefined incident attributes like severity, environments, teams, timestamps (started_at, resolved_at, etc.), or workflow controls (mark_as_test, trigger_manual_workflows)."),
    input_kind: Literal["text", "textarea", "select", "multi_select", "date", "datetime", "number", "checkbox", "tags", "rich_text"] | None = Field(None, description="The UI input component type for this field, ranging from simple text inputs to complex multi-select dropdowns, date pickers, rich text editors, and checkboxes."),
    value_kind: Literal["inherit", "group", "service", "functionality", "user", "catalog_entity"] | None = Field(None, description="The data source type for field values, allowing values to be inherited from parent contexts, grouped by organizational units, services, functionalities, users, or custom catalog entities."),
    value_kind_catalog_id: str | None = Field(None, description="The catalog identifier to reference when value_kind is set to 'catalog_entity', enabling integration with external catalog systems."),
    description: str | None = Field(None, description="A human-readable explanation of the form field's purpose and usage."),
    shown: list[str] | None = Field(None, description="An array defining the conditions or contexts in which this form field should be displayed to users."),
    required: list[str] | None = Field(None, description="An array specifying the conditions under which this form field becomes mandatory for users to complete."),
    show_on_incident_details: bool | None = Field(None, description="Whether this form field should be visible in the incident details panel when viewing incident information."),
    enabled: bool | None = Field(None, description="Whether this form field is active and available for use in forms."),
    default_values: list[str] | None = Field(None, description="An array of default values to pre-populate this form field when no user input is provided."),
) -> dict[str, Any] | ToolResult:
    """Update a specific form field configuration by ID, allowing modification of its type, input behavior, display settings, and validation rules."""

    # Construct request model with validation
    try:
        _request = _models.UpdateFormFieldRequest(
            path=_models.UpdateFormFieldRequestPath(id_=id_),
            body=_models.UpdateFormFieldRequestBody(data=_models.UpdateFormFieldRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateFormFieldRequestBodyDataAttributes(kind=kind, input_kind=input_kind, value_kind=value_kind, value_kind_catalog_id=value_kind_catalog_id, description=description, shown=shown, required=required, show_on_incident_details=show_on_incident_details, enabled=enabled, default_values=default_values) if any(v is not None for v in [kind, input_kind, value_kind, value_kind_catalog_id, description, shown, required, show_on_incident_details, enabled, default_values]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_form_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_fields/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_fields/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_form_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_form_field", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_form_field",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: FormFields
@mcp.tool()
async def delete_form_field(id_: str = Field(..., alias="id", description="The unique identifier of the form field to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a form field by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFormFieldRequest(
            path=_models.DeleteFormFieldRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_form_field: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_fields/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_fields/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_form_field")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_form_field", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_form_field",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormSetConditions
@mcp.tool()
async def list_form_set_conditions(
    form_set_id: str = Field(..., description="The unique identifier of the form set for which to retrieve conditions."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response for expanded context."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of conditions to return per page. Determines the batch size for paginated results."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all conditions associated with a specific form set. Conditions define the rules and logic that control form behavior and visibility."""

    # Construct request model with validation
    try:
        _request = _models.ListFormSetConditionsRequest(
            path=_models.ListFormSetConditionsRequestPath(form_set_id=form_set_id),
            query=_models.ListFormSetConditionsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_form_set_conditions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_sets/{form_set_id}/conditions", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_sets/{form_set_id}/conditions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_form_set_conditions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_form_set_conditions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_form_set_conditions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormSetConditions
@mcp.tool()
async def create_form_set_condition(
    form_set_id: str = Field(..., description="The unique identifier of the form set to which this condition will be applied."),
    type_: Literal["form_set_conditions"] = Field(..., alias="type", description="The resource type identifier, which must be 'form_set_conditions' to specify this is a form set condition resource."),
    form_field_id: str = Field(..., description="The unique identifier of the form field that this condition evaluates."),
    comparison: Literal["equal"] = Field(..., description="The comparison operator to use when evaluating the condition; currently supports equality checks."),
    values: list[str] = Field(..., description="An array of values to compare against the form field's value. The condition evaluates to true when the field matches one of these values."),
) -> dict[str, Any] | ToolResult:
    """Creates a new conditional rule for a form set that determines when specific form fields should be displayed or processed based on field value comparisons."""

    # Construct request model with validation
    try:
        _request = _models.CreateFormSetConditionRequest(
            path=_models.CreateFormSetConditionRequestPath(form_set_id=form_set_id),
            body=_models.CreateFormSetConditionRequestBody(data=_models.CreateFormSetConditionRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateFormSetConditionRequestBodyDataAttributes(form_field_id=form_field_id, comparison=comparison, values=values)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_form_set_condition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_sets/{form_set_id}/conditions", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_sets/{form_set_id}/conditions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_form_set_condition")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_form_set_condition", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_form_set_condition",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: FormSetConditions
@mcp.tool()
async def get_form_set_condition(id_: str = Field(..., alias="id", description="The unique identifier of the form set condition to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific form set condition by its unique identifier. Use this to fetch the configuration and rules associated with a particular form set condition."""

    # Construct request model with validation
    try:
        _request = _models.GetFormSetConditionRequest(
            path=_models.GetFormSetConditionRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_form_set_condition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_set_conditions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_set_conditions/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_form_set_condition")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_form_set_condition", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_form_set_condition",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormSetConditions
@mcp.tool()
async def update_form_set_condition(
    id_: str = Field(..., alias="id", description="The unique identifier of the form set condition to update."),
    type_: Literal["form_set_conditions"] = Field(..., alias="type", description="The resource type identifier, which must be 'form_set_conditions' to specify this is a form set condition resource."),
    form_field_id: str | None = Field(None, description="The ID of the form field that this condition evaluates or monitors for triggering the conditional logic."),
    comparison: Literal["equal"] | None = Field(None, description="The type of comparison to perform between the form field value and the specified values. Currently supports equality comparison."),
    values: list[str] | None = Field(None, description="An array of values to compare against the form field's value using the specified comparison operator. The condition is satisfied when the field value matches one of these values."),
) -> dict[str, Any] | ToolResult:
    """Update an existing form set condition that controls field visibility or behavior based on specified comparison criteria. This allows modification of which form fields are displayed or enabled based on the values of other fields."""

    # Construct request model with validation
    try:
        _request = _models.UpdateFormSetConditionRequest(
            path=_models.UpdateFormSetConditionRequestPath(id_=id_),
            body=_models.UpdateFormSetConditionRequestBody(data=_models.UpdateFormSetConditionRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateFormSetConditionRequestBodyDataAttributes(form_field_id=form_field_id, comparison=comparison, values=values) if any(v is not None for v in [form_field_id, comparison, values]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_form_set_condition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_set_conditions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_set_conditions/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_form_set_condition")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_form_set_condition", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_form_set_condition",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: FormSetConditions
@mcp.tool()
async def delete_form_set_condition(id_: str = Field(..., alias="id", description="The unique identifier of the form set condition to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a specific form set condition by its unique identifier. This operation permanently removes the condition and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFormSetConditionRequest(
            path=_models.DeleteFormSetConditionRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_form_set_condition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_set_conditions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_set_conditions/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_form_set_condition")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_form_set_condition", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_form_set_condition",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormSets
@mcp.tool()
async def list_form_sets(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., forms, metadata). Reduces the need for additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve for pagination, starting from 1. Use with page[size] to control result pagination."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of results per page. Adjust this value to balance between response size and number of requests needed."),
    filter_is_default: bool | None = Field(None, alias="filteris_default", description="Filter results to show only form sets marked as default (true) or non-default (false). Useful for identifying primary form set configurations."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of form sets with optional filtering and relationship inclusion. Use this to browse available form sets and their metadata."""

    # Construct request model with validation
    try:
        _request = _models.ListFormSetsRequest(
            query=_models.ListFormSetsRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_is_default=filter_is_default)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_form_sets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/form_sets"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_form_sets")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_form_sets", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_form_sets",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormSets
@mcp.tool()
async def create_form_set(
    type_: Literal["form_sets"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'form_sets' to indicate this operation creates a form set resource."),
    name: str = Field(..., description="A human-readable name for the form set. Used to identify and organize the form set in the system."),
    forms: list[str] = Field(..., description="An ordered list of forms to include in this set. Each item can be either a built-in form identifier (such as web_new_incident_form, slack_update_incident_form, etc.) or the slug of a custom form. The order determines how forms are presented in workflows."),
) -> dict[str, Any] | ToolResult:
    """Creates a new form set that groups multiple forms together for incident management workflows. Form sets can include built-in incident forms or custom forms to organize how incidents are created, updated, and resolved across web and Slack interfaces."""

    # Construct request model with validation
    try:
        _request = _models.CreateFormSetRequest(
            body=_models.CreateFormSetRequestBody(data=_models.CreateFormSetRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateFormSetRequestBodyDataAttributes(name=name, forms=forms)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_form_set: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/form_sets"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_form_set")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_form_set", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_form_set",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: FormSets
@mcp.tool()
async def get_form_set(id_: str = Field(..., alias="id", description="The unique identifier of the form set to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific form set by its unique identifier. Use this operation to fetch the complete configuration and details of a form set."""

    # Construct request model with validation
    try:
        _request = _models.GetFormSetRequest(
            path=_models.GetFormSetRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_form_set: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_sets/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_sets/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_form_set")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_form_set", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_form_set",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: FormSets
@mcp.tool()
async def update_form_set(
    id_: str = Field(..., alias="id", description="The unique identifier of the form set to update."),
    type_: Literal["form_sets"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'form_sets' to specify this is a form set resource."),
    forms: list[str] | None = Field(None, description="An ordered list of forms to include in this form set. Each form can be a custom form (referenced by its slug) or a built-in form such as web incident forms (web_new_incident_form, web_update_incident_form, etc.) or Slack incident forms (slack_new_incident_form, slack_update_incident_form, etc.). The order of forms in this array determines their presentation sequence."),
) -> dict[str, Any] | ToolResult:
    """Update an existing form set by replacing its configuration, including the forms it contains. Use this to modify which forms are included in a form set for web or Slack incident workflows."""

    # Construct request model with validation
    try:
        _request = _models.UpdateFormSetRequest(
            path=_models.UpdateFormSetRequestPath(id_=id_),
            body=_models.UpdateFormSetRequestBody(data=_models.UpdateFormSetRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateFormSetRequestBodyDataAttributes(forms=forms) if any(v is not None for v in [forms]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_form_set: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_sets/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_sets/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_form_set")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_form_set", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_form_set",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: FormSets
@mcp.tool()
async def delete_form_set(id_: str = Field(..., alias="id", description="The unique identifier of the form set to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a form set and all its associated data. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFormSetRequest(
            path=_models.DeleteFormSetRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_form_set: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/form_sets/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/form_sets/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_form_set")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_form_set", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_form_set",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Functionalities
@mcp.tool()
async def list_functionalities(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., metadata, relationships)."),
    page_number: int | None = Field(None, alias="pagenumber", description="Page number for pagination, starting from 1. Use with page[size] to control result set boundaries."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of results per page. Defines the maximum number of functionalities returned in a single request."),
    filter_backstage_id: str | None = Field(None, alias="filterbackstage_id", description="Filter results by Backstage system identifier to return only functionalities associated with a specific Backstage instance."),
    filter_cortex_id: str | None = Field(None, alias="filtercortex_id", description="Filter results by Cortex system identifier to return only functionalities associated with a specific Cortex instance."),
    filter_opslevel_id: str | None = Field(None, alias="filteropslevel_id", description="Filter results by OpsLevel system identifier to return only functionalities associated with a specific OpsLevel instance."),
    filter_external_id: str | None = Field(None, alias="filterexternal_id", description="Filter results by external system identifier to return only functionalities with a matching external reference."),
    sort: str | None = Field(None, description="Sort results by specified field(s) in ascending or descending order. Use format: field_name or -field_name for reverse order."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of functionalities with optional filtering by external system identifiers and sorting capabilities."""

    # Construct request model with validation
    try:
        _request = _models.ListFunctionalitiesRequest(
            query=_models.ListFunctionalitiesRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_backstage_id=filter_backstage_id, filter_cortex_id=filter_cortex_id, filter_opslevel_id=filter_opslevel_id, filter_external_id=filter_external_id, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_functionalities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/functionalities"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_functionalities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_functionalities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_functionalities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Functionalities
@mcp.tool()
async def create_functionality(
    type_: Literal["functionalities"] = Field(..., alias="type", description="The resource type identifier; must be set to 'functionalities' to indicate this is a functionality resource."),
    name: str = Field(..., description="The display name of the functionality; used to identify and reference this capability across the system."),
    description: str | None = Field(None, description="Internal description of the functionality; provides context for team members managing this resource."),
    public_description: str | None = Field(None, description="Public-facing description of the functionality; visible to external stakeholders and in public documentation."),
    notify_emails: list[str] | None = Field(None, description="Email addresses to notify about functionality updates and incidents; supports multiple recipients as a comma-separated or array format."),
    color: str | None = Field(None, description="Hex color code for visual identification of the functionality in dashboards and UI components."),
    position: int | None = Field(None, description="Display order position of the functionality in lists and navigation; lower numbers appear first."),
    backstage_id: str | None = Field(None, description="Backstage entity identifier for integration with Backstage catalog; format is namespace/kind/entity_name."),
    external_id: str | None = Field(None, description="External system identifier for cross-platform tracking and correlation with third-party tools."),
    opsgenie_team_id: str | None = Field(None, description="Opsgenie team identifier to link this functionality with incident response and on-call management."),
    cortex_id: str | None = Field(None, description="Cortex group identifier for integration with Cortex platform and group-level insights."),
    service_now_ci_sys_id: str | None = Field(None, description="Service Now configuration item system ID for ITSM integration and change management tracking."),
    show_uptime: bool | None = Field(None, description="Enable uptime monitoring and display for this functionality; when enabled, uptime metrics will be calculated and shown."),
    show_uptime_last_days: Literal[30, 60, 90] | None = Field(None, description="Time window for uptime calculation in days; valid options are 30, 60, or 90 days, with 60 days as the default."),
    environment_ids: list[str] | None = Field(None, description="Array of environment IDs where this functionality operates; links the functionality to specific deployment environments."),
    service_ids: list[str] | None = Field(None, description="Array of service IDs that implement or depend on this functionality; establishes service-to-functionality relationships."),
    owner_group_ids: list[str] | None = Field(None, description="Array of team/group IDs with ownership responsibility for this functionality; enables team-based access control and notifications."),
    owner_user_ids: list[int] | None = Field(None, description="Array of user IDs with individual ownership of this functionality; enables user-level accountability and direct notifications."),
    slack_channels: list[_models.CreateFunctionalityBodyDataAttributesSlackChannelsItem] | None = Field(None, description="Array of Slack channel identifiers for functionality-related notifications and updates; supports multiple channels for broad communication."),
    slack_aliases: list[_models.CreateFunctionalityBodyDataAttributesSlackAliasesItem] | None = Field(None, description="Array of Slack aliases or handles to mention in notifications; enables direct user mentions and targeted alerts."),
) -> dict[str, Any] | ToolResult:
    """Creates a new functionality with optional integrations to external systems, ownership assignments, and monitoring configurations. Functionalities represent logical business capabilities that can be tracked across services, environments, and teams."""

    # Construct request model with validation
    try:
        _request = _models.CreateFunctionalityRequest(
            body=_models.CreateFunctionalityRequestBody(data=_models.CreateFunctionalityRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateFunctionalityRequestBodyDataAttributes(name=name, description=description, public_description=public_description, notify_emails=notify_emails, color=color, position=position, backstage_id=backstage_id, external_id=external_id, opsgenie_team_id=opsgenie_team_id, cortex_id=cortex_id, service_now_ci_sys_id=service_now_ci_sys_id, show_uptime=show_uptime, show_uptime_last_days=show_uptime_last_days, environment_ids=environment_ids, service_ids=service_ids, owner_group_ids=owner_group_ids, owner_user_ids=owner_user_ids, slack_channels=slack_channels, slack_aliases=slack_aliases)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_functionality: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/functionalities"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_functionality")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_functionality", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_functionality",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Functionalities
@mcp.tool()
async def get_functionality(id_: str = Field(..., alias="id", description="The unique identifier of the functionality to retrieve. This is a required string value that specifies which functionality resource to fetch.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific functionality by its unique identifier. Use this operation to fetch detailed information about a single functionality resource."""

    # Construct request model with validation
    try:
        _request = _models.GetFunctionalityRequest(
            path=_models.GetFunctionalityRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_functionality: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/functionalities/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/functionalities/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_functionality")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_functionality", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_functionality",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Functionalities
@mcp.tool()
async def update_functionality(
    id_: str = Field(..., alias="id", description="The unique identifier of the functionality to update."),
    type_: Literal["functionalities"] = Field(..., alias="type", description="The resource type, which must be 'functionalities' to identify this as a functionality resource."),
    description: str | None = Field(None, description="Internal description of the functionality for reference and documentation purposes."),
    public_description: str | None = Field(None, description="Public-facing description of the functionality visible to external stakeholders and users."),
    notify_emails: list[str] | None = Field(None, description="List of email addresses to receive notifications related to this functionality. Specify as an array of valid email strings."),
    color: str | None = Field(None, description="Hexadecimal color code for visual identification of the functionality in UI displays (e.g., #FF5733)."),
    position: int | None = Field(None, description="Numeric position or order for sorting and displaying the functionality relative to others."),
    backstage_id: str | None = Field(None, description="Backstage entity reference in the format namespace/kind/entity_name to link this functionality to a Backstage catalog entity."),
    external_id: str | None = Field(None, description="External identifier for integrating this functionality with third-party systems or external databases."),
    opsgenie_team_id: str | None = Field(None, description="Opsgenie team identifier to associate incident response and alerting responsibilities with this functionality."),
    cortex_id: str | None = Field(None, description="Cortex group identifier to link this functionality with Cortex organizational groupings."),
    service_now_ci_sys_id: str | None = Field(None, description="Service Now Configuration Item system ID to establish traceability and integration with Service Now CMDB."),
    environment_ids: list[str] | None = Field(None, description="Array of environment identifiers (e.g., production, staging, development) where this functionality operates or is relevant."),
    service_ids: list[str] | None = Field(None, description="Array of service identifiers that implement or depend on this functionality."),
    owner_group_ids: list[str] | None = Field(None, description="Array of team/group identifiers designated as owners responsible for this functionality."),
    owner_user_ids: list[int] | None = Field(None, description="Array of user identifiers designated as individual owners responsible for this functionality."),
    slack_channels: list[_models.UpdateFunctionalityBodyDataAttributesSlackChannelsItem] | None = Field(None, description="Array of Slack channel identifiers for communication and notifications related to this functionality."),
    slack_aliases: list[_models.UpdateFunctionalityBodyDataAttributesSlackAliasesItem] | None = Field(None, description="Array of Slack aliases or handles for automated mentions and notifications in Slack workflows."),
) -> dict[str, Any] | ToolResult:
    """Update an existing functionality with new metadata, associations, and configuration. Modify properties like description, color, position, and linked resources such as services, environments, and owner teams."""

    # Construct request model with validation
    try:
        _request = _models.UpdateFunctionalityRequest(
            path=_models.UpdateFunctionalityRequestPath(id_=id_),
            body=_models.UpdateFunctionalityRequestBody(data=_models.UpdateFunctionalityRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateFunctionalityRequestBodyDataAttributes(description=description, public_description=public_description, notify_emails=notify_emails, color=color, position=position, backstage_id=backstage_id, external_id=external_id, opsgenie_team_id=opsgenie_team_id, cortex_id=cortex_id, service_now_ci_sys_id=service_now_ci_sys_id, environment_ids=environment_ids, service_ids=service_ids, owner_group_ids=owner_group_ids, owner_user_ids=owner_user_ids, slack_channels=slack_channels, slack_aliases=slack_aliases) if any(v is not None for v in [description, public_description, notify_emails, color, position, backstage_id, external_id, opsgenie_team_id, cortex_id, service_now_ci_sys_id, environment_ids, service_ids, owner_group_ids, owner_user_ids, slack_channels, slack_aliases]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_functionality: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/functionalities/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/functionalities/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_functionality")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_functionality", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_functionality",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Functionalities
@mcp.tool()
async def delete_functionality(id_: str = Field(..., alias="id", description="The unique identifier of the functionality to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a functionality by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteFunctionalityRequest(
            path=_models.DeleteFunctionalityRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_functionality: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/functionalities/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/functionalities/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_functionality")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_functionality", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_functionality",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Functionalities
@mcp.tool()
async def get_functionality_incidents_chart(
    id_: str = Field(..., alias="id", description="The unique identifier of the functionality for which to retrieve incident chart data."),
    period: str = Field(..., description="The time period for which to retrieve incident data. Specify the desired time range to filter incidents in the chart (e.g., last 7 days, last month, custom date range)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a chart visualization of incidents for a specific functionality over a defined time period. This helps track incident trends and patterns for a given functionality."""

    # Construct request model with validation
    try:
        _request = _models.GetFunctionalityIncidentsChartRequest(
            path=_models.GetFunctionalityIncidentsChartRequestPath(id_=id_),
            query=_models.GetFunctionalityIncidentsChartRequestQuery(period=period)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_functionality_incidents_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/functionalities/{id}/incidents_chart", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/functionalities/{id}/incidents_chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_functionality_incidents_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_functionality_incidents_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_functionality_incidents_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Functionalities
@mcp.tool()
async def get_functionality_uptime_chart(
    id_: str = Field(..., alias="id", description="The unique identifier of the functionality for which to retrieve the uptime chart."),
    period: str | None = Field(None, description="The time period for the uptime chart data (e.g., day, week, month, year). If not specified, a default period will be used."),
) -> dict[str, Any] | ToolResult:
    """Retrieve an uptime chart for a specific functionality, showing availability metrics over a selected time period."""

    # Construct request model with validation
    try:
        _request = _models.GetFunctionalityUptimeChartRequest(
            path=_models.GetFunctionalityUptimeChartRequestPath(id_=id_),
            query=_models.GetFunctionalityUptimeChartRequestQuery(period=period)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_functionality_uptime_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/functionalities/{id}/uptime_chart", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/functionalities/{id}/uptime_chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_functionality_uptime_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_functionality_uptime_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_functionality_uptime_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: WorkflowTasks
@mcp.tool()
async def list_workflow_tasks(
    workflow_id: str = Field(..., description="The unique identifier of the workflow containing the tasks to list."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., assignees, dependencies). Reduces need for additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of tasks to return per page. Adjust to balance between response size and number of requests needed."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of tasks within a specific workflow. Use pagination parameters to control result size and navigate through large task sets."""

    # Construct request model with validation
    try:
        _request = _models.ListWorkflowTasksRequest(
            path=_models.ListWorkflowTasksRequestPath(workflow_id=workflow_id),
            query=_models.ListWorkflowTasksRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflow_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workflows/{workflow_id}/workflow_tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workflows/{workflow_id}/workflow_tasks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflow_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflow_tasks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflow_tasks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: WorkflowTasks
@mcp.tool()
async def create_workflow_task(
    workflow_id: str = Field(..., description="The unique identifier of the workflow to which this task will be added."),
    type_: Literal["workflow_tasks"] = Field(..., alias="type", description="The resource type identifier for this operation, which must be set to 'workflow_tasks'."),
    task_params: _models.AddActionItemTaskParams | _models.UpdateActionItemTaskParams | _models.AddRoleTaskParams | _models.AddSlackBookmarkTaskParams | _models.AddTeamTaskParams | _models.AddToTimelineTaskParams | _models.ArchiveSlackChannelsTaskParams | _models.AttachDatadogDashboardsTaskParams | _models.AutoAssignRoleOpsgenieTaskParams | _models.AutoAssignRoleRootlyTaskParams | _models.AutoAssignRolePagerdutyTaskParams | _models.UpdatePagerdutyIncidentTaskParams | _models.CreatePagerdutyStatusUpdateTaskParams | _models.CreatePagertreeAlertTaskParams | _models.UpdatePagertreeAlertTaskParams | _models.AutoAssignRoleVictorOpsTaskParams | _models.CallPeopleTaskParams | _models.CreateAirtableTableRecordTaskParams | _models.CreateAsanaSubtaskTaskParams | _models.CreateAsanaTaskTaskParams | _models.CreateConfluencePageTaskParams | _models.CreateDatadogNotebookTaskParams | _models.CreateCodaPageTaskParams | _models.CreateDropboxPaperPageTaskParams | _models.CreateGithubIssueTaskParams | _models.CreateGitlabIssueTaskParams | _models.CreateOutlookEventTaskParams | _models.CreateGoogleCalendarEventTaskParams | _models.UpdateGoogleDocsPageTaskParams | _models.UpdateCodaPageTaskParams | _models.UpdateGoogleCalendarEventTaskParams | _models.CreateSharepointPageTaskParams | _models.CreateGoogleDocsPageTaskParams | _models.CreateGoogleDocsPermissionsTaskParams | _models.RemoveGoogleDocsPermissionsTaskParams | _models.CreateQuipPageTaskParams | _models.CreateGoogleMeetingTaskParams | _models.CreateGoToMeetingTaskParams | _models.CreateIncidentTaskParams | _models.CreateIncidentPostmortemTaskParams | _models.CreateJiraIssueTaskParams | _models.CreateJiraSubtaskTaskParams | _models.CreateLinearIssueTaskParams | _models.CreateLinearSubtaskIssueTaskParams | _models.CreateLinearIssueCommentTaskParams | _models.CreateMicrosoftTeamsMeetingTaskParams | _models.CreateMicrosoftTeamsChannelTaskParams | _models.AddMicrosoftTeamsTabTaskParams | _models.ArchiveMicrosoftTeamsChannelsTaskParams | _models.RenameMicrosoftTeamsChannelTaskParams | _models.InviteToMicrosoftTeamsChannelTaskParams | _models.CreateNotionPageTaskParams | _models.SendMicrosoftTeamsMessageTaskParams | _models.SendMicrosoftTeamsBlocksTaskParams | _models.UpdateNotionPageTaskParams | _models.CreateServiceNowIncidentTaskParams | _models.CreateShortcutStoryTaskParams | _models.CreateShortcutTaskTaskParams | _models.CreateTrelloCardTaskParams | _models.CreateWebexMeetingTaskParams | _models.CreateZendeskTicketTaskParams | _models.CreateZendeskJiraLinkTaskParams | _models.CreateClickupTaskTaskParams | _models.CreateMotionTaskTaskParams | _models.CreateZoomMeetingTaskParams | _models.GetGithubCommitsTaskParams | _models.GetGitlabCommitsTaskParams | _models.GetPulsesTaskParams | _models.GetAlertsTaskParams | _models.HttpClientTaskParams | _models.InviteToSlackChannelOpsgenieTaskParams | _models.InviteToSlackChannelRootlyTaskParams | _models.InviteToSlackChannelPagerdutyTaskParams | _models.InviteToSlackChannelTaskParams | _models.InviteToSlackChannelVictorOpsTaskParams | _models.PageOpsgenieOnCallRespondersTaskParams | _models.CreateOpsgenieAlertTaskParams | _models.UpdateOpsgenieAlertTaskParams | _models.UpdateOpsgenieIncidentTaskParams | _models.PageRootlyOnCallRespondersTaskParams | _models.PagePagerdutyOnCallRespondersTaskParams | _models.PageVictorOpsOnCallRespondersTaskParams | _models.UpdateVictorOpsIncidentTaskParams | _models.PrintTaskParams | _models.PublishIncidentTaskParams | _models.RedisClientTaskParams | _models.RenameSlackChannelTaskParams | _models.ChangeSlackChannelPrivacyTaskParams | _models.RunCommandHerokuTaskParams | _models.SendEmailTaskParams | _models.SendDashboardReportTaskParams | _models.CreateSlackChannelTaskParams | _models.SendSlackMessageTaskParams | _models.SendSmsTaskParams | _models.SendWhatsappMessageTaskParams | _models.SnapshotDatadogGraphTaskParams | _models.SnapshotGrafanaDashboardTaskParams | _models.SnapshotLookerLookTaskParams | _models.SnapshotNewRelicGraphTaskParams | _models.TweetTwitterMessageTaskParams | _models.UpdateAirtableTableRecordTaskParams | _models.UpdateAsanaTaskTaskParams | _models.UpdateGithubIssueTaskParams | _models.UpdateGitlabIssueTaskParams | _models.UpdateIncidentTaskParams | _models.UpdateIncidentPostmortemTaskParams | _models.UpdateJiraIssueTaskParams | _models.UpdateLinearIssueTaskParams | _models.UpdateServiceNowIncidentTaskParams | _models.UpdateShortcutStoryTaskParams | _models.UpdateShortcutTaskTaskParams | _models.UpdateSlackChannelTopicTaskParams | _models.UpdateStatusTaskParams | _models.UpdateIncidentStatusTimestampTaskParams | _models.UpdateTrelloCardTaskParams | _models.UpdateClickupTaskTaskParams | _models.UpdateMotionTaskTaskParams | _models.UpdateZendeskTicketTaskParams | _models.UpdateAttachedAlertsTaskParams | _models.TriggerWorkflowTaskParams | _models.SendSlackBlocksTaskParams | _models.GeniusCreateOpenaiChatCompletionTaskParams | _models.GeniusCreateWatsonxChatCompletionTaskParams | _models.GeniusCreateGoogleGeminiChatCompletionTaskParams | _models.GeniusCreateAnthropicChatCompletionTaskParams = Field(..., description="Configuration parameters specific to this task's type and behavior. Structure and required fields depend on the task implementation."),
    position: int | None = Field(None, description="The sequential position where this task should be placed within the workflow. Tasks are executed in position order."),
    skip_on_failure: bool | None = Field(None, description="When enabled, the workflow will skip this task if any previous tasks in the workflow have failed, allowing for conditional execution based on upstream success."),
    enabled: bool | None = Field(None, description="Controls whether this task is active and will execute when the workflow runs. Defaults to enabled."),
) -> dict[str, Any] | ToolResult:
    """Creates a new task within a workflow. The task can be positioned in the workflow sequence and configured with execution behavior settings like failure handling and enable/disable status."""

    # Construct request model with validation
    try:
        _request = _models.CreateWorkflowTaskRequest(
            path=_models.CreateWorkflowTaskRequestPath(workflow_id=workflow_id),
            body=_models.CreateWorkflowTaskRequestBody(data=_models.CreateWorkflowTaskRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateWorkflowTaskRequestBodyDataAttributes(position=position, skip_on_failure=skip_on_failure, enabled=enabled, task_params=task_params)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_workflow_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workflows/{workflow_id}/workflow_tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workflows/{workflow_id}/workflow_tasks"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_workflow_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_workflow_task", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_workflow_task",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: WorkflowTasks
@mcp.tool()
async def get_workflow_task(id_: str = Field(..., alias="id", description="The unique identifier of the workflow task to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific workflow task by its unique identifier. Use this to fetch detailed information about a single task within a workflow."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkflowTaskRequest(
            path=_models.GetWorkflowTaskRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workflow_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workflow_tasks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workflow_tasks/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workflow_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workflow_task", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workflow_task",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: WorkflowTasks
@mcp.tool()
async def update_workflow_task(
    id_: str = Field(..., alias="id", description="The unique identifier of the workflow task to update."),
    type_: Literal["workflow_tasks"] = Field(..., alias="type", description="The resource type identifier, which must be 'workflow_tasks' to specify this is a workflow task resource."),
    position: int | None = Field(None, description="The execution order position of this task within the workflow. Lower positions execute first."),
    skip_on_failure: bool | None = Field(None, description="When enabled, the workflow will skip this task and continue to the next one if any failures occur during execution."),
    enabled: bool | None = Field(None, description="Controls whether this task is active in the workflow. Disabled tasks are skipped during execution. Defaults to true (enabled)."),
    task_params: _models.AddActionItemTaskParams | _models.UpdateActionItemTaskParams | _models.AddRoleTaskParams | _models.AddSlackBookmarkTaskParams | _models.AddTeamTaskParams | _models.AddToTimelineTaskParams | _models.ArchiveSlackChannelsTaskParams | _models.AttachDatadogDashboardsTaskParams | _models.AutoAssignRoleOpsgenieTaskParams | _models.AutoAssignRoleRootlyTaskParams | _models.AutoAssignRolePagerdutyTaskParams | _models.UpdatePagerdutyIncidentTaskParams | _models.CreatePagerdutyStatusUpdateTaskParams | _models.CreatePagertreeAlertTaskParams | _models.UpdatePagertreeAlertTaskParams | _models.AutoAssignRoleVictorOpsTaskParams | _models.CallPeopleTaskParams | _models.CreateAirtableTableRecordTaskParams | _models.CreateAsanaSubtaskTaskParams | _models.CreateAsanaTaskTaskParams | _models.CreateConfluencePageTaskParams | _models.CreateDatadogNotebookTaskParams | _models.CreateCodaPageTaskParams | _models.CreateDropboxPaperPageTaskParams | _models.CreateGithubIssueTaskParams | _models.CreateGitlabIssueTaskParams | _models.CreateOutlookEventTaskParams | _models.CreateGoogleCalendarEventTaskParams | _models.UpdateGoogleDocsPageTaskParams | _models.UpdateCodaPageTaskParams | _models.UpdateGoogleCalendarEventTaskParams | _models.CreateSharepointPageTaskParams | _models.CreateGoogleDocsPageTaskParams | _models.CreateGoogleDocsPermissionsTaskParams | _models.RemoveGoogleDocsPermissionsTaskParams | _models.CreateQuipPageTaskParams | _models.CreateGoogleMeetingTaskParams | _models.CreateGoToMeetingTaskParams | _models.CreateIncidentTaskParams | _models.CreateIncidentPostmortemTaskParams | _models.CreateJiraIssueTaskParams | _models.CreateJiraSubtaskTaskParams | _models.CreateLinearIssueTaskParams | _models.CreateLinearSubtaskIssueTaskParams | _models.CreateLinearIssueCommentTaskParams | _models.CreateMicrosoftTeamsMeetingTaskParams | _models.CreateMicrosoftTeamsChannelTaskParams | _models.AddMicrosoftTeamsTabTaskParams | _models.ArchiveMicrosoftTeamsChannelsTaskParams | _models.RenameMicrosoftTeamsChannelTaskParams | _models.InviteToMicrosoftTeamsChannelTaskParams | _models.CreateNotionPageTaskParams | _models.SendMicrosoftTeamsMessageTaskParams | _models.SendMicrosoftTeamsBlocksTaskParams | _models.UpdateNotionPageTaskParams | _models.CreateServiceNowIncidentTaskParams | _models.CreateShortcutStoryTaskParams | _models.CreateShortcutTaskTaskParams | _models.CreateTrelloCardTaskParams | _models.CreateWebexMeetingTaskParams | _models.CreateZendeskTicketTaskParams | _models.CreateZendeskJiraLinkTaskParams | _models.CreateClickupTaskTaskParams | _models.CreateMotionTaskTaskParams | _models.CreateZoomMeetingTaskParams | _models.GetGithubCommitsTaskParams | _models.GetGitlabCommitsTaskParams | _models.GetPulsesTaskParams | _models.GetAlertsTaskParams | _models.HttpClientTaskParams | _models.InviteToSlackChannelOpsgenieTaskParams | _models.InviteToSlackChannelRootlyTaskParams | _models.InviteToSlackChannelPagerdutyTaskParams | _models.InviteToSlackChannelTaskParams | _models.InviteToSlackChannelVictorOpsTaskParams | _models.PageOpsgenieOnCallRespondersTaskParams | _models.CreateOpsgenieAlertTaskParams | _models.UpdateOpsgenieAlertTaskParams | _models.UpdateOpsgenieIncidentTaskParams | _models.PageRootlyOnCallRespondersTaskParams | _models.PagePagerdutyOnCallRespondersTaskParams | _models.PageVictorOpsOnCallRespondersTaskParams | _models.UpdateVictorOpsIncidentTaskParams | _models.PrintTaskParams | _models.PublishIncidentTaskParams | _models.RedisClientTaskParams | _models.RenameSlackChannelTaskParams | _models.ChangeSlackChannelPrivacyTaskParams | _models.RunCommandHerokuTaskParams | _models.SendEmailTaskParams | _models.SendDashboardReportTaskParams | _models.CreateSlackChannelTaskParams | _models.SendSlackMessageTaskParams | _models.SendSmsTaskParams | _models.SendWhatsappMessageTaskParams | _models.SnapshotDatadogGraphTaskParams | _models.SnapshotGrafanaDashboardTaskParams | _models.SnapshotLookerLookTaskParams | _models.SnapshotNewRelicGraphTaskParams | _models.TweetTwitterMessageTaskParams | _models.UpdateAirtableTableRecordTaskParams | _models.UpdateAsanaTaskTaskParams | _models.UpdateGithubIssueTaskParams | _models.UpdateGitlabIssueTaskParams | _models.UpdateIncidentTaskParams | _models.UpdateIncidentPostmortemTaskParams | _models.UpdateJiraIssueTaskParams | _models.UpdateLinearIssueTaskParams | _models.UpdateServiceNowIncidentTaskParams | _models.UpdateShortcutStoryTaskParams | _models.UpdateShortcutTaskTaskParams | _models.UpdateSlackChannelTopicTaskParams | _models.UpdateStatusTaskParams | _models.UpdateIncidentStatusTimestampTaskParams | _models.UpdateTrelloCardTaskParams | _models.UpdateClickupTaskTaskParams | _models.UpdateMotionTaskTaskParams | _models.UpdateZendeskTicketTaskParams | _models.UpdateAttachedAlertsTaskParams | _models.TriggerWorkflowTaskParams | _models.SendSlackBlocksTaskParams | _models.GeniusCreateOpenaiChatCompletionTaskParams | _models.GeniusCreateWatsonxChatCompletionTaskParams | _models.GeniusCreateGoogleGeminiChatCompletionTaskParams | _models.GeniusCreateAnthropicChatCompletionTaskParams | None = Field(None, description="Task-specific configuration parameters. Structure and content depend on the task type being configured."),
) -> dict[str, Any] | ToolResult:
    """Update a specific workflow task configuration by its ID. Modify task properties such as execution position, failure handling behavior, enabled status, and task-specific parameters."""

    # Construct request model with validation
    try:
        _request = _models.UpdateWorkflowTaskRequest(
            path=_models.UpdateWorkflowTaskRequestPath(id_=id_),
            body=_models.UpdateWorkflowTaskRequestBody(data=_models.UpdateWorkflowTaskRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateWorkflowTaskRequestBodyDataAttributes(position=position, skip_on_failure=skip_on_failure, enabled=enabled, task_params=task_params) if any(v is not None for v in [position, skip_on_failure, enabled, task_params]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_workflow_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workflow_tasks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workflow_tasks/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_workflow_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_workflow_task", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_workflow_task",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: WorkflowTasks
@mcp.tool()
async def delete_workflow_task(id_: str = Field(..., alias="id", description="The unique identifier of the workflow task to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific workflow task by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWorkflowTaskRequest(
            path=_models.DeleteWorkflowTaskRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_workflow_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workflow_tasks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workflow_tasks/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_workflow_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_workflow_task", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_workflow_task",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: WorkflowFormFieldConditions
@mcp.tool()
async def list_workflow_form_field_conditions(
    workflow_id: str = Field(..., description="The unique identifier of the workflow for which to retrieve form field conditions."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., field references, condition rules). Specify which associations should be populated to reduce additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use this to navigate through large result sets."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of results to return per page. Adjust this to control the size of each paginated response."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all form field conditions configured for a specific workflow. Form field conditions define rules that control the visibility, requirement status, or behavior of form fields based on other field values."""

    # Construct request model with validation
    try:
        _request = _models.ListWorkflowFormFieldConditionsRequest(
            path=_models.ListWorkflowFormFieldConditionsRequestPath(workflow_id=workflow_id),
            query=_models.ListWorkflowFormFieldConditionsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflow_form_field_conditions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workflows/{workflow_id}/form_field_conditions", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workflows/{workflow_id}/form_field_conditions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflow_form_field_conditions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflow_form_field_conditions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflow_form_field_conditions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: WorkflowFormFieldConditions
@mcp.tool()
async def get_workflow_form_field_condition(id_: str = Field(..., alias="id", description="The unique identifier of the workflow form field condition to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific workflow form field condition by its unique identifier. Use this to fetch the details of a condition that controls the visibility or behavior of a form field within a workflow."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkflowFormFieldConditionRequest(
            path=_models.GetWorkflowFormFieldConditionRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workflow_form_field_condition: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workflow_form_field_conditions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workflow_form_field_conditions/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workflow_form_field_condition")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workflow_form_field_condition", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workflow_form_field_condition",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: WorkflowGroups
@mcp.tool()
async def list_workflow_groups(
    include: str | None = Field(None, description="Comma-separated list of related fields to include in the response for expanded context (e.g., metadata, configuration details)."),
    page_number: int | None = Field(None, alias="pagenumber", description="Page number for pagination, starting from 1. Use with page[size] to navigate through large result sets."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of workflow groups to return per page. Adjust to control result set size for pagination."),
    filter_kind: str | None = Field(None, alias="filterkind", description="Filter results by workflow group kind or type. Specify the exact kind value to narrow results."),
    filter_expanded: bool | None = Field(None, alias="filterexpanded", description="Filter results by expansion state. Set to true to show only expanded groups, or false for collapsed groups."),
    filter_position: int | None = Field(None, alias="filterposition", description="Filter results by position or order index. Useful for retrieving groups at specific positions in a sequence."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of workflow groups with optional filtering by kind, expansion state, and position. Use this to discover available workflow groups and their configurations."""

    # Construct request model with validation
    try:
        _request = _models.ListWorkflowGroupsRequest(
            query=_models.ListWorkflowGroupsRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_kind=filter_kind, filter_expanded=filter_expanded, filter_position=filter_position)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflow_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/workflow_groups"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workflow_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workflow_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workflow_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: WorkflowGroups
@mcp.tool()
async def get_workflow_group(id_: str = Field(..., alias="id", description="The unique identifier of the workflow group to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific workflow group by its unique identifier. Use this operation to fetch detailed information about a workflow group configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkflowGroupRequest(
            path=_models.GetWorkflowGroupRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workflow_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workflow_groups/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workflow_groups/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workflow_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workflow_group", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workflow_group",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: WorkflowGroups
@mcp.tool()
async def update_workflow_group(
    id_: str = Field(..., alias="id", description="The unique identifier of the workflow group to update."),
    type_: Literal["workflow_groups"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'workflow_groups' to specify this is a workflow group resource."),
    kind: Literal["simple", "incident", "post_mortem", "action_item", "pulse", "alert"] | None = Field(None, description="The category or classification of the workflow group. Choose from: simple, incident, post_mortem, action_item, pulse, or alert."),
    description: str | None = Field(None, description="A human-readable description explaining the purpose or contents of the workflow group."),
    icon: str | None = Field(None, description="An emoji character displayed as a visual indicator next to the workflow group name."),
    expanded: bool | None = Field(None, description="A boolean flag indicating whether the workflow group should be displayed in an expanded (true) or collapsed (false) state."),
    position: int | None = Field(None, description="The display order of the workflow group relative to other groups, where lower numbers appear first."),
) -> dict[str, Any] | ToolResult:
    """Update a specific workflow group's configuration, including its kind, description, icon, expanded state, and position. Changes are applied to the workflow group identified by the provided id."""

    # Construct request model with validation
    try:
        _request = _models.UpdateWorkflowGroupRequest(
            path=_models.UpdateWorkflowGroupRequestPath(id_=id_),
            body=_models.UpdateWorkflowGroupRequestBody(data=_models.UpdateWorkflowGroupRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateWorkflowGroupRequestBodyDataAttributes(kind=kind, description=description, icon=icon, expanded=expanded, position=position) if any(v is not None for v in [kind, description, icon, expanded, position]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_workflow_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workflow_groups/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workflow_groups/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_workflow_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_workflow_group", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_workflow_group",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: WorkflowGroups
@mcp.tool()
async def delete_workflow_group(id_: str = Field(..., alias="id", description="The unique identifier of the workflow group to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a workflow group and all its associated data by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWorkflowGroupRequest(
            path=_models.DeleteWorkflowGroupRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_workflow_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workflow_groups/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workflow_groups/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_workflow_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_workflow_group", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_workflow_group",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: WorkflowRuns
@mcp.tool()
async def list_workflow_runs(
    workflow_id: str = Field(..., description="The unique identifier of the workflow for which to list runs."),
    include: Literal["genius_task_runs"] | None = Field(None, description="Optional comma-separated list of related data to include in the response. Use 'genius_task_runs' to include detailed task execution information for each workflow run."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use this to navigate through large result sets."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of workflow runs to return per page. Adjust this to control the size of each paginated response."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of workflow runs for a specified workflow. Optionally include related task run data to get detailed execution information."""

    # Construct request model with validation
    try:
        _request = _models.ListWorkflowRunsRequest(
            path=_models.ListWorkflowRunsRequestPath(workflow_id=workflow_id),
            query=_models.ListWorkflowRunsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workflow_runs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workflows/{workflow_id}/workflow_runs", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workflows/{workflow_id}/workflow_runs"
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

# Tags: WorkflowRuns
@mcp.tool()
async def create_workflow_run(
    workflow_id: str = Field(..., description="The unique identifier of the workflow for which to create a run."),
    type_: Literal["workflow_runs"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'workflow_runs' to specify the type of object being created."),
    attributes: _models.CreateWorkflowRunBodyDataAttributesV0 | _models.CreateWorkflowRunBodyDataAttributesV1 | _models.CreateWorkflowRunBodyDataAttributesV2 | _models.CreateWorkflowRunBodyDataAttributesV3 | _models.CreateWorkflowRunBodyDataAttributesV4 | _models.CreateWorkflowRunBodyDataAttributesV5 = Field(..., description="An object containing the workflow run configuration and execution parameters, such as input variables, scheduling options, or runtime settings."),
) -> dict[str, Any] | ToolResult:
    """Initiates a new workflow run for the specified workflow. This creates an execution instance with the provided configuration and attributes."""

    # Construct request model with validation
    try:
        _request = _models.CreateWorkflowRunRequest(
            path=_models.CreateWorkflowRunRequestPath(workflow_id=workflow_id),
            body=_models.CreateWorkflowRunRequestBody(data=_models.CreateWorkflowRunRequestBodyData(type_=type_, attributes=attributes))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_workflow_run: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workflows/{workflow_id}/workflow_runs", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workflows/{workflow_id}/workflow_runs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_workflow_run")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_workflow_run", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_workflow_run",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflows
@mcp.tool()
async def get_workflow(
    id_: str = Field(..., alias="id", description="The unique identifier of the workflow to retrieve."),
    include: Literal["form_field_conditions", "genius_tasks", "genius_workflow_runs"] | None = Field(None, description="Comma-separated list of related resources to include in the response. Valid options are form_field_conditions, genius_tasks, and genius_workflow_runs."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific workflow by its unique identifier. Optionally include related data such as form field conditions, genius tasks, or workflow run history."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkflowRequest(
            path=_models.GetWorkflowRequestPath(id_=id_),
            query=_models.GetWorkflowRequestQuery(include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workflow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workflows/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workflows/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workflows
@mcp.tool()
async def delete_workflow(id_: str = Field(..., alias="id", description="The unique identifier of the workflow to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a workflow by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWorkflowRequest(
            path=_models.DeleteWorkflowRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_workflow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workflows/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workflows/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_workflow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_workflow", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_workflow",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Heartbeats
@mcp.tool()
async def list_heartbeats(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., metadata, details). Reduces the need for additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of heartbeats to return per page. Adjust to balance between response size and number of requests needed."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of heartbeats. Use pagination parameters to control the number of results and navigate through pages."""

    # Construct request model with validation
    try:
        _request = _models.ListHeartbeatsRequest(
            query=_models.ListHeartbeatsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_heartbeats: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/heartbeats"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_heartbeats")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_heartbeats", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_heartbeats",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Heartbeats
@mcp.tool()
async def create_heartbeat(
    type_: Literal["heartbeats"] = Field(..., alias="type", description="The resource type identifier; must be set to 'heartbeats' to indicate this is a heartbeat resource."),
    name: str = Field(..., description="A human-readable name for the heartbeat to identify it in the system."),
    alert_summary: str = Field(..., description="A summary message that will be included in alerts triggered when the heartbeat fails to renew within the specified interval."),
    interval: int = Field(..., description="The numeric duration value that, combined with interval_unit, defines how frequently the heartbeat must be renewed to remain active."),
    interval_unit: Literal["seconds", "minutes", "hours"] = Field(..., description="The unit of time for the interval duration; must be one of: seconds, minutes, or hours."),
    notification_target_id: str = Field(..., description="The identifier of the recipient (user, group, service, or escalation policy) that will receive alerts when the heartbeat expires."),
    notification_target_type: Literal["User", "Group", "Service", "EscalationPolicy"] = Field(..., description="The type of notification target; must be one of: User, Group, Service, or EscalationPolicy."),
    description: str | None = Field(None, description="An optional detailed description providing additional context about the heartbeat's purpose or monitoring scope."),
    alert_urgency_id: str | None = Field(None, description="Optional identifier for the urgency level assigned to alerts triggered by heartbeat expiration. If not specified, a default urgency level is used."),
    enabled: bool | None = Field(None, description="Optional boolean flag to enable or disable alert triggering when the heartbeat expires. Defaults to true if not specified."),
) -> dict[str, Any] | ToolResult:
    """Creates a new heartbeat to monitor system health and trigger alerts when the heartbeat expires. Heartbeats are periodic signals that must be renewed; if not received within the specified interval, alerts are sent to the configured notification target."""

    # Construct request model with validation
    try:
        _request = _models.CreateHeartbeatRequest(
            body=_models.CreateHeartbeatRequestBody(data=_models.CreateHeartbeatRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateHeartbeatRequestBodyDataAttributes(name=name, description=description, alert_summary=alert_summary, alert_urgency_id=alert_urgency_id, interval=interval, interval_unit=interval_unit, notification_target_id=notification_target_id, notification_target_type=notification_target_type, enabled=enabled)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_heartbeat: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/heartbeats"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_heartbeat")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_heartbeat", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_heartbeat",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Heartbeats
@mcp.tool()
async def get_heartbeat(id_: str = Field(..., alias="id", description="The unique identifier of the heartbeat to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific heartbeat record by its unique identifier. Use this to fetch details about a particular heartbeat event or status check."""

    # Construct request model with validation
    try:
        _request = _models.GetHeartbeatRequest(
            path=_models.GetHeartbeatRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_heartbeat: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/heartbeats/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/heartbeats/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_heartbeat")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_heartbeat", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_heartbeat",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Heartbeats
@mcp.tool()
async def update_heartbeat(
    id_: str = Field(..., alias="id", description="The unique identifier of the heartbeat to update."),
    type_: Literal["heartbeats"] = Field(..., alias="type", description="The resource type, which must be 'heartbeats' to identify this as a heartbeat resource."),
    description: str | None = Field(None, description="A human-readable description of the heartbeat's purpose or monitoring context."),
    alert_summary: str | None = Field(None, description="A brief summary of the alerts that will be triggered when this heartbeat expires or fails."),
    alert_urgency_id: str | None = Field(None, description="The urgency level ID assigned to alerts triggered by heartbeat expiration, determining priority and escalation behavior."),
    interval: int | None = Field(None, description="The numeric interval value that, combined with interval_unit, defines how frequently the heartbeat should be received."),
    interval_unit: Literal["seconds", "minutes", "hours"] | None = Field(None, description="The time unit for the heartbeat interval. Valid options are seconds, minutes, or hours."),
    notification_target_id: str | None = Field(None, description="The ID of the user, group, service, or escalation policy that should receive notifications when the heartbeat expires."),
    notification_target_type: Literal["User", "Group", "Service", "EscalationPolicy"] | None = Field(None, description="The type of notification target. Must be one of: User, Group, Service, or EscalationPolicy."),
    enabled: bool | None = Field(None, description="Whether alerts should be triggered when this heartbeat expires. Set to false to temporarily disable alerting without removing the heartbeat configuration."),
) -> dict[str, Any] | ToolResult:
    """Update an existing heartbeat configuration by ID. Modify monitoring intervals, alert settings, and notification targets for a specific heartbeat."""

    # Construct request model with validation
    try:
        _request = _models.UpdateHeartbeatRequest(
            path=_models.UpdateHeartbeatRequestPath(id_=id_),
            body=_models.UpdateHeartbeatRequestBody(data=_models.UpdateHeartbeatRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateHeartbeatRequestBodyDataAttributes(description=description, alert_summary=alert_summary, alert_urgency_id=alert_urgency_id, interval=interval, interval_unit=interval_unit, notification_target_id=notification_target_id, notification_target_type=notification_target_type, enabled=enabled) if any(v is not None for v in [description, alert_summary, alert_urgency_id, interval, interval_unit, notification_target_id, notification_target_type, enabled]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_heartbeat: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/heartbeats/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/heartbeats/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_heartbeat")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_heartbeat", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_heartbeat",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Heartbeats
@mcp.tool()
async def delete_heartbeat(id_: str = Field(..., alias="id", description="The unique identifier of the heartbeat to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a heartbeat record by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteHeartbeatRequest(
            path=_models.DeleteHeartbeatRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_heartbeat: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/heartbeats/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/heartbeats/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_heartbeat")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_heartbeat", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_heartbeat",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentActionItems
@mcp.tool()
async def list_incident_action_items(
    incident_id: str = Field(..., description="The unique identifier of the incident for which to retrieve action items."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., assignee details, timestamps). Specify which fields or nested objects should be populated."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use this to navigate through multiple pages of results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of action items to return per page. Adjust this to control the size of each paginated response."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of action items associated with a specific incident. Use this to view all tasks and follow-ups that need to be completed for incident resolution."""

    # Construct request model with validation
    try:
        _request = _models.ListIncidentActionItemsRequest(
            path=_models.ListIncidentActionItemsRequestPath(incident_id=incident_id),
            query=_models.ListIncidentActionItemsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_incident_action_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{incident_id}/action_items", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{incident_id}/action_items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_incident_action_items")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_incident_action_items", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_incident_action_items",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentActionItems
@mcp.tool()
async def create_incident_action_item(
    incident_id: str = Field(..., description="The unique identifier of the incident to which this action item belongs."),
    type_: Literal["incident_action_items"] = Field(..., alias="type", description="The resource type identifier; must be set to 'incident_action_items'."),
    summary: str = Field(..., description="A brief title or headline for the action item that summarizes what needs to be done."),
    description: str | None = Field(None, description="Additional details or context about the action item, providing more information beyond the summary."),
    kind: Literal["task", "follow_up"] | None = Field(None, description="Categorizes the action item as either a task (work to be completed) or a follow-up (item to revisit or check on)."),
    assigned_to_user_id: int | None = Field(None, description="The user ID of the person responsible for completing this action item."),
    assigned_to_group_ids: list[str] | None = Field(None, description="A list of group IDs to assign this action item to; multiple groups can be assigned simultaneously."),
    priority: Literal["high", "medium", "low"] | None = Field(None, description="The urgency level of the action item: high, medium, or low priority."),
    status: Literal["open", "in_progress", "cancelled", "done"] | None = Field(None, description="The current state of the action item: open (not started), in_progress (actively being worked on), cancelled (no longer needed), or done (completed)."),
    due_date: str | None = Field(None, description="The target completion date for the action item in ISO 8601 format (YYYY-MM-DD)."),
    jira_issue_key: str | None = Field(None, description="An optional reference to a Jira issue key for integration with Jira tracking systems."),
) -> dict[str, Any] | ToolResult:
    """Creates a new action item associated with an incident to track tasks or follow-ups that need to be completed. Action items can be assigned to users or groups, prioritized, and tracked through their lifecycle."""

    # Construct request model with validation
    try:
        _request = _models.CreateIncidentActionItemRequest(
            path=_models.CreateIncidentActionItemRequestPath(incident_id=incident_id),
            body=_models.CreateIncidentActionItemRequestBody(data=_models.CreateIncidentActionItemRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateIncidentActionItemRequestBodyDataAttributes(summary=summary, description=description, kind=kind, assigned_to_user_id=assigned_to_user_id, assigned_to_group_ids=assigned_to_group_ids, priority=priority, status=status, due_date=due_date, jira_issue_key=jira_issue_key)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_incident_action_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{incident_id}/action_items", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{incident_id}/action_items"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_incident_action_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_incident_action_item", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_incident_action_item",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentActionItems
@mcp.tool()
async def get_incident_action_item(id_: str = Field(..., alias="id", description="The unique identifier of the incident action item to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific incident action item by its unique identifier. Use this to fetch details about a single action item associated with an incident."""

    # Construct request model with validation
    try:
        _request = _models.GetIncidentActionItemsRequest(
            path=_models.GetIncidentActionItemsRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_incident_action_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/action_items/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/action_items/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_incident_action_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_incident_action_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_incident_action_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentActionItems
@mcp.tool()
async def update_incident_action_item(
    id_: str = Field(..., alias="id", description="The unique identifier of the action item to update."),
    type_: Literal["incident_action_items"] = Field(..., alias="type", description="The resource type identifier; must be 'incident_action_items'."),
    summary: str | None = Field(None, description="A brief title or headline for the action item."),
    description: str | None = Field(None, description="Detailed information about the action item and what needs to be done."),
    kind: Literal["task", "follow_up"] | None = Field(None, description="Categorizes the action item as either a 'task' (work to be completed) or 'follow_up' (follow-up activity)."),
    assigned_to_user_id: int | None = Field(None, description="The ID of the user to assign this action item to. Only one user can be assigned."),
    assigned_to_group_ids: list[str] | None = Field(None, description="A list of group IDs to assign this action item to. Multiple groups can be assigned simultaneously."),
    priority: Literal["high", "medium", "low"] | None = Field(None, description="The urgency level of the action item: 'high', 'medium', or 'low'."),
    status: Literal["open", "in_progress", "cancelled", "done"] | None = Field(None, description="The current state of the action item: 'open' (not started), 'in_progress' (actively being worked on), 'cancelled' (abandoned), or 'done' (completed)."),
    due_date: str | None = Field(None, description="The target completion date for the action item in ISO 8601 format (YYYY-MM-DD)."),
    jira_issue_key: str | None = Field(None, description="The Jira issue key to link this action item to an external Jira ticket (e.g., 'PROJ-123')."),
) -> dict[str, Any] | ToolResult:
    """Update a specific incident action item by its ID. Modify properties such as summary, description, assignment, priority, status, due date, and Jira integration."""

    # Construct request model with validation
    try:
        _request = _models.UpdateIncidentActionItemRequest(
            path=_models.UpdateIncidentActionItemRequestPath(id_=id_),
            body=_models.UpdateIncidentActionItemRequestBody(data=_models.UpdateIncidentActionItemRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateIncidentActionItemRequestBodyDataAttributes(summary=summary, description=description, kind=kind, assigned_to_user_id=assigned_to_user_id, assigned_to_group_ids=assigned_to_group_ids, priority=priority, status=status, due_date=due_date, jira_issue_key=jira_issue_key) if any(v is not None for v in [summary, description, kind, assigned_to_user_id, assigned_to_group_ids, priority, status, due_date, jira_issue_key]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_incident_action_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/action_items/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/action_items/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_incident_action_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_incident_action_item", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_incident_action_item",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentActionItems
@mcp.tool()
async def delete_incident_action_item(id_: str = Field(..., alias="id", description="The unique identifier of the incident action item to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific incident action item by its unique identifier. This operation removes the action item record from the system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteIncidentActionItemRequest(
            path=_models.DeleteIncidentActionItemRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_incident_action_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/action_items/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/action_items/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_incident_action_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_incident_action_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_incident_action_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentActionItems
@mcp.tool()
async def list_action_items(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., incident, assignee). Reduces the need for follow-up requests."),
    page_number: int | None = Field(None, alias="pagenumber", description="Page number for pagination, starting from 1. Use with page[size] to navigate through large result sets."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of action items to return per page. Adjust to balance response size and number of requests needed."),
    filter_kind: str | None = Field(None, alias="filterkind", description="Filter results by action item kind or type (e.g., investigation, remediation, follow-up)."),
    filter_priority: str | None = Field(None, alias="filterpriority", description="Filter results by priority level (e.g., critical, high, medium, low)."),
    filter_status: str | None = Field(None, alias="filterstatus", description="Filter results by action item status (e.g., open, in_progress, completed, cancelled)."),
    filter_incident_status: str | None = Field(None, alias="filterincident_status", description="Filter results by the status of the associated incident (e.g., investigating, resolved, monitoring)."),
    sort: str | None = Field(None, description="Sort results by a specified field and direction (e.g., created_at:desc, priority:asc). Consult API documentation for sortable fields."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all action items for your organization with optional filtering by kind, priority, status, and incident status. Supports pagination and relationship inclusion."""

    # Construct request model with validation
    try:
        _request = _models.ListAllIncidentActionItemsRequest(
            query=_models.ListAllIncidentActionItemsRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_kind=filter_kind, filter_priority=filter_priority, filter_status=filter_status, filter_incident_status=filter_incident_status, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_action_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/action_items"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_action_items")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_action_items", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_action_items",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentEventFunctionalities
@mcp.tool()
async def list_incident_event_functionalities(
    incident_event_id: str = Field(..., description="The unique identifier of the incident event for which to list associated functionalities."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response for expanded context."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of functionalities to return per page. Adjust this value to control result batch size."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of functionalities associated with a specific incident event. Use pagination parameters to control result size and navigation."""

    # Construct request model with validation
    try:
        _request = _models.ListIncidentEventFunctionalitiesRequest(
            path=_models.ListIncidentEventFunctionalitiesRequestPath(incident_event_id=incident_event_id),
            query=_models.ListIncidentEventFunctionalitiesRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_incident_event_functionalities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/events/{incident_event_id}/functionalities", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/events/{incident_event_id}/functionalities"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_incident_event_functionalities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_incident_event_functionalities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_incident_event_functionalities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentEventFunctionalities
@mcp.tool()
async def add_functionality_to_incident_event(
    incident_event_id: str = Field(..., description="The unique identifier of the incident event to which the functionality will be added."),
    attributes_incident_event_id: str = Field(..., alias="attributesIncident_event_id", description="The unique identifier of the incident event being referenced in the request body (must match the incident_event_id in the path)."),
    type_: Literal["incident_event_functionalities"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'incident_event_functionalities' to indicate this is an incident event functionality resource."),
    functionality_id: str = Field(..., description="The unique identifier of the functionality being associated with this incident event."),
    status: Literal["operational", "partial_outage", "major_outage"] = Field(..., description="The current operational status of the affected functionality. Must be one of: operational (functioning normally), partial_outage (degraded performance), or major_outage (completely unavailable)."),
) -> dict[str, Any] | ToolResult:
    """Associates a functionality with an incident event and sets its operational status. Use this to track which functionalities are affected by an incident and their current impact level."""

    # Construct request model with validation
    try:
        _request = _models.CreateIncidentEventFunctionalityRequest(
            path=_models.CreateIncidentEventFunctionalityRequestPath(incident_event_id=incident_event_id),
            body=_models.CreateIncidentEventFunctionalityRequestBody(data=_models.CreateIncidentEventFunctionalityRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateIncidentEventFunctionalityRequestBodyDataAttributes(incident_event_id=attributes_incident_event_id, functionality_id=functionality_id, status=status)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_functionality_to_incident_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/events/{incident_event_id}/functionalities", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/events/{incident_event_id}/functionalities"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_functionality_to_incident_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_functionality_to_incident_event", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_functionality_to_incident_event",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentEventFunctionalities
@mcp.tool()
async def get_incident_event_functionality(id_: str = Field(..., alias="id", description="The unique identifier of the incident event functionality to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific incident event functionality by its unique identifier. Use this to fetch detailed information about a particular functionality associated with incident events."""

    # Construct request model with validation
    try:
        _request = _models.GetIncidentEventFunctionalitiesRequest(
            path=_models.GetIncidentEventFunctionalitiesRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_incident_event_functionality: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_event_functionalities/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_event_functionalities/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_incident_event_functionality")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_incident_event_functionality", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_incident_event_functionality",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentEventFunctionalities
@mcp.tool()
async def update_incident_event_functionality(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident event functionality to update."),
    type_: Literal["incident_event_functionalities"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'incident_event_functionalities' to specify the type of resource being updated."),
    status: Literal["operational", "partial_outage", "major_outage"] = Field(..., description="The current operational status of the affected functionality. Must be one of: 'operational' (fully functional), 'partial_outage' (degraded service), or 'major_outage' (service unavailable)."),
) -> dict[str, Any] | ToolResult:
    """Update the status of a specific incident event functionality. Use this to report changes in the operational status of affected services or features during an incident."""

    # Construct request model with validation
    try:
        _request = _models.UpdateIncidentEventFunctionalityRequest(
            path=_models.UpdateIncidentEventFunctionalityRequestPath(id_=id_),
            body=_models.UpdateIncidentEventFunctionalityRequestBody(data=_models.UpdateIncidentEventFunctionalityRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateIncidentEventFunctionalityRequestBodyDataAttributes(status=status)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_incident_event_functionality: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_event_functionalities/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_event_functionalities/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_incident_event_functionality")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_incident_event_functionality", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_incident_event_functionality",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentEventFunctionalities
@mcp.tool()
async def delete_incident_event_functionality(id_: str = Field(..., alias="id", description="The unique identifier of the incident event functionality to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific incident event functionality by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteIncidentEventFunctionalityRequest(
            path=_models.DeleteIncidentEventFunctionalityRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_incident_event_functionality: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_event_functionalities/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_event_functionalities/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_incident_event_functionality")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_incident_event_functionality", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_incident_event_functionality",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentEventServices
@mcp.tool()
async def list_incident_event_services(
    incident_event_id: str = Field(..., description="The unique identifier of the incident event for which to list associated services."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., service details, metadata). Specify which associations to expand for richer context."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of services to return per page. Adjust this value to control result set size for pagination."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of services associated with a specific incident event. Use pagination parameters to control result set size and navigation."""

    # Construct request model with validation
    try:
        _request = _models.ListIncidentEventServicesRequest(
            path=_models.ListIncidentEventServicesRequestPath(incident_event_id=incident_event_id),
            query=_models.ListIncidentEventServicesRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_incident_event_services: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/events/{incident_event_id}/services", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/events/{incident_event_id}/services"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_incident_event_services")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_incident_event_services", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_incident_event_services",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentEventServices
@mcp.tool()
async def add_service_to_incident_event(
    incident_event_id: str = Field(..., description="The unique identifier of the incident event to which the service will be added."),
    attributes_incident_event_id: str = Field(..., alias="attributesIncident_event_id", description="The unique identifier of the incident event being referenced in the request body (must match the incident_event_id in the path)."),
    type_: Literal["incident_event_services"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'incident_event_services' to indicate this is an incident event service resource."),
    service_id: str = Field(..., description="The unique identifier of the service to be associated with this incident event."),
    status: Literal["operational", "partial_outage", "major_outage"] = Field(..., description="The operational status of the affected service. Must be one of: operational (service functioning normally), partial_outage (service experiencing degraded performance), or major_outage (service unavailable)."),
) -> dict[str, Any] | ToolResult:
    """Associates a service with an incident event and sets its operational status. Use this to track which services are affected by an incident and their current status."""

    # Construct request model with validation
    try:
        _request = _models.CreateIncidentEventServiceRequest(
            path=_models.CreateIncidentEventServiceRequestPath(incident_event_id=incident_event_id),
            body=_models.CreateIncidentEventServiceRequestBody(data=_models.CreateIncidentEventServiceRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateIncidentEventServiceRequestBodyDataAttributes(incident_event_id=attributes_incident_event_id, service_id=service_id, status=status)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_service_to_incident_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/events/{incident_event_id}/services", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/events/{incident_event_id}/services"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_service_to_incident_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_service_to_incident_event", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_service_to_incident_event",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentEventServices
@mcp.tool()
async def get_incident_event_service(id_: str = Field(..., alias="id", description="The unique identifier of the incident event service to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific incident event service by its unique identifier. Use this to fetch detailed information about a single incident event service."""

    # Construct request model with validation
    try:
        _request = _models.GetIncidentEventServicesRequest(
            path=_models.GetIncidentEventServicesRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_incident_event_service: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_event_services/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_event_services/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_incident_event_service")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_incident_event_service", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_incident_event_service",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentEventServices
@mcp.tool()
async def update_incident_event_service_status(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident event service to update."),
    type_: Literal["incident_event_services"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'incident_event_services' to specify the type of resource being updated."),
    status: Literal["operational", "partial_outage", "major_outage"] = Field(..., description="The current operational status of the affected service. Choose from: operational (service running normally), partial_outage (service degraded or partially unavailable), or major_outage (service completely unavailable)."),
) -> dict[str, Any] | ToolResult:
    """Update the operational status of a specific incident event service. Use this to reflect the current impact level of a service during an incident."""

    # Construct request model with validation
    try:
        _request = _models.UpdateIncidentEventServiceRequest(
            path=_models.UpdateIncidentEventServiceRequestPath(id_=id_),
            body=_models.UpdateIncidentEventServiceRequestBody(data=_models.UpdateIncidentEventServiceRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateIncidentEventServiceRequestBodyDataAttributes(status=status)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_incident_event_service_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_event_services/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_event_services/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_incident_event_service_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_incident_event_service_status", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_incident_event_service_status",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentEventServices
@mcp.tool()
async def delete_incident_event_service(id_: str = Field(..., alias="id", description="The unique identifier of the incident event service to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific incident event service by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteIncidentEventServiceRequest(
            path=_models.DeleteIncidentEventServiceRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_incident_event_service: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_event_services/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_event_services/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_incident_event_service")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_incident_event_service", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_incident_event_service",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentEvents
@mcp.tool()
async def list_incident_events(
    incident_id: str = Field(..., description="The unique identifier of the incident for which to retrieve events."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., user details, attachments). Reduces the need for additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through large result sets."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of events to return per page. Adjust to balance response size and number of requests needed."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of events associated with a specific incident. Events are ordered chronologically and may include status changes, assignments, comments, and other incident activity."""

    # Construct request model with validation
    try:
        _request = _models.ListIncidentEventsRequest(
            path=_models.ListIncidentEventsRequestPath(incident_id=incident_id),
            query=_models.ListIncidentEventsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_incident_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{incident_id}/events", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{incident_id}/events"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_incident_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_incident_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_incident_events",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentEvents
@mcp.tool()
async def create_incident_event(
    incident_id: str = Field(..., description="The unique identifier of the incident to which this event belongs."),
    type_: Literal["incident_events"] = Field(..., alias="type", description="The type of event being created. Must be set to 'incident_events' to classify this as an incident event record."),
    event: str = Field(..., description="A concise summary or description of what occurred in this incident event."),
    visibility: Literal["internal", "external"] | None = Field(None, description="Controls who can view this event. Set to 'internal' for team-only visibility or 'external' to include external stakeholders. Defaults to internal if not specified."),
) -> dict[str, Any] | ToolResult:
    """Creates a new event record for an incident, capturing event details with optional visibility control. Use this to log incident updates, status changes, or other significant incident occurrences."""

    # Construct request model with validation
    try:
        _request = _models.CreateIncidentEventRequest(
            path=_models.CreateIncidentEventRequestPath(incident_id=incident_id),
            body=_models.CreateIncidentEventRequestBody(data=_models.CreateIncidentEventRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateIncidentEventRequestBodyDataAttributes(event=event, visibility=visibility)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_incident_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{incident_id}/events", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{incident_id}/events"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_incident_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_incident_event", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_incident_event",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentEvents
@mcp.tool()
async def get_incident_event(id_: str = Field(..., alias="id", description="The unique identifier of the incident event to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific incident event by its unique identifier. Use this to fetch detailed information about a single incident event."""

    # Construct request model with validation
    try:
        _request = _models.GetIncidentEventsRequest(
            path=_models.GetIncidentEventsRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_incident_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/events/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/events/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_incident_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_incident_event", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_incident_event",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentEvents
@mcp.tool()
async def update_incident_event(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident event to update."),
    type_: Literal["incident_events"] = Field(..., alias="type", description="The resource type, which must be 'incident_events' to identify this as an incident event resource."),
    event: str | None = Field(None, description="A brief summary or title describing the incident event."),
    visibility: Literal["internal", "external"] | None = Field(None, description="Controls who can view this incident event. Set to 'internal' for restricted visibility or 'external' for broader access."),
) -> dict[str, Any] | ToolResult:
    """Update a specific incident event by its ID. Modify the event summary and/or visibility settings for an existing incident event."""

    # Construct request model with validation
    try:
        _request = _models.UpdateIncidentEventRequest(
            path=_models.UpdateIncidentEventRequestPath(id_=id_),
            body=_models.UpdateIncidentEventRequestBody(data=_models.UpdateIncidentEventRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateIncidentEventRequestBodyDataAttributes(event=event, visibility=visibility) if any(v is not None for v in [event, visibility]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_incident_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/events/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/events/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_incident_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_incident_event", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_incident_event",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentEvents
@mcp.tool()
async def delete_incident_event(id_: str = Field(..., alias="id", description="The unique identifier of the incident event to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific incident event by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteIncidentEventRequest(
            path=_models.DeleteIncidentEventRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_incident_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/events/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/events/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_incident_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_incident_event", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_incident_event",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentFeedbacks
@mcp.tool()
async def list_incident_feedbacks(
    incident_id: str = Field(..., description="The unique identifier of the incident for which to retrieve feedbacks."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., user details, metadata). Specify which associations should be expanded in the results."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve for paginated results, starting from page 1. Use this to navigate through multiple pages of feedbacks."),
    page_size: int | None = Field(None, alias="pagesize", description="The maximum number of feedback records to return per page. Controls the size of each paginated result set."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of feedback entries associated with a specific incident. Use pagination parameters to control result size and navigate through feedback records."""

    # Construct request model with validation
    try:
        _request = _models.ListIncidentFeedbacksRequest(
            path=_models.ListIncidentFeedbacksRequestPath(incident_id=incident_id),
            query=_models.ListIncidentFeedbacksRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_incident_feedbacks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{incident_id}/feedbacks", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{incident_id}/feedbacks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_incident_feedbacks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_incident_feedbacks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_incident_feedbacks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentFeedbacks
@mcp.tool()
async def create_incident_feedback(
    incident_id: str = Field(..., description="The unique identifier of the incident for which feedback is being submitted."),
    type_: Literal["incident_feedbacks"] = Field(..., alias="type", description="The type of feedback being submitted. Must be set to 'incident_feedbacks' to classify this as incident feedback."),
    feedback: str = Field(..., description="The feedback content describing the user's comments or observations about the incident."),
    rating: Literal[4, 3, 2, 1, 0] = Field(..., description="A numeric rating for the incident on a scale of 0 to 4, where 0 is the lowest and 4 is the highest."),
    anonymous: bool | None = Field(None, description="Whether the feedback should be submitted anonymously, hiding the identity of the person providing it."),
) -> dict[str, Any] | ToolResult:
    """Submit feedback for an incident with a rating and optional anonymity. This allows users to provide structured feedback on incident handling and resolution."""

    # Construct request model with validation
    try:
        _request = _models.CreateIncidentFeedbackRequest(
            path=_models.CreateIncidentFeedbackRequestPath(incident_id=incident_id),
            body=_models.CreateIncidentFeedbackRequestBody(data=_models.CreateIncidentFeedbackRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateIncidentFeedbackRequestBodyDataAttributes(feedback=feedback, rating=rating, anonymous=anonymous)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_incident_feedback: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{incident_id}/feedbacks", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{incident_id}/feedbacks"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_incident_feedback")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_incident_feedback", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_incident_feedback",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentFeedbacks
@mcp.tool()
async def get_incident_feedback(id_: str = Field(..., alias="id", description="The unique identifier of the incident feedback to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific incident feedback by its unique identifier. Use this to fetch detailed information about a single feedback entry associated with an incident."""

    # Construct request model with validation
    try:
        _request = _models.GetIncidentFeedbacksRequest(
            path=_models.GetIncidentFeedbacksRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_incident_feedback: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/feedbacks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/feedbacks/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_incident_feedback")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_incident_feedback", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_incident_feedback",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentFeedbacks
@mcp.tool()
async def update_incident_feedback(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident feedback to update."),
    type_: Literal["incident_feedbacks"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'incident_feedbacks' to specify this is an incident feedback resource."),
    feedback: str | None = Field(None, description="The feedback text or comment describing the incident experience. Optional field that can be updated independently."),
    rating: Literal[4, 3, 2, 1, 0] | None = Field(None, description="A numeric rating for the incident feedback on a scale from 0 to 4, where 0 is the lowest and 4 is the highest. Optional field that can be updated independently."),
    anonymous: bool | None = Field(None, description="A boolean flag indicating whether the feedback should be submitted anonymously. When true, the feedback is not attributed to a specific user. Optional field that can be updated independently."),
) -> dict[str, Any] | ToolResult:
    """Update an existing incident feedback record by its ID. Modify the feedback text, rating, or anonymity status of a previously submitted incident feedback."""

    # Construct request model with validation
    try:
        _request = _models.UpdateIncidentFeedbackRequest(
            path=_models.UpdateIncidentFeedbackRequestPath(id_=id_),
            body=_models.UpdateIncidentFeedbackRequestBody(data=_models.UpdateIncidentFeedbackRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateIncidentFeedbackRequestBodyDataAttributes(feedback=feedback, rating=rating, anonymous=anonymous) if any(v is not None for v in [feedback, rating, anonymous]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_incident_feedback: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/feedbacks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/feedbacks/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_incident_feedback")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_incident_feedback", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_incident_feedback",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentFormFieldSelections
@mcp.tool()
async def list_incident_form_field_selections(
    incident_id: str = Field(..., description="The unique identifier of the incident for which to retrieve form field selections."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., field definitions, metadata). Specify which associations should be populated."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of results to return per page. Defines the maximum number of form field selections in each paginated response."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all form field selections associated with a specific incident. This lists the custom form fields and their selected values for the incident."""

    # Construct request model with validation
    try:
        _request = _models.ListIncidentFormFieldSelectionsRequest(
            path=_models.ListIncidentFormFieldSelectionsRequestPath(incident_id=incident_id),
            query=_models.ListIncidentFormFieldSelectionsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_incident_form_field_selections: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{incident_id}/form_field_selections", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{incident_id}/form_field_selections"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_incident_form_field_selections")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_incident_form_field_selections", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_incident_form_field_selections",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentFormFieldSelections
@mcp.tool()
async def create_incident_form_field_selection(
    incident_id: str = Field(..., description="The unique identifier of the incident to which this form field selection will be added."),
    attributes_incident_id: str = Field(..., alias="attributesIncident_id", description="The incident ID associated with this form field selection; must match the incident_id in the URL path."),
    type_: Literal["incident_form_field_selections"] = Field(..., alias="type", description="The resource type identifier; must be set to 'incident_form_field_selections'."),
    form_field_id: str = Field(..., description="The ID of the custom form field being configured for this incident."),
    value: str | None = Field(None, description="The text value to assign to this form field selection; used for text-based custom fields."),
    selected_catalog_entity_ids: list[str] | None = Field(None, description="An array of catalog entity IDs to associate with this form field selection; order may be significant depending on field configuration."),
    selected_group_ids: list[str] | None = Field(None, description="An array of group IDs to associate with this form field selection; order may be significant depending on field configuration."),
    selected_option_ids: list[str] | None = Field(None, description="An array of custom field option IDs to associate with this form field selection; order may be significant depending on field configuration."),
    selected_service_ids: list[str] | None = Field(None, description="An array of service IDs to associate with this form field selection; order may be significant depending on field configuration."),
    selected_functionality_ids: list[str] | None = Field(None, description="An array of functionality IDs to associate with this form field selection; order may be significant depending on field configuration."),
    selected_user_ids: list[int] | None = Field(None, description="An array of user IDs to associate with this form field selection; order may be significant depending on field configuration."),
) -> dict[str, Any] | ToolResult:
    """Creates a new form field selection for an incident, allowing you to assign values to custom fields such as text inputs, catalog entities, groups, options, services, functionalities, or users."""

    # Construct request model with validation
    try:
        _request = _models.CreateIncidentFormFieldSelectionRequest(
            path=_models.CreateIncidentFormFieldSelectionRequestPath(incident_id=incident_id),
            body=_models.CreateIncidentFormFieldSelectionRequestBody(data=_models.CreateIncidentFormFieldSelectionRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateIncidentFormFieldSelectionRequestBodyDataAttributes(incident_id=attributes_incident_id, form_field_id=form_field_id, value=value, selected_catalog_entity_ids=selected_catalog_entity_ids, selected_group_ids=selected_group_ids, selected_option_ids=selected_option_ids, selected_service_ids=selected_service_ids, selected_functionality_ids=selected_functionality_ids, selected_user_ids=selected_user_ids)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_incident_form_field_selection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{incident_id}/form_field_selections", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{incident_id}/form_field_selections"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_incident_form_field_selection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_incident_form_field_selection", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_incident_form_field_selection",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentFormFieldSelections
@mcp.tool()
async def get_incident_form_field_selection(id_: str = Field(..., alias="id", description="The unique identifier of the incident form field selection to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific incident form field selection by its unique identifier. Use this to fetch configuration details for how form fields are selected and displayed in incident reports."""

    # Construct request model with validation
    try:
        _request = _models.GetIncidentFormFieldSelectionRequest(
            path=_models.GetIncidentFormFieldSelectionRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_incident_form_field_selection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_form_field_selections/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_form_field_selections/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_incident_form_field_selection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_incident_form_field_selection", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_incident_form_field_selection",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentRetrospectives
@mcp.tool()
async def list_incident_post_mortems(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., incident details, user information)."),
    page_number: int | None = Field(None, alias="pagenumber", description="Page number for pagination, starting from 1."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of post-mortems to return per page."),
    filter_status: str | None = Field(None, alias="filterstatus", description="Filter results by post-mortem status (e.g., draft, published, archived)."),
    filter_type: str | None = Field(None, alias="filtertype", description="Filter results by incident type classification."),
    filter_user_id: int | None = Field(None, alias="filteruser_id", description="Filter results to post-mortems created by a specific user ID."),
    filter_started_at__gte: str | None = Field(None, alias="filterstarted_atgte", description="Filter to post-mortems with incident start time greater than or equal to this timestamp (ISO 8601 format)."),
    filter_started_at__lte: str | None = Field(None, alias="filterstarted_atlte", description="Filter to post-mortems with incident start time less than or equal to this timestamp (ISO 8601 format)."),
    filter_mitigated_at__gte: str | None = Field(None, alias="filtermitigated_atgte", description="Filter to post-mortems with mitigation time greater than or equal to this timestamp (ISO 8601 format)."),
    filter_mitigated_at__lte: str | None = Field(None, alias="filtermitigated_atlte", description="Filter to post-mortems with mitigation time less than or equal to this timestamp (ISO 8601 format)."),
    filter_resolved_at__gte: str | None = Field(None, alias="filterresolved_atgte", description="Filter to post-mortems with resolution time greater than or equal to this timestamp (ISO 8601 format)."),
    filter_resolved_at__lte: str | None = Field(None, alias="filterresolved_atlte", description="Filter to post-mortems with resolution time less than or equal to this timestamp (ISO 8601 format)."),
    sort: str | None = Field(None, description="Sort results by a specified field in ascending or descending order (e.g., created_at, status)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of incident post-mortems (retrospectives) with optional filtering by status, type, user, and date ranges, plus sorting capabilities."""

    # Construct request model with validation
    try:
        _request = _models.ListIncidentPostMortemsRequest(
            query=_models.ListIncidentPostMortemsRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_status=filter_status, filter_type=filter_type, filter_user_id=filter_user_id, filter_started_at__gte=filter_started_at__gte, filter_started_at__lte=filter_started_at__lte, filter_mitigated_at__gte=filter_mitigated_at__gte, filter_mitigated_at__lte=filter_mitigated_at__lte, filter_resolved_at__gte=filter_resolved_at__gte, filter_resolved_at__lte=filter_resolved_at__lte, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_incident_post_mortems: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/post_mortems"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_incident_post_mortems")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_incident_post_mortems", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_incident_post_mortems",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentRetrospectives
@mcp.tool()
async def get_incident_postmortem(id_: str = Field(..., alias="id", description="The unique identifier of the incident postmortem to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a detailed incident postmortem (retrospective) by its unique identifier. Use this to access the analysis and findings from a completed incident investigation."""

    # Construct request model with validation
    try:
        _request = _models.ListIncidentPostmortemRequest(
            path=_models.ListIncidentPostmortemRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_incident_postmortem: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/post_mortems/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/post_mortems/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_incident_postmortem")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_incident_postmortem", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_incident_postmortem",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentRetrospectives
@mcp.tool()
async def update_incident_postmortem(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident postmortem to update."),
    type_: Literal["incident_post_mortems"] = Field(..., alias="type", description="The resource type identifier; must be set to 'incident_post_mortems'."),
    title: str | None = Field(None, description="The title or heading of the incident postmortem document."),
    status: Literal["draft", "published"] | None = Field(None, description="The publication state of the postmortem; either 'draft' for work-in-progress or 'published' for finalized versions."),
    show_timeline: bool | None = Field(None, description="Whether to display the timeline of events in the postmortem."),
    show_timeline_trail: bool | None = Field(None, description="Whether to include trail events (audit/change history) in the timeline view."),
    show_timeline_genius: bool | None = Field(None, description="Whether to include workflow or automation events in the timeline view."),
    show_timeline_tasks: bool | None = Field(None, description="Whether to include task entries in the timeline view."),
    show_timeline_action_items: bool | None = Field(None, description="Whether to include action items and follow-ups in the timeline view."),
    show_groups_impacted: bool | None = Field(None, description="Whether to display information about affected groups or services in the postmortem."),
    show_alerts_attached: bool | None = Field(None, description="Whether to display alerts that were attached to or triggered during the incident."),
    show_action_items: bool | None = Field(None, description="Whether to include action items and follow-up tasks in the postmortem document."),
    cause_ids: list[str] | None = Field(None, description="A list of cause identifiers to associate with this incident postmortem, linking root causes to the incident."),
) -> dict[str, Any] | ToolResult:
    """Update an incident postmortem document by ID, allowing modifications to its content, visibility settings, and associated metadata. Use this to refine postmortem details, change publication status, or adjust which timeline elements and impact information are displayed."""

    # Construct request model with validation
    try:
        _request = _models.UpdateIncidentPostmortemRequest(
            path=_models.UpdateIncidentPostmortemRequestPath(id_=id_),
            body=_models.UpdateIncidentPostmortemRequestBody(data=_models.UpdateIncidentPostmortemRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateIncidentPostmortemRequestBodyDataAttributes(title=title, status=status, show_timeline=show_timeline, show_timeline_trail=show_timeline_trail, show_timeline_genius=show_timeline_genius, show_timeline_tasks=show_timeline_tasks, show_timeline_action_items=show_timeline_action_items, show_groups_impacted=show_groups_impacted, show_alerts_attached=show_alerts_attached, show_action_items=show_action_items, cause_ids=cause_ids) if any(v is not None for v in [title, status, show_timeline, show_timeline_trail, show_timeline_genius, show_timeline_tasks, show_timeline_action_items, show_groups_impacted, show_alerts_attached, show_action_items, cause_ids]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_incident_postmortem: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/post_mortems/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/post_mortems/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_incident_postmortem")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_incident_postmortem", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_incident_postmortem",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentRetrospectiveSteps
@mcp.tool()
async def get_incident_retrospective_step(id_: str = Field(..., alias="id", description="The unique identifier of the incident retrospective step to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific incident retrospective step by its unique identifier. Use this to fetch details about a particular step within an incident retrospective."""

    # Construct request model with validation
    try:
        _request = _models.GetIncidentRetrospectiveStepRequest(
            path=_models.GetIncidentRetrospectiveStepRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_incident_retrospective_step: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_retrospective_steps/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_retrospective_steps/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_incident_retrospective_step")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_incident_retrospective_step", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_incident_retrospective_step",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentRetrospectiveSteps
@mcp.tool()
async def update_incident_retrospective_step(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident retrospective step to update."),
    type_: Literal["incident_retrospective_steps"] = Field(..., alias="type", description="The resource type identifier, which must be 'incident_retrospective_steps' to specify the entity being updated."),
    title: str | None = Field(None, description="The name or title of the retrospective step."),
    description: str | None = Field(None, description="A detailed description of the retrospective step and its purpose."),
    due_date: str | None = Field(None, description="The target completion date for this step, specified in ISO 8601 format."),
    position: int | None = Field(None, description="The ordinal position of this step within the retrospective sequence, where lower numbers appear first."),
    skippable: bool | None = Field(None, description="Whether this step can be skipped during the retrospective process without blocking completion."),
    status: Literal["todo", "in_progress", "completed", "skipped"] | None = Field(None, description="The current state of the step: 'todo' (not started), 'in_progress' (actively being worked on), 'completed' (finished), or 'skipped' (bypassed)."),
) -> dict[str, Any] | ToolResult:
    """Update a specific incident retrospective step within an incident retrospective. Modify step details such as title, description, due date, position, and completion status."""

    # Construct request model with validation
    try:
        _request = _models.UpdateIncidentRetrospectiveStepRequest(
            path=_models.UpdateIncidentRetrospectiveStepRequestPath(id_=id_),
            body=_models.UpdateIncidentRetrospectiveStepRequestBody(data=_models.UpdateIncidentRetrospectiveStepRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateIncidentRetrospectiveStepRequestBodyDataAttributes(title=title, description=description, due_date=due_date, position=position, skippable=skippable, status=status) if any(v is not None for v in [title, description, due_date, position, skippable, status]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_incident_retrospective_step: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_retrospective_steps/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_retrospective_steps/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_incident_retrospective_step")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_incident_retrospective_step", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_incident_retrospective_step",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentRoleTasks
@mcp.tool()
async def list_incident_role_tasks(
    incident_role_id: str = Field(..., description="The unique identifier of the incident role for which to list associated tasks."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., assignees, status details). Reduces need for additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of tasks to return per page. Adjust to balance response size and number of requests needed."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all tasks assigned to a specific incident role. Use pagination to control result size and offset."""

    # Construct request model with validation
    try:
        _request = _models.ListIncidentRoleTasksRequest(
            path=_models.ListIncidentRoleTasksRequestPath(incident_role_id=incident_role_id),
            query=_models.ListIncidentRoleTasksRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_incident_role_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_roles/{incident_role_id}/incident_role_tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_roles/{incident_role_id}/incident_role_tasks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_incident_role_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_incident_role_tasks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_incident_role_tasks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentRoleTasks
@mcp.tool()
async def create_incident_role_task(
    incident_role_id: str = Field(..., description="The unique identifier of the incident role to which this task will be assigned."),
    type_: Literal["incident_role_tasks"] = Field(..., alias="type", description="The resource type identifier for incident role tasks. Must be set to 'incident_role_tasks'."),
    task: str = Field(..., description="A concise title or description of the work to be completed as part of this incident role task."),
    description: str | None = Field(None, description="Additional context or details about the task, including any relevant background information or acceptance criteria."),
    priority: Literal["high", "medium", "low"] | None = Field(None, description="The urgency level of the task. Choose from high, medium, or low priority to help with task sequencing and resource allocation."),
) -> dict[str, Any] | ToolResult:
    """Creates a new task within an incident role to track specific work items. Tasks help organize and prioritize actions needed to resolve the incident."""

    # Construct request model with validation
    try:
        _request = _models.CreateIncidentRoleTaskRequest(
            path=_models.CreateIncidentRoleTaskRequestPath(incident_role_id=incident_role_id),
            body=_models.CreateIncidentRoleTaskRequestBody(data=_models.CreateIncidentRoleTaskRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateIncidentRoleTaskRequestBodyDataAttributes(task=task, description=description, priority=priority)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_incident_role_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_roles/{incident_role_id}/incident_role_tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_roles/{incident_role_id}/incident_role_tasks"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_incident_role_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_incident_role_task", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_incident_role_task",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentRoleTasks
@mcp.tool()
async def get_incident_role_task(id_: str = Field(..., alias="id", description="The unique identifier of the incident role task to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific incident role task by its unique identifier. Use this to fetch details about a particular task assigned to a role within an incident."""

    # Construct request model with validation
    try:
        _request = _models.GetIncidentRoleTaskRequest(
            path=_models.GetIncidentRoleTaskRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_incident_role_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_role_tasks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_role_tasks/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_incident_role_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_incident_role_task", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_incident_role_task",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentRoleTasks
@mcp.tool()
async def update_incident_role_task(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident role task to update."),
    type_: Literal["incident_role_tasks"] = Field(..., alias="type", description="The resource type identifier, which must be 'incident_role_tasks' to specify the resource being updated."),
    task: str | None = Field(None, description="The task name or title for the incident role task."),
    description: str | None = Field(None, description="A detailed description providing context and information about the incident role task."),
    priority: Literal["high", "medium", "low"] | None = Field(None, description="The priority level for the incident role task: 'high' for urgent items, 'medium' for standard priority, or 'low' for non-urgent items."),
) -> dict[str, Any] | ToolResult:
    """Update an existing incident role task by its ID, allowing modification of task details, description, and priority level."""

    # Construct request model with validation
    try:
        _request = _models.UpdateIncidentRoleTaskRequest(
            path=_models.UpdateIncidentRoleTaskRequestPath(id_=id_),
            body=_models.UpdateIncidentRoleTaskRequestBody(data=_models.UpdateIncidentRoleTaskRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateIncidentRoleTaskRequestBodyDataAttributes(task=task, description=description, priority=priority) if any(v is not None for v in [task, description, priority]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_incident_role_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_role_tasks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_role_tasks/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_incident_role_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_incident_role_task", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_incident_role_task",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentRoleTasks
@mcp.tool()
async def delete_incident_role_task(id_: str = Field(..., alias="id", description="The unique identifier of the incident role task to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific incident role task by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteIncidentRoleTaskRequest(
            path=_models.DeleteIncidentRoleTaskRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_incident_role_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_role_tasks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_role_tasks/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_incident_role_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_incident_role_task", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_incident_role_task",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentRoles
@mcp.tool()
async def list_incident_roles(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., permissions, metadata). Specify which associations should be populated alongside each role."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve when paginating through results. Use with page[size] to control pagination."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of incident roles to return per page. Adjust this value to control the size of each paginated response."),
    filter_enabled: bool | None = Field(None, alias="filterenabled", description="Filter results to show only enabled or disabled incident roles. Set to true for active roles only, or false for inactive roles."),
    sort: str | None = Field(None, description="Sort the results by one or more fields (e.g., name, created_at). Prefix field names with a minus sign (-) to sort in descending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of incident roles with optional filtering and sorting capabilities. Use this to view all available roles that can be assigned during incident management."""

    # Construct request model with validation
    try:
        _request = _models.ListIncidentRolesRequest(
            query=_models.ListIncidentRolesRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_enabled=filter_enabled, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_incident_roles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/incident_roles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_incident_roles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_incident_roles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_incident_roles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentRoles
@mcp.tool()
async def create_incident_role(
    type_: Literal["incident_roles"] = Field(..., alias="type", description="The resource type identifier; must be set to 'incident_roles' to specify this is an incident role resource."),
    name: str = Field(..., description="The display name for the incident role (e.g., 'Incident Commander', 'Communications Lead'). Used to identify the role throughout the incident management system."),
    summary: str | None = Field(None, description="A brief summary of the incident role's purpose and key responsibilities."),
    description: str | None = Field(None, description="A detailed description of the incident role, including specific duties, authority levels, and escalation procedures."),
    position: int | None = Field(None, description="The ordinal position of this role in the incident role hierarchy or display order. Lower numbers typically appear first in lists."),
    optional: bool | None = Field(None, description="Whether this role is optional during incident response. When true, incidents can proceed without assigning someone to this role."),
    enabled: bool | None = Field(None, description="Whether this role is currently active and available for assignment. Disabled roles cannot be assigned to new incidents."),
    allow_multi_user_assignment: bool | None = Field(None, description="Whether multiple team members can be simultaneously assigned to this role during a single incident. When false, only one person can hold the role at a time."),
) -> dict[str, Any] | ToolResult:
    """Creates a new incident role that can be assigned to team members during incident response. Incident roles define responsibilities and permissions within the incident management workflow."""

    # Construct request model with validation
    try:
        _request = _models.CreateIncidentRoleRequest(
            body=_models.CreateIncidentRoleRequestBody(data=_models.CreateIncidentRoleRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateIncidentRoleRequestBodyDataAttributes(name=name, summary=summary, description=description, position=position, optional=optional, enabled=enabled, allow_multi_user_assignment=allow_multi_user_assignment)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_incident_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/incident_roles"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_incident_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_incident_role", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_incident_role",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentRoles
@mcp.tool()
async def get_incident_role(id_: str = Field(..., alias="id", description="The unique identifier of the incident role to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific incident role by its unique identifier. Use this to fetch detailed information about a particular incident role."""

    # Construct request model with validation
    try:
        _request = _models.GetIncidentRoleRequest(
            path=_models.GetIncidentRoleRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_incident_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_roles/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_roles/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_incident_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_incident_role", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_incident_role",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentRoles
@mcp.tool()
async def update_incident_role(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident role to update."),
    type_: Literal["incident_roles"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'incident_roles'."),
    summary: str | None = Field(None, description="A brief summary or title for the incident role."),
    description: str | None = Field(None, description="A detailed description of the incident role's purpose and responsibilities."),
    position: int | None = Field(None, description="The display order of this incident role relative to others, used for sorting in user interfaces."),
    optional: bool | None = Field(None, description="Whether this incident role is optional or required when assigning roles to incidents."),
    enabled: bool | None = Field(None, description="Whether this incident role is currently active and available for use."),
    allow_multi_user_assignment: bool | None = Field(None, description="Whether multiple users can be assigned to this incident role simultaneously."),
) -> dict[str, Any] | ToolResult:
    """Update an existing incident role by its ID, allowing modification of its summary, description, position, and assignment settings."""

    # Construct request model with validation
    try:
        _request = _models.UpdateIncidentRoleRequest(
            path=_models.UpdateIncidentRoleRequestPath(id_=id_),
            body=_models.UpdateIncidentRoleRequestBody(data=_models.UpdateIncidentRoleRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateIncidentRoleRequestBodyDataAttributes(summary=summary, description=description, position=position, optional=optional, enabled=enabled, allow_multi_user_assignment=allow_multi_user_assignment) if any(v is not None for v in [summary, description, position, optional, enabled, allow_multi_user_assignment]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_incident_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_roles/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_roles/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_incident_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_incident_role", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_incident_role",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentRoles
@mcp.tool()
async def delete_incident_role(id_: str = Field(..., alias="id", description="The unique identifier of the incident role to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete an incident role by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteIncidentRoleRequest(
            path=_models.DeleteIncidentRoleRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_incident_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_roles/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_roles/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_incident_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_incident_role", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_incident_role",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentStatusPageEvents
@mcp.tool()
async def list_incident_status_page_events(
    incident_id: str = Field(..., description="The unique identifier of the incident for which to retrieve status page events."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., incident details, status page information). Specify which associations to expand for richer context."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use this to navigate through results when there are many events."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of events to return per page. Adjust this to control the size of each paginated response."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of status page events associated with a specific incident. Use this to track all status updates and communications that were published for an incident."""

    # Construct request model with validation
    try:
        _request = _models.ListIncidentStatusPagesRequest(
            path=_models.ListIncidentStatusPagesRequestPath(incident_id=incident_id),
            query=_models.ListIncidentStatusPagesRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_incident_status_page_events: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{incident_id}/status-page-events", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{incident_id}/status-page-events"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_incident_status_page_events")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_incident_status_page_events", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_incident_status_page_events",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentStatusPageEvents
@mcp.tool()
async def create_incident_status_page_event(
    incident_id: str = Field(..., description="The unique identifier of the incident for which you are creating a status page event."),
    type_: Literal["incident_status_page_events"] = Field(..., alias="type", description="The type of resource being created; must be set to 'incident_status_page_events'."),
    event: str = Field(..., description="A brief summary describing the incident event (e.g., 'Service degradation detected', 'Issue resolved')."),
    status_page_id: str | None = Field(None, description="The unique identifier of the status page where this event should be posted. If omitted, the event may be posted to a default status page or require specification elsewhere."),
    status: Literal["investigating", "identified", "monitoring", "resolved", "scheduled", "in_progress", "verifying", "completed"] | None = Field(None, description="The current status of the incident event. Valid values indicate progression through the incident lifecycle: 'investigating' (initial assessment), 'identified' (root cause found), 'monitoring' (watching for stability), 'resolved' (issue fixed), 'scheduled' (planned maintenance), 'in_progress' (work underway), 'verifying' (confirming fix), or 'completed' (maintenance finished)."),
    notify_subscribers: bool | None = Field(None, description="When enabled, sends notifications to all subscribers of the status page(s) about this incident event. Defaults to false."),
    should_tweet: bool | None = Field(None, description="When enabled on Statuspage.io integrated pages, automatically publishes a tweet announcing this incident update. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Creates a new event for an incident on a status page, allowing you to post updates about incident status to subscribers and optionally publish to social media."""

    # Construct request model with validation
    try:
        _request = _models.CreateIncidentStatusPageRequest(
            path=_models.CreateIncidentStatusPageRequestPath(incident_id=incident_id),
            body=_models.CreateIncidentStatusPageRequestBody(data=_models.CreateIncidentStatusPageRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateIncidentStatusPageRequestBodyDataAttributes(event=event, status_page_id=status_page_id, status=status, notify_subscribers=notify_subscribers, should_tweet=should_tweet)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_incident_status_page_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{incident_id}/status-page-events", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{incident_id}/status-page-events"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_incident_status_page_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_incident_status_page_event", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_incident_status_page_event",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentStatusPageEvents
@mcp.tool()
async def get_incident_status_page_event(id_: str = Field(..., alias="id", description="The unique identifier of the incident status page event to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific incident status page event by its unique identifier. Use this to fetch detailed information about a particular status page event associated with an incident."""

    # Construct request model with validation
    try:
        _request = _models.GetIncidentStatusPagesRequest(
            path=_models.GetIncidentStatusPagesRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_incident_status_page_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/status-page-events/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/status-page-events/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_incident_status_page_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_incident_status_page_event", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_incident_status_page_event",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentStatusPageEvents
@mcp.tool()
async def update_incident_status_page_event(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident status page event to update."),
    type_: Literal["incident_status_page_events"] = Field(..., alias="type", description="The resource type identifier, which must be 'incident_status_page_events' to specify the event resource being updated."),
    event: str | None = Field(None, description="A brief summary describing the incident event (e.g., 'Database connection timeout', 'Service degradation resolved')."),
    status_page_id: str | None = Field(None, description="The unique identifier of the status page where this event should be posted or updated."),
    status: Literal["investigating", "identified", "monitoring", "resolved", "scheduled", "in_progress", "verifying", "completed"] | None = Field(None, description="The current phase of the incident: 'investigating' (initial assessment), 'identified' (root cause found), 'monitoring' (fix in progress), 'resolved' (issue fixed), 'scheduled' (planned maintenance), 'in_progress' (maintenance underway), 'verifying' (validating fix), or 'completed' (maintenance finished)."),
    notify_subscribers: bool | None = Field(None, description="When enabled, sends notifications to all subscribers of the status page(s) about this incident update. Defaults to false."),
    should_tweet: bool | None = Field(None, description="When enabled on Statuspage.io integrated pages, automatically publishes a tweet announcing this incident update. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Update a specific incident status page event to modify its summary, status, and notification settings. Use this to track incident progression through investigation, identification, monitoring, and resolution phases."""

    # Construct request model with validation
    try:
        _request = _models.UpdateIncidentStatusPageRequest(
            path=_models.UpdateIncidentStatusPageRequestPath(id_=id_),
            body=_models.UpdateIncidentStatusPageRequestBody(data=_models.UpdateIncidentStatusPageRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateIncidentStatusPageRequestBodyDataAttributes(event=event, status_page_id=status_page_id, status=status, notify_subscribers=notify_subscribers, should_tweet=should_tweet) if any(v is not None for v in [event, status_page_id, status, notify_subscribers, should_tweet]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_incident_status_page_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/status-page-events/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/status-page-events/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_incident_status_page_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_incident_status_page_event", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_incident_status_page_event",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentStatusPageEvents
@mcp.tool()
async def delete_status_page_event(id_: str = Field(..., alias="id", description="The unique identifier of the status page event to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a specific incident status page event. This removes the event record from the status page."""

    # Construct request model with validation
    try:
        _request = _models.DeleteIncidentStatusPageRequest(
            path=_models.DeleteIncidentStatusPageRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_status_page_event: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/status-page-events/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/status-page-events/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_status_page_event")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_status_page_event", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_status_page_event",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentTypes
@mcp.tool()
async def list_incident_types(
    include: str | None = Field(None, description="Comma-separated list of related fields to include in the response (e.g., metadata, categories). Specify which associations should be expanded in the returned incident type objects."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve for pagination, starting from 1. Use with page[size] to control result set boundaries."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of incident types to return per page. Defines the maximum number of results in each paginated response."),
    filter_color: str | None = Field(None, alias="filtercolor", description="Filter incident types by color value. Specify the exact color identifier or name to narrow results to matching incident types."),
    sort: str | None = Field(None, description="Comma-separated list of fields to sort by, with optional direction indicators (e.g., 'name,-created_at'). Controls the order of returned incident types."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of incident types, optionally filtered by color and sorted by specified fields."""

    # Construct request model with validation
    try:
        _request = _models.ListIncidentTypesRequest(
            query=_models.ListIncidentTypesRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_color=filter_color, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_incident_types: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/incident_types"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_incident_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_incident_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_incident_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentTypes
@mcp.tool()
async def create_incident_type(
    type_: Literal["incident_types"] = Field(..., alias="type", description="The resource type identifier; must be set to 'incident_types' to specify this is an incident type resource."),
    name: str = Field(..., description="The display name for the incident type; used to identify and reference this type throughout the system."),
    description: str | None = Field(None, description="A detailed explanation of the incident type's purpose and usage; helps users understand when to apply this type."),
    color: str | None = Field(None, description="A hexadecimal color code (e.g., #FF5733) used to visually distinguish this incident type in the UI."),
    position: int | None = Field(None, description="The display order of this incident type relative to others; lower numbers appear first in lists and menus."),
    notify_emails: list[str] | None = Field(None, description="A list of email addresses that will receive notifications when incidents of this type are created or updated."),
    slack_channels: list[_models.CreateIncidentTypeBodyDataAttributesSlackChannelsItem] | None = Field(None, description="A list of Slack channel identifiers or names where incident notifications will be posted for this type."),
    slack_aliases: list[_models.CreateIncidentTypeBodyDataAttributesSlackAliasesItem] | None = Field(None, description="A list of Slack aliases or shortcuts that can be used to quickly reference or create incidents of this type."),
) -> dict[str, Any] | ToolResult:
    """Creates a new incident type that can be used to categorize and manage incidents. Incident types support custom naming, visual styling, notifications, and Slack integration."""

    # Construct request model with validation
    try:
        _request = _models.CreateIncidentTypeRequest(
            body=_models.CreateIncidentTypeRequestBody(data=_models.CreateIncidentTypeRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateIncidentTypeRequestBodyDataAttributes(name=name, description=description, color=color, position=position, notify_emails=notify_emails, slack_channels=slack_channels, slack_aliases=slack_aliases)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_incident_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/incident_types"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_incident_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_incident_type", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_incident_type",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentTypes
@mcp.tool()
async def get_incident_type(id_: str = Field(..., alias="id", description="The unique identifier of the incident type to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific incident type by its unique identifier. Use this to fetch detailed information about a particular incident type configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetIncidentTypeRequest(
            path=_models.GetIncidentTypeRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_incident_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_types/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_types/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_incident_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_incident_type", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_incident_type",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentTypes
@mcp.tool()
async def update_incident_type(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident type to update."),
    type_: Literal["incident_types"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'incident_types'."),
    description: str | None = Field(None, description="A human-readable description of the incident type and its purpose."),
    color: str | None = Field(None, description="The hex color code used to visually represent this incident type in the UI."),
    position: int | None = Field(None, description="The display order of this incident type in lists and menus, where lower numbers appear first."),
    notify_emails: list[str] | None = Field(None, description="A list of email addresses that should receive notifications when incidents of this type are created or updated."),
    slack_channels: list[_models.UpdateIncidentTypeBodyDataAttributesSlackChannelsItem] | None = Field(None, description="A list of Slack channel identifiers or names where incident notifications should be posted."),
    slack_aliases: list[_models.UpdateIncidentTypeBodyDataAttributesSlackAliasesItem] | None = Field(None, description="A list of Slack user aliases or handles to mention or notify when incidents of this type occur."),
) -> dict[str, Any] | ToolResult:
    """Update an existing incident type by its ID, allowing modification of its display properties, notification settings, and associated Slack integrations."""

    # Construct request model with validation
    try:
        _request = _models.UpdateIncidentTypeRequest(
            path=_models.UpdateIncidentTypeRequestPath(id_=id_),
            body=_models.UpdateIncidentTypeRequestBody(data=_models.UpdateIncidentTypeRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateIncidentTypeRequestBodyDataAttributes(description=description, color=color, position=position, notify_emails=notify_emails, slack_channels=slack_channels, slack_aliases=slack_aliases) if any(v is not None for v in [description, color, position, notify_emails, slack_channels, slack_aliases]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_incident_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_types/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_types/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_incident_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_incident_type", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_incident_type",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: IncidentTypes
@mcp.tool()
async def delete_incident_type(id_: str = Field(..., alias="id", description="The unique identifier of the incident type to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete an incident type by its unique identifier. This action cannot be undone and will remove the incident type from the system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteIncidentTypeRequest(
            path=_models.DeleteIncidentTypeRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_incident_type: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incident_types/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incident_types/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_incident_type")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_incident_type", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_incident_type",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Incidents
@mcp.tool()
async def list_incidents(
    page_number: int | None = Field(None, alias="pagenumber", description="Page number for pagination (1-indexed). Use with page[size] to retrieve specific result sets."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of incidents per page. Determines the size of each paginated result set."),
    filter_kind: str | None = Field(None, alias="filterkind", description="Filter by incident kind (e.g., alert, event, anomaly). Narrows results to specific incident types."),
    filter_status: str | None = Field(None, alias="filterstatus", description="Filter by incident status (e.g., open, acknowledged, resolved, closed). Returns incidents matching the specified status."),
    filter_private: str | None = Field(None, alias="filterprivate", description="Filter by privacy setting. Use to show only private or public incidents."),
    filter_user_id: int | None = Field(None, alias="filteruser_id", description="Filter by user ID. Returns incidents assigned to or created by the specified user."),
    filter_severity_id: str | None = Field(None, alias="filterseverity_id", description="Filter by severity ID. Narrows results to incidents with the specified severity level."),
    filter_labels: str | None = Field(None, alias="filterlabels", description="Filter by labels. Comma-separated list of label identifiers to match incidents with those labels."),
    filter_type_ids: str | None = Field(None, alias="filtertype_ids", description="Filter by incident type IDs. Comma-separated list of type identifiers to match specific incident types."),
    filter_environment_ids: str | None = Field(None, alias="filterenvironment_ids", description="Filter by environment IDs. Comma-separated list of environment identifiers (e.g., production, staging)."),
    filter_functionality_ids: str | None = Field(None, alias="filterfunctionality_ids", description="Filter by functionality IDs. Comma-separated list of functionality identifiers affected by incidents."),
    filter_service_ids: str | None = Field(None, alias="filterservice_ids", description="Filter by service IDs. Comma-separated list of service identifiers to match incidents affecting those services."),
    filter_team_ids: str | None = Field(None, alias="filterteam_ids", description="Filter by team IDs. Comma-separated list of team identifiers responsible for or assigned to incidents."),
    filter_cause_ids: str | None = Field(None, alias="filtercause_ids", description="Filter by cause IDs. Comma-separated list of cause identifiers to match incidents with those root causes."),
    filter_custom_field_selected_option_ids: str | None = Field(None, alias="filtercustom_field_selected_option_ids", description="Filter by custom field selected option IDs. Comma-separated list of custom field option identifiers."),
    filter_updated_at__gt: str | None = Field(None, alias="filterupdated_atgt", description="Filter incidents updated after this timestamp (ISO 8601 format). Exclusive lower bound."),
    filter_updated_at__gte: str | None = Field(None, alias="filterupdated_atgte", description="Filter incidents updated on or after this timestamp (ISO 8601 format). Inclusive lower bound."),
    filter_updated_at__lt: str | None = Field(None, alias="filterupdated_atlt", description="Filter incidents updated before this timestamp (ISO 8601 format). Exclusive upper bound."),
    filter_updated_at__lte: str | None = Field(None, alias="filterupdated_atlte", description="Filter incidents updated on or before this timestamp (ISO 8601 format). Inclusive upper bound."),
    filter_started_at__gte: str | None = Field(None, alias="filterstarted_atgte", description="Filter incidents that started on or after this timestamp (ISO 8601 format). Inclusive lower bound."),
    filter_started_at__lte: str | None = Field(None, alias="filterstarted_atlte", description="Filter incidents that started on or before this timestamp (ISO 8601 format). Inclusive upper bound."),
    filter_detected_at__gt: str | None = Field(None, alias="filterdetected_atgt", description="Filter incidents detected after this timestamp (ISO 8601 format). Exclusive lower bound."),
    filter_detected_at__gte: str | None = Field(None, alias="filterdetected_atgte", description="Filter incidents detected on or after this timestamp (ISO 8601 format). Inclusive lower bound."),
    filter_detected_at__lt: str | None = Field(None, alias="filterdetected_atlt", description="Filter incidents detected before this timestamp (ISO 8601 format). Exclusive upper bound."),
    filter_detected_at__lte: str | None = Field(None, alias="filterdetected_atlte", description="Filter incidents detected on or before this timestamp (ISO 8601 format). Inclusive upper bound."),
    filter_acknowledged_at__gt: str | None = Field(None, alias="filteracknowledged_atgt", description="Filter incidents acknowledged after this timestamp (ISO 8601 format). Exclusive lower bound."),
    filter_acknowledged_at__gte: str | None = Field(None, alias="filteracknowledged_atgte", description="Filter incidents acknowledged on or after this timestamp (ISO 8601 format). Inclusive lower bound."),
    filter_acknowledged_at__lt: str | None = Field(None, alias="filteracknowledged_atlt", description="Filter incidents acknowledged before this timestamp (ISO 8601 format). Exclusive upper bound."),
    filter_acknowledged_at__lte: str | None = Field(None, alias="filteracknowledged_atlte", description="Filter incidents acknowledged on or before this timestamp (ISO 8601 format). Inclusive upper bound."),
    filter_mitigated_at__gte: str | None = Field(None, alias="filtermitigated_atgte", description="Filter incidents mitigated on or after this timestamp (ISO 8601 format). Inclusive lower bound."),
    filter_mitigated_at__lte: str | None = Field(None, alias="filtermitigated_atlte", description="Filter incidents mitigated on or before this timestamp (ISO 8601 format). Inclusive upper bound."),
    filter_resolved_at__gte: str | None = Field(None, alias="filterresolved_atgte", description="Filter incidents resolved on or after this timestamp (ISO 8601 format). Inclusive lower bound."),
    filter_resolved_at__lte: str | None = Field(None, alias="filterresolved_atlte", description="Filter incidents resolved on or before this timestamp (ISO 8601 format). Inclusive upper bound."),
    filter_closed_at__gt: str | None = Field(None, alias="filterclosed_atgt", description="Filter incidents closed after this timestamp (ISO 8601 format). Exclusive lower bound."),
    filter_closed_at__gte: str | None = Field(None, alias="filterclosed_atgte", description="Filter incidents closed on or after this timestamp (ISO 8601 format). Inclusive lower bound."),
    filter_closed_at__lt: str | None = Field(None, alias="filterclosed_atlt", description="Filter incidents closed before this timestamp (ISO 8601 format). Exclusive upper bound."),
    filter_closed_at__lte: str | None = Field(None, alias="filterclosed_atlte", description="Filter incidents closed on or before this timestamp (ISO 8601 format). Inclusive upper bound."),
    filter_in_triage_at__gt: str | None = Field(None, alias="filterin_triage_atgt", description="Filter incidents entered triage after this timestamp (ISO 8601 format). Exclusive lower bound."),
    filter_in_triage_at__gte: str | None = Field(None, alias="filterin_triage_atgte", description="Filter incidents entered triage on or after this timestamp (ISO 8601 format). Inclusive lower bound."),
    filter_in_triage_at__lt: str | None = Field(None, alias="filterin_triage_atlt", description="Filter incidents entered triage before this timestamp (ISO 8601 format). Exclusive upper bound."),
    filter_in_triage_at__lte: str | None = Field(None, alias="filterin_triage_atlte", description="Filter incidents entered triage on or before this timestamp (ISO 8601 format). Inclusive upper bound."),
    sort: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Field(None, description="Sort results by one or more fields. Prefix with hyphen (-) for descending order. Valid fields: created_at, updated_at."),
    include: Literal["sub_statuses", "causes", "subscribers", "roles", "slack_messages", "environments", "incident_types", "services", "functionalities", "groups", "events", "action_items", "custom_field_selections", "feedbacks", "incident_post_mortem"] | None = Field(None, description="Include related resources in the response. Comma-separated list of resources: sub_statuses, causes, subscribers, roles, slack_messages, environments, incident_types, services, functionalities, groups, events, action_items, custom_field_selections, feedbacks, incident_post_mortem."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of incidents with advanced filtering by status, severity, team, service, and temporal ranges. Supports sorting and inclusion of related resources like causes, subscribers, and post-mortems."""

    # Construct request model with validation
    try:
        _request = _models.ListIncidentsRequest(
            query=_models.ListIncidentsRequestQuery(page_number=page_number, page_size=page_size, filter_kind=filter_kind, filter_status=filter_status, filter_private=filter_private, filter_user_id=filter_user_id, filter_severity_id=filter_severity_id, filter_labels=filter_labels, filter_type_ids=filter_type_ids, filter_environment_ids=filter_environment_ids, filter_functionality_ids=filter_functionality_ids, filter_service_ids=filter_service_ids, filter_team_ids=filter_team_ids, filter_cause_ids=filter_cause_ids, filter_custom_field_selected_option_ids=filter_custom_field_selected_option_ids, filter_updated_at__gt=filter_updated_at__gt, filter_updated_at__gte=filter_updated_at__gte, filter_updated_at__lt=filter_updated_at__lt, filter_updated_at__lte=filter_updated_at__lte, filter_started_at__gte=filter_started_at__gte, filter_started_at__lte=filter_started_at__lte, filter_detected_at__gt=filter_detected_at__gt, filter_detected_at__gte=filter_detected_at__gte, filter_detected_at__lt=filter_detected_at__lt, filter_detected_at__lte=filter_detected_at__lte, filter_acknowledged_at__gt=filter_acknowledged_at__gt, filter_acknowledged_at__gte=filter_acknowledged_at__gte, filter_acknowledged_at__lt=filter_acknowledged_at__lt, filter_acknowledged_at__lte=filter_acknowledged_at__lte, filter_mitigated_at__gte=filter_mitigated_at__gte, filter_mitigated_at__lte=filter_mitigated_at__lte, filter_resolved_at__gte=filter_resolved_at__gte, filter_resolved_at__lte=filter_resolved_at__lte, filter_closed_at__gt=filter_closed_at__gt, filter_closed_at__gte=filter_closed_at__gte, filter_closed_at__lt=filter_closed_at__lt, filter_closed_at__lte=filter_closed_at__lte, filter_in_triage_at__gt=filter_in_triage_at__gt, filter_in_triage_at__gte=filter_in_triage_at__gte, filter_in_triage_at__lt=filter_in_triage_at__lt, filter_in_triage_at__lte=filter_in_triage_at__lte, sort=sort, include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_incidents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/incidents"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_incidents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_incidents", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_incidents",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Incidents
@mcp.tool()
async def create_incident(
    type_: Literal["incidents"] = Field(..., alias="type", description="The resource type identifier; must be set to 'incidents' to create an incident."),
    title: str | None = Field(None, description="A human-readable title for the incident. If omitted, the system will automatically generate one."),
    kind: Literal["test", "test_sub", "example", "example_sub", "normal", "normal_sub", "backfilled", "scheduled"] | None = Field(None, description="Classifies the incident type. Defaults to 'normal'. Use 'test' or 'test_sub' for testing, 'example' or 'example_sub' for examples, 'backfilled' for historical incidents, or 'scheduled' for maintenance windows."),
    parent_incident_id: str | None = Field(None, description="The ID of a parent incident if this incident is a sub-incident or related to another incident."),
    duplicate_incident_id: str | None = Field(None, description="The ID of an incident this one duplicates, used to link duplicate incidents together."),
    private: bool | None = Field(None, description="Marks the incident as private, restricting visibility. This setting is permanent and cannot be changed after creation."),
    summary: str | None = Field(None, description="A detailed summary or description of the incident."),
    user_id: str | None = Field(None, description="The user ID of the incident creator. Defaults to the user associated with the API key if not specified."),
    severity_id: str | None = Field(None, description="The ID of the severity level to assign to the incident (e.g., critical, high, medium, low)."),
    public_title: str | None = Field(None, description="A public-facing title for the incident, separate from the internal title."),
    alert_ids: list[str] | None = Field(None, description="An array of alert IDs to associate with this incident."),
    environment_ids: list[str] | None = Field(None, description="An array of environment IDs (e.g., production, staging) to associate with this incident."),
    incident_type_ids: list[str] | None = Field(None, description="An array of incident type IDs to categorize this incident."),
    service_ids: list[str] | None = Field(None, description="An array of service IDs affected by or related to this incident."),
    functionality_ids: list[str] | None = Field(None, description="An array of functionality IDs representing features or components impacted by this incident."),
    group_ids: list[str] | None = Field(None, description="An array of team IDs to assign ownership or visibility of this incident."),
    cause_ids: list[str] | None = Field(None, description="An array of cause IDs to identify root causes associated with this incident."),
    slack_channel_archived: bool | None = Field(None, description="Indicates whether the associated Slack channel for this incident has been archived."),
    google_drive_parent_id: str | None = Field(None, description="The Google Drive folder ID where incident-related documents should be stored."),
    notify_emails: list[str] | None = Field(None, description="An array of email addresses to notify about this incident creation."),
    status: Literal["in_triage", "started", "detected", "acknowledged", "mitigated", "resolved", "closed", "cancelled", "scheduled", "in_progress", "completed"] | None = Field(None, description="The current status of the incident. Use 'detected' or 'acknowledged' for active incidents, 'mitigated' or 'resolved' for recovery states, 'closed' for finalized incidents, or 'scheduled' for planned maintenance."),
    url: str | None = Field(None, description="A URL linking to external incident details, logs, or related resources."),
    scheduled_for: str | None = Field(None, description="The start date and time for a scheduled maintenance incident. Use ISO 8601 format."),
    scheduled_until: str | None = Field(None, description="The end date and time for a scheduled maintenance incident. Use ISO 8601 format."),
) -> dict[str, Any] | ToolResult:
    """Creates a new incident with optional metadata including severity, services, teams, and related resources. Automatically generates a title if not provided and defaults to non-private status."""

    # Construct request model with validation
    try:
        _request = _models.CreateIncidentRequest(
            body=_models.CreateIncidentRequestBody(data=_models.CreateIncidentRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateIncidentRequestBodyDataAttributes(title=title, kind=kind, parent_incident_id=parent_incident_id, duplicate_incident_id=duplicate_incident_id, private=private, summary=summary, user_id=user_id, severity_id=severity_id, public_title=public_title, alert_ids=alert_ids, environment_ids=environment_ids, incident_type_ids=incident_type_ids, service_ids=service_ids, functionality_ids=functionality_ids, group_ids=group_ids, cause_ids=cause_ids, slack_channel_archived=slack_channel_archived, google_drive_parent_id=google_drive_parent_id, notify_emails=notify_emails, status=status, url=url, scheduled_for=scheduled_for, scheduled_until=scheduled_until) if any(v is not None for v in [title, kind, parent_incident_id, duplicate_incident_id, private, summary, user_id, severity_id, public_title, alert_ids, environment_ids, incident_type_ids, service_ids, functionality_ids, group_ids, cause_ids, slack_channel_archived, google_drive_parent_id, notify_emails, status, url, scheduled_for, scheduled_until]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_incident: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/incidents"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_incident")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_incident", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_incident",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Incidents
@mcp.tool()
async def get_incident(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident to retrieve."),
    include: Literal["sub_statuses", "causes", "subscribers", "roles", "slack_messages", "environments", "incident_types", "services", "functionalities", "groups", "events", "action_items", "custom_field_selections", "feedbacks", "incident_post_mortem"] | None = Field(None, description="Comma-separated list of related resources to include in the response. Valid options include sub_statuses, causes, subscribers, roles, slack_messages, environments, incident_types, services, functionalities, groups, events, action_items, custom_field_selections, feedbacks, and incident_post_mortem."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific incident by its unique identifier. Optionally include related data such as sub-statuses, causes, subscribers, roles, and other associated resources."""

    # Construct request model with validation
    try:
        _request = _models.GetIncidentRequest(
            path=_models.GetIncidentRequestPath(id_=id_),
            query=_models.GetIncidentRequestQuery(include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_incident: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_incident")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_incident", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_incident",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Incidents
@mcp.tool()
async def update_incident(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident to update."),
    type_: Literal["incidents"] = Field(..., alias="type", description="The resource type, which must be 'incidents' for this operation."),
    title: str | None = Field(None, description="A human-readable title for the incident."),
    kind: Literal["test", "test_sub", "example", "example_sub", "normal", "normal_sub", "backfilled", "scheduled"] | None = Field(None, description="The classification of the incident. Options include test incidents, examples, normal incidents, backfilled historical incidents, and scheduled maintenance. Defaults to 'normal'."),
    parent_incident_id: str | None = Field(None, description="The ID of a parent incident if this incident is a sub-incident or child of another incident."),
    duplicate_incident_id: str | None = Field(None, description="The ID of another incident if this incident is a duplicate of an existing incident."),
    summary: str | None = Field(None, description="A detailed summary or description of the incident."),
    status: Literal["in_triage", "started", "detected", "acknowledged", "mitigated", "resolved", "closed", "cancelled", "scheduled", "in_progress", "completed"] | None = Field(None, description="The current status of the incident. Valid statuses include triage, detection, acknowledgment, mitigation, resolution, closure, and cancellation states, as well as scheduled maintenance states."),
    private: bool | None = Field(None, description="Mark the incident as private. Once set to private, this cannot be reverted. Defaults to false."),
    severity_id: str | None = Field(None, description="The ID of the severity level to assign to the incident."),
    public_title: str | None = Field(None, description="A public-facing title for the incident, separate from the internal title."),
    alert_ids: list[str] | None = Field(None, description="A list of alert IDs to associate with this incident."),
    environment_ids: list[str] | None = Field(None, description="A list of environment IDs where this incident occurred or is relevant."),
    incident_type_ids: list[str] | None = Field(None, description="A list of incident type IDs to categorize this incident."),
    service_ids: list[str] | None = Field(None, description="A list of service IDs affected by or related to this incident."),
    functionality_ids: list[str] | None = Field(None, description="A list of functionality IDs impacted by this incident."),
    group_ids: list[str] | None = Field(None, description="A list of team IDs to assign or associate with this incident."),
    cause_ids: list[str] | None = Field(None, description="A list of cause IDs that contributed to or explain this incident."),
    slack_channel_archived: bool | None = Field(None, description="Indicates whether the associated Slack channel for this incident has been archived."),
    google_drive_parent_id: str | None = Field(None, description="The Google Drive folder ID to use as the parent location for incident-related documents."),
    scheduled_for: str | None = Field(None, description="The start date and time for a scheduled maintenance incident. Use ISO 8601 format."),
    scheduled_until: str | None = Field(None, description="The end date and time for a scheduled maintenance incident. Use ISO 8601 format."),
) -> dict[str, Any] | ToolResult:
    """Update an existing incident with new details, status, severity, relationships, and metadata. Supports status transitions, severity assignment, linking to related incidents, and attaching resources like alerts, services, and teams."""

    # Construct request model with validation
    try:
        _request = _models.UpdateIncidentRequest(
            path=_models.UpdateIncidentRequestPath(id_=id_),
            body=_models.UpdateIncidentRequestBody(data=_models.UpdateIncidentRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateIncidentRequestBodyDataAttributes(title=title, kind=kind, parent_incident_id=parent_incident_id, duplicate_incident_id=duplicate_incident_id, summary=summary, status=status, private=private, severity_id=severity_id, public_title=public_title, alert_ids=alert_ids, environment_ids=environment_ids, incident_type_ids=incident_type_ids, service_ids=service_ids, functionality_ids=functionality_ids, group_ids=group_ids, cause_ids=cause_ids, slack_channel_archived=slack_channel_archived, google_drive_parent_id=google_drive_parent_id, scheduled_for=scheduled_for, scheduled_until=scheduled_until) if any(v is not None for v in [title, kind, parent_incident_id, duplicate_incident_id, summary, status, private, severity_id, public_title, alert_ids, environment_ids, incident_type_ids, service_ids, functionality_ids, group_ids, cause_ids, slack_channel_archived, google_drive_parent_id, scheduled_for, scheduled_until]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_incident: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_incident")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_incident", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_incident",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Incidents
@mcp.tool()
async def delete_incident(id_: str = Field(..., alias="id", description="The unique identifier of the incident to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific incident by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteIncidentRequest(
            path=_models.DeleteIncidentRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_incident: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_incident")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_incident", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_incident",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Incidents
@mcp.tool()
async def mitigate_incident(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident to mitigate."),
    type_: Literal["incidents"] = Field(..., alias="type", description="The resource type, which must be set to 'incidents' to specify that this operation applies to incident resources."),
    mitigation_message: str | None = Field(None, description="A brief explanation of how the incident was mitigated or resolved. This provides context for other team members reviewing the incident history."),
) -> dict[str, Any] | ToolResult:
    """Mark a specific incident as mitigated by providing its ID and documenting how the incident was resolved. This updates the incident's status to reflect that mitigation actions have been taken."""

    # Construct request model with validation
    try:
        _request = _models.MitigateIncidentRequest(
            path=_models.MitigateIncidentRequestPath(id_=id_),
            body=_models.MitigateIncidentRequestBody(data=_models.MitigateIncidentRequestBodyData(
                    type_=type_,
                    attributes=_models.MitigateIncidentRequestBodyDataAttributes(mitigation_message=mitigation_message) if any(v is not None for v in [mitigation_message]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for mitigate_incident: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{id}/mitigate", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{id}/mitigate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("mitigate_incident")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("mitigate_incident", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="mitigate_incident",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Incidents
@mcp.tool()
async def resolve_incident(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident to resolve."),
    type_: Literal["incidents"] = Field(..., alias="type", description="The resource type, which must be 'incidents' to specify this operation targets incident resources."),
    resolution_message: str | None = Field(None, description="Optional explanation describing the resolution steps taken or outcome of the incident resolution."),
) -> dict[str, Any] | ToolResult:
    """Mark a specific incident as resolved. Optionally provide details about how the incident was resolved."""

    # Construct request model with validation
    try:
        _request = _models.ResolveIncidentRequest(
            path=_models.ResolveIncidentRequestPath(id_=id_),
            body=_models.ResolveIncidentRequestBody(data=_models.ResolveIncidentRequestBodyData(
                    type_=type_,
                    attributes=_models.ResolveIncidentRequestBodyDataAttributes(resolution_message=resolution_message) if any(v is not None for v in [resolution_message]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for resolve_incident: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{id}/resolve", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{id}/resolve"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("resolve_incident")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("resolve_incident", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="resolve_incident",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Incidents
@mcp.tool()
async def cancel_incident(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident to cancel."),
    type_: Literal["incidents"] = Field(..., alias="type", description="The resource type, which must be 'incidents' to specify that this operation applies to incident resources."),
    cancellation_message: str | None = Field(None, description="An optional message explaining why the incident was cancelled."),
) -> dict[str, Any] | ToolResult:
    """Cancel a specific incident by its ID. Optionally provide a cancellation message to document the reason for cancellation."""

    # Construct request model with validation
    try:
        _request = _models.CancelIncidentRequest(
            path=_models.CancelIncidentRequestPath(id_=id_),
            body=_models.CancelIncidentRequestBody(data=_models.CancelIncidentRequestBodyData(
                    type_=type_,
                    attributes=_models.CancelIncidentRequestBodyDataAttributes(cancellation_message=cancellation_message) if any(v is not None for v in [cancellation_message]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for cancel_incident: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{id}/cancel", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{id}/cancel"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("cancel_incident")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("cancel_incident", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="cancel_incident",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Incidents
@mcp.tool()
async def update_incident_to_triage(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident to transition into triage state."),
    type_: Literal["incidents"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'incidents' to specify this operation applies to incident resources."),
) -> dict[str, Any] | ToolResult:
    """Move a specific incident into triage state for initial assessment and categorization. This operation marks the incident as requiring triage review."""

    # Construct request model with validation
    try:
        _request = _models.TriageIncidentRequest(
            path=_models.TriageIncidentRequestPath(id_=id_),
            body=_models.TriageIncidentRequestBody(data=_models.TriageIncidentRequestBodyData(type_=type_))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_incident_to_triage: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{id}/in_triage", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{id}/in_triage"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_incident_to_triage")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_incident_to_triage", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_incident_to_triage",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Incidents
@mcp.tool()
async def restart_incident(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident to restart."),
    type_: Literal["incidents"] = Field(..., alias="type", description="The resource type, which must be set to 'incidents' to specify the target resource category."),
) -> dict[str, Any] | ToolResult:
    """Restart a specific incident to resume its lifecycle and processing. This operation reactivates an incident by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.RestartIncidentRequest(
            path=_models.RestartIncidentRequestPath(id_=id_),
            body=_models.RestartIncidentRequestBody(data=_models.RestartIncidentRequestBodyData(type_=type_))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for restart_incident: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{id}/restart", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{id}/restart"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("restart_incident")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("restart_incident", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="restart_incident",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Incidents
@mcp.tool()
async def add_subscribers_to_incident(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident to which subscribers will be added."),
    type_: Literal["incidents"] = Field(..., alias="type", description="The resource type, which must be 'incidents' for this operation."),
    user_ids: list[str] | None = Field(None, description="Array of user IDs to add as subscribers to the incident. Users are identified by their unique identifiers."),
    remove_users_with_no_private_incident_access: bool | None = Field(None, description="When enabled, automatically removes any users from the subscriber list who lack read permissions for private incidents. Defaults to false, allowing all specified users to be added regardless of private incident access."),
) -> dict[str, Any] | ToolResult:
    """Add one or more users as subscribers to an incident, with optional enforcement of private incident access permissions. Subscribers receive notifications about incident updates."""

    # Construct request model with validation
    try:
        _request = _models.AddSubscribersToIncidentRequest(
            path=_models.AddSubscribersToIncidentRequestPath(id_=id_),
            body=_models.AddSubscribersToIncidentRequestBody(data=_models.AddSubscribersToIncidentRequestBodyData(
                    type_=type_,
                    attributes=_models.AddSubscribersToIncidentRequestBodyDataAttributes(user_ids=user_ids, remove_users_with_no_private_incident_access=remove_users_with_no_private_incident_access) if any(v is not None for v in [user_ids, remove_users_with_no_private_incident_access]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_subscribers_to_incident: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{id}/add_subscribers", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{id}/add_subscribers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_subscribers_to_incident")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_subscribers_to_incident", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_subscribers_to_incident",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Incidents
@mcp.tool()
async def remove_subscribers_from_incident(
    id_: str = Field(..., alias="id", description="The unique identifier of the incident from which subscribers will be removed."),
    type_: Literal["incidents"] = Field(..., alias="type", description="The resource type, which must be 'incidents' for this operation."),
    user_ids: list[str] | None = Field(None, description="Array of user IDs to remove from the incident's subscriber list. If not provided, only users without private incident access will be removed (if that option is enabled)."),
    remove_users_with_no_private_incident_access: bool | None = Field(None, description="When enabled, automatically removes any users who lack read permissions for private incidents from the subscriber list. Defaults to false."),
) -> dict[str, Any] | ToolResult:
    """Remove one or more subscribers from an incident. You can specify individual users to remove or automatically remove users lacking read permissions for private incidents."""

    # Construct request model with validation
    try:
        _request = _models.RemoveSubscribersToIncidentRequest(
            path=_models.RemoveSubscribersToIncidentRequestPath(id_=id_),
            body=_models.RemoveSubscribersToIncidentRequestBody(data=_models.RemoveSubscribersToIncidentRequestBodyData(
                    type_=type_,
                    attributes=_models.RemoveSubscribersToIncidentRequestBodyDataAttributes(user_ids=user_ids, remove_users_with_no_private_incident_access=remove_users_with_no_private_incident_access) if any(v is not None for v in [user_ids, remove_users_with_no_private_incident_access]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_subscribers_from_incident: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/incidents/{id}/remove_subscribers", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/incidents/{id}/remove_subscribers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_subscribers_from_incident")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_subscribers_from_incident", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_subscribers_from_incident",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: LiveCallRouters
@mcp.tool()
async def list_live_call_routers(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., nested objects or associations)."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve for pagination, starting from 1."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of results to return per page."),
    sort: str | None = Field(None, description="Comma-separated list of fields to sort by, with optional direction prefix (e.g., 'name,-created_at' for ascending name and descending creation date)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of live call routers with optional filtering and sorting capabilities."""

    # Construct request model with validation
    try:
        _request = _models.ListLiveCallRoutersRequest(
            query=_models.ListLiveCallRoutersRequestQuery(include=include, page_number=page_number, page_size=page_size, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_live_call_routers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/live_call_routers"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_live_call_routers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_live_call_routers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_live_call_routers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: LiveCallRouters
@mcp.tool()
async def create_live_call_router(
    data_type: Literal["live_call_routers"] = Field(..., alias="dataType", description="The resource type identifier; must be set to 'live_call_routers'."),
    escalation_policy_trigger_params_type: Literal["service", "group", "escalation_policy"] = Field(..., alias="escalation_policy_trigger_paramsType", description="The target type for escalation notifications: 'service' (PagerDuty service), 'group' (team/group), or 'escalation_policy' (escalation policy)."),
    kind: Literal["voicemail", "live"] = Field(..., description="The operational mode of the router: 'live' for direct call handling or 'voicemail' for voicemail-only setup."),
    name: str = Field(..., description="A descriptive name for the live call router."),
    country_code: Literal["AU", "CA", "NL", "NZ", "GB", "US"] = Field(..., description="The country where the phone number is registered: AU (Australia), CA (Canada), NL (Netherlands), NZ (New Zealand), GB (United Kingdom), or US (United States)."),
    phone_type: Literal["local", "toll_free", "mobile"] = Field(..., description="The phone number category: 'local' (geographic area code), 'toll_free' (no charge to caller), or 'mobile' (cellular number)."),
    phone_number: str = Field(..., description="The phone number to register for this router. Generate a number using the generate_phone_number API before providing it here."),
    id_: str = Field(..., alias="id", description="The unique identifier of the notification target (service, group, or escalation policy) for call routing."),
    enabled: bool | None = Field(None, description="Whether the live call router is active and operational."),
    voicemail_greeting: str | None = Field(None, description="Optional greeting message played when callers reach the voicemail system."),
    caller_greeting: str | None = Field(None, description="Optional greeting message played when callers first connect to the live call router."),
    waiting_music_url: Literal["https://storage.rootly.com/twilio/voicemail/ClockworkWaltz.mp3", "https://storage.rootly.com/twilio/voicemail/ith_brahms-116-4.mp3", "https://storage.rootly.com/twilio/voicemail/Mellotroniac_-_Flight_Of_Young_Hearts_Flute.mp3", "https://storage.rootly.com/twilio/voicemail/BusyStrings.mp3", "https://storage.rootly.com/twilio/voicemail/oldDog_-_endless_goodbye_%28instr.%29.mp3", "https://storage.rootly.com/twilio/voicemail/MARKOVICHAMP-Borghestral.mp3", "https://storage.rootly.com/twilio/voicemail/ith_chopin-15-2.mp3"] | None = Field(None, description="Optional background music URL played while callers wait. Choose from predefined Rootly-hosted audio tracks."),
    sent_to_voicemail_delay: int | None = Field(None, description="Optional delay in seconds before an unanswered call is automatically redirected to voicemail."),
    should_redirect_to_voicemail_on_no_answer: bool | None = Field(None, description="When enabled, prompts the caller to choose between leaving a voicemail or waiting to connect with a live person."),
    escalation_level_delay_in_seconds: int | None = Field(None, description="Optional override for the delay (in seconds) between escalation levels when routing through an escalation policy."),
    should_auto_resolve_alert_on_call_end: bool | None = Field(None, description="When enabled, automatically resolves the associated alert when the call ends."),
    alert_urgency_id: str | None = Field(None, description="Optional alert urgency level used in escalation paths to determine priority and who to page."),
    calling_tree_prompt: str | None = Field(None, description="Optional audio instructions or prompts that callers hear, guiding them to select routing options when this router is configured as a phone tree."),
    paging_targets: list[_models.CreateLiveCallRouterBodyDataAttributesPagingTargetsItem] | None = Field(None, description="Optional list of paging targets (services, groups, or escalation policies) that callers can select from when this router functions as a phone tree."),
) -> dict[str, Any] | ToolResult:
    """Creates a new Live Call Router to handle incoming calls with configurable routing, voicemail, and escalation options. The router can be set up as a live call handler or voicemail system with optional phone tree capabilities."""

    # Construct request model with validation
    try:
        _request = _models.CreateLiveCallRouterRequest(
            body=_models.CreateLiveCallRouterRequestBody(data=_models.CreateLiveCallRouterRequestBodyData(
                    type_=data_type,
                    attributes=_models.CreateLiveCallRouterRequestBodyDataAttributes(
                        kind=kind, enabled=enabled, name=name, country_code=country_code, phone_type=phone_type, phone_number=phone_number, voicemail_greeting=voicemail_greeting, caller_greeting=caller_greeting, waiting_music_url=waiting_music_url, sent_to_voicemail_delay=sent_to_voicemail_delay, should_redirect_to_voicemail_on_no_answer=should_redirect_to_voicemail_on_no_answer, escalation_level_delay_in_seconds=escalation_level_delay_in_seconds, should_auto_resolve_alert_on_call_end=should_auto_resolve_alert_on_call_end, alert_urgency_id=alert_urgency_id, calling_tree_prompt=calling_tree_prompt, paging_targets=paging_targets,
                        escalation_policy_trigger_params=_models.CreateLiveCallRouterRequestBodyDataAttributesEscalationPolicyTriggerParams(type_=escalation_policy_trigger_params_type, id_=id_)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_live_call_router: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/live_call_routers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_live_call_router")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_live_call_router", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_live_call_router",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: LiveCallRouters
@mcp.tool()
async def generate_phone_number_for_live_call_router(
    country_code: Literal["AU", "CA", "NL", "NZ", "GB", "US"] = Field(..., description="The country where the phone number will be allocated. Supported countries are Australia, Canada, Netherlands, New Zealand, United Kingdom, and United States."),
    phone_type: Literal["local", "toll_free", "mobile"] = Field(..., description="The type of phone number to generate: local (geographic area code), toll_free (caller pays no charges), or mobile (cellular number)."),
) -> dict[str, Any] | ToolResult:
    """Generates a dedicated phone number for routing incoming calls through Live Call Router. The phone number is allocated based on the specified country and type."""

    # Construct request model with validation
    try:
        _request = _models.GeneratePhoneNumberLiveCallRouterRequest(
            query=_models.GeneratePhoneNumberLiveCallRouterRequestQuery(country_code=country_code, phone_type=phone_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_phone_number_for_live_call_router: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/live_call_routers/generate_phone_number"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_phone_number_for_live_call_router")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_phone_number_for_live_call_router", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_phone_number_for_live_call_router",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: LiveCallRouters
@mcp.tool()
async def get_live_call_router(id_: str = Field(..., alias="id", description="The unique identifier of the Live Call Router to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific Live Call Router configuration by its unique identifier. Use this to fetch details about a configured call routing rule."""

    # Construct request model with validation
    try:
        _request = _models.GetLiveCallRouterRequest(
            path=_models.GetLiveCallRouterRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_live_call_router: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/live_call_routers/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/live_call_routers/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_live_call_router")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_live_call_router", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_live_call_router",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: LiveCallRouters
@mcp.tool()
async def update_live_call_router(
    id_: str = Field(..., alias="id", description="The unique identifier of the Live Call Router to update."),
    escalation_policy_trigger_params_id: str = Field(..., alias="escalation_policy_trigger_paramsId", description="The unique identifier of the notification target (Service, Group, or Escalation Policy) that will receive escalation alerts."),
    data_type: Literal["live_call_routers"] = Field(..., alias="dataType", description="The resource type identifier; must be 'live_call_routers'."),
    escalation_policy_trigger_params_type: Literal["Service", "Group", "EscalationPolicy"] = Field(..., alias="escalation_policy_trigger_paramsType", description="The category of the notification target: 'Service' for a specific service, 'Group' for a team or group, or 'EscalationPolicy' for an escalation policy."),
    kind: Literal["voicemail", "live"] | None = Field(None, description="The operational mode of the router: 'voicemail' for voicemail-only handling or 'live' for live call routing."),
    enabled: bool | None = Field(None, description="Whether the Live Call Router is active and accepting calls."),
    country_code: Literal["AU", "CA", "NL", "NZ", "GB", "US"] | None = Field(None, description="The country where the phone number is registered: AU (Australia), CA (Canada), NL (Netherlands), NZ (New Zealand), GB (United Kingdom), or US (United States)."),
    phone_type: Literal["local", "toll_free", "mobile"] | None = Field(None, description="The phone number type: 'local' for regional numbers, 'toll_free' for toll-free numbers, or 'mobile' for mobile numbers."),
    voicemail_greeting: str | None = Field(None, description="The audio message played when callers reach the voicemail system."),
    caller_greeting: str | None = Field(None, description="The greeting message played to callers when they first connect to the router."),
    waiting_music_url: Literal["https://storage.rootly.com/twilio/voicemail/ClockworkWaltz.mp3", "https://storage.rootly.com/twilio/voicemail/ith_brahms-116-4.mp3", "https://storage.rootly.com/twilio/voicemail/Mellotroniac_-_Flight_Of_Young_Hearts_Flute.mp3", "https://storage.rootly.com/twilio/voicemail/BusyStrings.mp3", "https://storage.rootly.com/twilio/voicemail/oldDog_-_endless_goodbye_%28instr.%29.mp3", "https://storage.rootly.com/twilio/voicemail/MARKOVICHAMP-Borghestral.mp3", "https://storage.rootly.com/twilio/voicemail/ith_chopin-15-2.mp3"] | None = Field(None, description="The URL of the background music played while callers wait in queue; must be one of the predefined Rootly-hosted audio tracks."),
    sent_to_voicemail_delay: int | None = Field(None, description="The number of seconds to wait before automatically redirecting a caller to voicemail if no one answers."),
    should_redirect_to_voicemail_on_no_answer: bool | None = Field(None, description="When enabled, prompts the caller to choose between leaving a voicemail or waiting to connect with a live representative."),
    escalation_level_delay_in_seconds: int | None = Field(None, description="The delay in seconds between escalation levels, overriding the default escalation policy timing."),
    should_auto_resolve_alert_on_call_end: bool | None = Field(None, description="When enabled, automatically resolves the associated alert when the call ends."),
    alert_urgency_id: str | None = Field(None, description="The identifier of the alert urgency level used to determine escalation routing and who receives page notifications."),
    calling_tree_prompt: str | None = Field(None, description="The audio instructions or prompt that callers hear when calling this number, guiding them to select routing options in a phone tree configuration."),
    paging_targets: list[_models.UpdateLiveCallRouterBodyDataAttributesPagingTargetsItem] | None = Field(None, description="An ordered list of targets (Services, Groups, or Escalation Policies) that callers can select from when this router is configured as a phone tree; order determines the sequence presented to callers."),
) -> dict[str, Any] | ToolResult:
    """Update the configuration of a Live Call Router, including routing behavior, greetings, escalation policies, and call handling preferences."""

    # Construct request model with validation
    try:
        _request = _models.UpdateLiveCallRouterRequest(
            path=_models.UpdateLiveCallRouterRequestPath(id_=id_),
            body=_models.UpdateLiveCallRouterRequestBody(data=_models.UpdateLiveCallRouterRequestBodyData(
                    type_=data_type,
                    attributes=_models.UpdateLiveCallRouterRequestBodyDataAttributes(
                        kind=kind, enabled=enabled, country_code=country_code, phone_type=phone_type, voicemail_greeting=voicemail_greeting, caller_greeting=caller_greeting, waiting_music_url=waiting_music_url, sent_to_voicemail_delay=sent_to_voicemail_delay, should_redirect_to_voicemail_on_no_answer=should_redirect_to_voicemail_on_no_answer, escalation_level_delay_in_seconds=escalation_level_delay_in_seconds, should_auto_resolve_alert_on_call_end=should_auto_resolve_alert_on_call_end, alert_urgency_id=alert_urgency_id, calling_tree_prompt=calling_tree_prompt, paging_targets=paging_targets,
                        escalation_policy_trigger_params=_models.UpdateLiveCallRouterRequestBodyDataAttributesEscalationPolicyTriggerParams(id_=escalation_policy_trigger_params_id, type_=escalation_policy_trigger_params_type)
                    )
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_live_call_router: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/live_call_routers/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/live_call_routers/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_live_call_router")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_live_call_router", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_live_call_router",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: LiveCallRouters
@mcp.tool()
async def delete_live_call_router(id_: str = Field(..., alias="id", description="The unique identifier of the Live Call Router to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a Live Call Router by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteLiveCallRouterRequest(
            path=_models.DeleteLiveCallRouterRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_live_call_router: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/live_call_routers/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/live_call_routers/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_live_call_router")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_live_call_router", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_live_call_router",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: OnCallRoles
@mcp.tool()
async def list_on_call_roles(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., users, schedules). Reduces the need for additional API calls by embedding associated data."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve when paginating through results. Use with page[size] to navigate large datasets."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of on-call roles to return per page. Controls the size of each paginated response."),
    sort: str | None = Field(None, description="Sort the results by one or more fields in ascending or descending order. Specify field names with optional +/- prefix to control sort direction (e.g., name, -created_at)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of on-call roles configured in the system. Use pagination parameters to control result size and navigation through the dataset."""

    # Construct request model with validation
    try:
        _request = _models.ListOnCallRolesRequest(
            query=_models.ListOnCallRolesRequestQuery(include=include, page_number=page_number, page_size=page_size, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_on_call_roles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/on_call_roles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_on_call_roles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_on_call_roles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_on_call_roles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: OnCallRoles
@mcp.tool()
async def create_on_call_role(
    type_: Literal["on_call_roles"] = Field(..., alias="type", description="The resource type identifier; must be set to 'on_call_roles' to specify this is an On-Call Role resource."),
    name: str = Field(..., description="The human-readable name for the On-Call Role; used for display and identification throughout the system."),
    system_role: str = Field(..., description="The role classification that determines editability and behavior; user and custom type roles are editable, while system-defined roles have restricted modification."),
    slug: str | None = Field(None, description="A URL-friendly identifier for the role; if not provided, it will be auto-generated from the role name."),
    alert_sources_permissions: list[Literal["create", "update", "delete"]] | None = Field(None, description="Array of permission objects controlling access to alert sources; each entry specifies allowed actions on alert source resources."),
    alert_urgency_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission objects controlling access to alert urgency levels; each entry specifies allowed actions on urgency classifications."),
    alerts_permissions: list[Literal["create", "update", "read"]] | None = Field(None, description="Array of permission objects controlling access to alerts; each entry specifies allowed actions such as view, acknowledge, or resolve."),
    api_keys_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission objects controlling access to API keys; each entry specifies allowed actions for creating, viewing, or revoking keys."),
    audits_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission objects controlling access to audit logs; each entry specifies allowed actions for viewing system activity records."),
    contacts_permissions: list[Literal["read"]] | None = Field(None, description="Array of permission objects controlling access to contacts; each entry specifies allowed actions for managing contact information."),
    escalation_policies_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission objects controlling access to escalation policies; each entry specifies allowed actions for creating and modifying escalation rules."),
    groups_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission objects controlling access to groups; each entry specifies allowed actions for managing group membership and settings."),
    heartbeats_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission objects controlling access to heartbeats; each entry specifies allowed actions for monitoring and managing heartbeat checks."),
    integrations_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission objects controlling access to integrations; each entry specifies allowed actions for connecting external tools and services."),
    invitations_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission objects controlling access to invitations; each entry specifies allowed actions for sending and managing user invitations."),
    live_call_routing_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission objects controlling access to live call routing; each entry specifies allowed actions for configuring call routing rules."),
    schedule_override_permissions: list[Literal["create", "update"]] | None = Field(None, description="Array of permission objects controlling access to schedule overrides; each entry specifies allowed actions for creating temporary schedule modifications."),
    schedules_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission objects controlling access to schedules; each entry specifies allowed actions for creating, viewing, and modifying on-call schedules."),
    services_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission objects controlling access to services; each entry specifies allowed actions for managing service configurations."),
    webhooks_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission objects controlling access to webhooks; each entry specifies allowed actions for creating and managing webhook integrations."),
    workflows_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission objects controlling access to workflows; each entry specifies allowed actions for creating and managing automation workflows."),
) -> dict[str, Any] | ToolResult:
    """Creates a new On-Call Role with specified permissions across various operational domains. Define the role name, system type, and granular access controls for alerts, schedules, integrations, and other resources."""

    # Construct request model with validation
    try:
        _request = _models.CreateOnCallRoleRequest(
            body=_models.CreateOnCallRoleRequestBody(data=_models.CreateOnCallRoleRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateOnCallRoleRequestBodyDataAttributes(name=name, slug=slug, system_role=system_role, alert_sources_permissions=alert_sources_permissions, alert_urgency_permissions=alert_urgency_permissions, alerts_permissions=alerts_permissions, api_keys_permissions=api_keys_permissions, audits_permissions=audits_permissions, contacts_permissions=contacts_permissions, escalation_policies_permissions=escalation_policies_permissions, groups_permissions=groups_permissions, heartbeats_permissions=heartbeats_permissions, integrations_permissions=integrations_permissions, invitations_permissions=invitations_permissions, live_call_routing_permissions=live_call_routing_permissions, schedule_override_permissions=schedule_override_permissions, schedules_permissions=schedules_permissions, services_permissions=services_permissions, webhooks_permissions=webhooks_permissions, workflows_permissions=workflows_permissions)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_on_call_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/on_call_roles"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_on_call_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_on_call_role", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_on_call_role",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: OnCallRoles
@mcp.tool()
async def get_on_call_role(id_: str = Field(..., alias="id", description="The unique identifier of the On-Call Role to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific On-Call Role by its unique identifier. Use this to fetch detailed information about a particular on-call role configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetOnCallRoleRequest(
            path=_models.GetOnCallRoleRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_on_call_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/on_call_roles/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/on_call_roles/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_on_call_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_on_call_role", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_on_call_role",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: OnCallRoles
@mcp.tool()
async def update_on_call_role(
    id_: str = Field(..., alias="id", description="The unique identifier of the On-Call Role to update."),
    type_: Literal["on_call_roles"] = Field(..., alias="type", description="The resource type identifier; must be set to 'on_call_roles'."),
    slug: str | None = Field(None, description="A URL-friendly identifier for the role used in API paths and references."),
    system_role: str | None = Field(None, description="The classification of the role (e.g., user, custom); only user and custom type roles can be modified."),
    alert_sources_permissions: list[Literal["create", "update", "delete"]] | None = Field(None, description="Array of permission strings defining access levels for alert sources."),
    alert_urgency_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission strings defining access levels for alert urgency levels."),
    alerts_permissions: list[Literal["create", "update", "read"]] | None = Field(None, description="Array of permission strings defining access levels for alerts."),
    api_keys_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission strings defining access levels for API keys."),
    audits_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission strings defining access levels for audit logs."),
    contacts_permissions: list[Literal["read"]] | None = Field(None, description="Array of permission strings defining access levels for contacts."),
    escalation_policies_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission strings defining access levels for escalation policies."),
    groups_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission strings defining access levels for groups."),
    heartbeats_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission strings defining access levels for heartbeats."),
    integrations_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission strings defining access levels for integrations."),
    invitations_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission strings defining access levels for invitations."),
    live_call_routing_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission strings defining access levels for live call routing."),
    schedule_override_permissions: list[Literal["create", "update"]] | None = Field(None, description="Array of permission strings defining access levels for schedule overrides."),
    schedules_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission strings defining access levels for schedules."),
    services_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission strings defining access levels for services."),
    webhooks_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission strings defining access levels for webhooks."),
    workflows_permissions: list[Literal["create", "read", "update", "delete"]] | None = Field(None, description="Array of permission strings defining access levels for workflows."),
) -> dict[str, Any] | ToolResult:
    """Update an existing On-Call Role with new configuration, including slug, system role type, and granular permissions across alert sources, contacts, schedules, and other resources."""

    # Construct request model with validation
    try:
        _request = _models.UpdateOnCallRoleRequest(
            path=_models.UpdateOnCallRoleRequestPath(id_=id_),
            body=_models.UpdateOnCallRoleRequestBody(data=_models.UpdateOnCallRoleRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateOnCallRoleRequestBodyDataAttributes(slug=slug, system_role=system_role, alert_sources_permissions=alert_sources_permissions, alert_urgency_permissions=alert_urgency_permissions, alerts_permissions=alerts_permissions, api_keys_permissions=api_keys_permissions, audits_permissions=audits_permissions, contacts_permissions=contacts_permissions, escalation_policies_permissions=escalation_policies_permissions, groups_permissions=groups_permissions, heartbeats_permissions=heartbeats_permissions, integrations_permissions=integrations_permissions, invitations_permissions=invitations_permissions, live_call_routing_permissions=live_call_routing_permissions, schedule_override_permissions=schedule_override_permissions, schedules_permissions=schedules_permissions, services_permissions=services_permissions, webhooks_permissions=webhooks_permissions, workflows_permissions=workflows_permissions) if any(v is not None for v in [slug, system_role, alert_sources_permissions, alert_urgency_permissions, alerts_permissions, api_keys_permissions, audits_permissions, contacts_permissions, escalation_policies_permissions, groups_permissions, heartbeats_permissions, integrations_permissions, invitations_permissions, live_call_routing_permissions, schedule_override_permissions, schedules_permissions, services_permissions, webhooks_permissions, workflows_permissions]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_on_call_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/on_call_roles/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/on_call_roles/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_on_call_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_on_call_role", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_on_call_role",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: OnCallRoles
@mcp.tool()
async def delete_on_call_role(id_: str = Field(..., alias="id", description="The unique identifier of the On-Call Role to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific On-Call Role by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOnCallRoleRequest(
            path=_models.DeleteOnCallRoleRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_on_call_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/on_call_roles/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/on_call_roles/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_on_call_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_on_call_role", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_on_call_role",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: OnCallShadows
@mcp.tool()
async def list_on_call_shadows(
    schedule_id: str = Field(..., description="The unique identifier of the schedule for which to retrieve shadow shifts."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., user details, shift metadata). Specify which associations to expand for richer context."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through large result sets."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of shadow shifts to return per page. Adjust this value to control result set size for pagination."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all shadow shifts assigned to a specific on-call schedule. Shadow shifts represent secondary coverage or training assignments that run parallel to primary on-call shifts."""

    # Construct request model with validation
    try:
        _request = _models.ListOnCallShadowsRequest(
            path=_models.ListOnCallShadowsRequestPath(schedule_id=schedule_id),
            query=_models.ListOnCallShadowsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_on_call_shadows: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedules/{schedule_id}/on_call_shadows", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedules/{schedule_id}/on_call_shadows"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_on_call_shadows")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_on_call_shadows", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_on_call_shadows",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: OnCallShadows
@mcp.tool()
async def create_on_call_shadow(
    schedule_id: str = Field(..., description="The unique identifier of the schedule to which this shadow configuration belongs."),
    type_: Literal["on_call_shadows"] = Field(..., alias="type", description="The resource type for this operation; must be set to 'on_call_shadows'."),
    shadowable_type: Literal["User", "Schedule"] = Field(..., description="The type of entity being shadowed: either 'User' to shadow a specific person or 'Schedule' to shadow an entire schedule."),
    shadowable_id: str = Field(..., description="The unique identifier of the user or schedule being shadowed, corresponding to the shadowable_type selected."),
    shadow_user_id: int = Field(..., description="The unique identifier of the user who will be shadowing and to whom the shadow shift belongs."),
    starts_at: str = Field(..., description="The start date and time for the shadow shift in ISO 8601 format."),
    ends_at: str = Field(..., description="The end date and time for the shadow shift in ISO 8601 format; must be after the start time."),
) -> dict[str, Any] | ToolResult:
    """Creates a new on-call shadow configuration that allows a designated user to shadow either another user or an entire schedule during a specified time period."""

    # Construct request model with validation
    try:
        _request = _models.CreateOnCallShadowRequest(
            path=_models.CreateOnCallShadowRequestPath(schedule_id=schedule_id),
            body=_models.CreateOnCallShadowRequestBody(data=_models.CreateOnCallShadowRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateOnCallShadowRequestBodyDataAttributes(shadowable_type=shadowable_type, shadowable_id=shadowable_id, shadow_user_id=shadow_user_id, starts_at=starts_at, ends_at=ends_at)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_on_call_shadow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedules/{schedule_id}/on_call_shadows", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedules/{schedule_id}/on_call_shadows"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_on_call_shadow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_on_call_shadow", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_on_call_shadow",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: OnCallShadows
@mcp.tool()
async def get_on_call_shadow(id_: str = Field(..., alias="id", description="The unique identifier of the On Call Shadow configuration to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific On Call Shadow configuration by its unique identifier. Use this to fetch details about an on-call shadow setup, including its rules and associated personnel."""

    # Construct request model with validation
    try:
        _request = _models.GetOnCallShadowRequest(
            path=_models.GetOnCallShadowRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_on_call_shadow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/on_call_shadows/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/on_call_shadows/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_on_call_shadow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_on_call_shadow", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_on_call_shadow",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: OnCallShadows
@mcp.tool()
async def update_on_call_shadow(
    id_: str = Field(..., alias="id", description="The unique identifier of the on-call shadow configuration to update."),
    type_: Literal["on_call_shadows"] = Field(..., alias="type", description="The resource type identifier, which must be 'on_call_shadows' to specify this is an on-call shadow resource."),
    schedule_id: str | None = Field(None, description="The ID of the schedule that this shadow shift is associated with."),
    shadowable_type: Literal["User", "Schedule"] | None = Field(None, description="The type of resource being shadowed: either a 'User' (individual team member) or a 'Schedule' (shift schedule)."),
    shadowable_id: str | None = Field(None, description="The ID of the user or schedule that is being shadowed, depending on the shadowable_type specified."),
    shadow_user_id: int | None = Field(None, description="The ID of the user who is performing the shadow shift and observing the on-call duties."),
    starts_at: str | None = Field(None, description="The start date and time of the shadow shift in ISO 8601 format (e.g., 2024-01-15T09:00:00Z)."),
    ends_at: str | None = Field(None, description="The end date and time of the shadow shift in ISO 8601 format (e.g., 2024-01-15T17:00:00Z)."),
) -> dict[str, Any] | ToolResult:
    """Update an existing on-call shadow configuration to modify shadowing assignments, time windows, or the user being shadowed. This allows adjustments to shadow shift details such as the shadowed user or schedule, shadow participant, and shift timing."""

    # Construct request model with validation
    try:
        _request = _models.UpdateOnCallShadowRequest(
            path=_models.UpdateOnCallShadowRequestPath(id_=id_),
            body=_models.UpdateOnCallShadowRequestBody(data=_models.UpdateOnCallShadowRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateOnCallShadowRequestBodyDataAttributes(schedule_id=schedule_id, shadowable_type=shadowable_type, shadowable_id=shadowable_id, shadow_user_id=shadow_user_id, starts_at=starts_at, ends_at=ends_at) if any(v is not None for v in [schedule_id, shadowable_type, shadowable_id, shadow_user_id, starts_at, ends_at]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_on_call_shadow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/on_call_shadows/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/on_call_shadows/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_on_call_shadow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_on_call_shadow", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_on_call_shadow",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: OverrideShifts
@mcp.tool()
async def delete_on_call_shadow(id_: str = Field(..., alias="id", description="The unique identifier of the on-call shadow configuration to delete.")) -> dict[str, Any] | ToolResult:
    """Remove a specific on-call shadow configuration by its unique identifier. This operation permanently deletes the shadow configuration and its associated settings."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOnCallShadowRequest(
            path=_models.DeleteOnCallShadowRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_on_call_shadow: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/on_call_shadows/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/on_call_shadows/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_on_call_shadow")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_on_call_shadow", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_on_call_shadow",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: OverrideShifts
@mcp.tool()
async def list_override_shifts(
    schedule_id: str = Field(..., description="The unique identifier of the schedule containing the override shifts to retrieve."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., user details, shift metadata). Specify which associations should be populated."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use this to navigate through multiple pages of results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of override shifts to return per page. Controls the batch size of results returned in each request."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of override shifts for a specific schedule. Override shifts represent temporary changes or substitutions to the standard schedule."""

    # Construct request model with validation
    try:
        _request = _models.ListOverrideShiftsRequest(
            path=_models.ListOverrideShiftsRequestPath(schedule_id=schedule_id),
            query=_models.ListOverrideShiftsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_override_shifts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedules/{schedule_id}/override_shifts", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedules/{schedule_id}/override_shifts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_override_shifts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_override_shifts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_override_shifts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: OverrideShifts
@mcp.tool()
async def create_override_shift(
    schedule_id: str = Field(..., description="The unique identifier of the schedule in which the override shift will be created."),
    type_: Literal["shifts"] = Field(..., alias="type", description="The resource type for this operation, which must be 'shifts' to indicate an override shift resource."),
    starts_at: str = Field(..., description="The start date and time of the override shift in ISO 8601 format (e.g., 2024-01-15T09:00:00Z)."),
    ends_at: str = Field(..., description="The end date and time of the override shift in ISO 8601 format (e.g., 2024-01-15T17:00:00Z). Must be after the start time."),
    user_id: int = Field(..., description="The numeric identifier of the user who will be assigned to this override shift."),
) -> dict[str, Any] | ToolResult:
    """Creates a new override shift for a user within a specified schedule, allowing temporary assignment changes during a defined time period."""

    # Construct request model with validation
    try:
        _request = _models.CreateOverrideShiftRequest(
            path=_models.CreateOverrideShiftRequestPath(schedule_id=schedule_id),
            body=_models.CreateOverrideShiftRequestBody(data=_models.CreateOverrideShiftRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateOverrideShiftRequestBodyDataAttributes(starts_at=starts_at, ends_at=ends_at, user_id=user_id)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_override_shift: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedules/{schedule_id}/override_shifts", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedules/{schedule_id}/override_shifts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_override_shift")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_override_shift", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_override_shift",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: OverrideShifts
@mcp.tool()
async def get_override_shift(id_: str = Field(..., alias="id", description="The unique identifier of the override shift to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific override shift by its unique identifier. Use this to fetch details about a single override shift record."""

    # Construct request model with validation
    try:
        _request = _models.GetOverrideShiftRequest(
            path=_models.GetOverrideShiftRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_override_shift: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/override_shifts/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/override_shifts/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_override_shift")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_override_shift", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_override_shift",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: OverrideShifts
@mcp.tool()
async def update_override_shift(
    id_: str = Field(..., alias="id", description="The unique identifier of the override shift to update."),
    type_: Literal["shifts"] = Field(..., alias="type", description="The resource type, which must be 'shifts' to indicate this operation applies to shift override resources."),
    user_id: int = Field(..., description="The user ID associated with this override shift, identifying which user the shift override applies to."),
) -> dict[str, Any] | ToolResult:
    """Update an existing override shift by its unique identifier. Allows modification of shift override details for a specific user."""

    # Construct request model with validation
    try:
        _request = _models.UpdateOverrideShiftRequest(
            path=_models.UpdateOverrideShiftRequestPath(id_=id_),
            body=_models.UpdateOverrideShiftRequestBody(data=_models.UpdateOverrideShiftRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateOverrideShiftRequestBodyDataAttributes(user_id=user_id)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_override_shift: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/override_shifts/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/override_shifts/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_override_shift")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_override_shift", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_override_shift",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: OverrideShifts
@mcp.tool()
async def delete_override_shift(id_: str = Field(..., alias="id", description="The unique identifier of the override shift to delete. This must be a valid override shift ID that exists in the system.")) -> dict[str, Any] | ToolResult:
    """Remove a specific override shift from the system by its unique identifier. This operation permanently deletes the override shift record."""

    # Construct request model with validation
    try:
        _request = _models.DeleteOverrideShiftRequest(
            path=_models.DeleteOverrideShiftRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_override_shift: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/override_shifts/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/override_shifts/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_override_shift")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_override_shift", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_override_shift",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: PlaybookTasks
@mcp.tool()
async def list_playbook_tasks(
    playbook_id: str = Field(..., description="The unique identifier of the playbook for which to retrieve tasks."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., task details, execution history). Specify which associations to expand for richer context."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve when paginating through results. Use with page[size] to navigate large task lists."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of tasks to return per page. Controls the batch size of results returned in each request."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of tasks associated with a specific playbook. Use pagination parameters to control result size and navigate through task collections."""

    # Construct request model with validation
    try:
        _request = _models.ListPlaybookTasksRequest(
            path=_models.ListPlaybookTasksRequestPath(playbook_id=playbook_id),
            query=_models.ListPlaybookTasksRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_playbook_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/playbooks/{playbook_id}/playbook_tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/playbooks/{playbook_id}/playbook_tasks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_playbook_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_playbook_tasks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_playbook_tasks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: PlaybookTasks
@mcp.tool()
async def create_playbook_task(
    playbook_id: str = Field(..., description="The unique identifier of the playbook to which this task will be added."),
    type_: Literal["playbook_tasks"] = Field(..., alias="type", description="The resource type identifier for this operation, which must be set to 'playbook_tasks'."),
    task: str = Field(..., description="The name or title of the task to be created."),
    description: str | None = Field(None, description="An optional detailed description providing context or instructions for the task."),
    position: int | None = Field(None, description="An optional numeric position to control the task's order within the playbook's task sequence. If not specified, the task will be appended to the end."),
) -> dict[str, Any] | ToolResult:
    """Creates a new task within a playbook. The task will be added to the specified playbook and can be positioned within the task sequence."""

    # Construct request model with validation
    try:
        _request = _models.CreatePlaybookTaskRequest(
            path=_models.CreatePlaybookTaskRequestPath(playbook_id=playbook_id),
            body=_models.CreatePlaybookTaskRequestBody(data=_models.CreatePlaybookTaskRequestBodyData(
                    type_=type_,
                    attributes=_models.CreatePlaybookTaskRequestBodyDataAttributes(task=task, description=description, position=position)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_playbook_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/playbooks/{playbook_id}/playbook_tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/playbooks/{playbook_id}/playbook_tasks"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_playbook_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_playbook_task", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_playbook_task",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: PlaybookTasks
@mcp.tool()
async def get_playbook_task(id_: str = Field(..., alias="id", description="The unique identifier of the playbook task to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific playbook task by its unique identifier. Use this to fetch detailed information about a single task within a playbook."""

    # Construct request model with validation
    try:
        _request = _models.GetPlaybookTaskRequest(
            path=_models.GetPlaybookTaskRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_playbook_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/playbook_tasks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/playbook_tasks/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_playbook_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_playbook_task", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_playbook_task",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: PlaybookTasks
@mcp.tool()
async def update_playbook_task(
    id_: str = Field(..., alias="id", description="The unique identifier of the playbook task to update."),
    type_: Literal["playbook_tasks"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'playbook_tasks' to specify the resource being updated."),
    task: str | None = Field(None, description="The name or title of the task to be executed within the playbook."),
    description: str | None = Field(None, description="A detailed explanation of what the task does and any relevant context for execution."),
    position: int | None = Field(None, description="The execution order of this task within the playbook, where lower numbers execute first."),
) -> dict[str, Any] | ToolResult:
    """Update a specific playbook task within a playbook by its ID. Modify task details such as the task name, description, or execution position."""

    # Construct request model with validation
    try:
        _request = _models.UpdatePlaybookTaskRequest(
            path=_models.UpdatePlaybookTaskRequestPath(id_=id_),
            body=_models.UpdatePlaybookTaskRequestBody(data=_models.UpdatePlaybookTaskRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdatePlaybookTaskRequestBodyDataAttributes(task=task, description=description, position=position) if any(v is not None for v in [task, description, position]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_playbook_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/playbook_tasks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/playbook_tasks/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_playbook_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_playbook_task", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_playbook_task",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: PlaybookTasks
@mcp.tool()
async def delete_playbook_task(id_: str = Field(..., alias="id", description="The unique identifier of the playbook task to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific playbook task by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeletePlaybookTaskRequest(
            path=_models.DeletePlaybookTaskRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_playbook_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/playbook_tasks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/playbook_tasks/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_playbook_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_playbook_task", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_playbook_task",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Playbooks
@mcp.tool()
async def list_playbooks(
    include: Literal["severities", "environments", "services", "functionalities", "groups", "causes", "incident_types"] | None = Field(None, description="Comma-separated list of related entities to include in the response. Valid options are: severities, environments, services, functionalities, groups, causes, or incident_types."),
    page_number: int | None = Field(None, alias="pagenumber", description="Page number for pagination (1-indexed). Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of playbooks to return per page. Use with page[number] to control result set size."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of playbooks with optional related metadata. Use include parameter to enrich results with associated severities, environments, services, functionalities, groups, causes, or incident types."""

    # Construct request model with validation
    try:
        _request = _models.ListPlaybooksRequest(
            query=_models.ListPlaybooksRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_playbooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/playbooks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_playbooks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_playbooks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_playbooks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Playbooks
@mcp.tool()
async def create_playbook(
    type_: Literal["playbooks"] = Field(..., alias="type", description="The resource type identifier; must be set to 'playbooks' to indicate this is a playbook resource."),
    title: str = Field(..., description="The name of the playbook; used as the primary identifier in lists and displays."),
    summary: str | None = Field(None, description="A brief overview or description of the playbook's purpose and scope."),
    external_url: str | None = Field(None, description="A URL pointing to external documentation or resources related to this playbook."),
    severity_ids: list[str] | None = Field(None, description="Array of Severity IDs to associate with this playbook; determines which severity levels this playbook applies to."),
    environment_ids: list[str] | None = Field(None, description="Array of Environment IDs to associate with this playbook; specifies which environments (e.g., production, staging) this playbook is relevant for."),
    service_ids: list[str] | None = Field(None, description="Array of Service IDs to associate with this playbook; links the playbook to specific services it addresses."),
    functionality_ids: list[str] | None = Field(None, description="Array of Functionality IDs to associate with this playbook; categorizes the playbook by the functional areas it covers."),
    group_ids: list[str] | None = Field(None, description="Array of Team IDs to associate with this playbook; designates which teams own or are responsible for executing this playbook."),
    incident_type_ids: list[str] | None = Field(None, description="Array of Incident Type IDs to associate with this playbook; specifies which incident types this playbook provides guidance for."),
) -> dict[str, Any] | ToolResult:
    """Creates a new playbook with metadata and associations. Playbooks can be linked to severities, environments, services, functionalities, teams, and incident types for contextual organization."""

    # Construct request model with validation
    try:
        _request = _models.CreatePlaybookRequest(
            body=_models.CreatePlaybookRequestBody(data=_models.CreatePlaybookRequestBodyData(
                    type_=type_,
                    attributes=_models.CreatePlaybookRequestBodyDataAttributes(title=title, summary=summary, external_url=external_url, severity_ids=severity_ids, environment_ids=environment_ids, service_ids=service_ids, functionality_ids=functionality_ids, group_ids=group_ids, incident_type_ids=incident_type_ids)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_playbook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/playbooks"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_playbook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_playbook", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_playbook",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Playbooks
@mcp.tool()
async def get_playbook(
    id_: str = Field(..., alias="id", description="The unique identifier of the playbook to retrieve."),
    include: Literal["severities", "environments", "services", "functionalities", "groups", "causes", "incident_types"] | None = Field(None, description="Comma-separated list of related entities to include in the response. Valid options are: severities, environments, services, functionalities, groups, causes, and incident_types."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific playbook by its unique identifier, with optional related data expansion."""

    # Construct request model with validation
    try:
        _request = _models.GetPlaybookRequest(
            path=_models.GetPlaybookRequestPath(id_=id_),
            query=_models.GetPlaybookRequestQuery(include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_playbook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/playbooks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/playbooks/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_playbook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_playbook", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_playbook",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Playbooks
@mcp.tool()
async def update_playbook(
    id_: str = Field(..., alias="id", description="The unique identifier of the playbook to update."),
    type_: Literal["playbooks"] = Field(..., alias="type", description="The resource type identifier; must be set to 'playbooks'."),
    title: str | None = Field(None, description="The display name or title of the playbook."),
    summary: str | None = Field(None, description="A brief overview or description of the playbook's purpose and scope."),
    external_url: str | None = Field(None, description="A URL pointing to external documentation or resources related to this playbook."),
    severity_ids: list[str] | None = Field(None, description="An array of Severity IDs to associate with this playbook, determining the severity levels it applies to."),
    environment_ids: list[str] | None = Field(None, description="An array of Environment IDs to associate with this playbook, specifying which environments it applies to."),
    service_ids: list[str] | None = Field(None, description="An array of Service IDs to associate with this playbook, linking it to specific services."),
    functionality_ids: list[str] | None = Field(None, description="An array of Functionality IDs to associate with this playbook, defining which functionalities it covers."),
    group_ids: list[str] | None = Field(None, description="An array of Team IDs to associate with this playbook, specifying which teams own or are responsible for it."),
    incident_type_ids: list[str] | None = Field(None, description="An array of Incident Type IDs to associate with this playbook, indicating which incident types trigger or use this playbook."),
) -> dict[str, Any] | ToolResult:
    """Update an existing playbook with new metadata, associations, and configuration. Modify the playbook's title, summary, external reference, and linked resources such as severity levels, environments, services, functionalities, teams, and incident types."""

    # Construct request model with validation
    try:
        _request = _models.UpdatePlaybookRequest(
            path=_models.UpdatePlaybookRequestPath(id_=id_),
            body=_models.UpdatePlaybookRequestBody(data=_models.UpdatePlaybookRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdatePlaybookRequestBodyDataAttributes(title=title, summary=summary, external_url=external_url, severity_ids=severity_ids, environment_ids=environment_ids, service_ids=service_ids, functionality_ids=functionality_ids, group_ids=group_ids, incident_type_ids=incident_type_ids) if any(v is not None for v in [title, summary, external_url, severity_ids, environment_ids, service_ids, functionality_ids, group_ids, incident_type_ids]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_playbook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/playbooks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/playbooks/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_playbook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_playbook", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_playbook",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Playbooks
@mcp.tool()
async def delete_playbook(id_: str = Field(..., alias="id", description="The unique identifier of the playbook to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a playbook by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeletePlaybookRequest(
            path=_models.DeletePlaybookRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_playbook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/playbooks/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/playbooks/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_playbook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_playbook", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_playbook",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveTemplates
@mcp.tool()
async def list_postmortem_templates(
    include: str | None = Field(None, description="Comma-separated list of related fields to include in the response (e.g., metadata, tags). Specify which additional data should be populated alongside each template."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve when paginating through results. Use with page[size] to control which set of templates is returned."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of templates to return per page. Determines the size of each paginated result set."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of retrospective (post-mortem) templates available in the system. Use pagination parameters to control which templates are returned."""

    # Construct request model with validation
    try:
        _request = _models.ListPostmortemTemplatesRequest(
            query=_models.ListPostmortemTemplatesRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_postmortem_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/post_mortem_templates"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_postmortem_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_postmortem_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_postmortem_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveTemplates
@mcp.tool()
async def create_postmortem_template(
    type_: Literal["post_mortem_templates"] = Field(..., alias="type", description="The resource type identifier, must be set to 'post_mortem_templates' to specify this is a postmortem template resource."),
    name: str = Field(..., description="A descriptive name for the postmortem template that identifies its purpose or use case."),
    content: str = Field(..., description="The template content that defines the postmortem structure and sections. Supports Liquid template syntax for dynamic variable substitution."),
    default: bool | None = Field(None, description="When enabled, this template will be automatically selected as the default option when creating or editing postmortems."),
    format_: Literal["html", "markdown"] | None = Field(None, alias="format", description="The markup format of the template content, either HTML or Markdown. Defaults to HTML if not specified."),
) -> dict[str, Any] | ToolResult:
    """Creates a new postmortem template that can be used as a standardized format for retrospectives. Supports Liquid template syntax for dynamic content and can be set as the default template for postmortem editing."""

    # Construct request model with validation
    try:
        _request = _models.CreatePostmortemTemplateRequest(
            body=_models.CreatePostmortemTemplateRequestBody(data=_models.CreatePostmortemTemplateRequestBodyData(
                    type_=type_,
                    attributes=_models.CreatePostmortemTemplateRequestBodyDataAttributes(name=name, default=default, content=content, format_=format_)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_postmortem_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/post_mortem_templates"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_postmortem_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_postmortem_template", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_postmortem_template",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveTemplates
@mcp.tool()
async def get_postmortem_template(id_: str = Field(..., alias="id", description="The unique identifier of the postmortem template to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific postmortem (retrospective) template by its unique identifier. Use this to fetch template details for viewing or further processing."""

    # Construct request model with validation
    try:
        _request = _models.GetPostmortemTemplateRequest(
            path=_models.GetPostmortemTemplateRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_postmortem_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/post_mortem_templates/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/post_mortem_templates/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_postmortem_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_postmortem_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_postmortem_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveTemplates
@mcp.tool()
async def update_postmortem_template(
    id_: str = Field(..., alias="id", description="The unique identifier of the postmortem template to update."),
    type_: Literal["post_mortem_templates"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'post_mortem_templates' to specify this is a postmortem template resource."),
    default: bool | None = Field(None, description="Whether this template should be selected by default when creating or editing a postmortem."),
    content: str | None = Field(None, description="The postmortem template content. Supports Liquid template syntax for dynamic content generation."),
    format_: Literal["html", "markdown"] | None = Field(None, alias="format", description="The markup format of the template content. Accepts either HTML or Markdown; defaults to HTML if not specified."),
) -> dict[str, Any] | ToolResult:
    """Update an existing postmortem/retrospective template by ID. Modify the template content, format, and default status for use in postmortem creation and editing."""

    # Construct request model with validation
    try:
        _request = _models.UpdatePostmortemTemplateRequest(
            path=_models.UpdatePostmortemTemplateRequestPath(id_=id_),
            body=_models.UpdatePostmortemTemplateRequestBody(data=_models.UpdatePostmortemTemplateRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdatePostmortemTemplateRequestBodyDataAttributes(default=default, content=content, format_=format_) if any(v is not None for v in [default, content, format_]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_postmortem_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/post_mortem_templates/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/post_mortem_templates/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_postmortem_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_postmortem_template", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_postmortem_template",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveTemplates
@mcp.tool()
async def delete_postmortem_template(id_: str = Field(..., alias="id", description="The unique identifier of the retrospective template to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific retrospective template by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeletePostmortemTemplateRequest(
            path=_models.DeletePostmortemTemplateRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_postmortem_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/post_mortem_templates/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/post_mortem_templates/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_postmortem_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_postmortem_template", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_postmortem_template",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pulses
@mcp.tool()
async def list_pulses(
    include: str | None = Field(None, description="Comma-separated list of related fields to include in the response (e.g., source details, label metadata). Specify which associations should be expanded in each pulse record."),
    filter_source: str | None = Field(None, alias="filtersource", description="Filter pulses by their source identifier or name. Returns only pulses originating from the specified source."),
    filter_labels: str | None = Field(None, alias="filterlabels", description="Filter pulses by one or more labels. Specify as comma-separated values to match pulses tagged with any of the provided labels."),
    filter_refs: str | None = Field(None, alias="filterrefs", description="Filter pulses by one or more reference identifiers. Specify as comma-separated values to match pulses linked to any of the provided references."),
    filter_started_at__gte: str | None = Field(None, alias="filterstarted_atgte", description="Filter pulses by start time (greater than or equal). Specify as an ISO 8601 timestamp to include only pulses that started on or after this time."),
    filter_started_at__lte: str | None = Field(None, alias="filterstarted_atlte", description="Filter pulses by start time (less than or equal). Specify as an ISO 8601 timestamp to include only pulses that started on or before this time."),
    filter_ended_at__gte: str | None = Field(None, alias="filterended_atgte", description="Filter pulses by end time (greater than or equal). Specify as an ISO 8601 timestamp to include only pulses that ended on or after this time."),
    filter_ended_at__lte: str | None = Field(None, alias="filterended_atlte", description="Filter pulses by end time (less than or equal). Specify as an ISO 8601 timestamp to include only pulses that ended on or before this time."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve in the paginated result set. Use with page[size] to navigate through results. Defaults to the first page if not specified."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of pulses to return per page. Controls the size of each paginated batch. Adjust based on your performance and data needs."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of pulses with optional filtering by source, labels, references, and time ranges. Use this to query pulse events across your system with flexible filtering and pagination controls."""

    # Construct request model with validation
    try:
        _request = _models.ListPulsesRequest(
            query=_models.ListPulsesRequestQuery(include=include, filter_source=filter_source, filter_labels=filter_labels, filter_refs=filter_refs, filter_started_at__gte=filter_started_at__gte, filter_started_at__lte=filter_started_at__lte, filter_ended_at__gte=filter_ended_at__gte, filter_ended_at__lte=filter_ended_at__lte, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pulses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pulses"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pulses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pulses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pulses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pulses
@mcp.tool()
async def create_pulse(
    type_: Literal["pulses"] = Field(..., alias="type", description="The pulse type identifier. Must be set to 'pulses' to indicate this is a pulse event."),
    summary: str = Field(..., description="A brief, human-readable title describing the pulse event. This is the primary display name for the pulse."),
    source: str | None = Field(None, description="The origin system or service that generated this pulse (e.g., 'k8s' for Kubernetes, 'datadog', 'pagerduty'). Helps identify the pulse source for filtering and correlation."),
    service_ids: list[str] | None = Field(None, description="Array of service identifiers to associate with this pulse. Services linked to a pulse will receive or display this event. Order is not significant."),
    environment_ids: list[str] | None = Field(None, description="Array of environment identifiers to associate with this pulse (e.g., 'production', 'staging'). Helps scope the pulse to specific deployment environments. Order is not significant."),
    ended_at: str | None = Field(None, description="The timestamp when the pulse event ended or resolved, in ISO 8601 format. Omit if the pulse is ongoing."),
    external_url: str | None = Field(None, description="A URL pointing to additional details or the source system's record of this pulse. Useful for linking to incident reports, deployment logs, or monitoring dashboards."),
    data: dict[str, Any] | None = Field(None, description="A JSON object containing custom or additional metadata about the pulse. Structure and content are flexible and depend on the pulse source and use case."),
) -> dict[str, Any] | ToolResult:
    """Creates a new pulse event to track system incidents, deployments, or other notable occurrences. Pulses can be associated with services and environments, and may include additional metadata and external references."""

    # Construct request model with validation
    try:
        _request = _models.CreatePulseRequest(
            body=_models.CreatePulseRequestBody(data=_models.CreatePulseRequestBodyData(
                    type_=type_,
                    attributes=_models.CreatePulseRequestBodyDataAttributes(source=source, summary=summary, service_ids=service_ids, environment_ids=environment_ids, ended_at=ended_at, external_url=external_url, data=data)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_pulse: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pulses"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_pulse")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_pulse", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_pulse",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Pulses
@mcp.tool()
async def get_pulse(id_: str = Field(..., alias="id", description="The unique identifier of the pulse to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific pulse by its unique identifier. Use this operation to fetch detailed information about a single pulse."""

    # Construct request model with validation
    try:
        _request = _models.GetPulseRequest(
            path=_models.GetPulseRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pulse: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pulses/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pulses/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pulse")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pulse", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pulse",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pulses
@mcp.tool()
async def update_pulse(
    id_: str = Field(..., alias="id", description="The unique identifier of the pulse to update."),
    source: str | None = Field(None, description="The origin or system that generated this pulse (e.g., 'k8s' for Kubernetes)."),
    summary: str | None = Field(None, description="A brief, human-readable summary describing the pulse event or status."),
    service_ids: list[str] | None = Field(None, description="Array of service identifiers to associate with this pulse. Order is not significant. Each item should be a valid service ID string."),
    environment_ids: list[str] | None = Field(None, description="Array of environment identifiers to associate with this pulse. Order is not significant. Each item should be a valid environment ID string."),
    ended_at: str | None = Field(None, description="The date and time when the pulse ended or was resolved, specified in ISO 8601 format."),
    external_url: str | None = Field(None, description="A URL pointing to external resources or systems related to this pulse for additional context or details."),
    data: dict[str, Any] | None = Field(None, description="A flexible object for storing additional custom data or metadata associated with the pulse."),
) -> dict[str, Any] | ToolResult:
    """Update an existing pulse with new metadata, service/environment associations, status, or custom data. Allows modification of pulse properties such as summary, source, associated services and environments, completion status, and additional contextual information."""

    # Construct request model with validation
    try:
        _request = _models.UpdatePulseRequest(
            path=_models.UpdatePulseRequestPath(id_=id_),
            body=_models.UpdatePulseRequestBody(data=_models.UpdatePulseRequestBodyData(attributes=_models.UpdatePulseRequestBodyDataAttributes(source=source, summary=summary, service_ids=service_ids, environment_ids=environment_ids, ended_at=ended_at, external_url=external_url, data=data) if any(v is not None for v in [source, summary, service_ids, environment_ids, ended_at, external_url, data]) else None) if any(v is not None for v in [source, summary, service_ids, environment_ids, ended_at, external_url, data]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_pulse: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pulses/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pulses/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_pulse")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_pulse", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_pulse",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveConfigurations
@mcp.tool()
async def list_retrospective_configurations(
    include: Literal["severities", "groups", "incident_types"] | None = Field(None, description="Comma-separated list of related data to include in the response. Valid options are severities, groups, or incident_types. Omit this parameter to return only core configuration data."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through large result sets."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of configurations to return per page. Use with page[number] to control pagination."),
    filter_kind: str | None = Field(None, alias="filterkind", description="Filter configurations by kind. Specify the configuration kind value to narrow results to a specific type."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of retrospective configurations with optional related data. Use filtering and inclusion parameters to customize the results returned."""

    # Construct request model with validation
    try:
        _request = _models.ListRetrospectiveConfigurationsRequest(
            query=_models.ListRetrospectiveConfigurationsRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_kind=filter_kind)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_retrospective_configurations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/retrospective_configurations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_retrospective_configurations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_retrospective_configurations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_retrospective_configurations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveConfigurations
@mcp.tool()
async def get_retrospective_configuration(
    id_: str = Field(..., alias="id", description="The unique identifier of the retrospective configuration to retrieve."),
    include: Literal["severities", "groups", "incident_types"] | None = Field(None, description="Optional comma-separated list of related entities to include in the response. Valid options are severities, groups, or incident_types."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific retrospective configuration by its unique identifier, with optional related data inclusion."""

    # Construct request model with validation
    try:
        _request = _models.GetRetrospectiveConfigurationRequest(
            path=_models.GetRetrospectiveConfigurationRequestPath(id_=id_),
            query=_models.GetRetrospectiveConfigurationRequestQuery(include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_retrospective_configuration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/retrospective_configurations/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/retrospective_configurations/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_retrospective_configuration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_retrospective_configuration", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_retrospective_configuration",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveConfigurations
@mcp.tool()
async def update_retrospective_configuration(
    id_: str = Field(..., alias="id", description="The unique identifier of the retrospective configuration to update."),
    type_: Literal["retrospective_configurations"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'retrospective_configurations' to specify the resource being updated."),
    severity_ids: list[str] | None = Field(None, description="An array of severity IDs to associate with this retrospective configuration. Incidents matching any of these severity levels will be subject to this configuration's retrospective rules."),
    group_ids: list[str] | None = Field(None, description="An array of team IDs to associate with this retrospective configuration. Incidents assigned to any of these teams will be subject to this configuration's retrospective rules."),
    incident_type_ids: list[str] | None = Field(None, description="An array of incident type IDs to associate with this retrospective configuration. Incidents classified as any of these types will be subject to this configuration's retrospective rules."),
) -> dict[str, Any] | ToolResult:
    """Update an existing retrospective configuration by modifying its associated severities, teams, and incident types. This operation allows you to refine which incidents trigger retrospectives based on their severity level, assigned team, and incident classification."""

    # Construct request model with validation
    try:
        _request = _models.UpdateRetrospectiveConfigurationRequest(
            path=_models.UpdateRetrospectiveConfigurationRequestPath(id_=id_),
            body=_models.UpdateRetrospectiveConfigurationRequestBody(data=_models.UpdateRetrospectiveConfigurationRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateRetrospectiveConfigurationRequestBodyDataAttributes(severity_ids=severity_ids, group_ids=group_ids, incident_type_ids=incident_type_ids) if any(v is not None for v in [severity_ids, group_ids, incident_type_ids]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_retrospective_configuration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/retrospective_configurations/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/retrospective_configurations/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_retrospective_configuration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_retrospective_configuration", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_retrospective_configuration",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveProcessGroupSteps
@mcp.tool()
async def list_retrospective_process_group_steps(
    retrospective_process_group_id: str = Field(..., description="The unique identifier of the retrospective process group whose steps you want to list."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., nested objects or associations)."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of steps to return per page. Adjust this value along with page[number] to control result set size."),
    filter_retrospective_step_id: str | None = Field(None, alias="filterretrospective_step_id", description="Filter results by retrospective step ID. Accepts a single step identifier to narrow the list to matching steps."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of steps within a specific retrospective process group. Use filtering and inclusion options to customize the results."""

    # Construct request model with validation
    try:
        _request = _models.ListRetrospectiveProcessGroupStepsRequest(
            path=_models.ListRetrospectiveProcessGroupStepsRequestPath(retrospective_process_group_id=retrospective_process_group_id),
            query=_models.ListRetrospectiveProcessGroupStepsRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_retrospective_step_id=filter_retrospective_step_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_retrospective_process_group_steps: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/retrospective_process_groups/{retrospective_process_group_id}/steps", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/retrospective_process_groups/{retrospective_process_group_id}/steps"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_retrospective_process_group_steps")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_retrospective_process_group_steps", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_retrospective_process_group_steps",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveProcessGroupSteps
@mcp.tool()
async def get_retrospective_process_group_step(id_: str = Field(..., alias="id", description="The unique identifier of the retrospective process group step to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific retrospective process group step by its unique identifier. Use this to fetch detailed information about a single step within a retrospective process group."""

    # Construct request model with validation
    try:
        _request = _models.GetRetrospectiveProcessGroupStepRequest(
            path=_models.GetRetrospectiveProcessGroupStepRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_retrospective_process_group_step: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/retrospective_process_group_steps/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/retrospective_process_group_steps/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_retrospective_process_group_step")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_retrospective_process_group_step", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_retrospective_process_group_step",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveProcessGroups
@mcp.tool()
async def list_retrospective_process_groups(
    retrospective_process_id: str = Field(..., description="The unique identifier of the retrospective process containing the groups to list."),
    include: Literal["retrospective_process_group_steps"] | None = Field(None, description="Comma-separated list of related resources to include in the response. Use 'retrospective_process_group_steps' to embed step details within each group."),
    sort: Literal["created_at", "-created_at", "updated_at", "-updated_at", "position", "-position"] | None = Field(None, description="Comma-separated list of fields to sort results by. Prefix with hyphen (e.g., '-created_at') for descending order. Available fields: created_at, updated_at, and position."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination (1-indexed). Use with page[size] to retrieve specific result sets."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of results per page for pagination. Determines how many groups are returned in each page."),
    filter_sub_status_id: str | None = Field(None, alias="filtersub_status_id", description="Filter results by a specific sub-status identifier to return only groups matching that sub-status."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all groups within a specific retrospective process. Supports filtering, sorting, and optional inclusion of nested group steps."""

    # Construct request model with validation
    try:
        _request = _models.ListRetrospectiveProcessGroupsRequest(
            path=_models.ListRetrospectiveProcessGroupsRequestPath(retrospective_process_id=retrospective_process_id),
            query=_models.ListRetrospectiveProcessGroupsRequestQuery(include=include, sort=sort, page_number=page_number, page_size=page_size, filter_sub_status_id=filter_sub_status_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_retrospective_process_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/retrospective_processes/{retrospective_process_id}/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/retrospective_processes/{retrospective_process_id}/groups"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_retrospective_process_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_retrospective_process_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_retrospective_process_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveProcessGroups
@mcp.tool()
async def get_retrospective_process_group(
    id_: str = Field(..., alias="id", description="The unique identifier of the Retrospective Process Group to retrieve."),
    include: Literal["retrospective_process_group_steps"] | None = Field(None, description="Comma-separated list of related resources to include in the response. Use 'retrospective_process_group_steps' to include the process group's associated steps."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific Retrospective Process Group by its unique identifier. Optionally include related process group steps in the response."""

    # Construct request model with validation
    try:
        _request = _models.GetRetrospectiveProcessGroupRequest(
            path=_models.GetRetrospectiveProcessGroupRequestPath(id_=id_),
            query=_models.GetRetrospectiveProcessGroupRequestQuery(include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_retrospective_process_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/retrospective_process_groups/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/retrospective_process_groups/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_retrospective_process_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_retrospective_process_group", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_retrospective_process_group",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveProcesses
@mcp.tool()
async def list_retrospective_processes(
    include: Literal["retrospective_steps", "severities", "incident_types", "groups"] | None = Field(None, description="Comma-separated list of related entities to include in the response. Valid options are: retrospective_steps, severities, incident_types, and groups. Omit this parameter to return only core retrospective process data."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use this to navigate through result sets when combined with page size."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of retrospective processes to return per page. Use this to control result set size for pagination."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of retrospective processes with optional related data. Use the include parameter to expand the response with associated retrospective steps, severity levels, incident types, or groups."""

    # Construct request model with validation
    try:
        _request = _models.ListRetrospectiveProcessesRequest(
            query=_models.ListRetrospectiveProcessesRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_retrospective_processes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/retrospective_processes"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_retrospective_processes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_retrospective_processes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_retrospective_processes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveProcesses
@mcp.tool()
async def create_retrospective_process(
    type_: Literal["retrospective_processes"] = Field(..., alias="type", description="The resource type identifier; must be set to 'retrospective_processes' to indicate this operation creates a retrospective process resource."),
    name: str = Field(..., description="A human-readable name for the retrospective process that will be displayed in your team's workflow."),
    copy_from: str = Field(..., description="The source for retrospective steps: either the ID of an existing retrospective process to copy steps from, or the literal value 'starter_template' to use a pre-configured template of standard retrospective steps."),
    description: str | None = Field(None, description="An optional detailed description of the retrospective process's purpose, scope, or any special instructions for participants."),
    retrospective_process_matching_criteria: _models.CreateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV0 | _models.CreateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV1 | _models.CreateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV2 | None = Field(None, description="Optional criteria object used to automatically match and assign retrospective processes to relevant teams, projects, or other entities based on specified conditions."),
) -> dict[str, Any] | ToolResult:
    """Creates a new retrospective process with optional configuration for copying steps from an existing process or starter template. Use this to set up a structured retrospective workflow for your team."""

    # Construct request model with validation
    try:
        _request = _models.CreateRetrospectiveProcessRequest(
            body=_models.CreateRetrospectiveProcessRequestBody(data=_models.CreateRetrospectiveProcessRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateRetrospectiveProcessRequestBodyDataAttributes(name=name, copy_from=copy_from, description=description, retrospective_process_matching_criteria=retrospective_process_matching_criteria)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_retrospective_process: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/retrospective_processes"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_retrospective_process")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_retrospective_process", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_retrospective_process",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveProcesses
@mcp.tool()
async def get_retrospective_process(
    id_: str = Field(..., alias="id", description="The unique identifier of the retrospective process to retrieve."),
    include: Literal["retrospective_steps", "severities", "incident_types", "groups"] | None = Field(None, description="Comma-separated list of related entities to include in the response. Valid options are retrospective_steps, severities, incident_types, and groups."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific retrospective process by its unique identifier, with optional related data expansion."""

    # Construct request model with validation
    try:
        _request = _models.GetRetrospectiveProcessRequest(
            path=_models.GetRetrospectiveProcessRequestPath(id_=id_),
            query=_models.GetRetrospectiveProcessRequestQuery(include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_retrospective_process: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/retrospective_processes/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/retrospective_processes/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_retrospective_process")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_retrospective_process", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_retrospective_process",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveProcesses
@mcp.tool()
async def update_retrospective_process(
    id_: str = Field(..., alias="id", description="The unique identifier of the retrospective process to update."),
    type_: Literal["retrospective_processes"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'retrospective_processes' to specify the entity being updated."),
    description: str | None = Field(None, description="A human-readable description of the retrospective process, explaining its purpose and scope."),
    retrospective_process_matching_criteria: _models.UpdateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV0 | _models.UpdateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV1 | _models.UpdateRetrospectiveProcessBodyDataAttributesRetrospectiveProcessMatchingCriteriaV2 | None = Field(None, description="Criteria object that defines the matching rules for identifying which retrospectives belong to this process. Specifies conditions such as team, project, or time-based filters."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing retrospective process with new configuration details. Allows modification of the process description and matching criteria to refine how retrospectives are identified and organized."""

    # Construct request model with validation
    try:
        _request = _models.UpdateRetrospectiveProcessRequest(
            path=_models.UpdateRetrospectiveProcessRequestPath(id_=id_),
            body=_models.UpdateRetrospectiveProcessRequestBody(data=_models.UpdateRetrospectiveProcessRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateRetrospectiveProcessRequestBodyDataAttributes(description=description, retrospective_process_matching_criteria=retrospective_process_matching_criteria) if any(v is not None for v in [description, retrospective_process_matching_criteria]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_retrospective_process: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/retrospective_processes/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/retrospective_processes/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_retrospective_process")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_retrospective_process", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_retrospective_process",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveProcesses
@mcp.tool()
async def delete_retrospective_process(id_: str = Field(..., alias="id", description="The unique identifier of the retrospective process to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a retrospective process and all associated data by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRetrospectiveProcessRequest(
            path=_models.DeleteRetrospectiveProcessRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_retrospective_process: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/retrospective_processes/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/retrospective_processes/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_retrospective_process")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_retrospective_process", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_retrospective_process",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveSteps
@mcp.tool()
async def list_retrospective_steps(
    retrospective_process_id: str = Field(..., description="The unique identifier of the retrospective process containing the steps to retrieve."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., participants, feedback, outcomes). Reduces need for additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through large result sets."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of retrospective steps to return per page. Adjust to balance response size and number of requests needed."),
    sort: str | None = Field(None, description="Sort results by specified field(s) in ascending or descending order. Use format: field_name or -field_name for reverse order (e.g., created_at or -created_at)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of retrospective steps for a specific retrospective process. Use pagination and sorting parameters to customize the results."""

    # Construct request model with validation
    try:
        _request = _models.ListRetrospectiveStepsRequest(
            path=_models.ListRetrospectiveStepsRequestPath(retrospective_process_id=retrospective_process_id),
            query=_models.ListRetrospectiveStepsRequestQuery(include=include, page_number=page_number, page_size=page_size, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_retrospective_steps: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/retrospective_processes/{retrospective_process_id}/retrospective_steps", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/retrospective_processes/{retrospective_process_id}/retrospective_steps"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_retrospective_steps")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_retrospective_steps", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_retrospective_steps",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveSteps
@mcp.tool()
async def create_retrospective_step(
    retrospective_process_id: str = Field(..., description="The unique identifier of the retrospective process to which this step belongs."),
    type_: Literal["retrospective_steps"] = Field(..., alias="type", description="The resource type identifier for this operation, which must be set to 'retrospective_steps'."),
    title: str = Field(..., description="The display name for this retrospective step."),
    description: str | None = Field(None, description="Additional context or instructions for participants about what to do during this step."),
    due_after_days: int | None = Field(None, description="Number of days after the retrospective starts when this step becomes due. Helps schedule step progression over time."),
    position: int | None = Field(None, description="The ordinal position of this step within the retrospective process sequence. Lower numbers appear first."),
    skippable: bool | None = Field(None, description="Whether participants can skip this step if needed. When true, the step can be bypassed; when false, it must be completed."),
) -> dict[str, Any] | ToolResult:
    """Creates a new step within a retrospective process. Steps define discrete phases or activities that guide the retrospective workflow."""

    # Construct request model with validation
    try:
        _request = _models.CreateRetrospectiveStepRequest(
            path=_models.CreateRetrospectiveStepRequestPath(retrospective_process_id=retrospective_process_id),
            body=_models.CreateRetrospectiveStepRequestBody(data=_models.CreateRetrospectiveStepRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateRetrospectiveStepRequestBodyDataAttributes(title=title, description=description, due_after_days=due_after_days, position=position, skippable=skippable)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_retrospective_step: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/retrospective_processes/{retrospective_process_id}/retrospective_steps", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/retrospective_processes/{retrospective_process_id}/retrospective_steps"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_retrospective_step")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_retrospective_step", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_retrospective_step",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveSteps
@mcp.tool()
async def get_retrospective_step(id_: str = Field(..., alias="id", description="The unique identifier of the retrospective step to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific retrospective step by its unique identifier. Use this to fetch details about a single retrospective step within a retrospective."""

    # Construct request model with validation
    try:
        _request = _models.GetRetrospectiveStepRequest(
            path=_models.GetRetrospectiveStepRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_retrospective_step: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/retrospective_steps/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/retrospective_steps/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_retrospective_step")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_retrospective_step", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_retrospective_step",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveSteps
@mcp.tool()
async def update_retrospective_step(
    id_: str = Field(..., alias="id", description="The unique identifier of the retrospective step to update."),
    type_: Literal["retrospective_steps"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'retrospective_steps' to specify the entity being updated."),
    title: str | None = Field(None, description="The display name or title of the retrospective step."),
    description: str | None = Field(None, description="A detailed explanation of the retrospective step's purpose and content."),
    due_after_days: int | None = Field(None, description="The number of days after retrospective creation when this step becomes due."),
    position: int | None = Field(None, description="The ordinal position of this step within the retrospective sequence, determining its display order."),
    skippable: bool | None = Field(None, description="Whether participants can skip this step during the retrospective process."),
) -> dict[str, Any] | ToolResult:
    """Update a specific retrospective step by its ID. Modify step details such as title, description, timing, position, and skippability to refine your retrospective workflow."""

    # Construct request model with validation
    try:
        _request = _models.UpdateRetrospectiveStepRequest(
            path=_models.UpdateRetrospectiveStepRequestPath(id_=id_),
            body=_models.UpdateRetrospectiveStepRequestBody(data=_models.UpdateRetrospectiveStepRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateRetrospectiveStepRequestBodyDataAttributes(title=title, description=description, due_after_days=due_after_days, position=position, skippable=skippable) if any(v is not None for v in [title, description, due_after_days, position, skippable]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_retrospective_step: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/retrospective_steps/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/retrospective_steps/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_retrospective_step")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_retrospective_step", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_retrospective_step",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: RetrospectiveSteps
@mcp.tool()
async def delete_retrospective_step(id_: str = Field(..., alias="id", description="The unique identifier of the retrospective step to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a retrospective step by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRetrospectiveStepRequest(
            path=_models.DeleteRetrospectiveStepRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_retrospective_step: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/retrospective_steps/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/retrospective_steps/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_retrospective_step")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_retrospective_step", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_retrospective_step",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Roles
@mcp.tool()
async def list_roles(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., permissions, users). Reduces the need for additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve for paginated results, starting from 1. Use with page[size] to control pagination."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of roles to return per page. Adjust this value to balance between response size and number of requests needed."),
    sort: str | None = Field(None, description="Sort the results by one or more fields using a comma-separated list. Prefix field names with a minus sign (-) to sort in descending order (e.g., -created_at,name)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of all available roles in the system. Supports filtering, sorting, and customizable pagination."""

    # Construct request model with validation
    try:
        _request = _models.ListRolesRequest(
            query=_models.ListRolesRequestQuery(include=include, page_number=page_number, page_size=page_size, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_roles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/roles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_roles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_roles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_roles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Roles
@mcp.tool()
async def get_role(id_: str = Field(..., alias="id", description="The unique identifier of the role to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific role by its unique identifier. Use this operation to fetch detailed information about a role."""

    # Construct request model with validation
    try:
        _request = _models.GetRoleRequest(
            path=_models.GetRoleRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/roles/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/roles/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_role", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_role",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Roles
@mcp.tool()
async def delete_role(id_: str = Field(..., alias="id", description="The unique identifier of the role to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a role by its unique identifier. This action removes the role and its associated permissions from the system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRoleRequest(
            path=_models.DeleteRoleRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/roles/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/roles/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_role", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_role",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: ScheduleRotationActiveDays
@mcp.tool()
async def list_schedule_rotation_active_days(
    schedule_rotation_id: str = Field(..., description="The unique identifier of the schedule rotation for which to list active days."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., schedule, users). Reduces the need for additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of active days to return per page. Adjust to balance response size and number of requests needed."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of active days for a specific schedule rotation. Active days define when the rotation is in effect."""

    # Construct request model with validation
    try:
        _request = _models.ListScheduleRotationActiveDaysRequest(
            path=_models.ListScheduleRotationActiveDaysRequestPath(schedule_rotation_id=schedule_rotation_id),
            query=_models.ListScheduleRotationActiveDaysRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_schedule_rotation_active_days: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedule_rotations/{schedule_rotation_id}/schedule_rotation_active_days", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedule_rotations/{schedule_rotation_id}/schedule_rotation_active_days"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_schedule_rotation_active_days")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_schedule_rotation_active_days", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_schedule_rotation_active_days",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: ScheduleRotationActiveDays
@mcp.tool()
async def add_active_day_to_schedule_rotation(
    schedule_rotation_id: str = Field(..., description="The unique identifier of the schedule rotation to which the active day will be added."),
    type_: Literal["schedule_rotation_active_days"] = Field(..., alias="type", description="The resource type identifier. Must be set to 'schedule_rotation_active_days' to indicate this is a schedule rotation active day resource."),
    day_name: Literal["S", "M", "T", "W", "R", "F", "U"] = Field(..., description="The day of the week for which active times are being configured. Use single-letter abbreviations: S (Sunday), M (Monday), T (Tuesday), W (Wednesday), R (Thursday), F (Friday), or U (Sunday alternate)."),
    active_time_attributes: list[_models.CreateScheduleRotationActiveDayBodyDataAttributesActiveTimeAttributesItem] = Field(..., description="An ordered array of active time periods for the specified day. Each item defines a time window when the schedule rotation is active. Order matters and determines the sequence of active periods throughout the day."),
) -> dict[str, Any] | ToolResult:
    """Adds an active day with specified time slots to a schedule rotation. This defines when the rotation is active for a particular day of the week."""

    # Construct request model with validation
    try:
        _request = _models.CreateScheduleRotationActiveDayRequest(
            path=_models.CreateScheduleRotationActiveDayRequestPath(schedule_rotation_id=schedule_rotation_id),
            body=_models.CreateScheduleRotationActiveDayRequestBody(data=_models.CreateScheduleRotationActiveDayRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateScheduleRotationActiveDayRequestBodyDataAttributes(day_name=day_name, active_time_attributes=active_time_attributes)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_active_day_to_schedule_rotation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedule_rotations/{schedule_rotation_id}/schedule_rotation_active_days", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedule_rotations/{schedule_rotation_id}/schedule_rotation_active_days"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_active_day_to_schedule_rotation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_active_day_to_schedule_rotation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_active_day_to_schedule_rotation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: ScheduleRotationActiveDays
@mcp.tool()
async def get_schedule_rotation_active_day(id_: str = Field(..., alias="id", description="The unique identifier of the schedule rotation active day to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific schedule rotation active day by its unique identifier. Use this to fetch details about a particular day within a schedule rotation."""

    # Construct request model with validation
    try:
        _request = _models.GetScheduleRotationActiveDayRequest(
            path=_models.GetScheduleRotationActiveDayRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_schedule_rotation_active_day: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedule_rotation_active_days/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedule_rotation_active_days/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_schedule_rotation_active_day")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_schedule_rotation_active_day", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_schedule_rotation_active_day",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: ScheduleRotationActiveDays
@mcp.tool()
async def update_schedule_rotation_active_day(
    id_: str = Field(..., alias="id", description="The unique identifier of the schedule rotation active day record to update."),
    type_: Literal["schedule_rotation_active_days"] = Field(..., alias="type", description="The resource type identifier, which must be 'schedule_rotation_active_days' to specify the type of object being updated."),
    day_name: Literal["S", "M", "T", "W", "R", "F", "U"] | None = Field(None, description="The day of the week for which active times apply, using single-letter abbreviations: S (Sunday), M (Monday), T (Tuesday), W (Wednesday), R (Thursday), F (Friday), or U (Sunday alternate)."),
    active_time_attributes: list[_models.UpdateScheduleRotationActiveDayBodyDataAttributesActiveTimeAttributesItem] | None = Field(None, description="An ordered array of active time period objects that define when the schedule rotation is active on the specified day. Each item configures a time window with start and end times."),
) -> dict[str, Any] | ToolResult:
    """Update the active times for a specific day within a schedule rotation. Modify which day of the week is active and configure the active time periods for that day."""

    # Construct request model with validation
    try:
        _request = _models.UpdateScheduleRotationActiveDayRequest(
            path=_models.UpdateScheduleRotationActiveDayRequestPath(id_=id_),
            body=_models.UpdateScheduleRotationActiveDayRequestBody(data=_models.UpdateScheduleRotationActiveDayRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateScheduleRotationActiveDayRequestBodyDataAttributes(day_name=day_name, active_time_attributes=active_time_attributes) if any(v is not None for v in [day_name, active_time_attributes]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_schedule_rotation_active_day: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedule_rotation_active_days/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedule_rotation_active_days/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_schedule_rotation_active_day")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_schedule_rotation_active_day", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_schedule_rotation_active_day",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: ScheduleRotationActiveDays
@mcp.tool()
async def delete_schedule_rotation_active_day(id_: str = Field(..., alias="id", description="The unique identifier of the schedule rotation active day to delete.")) -> dict[str, Any] | ToolResult:
    """Remove a specific schedule rotation active day from the system. This operation permanently deletes the identified active day configuration."""

    # Construct request model with validation
    try:
        _request = _models.DeleteScheduleRotationActiveDayRequest(
            path=_models.DeleteScheduleRotationActiveDayRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_schedule_rotation_active_day: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedule_rotation_active_days/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedule_rotation_active_days/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_schedule_rotation_active_day")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_schedule_rotation_active_day", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_schedule_rotation_active_day",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: ScheduleRotationUsers
@mcp.tool()
async def list_schedule_rotation_users(
    schedule_rotation_id: str = Field(..., description="The unique identifier of the schedule rotation for which to list assigned users."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., user details, rotation metadata). Specify which associations to expand for richer response data."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use this to navigate through result sets when the total exceeds the page size."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of users to return per page. Adjust this to control the size of each paginated response."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of users assigned to a specific schedule rotation. Use this to view all participants in a rotation schedule with optional filtering and pagination controls."""

    # Construct request model with validation
    try:
        _request = _models.ListScheduleRotationUsersRequest(
            path=_models.ListScheduleRotationUsersRequestPath(schedule_rotation_id=schedule_rotation_id),
            query=_models.ListScheduleRotationUsersRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_schedule_rotation_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedule_rotations/{schedule_rotation_id}/schedule_rotation_users", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedule_rotations/{schedule_rotation_id}/schedule_rotation_users"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_schedule_rotation_users")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_schedule_rotation_users", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_schedule_rotation_users",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: ScheduleRotationUsers
@mcp.tool()
async def add_user_to_schedule_rotation(
    schedule_rotation_id: str = Field(..., description="The unique identifier of the schedule rotation to which the user will be added."),
    user_id: int = Field(..., description="The unique identifier of the user to add to the schedule rotation."),
    position: int | None = Field(None, description="The position where the user should be placed in the rotation sequence. If not specified, the user will be added at the end of the rotation."),
) -> dict[str, Any] | ToolResult:
    """Adds a user to an existing schedule rotation, optionally specifying their position in the rotation order."""

    # Construct request model with validation
    try:
        _request = _models.CreateScheduleRotationUserRequest(
            path=_models.CreateScheduleRotationUserRequestPath(schedule_rotation_id=schedule_rotation_id),
            body=_models.CreateScheduleRotationUserRequestBody(data=_models.CreateScheduleRotationUserRequestBodyData(
                    attributes=_models.CreateScheduleRotationUserRequestBodyDataAttributes(user_id=user_id, position=position)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_user_to_schedule_rotation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedule_rotations/{schedule_rotation_id}/schedule_rotation_users", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedule_rotations/{schedule_rotation_id}/schedule_rotation_users"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_user_to_schedule_rotation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_user_to_schedule_rotation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_user_to_schedule_rotation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: ScheduleRotationUsers
@mcp.tool()
async def get_schedule_rotation_user(id_: str = Field(..., alias="id", description="The unique identifier of the schedule rotation user to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific schedule rotation user by their unique identifier. Use this to fetch details about an individual user assigned to a schedule rotation."""

    # Construct request model with validation
    try:
        _request = _models.GetScheduleRotationUserRequest(
            path=_models.GetScheduleRotationUserRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_schedule_rotation_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedule_rotation_users/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedule_rotation_users/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_schedule_rotation_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_schedule_rotation_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_schedule_rotation_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: ScheduleRotationUsers
@mcp.tool()
async def update_schedule_rotation_user(
    id_: str = Field(..., alias="id", description="The unique identifier of the schedule rotation user record to update."),
    type_: Literal["schedule_rotation_users"] = Field(..., alias="type", description="The resource type identifier, which must be 'schedule_rotation_users' to specify the target resource type."),
    user_id: int | None = Field(None, description="The ID of the user to assign to this rotation slot."),
    position: int | None = Field(None, description="The sequential position of this user within the rotation order, determining when they are scheduled."),
) -> dict[str, Any] | ToolResult:
    """Update a specific user's position and assignment within a schedule rotation by their unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.UpdateScheduleRotationUserRequest(
            path=_models.UpdateScheduleRotationUserRequestPath(id_=id_),
            body=_models.UpdateScheduleRotationUserRequestBody(data=_models.UpdateScheduleRotationUserRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateScheduleRotationUserRequestBodyDataAttributes(user_id=user_id, position=position) if any(v is not None for v in [user_id, position]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_schedule_rotation_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedule_rotation_users/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedule_rotation_users/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_schedule_rotation_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_schedule_rotation_user", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_schedule_rotation_user",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: ScheduleRotationUsers
@mcp.tool()
async def delete_schedule_rotation_user(id_: str = Field(..., alias="id", description="The unique identifier of the schedule rotation user to delete.")) -> dict[str, Any] | ToolResult:
    """Remove a schedule rotation user from the system by their unique identifier. This operation permanently deletes the specified schedule rotation user record."""

    # Construct request model with validation
    try:
        _request = _models.DeleteScheduleRotationUserRequest(
            path=_models.DeleteScheduleRotationUserRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_schedule_rotation_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedule_rotation_users/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedule_rotation_users/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_schedule_rotation_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_schedule_rotation_user", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_schedule_rotation_user",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: ScheduleRotations
@mcp.tool()
async def list_schedule_rotations(
    schedule_id: str = Field(..., description="The unique identifier of the schedule for which to list rotations."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., users, shifts). Reduces the need for additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve for paginated results, starting from 1."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of rotations to return per page. Adjust to balance response size and number of requests needed."),
    sort: str | None = Field(None, description="Sort results by specified field(s) in ascending or descending order. Use format: field_name or -field_name for descending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of schedule rotations for a specific schedule. Use pagination and sorting parameters to customize the results."""

    # Construct request model with validation
    try:
        _request = _models.ListScheduleRotationsRequest(
            path=_models.ListScheduleRotationsRequestPath(schedule_id=schedule_id),
            query=_models.ListScheduleRotationsRequestQuery(include=include, page_number=page_number, page_size=page_size, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_schedule_rotations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedules/{schedule_id}/schedule_rotations", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedules/{schedule_id}/schedule_rotations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_schedule_rotations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_schedule_rotations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_schedule_rotations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: ScheduleRotations
@mcp.tool()
async def create_schedule_rotation(
    schedule_id: str = Field(..., description="The unique identifier of the schedule to which this rotation will be added."),
    type_: Literal["schedule_rotations"] = Field(..., alias="type", description="The resource type identifier; must be set to 'schedule_rotations'."),
    name: str = Field(..., description="A human-readable name for this schedule rotation."),
    schedule_rotationable_type: Literal["ScheduleDailyRotation", "ScheduleWeeklyRotation", "ScheduleBiweeklyRotation", "ScheduleMonthlyRotation", "ScheduleCustomRotation"] = Field(..., description="The rotation pattern type: daily, weekly, biweekly, monthly, or custom. This determines how the rotation cycles through team members."),
    schedule_rotationable_attributes: _models.CreateScheduleRotationBodyDataAttributesScheduleRotationableAttributes = Field(..., description="Configuration object containing rotation-specific parameters; structure varies based on the selected rotation type (e.g., interval length for custom rotations, day-of-month for monthly rotations)."),
    position: int | None = Field(None, description="The ordinal position of this rotation within the schedule's rotation sequence; determines the order in which rotations are applied."),
    active_days: list[Literal["S", "M", "T", "W", "R", "F", "U"]] | None = Field(None, description="An array of days when this rotation is active; typically specified as day-of-week identifiers or date values depending on the rotation type."),
    active_time_attributes: list[_models.CreateScheduleRotationBodyDataAttributesActiveTimeAttributesItem] | None = Field(None, description="An array of time windows during which this rotation applies; each entry defines when on-call coverage is active for this rotation."),
    time_zone: str | None = Field(None, description="The IANA time zone name (e.g., 'America/New_York', 'Europe/London') used to interpret active times and rotation schedules; defaults to UTC if not specified."),
) -> dict[str, Any] | ToolResult:
    """Creates a new schedule rotation within a schedule, defining how on-call shifts rotate across team members. Specify the rotation type (daily, weekly, biweekly, monthly, or custom), active times, and rotation-specific configuration."""

    # Construct request model with validation
    try:
        _request = _models.CreateScheduleRotationRequest(
            path=_models.CreateScheduleRotationRequestPath(schedule_id=schedule_id),
            body=_models.CreateScheduleRotationRequestBody(data=_models.CreateScheduleRotationRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateScheduleRotationRequestBodyDataAttributes(name=name, position=position, schedule_rotationable_type=schedule_rotationable_type, active_days=active_days, active_time_attributes=active_time_attributes, time_zone=time_zone, schedule_rotationable_attributes=schedule_rotationable_attributes)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_schedule_rotation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedules/{schedule_id}/schedule_rotations", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedules/{schedule_id}/schedule_rotations"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_schedule_rotation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_schedule_rotation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_schedule_rotation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: ScheduleRotations
@mcp.tool()
async def get_schedule_rotation(id_: str = Field(..., alias="id", description="The unique identifier of the schedule rotation to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific schedule rotation by its unique identifier. Use this to fetch details about a particular rotation configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetScheduleRotationRequest(
            path=_models.GetScheduleRotationRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_schedule_rotation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedule_rotations/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedule_rotations/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_schedule_rotation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_schedule_rotation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_schedule_rotation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: ScheduleRotations
@mcp.tool()
async def update_schedule_rotation(
    id_: str = Field(..., alias="id", description="The unique identifier of the schedule rotation to update."),
    type_: Literal["schedule_rotations"] = Field(..., alias="type", description="The resource type identifier, which must be 'schedule_rotations' to specify this is a schedule rotation resource."),
    schedule_rotationable_type: Literal["ScheduleDailyRotation", "ScheduleWeeklyRotation", "ScheduleBiweeklyRotation", "ScheduleMonthlyRotation", "ScheduleCustomRotation"] = Field(..., description="The rotation pattern type: daily, weekly, biweekly, monthly, or custom rotation schedules."),
    position: int | None = Field(None, description="The ordinal position of this schedule rotation in the sequence, used to determine rotation order."),
    active_days: list[Literal["S", "M", "T", "W", "R", "F", "U"]] | None = Field(None, description="An array of days when the rotation is active. Order and format depend on the selected rotation type."),
    active_time_attributes: list[_models.UpdateScheduleRotationBodyDataAttributesActiveTimeAttributesItem] | None = Field(None, description="An array of time window objects defining when the rotation applies each day, including start and end times."),
    time_zone: str | None = Field(None, description="The IANA timezone identifier for interpreting all times in this rotation (defaults to Etc/UTC if not specified)."),
    schedule_rotationable_attributes: _models.UpdateScheduleRotationBodyDataAttributesScheduleRotationableAttributes | None = Field(None, description="Configuration object containing rotation-specific parameters that vary based on the selected rotation type."),
) -> dict[str, Any] | ToolResult:
    """Update an existing schedule rotation configuration, including its rotation type, active days, time windows, and timezone settings."""

    # Construct request model with validation
    try:
        _request = _models.UpdateScheduleRotationRequest(
            path=_models.UpdateScheduleRotationRequestPath(id_=id_),
            body=_models.UpdateScheduleRotationRequestBody(data=_models.UpdateScheduleRotationRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateScheduleRotationRequestBodyDataAttributes(position=position, schedule_rotationable_type=schedule_rotationable_type, active_days=active_days, active_time_attributes=active_time_attributes, time_zone=time_zone, schedule_rotationable_attributes=schedule_rotationable_attributes)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_schedule_rotation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedule_rotations/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedule_rotations/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_schedule_rotation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_schedule_rotation", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_schedule_rotation",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: ScheduleRotations
@mcp.tool()
async def delete_schedule_rotation(id_: str = Field(..., alias="id", description="The unique identifier of the schedule rotation to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a schedule rotation by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteScheduleRotationRequest(
            path=_models.DeleteScheduleRotationRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_schedule_rotation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedule_rotations/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedule_rotations/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_schedule_rotation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_schedule_rotation", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_schedule_rotation",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Schedules
@mcp.tool()
async def list_schedules(
    include: str | None = Field(None, description="Comma-separated list of related fields to include in the response, such as associated resources or metadata."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve when paginating through results, starting from page 1."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of schedules to return per page. Adjust this value to control the size of each paginated response."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of schedules. Use pagination parameters to control the number of results and navigate through pages."""

    # Construct request model with validation
    try:
        _request = _models.ListSchedulesRequest(
            query=_models.ListSchedulesRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_schedules: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/schedules"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_schedules")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_schedules", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_schedules",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Schedules
@mcp.tool()
async def create_schedule(
    type_: Literal["schedules"] = Field(..., alias="type", description="Resource type identifier; must be set to 'schedules' to indicate this is a schedule resource."),
    name: str = Field(..., description="The display name for the schedule; used to identify the schedule in the system."),
    description: str | None = Field(None, description="Optional details about the schedule's purpose, scope, or other contextual information."),
    all_time_coverage: bool | None = Field(None, description="When enabled, indicates the schedule provides continuous 24/7 coverage; when disabled, coverage is limited to specified time periods."),
    owner_group_ids: list[str] | None = Field(None, description="List of team IDs that will own and manage this schedule; teams can have shared ownership of a single schedule."),
    owner_user_id: int | None = Field(None, description="The numeric ID of the user who owns this schedule; takes precedence over team ownership if both are specified."),
) -> dict[str, Any] | ToolResult:
    """Creates a new schedule with specified coverage settings and ownership. Use this to set up on-call schedules with optional 24/7 coverage and team or user ownership."""

    # Construct request model with validation
    try:
        _request = _models.CreateScheduleRequest(
            body=_models.CreateScheduleRequestBody(data=_models.CreateScheduleRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateScheduleRequestBodyDataAttributes(name=name, description=description, all_time_coverage=all_time_coverage, owner_group_ids=owner_group_ids, owner_user_id=owner_user_id)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_schedule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/schedules"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

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
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Schedules
@mcp.tool()
async def get_schedule(id_: str = Field(..., alias="id", description="The unique identifier of the schedule to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific schedule by its unique identifier. Use this operation to fetch detailed information about a schedule."""

    # Construct request model with validation
    try:
        _request = _models.GetScheduleRequest(
            path=_models.GetScheduleRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_schedule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedules/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedules/{id}"
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

# Tags: Schedules
@mcp.tool()
async def update_schedule(
    id_: str = Field(..., alias="id", description="The unique identifier of the schedule to update."),
    type_: Literal["schedules"] = Field(..., alias="type", description="The resource type identifier; must be set to 'schedules' to specify this operation targets schedule resources."),
    name: str | None = Field(None, description="The display name for the schedule."),
    description: str | None = Field(None, description="A detailed description of the schedule's purpose and scope."),
    all_time_coverage: bool | None = Field(None, description="When enabled, indicates the schedule provides continuous 24/7 coverage."),
    owner_group_ids: list[str] | None = Field(None, description="A list of team or group identifiers that own and manage this schedule. Order and format follow the API's standard array serialization."),
    owner_user_id: int | None = Field(None, description="The numeric identifier of the user responsible for owning and administering this schedule."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing schedule with new configuration details such as name, description, coverage settings, and ownership assignments."""

    # Construct request model with validation
    try:
        _request = _models.UpdateScheduleRequest(
            path=_models.UpdateScheduleRequestPath(id_=id_),
            body=_models.UpdateScheduleRequestBody(data=_models.UpdateScheduleRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateScheduleRequestBodyDataAttributes(name=name, description=description, all_time_coverage=all_time_coverage, owner_group_ids=owner_group_ids, owner_user_id=owner_user_id) if any(v is not None for v in [name, description, all_time_coverage, owner_group_ids, owner_user_id]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_schedule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedules/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedules/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_schedule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_schedule", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_schedule",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Schedules
@mcp.tool()
async def delete_schedule(id_: str = Field(..., alias="id", description="The unique identifier of the schedule to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a schedule by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteScheduleRequest(
            path=_models.DeleteScheduleRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_schedule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedules/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedules/{id}"
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

# Tags: Shifts
@mcp.tool()
async def list_schedule_shifts(
    id_: str = Field(..., alias="id", description="The unique identifier of the schedule whose shifts you want to retrieve."),
    to: str | None = Field(None, description="Optional end date for filtering shifts. Shifts on or before this date will be included in the results. Use ISO 8601 format."),
    from_: str | None = Field(None, alias="from", description="Optional start date for filtering shifts. Shifts on or after this date will be included in the results. Use ISO 8601 format."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all shifts for a specific schedule, with optional filtering by date range. Use this to view scheduled shifts within a given time period."""

    # Construct request model with validation
    try:
        _request = _models.GetScheduleShiftsRequest(
            path=_models.GetScheduleShiftsRequestPath(id_=id_),
            query=_models.GetScheduleShiftsRequestQuery(to=to, from_=from_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_schedule_shifts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/schedules/{id}/shifts", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/schedules/{id}/shifts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_schedule_shifts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_schedule_shifts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_schedule_shifts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Secrets
@mcp.tool()
async def get_secret(id_: str = Field(..., alias="id", description="The unique identifier of the secret to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific secret by its unique identifier. Returns the secret details if found and accessible."""

    # Construct request model with validation
    try:
        _request = _models.GetSecretRequest(
            path=_models.GetSecretRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_secret: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/secrets/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/secrets/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_secret")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_secret", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_secret",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Secrets
@mcp.tool()
async def update_secret(
    id_: str = Field(..., alias="id", description="The unique identifier of the secret to update."),
    type_: Literal["secrets"] = Field(..., alias="type", description="The resource type, which must be 'secrets' for this operation."),
    name: str = Field(..., description="The name of the secret. Used to identify and reference the secret."),
    secret: str | None = Field(None, description="The secret value or credential data to store."),
    hashicorp_vault_mount: str | None = Field(None, description="The HashiCorp Vault secret mount path where the secret is stored. Defaults to 'secret' if not specified."),
    hashicorp_vault_path: str | None = Field(None, description="The path within the HashiCorp Vault mount where the secret is located."),
    hashicorp_vault_version: int | None = Field(None, description="The version number of the secret in HashiCorp Vault. Defaults to 0 (latest version) if not specified."),
) -> dict[str, Any] | ToolResult:
    """Update an existing secret by its ID. Modify the secret's name, value, and HashiCorp Vault configuration settings."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSecretRequest(
            path=_models.UpdateSecretRequestPath(id_=id_),
            body=_models.UpdateSecretRequestBody(data=_models.UpdateSecretRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateSecretRequestBodyDataAttributes(name=name, secret=secret, hashicorp_vault_mount=hashicorp_vault_mount, hashicorp_vault_path=hashicorp_vault_path, hashicorp_vault_version=hashicorp_vault_version)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_secret: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/secrets/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/secrets/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_secret")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_secret", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_secret",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Secrets
@mcp.tool()
async def delete_secret(id_: str = Field(..., alias="id", description="The unique identifier of the secret to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a secret by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSecretRequest(
            path=_models.DeleteSecretRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_secret: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/secrets/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/secrets/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_secret")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_secret", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_secret",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Services
@mcp.tool()
async def list_services(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., owners, tags, metadata)."),
    page_number: int | None = Field(None, alias="pagenumber", description="Page number for pagination, starting from 1. Use with page[size] to control result set boundaries."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of services to return per page. Defines the maximum number of results in each paginated response."),
    filter_backstage_id: str | None = Field(None, alias="filterbackstage_id", description="Filter services by their Backstage identifier. Returns only services matching this exact ID."),
    filter_cortex_id: str | None = Field(None, alias="filtercortex_id", description="Filter services by their Cortex identifier. Returns only services matching this exact ID."),
    filter_opslevel_id: str | None = Field(None, alias="filteropslevel_id", description="Filter services by their OpsLevel identifier. Returns only services matching this exact ID."),
    filter_external_id: str | None = Field(None, alias="filterexternal_id", description="Filter services by their external system identifier. Returns only services matching this exact ID."),
    sort: str | None = Field(None, description="Sort results by specified field(s). Use format like 'name' or 'name,-created_at' for ascending/descending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of services with optional filtering by external system identifiers and sorting capabilities."""

    # Construct request model with validation
    try:
        _request = _models.ListServicesRequest(
            query=_models.ListServicesRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_backstage_id=filter_backstage_id, filter_cortex_id=filter_cortex_id, filter_opslevel_id=filter_opslevel_id, filter_external_id=filter_external_id, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_services: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/services"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_services")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_services", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_services",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Services
@mcp.tool()
async def create_service(
    type_: Literal["services"] = Field(..., alias="type", description="The resource type identifier; must be set to 'services'."),
    name: str = Field(..., description="The display name of the service."),
    description: str | None = Field(None, description="Internal description of the service for team reference."),
    public_description: str | None = Field(None, description="Public-facing description of the service visible to external stakeholders."),
    notify_emails: list[str] | None = Field(None, description="Email addresses to receive service notifications; accepts multiple values."),
    color: str | None = Field(None, description="Hex color code for visual identification of the service in dashboards and lists."),
    position: int | None = Field(None, description="Display order of the service in lists and navigation; lower values appear first."),
    show_uptime: bool | None = Field(None, description="Whether to display uptime metrics for this service."),
    show_uptime_last_days: Literal[30, 60, 90] | None = Field(None, description="Time window for uptime calculation; choose from 30, 60, or 90 days (defaults to 60 days)."),
    backstage_id: str | None = Field(None, description="Backstage entity identifier in the format namespace/kind/entity_name for catalog integration."),
    external_id: str | None = Field(None, description="External system identifier for cross-platform service tracking."),
    opsgenie_team_id: str | None = Field(None, description="Opsgenie team identifier for incident management integration."),
    cortex_id: str | None = Field(None, description="Cortex group identifier for service grouping and organization."),
    service_now_ci_sys_id: str | None = Field(None, description="ServiceNow configuration item system ID for ITSM integration."),
    github_repository_name: str | None = Field(None, description="GitHub repository identifier in the format owner/repository_name."),
    github_repository_branch: str | None = Field(None, description="GitHub branch name (e.g., main, develop) for source code tracking."),
    gitlab_repository_name: str | None = Field(None, description="GitLab repository identifier in the format group/project_name."),
    gitlab_repository_branch: str | None = Field(None, description="GitLab branch name (e.g., main, develop) for source code tracking."),
    environment_ids: list[str] | None = Field(None, description="IDs of environments where this service is deployed; accepts multiple values."),
    service_ids: list[str] | None = Field(None, description="IDs of services that depend on this service; accepts multiple values to define service dependencies."),
    owner_group_ids: list[str] | None = Field(None, description="IDs of teams with ownership responsibility for this service; accepts multiple values."),
    owner_user_ids: list[int] | None = Field(None, description="IDs of individual users with ownership responsibility for this service; accepts multiple values."),
    alerts_email_enabled: bool | None = Field(None, description="Enable email notifications for service alerts and incidents."),
    alert_urgency_id: str | None = Field(None, description="Alert urgency level ID that determines notification priority and escalation behavior."),
    slack_channels: list[_models.CreateServiceBodyDataAttributesSlackChannelsItem] | None = Field(None, description="Slack channel identifiers for service notifications; accepts multiple channels."),
    slack_aliases: list[_models.CreateServiceBodyDataAttributesSlackAliasesItem] | None = Field(None, description="Slack aliases or mentions (e.g., @service-team) for automated notifications; accepts multiple values."),
) -> dict[str, Any] | ToolResult:
    """Creates a new service with optional integrations, ownership, and monitoring configuration. Supports linking to external systems like GitHub, GitLab, Backstage, Opsgenie, and ServiceNow."""

    # Construct request model with validation
    try:
        _request = _models.CreateServiceRequest(
            body=_models.CreateServiceRequestBody(data=_models.CreateServiceRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateServiceRequestBodyDataAttributes(name=name, description=description, public_description=public_description, notify_emails=notify_emails, color=color, position=position, show_uptime=show_uptime, show_uptime_last_days=show_uptime_last_days, backstage_id=backstage_id, external_id=external_id, opsgenie_team_id=opsgenie_team_id, cortex_id=cortex_id, service_now_ci_sys_id=service_now_ci_sys_id, github_repository_name=github_repository_name, github_repository_branch=github_repository_branch, gitlab_repository_name=gitlab_repository_name, gitlab_repository_branch=gitlab_repository_branch, environment_ids=environment_ids, service_ids=service_ids, owner_group_ids=owner_group_ids, owner_user_ids=owner_user_ids, alerts_email_enabled=alerts_email_enabled, alert_urgency_id=alert_urgency_id, slack_channels=slack_channels, slack_aliases=slack_aliases)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_service: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/services"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_service")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_service", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_service",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Services
@mcp.tool()
async def get_service(id_: str = Field(..., alias="id", description="The unique identifier of the service to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific service by its unique identifier. Use this operation to fetch detailed information about a single service."""

    # Construct request model with validation
    try:
        _request = _models.GetServiceRequest(
            path=_models.GetServiceRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_service: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/services/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/services/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_service")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_service", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_service",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Services
@mcp.tool()
async def update_service(
    id_: str = Field(..., alias="id", description="The unique identifier of the service to update."),
    type_: Literal["services"] = Field(..., alias="type", description="The resource type, which must be 'services' for this operation."),
    description: str | None = Field(None, description="Internal description of the service for team reference."),
    public_description: str | None = Field(None, description="Public-facing description of the service visible to external stakeholders."),
    notify_emails: list[str] | None = Field(None, description="Email addresses to receive notifications related to this service. Provide as a list of valid email addresses."),
    color: str | None = Field(None, description="Hexadecimal color code for visual identification of the service in dashboards and lists."),
    position: int | None = Field(None, description="Display order of the service in lists and navigation. Lower numbers appear first."),
    backstage_id: str | None = Field(None, description="Backstage entity reference for integration with Backstage catalog. Format: namespace/kind/entity_name."),
    external_id: str | None = Field(None, description="External identifier for tracking this service in third-party systems or internal databases."),
    cortex_id: str | None = Field(None, description="Cortex group identifier to associate this service with a Cortex group for metrics and insights."),
    service_now_ci_sys_id: str | None = Field(None, description="ServiceNow Configuration Item system ID for ITSM integration and change tracking."),
    github_repository_name: str | None = Field(None, description="GitHub repository identifier for source code integration. Format: owner/repository_name."),
    github_repository_branch: str | None = Field(None, description="Default branch in the GitHub repository to track for deployments and changes. Example: main or develop."),
    gitlab_repository_name: str | None = Field(None, description="GitLab repository identifier for source code integration. Format: group/project_name."),
    gitlab_repository_branch: str | None = Field(None, description="Default branch in the GitLab repository to track for deployments and changes. Example: main or develop."),
    environment_ids: list[str] | None = Field(None, description="List of environment IDs where this service is deployed or operates."),
    service_ids: list[str] | None = Field(None, description="List of service IDs that depend on this service, establishing service dependency relationships."),
    owner_group_ids: list[str] | None = Field(None, description="List of team/group IDs that own and are responsible for this service."),
    owner_user_ids: list[int] | None = Field(None, description="List of user IDs designated as owners responsible for this service."),
    alerts_email_enabled: bool | None = Field(None, description="Enable or disable email notifications for alerts and incidents related to this service."),
    alert_urgency_id: str | None = Field(None, description="Alert urgency level ID that determines the severity classification and routing of alerts for this service."),
    slack_channels: list[_models.UpdateServiceBodyDataAttributesSlackChannelsItem] | None = Field(None, description="List of Slack channel identifiers to receive notifications and alerts for this service."),
    slack_aliases: list[_models.UpdateServiceBodyDataAttributesSlackAliasesItem] | None = Field(None, description="List of Slack aliases or handles to mention when sending notifications about this service."),
) -> dict[str, Any] | ToolResult:
    """Update an existing service with new metadata, integrations, ownership, and notification settings. Modify service details such as description, color, position, external system associations, and linked resources."""

    # Construct request model with validation
    try:
        _request = _models.UpdateServiceRequest(
            path=_models.UpdateServiceRequestPath(id_=id_),
            body=_models.UpdateServiceRequestBody(data=_models.UpdateServiceRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateServiceRequestBodyDataAttributes(description=description, public_description=public_description, notify_emails=notify_emails, color=color, position=position, backstage_id=backstage_id, external_id=external_id, cortex_id=cortex_id, service_now_ci_sys_id=service_now_ci_sys_id, github_repository_name=github_repository_name, github_repository_branch=github_repository_branch, gitlab_repository_name=gitlab_repository_name, gitlab_repository_branch=gitlab_repository_branch, environment_ids=environment_ids, service_ids=service_ids, owner_group_ids=owner_group_ids, owner_user_ids=owner_user_ids, alerts_email_enabled=alerts_email_enabled, alert_urgency_id=alert_urgency_id, slack_channels=slack_channels, slack_aliases=slack_aliases) if any(v is not None for v in [description, public_description, notify_emails, color, position, backstage_id, external_id, cortex_id, service_now_ci_sys_id, github_repository_name, github_repository_branch, gitlab_repository_name, gitlab_repository_branch, environment_ids, service_ids, owner_group_ids, owner_user_ids, alerts_email_enabled, alert_urgency_id, slack_channels, slack_aliases]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_service: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/services/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/services/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_service")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_service", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_service",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Services
@mcp.tool()
async def delete_service(id_: str = Field(..., alias="id", description="The unique identifier of the service to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a service by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteServiceRequest(
            path=_models.DeleteServiceRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_service: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/services/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/services/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_service")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_service", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_service",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Services
@mcp.tool()
async def get_service_incidents_chart(
    id_: str = Field(..., alias="id", description="The unique identifier of the service for which to retrieve incident chart data."),
    period: str = Field(..., description="The time period for the incident chart data (e.g., last 7 days, last 30 days, or a specific date range). Specify the period in the format expected by the API."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a chart visualization of incidents for a specific service over a defined time period. This helps track incident trends and patterns for the service."""

    # Construct request model with validation
    try:
        _request = _models.GetServiceIncidentsChartRequest(
            path=_models.GetServiceIncidentsChartRequestPath(id_=id_),
            query=_models.GetServiceIncidentsChartRequestQuery(period=period)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_service_incidents_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/services/{id}/incidents_chart", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/services/{id}/incidents_chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_service_incidents_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_service_incidents_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_service_incidents_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Services
@mcp.tool()
async def get_service_uptime_chart(
    id_: str = Field(..., alias="id", description="The unique identifier of the service for which to retrieve the uptime chart."),
    period: str | None = Field(None, description="The time period to display in the chart (e.g., last 7 days, 30 days, or 90 days). If not specified, a default period will be used."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a visual uptime chart for a specific service, showing availability metrics over a selected time period."""

    # Construct request model with validation
    try:
        _request = _models.GetServiceUptimeChartRequest(
            path=_models.GetServiceUptimeChartRequestPath(id_=id_),
            query=_models.GetServiceUptimeChartRequestQuery(period=period)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_service_uptime_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/services/{id}/uptime_chart", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/services/{id}/uptime_chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_service_uptime_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_service_uptime_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_service_uptime_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Severities
@mcp.tool()
async def list_severities(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., metadata, counts). Specify which associations should be expanded in the result."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve for pagination, starting from 1. Use with page[size] to control result set boundaries."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of results per page. Defines how many severity records are returned in each paginated response."),
    filter_color: str | None = Field(None, alias="filtercolor", description="Filter results by severity color value. Narrows the list to severities matching the specified color."),
    sort: str | None = Field(None, description="Comma-separated list of fields to sort by, with optional direction indicators (e.g., 'name,-created_at'). Controls the order of returned results."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of severity levels, with optional filtering by color and custom sorting capabilities."""

    # Construct request model with validation
    try:
        _request = _models.ListSeveritiesRequest(
            query=_models.ListSeveritiesRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_color=filter_color, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_severities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/severities"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_severities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_severities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_severities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Severities
@mcp.tool()
async def create_severity(
    type_: Literal["severities"] = Field(..., alias="type", description="Resource type identifier; must be set to 'severities' to indicate this is a severity resource."),
    name: str = Field(..., description="The display name for this severity level (e.g., 'Critical', 'High Priority')."),
    description: str | None = Field(None, description="A detailed explanation of when this severity level should be used and its implications."),
    severity: Literal["critical", "high", "medium", "low"] | None = Field(None, description="The severity tier classification. Choose from: critical (highest priority), high, medium, or low (lowest priority)."),
    color: str | None = Field(None, description="A hexadecimal color code (e.g., #FF0000) used to visually represent this severity in the UI."),
    position: int | None = Field(None, description="The display order of this severity relative to others; lower numbers appear first in lists and hierarchies."),
    notify_emails: list[str] | None = Field(None, description="Email addresses that should receive notifications when incidents of this severity are created or escalated. Provide as an array of valid email addresses."),
    slack_channels: list[_models.CreateSeverityBodyDataAttributesSlackChannelsItem] | None = Field(None, description="Slack channel identifiers or names to automatically post incident notifications. Provide as an array of channel references."),
    slack_aliases: list[_models.CreateSeverityBodyDataAttributesSlackAliasesItem] | None = Field(None, description="Slack user aliases or group handles to mention in severity-related notifications. Provide as an array of alias strings."),
) -> dict[str, Any] | ToolResult:
    """Creates a new severity level for categorizing and routing incidents. Severities can be configured with notification channels, visual indicators, and organizational metadata."""

    # Construct request model with validation
    try:
        _request = _models.CreateSeverityRequest(
            body=_models.CreateSeverityRequestBody(data=_models.CreateSeverityRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateSeverityRequestBodyDataAttributes(name=name, description=description, severity=severity, color=color, position=position, notify_emails=notify_emails, slack_channels=slack_channels, slack_aliases=slack_aliases)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_severity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/severities"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_severity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_severity", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_severity",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Severities
@mcp.tool()
async def get_severity(id_: str = Field(..., alias="id", description="The unique identifier of the severity to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific severity record by its unique identifier. Use this to fetch detailed information about a severity level."""

    # Construct request model with validation
    try:
        _request = _models.GetSeverityRequest(
            path=_models.GetSeverityRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_severity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/severities/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/severities/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_severity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_severity", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_severity",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Severities
@mcp.tool()
async def update_severity(
    id_: str = Field(..., alias="id", description="The unique identifier of the severity to update."),
    type_: Literal["severities"] = Field(..., alias="type", description="The resource type identifier; must be set to 'severities' to specify this is a severity resource."),
    description: str | None = Field(None, description="A descriptive label or explanation for this severity level."),
    severity: Literal["critical", "high", "medium", "low"] | None = Field(None, description="The severity level classification; must be one of: critical, high, medium, or low."),
    color: str | None = Field(None, description="A hexadecimal color code used to visually represent this severity in the UI."),
    position: int | None = Field(None, description="The display order of this severity relative to others; lower numbers appear first."),
    notify_emails: list[str] | None = Field(None, description="A list of email addresses that should receive notifications when incidents of this severity are triggered."),
    slack_channels: list[_models.UpdateSeverityBodyDataAttributesSlackChannelsItem] | None = Field(None, description="A list of Slack channel identifiers or names where notifications for this severity should be posted."),
    slack_aliases: list[_models.UpdateSeverityBodyDataAttributesSlackAliasesItem] | None = Field(None, description="A list of Slack user aliases or group handles that should be notified when incidents of this severity occur."),
) -> dict[str, Any] | ToolResult:
    """Update an existing severity configuration by ID, allowing modification of its description, level, visual appearance, notification settings, and associated communication channels."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSeverityRequest(
            path=_models.UpdateSeverityRequestPath(id_=id_),
            body=_models.UpdateSeverityRequestBody(data=_models.UpdateSeverityRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateSeverityRequestBodyDataAttributes(description=description, severity=severity, color=color, position=position, notify_emails=notify_emails, slack_channels=slack_channels, slack_aliases=slack_aliases) if any(v is not None for v in [description, severity, color, position, notify_emails, slack_channels, slack_aliases]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_severity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/severities/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/severities/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_severity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_severity", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_severity",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Severities
@mcp.tool()
async def delete_severity(id_: str = Field(..., alias="id", description="The unique identifier of the severity to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a severity by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSeverityRequest(
            path=_models.DeleteSeverityRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_severity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/severities/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/severities/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_severity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_severity", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_severity",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Shifts
@mcp.tool()
async def list_shifts(
    include: Literal["shift_override", "user"] | None = Field(None, description="Comma-separated list of related resources to include in the response. Valid options are shift_override (to include override details) and user (to include user information)."),
    to: str | None = Field(None, description="End of the time range for filtering shifts. Use ISO 8601 format for the date/time value."),
    from_: str | None = Field(None, alias="from", description="Start of the time range for filtering shifts. Use ISO 8601 format for the date/time value."),
    user_ids: list[int] | None = Field(None, description="Array of user IDs to filter shifts by specific users. Only shifts assigned to these users will be returned."),
    schedule_ids: list[str] | None = Field(None, description="Array of schedule IDs to filter shifts by specific schedules. Only shifts belonging to these schedules will be returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of shifts, optionally filtered by users or schedules and within a specified time range. Supports including related data such as shift overrides and user information."""

    # Construct request model with validation
    try:
        _request = _models.ListShiftsRequest(
            query=_models.ListShiftsRequestQuery(include=include, to=to, from_=from_, user_ids=user_ids, schedule_ids=schedule_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_shifts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/shifts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_shifts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_shifts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_shifts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: StatusPageTemplates
@mcp.tool()
async def list_status_page_templates(
    status_page_id: str = Field(..., description="The unique identifier of the status page for which to list templates."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., components, incidents). Reduces the need for additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of templates to return per page. Adjust to balance response size and number of requests needed."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of templates available for a specific status page. Templates define the layout and structure for status page content."""

    # Construct request model with validation
    try:
        _request = _models.ListStatusPageTemplatesRequest(
            path=_models.ListStatusPageTemplatesRequestPath(status_page_id=status_page_id),
            query=_models.ListStatusPageTemplatesRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_status_page_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/status-pages/{status_page_id}/templates", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/status-pages/{status_page_id}/templates"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_status_page_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_status_page_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_status_page_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: StatusPageTemplates
@mcp.tool()
async def get_status_page_template(id_: str = Field(..., alias="id", description="The unique identifier of the status page template to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific status page template by its unique identifier. Use this to fetch the full details and configuration of a template for viewing or further operations."""

    # Construct request model with validation
    try:
        _request = _models.GetStatusPageTemplateRequest(
            path=_models.GetStatusPageTemplateRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_status_page_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/templates/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/templates/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_status_page_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_status_page_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_status_page_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: StatusPageTemplates
@mcp.tool()
async def delete_status_page_template(id_: str = Field(..., alias="id", description="The unique identifier of the status page template to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a specific status page template by its unique identifier. This operation permanently removes the template and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteStatusPageTemplateRequest(
            path=_models.DeleteStatusPageTemplateRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_status_page_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/templates/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/templates/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_status_page_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_status_page_template", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_status_page_template",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: StatusPages
@mcp.tool()
async def list_status_pages(
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., components, incidents). Reduces the need for additional API calls."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve for pagination, starting from 1. Use with page[size] to navigate through results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of status pages to return per page. Adjust to control result set size for pagination."),
    sort: str | None = Field(None, description="Sort the results by a specified field and direction (e.g., name, created_at). Use ascending or descending order to organize the list."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of status pages. Use pagination parameters to control the number of results and navigate through pages."""

    # Construct request model with validation
    try:
        _request = _models.ListStatusPagesRequest(
            query=_models.ListStatusPagesRequestQuery(include=include, page_number=page_number, page_size=page_size, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_status_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/status-pages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_status_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_status_pages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_status_pages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: StatusPages
@mcp.tool()
async def create_status_page(
    type_: Literal["status_pages"] = Field(..., alias="type", description="The resource type identifier; must be set to 'status_pages'."),
    title: str = Field(..., description="The internal title of the status page used for identification and management."),
    public_title: str | None = Field(None, description="The title displayed to public visitors on the status page."),
    description: str | None = Field(None, description="Internal description for reference and documentation purposes."),
    public_description: str | None = Field(None, description="Description visible to public visitors on the status page."),
    header_color: str | None = Field(None, description="Hex color code for the page header (e.g., '#0061F2')."),
    footer_color: str | None = Field(None, description="Hex color code for the page footer (e.g., '#1F2F41')."),
    allow_search_engine_index: bool | None = Field(None, description="When enabled, allows search engines to index and include your public status page in search results."),
    show_uptime: bool | None = Field(None, description="When enabled, displays uptime statistics on the status page."),
    show_uptime_last_days: Literal[30, 60, 90] | None = Field(None, description="The time period over which uptime is calculated and displayed; choose from 30, 60, or 90 days."),
    success_message: str | None = Field(None, description="Custom message displayed when all monitored components are operational."),
    failure_message: str | None = Field(None, description="Custom message displayed when one or more monitored components are experiencing issues."),
    authentication_enabled: bool | None = Field(None, description="When enabled, requires a password to access the status page; defaults to disabled."),
    authentication_password: str | None = Field(None, description="Password required for accessing the status page when authentication is enabled."),
    website_url: str | None = Field(None, description="URL to your organization's website, displayed as a link on the status page."),
    website_privacy_url: str | None = Field(None, description="URL to your organization's privacy policy, displayed as a link on the status page."),
    website_support_url: str | None = Field(None, description="URL to your organization's support or help center, displayed as a link on the status page."),
    ga_tracking_id: str | None = Field(None, description="Google Analytics tracking ID for monitoring visitor analytics on the status page."),
    time_zone: str | None = Field(None, description="IANA time zone name for displaying incident times and uptime calculations; defaults to 'Etc/UTC'."),
    public: bool | None = Field(None, description="When enabled, makes the status page publicly accessible; when disabled, restricts access."),
    service_ids: list[str] | None = Field(None, description="Array of service IDs to attach and monitor on this status page."),
    functionality_ids: list[str] | None = Field(None, description="Array of functionality IDs to attach and display on this status page."),
    enabled: bool | None = Field(None, description="When enabled, the status page is active and operational; when disabled, the page is inactive."),
) -> dict[str, Any] | ToolResult:
    """Creates a new status page with customizable branding, authentication, and component tracking. Configure visibility settings, messaging, and integrations to monitor service status."""

    # Construct request model with validation
    try:
        _request = _models.CreateStatusPageRequest(
            body=_models.CreateStatusPageRequestBody(data=_models.CreateStatusPageRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateStatusPageRequestBodyDataAttributes(title=title, public_title=public_title, description=description, public_description=public_description, header_color=header_color, footer_color=footer_color, allow_search_engine_index=allow_search_engine_index, show_uptime=show_uptime, show_uptime_last_days=show_uptime_last_days, success_message=success_message, failure_message=failure_message, authentication_enabled=authentication_enabled, authentication_password=authentication_password, website_url=website_url, website_privacy_url=website_privacy_url, website_support_url=website_support_url, ga_tracking_id=ga_tracking_id, time_zone=time_zone, public=public, service_ids=service_ids, functionality_ids=functionality_ids, enabled=enabled)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_status_page: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/status-pages"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_status_page")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_status_page", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_status_page",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: StatusPages
@mcp.tool()
async def get_status_page(id_: str = Field(..., alias="id", description="The unique identifier of the status page to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific status page by its unique identifier. Use this to fetch detailed information about a status page including its current state and configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetStatusPageRequest(
            path=_models.GetStatusPageRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_status_page: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/status-pages/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/status-pages/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_status_page")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_status_page", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_status_page",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: StatusPages
@mcp.tool()
async def update_status_page(
    id_: str = Field(..., alias="id", description="The unique identifier of the status page to update."),
    type_: Literal["status_pages"] = Field(..., alias="type", description="The resource type identifier; must be set to 'status_pages'."),
    title: str | None = Field(None, description="The internal title of the status page used for administrative purposes."),
    public_title: str | None = Field(None, description="The title displayed to the public on the status page."),
    description: str | None = Field(None, description="Internal description of the status page for administrative reference."),
    public_description: str | None = Field(None, description="Public-facing description displayed on the status page."),
    header_color: str | None = Field(None, description="Hex color code for the page header (e.g., '#0061F2')."),
    footer_color: str | None = Field(None, description="Hex color code for the page footer (e.g., '#1F2F41')."),
    allow_search_engine_index: bool | None = Field(None, description="Whether to allow search engines to index and include this status page in search results."),
    show_uptime: bool | None = Field(None, description="Whether to display uptime statistics on the status page."),
    show_uptime_last_days: Literal[30, 60, 90] | None = Field(None, description="The time period in days for uptime calculation; choose from 30, 60, or 90 days."),
    success_message: str | None = Field(None, description="Custom message displayed when all monitored components are operational."),
    failure_message: str | None = Field(None, description="Custom message displayed when one or more monitored components are experiencing issues."),
    authentication_enabled: bool | None = Field(None, description="Enable password protection for accessing the status page; defaults to disabled."),
    authentication_password: str | None = Field(None, description="Password required to access the status page when authentication is enabled."),
    website_url: str | None = Field(None, description="URL to your organization's main website."),
    website_privacy_url: str | None = Field(None, description="URL to your organization's privacy policy."),
    website_support_url: str | None = Field(None, description="URL to your organization's support or help center."),
    ga_tracking_id: str | None = Field(None, description="Google Analytics tracking ID for monitoring status page traffic and user behavior."),
    time_zone: str | None = Field(None, description="IANA time zone name for displaying timestamps on the status page; defaults to 'Etc/UTC'."),
    public: bool | None = Field(None, description="Make the status page publicly accessible without authentication."),
    service_ids: list[str] | None = Field(None, description="Array of service IDs to attach and display on the status page."),
    functionality_ids: list[str] | None = Field(None, description="Array of functionality IDs to attach and display on the status page."),
    enabled: bool | None = Field(None, description="Enable or disable the status page; disabled pages are not accessible."),
) -> dict[str, Any] | ToolResult:
    """Update an existing status page configuration, including branding, visibility settings, authentication, and attached services or functionalities."""

    # Construct request model with validation
    try:
        _request = _models.UpdateStatusPageRequest(
            path=_models.UpdateStatusPageRequestPath(id_=id_),
            body=_models.UpdateStatusPageRequestBody(data=_models.UpdateStatusPageRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateStatusPageRequestBodyDataAttributes(title=title, public_title=public_title, description=description, public_description=public_description, header_color=header_color, footer_color=footer_color, allow_search_engine_index=allow_search_engine_index, show_uptime=show_uptime, show_uptime_last_days=show_uptime_last_days, success_message=success_message, failure_message=failure_message, authentication_enabled=authentication_enabled, authentication_password=authentication_password, website_url=website_url, website_privacy_url=website_privacy_url, website_support_url=website_support_url, ga_tracking_id=ga_tracking_id, time_zone=time_zone, public=public, service_ids=service_ids, functionality_ids=functionality_ids, enabled=enabled) if any(v is not None for v in [title, public_title, description, public_description, header_color, footer_color, allow_search_engine_index, show_uptime, show_uptime_last_days, success_message, failure_message, authentication_enabled, authentication_password, website_url, website_privacy_url, website_support_url, ga_tracking_id, time_zone, public, service_ids, functionality_ids, enabled]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_status_page: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/status-pages/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/status-pages/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_status_page")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_status_page", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_status_page",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: StatusPages
@mcp.tool()
async def delete_status_page(id_: str = Field(..., alias="id", description="The unique identifier of the status page to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a status page by its unique identifier. This action cannot be undone and will remove the status page and all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteStatusPageRequest(
            path=_models.DeleteStatusPageRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_status_page: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/status-pages/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/status-pages/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_status_page")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_status_page", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_status_page",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def list_teams(
    include: Literal["users"] | None = Field(None, description="Comma-separated list of related resources to include in the response. Use 'users' to include team member information."),
    page_number: int | None = Field(None, alias="pagenumber", description="Page number for pagination (1-indexed). Use with page[size] to retrieve specific result sets."),
    page_size: int | None = Field(None, alias="pagesize", description="Number of teams to return per page. Use with page[number] to control pagination."),
    filter_backstage_id: str | None = Field(None, alias="filterbackstage_id", description="Filter teams by their Backstage identifier."),
    filter_cortex_id: str | None = Field(None, alias="filtercortex_id", description="Filter teams by their Cortex identifier."),
    filter_opslevel_id: str | None = Field(None, alias="filteropslevel_id", description="Filter teams by their OpsLevel identifier."),
    filter_external_id: str | None = Field(None, alias="filterexternal_id", description="Filter teams by their external identifier (used for cross-system references)."),
    filter_color: str | None = Field(None, alias="filtercolor", description="Filter teams by their display color."),
    sort: str | None = Field(None, description="Sort results by a specified field. Consult API documentation for available sort fields and order direction syntax."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of teams with optional filtering by external identifiers and sorting. Optionally include related user data for each team."""

    # Construct request model with validation
    try:
        _request = _models.ListTeamsRequest(
            query=_models.ListTeamsRequestQuery(include=include, page_number=page_number, page_size=page_size, filter_backstage_id=filter_backstage_id, filter_cortex_id=filter_cortex_id, filter_opslevel_id=filter_opslevel_id, filter_external_id=filter_external_id, filter_color=filter_color, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_teams: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/teams"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_teams")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_teams", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_teams",
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
    type_: Literal["groups"] = Field(..., alias="type", description="The type of entity being created; must be 'groups' to indicate this is a team/group resource."),
    name: str = Field(..., description="The display name for the team; used as the primary identifier in the UI."),
    description: str | None = Field(None, description="A detailed description of the team's purpose, scope, or other relevant information."),
    notify_emails: list[str] | None = Field(None, description="Email addresses to associate with the team for notifications and communications; provided as an array of email strings."),
    color: str | None = Field(None, description="A hexadecimal color code (e.g., #FF5733) used to visually represent the team in the UI."),
    position: int | None = Field(None, description="The display order of the team in lists and navigation; lower numbers appear first."),
    backstage_id: str | None = Field(None, description="The Backstage entity reference for this team, formatted as namespace/kind/entity_name to enable integration with Backstage catalogs."),
    external_id: str | None = Field(None, description="An external identifier from your organization's system to link this team with external records or systems."),
    pagerduty_service_id: str | None = Field(None, description="The PagerDuty service ID to associate with this team for incident management and on-call scheduling."),
    opsgenie_team_id: str | None = Field(None, description="The Opsgenie team ID to associate with this team for alert routing and escalation policies."),
    victor_ops_id: str | None = Field(None, description="The VictorOps group ID to associate with this team for incident response and alerting."),
    pagertree_id: str | None = Field(None, description="The PagerTree group ID to associate with this team for incident management and team coordination."),
    cortex_id: str | None = Field(None, description="The Cortex group ID to associate with this team for engineering metrics and insights."),
    service_now_ci_sys_id: str | None = Field(None, description="The ServiceNow Configuration Item (CI) system ID to link this team with IT asset management records."),
    user_ids: list[int] | None = Field(None, description="User IDs of team members to add to this team; provided as an array of user identifiers."),
    admin_ids: list[int] | None = Field(None, description="User IDs of team administrators; these users must also be included in the user_ids array and will have elevated permissions for team management."),
    alerts_email_enabled: bool | None = Field(None, description="Enable or disable email notifications for alerts sent to this team."),
    alert_urgency_id: str | None = Field(None, description="The alert urgency level ID for this team, determining how alerts are prioritized and routed."),
    slack_channels: list[_models.CreateTeamBodyDataAttributesSlackChannelsItem] | None = Field(None, description="Slack channel names or IDs to associate with this team for notifications and integrations; provided as an array."),
    slack_aliases: list[_models.CreateTeamBodyDataAttributesSlackAliasesItem] | None = Field(None, description="Slack aliases or handles to associate with this team for mentions and direct messaging; provided as an array."),
) -> dict[str, Any] | ToolResult:
    """Creates a new team with the specified configuration, including optional integrations with external services like PagerDuty, Opsgenie, Slack, and Backstage. The team can include members and admins, and supports email-based alerts."""

    # Construct request model with validation
    try:
        _request = _models.CreateTeamRequest(
            body=_models.CreateTeamRequestBody(data=_models.CreateTeamRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateTeamRequestBodyDataAttributes(name=name, description=description, notify_emails=notify_emails, color=color, position=position, backstage_id=backstage_id, external_id=external_id, pagerduty_service_id=pagerduty_service_id, opsgenie_team_id=opsgenie_team_id, victor_ops_id=victor_ops_id, pagertree_id=pagertree_id, cortex_id=cortex_id, service_now_ci_sys_id=service_now_ci_sys_id, user_ids=user_ids, admin_ids=admin_ids, alerts_email_enabled=alerts_email_enabled, alert_urgency_id=alert_urgency_id, slack_channels=slack_channels, slack_aliases=slack_aliases)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/teams"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

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
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def get_team(
    id_: str = Field(..., alias="id", description="The unique identifier of the team to retrieve."),
    include: Literal["users"] | None = Field(None, description="Comma-separated list of related resources to include in the response. Supported values: users (to include team members)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific team by its unique identifier. Optionally include related resources such as team members in the response."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamRequest(
            path=_models.GetTeamRequestPath(id_=id_),
            query=_models.GetTeamRequestQuery(include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/teams/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/teams/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def update_team(
    id_: str = Field(..., alias="id", description="The unique identifier of the team to update."),
    type_: Literal["groups"] = Field(..., alias="type", description="The resource type, which must be 'groups' for team operations."),
    description: str | None = Field(None, description="A text description of the team's purpose or scope."),
    notify_emails: list[str] | None = Field(None, description="Email addresses to receive team notifications. Provide as an array of valid email addresses."),
    color: str | None = Field(None, description="The team's display color as a hexadecimal color code (e.g., #FF5733)."),
    position: int | None = Field(None, description="The team's display order in lists and hierarchies. Lower numbers appear first."),
    backstage_id: str | None = Field(None, description="The Backstage catalog entity reference for this team, formatted as namespace/kind/entity_name."),
    external_id: str | None = Field(None, description="An external identifier for this team in third-party systems."),
    pagerduty_service_id: str | None = Field(None, description="The PagerDuty service ID linked to this team for incident management."),
    victor_ops_id: str | None = Field(None, description="The VictorOps group ID linked to this team for on-call management."),
    pagertree_id: str | None = Field(None, description="The PagerTree group ID linked to this team for incident tracking."),
    cortex_id: str | None = Field(None, description="The Cortex group ID linked to this team for engineering metrics."),
    service_now_ci_sys_id: str | None = Field(None, description="The ServiceNow configuration item system ID linked to this team."),
    user_ids: list[int] | None = Field(None, description="Array of user IDs who are members of this team. Order is not significant."),
    admin_ids: list[int] | None = Field(None, description="Array of user IDs with admin privileges for this team. All admin IDs must also be included in the user_ids array."),
    alerts_email_enabled: bool | None = Field(None, description="Enable or disable email notifications for team alerts."),
    alert_urgency_id: str | None = Field(None, description="The alert urgency level ID that determines notification priority for this team."),
    slack_channels: list[_models.UpdateTeamBodyDataAttributesSlackChannelsItem] | None = Field(None, description="Slack channels to associate with this team for notifications and updates. Provide as an array of channel identifiers or names."),
    slack_aliases: list[_models.UpdateTeamBodyDataAttributesSlackAliasesItem] | None = Field(None, description="Slack aliases or mentions associated with this team for easy reference. Provide as an array of alias strings."),
) -> dict[str, Any] | ToolResult:
    """Update team configuration including metadata, integrations, members, and notification settings. Requires team ID and type specification."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTeamRequest(
            path=_models.UpdateTeamRequestPath(id_=id_),
            body=_models.UpdateTeamRequestBody(data=_models.UpdateTeamRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateTeamRequestBodyDataAttributes(description=description, notify_emails=notify_emails, color=color, position=position, backstage_id=backstage_id, external_id=external_id, pagerduty_service_id=pagerduty_service_id, victor_ops_id=victor_ops_id, pagertree_id=pagertree_id, cortex_id=cortex_id, service_now_ci_sys_id=service_now_ci_sys_id, user_ids=user_ids, admin_ids=admin_ids, alerts_email_enabled=alerts_email_enabled, alert_urgency_id=alert_urgency_id, slack_channels=slack_channels, slack_aliases=slack_aliases) if any(v is not None for v in [description, notify_emails, color, position, backstage_id, external_id, pagerduty_service_id, victor_ops_id, pagertree_id, cortex_id, service_now_ci_sys_id, user_ids, admin_ids, alerts_email_enabled, alert_urgency_id, slack_channels, slack_aliases]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/teams/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/teams/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_team", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_team",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Teams
@mcp.tool()
async def delete_team(id_: str = Field(..., alias="id", description="The unique identifier of the team to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a team by its unique identifier. This action cannot be undone and will remove the team and all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTeamRequest(
            path=_models.DeleteTeamRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/teams/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/teams/{id}"
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

# Tags: Teams
@mcp.tool()
async def get_team_incidents_chart(
    id_: str = Field(..., alias="id", description="The unique identifier of the team for which to retrieve incident chart data."),
    period: str = Field(..., description="The time period for which to retrieve incident data. Specify the desired reporting window (e.g., daily, weekly, monthly, or a specific date range)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a chart visualization of incidents for a specific team over a defined time period. This provides aggregated incident data suitable for dashboard and reporting purposes."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamIncidentsChartRequest(
            path=_models.GetTeamIncidentsChartRequestPath(id_=id_),
            query=_models.GetTeamIncidentsChartRequestQuery(period=period)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team_incidents_chart: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/teams/{id}/incidents_chart", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/teams/{id}/incidents_chart"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_team_incidents_chart")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_team_incidents_chart", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_team_incidents_chart",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: UserEmailAddresses
@mcp.tool()
async def list_user_email_addresses(user_id: str = Field(..., description="The unique identifier of the user whose email addresses should be retrieved.")) -> dict[str, Any] | ToolResult:
    """Retrieves all email addresses associated with a specific user account. Returns a collection of email addresses linked to the user's profile."""

    # Construct request model with validation
    try:
        _request = _models.GetUserEmailAddressesRequest(
            path=_models.GetUserEmailAddressesRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_email_addresses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/users/{user_id}/email_addresses", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/users/{user_id}/email_addresses"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_email_addresses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_email_addresses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_email_addresses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: UserEmailAddresses
@mcp.tool()
async def add_email_address_to_user(
    user_id: str = Field(..., description="The unique identifier of the user to whom the email address will be added."),
    type_: Literal["user_email_addresses"] = Field(..., alias="type", description="The type of email address being created. Must be set to 'user_email_addresses' to indicate this is a standard user email address."),
    email: str = Field(..., description="The email address to add to the user account. Must be a valid email format."),
) -> dict[str, Any] | ToolResult:
    """Adds a new email address to a user account. The email address is created as a user email address type and becomes associated with the specified user."""

    # Construct request model with validation
    try:
        _request = _models.CreateUserEmailAddressRequest(
            path=_models.CreateUserEmailAddressRequestPath(user_id=user_id),
            body=_models.CreateUserEmailAddressRequestBody(data=_models.CreateUserEmailAddressRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateUserEmailAddressRequestBodyDataAttributes(email=email)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_email_address_to_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/users/{user_id}/email_addresses", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/users/{user_id}/email_addresses"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_email_address_to_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_email_address_to_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_email_address_to_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: UserEmailAddresses
@mcp.tool()
async def get_email_address(id_: str = Field(..., alias="id", description="The unique identifier of the email address to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific user email address by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.ShowUserEmailAddressRequest(
            path=_models.ShowUserEmailAddressRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_email_address: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/email_addresses/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/email_addresses/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_email_address")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_email_address", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_email_address",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: UserEmailAddresses
@mcp.tool()
async def update_user_email_address(
    id_: str = Field(..., alias="id", description="The unique identifier of the user email address record to update."),
    type_: Literal["user_email_addresses"] = Field(..., alias="type", description="The resource type identifier, which must be 'user_email_addresses' to specify this is a user email address resource."),
    email: str | None = Field(None, description="The new email address value to assign to this record."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing user email address record. Specify the email address ID and provide the new email value to modify."""

    # Construct request model with validation
    try:
        _request = _models.UpdateUserEmailAddressRequest(
            path=_models.UpdateUserEmailAddressRequestPath(id_=id_),
            body=_models.UpdateUserEmailAddressRequestBody(data=_models.UpdateUserEmailAddressRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateUserEmailAddressRequestBodyDataAttributes(email=email) if any(v is not None for v in [email]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user_email_address: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/email_addresses/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/email_addresses/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user_email_address")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user_email_address", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user_email_address",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: UserEmailAddresses
@mcp.tool()
async def delete_email_address(id_: str = Field(..., alias="id", description="The unique identifier of the email address to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a user's email address by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteUserEmailAddressRequest(
            path=_models.DeleteUserEmailAddressRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_email_address: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/email_addresses/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/email_addresses/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_email_address")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_email_address", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_email_address",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: UserNotificationRules
@mcp.tool()
async def get_notification_rule(id_: str = Field(..., alias="id", description="The unique identifier of the notification rule to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves a specific notification rule by its unique identifier. Use this to fetch the configuration and settings for a particular user notification rule."""

    # Construct request model with validation
    try:
        _request = _models.GetUserNotificationRuleRequest(
            path=_models.GetUserNotificationRuleRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_notification_rule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/notification_rules/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/notification_rules/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_notification_rule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_notification_rule", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_notification_rule",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: UserNotificationRules
@mcp.tool()
async def delete_notification_rule(id_: str = Field(..., alias="id", description="The unique identifier of the notification rule to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a specific notification rule by its unique identifier. This operation permanently removes the rule and stops any notifications governed by it."""

    # Construct request model with validation
    try:
        _request = _models.DeleteUserNotificationRuleRequest(
            path=_models.DeleteUserNotificationRuleRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_notification_rule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/notification_rules/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/notification_rules/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_notification_rule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_notification_rule", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_notification_rule",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: UserPhoneNumbers
@mcp.tool()
async def list_user_phone_numbers(user_id: str = Field(..., description="The unique identifier of the user whose phone numbers should be retrieved.")) -> dict[str, Any] | ToolResult:
    """Retrieves all phone numbers associated with a specific user account. Returns a collection of phone number records for the given user."""

    # Construct request model with validation
    try:
        _request = _models.GetUserPhoneNumbersRequest(
            path=_models.GetUserPhoneNumbersRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_phone_numbers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/users/{user_id}/phone_numbers", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/users/{user_id}/phone_numbers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_phone_numbers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_phone_numbers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_phone_numbers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: UserPhoneNumbers
@mcp.tool()
async def add_phone_number_to_user(
    user_id: str = Field(..., description="The unique identifier of the user to whom the phone number will be added."),
    type_: Literal["user_phone_numbers"] = Field(..., alias="type", description="The type of phone number resource being created. Must be set to 'user_phone_numbers'."),
    phone: str = Field(..., description="The phone number in international format (e.g., +1 country code followed by the number)."),
) -> dict[str, Any] | ToolResult:
    """Adds a new phone number to a user's account. The phone number must be provided in international format."""

    # Construct request model with validation
    try:
        _request = _models.CreateUserPhoneNumberRequest(
            path=_models.CreateUserPhoneNumberRequestPath(user_id=user_id),
            body=_models.CreateUserPhoneNumberRequestBody(data=_models.CreateUserPhoneNumberRequestBodyData(
                    type_=type_,
                    attributes=_models.CreateUserPhoneNumberRequestBodyDataAttributes(phone=phone)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_phone_number_to_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/users/{user_id}/phone_numbers", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/users/{user_id}/phone_numbers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_phone_number_to_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_phone_number_to_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_phone_number_to_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: UserPhoneNumbers
@mcp.tool()
async def get_phone_number(id_: str = Field(..., alias="id", description="The unique identifier of the phone number record to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific user phone number by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.ShowUserPhoneNumberRequest(
            path=_models.ShowUserPhoneNumberRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_phone_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/phone_numbers/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/phone_numbers/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_phone_number")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_phone_number", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_phone_number",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: UserPhoneNumbers
@mcp.tool()
async def update_user_phone_number(
    id_: str = Field(..., alias="id", description="The unique identifier of the user phone number record to update."),
    type_: Literal["user_phone_numbers"] = Field(..., alias="type", description="The resource type identifier, which must be 'user_phone_numbers' to specify this is a user phone number resource."),
    phone: str | None = Field(None, description="The new phone number in international format (e.g., +1 country code followed by the number)."),
) -> dict[str, Any] | ToolResult:
    """Updates a user's phone number by ID. The phone number must be provided in international format."""

    # Construct request model with validation
    try:
        _request = _models.UpdateUserPhoneNumberRequest(
            path=_models.UpdateUserPhoneNumberRequestPath(id_=id_),
            body=_models.UpdateUserPhoneNumberRequestBody(data=_models.UpdateUserPhoneNumberRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateUserPhoneNumberRequestBodyDataAttributes(phone=phone) if any(v is not None for v in [phone]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user_phone_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/phone_numbers/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/phone_numbers/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user_phone_number")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user_phone_number", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user_phone_number",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: UserPhoneNumbers
@mcp.tool()
async def delete_user_phone_number(id_: str = Field(..., alias="id", description="The unique identifier of the phone number to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific user phone number by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteUserPhoneNumberRequest(
            path=_models.DeleteUserPhoneNumberRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user_phone_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/phone_numbers/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/phone_numbers/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_user_phone_number")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_user_phone_number", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_user_phone_number",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def list_users(
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination (1-indexed). Use with page[size] to control result offset."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of users to return per page. Use with page[number] to paginate through results."),
    filter_email: str | None = Field(None, alias="filteremail", description="Filter results by user email address. Matches against the email field."),
    sort: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Field(None, description="Sort results by one or more fields in comma-separated format. Prefix field name with hyphen (-) for descending order. Valid fields are created_at and updated_at."),
    include: Literal["email_addresses", "phone_numbers", "devices", "role", "on_call_role"] | None = Field(None, description="Include related resources in the response as comma-separated values. Available relationships are email_addresses, phone_numbers, devices, role, and on_call_role."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of users with optional filtering, sorting, and relationship inclusion. Supports email-based filtering and customizable result ordering."""

    # Construct request model with validation
    try:
        _request = _models.ListUsersRequest(
            query=_models.ListUsersRequestQuery(page_number=page_number, page_size=page_size, filter_email=filter_email, sort=sort, include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/users"
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

# Tags: Users
@mcp.tool()
async def get_current_user() -> dict[str, Any] | ToolResult:
    """Retrieve the profile information for the authenticated user making the request. This endpoint returns details about the current user's account."""

    # Extract parameters for API call
    _http_path = "/v1/users/me"
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

# Tags: Users
@mcp.tool()
async def get_user(
    id_: str = Field(..., alias="id", description="The unique identifier of the user to retrieve."),
    include: Literal["email_addresses", "phone_numbers", "devices", "role", "on_call_role"] | None = Field(None, description="Comma-separated list of related data to include in the response. Valid options are: email_addresses, phone_numbers, devices, role, and on_call_role."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific user by their unique identifier. Optionally include related data such as contact information, devices, and role assignments."""

    # Construct request model with validation
    try:
        _request = _models.GetUserRequest(
            path=_models.GetUserRequestPath(id_=id_),
            query=_models.GetUserRequestQuery(include=include)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/users/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/users/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def update_user(
    id_: str = Field(..., alias="id", description="The unique identifier of the user to update."),
    type_: Literal["users"] = Field(..., alias="type", description="The resource type, which must be 'users' to specify this operation targets user resources."),
    first_name: str | None = Field(None, description="The user's first name."),
    last_name: str | None = Field(None, description="The user's last name."),
    role_id: str | None = Field(None, description="The ID of the role to assign to this user, determining their primary permissions and access level."),
    on_call_role_id: str | None = Field(None, description="The ID of the on-call role to assign to this user, defining their on-call responsibilities and escalation policies."),
) -> dict[str, Any] | ToolResult:
    """Update user details including name and role assignments for a specific user by their ID."""

    # Construct request model with validation
    try:
        _request = _models.UpdateUserRequest(
            path=_models.UpdateUserRequestPath(id_=id_),
            body=_models.UpdateUserRequestBody(data=_models.UpdateUserRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateUserRequestBodyDataAttributes(first_name=first_name, last_name=last_name, role_id=role_id, on_call_role_id=on_call_role_id) if any(v is not None for v in [first_name, last_name, role_id, on_call_role_id]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/users/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/users/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

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
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def delete_user(id_: str = Field(..., alias="id", description="The unique identifier of the user to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a user account by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteUserRequest(
            path=_models.DeleteUserRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/users/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/users/{id}"
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

# Tags: WebhooksDeliveries
@mcp.tool()
async def list_webhook_deliveries(
    endpoint_id: str = Field(..., description="The unique identifier of the webhook endpoint for which to retrieve deliveries."),
    include: str | None = Field(None, description="Comma-separated list of related resources to include in the response (e.g., request details, response data). Specify which additional fields should be populated in the delivery records."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number for pagination, starting from 1. Use this to navigate through multiple pages of results."),
    page_size: int | None = Field(None, alias="pagesize", description="The number of delivery records to return per page. Controls the size of each paginated result set."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of webhook delivery attempts for a specific webhook endpoint, including details about each delivery's status and outcome."""

    # Construct request model with validation
    try:
        _request = _models.ListWebhooksDeliveriesRequest(
            path=_models.ListWebhooksDeliveriesRequestPath(endpoint_id=endpoint_id),
            query=_models.ListWebhooksDeliveriesRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhook_deliveries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/webhooks/endpoints/{endpoint_id}/deliveries", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/webhooks/endpoints/{endpoint_id}/deliveries"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_webhook_deliveries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_webhook_deliveries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_webhook_deliveries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: WebhooksDeliveries
@mcp.tool()
async def retry_webhook_delivery(id_: str = Field(..., alias="id", description="The unique identifier of the webhook delivery to retry.")) -> dict[str, Any] | ToolResult:
    """Retries the delivery of a previously failed webhook event. Use this operation to manually re-attempt sending a webhook that did not reach its destination."""

    # Construct request model with validation
    try:
        _request = _models.DeliverWebhooksDeliveryRequest(
            path=_models.DeliverWebhooksDeliveryRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for retry_webhook_delivery: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/webhooks/deliveries/{id}/deliver", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/webhooks/deliveries/{id}/deliver"
    _http_headers = {}
    # Constant headers (from schemas.patch.json add_constant_headers) — fixed values, not agent-configurable
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("retry_webhook_delivery")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("retry_webhook_delivery", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="retry_webhook_delivery",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: WebhooksDeliveries
@mcp.tool()
async def get_webhook_delivery(id_: str = Field(..., alias="id", description="The unique identifier of the webhook delivery to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific webhook delivery event, including its status, payload, and response data."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhooksDeliveryRequest(
            path=_models.GetWebhooksDeliveryRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook_delivery: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/webhooks/deliveries/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/webhooks/deliveries/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_webhook_delivery")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_webhook_delivery", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_webhook_delivery",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: WebhooksEndpoints
@mcp.tool()
async def list_webhook_endpoints(
    include: str | None = Field(None, description="Comma-separated list of related fields to include in the response for each webhook endpoint, such as event types or configuration details."),
    page_number: int | None = Field(None, alias="pagenumber", description="The page number to retrieve when paginating through results, starting from page 1."),
    page_size: int | None = Field(None, alias="pagesize", description="The maximum number of webhook endpoints to return per page."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of all configured webhook endpoints. Use pagination parameters to control the number of results and navigate through pages."""

    # Construct request model with validation
    try:
        _request = _models.ListWebhooksEndpointsRequest(
            query=_models.ListWebhooksEndpointsRequestQuery(include=include, page_number=page_number, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhook_endpoints: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/webhooks/endpoints"
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

# Tags: WebhooksEndpoints
@mcp.tool()
async def get_webhook_endpoint(id_: str = Field(..., alias="id", description="The unique identifier of the webhook endpoint to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves the configuration and details of a specific webhook endpoint by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetWebhooksEndpointRequest(
            path=_models.GetWebhooksEndpointRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_webhook_endpoint: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/webhooks/endpoints/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/webhooks/endpoints/{id}"
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

# Tags: WebhooksEndpoints
@mcp.tool()
async def update_webhooks_endpoint(
    id_: str = Field(..., alias="id", description="The unique identifier of the webhook endpoint to update."),
    type_: Literal["webhooks_endpoints"] = Field(..., alias="type", description="The resource type identifier, which must be set to 'webhooks_endpoints' to specify this is a webhook endpoint resource."),
    event_types: list[Literal["incident.created", "incident.updated", "incident.in_triage", "incident.mitigated", "incident.resolved", "incident.cancelled", "incident.deleted", "incident.scheduled.created", "incident.scheduled.updated", "incident.scheduled.in_progress", "incident.scheduled.completed", "incident.scheduled.deleted", "incident_post_mortem.created", "incident_post_mortem.updated", "incident_post_mortem.published", "incident_post_mortem.deleted", "incident_status_page_event.created", "incident_status_page_event.updated", "incident_status_page_event.deleted", "incident_event.created", "incident_event.updated", "incident_event.deleted", "alert.created", "pulse.created", "genius_workflow_run.queued", "genius_workflow_run.started", "genius_workflow_run.completed", "genius_workflow_run.failed", "genius_workflow_run.canceled"]] | None = Field(None, description="An array of event type strings that this webhook endpoint should subscribe to. Events not included in this list will not trigger the webhook."),
    enabled: bool | None = Field(None, description="A boolean flag indicating whether this webhook endpoint is active and should receive events. Set to true to enable or false to disable."),
) -> dict[str, Any] | ToolResult:
    """Update the configuration of a specific webhook endpoint, including its event subscriptions and enabled status."""

    # Construct request model with validation
    try:
        _request = _models.UpdateWebhooksEndpointRequest(
            path=_models.UpdateWebhooksEndpointRequestPath(id_=id_),
            body=_models.UpdateWebhooksEndpointRequestBody(data=_models.UpdateWebhooksEndpointRequestBodyData(
                    type_=type_,
                    attributes=_models.UpdateWebhooksEndpointRequestBodyDataAttributes(event_types=event_types, enabled=enabled) if any(v is not None for v in [event_types, enabled]) else None
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_webhooks_endpoint: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/webhooks/endpoints/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/webhooks/endpoints/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "application/vnd.api+json"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_webhooks_endpoint")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_webhooks_endpoint", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_webhooks_endpoint",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/vnd.api+json",
        headers=_http_headers,
    )

    return _response_data

# Tags: WebhooksEndpoints
@mcp.tool()
async def delete_webhook_endpoint(id_: str = Field(..., alias="id", description="The unique identifier of the webhook endpoint to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a webhook endpoint by its unique identifier. This action cannot be undone and will stop all webhook deliveries to this endpoint."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWebhooksEndpointRequest(
            path=_models.DeleteWebhooksEndpointRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_webhook_endpoint: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/webhooks/endpoints/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/webhooks/endpoints/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_webhook_endpoint")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_webhook_endpoint", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_webhook_endpoint",
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
        print("  python rootly_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Rootly MCP Server")

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
    logger.info("Starting Rootly MCP Server")
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

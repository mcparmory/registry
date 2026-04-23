#!/usr/bin/env python3
"""
PDF.co API MCP Server
Generated: 2026-04-23 21:35:49 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://api.pdf.co/v1")
SERVER_NAME = "PDF.co API"
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
    _auth_handlers["ApiKeyAuth"] = _auth.APIKeyAuth(env_var="API_KEY", location="header", param_name="x-api-key")
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

mcp = FastMCP("PDF.co API", middleware=[_JsonCoercionMiddleware()])

# Tags: Extraction
@mcp.tool()
async def extract_invoice_data(
    url: str = Field(..., description="URL of the invoice document to process. Accepts PDF and image formats. Defaults to a sample invoice if not provided."),
    customfield: str | None = Field(None, description="JSON string specifying custom field names to extract beyond standard invoice fields. Use camelCase for field names (e.g., storeNumber, deliveryDate) with multiple fields comma-separated."),
    callback: str | None = Field(None, description="Webhook URL for asynchronous delivery of parsing results. If provided, results will be sent to this endpoint upon completion instead of being returned directly."),
) -> dict[str, Any] | ToolResult:
    """Extract structured data from invoices using advanced AI. Automatically parse invoice content and return key fields regardless of layout or format, with optional support for custom field extraction."""

    # Construct request model with validation
    try:
        _request = _models.PostV1AiInvoiceParserRequest(
            body=_models.PostV1AiInvoiceParserRequestBody(url=url, customfield=customfield, callback=callback)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for extract_invoice_data: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/ai-invoice-parser"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("extract_invoice_data")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("extract_invoice_data", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="extract_invoice_data",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Extraction
@mcp.tool()
async def extract_data_from_pdf_document(
    url: str = Field(..., description="URL of the PDF document to parse. Can be a remote URL or a local file path accessible to the service."),
    template: str | None = Field(None, description="JSON template defining extraction rules, including field patterns (regex-based), table structures with multi-page support, and data type specifications. Defaults to a multi-page table extraction template if not provided."),
    outputformat: Literal["JSON", "YAML", "XML", "CSV"] | None = Field(None, description="Format for the extracted output data. Choose from JSON, YAML, XML, or CSV. Defaults to JSON."),
    generatecsvheaders: bool | None = Field(None, description="When true, includes column headers in CSV output. Only applicable when outputformat is CSV."),
    name: str | None = Field(None, description="Optional filename for the generated output file. If not specified, a default name will be assigned."),
    pages: str | None = Field(None, description="Specifies which pages to process using 0-based indices. Supports individual pages (e.g., 0, 5), ranges (e.g., 3-7), open-ended ranges (e.g., 10-), and reverse indexing (e.g., !0 for last page). Items are comma-separated. If omitted, all pages are processed.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
) -> dict[str, Any] | ToolResult:
    """Extracts structured data from PDF documents using a customizable parser template. Supports extraction from form fields, tables, and multi-page documents with flexible output formatting."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfDocumentparserRequest(
            body=_models.PostV1PdfDocumentparserRequestBody(url=url, template=template, outputformat=outputformat, generatecsvheaders=generatecsvheaders, name=name, pages=pages)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for extract_data_from_pdf_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/documentparser"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("extract_data_from_pdf_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("extract_data_from_pdf_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="extract_data_from_pdf_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Extraction
@mcp.tool()
async def list_document_parser_templates() -> dict[str, Any] | ToolResult:
    """Retrieve all available Document Parser data extraction templates accessible to the current user. Use this to discover template options before configuring document parsing operations."""

    # Extract parameters for API call
    _http_path = "/v1/pdf/documentparser/templates"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_document_parser_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_document_parser_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_document_parser_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Extraction
@mcp.tool()
async def get_document_parser_template(id_: str = Field(..., alias="id", description="The unique identifier of the document parser template to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific document parser template using its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetV1DocumentparserTemplatesIdRequest(
            path=_models.GetV1DocumentparserTemplatesIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_document_parser_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pdf/documentparser/templates/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pdf/documentparser/templates/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_document_parser_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_document_parser_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_document_parser_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Extraction
@mcp.tool()
async def extract_pdf_attachments(url: str = Field(..., description="The URL of the PDF file to extract attachments from. Defaults to a sample PDF file if not provided.")) -> dict[str, Any] | ToolResult:
    """Extracts all attachments embedded in a PDF file from the provided URL. Returns the extracted attachment data for processing or download."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfAttachmentsExtractRequest(
            body=_models.PostV1PdfAttachmentsExtractRequestBody(url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for extract_pdf_attachments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/attachments/extract"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("extract_pdf_attachments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("extract_pdf_attachments", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="extract_pdf_attachments",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Editing
@mcp.tool()
async def add_content_to_pdf(
    url: str = Field(..., description="URL of the source PDF file to edit. Defaults to a sample PDF if not provided."),
    annotations_string: str = Field(..., alias="annotationsString", description="One or more text annotations to add to the PDF. Each annotation is semicolon-delimited with parameters: x-coordinate, y-coordinate, page numbers, text content, font size, font name, font color, optional link URL, transparency setting, width, height, and text alignment."),
    name: str | None = Field(None, description="Name for the output document. Defaults to 'newDocument' if not specified."),
    images_string: str | None = Field(None, alias="imagesString", description="One or more images or PDF objects to overlay on the source PDF. Each item is semicolon-delimited with parameters: x-coordinate, y-coordinate, page numbers, URL to the image or PDF file, optional link to open, width, and height."),
    fields_string: str | None = Field(None, alias="fieldsString", description="Values to populate in fillable PDF form fields. Each entry is semicolon-delimited with parameters: page number, field name, and field value."),
) -> dict[str, Any] | ToolResult:
    """Add or modify content in a PDF document by inserting text annotations, images, other PDFs, and filling form fields. Supports both native PDFs and scanned documents."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfEditAddRequest(
            body=_models.PostV1PdfEditAddRequestBody(url=url, name=name, annotations_string=annotations_string, images_string=images_string, fields_string=fields_string)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_content_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/edit/add"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_content_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_content_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_content_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Editing
@mcp.tool()
async def replace_text_in_pdf(
    url: str = Field(..., description="URL of the PDF file to process. Defaults to a sample agreement template if not specified."),
    searchstrings: list[str] | None = Field(None, description="Array of text strings or patterns to search for in the PDF. Order corresponds to replacestrings array for paired replacements."),
    replacestrings: list[str] | None = Field(None, description="Array of replacement text strings corresponding to each search string. Must have the same length as searchstrings for proper pairing."),
    regex: bool | None = Field(None, description="Enable regular expression matching for search strings. When true, searchstrings are interpreted as regex patterns rather than literal text."),
    casesensitive: bool | None = Field(None, description="Perform case-sensitive text matching. When true, 'Hello' and 'hello' are treated as different strings."),
    replacementlimit: float | None = Field(None, description="Maximum number of replacements to perform per search string. Defaults to 1 replacement per string."),
    pages: str | None = Field(None, description="Comma-separated page indices or ranges to process (0-based indexing). Supports ranges (e.g., 3-7), open-ended ranges (e.g., 10-), and reverse indexing (e.g., !0 for last page). If omitted, all pages are processed.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Output filename for the processed PDF document."),
) -> dict[str, Any] | ToolResult:
    """Search for text patterns in a PDF document and replace them with new text. Supports literal string matching or regular expressions, with options for case sensitivity and replacement limits."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfEditReplaceTextRequest(
            body=_models.PostV1PdfEditReplaceTextRequestBody(url=url, searchstrings=searchstrings, replacestrings=replacestrings, regex=regex, casesensitive=casesensitive, replacementlimit=replacementlimit, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for replace_text_in_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/edit/replace-text"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("replace_text_in_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("replace_text_in_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="replace_text_in_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Editing
@mcp.tool()
async def replace_text_with_image_in_pdf(
    url: str = Field(..., description="URL of the PDF file to modify. Accepts publicly accessible URLs or data URIs."),
    replaceimage: str | None = Field(None, description="Base64-encoded image data (with data URI prefix) to use as the replacement. Supports PNG, JPEG, and other common image formats."),
    regex: bool | None = Field(None, description="Enable regular expression matching for the search string. When true, the search string is interpreted as a regex pattern; when false, performs literal text matching."),
    casesensitive: bool | None = Field(None, description="Perform case-sensitive text matching. When true, 'Text' and 'text' are treated as different; when false, they match regardless of case."),
    replacementlimit: float | None = Field(None, description="Maximum number of replacements to perform per search term. Use 0 to replace all occurrences; any positive integer limits replacements to that count."),
    pages: str | None = Field(None, description="Comma-separated page indices or ranges to process (0-based indexing). Supports ranges (e.g., 3-7), open-ended ranges (e.g., 10-), reverse indexing (e.g., !0 for last page), and individual pages. Omit to process all pages.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Custom filename for the generated output PDF. If not specified, a default name is assigned."),
    searchstring: str | None = Field(None),
) -> dict[str, Any] | ToolResult:
    """Search for specific text in a PDF document and replace it with an image. Supports regex patterns and case-sensitive matching with optional replacement limits and page range targeting."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfEditReplaceTextWithImageRequest(
            body=_models.PostV1PdfEditReplaceTextWithImageRequestBody(url=url, replaceimage=replaceimage, regex=regex, casesensitive=casesensitive, replacementlimit=replacementlimit, pages=pages, name=name, searchstring=searchstring)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for replace_text_with_image_in_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/edit/replace-text-with-image"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("replace_text_with_image_in_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("replace_text_with_image_in_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="replace_text_with_image_in_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Editing
@mcp.tool()
async def delete_text_from_pdf(
    url: str = Field(..., description="URL of the PDF document to process. Defaults to a sample agreement template if not provided."),
    searchstrings: list[str] | None = Field(None, description="Array of text strings to search for and delete from the PDF. Each string is treated as a literal match unless regex mode is enabled. Defaults to common placeholder tokens like [CLIENT-NAME], [CLIENT-COMPANY], etc."),
    regex: bool | None = Field(None, description="Enable regular expression matching for search strings. When true, searchstrings are interpreted as regex patterns instead of literal text."),
    casesensitive: bool | None = Field(None, description="Control case sensitivity for text matching. When true, searches are case-sensitive; when false, matches ignore case differences."),
    replacementlimit: float | None = Field(None, description="Maximum number of times each search string should be deleted per page. Defaults to 2 deletions per page."),
    pages: str | None = Field(None, description="Comma-separated page indices or ranges to process (0-based numbering). Use single numbers (e.g., 0, 5), ranges (e.g., 3-7), or open-ended ranges (e.g., 10-). If omitted, all pages are processed."),
    name: str | None = Field(None, description="Custom file name for the generated output PDF. If not specified, a default name will be assigned."),
) -> dict[str, Any] | ToolResult:
    """Remove specified text strings from a PDF document. Supports literal text matching or regex patterns, with options for case sensitivity and limiting replacements per page."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfEditDeleteTextRequest(
            body=_models.PostV1PdfEditDeleteTextRequestBody(url=url, searchstrings=searchstrings, regex=regex, casesensitive=casesensitive, replacementlimit=replacementlimit, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_text_from_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/edit/delete-text"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_text_from_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_text_from_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_text_from_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_to_csv(
    url: str = Field(..., description="URL of the PDF file to convert. Can be a direct file URL or a cloud storage link. Defaults to a sample PDF if not provided."),
    lang: str | None = Field(None, description="Language code for OCR processing of scanned images. Uses standard language codes (e.g., 'eng' for English). Defaults to English."),
    rect: str | None = Field(None, description="Rectangular region to extract from the PDF, specified as four space-separated values: x-coordinate, y-coordinate, width, and height. Use the PDF Edit Add Helper tool to measure coordinates. Only content within this region will be extracted."),
    unwrap: bool | None = Field(None, description="When enabled, unwraps multi-line text within table cells into single lines. Only applies when line grouping mode is set to 1."),
    linegrouping: Literal["1", "2", "3"] | None = Field(None, description="Controls how text lines are grouped within table cells during extraction. Choose from three modes (1, 2, or 3) to adjust grouping behavior. See documentation for detailed mode descriptions.", pattern="^[123]$"),
    pages: str | None = Field(None, description="Specifies which pages to process using 0-based indices. Supports individual pages (e.g., 0, 5), ranges (e.g., 3-7), open-ended ranges (e.g., 10-), and reverse indexing from the end (!0 for last page). Separate multiple selections with commas. Processes all pages by default.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Output filename for the generated CSV file. Defaults to 'result.csv'."),
) -> dict[str, Any] | ToolResult:
    """Convert PDF documents and scanned images into CSV format, preserving table structure, columns, rows, and layout information. Supports selective page extraction and configurable text grouping strategies."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertToCsvRequest(
            body=_models.PostV1PdfConvertToCsvRequestBody(url=url, lang=lang, rect=rect, unwrap=unwrap, linegrouping=linegrouping, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_csv: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/to/csv"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_csv")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_csv", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_csv",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_to_json(
    url: str = Field(..., description="URL of the PDF file to convert. Accepts publicly accessible URLs pointing to PDF documents or scanned images."),
    lang: str | None = Field(None, description="Language code for OCR processing when extracting text from scanned PDFs, PNGs, and JPGs. Use ISO 639-3 three-letter language codes (e.g., 'eng' for English). Combine multiple languages with a plus sign (e.g., 'eng+deu') to process text in multiple languages simultaneously.", pattern="^[a-z]{3}(\\+[a-z]{3})*$"),
    rect: str | None = Field(None, description="Rectangular region to extract from the PDF, specified as coordinates in the format: x-position, y-position, width, and height. Use the PDF Edit Add Helper tool to determine precise coordinates for targeted extraction."),
    unwrap: bool | None = Field(None, description="When enabled, unwraps multi-line text within table cells into single lines. Only applies when line grouping mode is set to 1."),
    linegrouping: Literal["1", "2", "3"] | None = Field(None, description="Controls how text lines are grouped during extraction. Choose from three modes (1, 2, or 3) to adjust line grouping behavior within table cells. Refer to line grouping options documentation for detailed behavior differences.", pattern="^[123]$"),
    pages: str | None = Field(None, description="Specifies which pages to process using zero-based indices and ranges. Supports individual pages (e.g., '0'), ranges (e.g., '3-7'), open-ended ranges (e.g., '10-'), and reverse indexing from the end (e.g., '!0' for last page). Separate multiple selections with commas. If omitted, all pages are processed.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Custom filename for the generated JSON output file."),
) -> dict[str, Any] | ToolResult:
    """Convert PDF documents and scanned images into structured JSON format, preserving text content, fonts, images, vectors, and formatting information. Supports OCR for scanned documents and flexible page selection."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertToJson2Request(
            body=_models.PostV1PdfConvertToJson2RequestBody(url=url, lang=lang, rect=rect, unwrap=unwrap, linegrouping=linegrouping, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_json: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/to/json2"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_json")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_json", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_json",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_to_json_with_ai(
    url: str = Field(..., description="URL of the PDF, PNG, or JPG file to convert. Accepts publicly accessible URLs or file paths from supported cloud storage."),
    lang: str | None = Field(None, description="OCR language code for extracting text from scanned PDFs and images. Use 3-letter ISO 639-2 language codes (e.g., 'eng' for English). Combine multiple languages with '+' to process bilingual documents (e.g., 'eng+deu' for English and German).", pattern="^[a-z]{3}(\\+[a-z]{3})*$"),
    rect: str | None = Field(None, description="Rectangular region coordinates for targeted extraction. Specify as four space-separated values: x-offset, y-offset, width, and height. Use the PDF Edit Add Helper tool to measure coordinates precisely."),
    unwrap: bool | None = Field(None, description="When enabled with line grouping mode 1, merges multi-line text within table cells into single lines for cleaner output."),
    linegrouping: Literal["1", "2", "3"] | None = Field(None, description="Controls text line grouping strategy during extraction. Mode 1 groups lines tightly, mode 2 uses standard grouping, and mode 3 applies loose grouping. Affects how text is organized in the JSON output.", pattern="^[123]$"),
    pages: str | None = Field(None, description="Specifies which pages to process using 0-based indices. Supports individual pages (e.g., '0,2,5'), ranges (e.g., '3-7'), open-ended ranges (e.g., '10-'), and reverse indexing from the end (e.g., '!0' for last page). Comma-separate multiple selections; whitespace is allowed.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Custom filename for the generated JSON output file."),
) -> dict[str, Any] | ToolResult:
    """Convert PDF documents and scanned images into structured JSON format using AI-powered extraction. Supports OCR for scanned content, coordinate-based region extraction, and configurable text grouping strategies."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertToJsonMetaRequest(
            body=_models.PostV1PdfConvertToJsonMetaRequestBody(url=url, lang=lang, rect=rect, unwrap=unwrap, linegrouping=linegrouping, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_json_with_ai: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/to/json-meta"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_json_with_ai")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_json_with_ai", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_json_with_ai",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_to_text(
    url: str = Field(..., description="URL of the PDF or image file to convert. Accepts PDF, PNG, and JPG formats. Defaults to a sample PDF if not provided."),
    lang: str | None = Field(None, description="Language code for OCR processing when extracting text from scanned PDFs, images, or JPG documents. Use three-letter ISO 639-2 language codes (e.g., 'eng' for English). Combine multiple languages with a plus sign to process text in two languages simultaneously (e.g., 'eng+deu'). Defaults to English.", pattern="^[a-z]{3}(\\+[a-z]{3})*$"),
    rect: str | None = Field(None, description="Rectangular region to extract text from, specified as coordinates in the format: x-offset, y-offset, width, height (all in points). Use the PDF Edit Add Helper tool to measure coordinates. If omitted, processes the entire document."),
    unwrap: bool | None = Field(None, description="When enabled with line grouping mode 1, unwraps multi-line text within table cells into single lines. Defaults to disabled."),
    linegrouping: Literal["1", "2", "3"] | None = Field(None, description="Controls how text lines are grouped during extraction, particularly within table cells. Choose from mode 1, 2, or 3 for different grouping behaviors. See documentation for detailed mode descriptions.", pattern="^[123]$"),
    pages: str | None = Field(None, description="Specifies which pages to process using zero-based indices. Supports individual pages (e.g., '0'), ranges (e.g., '3-7'), open-ended ranges (e.g., '10-'), and reverse indexing from the end (e.g., '!0' for last page). Separate multiple selections with commas. Processes all pages if omitted.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Custom filename for the generated text output file."),
) -> dict[str, Any] | ToolResult:
    """Convert PDF documents and scanned images to text while preserving layout. Uses OCR technology to extract text from both native PDFs and image-based documents."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertToTextRequest(
            body=_models.PostV1PdfConvertToTextRequestBody(url=url, lang=lang, rect=rect, unwrap=unwrap, linegrouping=linegrouping, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/to/text"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_text")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_text", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_text",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_to_text_fast(
    url: str = Field(..., description="URL of the PDF file to convert. Accepts publicly accessible PDF URLs."),
    pages: str | None = Field(None, description="Comma-separated page indices or ranges to extract (0-based indexing). Supports individual pages (e.g., 0, 5), ranges (e.g., 3-7, 10-), and reverse indexing from the end (e.g., !0 for last page, !5-!2 for range from end). Whitespace around separators is allowed. Omit to process all pages.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Custom file name for the generated text output."),
) -> dict[str, Any] | ToolResult:
    """Convert a PDF document to plain text using fast, lightweight processing without AI-powered layout analysis or OCR. Use this for quick conversions when layout preservation and scanned page support are not required."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertToTextSimpleRequest(
            body=_models.PostV1PdfConvertToTextSimpleRequestBody(url=url, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_text_fast: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/to/text-simple"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_text_fast")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_text_fast", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_text_fast",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_to_xls(
    url: str = Field(..., description="URL of the PDF file to convert. Defaults to a sample PDF if not provided."),
    lang: str | None = Field(None, description="Language(s) for OCR processing when extracting text from scanned PDFs, images, or JPG documents. Use ISO 639-3 three-letter language codes, optionally combining two languages with a plus sign (e.g., eng+deu for English and German). Defaults to English.", pattern="^[a-z]{3}(\\+[a-z]{3})*$"),
    rect: str | None = Field(None, description="Rectangular region to extract from the PDF, specified as four space-separated values: x-coordinate, y-coordinate, width, and height. Use the PDF Edit Add Helper tool to determine coordinates."),
    unwrap: bool | None = Field(None, description="When enabled, unwraps multi-line text within table cells into single lines. Only applies when line grouping mode is set to 1."),
    linegrouping: Literal["1", "2", "3"] | None = Field(None, description="Controls how text lines are grouped during extraction from table cells. Choose from three modes (1, 2, or 3) to adjust grouping behavior. See Line Grouping Options for details on each mode.", pattern="^[123]$"),
    pages: str | None = Field(None, description="Specifies which pages to process using zero-based indices or ranges. Use comma-separated values with formats like: single page (0), range (3-7), open-ended range (10-), or reverse indexing (!0 for last page). If omitted, all pages are processed.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Custom file name for the generated Excel output file."),
) -> dict[str, Any] | ToolResult:
    """Convert a PDF document to Excel (.xls) format while preserving layout, fonts, and table structure. Supports OCR for scanned documents and flexible page selection."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertToXlsRequest(
            body=_models.PostV1PdfConvertToXlsRequestBody(url=url, lang=lang, rect=rect, unwrap=unwrap, linegrouping=linegrouping, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_xls: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/to/xls"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_xls")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_xls", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_xls",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_to_xlsx(
    url: str = Field(..., description="URL of the PDF file to convert. Defaults to a sample PDF if not provided."),
    lang: str | None = Field(None, description="Language code for OCR processing of scanned PDFs, images, and JPG documents. Use ISO 639-3 three-letter codes (e.g., 'eng' for English). Combine multiple languages with '+' for simultaneous processing (e.g., 'eng+deu'). Defaults to English.", pattern="^[a-z]{3}(\\+[a-z]{3})*$"),
    rect: str | None = Field(None, description="Rectangular region to extract from the PDF, specified as four space-separated values: x-coordinate, y-coordinate, width, and height. Use the PDF Edit Add Helper tool to determine coordinates. Omit to process the entire document."),
    unwrap: bool | None = Field(None, description="When enabled with line grouping mode 1, unwraps multi-line text within table cells into single lines. Defaults to disabled."),
    linegrouping: Literal["1", "2", "3"] | None = Field(None, description="Controls how text lines are grouped during extraction from table cells. Choose from mode 1, 2, or 3 for different grouping behaviors. See Line Grouping Options for detailed behavior differences.", pattern="^[123]$"),
    pages: str | None = Field(None, description="Specifies which pages to process using zero-based indices. Supports individual pages (e.g., '0'), ranges (e.g., '3-7'), open-ended ranges (e.g., '10-'), and reverse indexing (e.g., '!0' for last page). Separate multiple selections with commas. Omit to process all pages.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Custom filename for the generated Excel output file. If not specified, a default name will be assigned."),
) -> dict[str, Any] | ToolResult:
    """Convert a PDF document to Excel (.xlsx format) while preserving layout, fonts, and table structure. Supports OCR for scanned documents and flexible page selection."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertToXlsxRequest(
            body=_models.PostV1PdfConvertToXlsxRequestBody(url=url, lang=lang, rect=rect, unwrap=unwrap, linegrouping=linegrouping, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_xlsx: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/to/xlsx"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_xlsx")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_xlsx", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_xlsx",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_to_xml(
    url: str = Field(..., description="URL of the PDF file to convert. Accepts publicly accessible PDF URLs; defaults to a sample PDF if not provided."),
    lang: str | None = Field(None, description="OCR language code for text extraction from scanned PDFs, images, and documents. Use ISO 639-3 three-letter language codes (e.g., 'eng' for English). Combine multiple languages with '+' for simultaneous processing (e.g., 'eng+deu'). Defaults to English.", pattern="^[a-z]{3}(\\+[a-z]{3})*$"),
    rect: str | None = Field(None, description="Rectangular region to extract from the PDF, specified as space-separated coordinates: x-offset, y-offset, width, and height. Use the PDF Edit Add Helper tool to determine precise coordinates for targeted extraction."),
    unwrap: bool | None = Field(None, description="When enabled with line grouping mode 1, unwraps multi-line text within table cells into single continuous lines. Defaults to disabled."),
    linegrouping: Literal["1", "2", "3"] | None = Field(None, description="Controls text line grouping behavior during extraction. Mode 1 groups lines within table cells, mode 2 applies alternative grouping, and mode 3 uses a third grouping strategy. See documentation for detailed behavior differences.", pattern="^[123]$"),
    name: str | None = Field(None, description="Custom filename for the generated XML output file. If not specified, a default name is assigned."),
    pages: str | None = Field(None, description="Comma-separated list of pages to process (0-based indexing). Supports individual pages (e.g., '0,2,5'), ranges (e.g., '3-7'), open-ended ranges (e.g., '10-'), and reverse indexing from end (!0 for last page, !5-!2 for range from end). Processes all pages if omitted.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
) -> dict[str, Any] | ToolResult:
    """Convert a PDF document to XML format with detailed extraction of text content, table structures, font information, image references, and precise object positioning data."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertToXmlRequest(
            body=_models.PostV1PdfConvertToXmlRequestBody(url=url, lang=lang, rect=rect, unwrap=unwrap, linegrouping=linegrouping, name=name, pages=pages)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_xml: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/to/xml"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_xml")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_xml", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_xml",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_to_html(
    url: str = Field(..., description="URL of the PDF file to convert. Accepts publicly accessible URLs pointing to PDF documents or scanned images (PNG, JPG)."),
    lang: str | None = Field(None, description="Language code for OCR processing when converting scanned PDFs or image files. Use three-letter ISO 639-2 language codes (e.g., 'eng' for English). Combine multiple languages with '+' to enable simultaneous multi-language OCR (e.g., 'eng+deu' for English and German). Defaults to English.", pattern="^[a-z]{3}(\\+[a-z]{3})*$"),
    rect: str | None = Field(None, description="Rectangular region to extract, specified as four space-separated coordinates: x, y, width, and height. Use the PDF Edit Add Helper tool to measure coordinates. Only content within this region will be converted."),
    pages: str | None = Field(None, description="Page selection using zero-based indices and ranges. Specify individual pages (e.g., '0,2,5'), ranges (e.g., '3-7'), open-ended ranges (e.g., '10-'), or reverse indices from the end (e.g., '!0' for last page, '!5-!2' for pages from fifth-to-last to second-to-last). Comma-separate multiple selections. Omit to process all pages.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Custom filename for the generated HTML output file."),
) -> dict[str, Any] | ToolResult:
    """Convert PDF documents and scanned images into HTML format while preserving text, fonts, images, vectors, and formatting. Supports OCR for scanned documents and selective page/region extraction."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertToHtmlRequest(
            body=_models.PostV1PdfConvertToHtmlRequestBody(url=url, lang=lang, rect=rect, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_html: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/to/html"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_html")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_html", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_html",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_to_jpg(
    url: str = Field(..., description="URL of the PDF file to convert. Can be a remote URL or a local file path. Defaults to a sample encrypted PDF for testing."),
    rect: str | None = Field(None, description="Optional rectangular region to extract from each page, specified as four space-separated values: x-coordinate, y-coordinate, width, and height (e.g., '10 20 300 400'). If omitted, the entire page is converted."),
    pages: str | None = Field(None, description="Optional comma-separated list of pages to convert (0-based indexing). Supports individual pages (e.g., '0,2,5'), ranges (e.g., '3-7'), open-ended ranges (e.g., '10-'), and reverse indexing where !0 is the last page (e.g., '!0, !5-!2'). If omitted, all pages are converted.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Output filename for the converted JPEG image. Defaults to 'result.jpg'."),
) -> dict[str, Any] | ToolResult:
    """Convert a PDF document to high-quality JPEG images. Optionally extract specific pages or regions from the PDF."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertToJpgRequest(
            body=_models.PostV1PdfConvertToJpgRequestBody(url=url, rect=rect, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_jpg: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/to/jpg"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_jpg")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_jpg", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_jpg",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_to_png(
    url: str = Field(..., description="URL of the PDF file to convert. Defaults to a sample PDF if not provided."),
    rect: str | None = Field(None, description="Optional rectangular region to extract from the PDF, specified as four space-separated values: x-coordinate, y-coordinate, width, and height (e.g., '10 20 300 400')."),
    pages: str | None = Field(None, description="Optional page selection using 0-based indices and ranges. Specify individual pages (e.g., '0,2,5'), ranges (e.g., '3-7'), open-ended ranges (e.g., '10-'), or reverse indices from the end (e.g., '!0' for last page, '!5-!2' for pages in reverse). Items are comma-separated. If omitted, all pages are processed.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Optional custom file name for the generated PNG output file."),
) -> dict[str, Any] | ToolResult:
    """Convert a PDF document to high-quality PNG images. Optionally extract specific regions or pages from the PDF."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertToPngRequest(
            body=_models.PostV1PdfConvertToPngRequestBody(url=url, rect=rect, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_png: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/to/png"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_png")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_png", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_png",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_to_webp(
    url: str = Field(..., description="URL of the PDF file to convert. Accepts publicly accessible PDF URLs or file paths. Defaults to a sample PDF if not specified."),
    rect: str | None = Field(None, description="Optional rectangular region to extract from the PDF, specified as four space-separated values: x-coordinate, y-coordinate, width, and height. Use this to crop a specific area of interest from the page."),
    pages: str | None = Field(None, description="Optional page selection using 0-based indices. Specify individual pages (e.g., 0, 2, 5), ranges (e.g., 3-7, 10-), or reverse indices from the end (e.g., !0 for last page, !5-!2 for range from fifth-to-last to third-to-last). Separate multiple selections with commas. Defaults to all pages if omitted.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Optional custom file name for the generated WebP output file."),
) -> dict[str, Any] | ToolResult:
    """Convert a PDF document to high-quality WebP image format. Supports selective page extraction and region-based cropping for targeted conversions."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertToWebpRequest(
            body=_models.PostV1PdfConvertToWebpRequestBody(url=url, rect=rect, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_webp: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/to/webp"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_webp")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_webp", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_webp",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_to_tiff(
    url: str = Field(..., description="URL of the PDF file to convert. Defaults to a sample PDF if not provided."),
    rect: str | None = Field(None, description="Rectangular region to extract from the PDF, specified as four space-separated coordinates: x y width height. Use the PDF Edit Add Helper tool to measure and obtain precise coordinates for your target region."),
    unwrap: bool | None = Field(None, description="When enabled with lineGrouping, unwraps text lines within table cells into single lines for cleaner extraction."),
    pages: str | None = Field(None, description="Comma-separated list of pages to convert (0-based indexing). Supports individual pages (e.g., 0, 5), ranges (e.g., 3-7, 10-), and reverse indexing from the end (e.g., !0 for last page, !5-!2 for range from fifth-to-last to third-to-last). Whitespace is allowed. Defaults to all pages if not specified.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Custom file name for the generated TIFF output file."),
) -> dict[str, Any] | ToolResult:
    """Convert a PDF document to high-quality TIFF image format. Optionally extract specific regions, select page ranges, and customize output file naming."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertToTiffRequest(
            body=_models.PostV1PdfConvertToTiffRequestBody(url=url, rect=rect, unwrap=unwrap, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_tiff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/to/tiff"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_tiff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_tiff", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_tiff",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_from_doc(
    url: str = Field(..., description="URL of the source document file to convert. Must point to a valid DOC, DOCX, RTF, TXT, or XPS file accessible via HTTP(S)."),
    name: str | None = Field(None, description="Optional filename for the output PDF file. Defaults to 'result.pdf' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Convert document files (DOC, DOCX, RTF, TXT, XPS) to PDF format. Accepts a URL pointing to the source document and returns the converted PDF."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertFromDocRequest(
            body=_models.PostV1PdfConvertFromDocRequestBody(url=url, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_from_doc: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/from/doc"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_from_doc")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_from_doc", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_from_doc",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_from_csv(
    url: str = Field(..., description="URL of the CSV, XLS, or XLSX file to convert. Must be a publicly accessible HTTP(S) URL pointing to the spreadsheet file."),
    name: str | None = Field(None, description="Output filename for the generated PDF document. Defaults to 'result.pdf' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Convert CSV, XLS, or XLSX spreadsheet files into PDF format. Accepts a file URL and returns a generated PDF document."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertFromCsvRequest(
            body=_models.PostV1PdfConvertFromCsvRequestBody(url=url, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_from_csv: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/from/csv"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_from_csv")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_from_csv", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_from_csv",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_from_image(
    url: str = Field(..., description="One or more image URLs to convert into PDF, separated by commas. Supported formats are JPG, PNG, and TIFF. Images are processed in the order provided."),
    name: str | None = Field(None, description="Optional custom file name for the generated PDF output file."),
) -> dict[str, Any] | ToolResult:
    """Convert image files (JPG, PNG, TIFF) into PDF format. Accepts one or more image URLs and generates a single PDF document."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertFromImageRequest(
            body=_models.PostV1PdfConvertFromImageRequestBody(url=url, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_from_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/from/image"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_from_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_from_image", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_from_image",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_from_url(
    url: str = Field(..., description="The URL of the webpage to convert to PDF. Defaults to the Wikipedia contact page if not specified."),
    margins: str | None = Field(None, description="Space around the page edges in the PDF output. Specified as a measurement value (e.g., millimeters). Defaults to 5mm."),
    papersize: Literal["Letter", "Legal", "Tabloid", "Ledger", "A0", "A1", "A2", "A3", "A4", "A5", "A6"] | str | None = Field(None, description="The paper size for the PDF document. Defaults to Letter size."),
    orientation: Literal["Portrait", "Landscape"] | None = Field(None, description="The page orientation for the PDF output. Defaults to Portrait orientation."),
    printbackground: bool | None = Field(None, description="Whether to include background colors and images in the PDF. Enabled by default."),
    mediatype: Literal["print", "screen", "none"] | None = Field(None, description="The rendering mode for the conversion. Defaults to print mode for optimal PDF formatting."),
    donotwaitfullload: bool | None = Field(None, description="When true, speeds up conversion by waiting only for minimal page loading instead of full page load completion. Defaults to false for thorough rendering."),
    header: str | None = Field(None, description="Custom HTML content to display at the top of every page in the PDF. Must be valid HTML format."),
    footer: str | None = Field(None, description="Custom HTML content to display at the bottom of every page in the PDF. Must be valid HTML format."),
    name: str | None = Field(None, description="The filename for the generated PDF file output."),
) -> dict[str, Any] | ToolResult:
    """Convert a webpage from a URL into a PDF document. The converter processes all JavaScript triggered during page load, including dynamic content and popups, with no option to disable scripting."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertFromUrlRequest(
            body=_models.PostV1PdfConvertFromUrlRequestBody(url=url, margins=margins, papersize=papersize, orientation=orientation, printbackground=printbackground, mediatype=mediatype, donotwaitfullload=donotwaitfullload, header=header, footer=footer, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_from_url: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/from/url"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_from_url")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_from_url", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_from_url",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_pdf_from_html(
    html: str = Field(..., description="The HTML code to convert to PDF. Can include inline styles, scripts, and other HTML elements."),
    templateid: int = Field(..., description="Template identifier that determines the PDF layout and styling template to apply. Defaults to template 1."),
    margins: str | None = Field(None, description="Page margins specified as top, right, bottom, and left values in pixels. Defaults to 40px top/bottom and 20px left/right."),
    papersize: Literal["Letter", "Legal", "Tabloid", "Ledger", "A0", "A1", "A2", "A3", "A4", "A5", "A6"] | str | None = Field(None, description="Paper size for the output PDF (e.g., Letter, A4, Legal). Defaults to Letter size."),
    orientation: Literal["Portrait", "Landscape"] | None = Field(None, description="Page orientation for the output PDF. Defaults to Portrait; can be set to Landscape for wider layouts."),
    printbackground: bool | None = Field(None, description="Whether to print background colors and images in the PDF. Enabled by default."),
    mediatype: Literal["print", "screen", "none"] | None = Field(None, description="Media type used for rendering, typically 'print' for print-optimized output or 'screen' for screen-optimized output. Defaults to print."),
    donotwaitfullload: bool | None = Field(None, description="When true, speeds up conversion by waiting only for minimal page load instead of full page load completion. Defaults to false for thorough rendering."),
    header: str | None = Field(None, description="Custom HTML content to display in the header of every page. Must be valid HTML format."),
    footer: str | None = Field(None, description="Custom HTML content to display in the footer of every page. Must be valid HTML format."),
    name: str | None = Field(None, description="Output filename for the generated PDF document. Defaults to 'multipagedInvoiceWithQRCode.pdf'."),
) -> dict[str, Any] | ToolResult:
    """Convert HTML content into a PDF document. The converter processes JavaScript triggered during page load and includes dynamic content like popups in the output."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertFromHtmlRequest(
            body=_models.PostV1PdfConvertFromHtmlRequestBody(html=html, templateid=templateid, margins=margins, papersize=papersize, orientation=orientation, printbackground=printbackground, mediatype=mediatype, donotwaitfullload=donotwaitfullload, header=header, footer=footer, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_from_html: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/from/html"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_from_html")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_from_html", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_from_html",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def list_templates_html() -> dict[str, Any] | ToolResult:
    """Retrieve all HTML templates available for the current user. Returns a collection of template resources that can be used for rendering or customization."""

    # Extract parameters for API call
    _http_path = "/v1/templates/html"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_templates_html")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_templates_html", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_templates_html",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def get_html_template(id_: str = Field(..., alias="id", description="The unique identifier of the HTML template to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific HTML template by its unique identifier. Use this operation to fetch the full template content for rendering or editing purposes."""

    # Construct request model with validation
    try:
        _request = _models.GetV1TemplatesHtmlIdRequest(
            path=_models.GetV1TemplatesHtmlIdRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_html_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/templates/html/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/templates/html/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_html_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_html_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_html_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Conversion
@mcp.tool()
async def convert_email_to_pdf(
    url: str = Field(..., description="URL pointing to the email file (.msg or .eml) to convert. Defaults to a sample email file if not specified."),
    margins: str | None = Field(None, description="Custom page margins as space-separated values (top right bottom left). Supports px, mm, cm, or in units. A single value applies to all sides. Overrides default CSS margins."),
    papersize: str | None = Field(None, description="Paper size for the output PDF. Use standard sizes (Letter, Legal, A0–A6, etc.) or specify custom dimensions as width and height with optional units (px, mm, cm, or in)."),
    orientation: Literal["Portrait", "Landscape"] | None = Field(None, description="Page orientation for the output PDF: Portrait for vertical layout or Landscape for horizontal layout. Defaults to Portrait."),
    name: str | None = Field(None, description="Output filename for the generated PDF document. Defaults to 'email-with-attachments' if not specified."),
    header: str | None = Field(None, description="Custom HTML content to display in the header of every page. Provide valid HTML markup."),
    footer: str | None = Field(None, description="Custom HTML content to display in the footer of every page. Provide valid HTML markup."),
) -> dict[str, Any] | ToolResult:
    """Convert email files (.msg or .eml format) to PDF documents, automatically extracting and embedding any attachments as PDF attachments within the output file."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfConvertFromEmailRequest(
            body=_models.PostV1PdfConvertFromEmailRequestBody(url=url, margins=margins, papersize=papersize, orientation=orientation, name=name, header=header, footer=footer)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_email_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/convert/from/email"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_email_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_email_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_email_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Excel Conversion
@mcp.tool()
async def convert_spreadsheet_to_csv(
    url: str = Field(..., description="URL of the Excel file to convert. Must be a publicly accessible URL pointing to a valid xls or xlsx file."),
    worksheetindex: str | None = Field(None, description="Zero-based index of the worksheet to convert (first worksheet is index 1). If not specified, the first worksheet is used by default.", pattern="^\\d+$"),
    name: str | None = Field(None, description="Custom filename for the generated CSV output file. If not provided, a default name will be assigned."),
) -> dict[str, Any] | ToolResult:
    """Converts an Excel file (xls/xlsx format) to CSV format. Optionally specify which worksheet to convert and customize the output filename."""

    # Construct request model with validation
    try:
        _request = _models.PostV1XlsConvertToCsvRequest(
            body=_models.PostV1XlsConvertToCsvRequestBody(url=url, worksheetindex=worksheetindex, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_to_csv: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/xls/convert/to/csv"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_to_csv")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_to_csv", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_to_csv",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Excel Conversion
@mcp.tool()
async def convert_spreadsheet_to_json(
    url: str = Field(..., description="URL of the spreadsheet file to convert. Must be a publicly accessible URL pointing to an xls, xlsx, or csv file."),
    worksheetindex: str | None = Field(None, description="Zero-based index of the worksheet to extract (e.g., 1 for the first sheet, 2 for the second). Only applicable to Excel files with multiple sheets. Omit to use the default sheet.", pattern="^\\d+$"),
    name: str | None = Field(None, description="Custom name for the generated JSON output file. If not provided, a default name will be used."),
) -> dict[str, Any] | ToolResult:
    """Converts Excel (xls/xlsx) or CSV files to JSON format. Supports selecting specific worksheets and customizing output file names."""

    # Construct request model with validation
    try:
        _request = _models.PostV1XlsConvertToJsonRequest(
            body=_models.PostV1XlsConvertToJsonRequestBody(url=url, worksheetindex=worksheetindex, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_to_json: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/xls/convert/to/json"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_to_json")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_to_json", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_to_json",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Excel Conversion
@mcp.tool()
async def convert_spreadsheet_to_html(
    url: str = Field(..., description="URL of the spreadsheet file to convert. Must be a publicly accessible URL pointing to an xls, xlsx, or csv file."),
    worksheetindex: str | None = Field(None, description="Zero-based index of the worksheet to convert when the file contains multiple sheets. Defaults to the first worksheet if not specified.", pattern="^\\d+$"),
    name: str | None = Field(None, description="Custom name for the generated HTML output file. If not provided, a default name will be used."),
) -> dict[str, Any] | ToolResult:
    """Converts Excel (xls/xlsx) or CSV files to HTML format. Supports selecting specific worksheets and customizing the output file name."""

    # Construct request model with validation
    try:
        _request = _models.PostV1XlsConvertToHtmlRequest(
            body=_models.PostV1XlsConvertToHtmlRequestBody(url=url, worksheetindex=worksheetindex, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_to_html: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/xls/convert/to/html"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_to_html")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_to_html", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_to_html",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Excel Conversion
@mcp.tool()
async def convert_spreadsheet_to_text(
    url: str = Field(..., description="URL of the spreadsheet file to convert. Must be a publicly accessible URL pointing to an xls, xlsx, or csv file."),
    worksheetindex: str | None = Field(None, description="Zero-based index of the worksheet to convert (first worksheet is index 1). If not specified, the first worksheet is used by default.", pattern="^\\d+$"),
    name: str | None = Field(None, description="Custom filename for the generated text output file. If not provided, a default name will be assigned."),
) -> dict[str, Any] | ToolResult:
    """Converts Excel spreadsheets (xls, xlsx, or csv files) to plain text format. Optionally specify which worksheet to convert and customize the output filename."""

    # Construct request model with validation
    try:
        _request = _models.PostV1XlsConvertToTxtRequest(
            body=_models.PostV1XlsConvertToTxtRequestBody(url=url, worksheetindex=worksheetindex, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_to_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/xls/convert/to/txt"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_to_text")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_to_text", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_to_text",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Excel Conversion
@mcp.tool()
async def convert_spreadsheet_to_xml(
    url: str = Field(..., description="URL of the spreadsheet file to convert. Must be a publicly accessible URL pointing to an xls, xlsx, or csv file."),
    worksheetindex: str | None = Field(None, description="Zero-based index of the worksheet to convert from multi-sheet workbooks. Use 1 for the first worksheet, 2 for the second, and so on. Only applicable to Excel files with multiple sheets.", pattern="^\\d+$"),
    name: str | None = Field(None, description="Custom name for the generated XML output file. If not specified, a default name will be used."),
) -> dict[str, Any] | ToolResult:
    """Converts Excel (xls/xlsx) or CSV files to XML format. Supports selecting a specific worksheet from multi-sheet workbooks."""

    # Construct request model with validation
    try:
        _request = _models.PostV1XlsConvertToXmlRequest(
            body=_models.PostV1XlsConvertToXmlRequestBody(url=url, worksheetindex=worksheetindex, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_to_xml: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/xls/convert/to/xml"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_to_xml")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_to_xml", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_to_xml",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Excel Conversion
@mcp.tool()
async def convert_spreadsheet_to_pdf(
    url: str = Field(..., description="URL of the spreadsheet file to convert. Accepts XLS, XLSX, or CSV formats."),
    worksheetindex: str | None = Field(None, description="Zero-based index of the worksheet to convert when the file contains multiple sheets. Defaults to the first worksheet if not specified.", pattern="^\\d+$"),
    name: str | None = Field(None, description="Custom filename for the generated PDF output file."),
    autosize: bool | None = Field(None, description="When enabled, automatically adjusts page dimensions to fit the content. When disabled, uses the worksheet's configured page setup settings."),
) -> dict[str, Any] | ToolResult:
    """Converts Excel (XLS/XLSX) or CSV files to PDF format with optional worksheet selection and automatic page sizing."""

    # Construct request model with validation
    try:
        _request = _models.PostV1XlsConvertToPdfRequest(
            body=_models.PostV1XlsConvertToPdfRequestBody(url=url, worksheetindex=worksheetindex, name=name, autosize=autosize)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_spreadsheet_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/xls/convert/to/pdf"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_spreadsheet_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_spreadsheet_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_spreadsheet_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Merging & Splitting
@mcp.tool()
async def merge_pdfs(
    url: str = Field(..., description="One or more URLs pointing to PDF files to merge, separated by commas. URLs must be accessible and point to valid PDF documents. Defaults to sample encrypted PDFs if not specified."),
    name: str | None = Field(None, description="The filename for the resulting merged PDF document. Defaults to 'result.pdf' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Merge multiple PDF files into a single consolidated PDF document. Provide one or more PDF URLs to combine them in the order specified."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfMergeRequest(
            body=_models.PostV1PdfMergeRequestBody(url=url, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for merge_pdfs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/merge"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("merge_pdfs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("merge_pdfs", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="merge_pdfs",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Merging & Splitting
@mcp.tool()
async def merge_documents_to_pdf(
    url: str = Field(..., description="Comma-separated URLs of source files to merge. Supports PDF, DOC, DOCX, XLS, XLSX, RTF, TXT, PNG, JPG, and ZIP files containing documents or images. Multiple files are merged in the order specified."),
    name: str | None = Field(None, description="Optional custom filename for the generated PDF output file."),
) -> dict[str, Any] | ToolResult:
    """Merge multiple documents and images of various formats (PDF, DOC, DOCX, XLS, XLSX, RTF, TXT, PNG, JPG, or ZIP archives) into a single PDF file. This operation supports broader file type compatibility than standard PDF merge but consumes additional credits due to internal format conversions."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfMerge2Request(
            body=_models.PostV1PdfMerge2RequestBody(url=url, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for merge_documents_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/merge2"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("merge_documents_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("merge_documents_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="merge_documents_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Merging & Splitting
@mcp.tool()
async def split_pdf(
    url: str = Field(..., description="URL of the PDF file to split. Accepts any publicly accessible PDF URL; defaults to a sample PDF if not provided."),
    pages: str | None = Field(None, description="Pages to extract from the PDF using 1-based indexing. Specify individual pages (e.g., 1,3,5), ranges (e.g., 1-5), or combinations (e.g., 1-3,5,7-9). Use !1 to reference the last page and !6-!2 for ranges from the end. Omit the end number in a range (e.g., 3-) to include all pages from that point onward.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Filename for the output PDF file. Defaults to 'result.pdf' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Split a PDF document into multiple separate PDF files by specifying which pages to extract using page numbers or ranges."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfSplitRequest(
            body=_models.PostV1PdfSplitRequestBody(url=url, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for split_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/split"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("split_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("split_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="split_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: PDF Merging & Splitting
@mcp.tool()
async def split_pdf_by_text_search(
    url: str = Field(..., description="URL of the PDF file to split. Must be a publicly accessible URL pointing to a valid PDF document."),
    searchstring: str = Field(..., description="Text pattern or barcode format to search for within the PDF. Supports barcode syntax like [[barcode:qrcode,datamatrix /pattern/]] for barcode detection, or plain text strings for text search."),
    regexsearch: bool | None = Field(None, description="Enable regular expression matching for the search string. When enabled, the searchstring is interpreted as a regex pattern rather than literal text."),
    excludekeypages: bool | None = Field(None, description="Exclude pages containing the search match from the output files. When enabled, matching pages are removed; when disabled, they are included in the split results."),
    casesensitive: bool | None = Field(None, description="Perform case-sensitive text matching. When disabled, search is case-insensitive."),
    lang: str | None = Field(None, description="OCR language for extracting text from scanned PDFs, images, and documents. Use ISO 639-3 language codes (e.g., 'eng' for English). Combine multiple languages with '+' for simultaneous processing (e.g., 'eng+deu').", pattern="^[a-z]{3}(\\+[a-z]{3})*$"),
    name: str | None = Field(None, description="Base name for the output PDF files. The system will append sequential numbering to create individual split file names."),
) -> dict[str, Any] | ToolResult:
    """Split a PDF document into multiple files by searching for specific text patterns or barcodes. Pages containing the search term can be used as split points, with options to exclude or include those pages in the output."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfSplit2Request(
            body=_models.PostV1PdfSplit2RequestBody(url=url, searchstring=searchstring, regexsearch=regexsearch, excludekeypages=excludekeypages, casesensitive=casesensitive, lang=lang, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for split_pdf_by_text_search: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/split2"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("split_pdf_by_text_search")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("split_pdf_by_text_search", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="split_pdf_by_text_search",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Forms
@mcp.tool()
async def get_pdf_form_fields(url: str = Field(..., description="The URL of the PDF file to analyze. Must be a publicly accessible URL pointing to a valid PDF document containing form fields.")) -> dict[str, Any] | ToolResult:
    """Extract and retrieve metadata about all fillable form fields within a PDF document. Returns field names, types, and properties for programmatic form processing."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfInfoFieldsRequest(
            body=_models.PostV1PdfInfoFieldsRequestBody(url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pdf_form_fields: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/info/fields"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pdf_form_fields")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pdf_form_fields", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pdf_form_fields",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Find & Search
@mcp.tool()
async def search_pdf_text(
    url: str = Field(..., description="URL of the PDF file to search. Defaults to a sample PDF if not specified."),
    searchstring: str = Field(..., description="Text or pattern to find in the PDF. When regex search is enabled, this accepts regular expression syntax (e.g., date patterns like \\d+/\\d+/\\d+)."),
    regexsearch: bool | None = Field(None, description="Enable regular expression matching for the search string. When true, the search string is interpreted as a regex pattern; when false, performs literal string matching."),
    wordmatchingmode: str | None = Field(None, description="Word matching mode to control how text boundaries are handled during search (e.g., whole words only vs. partial matches)."),
    casesensitive: bool | None = Field(None, description="Control search sensitivity to letter case. Set to false for case-insensitive matching; true for case-sensitive matching."),
    pages: str | None = Field(None, description="Specify which pages to search using 0-based indices. Supports individual pages (e.g., 0, 5), ranges (e.g., 3-7, 10-), and reverse indexing (e.g., !0 for last page). Use comma-separated values for multiple selections. Omit to search all pages.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Name identifier for the output results."),
) -> dict[str, Any] | ToolResult:
    """Search for text patterns in a PDF document and retrieve their precise coordinates. Supports both literal string matching and regular expression patterns for flexible text discovery."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfFindRequest(
            body=_models.PostV1PdfFindRequestBody(url=url, searchstring=searchstring, regexsearch=regexsearch, wordmatchingmode=wordmatchingmode, casesensitive=casesensitive, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_pdf_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/find"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_pdf_text")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_pdf_text", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_pdf_text",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Find & Search
@mcp.tool()
async def search_tables_in_pdf(
    url: str = Field(..., description="URL of the PDF file to analyze. Defaults to a sample PDF if not provided."),
    pages: str | None = Field(None, description="Comma-separated page indices or ranges to scan (0-based indexing). Supports individual pages (e.g., 0, 5), ranges (e.g., 3-7, 10-), and reverse indexing from the end (e.g., !0 for last page, !5-!2 for range from fifth-to-last to third-to-last). Whitespace is allowed. If omitted, all pages are processed.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Optional custom name for the generated output file."),
) -> dict[str, Any] | ToolResult:
    """Scan a PDF document using AI to detect and extract tables, returning their locations, coordinates, and column information for specified pages."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfFindTableRequest(
            body=_models.PostV1PdfFindTableRequestBody(url=url, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_tables_in_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/find/table"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_tables_in_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_tables_in_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_tables_in_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Find & Search
@mcp.tool()
async def make_pdf_searchable(
    url: str = Field(..., description="URL of the PDF or image file to process. Accepts remote URLs pointing to scanned documents or image files that need OCR conversion."),
    lang: str | None = Field(None, description="Language code for OCR processing (e.g., 'eng' for English). Defaults to English if not specified. Use standard ISO 639-3 language codes."),
    pages: str | None = Field(None, description="Comma-separated page indices or ranges to process (0-based indexing). Supports individual pages (e.g., 0, 5), ranges (e.g., 3-7, 10-), and reverse indexing (e.g., !0 for last page). Whitespace is allowed. If omitted, all pages are processed.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Output filename for the resulting searchable PDF. Defaults to 'result.pdf' if not specified."),
    rect: str | None = Field(None, description="Rectangular region coordinates for targeted OCR processing, specified as four space-separated values: x y width height (in points). Use the PDF Edit Add Helper tool to measure coordinates. If omitted, the entire page is processed."),
) -> dict[str, Any] | ToolResult:
    """Convert scanned PDF documents or image files into text-searchable PDFs by running OCR and adding an invisible text layer for search and indexing capabilities."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfMakesearchableRequest(
            body=_models.PostV1PdfMakesearchableRequestBody(url=url, lang=lang, pages=pages, name=name, rect=rect)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for make_pdf_searchable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/makesearchable"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("make_pdf_searchable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("make_pdf_searchable", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="make_pdf_searchable",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Find & Search
@mcp.tool()
async def convert_pdf_to_unsearchable(
    url: str = Field(..., description="URL of the PDF file to convert. Can be a direct file URL or a cloud storage path (e.g., S3 URI)."),
    pages: str | None = Field(None, description="Comma-separated page indices or ranges to process (0-based indexing). Supports individual pages (e.g., 0, 5), ranges (e.g., 3-7, 10-), and reverse indexing from the end (e.g., !0 for last page, !5-!2 for range from fifth-to-last to third-to-last). Whitespace is allowed. If omitted, all pages are processed.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Output filename for the resulting unsearchable PDF document."),
) -> dict[str, Any] | ToolResult:
    """Convert a PDF file into an unsearchable version by rendering it as a flat image, effectively creating a scanned PDF that prevents text extraction."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfMakeunsearchableRequest(
            body=_models.PostV1PdfMakeunsearchableRequestBody(url=url, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_pdf_to_unsearchable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/makeunsearchable"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_pdf_to_unsearchable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_pdf_to_unsearchable", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_pdf_to_unsearchable",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Document, File & System
@mcp.tool()
async def compress_pdf(
    url: str = Field(..., description="URL of the PDF file to compress. Defaults to a sample PDF if not provided."),
    name: str | None = Field(None, description="Optional file name for the compressed output PDF. If not specified, a default name will be generated."),
    config: dict[str, Any] | None = Field(None, description="Compression configuration object controlling image optimization strategies. Allows separate settings for color, grayscale, and monochrome images, including downsampling thresholds (in DPI), compression format selection (JPEG or CCITT G4), and quality parameters. Defaults to balanced compression settings optimized for file size reduction."),
) -> dict[str, Any] | ToolResult:
    """Compress PDF files to reduce their size by optimizing images and content. Supports configurable downsampling, compression formats, and quality settings for color, grayscale, and monochrome images."""

    # Construct request model with validation
    try:
        _request = _models.PostV2PdfCompressRequest(
            body=_models.PostV2PdfCompressRequestBody(url=url, name=name, config=config)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for compress_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/pdf/compress"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("compress_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("compress_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="compress_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Document, File & System
@mcp.tool()
async def get_pdf_info(url: str = Field(..., description="The URL of the PDF document to analyze. Must be a valid, publicly accessible PDF file URL.")) -> dict[str, Any] | ToolResult:
    """Retrieve detailed metadata, properties, and security permissions for a PDF document from a specified URL."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfInfoRequest(
            body=_models.PostV1PdfInfoRequestBody(url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pdf_info: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/info"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pdf_info")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pdf_info", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pdf_info",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Document, File & System
@mcp.tool()
async def get_job_status(
    jobid: str = Field(..., description="The unique identifier of the asynchronous job whose status you want to check. This ID is returned when you initially create a background job."),
    force: bool | None = Field(None, description="When enabled, forces a fresh status check from the server rather than returning a cached result, ensuring you get the most current job state."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the current status of an asynchronous background job that was previously initiated through the PDF.co API. Use this operation to poll and monitor the progress of long-running tasks."""

    # Construct request model with validation
    try:
        _request = _models.PostV1JobCheckRequest(
            body=_models.PostV1JobCheckRequestBody(jobid=jobid, force=force)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_job_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/job/check"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_job_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_job_status", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_job_status",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Document, File & System
@mcp.tool()
async def get_account_credit_balance() -> dict[str, Any] | ToolResult:
    """Retrieve the current credit balance and related account balance information for the authenticated user's account."""

    # Extract parameters for API call
    _http_path = "/v1/account/credit/balance"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_account_credit_balance")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_account_credit_balance", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_account_credit_balance",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Document, File & System
@mcp.tool()
async def classify_document(
    url: str = Field(..., description="URL of the document to classify. Accepts PDF, JPG, or PNG files. Defaults to a sample invoice if not provided."),
    casesensitive: bool | None = Field(None, description="Controls whether the classification search is case-sensitive. Set to false to ignore case differences during analysis; defaults to true for case-sensitive matching."),
) -> dict[str, Any] | ToolResult:
    """Analyzes the content of a PDF, JPG, or PNG document to automatically determine its classification using built-in AI or custom-defined classification rules."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfClassifierRequest(
            body=_models.PostV1PdfClassifierRequestBody(url=url, casesensitive=casesensitive)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for classify_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/classifier"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("classify_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("classify_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="classify_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Document, File & System
@mcp.tool()
async def send_email_with_attachment(
    url: str = Field(..., description="URL of the file to attach to the email. Defaults to a sample PDF from AWS S3."),
    from_: str = Field(..., alias="from", description="Sender email address in the format 'Name <email@domain.com>' or just 'email@domain.com'."),
    to: str = Field(..., description="Primary recipient email address. Use comma-separated values for multiple recipients."),
    subject: str = Field(..., description="Email subject line."),
    smtpserver: str = Field(..., description="SMTP server hostname (e.g., smtp.gmail.com for Gmail, smtp.office365.com for Outlook)."),
    smtpusername: str = Field(..., description="Username or email address for SMTP authentication."),
    smtppassword: str = Field(..., description="Password or app-specific password for SMTP authentication. For Gmail, use an app-specific password rather than your account password."),
    replyto: str | None = Field(None, description="Reply-to email address. If specified, replies will be directed to this address instead of the sender."),
    cc: str | None = Field(None, description="Carbon copy recipient email address. Use comma-separated values for multiple recipients."),
    bcc: str | None = Field(None, description="Blind carbon copy recipient email address. Use comma-separated values for multiple recipients. Recipients in this field are hidden from other recipients."),
    name: str | None = Field(None, description="Custom filename for the attachment. If not specified, the original filename from the URL will be used."),
) -> dict[str, Any] | ToolResult:
    """Send an email message with optional file attachment. Supports multiple recipients and requires SMTP server credentials for delivery."""

    # Construct request model with validation
    try:
        _request = _models.PostV1EmailSendRequest(
            body=_models.PostV1EmailSendRequestBody(url=url, from_=from_, to=to, replyto=replyto, cc=cc, bcc=bcc, subject=subject, smtpserver=smtpserver, smtpusername=smtpusername, smtppassword=smtppassword, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_email_with_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/email/send"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_email_with_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_email_with_attachment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_email_with_attachment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Document, File & System
@mcp.tool()
async def extract_email_components(url: str = Field(..., description="URL pointing to the email file (.eml format) to be decoded. Defaults to a sample email file if not provided.")) -> dict[str, Any] | ToolResult:
    """Decode an email message file to extract and parse its components including headers, body, attachments, and metadata."""

    # Construct request model with validation
    try:
        _request = _models.PostV1EmailDecodeRequest(
            body=_models.PostV1EmailDecodeRequestBody(url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for extract_email_components: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/email/decode"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("extract_email_components")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("extract_email_components", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="extract_email_components",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Document, File & System
@mcp.tool()
async def extract_email_attachments(url: str = Field(..., description="The URL pointing to the EML email file to process. Must be a valid, accessible HTTP(S) URL. Defaults to a sample EML file if not provided.")) -> dict[str, Any] | ToolResult:
    """Extract all attachments from an email message. Provide the URL to an EML file to retrieve and process its attachments."""

    # Construct request model with validation
    try:
        _request = _models.PostV1EmailExtractAttachmentsRequest(
            body=_models.PostV1EmailExtractAttachmentsRequestBody(url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for extract_email_attachments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/email/extract-attachments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("extract_email_attachments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("extract_email_attachments", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="extract_email_attachments",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Document, File & System
@mcp.tool()
async def delete_temporary_file(url: str = Field(..., description="The S3 URL of the temporary file to delete. This should be a full URL path to the file in the temporary storage bucket.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes a temporary file from cloud storage. This operation removes files that were previously uploaded by you or generated by the API."""

    # Construct request model with validation
    try:
        _request = _models.PostV1FileDeleteRequest(
            body=_models.PostV1FileDeleteRequestBody(url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_temporary_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/file/delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_temporary_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_temporary_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_temporary_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Document, File & System
@mcp.tool()
async def upload_file_from_url(
    url: str = Field(..., description="The source URL of the file to download and upload. Must be a valid, accessible HTTP or HTTPS URL."),
    name: str | None = Field(None, description="Optional custom name for the uploaded file. If not provided, the original filename from the source URL will be used."),
) -> dict[str, Any] | ToolResult:
    """Downloads a file from a source URL and uploads it as a temporary file to the system. Temporary files are automatically deleted after 1 hour."""

    # Construct request model with validation
    try:
        _request = _models.GetV1FileUploadUrlRequest(
            query=_models.GetV1FileUploadUrlRequestQuery(url=url, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_file_from_url: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/file/upload/url"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_file_from_url")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_file_from_url", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_file_from_url",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Document, File & System
@mcp.tool()
async def upload_file_from_url_direct(
    url: str = Field(..., description="The remote URL pointing to the file to download and upload. Must be a valid URI format."),
    name: str | None = Field(None, description="Optional custom name for the uploaded file. If not provided, the original filename from the source URL will be used."),
) -> dict[str, Any] | ToolResult:
    """Downloads a file from a remote URL and uploads it as a temporary file to the system. The temporary file will be automatically deleted after 1 hour."""

    # Construct request model with validation
    try:
        _request = _models.PostV1FileUploadUrlRequest(
            body=_models.PostV1FileUploadUrlRequestBody(name=name, url=url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_file_from_url_direct: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/file/upload/url"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_file_from_url_direct")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_file_from_url_direct", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_file_from_url_direct",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Document, File & System
@mcp.tool()
async def create_file_from_base64(
    file_: str = Field(..., alias="file", description="Base64-encoded file content to upload. Must be a valid base64 string representing the file bytes."),
    name: str | None = Field(None, description="Optional name for the generated file. If not provided, a default name will be assigned."),
) -> dict[str, Any] | ToolResult:
    """Creates a temporary file from base64-encoded data that can be used with other API methods. The temporary file is automatically deleted after 1 hour."""

    # Construct request model with validation
    try:
        _request = _models.PostV1FileUploadBase64Request(
            body=_models.PostV1FileUploadBase64RequestBody(name=name, file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_file_from_base64: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/file/upload/base64"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_file_from_base64")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_file_from_base64", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_file_from_base64",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Document, File & System
@mcp.tool()
async def get_file_upload_presigned_url(
    name: str | None = Field(None, description="The name to assign to the uploaded file. Must be provided as a string."),
    contenttype: str | None = Field(None, description="The MIME type of the file being uploaded (e.g., application/pdf, image/png, text/plain)."),
) -> dict[str, Any] | ToolResult:
    """Generate a pre-signed URL for uploading a file. Use the returned URL with a PUT request to upload your file, then access it via the provided link."""

    # Construct request model with validation
    try:
        _request = _models.GetV1FileUploadGetPresignedUrlRequest(
            query=_models.GetV1FileUploadGetPresignedUrlRequestQuery(name=name, contenttype=contenttype)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_upload_presigned_url: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/file/upload/get-presigned-url"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_upload_presigned_url")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_upload_presigned_url", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_upload_presigned_url",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Document, File & System
@mcp.tool()
async def add_password_to_pdf(
    url: str = Field(..., description="URL of the PDF file to secure. Defaults to a sample PDF if not provided."),
    ownerpassword: str | None = Field(None, description="Password required to modify document permissions and security settings. Defaults to '12345' if not specified."),
    userpassword: str | None = Field(None, description="Password required for users to open and view the PDF document. Defaults to '54321' if not specified."),
    allowaccessibilitysupport: bool | None = Field(None, description="Whether to allow screen readers and accessibility tools to access the document content."),
    allowassemblydocument: bool | None = Field(None, description="Whether to allow users to assemble or reorganize pages within the document."),
    allowprintdocument: bool | None = Field(None, description="Whether to allow users to print the document. Disabled by default."),
    allowfillforms: bool | None = Field(None, description="Whether to allow users to fill in form fields within the document. Disabled by default."),
    allowmodifydocument: bool | None = Field(None, description="Whether to allow users to modify or edit the document content. Disabled by default."),
    allowcontentextraction: bool | None = Field(None, description="Whether to allow users to copy or extract text and graphics from the document. Disabled by default."),
    allowmodifyannotations: bool | None = Field(None, description="Whether to allow users to add, modify, or delete annotations and comments. Disabled by default."),
    printquality: str | None = Field(None, description="Quality level for printing permissions. Set to 'LowResolution' by default to restrict print quality."),
    name: str | None = Field(None, description="Output filename for the secured PDF document. Defaults to 'output-protected.pdf' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Secure a PDF document by adding password protection and configurable access restrictions. Specify owner and user passwords along with granular permissions for printing, editing, copying, and other document operations."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfSecurityAddRequest(
            body=_models.PostV1PdfSecurityAddRequestBody(url=url, ownerpassword=ownerpassword, userpassword=userpassword, allowaccessibilitysupport=allowaccessibilitysupport, allowassemblydocument=allowassemblydocument, allowprintdocument=allowprintdocument, allowfillforms=allowfillforms, allowmodifydocument=allowmodifydocument, allowcontentextraction=allowcontentextraction, allowmodifyannotations=allowmodifyannotations, printquality=printquality, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_password_to_pdf: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/security/add"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_password_to_pdf")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_password_to_pdf", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_password_to_pdf",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Document, File & System
@mcp.tool()
async def remove_pdf_password(
    url: str = Field(..., description="The URL of the PDF file to remove password protection from. Can be a direct file URL or a cloud storage link."),
    name: str | None = Field(None, description="The desired filename for the unprotected PDF output. Defaults to 'unprotected' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Remove password protection and access restrictions from a PDF file, making it fully accessible without authentication."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfSecurityRemoveRequest(
            body=_models.PostV1PdfSecurityRemoveRequestBody(url=url, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_pdf_password: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/security/remove"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_pdf_password")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_pdf_password", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_pdf_password",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pages
@mcp.tool()
async def delete_pdf_pages(
    url: str = Field(..., description="URL of the PDF file to process. Can be a direct file URL or a path to a PDF stored in cloud storage."),
    pages: str | None = Field(None, description="Comma-separated list of page numbers or ranges to delete, using 1-based indexing. Supports ranges (e.g., 3-5), individual pages (e.g., 2), and negative indices where !1 is the last page (e.g., !1 deletes the last page, !6-!2 deletes from the 6th-to-last to 2nd-to-last page). Whitespace around values is ignored.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    name: str | None = Field(None, description="Filename for the output PDF document. Defaults to 'result.pdf' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Removes specified pages from a PDF file and returns the modified document. Pages are identified using 1-based indexing with support for ranges and negative indices (where !1 refers to the last page)."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfEditDeletePagesRequest(
            body=_models.PostV1PdfEditDeletePagesRequestBody(url=url, pages=pages, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_pdf_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/edit/delete-pages"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_pdf_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_pdf_pages", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_pdf_pages",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pages
@mcp.tool()
async def rotate_pdf_pages(
    url: str = Field(..., description="The URL of the PDF file to rotate. Can be a remote URL or a local file path."),
    pages: str | None = Field(None, description="Zero-based page indices or ranges to rotate, specified as comma-separated values. Supports individual pages (e.g., 0, 2, 5), ranges (e.g., 3-7, 10-), and reverse indexing from the end of the document (e.g., !0 for last page, !5-!2 for a range from the end). Whitespace around values is allowed. Omit to rotate all pages.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
    angle: str | None = Field(None, description="The rotation angle in degrees to apply to selected pages. Common values are 90, 180, and 270 for standard rotations."),
    name: str | None = Field(None, description="The filename for the output PDF document after rotation is applied."),
) -> dict[str, Any] | ToolResult:
    """Rotates specified pages in a PDF document by a given angle. If no pages are specified, the operation rotates all pages in the document."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfEditRotateRequest(
            body=_models.PostV1PdfEditRotateRequestBody(url=url, pages=pages, angle=angle, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rotate_pdf_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/edit/rotate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("rotate_pdf_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("rotate_pdf_pages", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="rotate_pdf_pages",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pages
@mcp.tool()
async def auto_rotate_pdf_pages(
    url: str = Field(..., description="URL of the PDF file to auto-rotate. Accepts a publicly accessible PDF document URL."),
    lang: str | None = Field(None, description="Language(s) for text recognition during rotation analysis. Use a 3-letter language code (e.g., 'eng' for English). Combine multiple languages with a plus sign (e.g., 'eng+deu') for simultaneous multi-language support. Defaults to English.", pattern="^[a-z]{3}(\\+[a-z]{3})*$"),
    name: str | None = Field(None, description="Output filename for the rotated PDF. Specify the desired name with .pdf extension for the returned document."),
) -> dict[str, Any] | ToolResult:
    """Automatically corrects the rotation of pages in a scanned PDF using AI-powered text analysis. Supports multiple languages for accurate text detection and orientation correction."""

    # Construct request model with validation
    try:
        _request = _models.PostV1PdfEditRotateAutoRequest(
            body=_models.PostV1PdfEditRotateAutoRequestBody(url=url, lang=lang, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for auto_rotate_pdf_pages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pdf/edit/rotate/auto"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("auto_rotate_pdf_pages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("auto_rotate_pdf_pages", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="auto_rotate_pdf_pages",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Barcodes
@mcp.tool()
async def generate_barcode(
    value: str | None = Field(None, description="The data or text to encode in the barcode. Defaults to 'abcdef123456' if not provided."),
    type_: Literal["AustralianPostCode", "Aztec", "Codabar", "CodablockF", "Code128", "Code16K", "Code39", "Code39Extended", "Code39Mod43", "Code39Mod43Extended", "Code93", "DataMatrix", "DPMDataMatrix", "EAN13", "EAN2", "EAN5", "EAN8", "GS1DataBarExpanded", "GS1DataBarExpandedStacked", "GS1DataBarLimited", "GS1DataBarOmnidirectional", "GS1DataBarStacked", "GTIN12", "GTIN13", "GTIN14", "GTIN8", "IntelligentMail", "Interleaved2of5", "ITF14", "MaxiCode", "MICR", "MicroPDF", "MSI", "PatchCode", "PDF417", "Pharmacode", "PostNet", "PZN", "QRCode", "RoyalMail", "RoyalMailKIX", "Trioptic", "UPCA", "UPCE", "UPU"] | None = Field(None, alias="type", description="The barcode format type to generate. Defaults to QR Code if not specified. Supports formats such as QR Code, Data Matrix, Code 39, Code 128, and PDF417."),
    decorationimage: str | None = Field(None, description="Optional image file to embed or overlay on the generated barcode for branding or decoration purposes."),
    name: str | None = Field(None, description="The output filename for the generated barcode image. Defaults to 'barcode.png' if not provided."),
) -> dict[str, Any] | ToolResult:
    """Generate high-quality barcode images in various formats including QR Code, Data Matrix, Code 39, Code 128, PDF417, and other standard barcode types."""

    # Construct request model with validation
    try:
        _request = _models.PostV1BarcodeGenerateRequest(
            body=_models.PostV1BarcodeGenerateRequestBody(value=value, type_=type_, decorationimage=decorationimage, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_barcode: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/barcode/generate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_barcode")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_barcode", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_barcode",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Barcodes
@mcp.tool()
async def read_barcodes_from_url(
    url: str = Field(..., description="URL of the image or PDF document to scan for barcodes. Must be publicly accessible."),
    types: str = Field(..., description="Comma-separated list of barcode types to detect. Choose from 40+ supported formats including QRCode, Code128, EAN13, DataMatrix, PDF417, GS1, and others. Only specified types will be decoded."),
    pages: str | None = Field(None, description="Optional page indices or ranges to scan (0-based, applies to PDFs only). Specify individual pages (e.g., 0,2,5), ranges (e.g., 3-7 or 10-), or reverse indices (e.g., !0 for last page). Comma-separated with optional whitespace. If omitted, all pages are processed.", pattern="^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$"),
) -> dict[str, Any] | ToolResult:
    """Decode barcodes and QR codes from images or PDF documents accessible via URL. Supports 40+ barcode formats including QR Code, Code 128, EAN, DataMatrix, PDF417, and GS1 standards."""

    # Construct request model with validation
    try:
        _request = _models.PostV1BarcodeReadFromUrlRequest(
            body=_models.PostV1BarcodeReadFromUrlRequestBody(url=url, types=types, pages=pages)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for read_barcodes_from_url: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/barcode/read/from/url"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("read_barcodes_from_url")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("read_barcodes_from_url", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="read_barcodes_from_url",
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
        print("  python pdf_co_api_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="PDF.co API MCP Server")

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
    logger.info("Starting PDF.co API MCP Server")
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

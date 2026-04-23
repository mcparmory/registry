#!/usr/bin/env python3
"""
Bitbucket MCP Server

API Info:
- Contact: Bitbucket Support <support@bitbucket.org> (https://support.atlassian.com/bitbucket-cloud/)
- Terms of Service: https://www.atlassian.com/legal/customer-agreement

Generated: 2026-04-23 21:02:39 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://api.bitbucket.org/2.0")
SERVER_NAME = "Bitbucket"
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
    'oauth2',
    'basic',
    'api_key',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["oauth2"] = _auth.OAuth2Auth()
    logging.info("Authentication configured: oauth2")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for oauth2 not configured: {error_msg}")
    _auth_handlers["oauth2"] = None
try:
    _auth_handlers["basic"] = _auth.BasicAuth(env_var_username="BASIC_AUTH_USERNAME", env_var_password="BASIC_AUTH_PASSWORD")
    logging.info("Authentication configured: basic")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for basic not configured: {error_msg}")
    _auth_handlers["basic"] = None
try:
    _auth_handlers["api_key"] = _auth.APIKeyAuth(env_var="API_KEY", location="header", param_name="Authorization")
    logging.info("Authentication configured: api_key")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for api_key not configured: {error_msg}")
    _auth_handlers["api_key"] = None

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

mcp = FastMCP("Bitbucket", middleware=[_JsonCoercionMiddleware()])

# Tags: Webhooks
@mcp.tool()
async def list_webhook_event_types() -> dict[str, Any] | ToolResult:
    """Retrieves all webhook resource and subject types on which webhooks can be registered. Each returned type includes an events link for browsing the paginated list of specific events that subject type can emit. No authentication required."""

    # Extract parameters for API call
    _http_path = "/hook_events"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_webhook_event_types")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_webhook_event_types", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_webhook_event_types",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Webhooks
@mcp.tool()
async def list_webhook_event_types_by_subject(subject_type: Literal["repository", "workspace"] = Field(..., description="The entity type for which to retrieve subscribable webhook events. Note: team and user subject types are deprecated; use workspace instead.")) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all valid webhook event types available for subscription on a given subject type (repository or workspace). This is public data requiring no authentication or scopes."""

    # Construct request model with validation
    try:
        _request = _models.GetHookEventsBySubjectTypeRequest(
            path=_models.GetHookEventsBySubjectTypeRequestPath(subject_type=subject_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_webhook_event_types_by_subject: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/hook_events/{subject_type}", _request.path.model_dump(by_alias=True)) if _request.path else "/hook_events/{subject_type}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_webhook_event_types_by_subject")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_webhook_event_types_by_subject", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_webhook_event_types_by_subject",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories
@mcp.tool()
async def list_workspace_repositories(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    role: Literal["admin", "contributor", "member", "owner"] | None = Field(None, description="Filters repositories based on the authenticated user's access level: member (read access), contributor (write access), admin (administrator access), or owner (all repositories owned by the user)."),
    q: str | None = Field(None, description="A query string to filter repositories using Bitbucket's filtering syntax, allowing you to narrow results by repository properties."),
    sort: str | None = Field(None, description="The field name by which to sort the returned repositories, following Bitbucket's sorting syntax for ordering results."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all repositories within a specified workspace. Results can be filtered by the authenticated user's role and further narrowed using query and sort parameters."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceRequest(
            path=_models.GetRepositoriesByWorkspaceRequestPath(workspace=workspace),
            query=_models.GetRepositoriesByWorkspaceRequestQuery(role=role, q=q, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_repositories: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_repositories")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_repositories", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_repositories",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories
@mcp.tool()
async def get_repository(
    repo_slug: str = Field(..., description="The repository identifier, either as a URL-friendly slug or as a UUID wrapped in curly-braces."),
    workspace: str = Field(..., description="The workspace identifier, either as a URL-friendly slug or as a UUID wrapped in curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed metadata for a specific repository within a workspace. Returns the full repository object including settings, links, and configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories
@mcp.tool()
async def create_repository(
    repo_slug: str = Field(..., description="The slug or UUID of the repository to create. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID in which to create the repository. UUIDs must be surrounded by curly-braces."),
    body: _models.Repository | None = Field(None, description="Optional request body containing repository configuration such as SCM type and project assignment. If no project is specified, the repository is automatically assigned to the oldest project in the workspace."),
) -> dict[str, Any] | ToolResult:
    """Creates a new repository in the specified workspace. Optionally assigns the repository to a project by providing a project key or UUID in the request body."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesRequest(
            path=_models.PostRepositoriesRequestPath(repo_slug=repo_slug, workspace=workspace),
            body=_models.PostRepositoriesRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_repository", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_repository",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories
@mcp.tool()
async def update_repository(
    repo_slug: str = Field(..., description="The slug or UUID of the repository to update. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID containing the repository. UUIDs must be surrounded by curly-braces."),
    body: _models.Repository | None = Field(None, description="The repository fields to update, such as name, description, or visibility settings. Refer to the repository POST endpoint documentation for the full request body structure."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing repository's settings and metadata within a workspace, or creates one if it does not exist. Renaming the repository will change its URL slug and return the new location in the response's Location header if no slug conflict occurs."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesRequest(
            path=_models.PutRepositoriesRequestPath(repo_slug=repo_slug, workspace=workspace),
            body=_models.PutRepositoriesRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_repository", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_repository",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories
@mcp.tool()
async def delete_repository(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository to delete. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly-braces."),
    redirect_to: str | None = Field(None, description="An optional redirect path to display a friendly relocation message in the Bitbucket UI when a repository has moved. Note that GET requests to the original endpoint will still return a 404 regardless."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes the specified repository from a workspace. This action is irreversible and does not affect any existing forks of the repository."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesRequest(
            path=_models.DeleteRepositoriesRequestPath(repo_slug=repo_slug, workspace=workspace),
            query=_models.DeleteRepositoriesRequestQuery(redirect_to=redirect_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_repository", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_repository",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Branch restrictions
@mcp.tool()
async def list_branch_restrictions(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
    kind: str | None = Field(None, description="Filters results to only return branch restrictions of the specified type, such as push or merge restrictions."),
    pattern: str | None = Field(None, description="Filters results to only return branch restrictions that apply to branches matching the specified pattern."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all branch restrictions configured for a repository. Optionally filter results by restriction kind or branch name pattern."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugBranchRestrictionsRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugBranchRestrictionsRequestPath(repo_slug=repo_slug, workspace=workspace),
            query=_models.GetRepositoriesByWorkspaceByRepoSlugBranchRestrictionsRequestQuery(kind=kind, pattern=pattern)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_branch_restrictions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/branch-restrictions", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/branch-restrictions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_branch_restrictions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_branch_restrictions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_branch_restrictions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Branch restrictions
@mcp.tool()
async def create_branch_restriction(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
    body: _models.Branchrestriction | None = Field(None, description="The branch restriction rule definition, including the restriction kind, branch matching strategy (glob pattern or branching model type), and optionally the users and groups exempt from the restriction."),
) -> dict[str, Any] | ToolResult:
    """Creates a new branch restriction rule for a repository, controlling actions such as pushing, merging, or deleting branches based on matching patterns or branching model types."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesBranchRestrictionsRequest(
            path=_models.PostRepositoriesBranchRestrictionsRequestPath(repo_slug=repo_slug, workspace=workspace),
            body=_models.PostRepositoriesBranchRestrictionsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_branch_restriction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/branch-restrictions", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/branch-restrictions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_branch_restriction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_branch_restriction", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_branch_restriction",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Branch restrictions
@mcp.tool()
async def get_branch_restriction(
    id_: str = Field(..., alias="id", description="The unique numeric identifier of the branch restriction rule to retrieve."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific branch restriction rule for a repository by its unique ID. Use this to inspect the configuration of an individual branch protection or access control rule."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugBranchRestrictionsByIdRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugBranchRestrictionsByIdRequestPath(id_=id_, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_branch_restriction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/branch-restrictions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/branch-restrictions/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_branch_restriction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_branch_restriction", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_branch_restriction",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Branch restrictions
@mcp.tool()
async def update_branch_restriction(
    id_: str = Field(..., alias="id", description="The unique numeric identifier of the branch restriction rule to update."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace. UUID values must be surrounded by curly-braces."),
    body: _models.Branchrestriction | None = Field(None, description="The request body containing the branch restriction rule fields to update. Only fields present in the body will be modified."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing branch restriction rule for a repository. Only fields included in the request body are modified; omitted fields retain their current values."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesBranchRestrictionsRequest(
            path=_models.PutRepositoriesBranchRestrictionsRequestPath(id_=id_, repo_slug=repo_slug, workspace=workspace),
            body=_models.PutRepositoriesBranchRestrictionsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_branch_restriction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/branch-restrictions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/branch-restrictions/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_branch_restriction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_branch_restriction", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_branch_restriction",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Branch restrictions
@mcp.tool()
async def delete_branch_restriction(
    id_: str = Field(..., alias="id", description="The unique numeric identifier of the branch restriction rule to delete."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes an existing branch restriction rule from a repository. This action cannot be undone and will immediately remove the associated access or push controls."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesBranchRestrictionsRequest(
            path=_models.DeleteRepositoriesBranchRestrictionsRequestPath(id_=id_, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_branch_restriction: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/branch-restrictions/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/branch-restrictions/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_branch_restriction")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_branch_restriction", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_branch_restriction",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Branching model
@mcp.tool()
async def get_branching_model(
    repo_slug: str = Field(..., description="The repository identifier, either the URL-friendly slug or the repository UUID enclosed in curly-braces."),
    workspace: str = Field(..., description="The workspace identifier, either the workspace slug or the workspace UUID enclosed in curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the active branching model for a repository, including the development branch, optional production branch, and all enabled branch types. This is a read-only view; use the branching model settings endpoint to modify the configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesBranchingModelRequest(
            path=_models.GetRepositoriesBranchingModelRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_branching_model: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/branching-model", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/branching-model"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_branching_model")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_branching_model", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_branching_model",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Branching model
@mcp.tool()
async def get_branching_model_settings(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository whose branching model settings are being retrieved. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the raw branching model configuration for a repository, including development and production branch settings, branch type definitions, and default branch deletion behavior. Use the active branching model endpoint instead if you need to see the configuration resolved against actual current branches."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesBranchingModelSettingsRequest(
            path=_models.GetRepositoriesBranchingModelSettingsRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_branching_model_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/branching-model/settings", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/branching-model/settings"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_branching_model_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_branching_model_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_branching_model_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Branching model
@mcp.tool()
async def update_branching_model_settings(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Updates the branching model configuration for a repository, including development branch, production branch, branch type prefixes, and default branch deletion behavior. Only properties explicitly passed in the request body will be modified; omitted properties remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesBranchingModelSettingsRequest(
            path=_models.PutRepositoriesBranchingModelSettingsRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_branching_model_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/branching-model/settings", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/branching-model/settings"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_branching_model_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_branching_model_settings", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_branching_model_settings",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commits
@mcp.tool()
async def get_commit(
    commit: str = Field(..., description="The full SHA1 hash of the commit to retrieve."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves details for a specific commit in a repository using its SHA1 identifier. Returns commit metadata including author, timestamp, and associated changes."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesCommitRequest(
            path=_models.GetRepositoriesCommitRequestPath(commit=commit, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_commit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_commit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_commit", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_commit",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commits
@mcp.tool()
async def approve_commit(
    commit: str = Field(..., description="The full SHA1 hash identifying the specific commit to approve."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository containing the commit. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Approves a specific commit as the authenticated user, recording their explicit approval. Requires the user to have direct access to the repository, as public visibility alone does not grant approval permissions."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesCommitApproveRequest(
            path=_models.PostRepositoriesCommitApproveRequestPath(commit=commit, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for approve_commit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/approve", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/approve"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("approve_commit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("approve_commit", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="approve_commit",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commits
@mcp.tool()
async def unapprove_commit(
    commit: str = Field(..., description="The SHA1 hash uniquely identifying the commit to unapprove."),
    repo_slug: str = Field(..., description="The repository slug or UUID (surrounded by curly-braces) that contains the commit."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID (surrounded by curly-braces) that owns the repository."),
) -> dict[str, Any] | ToolResult:
    """Removes the authenticated user's approval from a specified commit in a repository. This action requires explicit access to the repository; public visibility alone does not grant approval or unapproval rights."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesCommitApproveRequest(
            path=_models.DeleteRepositoriesCommitApproveRequestPath(commit=commit, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unapprove_commit: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/approve", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/approve"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unapprove_commit")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unapprove_commit", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unapprove_commit",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commits
@mcp.tool()
async def list_commit_comments(
    commit: str = Field(..., description="The full SHA1 hash identifying the specific commit whose comments should be retrieved."),
    repo_slug: str = Field(..., description="The repository slug or UUID that uniquely identifies the repository within the workspace. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID that uniquely identifies the workspace containing the repository. UUIDs must be surrounded by curly-braces."),
    q: str | None = Field(None, description="A query string to filter the returned comments using Bitbucket's filtering and sorting syntax, allowing you to narrow results by specific field conditions."),
    sort: str | None = Field(None, description="The field name by which to sort the returned comments, following Bitbucket's filtering and sorting syntax. Overrides the default oldest-to-newest ordering."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all comments (both global and inline) for a specific commit in a repository. Results are sorted oldest to newest by default and can be filtered or reordered using query parameters."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugCommitByCommitCommentsRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugCommitByCommitCommentsRequestPath(commit=commit, repo_slug=repo_slug, workspace=workspace),
            query=_models.GetRepositoriesByWorkspaceByRepoSlugCommitByCommitCommentsRequestQuery(q=q, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_commit_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/comments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_commit_comments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_commit_comments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_commit_comments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commits
@mcp.tool()
async def create_commit_comment(
    commit: str = Field(..., description="The full SHA1 hash of the commit to comment on."),
    repo_slug: str = Field(..., description="The repository slug or UUID (surrounded by curly-braces) that identifies the repository within the workspace."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID (surrounded by curly-braces) that identifies the workspace containing the repository."),
    body: _models.CommitComment | None = Field(None, description="The comment payload, including the comment content and an optional parent comment ID to post a reply in an existing thread."),
) -> dict[str, Any] | ToolResult:
    """Posts a new comment on a specific commit in a repository. Supports threaded replies by referencing a parent comment ID in the request body."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesCommitCommentsRequest(
            path=_models.PostRepositoriesCommitCommentsRequestPath(commit=commit, repo_slug=repo_slug, workspace=workspace),
            body=_models.PostRepositoriesCommitCommentsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_commit_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/comments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_commit_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_commit_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_commit_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commits
@mcp.tool()
async def get_commit_comment(
    comment_id: str = Field(..., description="The unique numeric identifier of the commit comment to retrieve."),
    commit: str = Field(..., description="The full SHA1 hash of the commit whose comment is being retrieved."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) or the repository UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug (URL-friendly identifier) or the workspace UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific comment on a commit by its comment ID. Returns the full comment details including content, author, and timestamps."""

    _comment_id = _parse_int(comment_id)

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugCommitByCommitCommentsByCommentIdRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugCommitByCommitCommentsByCommentIdRequestPath(comment_id=_comment_id, commit=commit, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_commit_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/comments/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/comments/{comment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_commit_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_commit_comment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_commit_comment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commits
@mcp.tool()
async def update_commit_comment(
    comment_id: str = Field(..., description="The unique numeric identifier of the comment to update."),
    commit: str = Field(..., description="The full SHA1 hash of the commit that the comment belongs to."),
    repo_slug: str = Field(..., description="The repository slug or UUID (surrounded by curly-braces) that uniquely identifies the repository within the workspace."),
    workspace: str = Field(..., description="The workspace slug or UUID (surrounded by curly-braces) that uniquely identifies the workspace containing the repository."),
    body: _models.CommitComment | None = Field(None, description="The request body containing the updated comment content, structured as a commit comment object with a raw text content field."),
) -> dict[str, Any] | ToolResult:
    """Updates the text content of an existing comment on a specific commit. Only the comment's content can be modified; other properties remain unchanged."""

    _comment_id = _parse_int(comment_id)

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesCommitCommentsRequest(
            path=_models.PutRepositoriesCommitCommentsRequestPath(comment_id=_comment_id, commit=commit, repo_slug=repo_slug, workspace=workspace),
            body=_models.PutRepositoriesCommitCommentsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_commit_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/comments/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/comments/{comment_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_commit_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_commit_comment", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_commit_comment",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commits
@mcp.tool()
async def delete_commit_comment(
    comment_id: str = Field(..., description="The unique numeric identifier of the commit comment to delete."),
    commit: str = Field(..., description="The full SHA1 hash of the commit whose comment is being deleted."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Deletes a specific comment on a commit in a repository. If the comment has visible replies, it will be soft-deleted — its content is blanked and marked as deleted — to preserve the integrity of the comment thread."""

    _comment_id = _parse_int(comment_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesCommitCommentsRequest(
            path=_models.DeleteRepositoriesCommitCommentsRequestPath(comment_id=_comment_id, commit=commit, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_commit_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/comments/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/comments/{comment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_commit_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_commit_comment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_commit_comment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def get_commit_property(
    workspace: str = Field(..., description="The workspace containing the repository, identified by its slug or UUID (UUID must be wrapped in curly braces)."),
    repo_slug: str = Field(..., description="The slug of the repository where the commit resides."),
    commit: str = Field(..., description="The identifier of the commit whose application property is being retrieved."),
    app_key: str = Field(..., description="The unique key identifying the Connect app that owns the property."),
    property_name: str = Field(..., description="The name of the application property to retrieve from the specified commit."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific application property value stored against a commit in a Bitbucket repository. Useful for reading custom metadata attached to a commit by a Connect app."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesCommitPropertiesRequest(
            path=_models.GetRepositoriesCommitPropertiesRequestPath(workspace=workspace, repo_slug=repo_slug, commit=commit, app_key=app_key, property_name=property_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_commit_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/properties/{app_key}/{property_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/properties/{app_key}/{property_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_commit_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_commit_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_commit_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def update_commit_property(
    workspace: str = Field(..., description="The workspace that contains the repository, identified by its slug or UUID (UUID must be wrapped in curly braces)."),
    repo_slug: str = Field(..., description="The slug of the repository where the commit resides."),
    commit: str = Field(..., description="The commit identifier (hash) against which the application property is stored."),
    app_key: str = Field(..., description="The unique key identifying the Connect app that owns the property."),
    property_name: str = Field(..., description="The name of the application property to update, scoped to the specified Connect app."),
) -> dict[str, Any] | ToolResult:
    """Update the value of an application property stored against a specific commit in a repository. Application properties allow Connect apps to associate custom metadata with Bitbucket resources."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesCommitPropertiesRequest(
            path=_models.PutRepositoriesCommitPropertiesRequestPath(workspace=workspace, repo_slug=repo_slug, commit=commit, app_key=app_key, property_name=property_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_commit_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/properties/{app_key}/{property_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/properties/{app_key}/{property_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_commit_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_commit_property", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_commit_property",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def delete_commit_property(
    workspace: str = Field(..., description="The workspace containing the repository, specified as either the workspace slug or the workspace UUID wrapped in curly braces."),
    repo_slug: str = Field(..., description="The slug identifier of the repository from which the commit property will be deleted."),
    commit: str = Field(..., description="The commit identifier (hash) whose associated application property will be deleted."),
    app_key: str = Field(..., description="The unique key identifying the Bitbucket Connect app that owns the property being deleted."),
    property_name: str = Field(..., description="The name of the application property to delete from the specified commit."),
) -> dict[str, Any] | ToolResult:
    """Deletes a specific application property value stored against a commit in a Bitbucket repository. This permanently removes the key-value metadata associated with the given Connect app and property name."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesCommitPropertiesRequest(
            path=_models.DeleteRepositoriesCommitPropertiesRequestPath(workspace=workspace, repo_slug=repo_slug, commit=commit, app_key=app_key, property_name=property_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_commit_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/properties/{app_key}/{property_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/properties/{app_key}/{property_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_commit_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_commit_property", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_commit_property",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def list_commit_pull_requests(
    workspace: str = Field(..., description="The workspace identifier, either the workspace slug or the UUID enclosed in curly braces."),
    repo_slug: str = Field(..., description="The repository identifier, either the repository slug or the UUID enclosed in curly braces."),
    commit: str = Field(..., description="The full SHA1 hash of the commit whose associated pull requests should be retrieved."),
    pagelen: str | None = Field(None, description="The number of pull requests to return per page; controls pagination page size."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all pull requests that include a specific commit as part of their review. Requires the Pull Request Commit Links app to be installed on the repository."""

    _pagelen = _parse_int(pagelen)

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesCommitPullrequestsRequest(
            path=_models.GetRepositoriesCommitPullrequestsRequestPath(workspace=workspace, repo_slug=repo_slug, commit=commit),
            query=_models.GetRepositoriesCommitPullrequestsRequestQuery(pagelen=_pagelen)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_commit_pull_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/pullrequests", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/pullrequests"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_commit_pull_requests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_commit_pull_requests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_commit_pull_requests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reports, Commits
@mcp.tool()
async def list_commit_reports(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace."),
    commit: str = Field(..., description="The full commit hash identifying the specific commit whose reports should be retrieved."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of code insight reports linked to a specific commit in a repository. Useful for reviewing quality, security, or test results associated with a given commit."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsRequestPath(workspace=workspace, repo_slug=repo_slug, commit=commit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_commit_reports: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/reports", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/reports"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_commit_reports")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_commit_reports", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_commit_reports",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reports, Commits
@mcp.tool()
async def get_commit_report(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that contains the commit and report."),
    commit: str = Field(..., description="The full commit hash identifying the specific commit the report is associated with."),
    report_id: str = Field(..., alias="reportId", description="The unique identifier of the report, accepted as either a UUID or an external ID assigned by the reporting tool."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single code insight report for a specific commit in a repository. Returns the full report details matching the provided report ID."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdRequestPath(workspace=workspace, repo_slug=repo_slug, commit=commit, report_id=report_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_commit_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{reportId}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{reportId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_commit_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_commit_report", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_commit_report",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reports, Commits
@mcp.tool()
async def create_or_update_commit_report(
    workspace: str = Field(..., description="The workspace identifier — either the slug (short name) or the UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that contains the target commit."),
    commit: str = Field(..., description="The full commit hash that this report is associated with."),
    report_id: str = Field(..., alias="reportId", description="A unique identifier for the report scoped to this commit — either a UUID or an external ID. To avoid collisions with other systems, prefix external IDs with your system name (e.g., mySystem-001)."),
    body: _models.PutRepositoriesCommitReportsBody | None = Field(None, description="The report payload containing metadata and result data. Supports fields: title, details, report_type (SECURITY, COVERAGE, TEST, BUG), reporter, link, result (PASSED, FAILED, PENDING), and a data array of typed metric entries. Each data entry specifies a title, type (BOOLEAN, DATE, DURATION, LINK, NUMBER, PERCENTAGE, TEXT), and a value whose format depends on the type — see the data field format table for type-specific value requirements."),
) -> dict[str, Any] | ToolResult:
    """Creates or updates a Code Insights report for a specific commit in a repository. Use a unique report ID per commit, optionally prefixed with your system name to avoid collisions."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesCommitReportsRequest(
            path=_models.PutRepositoriesCommitReportsRequestPath(workspace=workspace, repo_slug=repo_slug, commit=commit, report_id=report_id),
            body=_models.PutRepositoriesCommitReportsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_or_update_commit_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{reportId}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{reportId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_or_update_commit_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_or_update_commit_report", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_or_update_commit_report",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reports, Commits
@mcp.tool()
async def delete_commit_report(
    workspace: str = Field(..., description="The workspace identifier, either the slug (short name) or the UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that contains the commit and its associated report."),
    commit: str = Field(..., description="The full commit hash identifying the commit to which the report belongs."),
    report_id: str = Field(..., alias="reportId", description="The unique identifier of the report to delete, accepted as either the report's UUID or its external ID."),
) -> dict[str, Any] | ToolResult:
    """Deletes a single code insights report associated with a specific commit in a repository. The report is identified by its unique report ID."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesCommitReportsRequest(
            path=_models.DeleteRepositoriesCommitReportsRequestPath(workspace=workspace, repo_slug=repo_slug, commit=commit, report_id=report_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_commit_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{reportId}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{reportId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_commit_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_commit_report", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_commit_report",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reports, Commits
@mcp.tool()
async def list_commit_report_annotations(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace."),
    commit: str = Field(..., description="The full commit hash identifying the specific commit whose report annotations should be retrieved."),
    report_id: str = Field(..., alias="reportId", description="The unique identifier of the report, accepted as either a UUID or an external ID, for which annotations will be listed."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of annotations associated with a specific code insights report for a given commit in a repository."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdAnnotationsRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdAnnotationsRequestPath(workspace=workspace, repo_slug=repo_slug, commit=commit, report_id=report_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_commit_report_annotations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{reportId}/annotations", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{reportId}/annotations"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_commit_report_annotations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_commit_report_annotations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_commit_report_annotations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reports, Commits
@mcp.tool()
async def bulk_create_annotations(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (e.g., my-team) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the workspace."),
    commit: str = Field(..., description="The full commit hash for which the report and its annotations are being uploaded."),
    report_id: str = Field(..., alias="reportId", description="The UUID or external ID of the report to which these annotations belong."),
    body: list[_models.ReportAnnotation] | None = Field(None, description="Array of annotation objects to create or update. Each annotation must include a unique external_id and may specify fields such as annotation_type (VULNERABILITY, CODE_SMELL, BUG), severity (CRITICAL, HIGH, MEDIUM, LOW), result (PASSED, FAILED, IGNORED, SKIPPED), and an optional file path and line number. Up to 100 annotations can be submitted per request.", min_length=1, max_length=100),
) -> dict[str, Any] | ToolResult:
    """Bulk create or update up to 100 annotations for a specific commit report in a repository. Annotations represent individual findings (e.g., vulnerabilities, bugs, code smells) and can be optionally linked to a specific file and line number."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesCommitReportsAnnotationsRequest(
            path=_models.PostRepositoriesCommitReportsAnnotationsRequestPath(workspace=workspace, repo_slug=repo_slug, commit=commit, report_id=report_id),
            body=_models.PostRepositoriesCommitReportsAnnotationsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for bulk_create_annotations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{reportId}/annotations", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{reportId}/annotations"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("bulk_create_annotations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("bulk_create_annotations", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="bulk_create_annotations",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reports, Commits
@mcp.tool()
async def get_commit_report_annotation(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The URL-friendly slug of the repository within the specified workspace."),
    commit: str = Field(..., description="The full commit hash identifying the commit to which the report belongs."),
    report_id: str = Field(..., alias="reportId", description="The unique identifier of the report, accepted as either its UUID or its external ID string."),
    annotation_id: str = Field(..., alias="annotationId", description="The unique identifier of the annotation to retrieve, accepted as either its UUID or its external ID string."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single annotation by its ID from a specific code insight report on a given commit. Useful for inspecting individual findings or diagnostics attached to a commit report."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdAnnotationsByAnnotationIdRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugCommitByCommitReportsByReportIdAnnotationsByAnnotationIdRequestPath(workspace=workspace, repo_slug=repo_slug, commit=commit, report_id=report_id, annotation_id=annotation_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_commit_report_annotation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{reportId}/annotations/{annotationId}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{reportId}/annotations/{annotationId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_commit_report_annotation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_commit_report_annotation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_commit_report_annotation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reports, Commits
@mcp.tool()
async def upsert_commit_report_annotation(
    workspace: str = Field(..., description="The workspace identifier, either the slug or the UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the workspace."),
    commit: str = Field(..., description="The full commit hash that the report and annotation belong to."),
    report_id: str = Field(..., alias="reportId", description="The unique identifier of the report to annotate, either its UUID or the external ID used when the report was created."),
    annotation_id: str = Field(..., alias="annotationId", description="The unique identifier for this annotation, either its UUID or an external ID; prefix external IDs with your system name to avoid collisions."),
    body: _models.PutRepositoriesCommitReportsAnnotationsBody | None = Field(None, description="The annotation payload containing fields such as title, summary, annotation_type (VULNERABILITY, CODE_SMELL, BUG), severity (CRITICAL, HIGH, MEDIUM, LOW), result (PASSED, FAILED, IGNORED, SKIPPED), and optional file path and line number."),
) -> dict[str, Any] | ToolResult:
    """Creates or updates a single annotation on a specific commit report, representing an individual finding such as a vulnerability, bug, or code smell, optionally linked to a file and line number."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesCommitReportsAnnotationsRequest(
            path=_models.PutRepositoriesCommitReportsAnnotationsRequestPath(workspace=workspace, repo_slug=repo_slug, commit=commit, report_id=report_id, annotation_id=annotation_id),
            body=_models.PutRepositoriesCommitReportsAnnotationsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upsert_commit_report_annotation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{reportId}/annotations/{annotationId}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{reportId}/annotations/{annotationId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upsert_commit_report_annotation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upsert_commit_report_annotation", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upsert_commit_report_annotation",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Reports, Commits
@mcp.tool()
async def delete_commit_annotation(
    workspace: str = Field(..., description="The workspace identifier, either the slug (short name) or the UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the workspace."),
    commit: str = Field(..., description="The commit hash or identifier that the target annotation belongs to."),
    report_id: str = Field(..., alias="reportId", description="The unique identifier of the report containing the annotation, either its UUID or external ID."),
    annotation_id: str = Field(..., alias="annotationId", description="The unique identifier of the annotation to delete, either its UUID or external ID."),
) -> dict[str, Any] | ToolResult:
    """Deletes a single annotation from a specific commit report in a repository. The annotation is identified by its unique ID within the specified report."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesCommitReportsAnnotationsRequest(
            path=_models.DeleteRepositoriesCommitReportsAnnotationsRequestPath(workspace=workspace, repo_slug=repo_slug, commit=commit, report_id=report_id, annotation_id=annotation_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_commit_annotation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{reportId}/annotations/{annotationId}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/reports/{reportId}/annotations/{annotationId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_commit_annotation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_commit_annotation", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_commit_annotation",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commit statuses
@mcp.tool()
async def list_commit_statuses(
    commit: str = Field(..., description="The full SHA1 hash of the commit whose statuses you want to retrieve."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace. UUIDs must be surrounded by curly-braces."),
    refname: str | None = Field(None, description="Filters results to only include commit statuses created with the specified ref name, or those created without any ref name."),
    q: str | None = Field(None, description="A query string to filter results using Bitbucket's filtering and sorting syntax, allowing you to narrow the returned statuses by field values."),
    sort: str | None = Field(None, description="The field by which to sort the returned statuses using Bitbucket's filtering and sorting syntax. Defaults to created_on if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all statuses (such as CI/CD build results) associated with a specific commit in a Bitbucket repository. Supports filtering by ref name, query string, and custom sorting."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesCommitStatusesRequest(
            path=_models.GetRepositoriesCommitStatusesRequestPath(commit=commit, repo_slug=repo_slug, workspace=workspace),
            query=_models.GetRepositoriesCommitStatusesRequestQuery(refname=refname, q=q, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_commit_statuses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/statuses", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/statuses"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_commit_statuses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_commit_statuses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_commit_statuses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commit statuses
@mcp.tool()
async def create_commit_build_status(
    commit: str = Field(..., description="The full SHA1 hash of the commit to attach the build status to."),
    repo_slug: str = Field(..., description="The repository identifier, either as a slug (e.g. my-repo) or as a UUID surrounded by curly braces."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (e.g. my-workspace) or as a UUID surrounded by curly braces."),
    body: _models.Commitstatus | None = Field(None, description="The build status payload containing fields such as key, state, description, url, and optionally refname. The key uniquely identifies the build status; if it already exists, the existing record will be overwritten. Set refname to the pull request source branch to associate the status with a pull request. The url field supports URI templates with context variables repository and commit."),
) -> dict[str, Any] | ToolResult:
    """Creates or overwrites a build status for a specific commit in a repository, allowing CI/CD systems to report build results. Optionally associate the status with a pull request by specifying the source branch via the refname field."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesCommitStatusesBuildRequest(
            path=_models.PostRepositoriesCommitStatusesBuildRequestPath(commit=commit, repo_slug=repo_slug, workspace=workspace),
            body=_models.PostRepositoriesCommitStatusesBuildRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_commit_build_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/statuses/build", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/statuses/build"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_commit_build_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_commit_build_status", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_commit_build_status",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commit statuses
@mcp.tool()
async def get_commit_build_status(
    commit: str = Field(..., description="The full SHA1 hash of the commit whose build status you want to retrieve."),
    key: str = Field(..., description="The unique key identifying the specific build status entry associated with the commit."),
    repo_slug: str = Field(..., description="The repository identifier, either as a URL-friendly slug or as a UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace identifier, either as a URL-friendly slug or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific build status for a given commit using its unique key. Useful for checking the CI/CD pipeline result associated with a particular commit in a repository."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesCommitStatusesBuildRequest(
            path=_models.GetRepositoriesCommitStatusesBuildRequestPath(commit=commit, key=key, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_commit_build_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/statuses/build/{key}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/statuses/build/{key}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_commit_build_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_commit_build_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_commit_build_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commit statuses
@mcp.tool()
async def update_commit_build_status(
    commit: str = Field(..., description="The full SHA1 hash of the commit whose build status you want to update."),
    key: str = Field(..., description="The unique key identifying the build status entry to update. This value cannot be changed via this operation."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) or the repository UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug (URL-friendly identifier) or the workspace UUID surrounded by curly-braces."),
    body: _models.Commitstatus | None = Field(None, description="The request body containing the build status fields to update, such as state, name, description, url, or refname."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing build status entry for a specific commit in a repository. Allows modification of state, name, description, URL, and ref name, while the unique key remains immutable."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesCommitStatusesBuildRequest(
            path=_models.PutRepositoriesCommitStatusesBuildRequestPath(commit=commit, key=key, repo_slug=repo_slug, workspace=workspace),
            body=_models.PutRepositoriesCommitStatusesBuildRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_commit_build_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commit/{commit}/statuses/build/{key}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commit/{commit}/statuses/build/{key}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_commit_build_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_commit_build_status", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_commit_build_status",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commits
@mcp.tool()
async def list_commits(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository within the workspace."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that owns the repository."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all commits for a repository in reverse chronological (topological) order, similar to `git log --all`. Supports filtering by included/excluded refs and an optional file or directory path to scope results."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugCommitsRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugCommitsRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_commits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commits", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commits"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_commits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_commits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_commits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commits
@mcp.tool()
async def list_commits_with_filters(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of commits for a repository, accepting include and exclude branch/commit parameters in the request body to avoid URL length limitations. This is functionally identical to the GET commits endpoint but does not support creating new commits."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesForWorkspaceForRepoSlugCommitsRequest(
            path=_models.PostRepositoriesForWorkspaceForRepoSlugCommitsRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_commits_with_filters: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commits", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commits"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_commits_with_filters")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_commits_with_filters", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_commits_with_filters",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commits
@mcp.tool()
async def list_commits_by_revision(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository within the workspace. UUID values must be surrounded by curly-braces."),
    revision: str = Field(..., description="The starting point for the commit log; accepts a full or abbreviated commit SHA1 or a ref name such as a branch or tag."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of commits for a given branch, tag, or commit SHA in reverse chronological order, similar to `git log`. Supports filtering by additional include/exclude refs and an optional file or directory path to narrow results to commits affecting that path."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugCommitsByRevisionRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugCommitsByRevisionRequestPath(repo_slug=repo_slug, revision=revision, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_commits_by_revision: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commits/{revision}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commits/{revision}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_commits_by_revision")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_commits_by_revision", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_commits_by_revision",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commits
@mcp.tool()
async def list_commits_by_revision_post(
    repo_slug: str = Field(..., description="The repository identifier, either as a slug (URL-friendly name) or as a UUID surrounded by curly-braces."),
    revision: str = Field(..., description="The starting point for the commit history, specified as a full or abbreviated commit SHA1 hash or a ref name such as a branch or tag."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (workspace ID) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the commit history for a specific revision (SHA1 or branch/tag name) in a repository, using the request body to pass include and exclude filters instead of URL parameters to avoid length limitations."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesForWorkspaceForRepoSlugCommitsForRevisionRequest(
            path=_models.PostRepositoriesForWorkspaceForRepoSlugCommitsForRevisionRequestPath(repo_slug=repo_slug, revision=revision, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_commits_by_revision_post: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/commits/{revision}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/commits/{revision}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_commits_by_revision_post")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_commits_by_revision_post", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_commits_by_revision_post",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def list_default_reviewers(
    repo_slug: str = Field(..., description="The repository identifier, either as a slug (URL-friendly name) or as a UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (workspace short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the list of users automatically added as reviewers on every new pull request for the specified repository. To include reviewers inherited from the parent project, use the effective-default-reviewers endpoint instead."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugDefaultReviewersRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugDefaultReviewersRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_default_reviewers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/default-reviewers", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/default-reviewers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_default_reviewers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_default_reviewers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_default_reviewers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def get_default_reviewer(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces."),
    target_username: str = Field(..., description="The username or UUID of the default reviewer to look up. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID that owns the repository. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific default reviewer for a repository, confirming they are on the default reviewers list. A 404 response indicates the specified user is not a default reviewer for the repository."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugDefaultReviewersByTargetUsernameRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugDefaultReviewersByTargetUsernameRequestPath(repo_slug=repo_slug, target_username=target_username, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_default_reviewer: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/default-reviewers/{target_username}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/default-reviewers/{target_username}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_default_reviewer")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_default_reviewer", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_default_reviewer",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def add_default_reviewer(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository within the workspace."),
    target_username: str = Field(..., description="The username or UUID of the user to add as a default reviewer for the repository."),
    workspace: str = Field(..., description="The workspace slug or UUID that owns the repository."),
) -> dict[str, Any] | ToolResult:
    """Adds a specified user to the repository's list of default reviewers for pull requests. This operation is idempotent — adding a user who is already a default reviewer has no effect."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesDefaultReviewersRequest(
            path=_models.PutRepositoriesDefaultReviewersRequestPath(repo_slug=repo_slug, target_username=target_username, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_default_reviewer: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/default-reviewers/{target_username}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/default-reviewers/{target_username}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_default_reviewer")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_default_reviewer", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_default_reviewer",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def remove_default_reviewer(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository within the workspace."),
    target_username: str = Field(..., description="The username or UUID of the default reviewer to remove from the repository."),
    workspace: str = Field(..., description="The workspace slug or UUID that contains the repository."),
) -> dict[str, Any] | ToolResult:
    """Removes a specified user from the default reviewers list for a repository. After removal, the user will no longer be automatically added as a reviewer on new pull requests."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesDefaultReviewersRequest(
            path=_models.DeleteRepositoriesDefaultReviewersRequestPath(repo_slug=repo_slug, target_username=target_username, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_default_reviewer: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/default-reviewers/{target_username}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/default-reviewers/{target_username}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_default_reviewer")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_default_reviewer", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_default_reviewer",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deployments
@mcp.tool()
async def list_deploy_keys(
    repo_slug: str = Field(..., description="The repository identifier, either as a slug (URL-friendly name) or as a UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all deploy keys associated with a specific repository in a workspace. Deploy keys provide read or read/write access to a repository without requiring user credentials."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugDeployKeysRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugDeployKeysRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_deploy_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/deploy-keys", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/deploy-keys"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_deploy_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_deploy_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_deploy_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deployments
@mcp.tool()
async def add_deploy_key(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Adds a new SSH deploy key to a repository, granting read or write access without requiring user credentials. Note that deploy keys authenticated via an OAuth consumer will be invalidated if that consumer is modified."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesDeployKeysRequest(
            path=_models.PostRepositoriesDeployKeysRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_deploy_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/deploy-keys", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/deploy-keys"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_deploy_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_deploy_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_deploy_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deployments
@mcp.tool()
async def get_deploy_key(
    key_id: str = Field(..., description="The unique numeric identifier of the deploy key to retrieve."),
    repo_slug: str = Field(..., description="The repository slug or UUID that owns the deploy key. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace identifier (slug) or UUID in which the repository resides. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific deploy key associated with a repository, identified by its unique key ID. Useful for inspecting deploy key details such as label, public key value, and permissions."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugDeployKeysByKeyIdRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugDeployKeysByKeyIdRequestPath(key_id=key_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_deploy_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/deploy-keys/{key_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/deploy-keys/{key_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_deploy_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_deploy_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_deploy_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deployments
@mcp.tool()
async def update_deploy_key(
    key_id: str = Field(..., description="The numeric ID of the deploy key to update."),
    repo_slug: str = Field(..., description="The repository slug or UUID (surrounded by curly-braces) that contains the deploy key."),
    workspace: str = Field(..., description="The workspace slug or UUID (surrounded by curly-braces) that owns the repository."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing deploy key in a repository, allowing the label and comment to be changed while keeping the same public key value."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesDeployKeysRequest(
            path=_models.PutRepositoriesDeployKeysRequestPath(key_id=key_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_deploy_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/deploy-keys/{key_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/deploy-keys/{key_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_deploy_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_deploy_key", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_deploy_key",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deployments
@mcp.tool()
async def delete_deploy_key(
    key_id: str = Field(..., description="The unique numeric identifier of the deploy key to delete."),
    repo_slug: str = Field(..., description="The repository slug or UUID that owns the deploy key. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID where the repository resides. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a deploy key from a repository, revoking its access. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesDeployKeysRequest(
            path=_models.DeleteRepositoriesDeployKeysRequestPath(key_id=key_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_deploy_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/deploy-keys/{key_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/deploy-keys/{key_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_deploy_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_deploy_key", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_deploy_key",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deployments
@mcp.tool()
async def list_deployments(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of all deployments for a specified repository. Returns deployment history and status information for the given workspace and repository."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugDeploymentsRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugDeploymentsRequestPath(workspace=workspace, repo_slug=repo_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_deployments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/deployments", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/deployments"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_deployments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_deployments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_deployments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deployments
@mcp.tool()
async def get_deployment(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that contains the deployment."),
    deployment_uuid: str = Field(..., description="The unique identifier (UUID) of the deployment to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves detailed information about a specific deployment in a repository. Use this to inspect the status, configuration, and metadata of a single deployment by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugDeploymentsByDeploymentUuidRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugDeploymentsByDeploymentUuidRequestPath(workspace=workspace, repo_slug=repo_slug, deployment_uuid=deployment_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_deployment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/deployments/{deployment_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/deployments/{deployment_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_deployment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_deployment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_deployment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def list_environment_variables(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
    environment_uuid: str = Field(..., description="The unique identifier of the deployment environment whose variables should be listed."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all deployment variables configured for a specific environment in a repository. Returns environment-level variables used during deployments."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesDeploymentsConfigEnvironmentsVariablesRequest(
            path=_models.GetRepositoriesDeploymentsConfigEnvironmentsVariablesRequestPath(workspace=workspace, repo_slug=repo_slug, environment_uuid=environment_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_environment_variables: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/deployments_config/environments/{environment_uuid}/variables", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/deployments_config/environments/{environment_uuid}/variables"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_environment_variables")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_environment_variables", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_environment_variables",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def create_environment_variable(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
    environment_uuid: str = Field(..., description="The unique identifier of the deployment environment in which the variable will be created."),
    body: _models.PostRepositoriesDeploymentsConfigEnvironmentsVariablesBody | None = Field(None, description="The variable definition to create, including its key, value, and whether it should be treated as secured (masked)."),
) -> dict[str, Any] | ToolResult:
    """Creates a new variable scoped to a specific deployment environment in a repository. Use this to define environment-level configuration or secrets for deployment pipelines."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesDeploymentsConfigEnvironmentsVariablesRequest(
            path=_models.PostRepositoriesDeploymentsConfigEnvironmentsVariablesRequestPath(workspace=workspace, repo_slug=repo_slug, environment_uuid=environment_uuid),
            body=_models.PostRepositoriesDeploymentsConfigEnvironmentsVariablesRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_environment_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/deployments_config/environments/{environment_uuid}/variables", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/deployments_config/environments/{environment_uuid}/variables"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_environment_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_environment_variable", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_environment_variable",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def update_environment_variable(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the workspace that owns the deployment environment."),
    environment_uuid: str = Field(..., description="The UUID of the deployment environment whose variable is being updated."),
    variable_uuid: str = Field(..., description="The UUID of the specific variable to update within the deployment environment."),
    body: _models.PutRepositoriesDeploymentsConfigEnvironmentsVariablesBody | None = Field(None, description="The request body containing the updated variable fields, such as key, value, or secured flag."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing deployment environment level variable for a specific environment in a repository. Use this to modify the key, value, or secured status of a previously created variable."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesDeploymentsConfigEnvironmentsVariablesRequest(
            path=_models.PutRepositoriesDeploymentsConfigEnvironmentsVariablesRequestPath(workspace=workspace, repo_slug=repo_slug, environment_uuid=environment_uuid, variable_uuid=variable_uuid),
            body=_models.PutRepositoriesDeploymentsConfigEnvironmentsVariablesRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_environment_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/deployments_config/environments/{environment_uuid}/variables/{variable_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/deployments_config/environments/{environment_uuid}/variables/{variable_uuid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_environment_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_environment_variable", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_environment_variable",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def delete_environment_variable(
    workspace: str = Field(..., description="The workspace identifier, either the slug (short name) or the UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the workspace."),
    environment_uuid: str = Field(..., description="The unique identifier (UUID) of the deployment environment from which the variable will be deleted."),
    variable_uuid: str = Field(..., description="The unique identifier (UUID) of the variable to permanently delete from the environment."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific variable from a deployment environment in a repository. This removes the variable and its value from the environment's configuration."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesDeploymentsConfigEnvironmentsVariablesRequest(
            path=_models.DeleteRepositoriesDeploymentsConfigEnvironmentsVariablesRequestPath(workspace=workspace, repo_slug=repo_slug, environment_uuid=environment_uuid, variable_uuid=variable_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_environment_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/deployments_config/environments/{environment_uuid}/variables/{variable_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/deployments_config/environments/{environment_uuid}/variables/{variable_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_environment_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_environment_variable", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_environment_variable",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commits
@mcp.tool()
async def get_repository_diff(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository within the workspace."),
    spec: str = Field(..., description="A single commit SHA or a two-commit range using double-dot notation to define the diff scope. For two-commit ranges, the first commit contains the changes to preview and the second represents the comparison target (note: opposite order from git diff)."),
    workspace: str = Field(..., description="The workspace slug or UUID that owns the repository."),
    context: int | None = Field(None, description="Number of context lines to include around each change in the diff, overriding the default of three lines."),
    path: str | None = Field(None, description="Restricts the diff output to a specific file path within the repository. This parameter may be repeated to filter on multiple paths."),
    ignore_whitespace: bool | None = Field(None, description="When true, whitespace differences are excluded from the diff output."),
    binary: bool | None = Field(None, description="When true, binary files are included in the diff output. Defaults to true if omitted."),
    renames: bool | None = Field(None, description="When true, rename detection is performed to identify moved or renamed files. Defaults to true if omitted."),
    topic: bool | None = Field(None, description="When true, returns a two-way three-dot diff showing changes between the source commit and the merge base of the source and destination commits. When false, returns a simple two-dot diff between source and destination. Defaults to true if omitted."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a raw git-style diff for a repository, either for a single commit against its first parent or between two commits using dot notation. Supports three-dot topic diffs, file path filtering, and whitespace/rename/binary options."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesDiffRequest(
            path=_models.GetRepositoriesDiffRequestPath(repo_slug=repo_slug, spec=spec, workspace=workspace),
            query=_models.GetRepositoriesDiffRequestQuery(context=context, path=path, ignore_whitespace=ignore_whitespace, binary=binary, renames=renames, topic=topic)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_diff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/diff/{spec}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/diff/{spec}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_diff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_diff", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_diff",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commits
@mcp.tool()
async def get_diffstat(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository within the workspace."),
    spec: str = Field(..., description="A single commit SHA or a commit range using double-dot notation to compare two commits. For two-commit specs, the first commit represents the source (changes to preview) and the second represents the destination (state to compare against)."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository."),
    ignore_whitespace: bool | None = Field(None, description="When true, whitespace-only changes are excluded from the diffstat output."),
    path: str | None = Field(None, description="Restricts the diffstat to one or more specific file paths; repeat this parameter to include multiple paths."),
    renames: bool | None = Field(None, description="Controls whether file rename detection is performed; defaults to true when omitted."),
    topic: bool | None = Field(None, description="When true, returns a three-dot diff between the source commit and the merge base of the source and destination commits. When false, returns a simple two-dot diff between the two commits."),
) -> dict[str, Any] | ToolResult:
    """Retrieves file-level change statistics for a commit or commit range, returning a record per modified path with the type of change and lines added or removed. Supports single-commit diffs against the first parent, two-commit diffs, and three-dot topic branch diffs."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesDiffstatRequest(
            path=_models.GetRepositoriesDiffstatRequestPath(repo_slug=repo_slug, spec=spec, workspace=workspace),
            query=_models.GetRepositoriesDiffstatRequestQuery(ignore_whitespace=ignore_whitespace, path=path, renames=renames, topic=topic)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_diffstat: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/diffstat/{spec}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/diffstat/{spec}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_diffstat")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_diffstat", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_diffstat",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Downloads
@mcp.tool()
async def list_download_artifacts(
    repo_slug: str = Field(..., description="The repository identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all download artifacts associated with a specific repository in a workspace. Returns a list of available download links for the repository."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugDownloadsRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugDownloadsRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_download_artifacts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/downloads", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/downloads"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_download_artifacts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_download_artifacts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_download_artifacts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Downloads
@mcp.tool()
async def upload_download_artifact(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Upload one or more download artifacts to a repository using a multipart/form-data POST request. If a file with the same name already exists, it will be replaced."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesDownloadsRequest(
            path=_models.PostRepositoriesDownloadsRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_download_artifact: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/downloads", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/downloads"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_download_artifact")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_download_artifact", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_download_artifact",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Downloads
@mcp.tool()
async def get_download_artifact(
    filename: str = Field(..., description="The exact filename of the download artifact to retrieve from the repository's downloads section."),
    repo_slug: str = Field(..., description="The repository identifier, either as a URL-friendly slug or as a UUID enclosed in curly braces."),
    workspace: str = Field(..., description="The workspace identifier, either as a URL-friendly slug or as a UUID enclosed in curly braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the actual file contents of a download artifact from a repository, redirecting to the file's direct download URL. Returns the raw file data rather than artifact metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugDownloadsByFilenameRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugDownloadsByFilenameRequestPath(filename=filename, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_download_artifact: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/downloads/{filename}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/downloads/{filename}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_download_artifact")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_download_artifact", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_download_artifact",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Downloads
@mcp.tool()
async def delete_download_artifact(
    filename: str = Field(..., description="The exact name of the download artifact file to delete, including its file extension."),
    repo_slug: str = Field(..., description="The repository identifier, either as a URL-friendly slug or as a UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace identifier, either as a URL-friendly slug or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific download artifact file from a repository. This action cannot be undone and removes the file from the repository's public downloads section."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesDownloadsRequest(
            path=_models.DeleteRepositoriesDownloadsRequestPath(filename=filename, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_download_artifact: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/downloads/{filename}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/downloads/{filename}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_download_artifact")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_download_artifact", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_download_artifact",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Branching model
@mcp.tool()
async def get_effective_branching_model(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that contains the repository. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the effective (currently applied) branching model for a repository, reflecting any inherited workspace-level settings combined with repository-specific overrides."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesEffectiveBranchingModelRequest(
            path=_models.GetRepositoriesEffectiveBranchingModelRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_effective_branching_model: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/effective-branching-model", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/effective-branching-model"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_effective_branching_model")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_effective_branching_model", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_effective_branching_model",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def list_effective_default_reviewers(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that contains the repository. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the effective default reviewers for a repository, combining reviewers defined at the repository level with those inherited from its parent project. These users are automatically added as reviewers on every new pull request created in the repository."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesEffectiveDefaultReviewersRequest(
            path=_models.GetRepositoriesEffectiveDefaultReviewersRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_effective_default_reviewers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/effective-default-reviewers", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/effective-default-reviewers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_effective_default_reviewers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_effective_default_reviewers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_effective_default_reviewers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deployments
@mcp.tool()
async def list_environments(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace whose environments will be listed."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all deployment environments configured for a specified repository within a workspace. Useful for inspecting available environments such as production, staging, or test."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugEnvironmentsRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugEnvironmentsRequestPath(workspace=workspace, repo_slug=repo_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_environments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/environments", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/environments"
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

# Tags: Deployments
@mcp.tool()
async def create_environment(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace where the environment will be created."),
    body: _models.PostRepositoriesEnvironmentsBody | None = Field(None, description="The request body containing the environment configuration details, such as name and environment type."),
) -> dict[str, Any] | ToolResult:
    """Creates a new deployment environment (e.g., production, staging, test) within a specified repository. Environments are used to manage deployment configurations and variables."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesEnvironmentsRequest(
            path=_models.PostRepositoriesEnvironmentsRequestPath(workspace=workspace, repo_slug=repo_slug),
            body=_models.PostRepositoriesEnvironmentsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/environments", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/environments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
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

# Tags: Deployments
@mcp.tool()
async def get_environment(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that contains the target environment."),
    environment_uuid: str = Field(..., description="The unique UUID of the deployment environment to retrieve, surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific deployment environment within a repository. Use this to inspect environment configuration, status, and metadata by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugEnvironmentsByEnvironmentUuidRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugEnvironmentsByEnvironmentUuidRequestPath(workspace=workspace, repo_slug=repo_slug, environment_uuid=environment_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/environments/{environment_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/environments/{environment_uuid}"
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

# Tags: Deployments
@mcp.tool()
async def delete_environment(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
    environment_uuid: str = Field(..., description="The unique UUID of the deployment environment to delete, surrounded by curly braces."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a deployment environment from a repository. This action cannot be undone and will remove all associated environment configuration."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesEnvironmentsRequest(
            path=_models.DeleteRepositoriesEnvironmentsRequestPath(workspace=workspace, repo_slug=repo_slug, environment_uuid=environment_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/environments/{environment_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/environments/{environment_uuid}"
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

# Tags: Deployments
@mcp.tool()
async def update_environment(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
    environment_uuid: str = Field(..., description="The unique identifier (UUID) of the deployment environment to update."),
) -> dict[str, Any] | ToolResult:
    """Apply configuration changes to a specific deployment environment in a repository. Use this to modify environment settings such as variables or deployment rules."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesEnvironmentsChangesRequest(
            path=_models.PostRepositoriesEnvironmentsChangesRequestPath(workspace=workspace, repo_slug=repo_slug, environment_uuid=environment_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_environment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/environments/{environment_uuid}/changes", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/environments/{environment_uuid}/changes"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_environment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_environment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_environment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Source, Repositories
@mcp.tool()
async def list_file_history(
    commit: str = Field(..., description="The SHA1 hash of the commit to start the file history from."),
    path: str = Field(..., description="The path to the file within the repository whose commit history you want to retrieve."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository; UUIDs must be surrounded by curly braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace; UUIDs must be surrounded by curly braces."),
    renames: str | None = Field(None, description="Controls whether Bitbucket follows the file across renames when traversing history; defaults to true, set to false to disable rename tracking."),
    q: str | None = Field(None, description="A filter expression to narrow down the returned commits using Bitbucket's filtering and sorting syntax."),
    sort: str | None = Field(None, description="The name of a response property to sort results by, using Bitbucket's filtering and sorting syntax."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of commits that modified a specific file in a repository, returned in reverse chronological order. Supports rename tracking, filtering, and sorting to precisely scope the results."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesFilehistoryRequest(
            path=_models.GetRepositoriesFilehistoryRequestPath(commit=commit, path=path, repo_slug=repo_slug, workspace=workspace),
            query=_models.GetRepositoriesFilehistoryRequestQuery(renames=renames, q=q, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/filehistory/{commit}/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/filehistory/{commit}/{path}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories
@mcp.tool()
async def list_repository_forks(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository whose forks should be listed. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace that contains the repository. UUIDs must be surrounded by curly-braces."),
    role: Literal["admin", "contributor", "member", "owner"] | None = Field(None, description="Filters returned forks based on the authenticated user's role: member (explicit read access), contributor (explicit write access), admin (explicit administrator access), or owner (repositories owned by the current user)."),
    q: str | None = Field(None, description="A query string to filter and narrow down the list of returned forks using Bitbucket's filtering and sorting syntax."),
    sort: str | None = Field(None, description="The field name by which the returned fork results should be sorted, following Bitbucket's filtering and sorting syntax."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all forks for a specified repository in a given workspace. Results can be filtered by the authenticated user's role, a query string, and sorted by a specified field."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesForksRequest(
            path=_models.GetRepositoriesForksRequestPath(repo_slug=repo_slug, workspace=workspace),
            query=_models.GetRepositoriesForksRequestQuery(role=role, q=q, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_forks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/forks", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/forks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_forks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_forks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_forks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories
@mcp.tool()
async def fork_repository(
    repo_slug: str = Field(..., description="The slug or UUID of the repository to fork. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The slug or UUID of the workspace that owns the source repository. UUIDs must be surrounded by curly-braces."),
    body: _models.Repository | None = Field(None, description="Optional request body following the repository JSON schema to configure the fork. Must include a workspace slug to specify the fork destination, and a name to distinguish it from the parent. Overridable fields include name, description, fork_policy, language, mainbranch, is_private, has_issues, has_wiki, and project. Fields scm, parent, and full_name cannot be overridden."),
) -> dict[str, Any] | ToolResult:
    """Creates a new fork of the specified repository into a target workspace, optionally overriding properties such as name, description, visibility, and issue tracker settings. The fork inherits most parent properties by default, but scm, parent, and full_name cannot be changed."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesForksRequest(
            path=_models.PostRepositoriesForksRequestPath(repo_slug=repo_slug, workspace=workspace),
            body=_models.PostRepositoriesForksRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for fork_repository: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/forks", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/forks"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("fork_repository")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("fork_repository", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="fork_repository",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories, Webhooks
@mcp.tool()
async def list_repository_webhooks(
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) or the repository UUID enclosed in curly-braces, uniquely identifying the target repository within the workspace."),
    workspace: str = Field(..., description="The workspace slug (ID) or the workspace UUID enclosed in curly-braces, identifying the workspace that owns the repository."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all webhooks installed on a specific repository. Useful for auditing or managing event-driven integrations configured for the repo."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugHooksRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugHooksRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_webhooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/hooks", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/hooks"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_webhooks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_webhooks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_webhooks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories, Webhooks
@mcp.tool()
async def get_repository_webhook(
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) or the repository UUID surrounded by curly-braces."),
    uid: str = Field(..., description="The unique identifier of the installed webhook to retrieve."),
    workspace: str = Field(..., description="The workspace slug (ID) or the workspace UUID surrounded by curly-braces that owns the repository."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific webhook installed on a repository, identified by its unique ID. Use this to inspect webhook configuration, events, and status for a given repository."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugHooksByUidRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugHooksByUidRequestPath(repo_slug=repo_slug, uid=uid, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/hooks/{uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/hooks/{uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_webhook", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_webhook",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories, Webhooks
@mcp.tool()
async def update_repository_webhook(
    repo_slug: str = Field(..., description="The repository identifier, either its slug (short name) or its UUID surrounded by curly-braces."),
    uid: str = Field(..., description="The unique identifier of the installed webhook subscription to update."),
    workspace: str = Field(..., description="The workspace identifier, either its slug or its UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing webhook subscription on a repository, allowing mutation of its description, URL, secret, active status, and events. The secret field controls HMAC signature generation for the X-Hub-Signature header; omit it to leave unchanged, or pass null to remove it."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesHooksRequest(
            path=_models.PutRepositoriesHooksRequestPath(repo_slug=repo_slug, uid=uid, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_repository_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/hooks/{uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/hooks/{uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_repository_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_repository_webhook", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_repository_webhook",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories, Webhooks
@mcp.tool()
async def delete_repository_webhook(
    repo_slug: str = Field(..., description="The repository identifier, either as a slug (URL-friendly name) or as a UUID surrounded by curly-braces."),
    uid: str = Field(..., description="The unique identifier of the installed webhook subscription to delete."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a specific webhook subscription from a repository, stopping all future event deliveries to the configured endpoint."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesHooksRequest(
            path=_models.DeleteRepositoriesHooksRequestPath(repo_slug=repo_slug, uid=uid, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_repository_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/hooks/{uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/hooks/{uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_repository_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_repository_webhook", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_repository_webhook",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commits
@mcp.tool()
async def get_merge_base(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces."),
    revspec: str = Field(..., description="A range of exactly two commits specified using double-dot notation, identifying the two commits whose common ancestor should be found."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID that owns the repository. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Finds the best common ancestor commit between two commits in a repository, useful for determining the divergence point of branches or commits. If multiple best common ancestors exist, one is returned arbitrarily."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesMergeBaseRequest(
            path=_models.GetRepositoriesMergeBaseRequestPath(repo_slug=repo_slug, revspec=revspec, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_merge_base: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/merge-base/{revspec}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/merge-base/{revspec}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_merge_base")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_merge_base", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_merge_base",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories
@mcp.tool()
async def get_repository_override_settings(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that contains the repository. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the inheritance state for a repository's settings, indicating which settings are overridden at the repository level versus inherited from the workspace."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesOverrideSettingsRequest(
            path=_models.GetRepositoriesOverrideSettingsRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_override_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/override-settings", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/override-settings"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_override_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_override_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_override_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories
@mcp.tool()
async def set_repository_override_settings(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that contains the repository. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Configures the inheritance state for a repository's settings, determining which settings are overridden at the repository level versus inherited from the workspace."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesOverrideSettingsRequest(
            path=_models.PutRepositoriesOverrideSettingsRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_repository_override_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/override-settings", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/override-settings"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_repository_override_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_repository_override_settings", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_repository_override_settings",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Commits
@mcp.tool()
async def get_repository_patch(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces."),
    spec: str = Field(..., description="A single commit SHA or a two-commit range using double-dot notation to generate a patch series. For a range, the first commit is the source and the second is the destination."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a raw patch for a single commit (diffed against its first parent) or a patch series for a two-commit range, including commit headers such as author and message. Unlike diffs, patches carry full commit metadata and are returned as plain text in the repository's native encoding."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPatchRequest(
            path=_models.GetRepositoriesPatchRequestPath(repo_slug=repo_slug, spec=spec, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_patch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/patch/{spec}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/patch/{spec}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_patch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_patch", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_patch",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories
@mcp.tool()
async def list_repository_group_permissions(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of explicit group permissions configured for a specific repository. Only explicitly set group permissions are returned; inherited or default permissions are not included."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigGroupsRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigGroupsRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_group_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/permissions-config/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/permissions-config/groups"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_group_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_group_permissions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_group_permissions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories
@mcp.tool()
async def get_repository_group_permission(
    group_slug: str = Field(..., description="The slug identifier of the group whose repository permission is being retrieved."),
    repo_slug: str = Field(..., description="The repository slug or UUID (surrounded by curly-braces) that identifies the target repository."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID (surrounded by curly-braces) that contains the repository."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the explicit permission level assigned to a specific group for a given repository. Requires admin permission on the repository; returns one of: admin, write, read, or none."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigGroupsByGroupSlugRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigGroupsByGroupSlugRequestPath(group_slug=group_slug, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_group_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/permissions-config/groups/{group_slug}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/permissions-config/groups/{group_slug}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_group_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_group_permission", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_group_permission",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories
@mcp.tool()
async def list_repository_user_permissions(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of explicit user-level permissions configured for a specific repository. Only directly assigned user permissions are returned; inherited or group-based permissions are not included."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigUsersRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigUsersRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_user_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/permissions-config/users", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/permissions-config/users"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_user_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_user_permissions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_user_permissions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories
@mcp.tool()
async def get_user_repository_permission(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUID format must be surrounded by curly-braces."),
    selected_user_id: str = Field(..., description="The unique identifier of the user whose permission is being retrieved. Accepts either an Atlassian Account ID or a UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID that contains the repository. UUID format must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the explicit permission level assigned to a specific user for a given repository. Requires admin permission on the repository; returns one of: admin, write, read, or none."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigUsersBySelectedUserIdRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPermissionsConfigUsersBySelectedUserIdRequestPath(repo_slug=repo_slug, selected_user_id=selected_user_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_repository_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/permissions-config/users/{selected_user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/permissions-config/users/{selected_user_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_repository_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_repository_permission", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_repository_permission",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories
@mcp.tool()
async def delete_user_repository_permission(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository within the workspace."),
    selected_user_id: str = Field(..., description="The account identifier for the user whose repository permission will be deleted, provided as either an Atlassian Account ID or a UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace identifier, provided as either the workspace slug or a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Deletes an explicit user-level permission for a specific repository, removing any custom access grant assigned to that user. Requires admin permission on the repository and authentication via app passwords."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesPermissionsConfigUsersRequest(
            path=_models.DeleteRepositoriesPermissionsConfigUsersRequestPath(repo_slug=repo_slug, selected_user_id=selected_user_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user_repository_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/permissions-config/users/{selected_user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/permissions-config/users/{selected_user_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_user_repository_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_user_repository_permission", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_user_repository_permission",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def list_pipelines(
    workspace: str = Field(..., description="The workspace identifier, either the slug (short name) or the UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
    creator_uuid: str | None = Field(None, alias="creator.uuid", description="Filter pipelines to only those created by the user with this UUID."),
    target_ref_type: Literal["BRANCH", "TAG", "ANNOTATED_TAG"] | None = Field(None, alias="target.ref_type", description="Filter pipelines by the type of Git reference that triggered them. Must be one of BRANCH, TAG, or ANNOTATED_TAG."),
    target_ref_name: str | None = Field(None, alias="target.ref_name", description="Filter pipelines by the exact name of the Git reference (branch name, tag name, etc.) that triggered them."),
    target_branch: str | None = Field(None, alias="target.branch", description="Filter pipelines by the name of the branch that triggered them."),
    target_commit_hash: str | None = Field(None, alias="target.commit.hash", description="Filter pipelines by the commit hash (revision) that triggered them."),
    target_selector_pattern: str | None = Field(None, alias="target.selector.pattern", description="Filter pipelines by the pipeline configuration pattern (e.g., a custom pipeline name pattern)."),
    target_selector_type: Literal["BRANCH", "TAG", "CUSTOM", "PULLREQUESTS", "DEFAULT"] | None = Field(None, alias="target.selector.type", description="Filter pipelines by their selector type, indicating the category of pipeline. Must be one of BRANCH, TAG, CUSTOM, PULLREQUESTS, or DEFAULT."),
    created_on: str | None = Field(None, description="Filter pipelines by their creation date and time, provided in ISO 8601 date-time format."),
    trigger_type: Literal["PUSH", "MANUAL", "SCHEDULED", "PARENT_STEP"] | None = Field(None, description="Filter pipelines by what triggered them. Must be one of PUSH, MANUAL, SCHEDULED, or PARENT_STEP."),
    status: Literal["PARSING", "PENDING", "PAUSED", "HALTED", "BUILDING", "ERROR", "PASSED", "FAILED", "STOPPED", "UNKNOWN"] | None = Field(None, description="Filter pipelines by their current execution status. Must be one of PARSING, PENDING, PAUSED, HALTED, BUILDING, ERROR, PASSED, FAILED, STOPPED, or UNKNOWN."),
    sort: Literal["creator.uuid", "created_on", "run_creation_date"] | None = Field(None, description="The field by which to sort the returned pipelines. Must be one of creator.uuid, created_on, or run_creation_date."),
    page: str | None = Field(None, description="The page number to retrieve in the paginated result set, starting at 1."),
    pagelen: str | None = Field(None, description="The maximum number of pipeline results to return per page, between 1 and 100."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of pipelines for a specific repository, with support for filtering by branch, commit, status, trigger type, and more, as well as sorting of results."""

    _page = _parse_int(page)
    _pagelen = _parse_int(pagelen)

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPipelinesRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPipelinesRequestPath(workspace=workspace, repo_slug=repo_slug),
            query=_models.GetRepositoriesByWorkspaceByRepoSlugPipelinesRequestQuery(creator_uuid=creator_uuid, target_ref_type=target_ref_type, target_ref_name=target_ref_name, target_branch=target_branch, target_commit_hash=target_commit_hash, target_selector_pattern=target_selector_pattern, target_selector_type=target_selector_type, created_on=created_on, trigger_type=trigger_type, status=status, sort=sort, page=_page, pagelen=_pagelen)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pipelines: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines"
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

# Tags: Pipelines
@mcp.tool()
async def trigger_pipeline(
    workspace: str = Field(..., description="The workspace identifier — either the slug (short name) or the UUID surrounded by curly braces — that owns the repository."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) or identifier within the workspace where the pipeline will be triggered."),
    body: _models.PostRepositoriesPipelinesBody | None = Field(None, description="The pipeline trigger payload defining the target and optional variables. The target type determines the trigger mode: use 'pipeline_ref_target' for branch or tag triggers, 'pipeline_commit_target' for a specific commit with a custom selector, or 'pipeline_pullrequest_target' for pull request pipelines. Optionally include a 'variables' array of key-value pairs (with optional 'secured' flag) to inject build-time variables into custom pipelines."),
) -> dict[str, Any] | ToolResult:
    """Creates and initiates a pipeline run for a repository, supporting multiple trigger modes including branch-based, commit-specific, custom selector, pull request, and variable-injected pipelines as defined in the repository's bitbucket-pipelines.yml file."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesPipelinesRequest(
            path=_models.PostRepositoriesPipelinesRequestPath(workspace=workspace, repo_slug=repo_slug),
            body=_models.PostRepositoriesPipelinesRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for trigger_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
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

# Tags: Pipelines
@mcp.tool()
async def list_pipeline_caches(
    workspace: str = Field(..., description="The slug or UUID of the workspace that owns the repository."),
    repo_slug: str = Field(..., description="The slug or UUID of the repository whose pipeline caches are being listed."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all pipeline caches configured for a repository, providing visibility into cached dependencies and build artifacts used to speed up pipeline runs."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPipelinesConfigCachesRequest(
            path=_models.GetRepositoriesPipelinesConfigCachesRequestPath(workspace=workspace, repo_slug=repo_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pipeline_caches: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines-config/caches", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines-config/caches"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pipeline_caches")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pipeline_caches", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pipeline_caches",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def delete_pipeline_caches(
    workspace: str = Field(..., description="The workspace slug or UUID identifying the account that owns the repository."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository whose pipeline caches will be deleted."),
    name: str = Field(..., description="The name of the pipeline cache to delete; all versions matching this name will be removed."),
) -> dict[str, Any] | ToolResult:
    """Delete all cached versions for a specific pipeline cache by name in a repository. This removes the named cache entries from the repository's pipelines configuration."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesForWorkspaceForRepoSlugPipelinesConfigCachesRequest(
            path=_models.DeleteRepositoriesForWorkspaceForRepoSlugPipelinesConfigCachesRequestPath(workspace=workspace, repo_slug=repo_slug),
            query=_models.DeleteRepositoriesForWorkspaceForRepoSlugPipelinesConfigCachesRequestQuery(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_pipeline_caches: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines-config/caches", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines-config/caches"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_pipeline_caches")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_pipeline_caches", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_pipeline_caches",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def delete_pipeline_cache(
    workspace: str = Field(..., description="The workspace slug or UUID identifying the account that owns the repository."),
    repo_slug: str = Field(..., description="The repository slug identifying the repository whose pipeline cache will be deleted."),
    cache_uuid: str = Field(..., description="The unique identifier (UUID) of the pipeline cache to delete."),
) -> dict[str, Any] | ToolResult:
    """Deletes a specific pipeline cache from a repository, freeing up cached resources associated with the given cache UUID."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesForWorkspaceForRepoSlugPipelinesConfigCachesForCacheUuidRequest(
            path=_models.DeleteRepositoriesForWorkspaceForRepoSlugPipelinesConfigCachesForCacheUuidRequestPath(workspace=workspace, repo_slug=repo_slug, cache_uuid=cache_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_pipeline_cache: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines-config/caches/{cache_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines-config/caches/{cache_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_pipeline_cache")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_pipeline_cache", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_pipeline_cache",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def get_pipeline_cache_content_uri(
    workspace: str = Field(..., description="The slug or UUID of the Bitbucket workspace that owns the repository."),
    repo_slug: str = Field(..., description="The slug or UUID of the repository containing the pipeline cache."),
    cache_uuid: str = Field(..., description="The unique identifier (UUID) of the pipeline cache whose content URI you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the download URI for the content of a specific pipeline cache in a repository. Use this URI to access or download the cached build artifacts."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPipelinesConfigCachesContentUriRequest(
            path=_models.GetRepositoriesPipelinesConfigCachesContentUriRequestPath(workspace=workspace, repo_slug=repo_slug, cache_uuid=cache_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pipeline_cache_content_uri: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines-config/caches/{cache_uuid}/content-uri", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines-config/caches/{cache_uuid}/content-uri"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pipeline_cache_content_uri")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pipeline_cache_content_uri", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pipeline_cache_content_uri",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def list_repository_runners(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all pipeline runners configured for a specific repository. Runners are used to execute Bitbucket Pipelines builds within the given workspace and repository."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigRunnersRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigRunnersRequestPath(workspace=workspace, repo_slug=repo_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_runners: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines-config/runners", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines-config/runners"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_runners")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_runners", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_runners",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def create_repository_runner(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace where the runner will be created."),
) -> dict[str, Any] | ToolResult:
    """Creates a new runner for a specific repository in Bitbucket Pipelines, enabling custom build infrastructure to be registered and used for pipeline executions within that repository."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesPipelinesConfigRunnersRequest(
            path=_models.PostRepositoriesPipelinesConfigRunnersRequestPath(workspace=workspace, repo_slug=repo_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_repository_runner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines-config/runners", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines-config/runners"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_repository_runner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_repository_runner", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_repository_runner",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def get_repository_runner(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace."),
    runner_uuid: str = Field(..., description="The unique UUID of the runner to retrieve, used to identify a specific Pipelines runner within the repository."),
) -> dict[str, Any] | ToolResult:
    """Retrieves details of a specific Pipelines runner configured for a repository, identified by its UUID."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigRunnersByRunnerUuidRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigRunnersByRunnerUuidRequestPath(workspace=workspace, repo_slug=repo_slug, runner_uuid=runner_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_runner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines-config/runners/{runner_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines-config/runners/{runner_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_runner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_runner", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_runner",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def update_repository_runner(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
    runner_uuid: str = Field(..., description="The unique identifier (UUID) of the runner to update, surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Updates the configuration of a specific runner associated with a repository. Identifies the target runner by its UUID within the given workspace and repository."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesPipelinesConfigRunnersRequest(
            path=_models.PutRepositoriesPipelinesConfigRunnersRequestPath(workspace=workspace, repo_slug=repo_slug, runner_uuid=runner_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_repository_runner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines-config/runners/{runner_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines-config/runners/{runner_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_repository_runner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_repository_runner", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_repository_runner",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def delete_repository_runner(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
    runner_uuid: str = Field(..., description="The unique UUID of the runner to delete, used to precisely identify the target runner within the repository's Pipelines configuration."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a specific runner from a repository's Pipelines configuration. The runner is identified by its UUID and will no longer be available for pipeline jobs in that repository."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesPipelinesConfigRunnersRequest(
            path=_models.DeleteRepositoriesPipelinesConfigRunnersRequestPath(workspace=workspace, repo_slug=repo_slug, runner_uuid=runner_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_repository_runner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines-config/runners/{runner_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines-config/runners/{runner_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_repository_runner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_repository_runner", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_repository_runner",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def get_pipeline(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace."),
    pipeline_uuid: str = Field(..., description="The unique UUID of the pipeline run to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific pipeline run within a repository, including its status, steps, and configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidRequestPath(workspace=workspace, repo_slug=repo_slug, pipeline_uuid=pipeline_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}"
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

# Tags: Pipelines
@mcp.tool()
async def list_pipeline_steps(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that contains the pipeline."),
    pipeline_uuid: str = Field(..., description="The unique UUID of the pipeline whose steps are to be listed, formatted as a standard UUID string."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all steps for a specified pipeline in a repository, providing visibility into each stage of the pipeline's execution."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidStepsRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidStepsRequestPath(workspace=workspace, repo_slug=repo_slug, pipeline_uuid=pipeline_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pipeline_steps: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}/steps", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}/steps"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pipeline_steps")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pipeline_steps", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pipeline_steps",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def get_pipeline_step(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug, which is the URL-friendly name of the repository within the specified workspace."),
    pipeline_uuid: str = Field(..., description="The unique identifier (UUID) of the pipeline whose step is being retrieved."),
    step_uuid: str = Field(..., description="The unique identifier (UUID) of the specific step within the pipeline to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific step within a pipeline, including its status, timing, and configuration. Useful for monitoring or inspecting individual steps of a CI/CD pipeline run."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidStepsByStepUuidRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPipelinesByPipelineUuidStepsByStepUuidRequestPath(workspace=workspace, repo_slug=repo_slug, pipeline_uuid=pipeline_uuid, step_uuid=step_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pipeline_step: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}/steps/{step_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}/steps/{step_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pipeline_step")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pipeline_step", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pipeline_step",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def get_pipeline_step_log(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug, which is the URL-friendly name of the repository within the workspace."),
    pipeline_uuid: str = Field(..., description="The unique identifier (UUID) of the pipeline whose step log is being retrieved."),
    step_uuid: str = Field(..., description="The unique identifier (UUID) of the specific pipeline step whose log file should be returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the full log file for a specific step within a pipeline. Supports HTTP Range requests to efficiently stream or paginate potentially large log files."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPipelinesStepsLogRequest(
            path=_models.GetRepositoriesPipelinesStepsLogRequestPath(workspace=workspace, repo_slug=repo_slug, pipeline_uuid=pipeline_uuid, step_uuid=step_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pipeline_step_log: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}/steps/{step_uuid}/log", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}/steps/{step_uuid}/log"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pipeline_step_log")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pipeline_step_log", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pipeline_step_log",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def get_pipeline_step_log_container(
    workspace: str = Field(..., description="The workspace identifier, either as a slug or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug identifying the target repository within the workspace."),
    pipeline_uuid: str = Field(..., description="The UUID of the pipeline whose step logs are being retrieved."),
    step_uuid: str = Field(..., description="The UUID of the step within the pipeline whose container logs are being retrieved."),
    log_uuid: str = Field(..., description="The UUID identifying which container log to retrieve — use the step UUID for the main build container, or the service container UUID for a service container."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the log file for a build container or service container within a specific pipeline step. Supports HTTP Range requests to efficiently handle large log files."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPipelinesStepsLogsRequest(
            path=_models.GetRepositoriesPipelinesStepsLogsRequestPath(workspace=workspace, repo_slug=repo_slug, pipeline_uuid=pipeline_uuid, step_uuid=step_uuid, log_uuid=log_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pipeline_step_log_container: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}/steps/{step_uuid}/logs/{log_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}/steps/{step_uuid}/logs/{log_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pipeline_step_log_container")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pipeline_step_log_container", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pipeline_step_log_container",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def get_pipeline_step_test_report(
    workspace: str = Field(..., description="The workspace identifier, either the slug (short name) or the UUID enclosed in curly braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace."),
    pipeline_uuid: str = Field(..., description="The UUID of the pipeline whose step test reports are being retrieved."),
    step_uuid: str = Field(..., description="The UUID of the specific pipeline step for which test reports are being retrieved."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a summary of test reports for a specific step within a pipeline, providing an overview of test results such as pass/fail counts and coverage metrics."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPipelinesStepsTestReportsRequest(
            path=_models.GetRepositoriesPipelinesStepsTestReportsRequestPath(workspace=workspace, repo_slug=repo_slug, pipeline_uuid=pipeline_uuid, step_uuid=step_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pipeline_step_test_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}/steps/{step_uuid}/test_reports", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}/steps/{step_uuid}/test_reports"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pipeline_step_test_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pipeline_step_test_report", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pipeline_step_test_report",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def list_pipeline_step_test_cases(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
    pipeline_uuid: str = Field(..., description="The unique identifier (UUID) of the pipeline whose step test cases are being retrieved."),
    step_uuid: str = Field(..., description="The unique identifier (UUID) of the pipeline step whose test cases are being retrieved."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all test cases from the test report for a specific step within a pipeline. Useful for inspecting individual test outcomes after a CI pipeline run."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPipelinesStepsTestReportsTestCasesRequest(
            path=_models.GetRepositoriesPipelinesStepsTestReportsTestCasesRequestPath(workspace=workspace, repo_slug=repo_slug, pipeline_uuid=pipeline_uuid, step_uuid=step_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pipeline_step_test_cases: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}/steps/{step_uuid}/test_reports/test_cases", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}/steps/{step_uuid}/test_reports/test_cases"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pipeline_step_test_cases")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pipeline_step_test_cases", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pipeline_step_test_cases",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def list_test_case_reasons(
    workspace: str = Field(..., description="The workspace identifier, either as a slug or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug identifying the target repository within the workspace."),
    pipeline_uuid: str = Field(..., description="The UUID of the pipeline containing the step and test case."),
    step_uuid: str = Field(..., description="The UUID of the pipeline step that contains the test case."),
    test_case_uuid: str = Field(..., description="The UUID of the specific test case whose reasons are being retrieved."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the reasons (output details) for a specific test case within a pipeline step, providing diagnostic information such as failure messages or stack traces."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPipelinesStepsTestReportsTestCasesTestCaseReasonsRequest(
            path=_models.GetRepositoriesPipelinesStepsTestReportsTestCasesTestCaseReasonsRequestPath(workspace=workspace, repo_slug=repo_slug, pipeline_uuid=pipeline_uuid, step_uuid=step_uuid, test_case_uuid=test_case_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_test_case_reasons: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}/steps/{step_uuid}/test_reports/test_cases/{test_case_uuid}/test_case_reasons", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}/steps/{step_uuid}/test_reports/test_cases/{test_case_uuid}/test_case_reasons"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_test_case_reasons")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_test_case_reasons", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_test_case_reasons",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def stop_pipeline(
    workspace: str = Field(..., description="The workspace identifier, either the workspace slug (short name) or the workspace UUID enclosed in curly braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that contains the pipeline to stop."),
    pipeline_uuid: str = Field(..., description="The unique identifier (UUID) of the pipeline to stop, enclosed in curly braces."),
) -> dict[str, Any] | ToolResult:
    """Stops a running pipeline and all of its in-progress steps that have not yet completed. Use this to immediately halt pipeline execution within a specific repository."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesPipelinesStopPipelineRequest(
            path=_models.PostRepositoriesPipelinesStopPipelineRequestPath(workspace=workspace, repo_slug=repo_slug, pipeline_uuid=pipeline_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for stop_pipeline: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}/stopPipeline", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines/{pipeline_uuid}/stopPipeline"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("stop_pipeline")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("stop_pipeline", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="stop_pipeline",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def get_pipelines_config(
    workspace: str = Field(..., description="The slug or UUID of the workspace that owns the repository."),
    repo_slug: str = Field(..., description="The slug or UUID of the repository whose Pipelines configuration is being retrieved."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the Pipelines configuration for a specific repository, including settings that control how pipelines are enabled and executed."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPipelinesConfigRequest(
            path=_models.GetRepositoriesPipelinesConfigRequestPath(workspace=workspace, repo_slug=repo_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pipelines_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pipelines_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pipelines_config", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pipelines_config",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def set_pipeline_next_build_number(
    workspace: str = Field(..., description="The workspace identifier, either as a slug or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug identifying which repository's pipeline build number sequence to update."),
    body: _models.PutRepositoriesPipelinesConfigBuildNumberBody | None = Field(None, description="Request body containing the next build number to assign. Must be strictly higher than the current latest build number for this repository."),
) -> dict[str, Any] | ToolResult:
    """Updates the next build number to be assigned to a pipeline in the specified repository. The configured value must be strictly greater than the current latest build number."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesPipelinesConfigBuildNumberRequest(
            path=_models.PutRepositoriesPipelinesConfigBuildNumberRequestPath(workspace=workspace, repo_slug=repo_slug),
            body=_models.PutRepositoriesPipelinesConfigBuildNumberRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_pipeline_next_build_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/build_number", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/build_number"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_pipeline_next_build_number")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_pipeline_next_build_number", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_pipeline_next_build_number",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def list_pipeline_schedules(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all configured pipeline schedules for a given repository. Returns the list of schedules that define when pipelines are automatically triggered."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSchedulesRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSchedulesRequestPath(workspace=workspace, repo_slug=repo_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pipeline_schedules: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/schedules", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/schedules"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pipeline_schedules")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pipeline_schedules", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pipeline_schedules",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def create_pipeline_schedule(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the workspace for which the pipeline schedule will be created."),
    body: _models.PostRepositoriesPipelinesConfigSchedulesBody | None = Field(None, description="The schedule configuration payload defining the timing, target branch, and other schedule properties for the pipeline."),
) -> dict[str, Any] | ToolResult:
    """Creates a new pipeline schedule for the specified repository, allowing automated pipeline runs at defined intervals or times."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesPipelinesConfigSchedulesRequest(
            path=_models.PostRepositoriesPipelinesConfigSchedulesRequestPath(workspace=workspace, repo_slug=repo_slug),
            body=_models.PostRepositoriesPipelinesConfigSchedulesRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_pipeline_schedule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/schedules", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/schedules"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_pipeline_schedule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_pipeline_schedule", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_pipeline_schedule",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def get_pipeline_schedule(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace."),
    schedule_uuid: str = Field(..., description="The UUID that uniquely identifies the pipeline schedule to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific pipeline schedule by its UUID for a given repository. Returns the full schedule configuration including timing and status details."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSchedulesByScheduleUuidRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSchedulesByScheduleUuidRequestPath(workspace=workspace, repo_slug=repo_slug, schedule_uuid=schedule_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pipeline_schedule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/schedules/{schedule_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/schedules/{schedule_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pipeline_schedule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pipeline_schedule", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pipeline_schedule",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def update_pipeline_schedule(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
    schedule_uuid: str = Field(..., description="The unique identifier (UUID) of the pipeline schedule to update."),
    body: _models.PutRepositoriesPipelinesConfigSchedulesBody | None = Field(None, description="The updated schedule configuration payload containing the fields to modify on the existing schedule."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing pipeline schedule for a repository. Use this to modify the timing or configuration of a scheduled pipeline run."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesPipelinesConfigSchedulesRequest(
            path=_models.PutRepositoriesPipelinesConfigSchedulesRequestPath(workspace=workspace, repo_slug=repo_slug, schedule_uuid=schedule_uuid),
            body=_models.PutRepositoriesPipelinesConfigSchedulesRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_pipeline_schedule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/schedules/{schedule_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/schedules/{schedule_uuid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_pipeline_schedule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_pipeline_schedule", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_pipeline_schedule",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def delete_pipeline_schedule(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
    schedule_uuid: str = Field(..., description="The unique UUID of the pipeline schedule to delete, used to identify the specific schedule within the repository."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific pipeline schedule from a repository. This removes the scheduled trigger and prevents any future automated pipeline runs associated with it."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesPipelinesConfigSchedulesRequest(
            path=_models.DeleteRepositoriesPipelinesConfigSchedulesRequestPath(workspace=workspace, repo_slug=repo_slug, schedule_uuid=schedule_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_pipeline_schedule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/schedules/{schedule_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/schedules/{schedule_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_pipeline_schedule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_pipeline_schedule", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_pipeline_schedule",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def list_schedule_executions(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace."),
    schedule_uuid: str = Field(..., description="The UUID of the pipeline schedule whose executions should be retrieved."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the execution history for a specific pipeline schedule in a repository. Returns a list of past executions triggered by the given schedule."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPipelinesConfigSchedulesExecutionsRequest(
            path=_models.GetRepositoriesPipelinesConfigSchedulesExecutionsRequestPath(workspace=workspace, repo_slug=repo_slug, schedule_uuid=schedule_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_schedule_executions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/schedules/{schedule_uuid}/executions", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/schedules/{schedule_uuid}/executions"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_schedule_executions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_schedule_executions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_schedule_executions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def get_repository_ssh_key_pair(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the SSH key pair configured for a repository's pipeline, returning only the public key. The private key is write-only and is never exposed through the API or logs."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPipelinesConfigSshKeyPairRequest(
            path=_models.GetRepositoriesPipelinesConfigSshKeyPairRequestPath(workspace=workspace, repo_slug=repo_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_ssh_key_pair: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/key_pair", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/key_pair"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_ssh_key_pair")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_ssh_key_pair", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_ssh_key_pair",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def set_repository_ssh_key_pair(
    workspace: str = Field(..., description="The workspace identifier, either the slug (short name) or the UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
    body: _models.PutRepositoriesPipelinesConfigSshKeyPairBody | None = Field(None, description="The SSH key pair payload containing the public and private key to set for the repository's pipeline configuration."),
) -> dict[str, Any] | ToolResult:
    """Creates or updates the SSH key pair for a repository's pipeline configuration. The private key will be set as the default SSH identity in the build container."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesPipelinesConfigSshKeyPairRequest(
            path=_models.PutRepositoriesPipelinesConfigSshKeyPairRequestPath(workspace=workspace, repo_slug=repo_slug),
            body=_models.PutRepositoriesPipelinesConfigSshKeyPairRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_repository_ssh_key_pair: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/key_pair", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/key_pair"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_repository_ssh_key_pair")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_repository_ssh_key_pair", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_repository_ssh_key_pair",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def delete_repository_ssh_key_pair(
    workspace: str = Field(..., description="The workspace identifier, either the slug (short name) or the UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
) -> dict[str, Any] | ToolResult:
    """Deletes the SSH key pair configured for a repository's pipelines. This removes both the public and private keys associated with the repository's pipeline SSH configuration."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesPipelinesConfigSshKeyPairRequest(
            path=_models.DeleteRepositoriesPipelinesConfigSshKeyPairRequestPath(workspace=workspace, repo_slug=repo_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_repository_ssh_key_pair: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/key_pair", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/key_pair"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_repository_ssh_key_pair")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_repository_ssh_key_pair", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_repository_ssh_key_pair",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def list_pipeline_ssh_known_hosts(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all SSH known hosts configured at the repository level for Pipelines. Known hosts are used to verify remote server identities during pipeline SSH connections."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSshKnownHostsRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSshKnownHostsRequestPath(workspace=workspace, repo_slug=repo_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pipeline_ssh_known_hosts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/known_hosts", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/known_hosts"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pipeline_ssh_known_hosts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pipeline_ssh_known_hosts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pipeline_ssh_known_hosts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def create_ssh_known_host(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
    body: _models.PostRepositoriesPipelinesConfigSshKnownHostsBody | None = Field(None, description="The known host object to create, containing the hostname and its associated public key details."),
) -> dict[str, Any] | ToolResult:
    """Adds a known SSH host to a repository's Pipelines configuration, enabling trusted host verification during pipeline execution."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesPipelinesConfigSshKnownHostsRequest(
            path=_models.PostRepositoriesPipelinesConfigSshKnownHostsRequestPath(workspace=workspace, repo_slug=repo_slug),
            body=_models.PostRepositoriesPipelinesConfigSshKnownHostsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_ssh_known_host: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/known_hosts", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/known_hosts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_ssh_known_host")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_ssh_known_host", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_ssh_known_host",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def get_pipeline_ssh_known_host(
    workspace: str = Field(..., description="The workspace identifier, either the slug (short name) or the UUID enclosed in curly braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace."),
    known_host_uuid: str = Field(..., description="The UUID of the SSH known host entry to retrieve, uniquely identifying it within the repository's Pipelines SSH configuration."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific SSH known host entry configured at the repository level for Pipelines, identified by its UUID."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSshKnownHostsByKnownHostUuidRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigSshKnownHostsByKnownHostUuidRequestPath(workspace=workspace, repo_slug=repo_slug, known_host_uuid=known_host_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pipeline_ssh_known_host: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/known_hosts/{known_host_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/known_hosts/{known_host_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pipeline_ssh_known_host")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pipeline_ssh_known_host", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pipeline_ssh_known_host",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def update_pipeline_known_host(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
    known_host_uuid: str = Field(..., description="The unique UUID of the SSH known host entry to update, used to identify the specific record within the repository's pipeline configuration."),
    body: _models.PutRepositoriesPipelinesConfigSshKnownHostsBody | None = Field(None, description="The request body containing the updated SSH known host details, such as the hostname and public key fingerprint."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing SSH known host entry in a repository's pipeline configuration, allowing you to modify the host details for secure pipeline connections."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesPipelinesConfigSshKnownHostsRequest(
            path=_models.PutRepositoriesPipelinesConfigSshKnownHostsRequestPath(workspace=workspace, repo_slug=repo_slug, known_host_uuid=known_host_uuid),
            body=_models.PutRepositoriesPipelinesConfigSshKnownHostsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_pipeline_known_host: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/known_hosts/{known_host_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/known_hosts/{known_host_uuid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_pipeline_known_host")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_pipeline_known_host", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_pipeline_known_host",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def delete_known_host(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
    known_host_uuid: str = Field(..., description="The unique UUID of the known host entry to delete, used to identify the specific record within the repository's Pipelines SSH configuration."),
) -> dict[str, Any] | ToolResult:
    """Deletes a specific SSH known host entry from a repository's Pipelines configuration. This removes the trusted host record identified by its UUID, preventing Pipelines from automatically trusting that host during SSH operations."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesPipelinesConfigSshKnownHostsRequest(
            path=_models.DeleteRepositoriesPipelinesConfigSshKnownHostsRequestPath(workspace=workspace, repo_slug=repo_slug, known_host_uuid=known_host_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_known_host: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/known_hosts/{known_host_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/known_hosts/{known_host_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_known_host")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_known_host", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_known_host",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def list_repository_pipeline_variables(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all pipeline variables configured at the repository level for a given workspace and repository. Useful for inspecting environment variables available to pipelines without exposing secured values."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigVariablesRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigVariablesRequestPath(workspace=workspace, repo_slug=repo_slug)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_pipeline_variables: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/variables", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/variables"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_pipeline_variables")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_pipeline_variables", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_pipeline_variables",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def create_repository_pipeline_variable(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
    body: _models.PostRepositoriesPipelinesConfigVariablesBody | None = Field(None, description="The pipeline variable object to create, including its key, value, and whether it should be secured (masked in logs)."),
) -> dict[str, Any] | ToolResult:
    """Creates a new pipeline environment variable at the repository level, making it available to all pipelines within the specified repository."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesPipelinesConfigVariablesRequest(
            path=_models.PostRepositoriesPipelinesConfigVariablesRequestPath(workspace=workspace, repo_slug=repo_slug),
            body=_models.PostRepositoriesPipelinesConfigVariablesRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_repository_pipeline_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/variables", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/variables"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_repository_pipeline_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_repository_pipeline_variable", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_repository_pipeline_variable",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def get_pipeline_variable(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that uniquely identifies the repository within the workspace."),
    variable_uuid: str = Field(..., description="The UUID of the pipeline configuration variable to retrieve, uniquely identifying it within the repository."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific pipeline configuration variable for a repository by its UUID. Use this to inspect the details of a single repository-level pipeline variable."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigVariablesByVariableUuidRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPipelinesConfigVariablesByVariableUuidRequestPath(workspace=workspace, repo_slug=repo_slug, variable_uuid=variable_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pipeline_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/variables/{variable_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/variables/{variable_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pipeline_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pipeline_variable", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pipeline_variable",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def update_repository_pipeline_variable(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    repo_slug: str = Field(..., description="The repository slug or identifier within the specified workspace."),
    variable_uuid: str = Field(..., description="The unique UUID of the pipeline variable to update, used to identify the exact variable to modify."),
    body: _models.PutRepositoriesPipelinesConfigVariablesBody | None = Field(None, description="The updated variable object containing the new values or configuration to apply to the repository pipeline variable."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing pipeline variable at the repository level, allowing modification of its value or configuration. Targets a specific variable by its UUID within the given workspace and repository."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesPipelinesConfigVariablesRequest(
            path=_models.PutRepositoriesPipelinesConfigVariablesRequestPath(workspace=workspace, repo_slug=repo_slug, variable_uuid=variable_uuid),
            body=_models.PutRepositoriesPipelinesConfigVariablesRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_repository_pipeline_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/variables/{variable_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/variables/{variable_uuid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_repository_pipeline_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_repository_pipeline_variable", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_repository_pipeline_variable",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def delete_repository_pipeline_variable(
    workspace: str = Field(..., description="The workspace identifier, either the slug (short name) or the UUID surrounded by curly-braces."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) that contains the pipeline variable to delete."),
    variable_uuid: str = Field(..., description="The UUID of the pipeline variable to delete, uniquely identifying the variable within the repository."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific pipeline variable from a repository. This removes the variable and its value from the repository's pipeline configuration."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesPipelinesConfigVariablesRequest(
            path=_models.DeleteRepositoriesPipelinesConfigVariablesRequestPath(workspace=workspace, repo_slug=repo_slug, variable_uuid=variable_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_repository_pipeline_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pipelines_config/variables/{variable_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pipelines_config/variables/{variable_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_repository_pipeline_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_repository_pipeline_variable", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_repository_pipeline_variable",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def get_repository_property(
    workspace: str = Field(..., description="The workspace containing the repository, identified by its slug or UUID wrapped in curly braces."),
    repo_slug: str = Field(..., description="The slug of the repository from which the property value will be retrieved."),
    app_key: str = Field(..., description="The unique key identifying the Connect app that owns the property."),
    property_name: str = Field(..., description="The name of the application property to retrieve from the repository."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific application property value stored against a repository for a given Connect app. Useful for reading custom metadata or configuration values associated with a repository."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPropertiesRequest(
            path=_models.GetRepositoriesPropertiesRequestPath(workspace=workspace, repo_slug=repo_slug, app_key=app_key, property_name=property_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/properties/{app_key}/{property_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/properties/{app_key}/{property_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def update_repository_property(
    workspace: str = Field(..., description="The repository container, identified by either the workspace slug or the workspace UUID wrapped in curly braces."),
    repo_slug: str = Field(..., description="The slug identifier of the repository within the specified workspace."),
    app_key: str = Field(..., description="The unique key identifying the Connect app that owns this property."),
    property_name: str = Field(..., description="The name of the application property to update, scoped to the specified Connect app."),
) -> dict[str, Any] | ToolResult:
    """Updates the value of a named application property stored against a specific repository. Properties are scoped to a Connect app and allow apps to persist custom metadata on repositories."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesPropertiesRequest(
            path=_models.PutRepositoriesPropertiesRequestPath(workspace=workspace, repo_slug=repo_slug, app_key=app_key, property_name=property_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_repository_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/properties/{app_key}/{property_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/properties/{app_key}/{property_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_repository_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_repository_property", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_repository_property",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def delete_repository_property(
    workspace: str = Field(..., description="The workspace containing the repository, specified as either the workspace slug or the workspace UUID wrapped in curly braces."),
    repo_slug: str = Field(..., description="The slug identifier of the repository from which the property will be deleted."),
    app_key: str = Field(..., description="The unique key identifying the Connect app that owns the property to be deleted."),
    property_name: str = Field(..., description="The name of the application property to delete from the repository."),
) -> dict[str, Any] | ToolResult:
    """Deletes a specific application property value stored against a repository. Removes the property identified by the app key and property name from the target repository."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesPropertiesRequest(
            path=_models.DeleteRepositoriesPropertiesRequestPath(workspace=workspace, repo_slug=repo_slug, app_key=app_key, property_name=property_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_repository_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/properties/{app_key}/{property_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/properties/{app_key}/{property_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_repository_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_repository_property", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_repository_property",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def list_pull_requests(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly-braces."),
    state: Literal["OPEN", "MERGED", "DECLINED", "SUPERSEDED"] | None = Field(None, description="Filters results to pull requests in the specified state. Repeat this parameter multiple times to include pull requests from more than one state simultaneously."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all pull requests for a specified repository, defaulting to open pull requests. Supports filtering by one or more states, as well as additional filtering and sorting options."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsRequestPath(repo_slug=repo_slug, workspace=workspace),
            query=_models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsRequestQuery(state=state)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pull_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pull_requests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pull_requests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pull_requests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def create_pull_request(
    repo_slug: str = Field(..., description="The repository slug or UUID (surrounded by curly-braces) identifying the target repository where the pull request will be created."),
    workspace: str = Field(..., description="The workspace slug or UUID (surrounded by curly-braces) that owns the repository."),
    body: _models.Pullrequest | None = Field(None, description="The pull request payload including required fields such as title and source branch, plus optional fields like destination branch, reviewers list (array of user UUID objects), description, close_source_branch flag, and draft flag."),
) -> dict[str, Any] | ToolResult:
    """Creates a new pull request in the specified repository, authored by the authenticated user, merging a source branch into a destination branch (defaults to the repository's main branch if not specified)."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesPullrequestsRequest(
            path=_models.PostRepositoriesPullrequestsRequestPath(repo_slug=repo_slug, workspace=workspace),
            body=_models.PostRepositoriesPullrequestsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_pull_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_pull_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_pull_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_pull_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def list_pull_request_activity(
    repo_slug: str = Field(..., description="The repository identifier, either as a slug (URL-friendly name) or as a UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated activity log for all pull requests in a repository, including comments, updates (state changes), approvals, and request changes. Inline comments on files or code lines include an additional inline property with location details."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsActivityRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsActivityRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pull_request_activity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/activity", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/activity"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pull_request_activity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pull_request_activity", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pull_request_activity",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def get_pull_request(
    pull_request_id: int = Field(..., description="The unique numeric identifier of the pull request to retrieve."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository; UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace; UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific pull request within a repository, including its status, reviewers, and associated commits."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pull_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pull_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pull_request", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pull_request",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def update_pull_request(
    pull_request_id: int = Field(..., description="The unique numeric identifier of the pull request to update."),
    repo_slug: str = Field(..., description="The repository slug or UUID (surrounded by curly-braces) that contains the pull request."),
    workspace: str = Field(..., description="The workspace slug or UUID (surrounded by curly-braces) that owns the repository."),
    body: _models.Pullrequest | None = Field(None, description="The request body containing the pull request fields to update, such as title, description, source branch, or destination branch."),
) -> dict[str, Any] | ToolResult:
    """Updates an open pull request's metadata, such as its title, description, or source and destination branches. Only pull requests in an open state can be modified."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesPullrequestsRequest(
            path=_models.PutRepositoriesPullrequestsRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace),
            body=_models.PutRepositoriesPullrequestsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_pull_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_pull_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_pull_request", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_pull_request",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def list_pull_request_activity_by_id(
    pull_request_id: int = Field(..., description="The numeric ID of the pull request whose activity log should be retrieved."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated activity log for a specific pull request, including reviewer comments, updates, approvals, and change requests. Inline comments on files or code lines include an additional inline property with location details."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdActivityRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdActivityRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pull_request_activity_by_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/activity", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/activity"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pull_request_activity_by_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pull_request_activity_by_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pull_request_activity_by_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def approve_pull_request(
    pull_request_id: int = Field(..., description="The numeric ID of the pull request to approve."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Approves the specified pull request on behalf of the authenticated user. This records the user's approval and contributes to any required approval count for merging."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesPullrequestsApproveRequest(
            path=_models.PostRepositoriesPullrequestsApproveRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for approve_pull_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/approve", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/approve"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("approve_pull_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("approve_pull_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="approve_pull_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def unapprove_pull_request(
    pull_request_id: int = Field(..., description="The unique numeric identifier of the pull request to unapprove."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Removes the authenticated user's approval from the specified pull request. Use this to retract a previously submitted approval on a pull request in the given repository."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesPullrequestsApproveRequest(
            path=_models.DeleteRepositoriesPullrequestsApproveRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unapprove_pull_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/approve", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/approve"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unapprove_pull_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unapprove_pull_request", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unapprove_pull_request",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def list_pull_request_comments(
    pull_request_id: int = Field(..., description="The unique numeric ID of the pull request whose comments should be retrieved."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all comments on a pull request, including global comments, inline comments, and replies. Results are sorted oldest to newest by default and support filtering and sorting via query parameters."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdCommentsRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdCommentsRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pull_request_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pull_request_comments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pull_request_comments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pull_request_comments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def create_pull_request_comment(
    pull_request_id: int = Field(..., description="The unique numeric identifier of the pull request on which the comment will be created."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
    body: _models.PullrequestComment | None = Field(None, description="The request body containing the comment content and any optional metadata such as inline positioning or parent comment reference."),
) -> dict[str, Any] | ToolResult:
    """Creates a new comment on a specified pull request in a Bitbucket repository. Returns the newly created comment object upon success."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesPullrequestsCommentsRequest(
            path=_models.PostRepositoriesPullrequestsCommentsRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace),
            body=_models.PostRepositoriesPullrequestsCommentsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_pull_request_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_pull_request_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_pull_request_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_pull_request_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def get_pull_request_comment(
    comment_id: str = Field(..., description="The unique numeric identifier of the comment to retrieve."),
    pull_request_id: int = Field(..., description="The unique numeric identifier of the pull request containing the comment."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) or the repository UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug (URL-friendly name) or the workspace UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific comment from a pull request by its comment ID. Returns the full comment details including content, author, and timestamps."""

    _comment_id = _parse_int(comment_id)

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdCommentsByCommentIdRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdCommentsByCommentIdRequestPath(comment_id=_comment_id, pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pull_request_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments/{comment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pull_request_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pull_request_comment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pull_request_comment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def update_pull_request_comment(
    comment_id: str = Field(..., description="The unique numeric identifier of the comment to update."),
    pull_request_id: int = Field(..., description="The unique numeric identifier of the pull request containing the comment."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace. UUIDs must be surrounded by curly-braces."),
    body: _models.PullrequestComment | None = Field(None, description="The request body containing the updated comment content to replace the existing comment."),
) -> dict[str, Any] | ToolResult:
    """Updates the content of an existing comment on a specific pull request. Only the comment body can be modified through this operation."""

    _comment_id = _parse_int(comment_id)

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesPullrequestsCommentsRequest(
            path=_models.PutRepositoriesPullrequestsCommentsRequestPath(comment_id=_comment_id, pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace),
            body=_models.PutRepositoriesPullrequestsCommentsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_pull_request_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments/{comment_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_pull_request_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_pull_request_comment", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_pull_request_comment",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def delete_pull_request_comment(
    comment_id: str = Field(..., description="The unique numeric identifier of the comment to delete."),
    pull_request_id: int = Field(..., description="The unique numeric identifier of the pull request containing the comment."),
    repo_slug: str = Field(..., description="The repository slug (URL-friendly name) or the repository UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug (URL-friendly name) or the workspace UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific comment from a pull request. This action is irreversible and removes the comment from the pull request discussion thread."""

    _comment_id = _parse_int(comment_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesPullrequestsCommentsRequest(
            path=_models.DeleteRepositoriesPullrequestsCommentsRequestPath(comment_id=_comment_id, pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_pull_request_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments/{comment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_pull_request_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_pull_request_comment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_pull_request_comment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def resolve_pull_request_comment(
    comment_id: str = Field(..., description="The unique numeric identifier of the comment thread to resolve."),
    pull_request_id: int = Field(..., description="The unique numeric identifier of the pull request containing the comment thread."),
    repo_slug: str = Field(..., description="The repository slug or UUID (surrounded by curly-braces) that uniquely identifies the repository within the workspace."),
    workspace: str = Field(..., description="The workspace slug or UUID (surrounded by curly-braces) that uniquely identifies the workspace containing the repository."),
) -> dict[str, Any] | ToolResult:
    """Marks a pull request comment thread as resolved, collapsing the discussion and indicating the concern has been addressed."""

    _comment_id = _parse_int(comment_id)

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesPullrequestsCommentsResolveRequest(
            path=_models.PostRepositoriesPullrequestsCommentsResolveRequestPath(comment_id=_comment_id, pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for resolve_pull_request_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments/{comment_id}/resolve", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments/{comment_id}/resolve"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("resolve_pull_request_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("resolve_pull_request_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="resolve_pull_request_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def reopen_pull_request_comment_thread(
    comment_id: str = Field(..., description="The unique numeric identifier of the comment whose resolved status should be removed."),
    pull_request_id: int = Field(..., description="The unique numeric identifier of the pull request containing the comment thread."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Reopens a previously resolved comment thread on a pull request by removing its resolved status. This allows further discussion to continue on the specified comment."""

    _comment_id = _parse_int(comment_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesPullrequestsCommentsResolveRequest(
            path=_models.DeleteRepositoriesPullrequestsCommentsResolveRequestPath(comment_id=_comment_id, pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reopen_pull_request_comment_thread: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments/{comment_id}/resolve", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments/{comment_id}/resolve"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reopen_pull_request_comment_thread")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reopen_pull_request_comment_thread", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reopen_pull_request_comment_thread",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def list_pull_request_commits(
    pull_request_id: int = Field(..., description="The unique numeric identifier of the pull request whose commits are being retrieved."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository; UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that owns the repository; UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of commits associated with a specific pull request. These are the commits that will be merged into the destination branch upon pull request acceptance."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPullrequestsCommitsRequest(
            path=_models.GetRepositoriesPullrequestsCommitsRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pull_request_commits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/commits", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/commits"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pull_request_commits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pull_request_commits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pull_request_commits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def decline_pull_request(
    pull_request_id: int = Field(..., description="The unique numeric ID of the pull request to decline."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Declines an open pull request in the specified repository, rejecting the proposed changes. Use this to formally close a pull request without merging."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesPullrequestsDeclineRequest(
            path=_models.PostRepositoriesPullrequestsDeclineRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for decline_pull_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/decline", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/decline"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("decline_pull_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("decline_pull_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="decline_pull_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def get_pull_request_diff(
    pull_request_id: int = Field(..., description="The unique numeric identifier of the pull request whose diff you want to retrieve."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository containing the pull request. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the file diff for a specific pull request, showing all line-level changes between the source and destination branches. Redirects to the repository diff endpoint using the revspec corresponding to the pull request."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPullrequestsDiffRequest(
            path=_models.GetRepositoriesPullrequestsDiffRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pull_request_diff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/diff", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/diff"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pull_request_diff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pull_request_diff", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pull_request_diff",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def get_pull_request_diffstat(
    pull_request_id: int = Field(..., description="The unique numeric identifier of the pull request whose diff stat you want to retrieve."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the diff stat for a specific pull request, showing a summary of file changes (additions, deletions, modifications) by redirecting to the repository diffstat endpoint using the pull request's revision spec."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPullrequestsDiffstatRequest(
            path=_models.GetRepositoriesPullrequestsDiffstatRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pull_request_diffstat: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/diffstat", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/diffstat"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pull_request_diffstat")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pull_request_diffstat", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pull_request_diffstat",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def merge_pull_request(
    pull_request_id: int = Field(..., description="The numeric ID of the pull request to merge."),
    repo_slug: str = Field(..., description="The repository slug or UUID (surrounded by curly-braces) identifying the target repository."),
    workspace: str = Field(..., description="The workspace slug or UUID (surrounded by curly-braces) that owns the repository."),
    async_: bool | None = Field(None, alias="async", description="When true, the merge runs asynchronously and returns immediately with a 202 status and a polling link in the Location header; when false (default), the merge runs synchronously and returns 200 on success, or 202 with a polling link if the merge exceeds the timeout threshold."),
    message: str | None = Field(None, description="Custom commit message to use on the resulting merge commit; limited to 128 KiB in size."),
    close_source_branch: bool | None = Field(None, description="Whether to delete the source branch after a successful merge; falls back to the value set when the pull request was created if not provided, which defaults to false."),
    merge_strategy: Literal["merge_commit", "squash", "fast_forward", "squash_fast_forward", "rebase_fast_forward", "rebase_merge"] | None = Field(None, description="The strategy used to merge the pull request into the target branch; controls how commits are combined or rewritten."),
) -> dict[str, Any] | ToolResult:
    """Merges a pull request in the specified repository, combining the source branch into the target branch using the chosen merge strategy. Supports synchronous and asynchronous execution modes."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesPullrequestsMergeRequest(
            path=_models.PostRepositoriesPullrequestsMergeRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace),
            query=_models.PostRepositoriesPullrequestsMergeRequestQuery(async_=async_),
            body=_models.PostRepositoriesPullrequestsMergeRequestBody(message=message, close_source_branch=close_source_branch, merge_strategy=merge_strategy)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for merge_pull_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/merge", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/merge"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("merge_pull_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("merge_pull_request", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="merge_pull_request",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def get_pull_request_merge_task_status(
    pull_request_id: int = Field(..., description="The numeric ID of the pull request whose merge task status is being checked."),
    repo_slug: str = Field(..., description="The repository slug or UUID (surrounded by curly-braces) identifying the repository containing the pull request."),
    task_id: str = Field(..., description="The task ID returned by the merge endpoint when the merge operation was accepted asynchronously with a 202 response."),
    workspace: str = Field(..., description="The workspace slug or UUID (surrounded by curly-braces) identifying the workspace that owns the repository."),
) -> dict[str, Any] | ToolResult:
    """Checks the status of an asynchronous pull request merge task using a task ID returned from a long-running merge operation. Returns PENDING while in progress, SUCCESS with the merged pull request object on completion, or an error if the merge failed."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPullrequestsMergeTaskStatusRequest(
            path=_models.GetRepositoriesPullrequestsMergeTaskStatusRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, task_id=task_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pull_request_merge_task_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/merge/task-status/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/merge/task-status/{task_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pull_request_merge_task_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pull_request_merge_task_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pull_request_merge_task_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def get_pull_request_patch(
    pull_request_id: int = Field(..., description="The unique numeric identifier of the pull request within the repository."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository; UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace; UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the patch file for a specific pull request, redirecting to the repository patch endpoint using the pull request's revision specification."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPullrequestsPatchRequest(
            path=_models.GetRepositoriesPullrequestsPatchRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pull_request_patch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/patch", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/patch"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pull_request_patch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pull_request_patch", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pull_request_patch",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def request_pull_request_changes(
    pull_request_id: int = Field(..., description="The unique numeric identifier of the pull request on which changes are being requested."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository containing the pull request. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUID values must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Request changes on a pull request in a Bitbucket repository, indicating that the pull request requires modifications before it can be approved or merged."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesPullrequestsRequestChangesRequest(
            path=_models.PostRepositoriesPullrequestsRequestChangesRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for request_pull_request_changes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/request-changes", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/request-changes"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("request_pull_request_changes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("request_pull_request_changes", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="request_pull_request_changes",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def remove_pull_request_change_request(
    pull_request_id: int = Field(..., description="The numeric ID of the pull request from which the change request will be removed."),
    repo_slug: str = Field(..., description="The repository slug or UUID (surrounded by curly-braces) identifying the repository containing the pull request."),
    workspace: str = Field(..., description="The workspace slug or UUID (surrounded by curly-braces) identifying the workspace that owns the repository."),
) -> dict[str, Any] | ToolResult:
    """Removes the authenticated user's change request from a pull request, withdrawing their objection and allowing the PR to proceed toward merge."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesPullrequestsRequestChangesRequest(
            path=_models.DeleteRepositoriesPullrequestsRequestChangesRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_pull_request_change_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/request-changes", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/request-changes"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_pull_request_change_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_pull_request_change_request", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_pull_request_change_request",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests, Commit statuses
@mcp.tool()
async def list_pull_request_statuses(
    pull_request_id: int = Field(..., description="The unique numeric identifier of the pull request whose statuses should be retrieved."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUID values must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace. UUID values must be surrounded by curly-braces."),
    q: str | None = Field(None, description="A query string to filter the returned statuses using Bitbucket's filtering and sorting syntax, allowing you to narrow down results by specific fields or conditions."),
    sort: str | None = Field(None, description="The field name by which to sort the returned statuses using Bitbucket's filtering and sorting syntax. Defaults to created_on if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all commit statuses (such as CI/CD build results) associated with a specific pull request in a Bitbucket repository. Supports filtering and sorting to narrow down results."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPullrequestsStatusesRequest(
            path=_models.GetRepositoriesPullrequestsStatusesRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace),
            query=_models.GetRepositoriesPullrequestsStatusesRequestQuery(q=q, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pull_request_statuses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/statuses", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/statuses"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pull_request_statuses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pull_request_statuses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pull_request_statuses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def list_pull_request_tasks(
    pull_request_id: int = Field(..., description="The unique numeric identifier of the pull request whose tasks should be listed."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace. UUIDs must be surrounded by curly-braces."),
    q: str | None = Field(None, description="A query string to filter the returned tasks using Bitbucket's filtering and sorting syntax."),
    sort: str | None = Field(None, description="The field by which results should be sorted using Bitbucket's filtering and sorting syntax. Defaults to created_on if not specified."),
    pagelen: int | None = Field(None, description="The number of task objects to include per page of results. Accepts values between 1 and 100; defaults to 10."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of tasks associated with a specific pull request in a repository. Supports filtering and sorting results by the 'task' field."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdTasksRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdTasksRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace),
            query=_models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdTasksRequestQuery(q=q, sort=sort, pagelen=pagelen)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pull_request_tasks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/tasks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pull_request_tasks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pull_request_tasks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pull_request_tasks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def create_pull_request_task(
    pull_request_id: int = Field(..., description="The numeric ID of the pull request on which the task will be created."),
    repo_slug: str = Field(..., description="The repository slug or UUID (surrounded by curly-braces) that uniquely identifies the repository within the workspace."),
    workspace: str = Field(..., description="The workspace slug or UUID (surrounded by curly-braces) that identifies the Bitbucket workspace containing the repository."),
    raw: str = Field(..., description="The text content of the task to be created on the pull request."),
    comment: _models.PostRepositoriesPullrequestsTasksBodyComment | None = Field(None, description="An optional reference to a pull request comment by its ID; when provided, the task will be displayed beneath that comment in the pull request view."),
    pending: bool | None = Field(None, description="Indicates whether the task should be created in a pending (incomplete) state; when omitted, the default state is applied."),
) -> dict[str, Any] | ToolResult:
    """Creates a new task on a specified pull request in a Bitbucket repository. Tasks can optionally be linked to a specific comment, causing them to appear beneath that comment in the pull request view."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesPullrequestsTasksRequest(
            path=_models.PostRepositoriesPullrequestsTasksRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, workspace=workspace),
            body=_models.PostRepositoriesPullrequestsTasksRequestBody(comment=comment, pending=pending,
                content=_models.PostRepositoriesPullrequestsTasksRequestBodyContent(raw=raw))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_pull_request_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/tasks", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/tasks"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_pull_request_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_pull_request_task", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_pull_request_task",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def get_pull_request_task(
    pull_request_id: int = Field(..., description="The numeric ID of the pull request containing the task."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces."),
    task_id: str = Field(..., description="The unique numeric ID of the task to retrieve."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific task associated with a pull request in the given repository. Returns full task details for the specified task ID."""

    _task_id = _parse_int(task_id)

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdTasksByTaskIdRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugPullrequestsByPullRequestIdTasksByTaskIdRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, task_id=_task_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pull_request_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/tasks/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/tasks/{task_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pull_request_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pull_request_task", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pull_request_task",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def update_pull_request_task(
    pull_request_id: int = Field(..., description="The numeric ID of the pull request that contains the task to update."),
    repo_slug: str = Field(..., description="The repository slug or UUID (surrounded by curly-braces) identifying the repository containing the pull request."),
    task_id: str = Field(..., description="The unique numeric ID of the task to update."),
    workspace: str = Field(..., description="The workspace slug or UUID (surrounded by curly-braces) identifying the workspace that owns the repository."),
    raw: str = Field(..., description="The updated text content of the task."),
    state: Literal["RESOLVED", "UNRESOLVED"] | None = Field(None, description="The resolution state of the task, indicating whether it is open or completed."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing task on a specific pull request, allowing changes to the task content and resolution state."""

    _task_id = _parse_int(task_id)

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesPullrequestsTasksRequest(
            path=_models.PutRepositoriesPullrequestsTasksRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, task_id=_task_id, workspace=workspace),
            body=_models.PutRepositoriesPullrequestsTasksRequestBody(state=state,
                content=_models.PutRepositoriesPullrequestsTasksRequestBodyContent(raw=raw))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_pull_request_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/tasks/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/tasks/{task_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_pull_request_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_pull_request_task", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_pull_request_task",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pullrequests
@mcp.tool()
async def delete_pull_request_task(
    pull_request_id: int = Field(..., description="The numeric ID of the pull request from which the task will be deleted."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces."),
    task_id: str = Field(..., description="The unique numeric ID of the task to delete."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific task from a pull request. This action cannot be undone and removes the task from the pull request's task list."""

    _task_id = _parse_int(task_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesPullrequestsTasksRequest(
            path=_models.DeleteRepositoriesPullrequestsTasksRequestPath(pull_request_id=pull_request_id, repo_slug=repo_slug, task_id=_task_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_pull_request_task: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/tasks/{task_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/tasks/{task_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_pull_request_task")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_pull_request_task", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_pull_request_task",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def get_pull_request_property(
    workspace: str = Field(..., description="The workspace containing the repository, identified by its slug or UUID (UUID must be wrapped in curly braces)."),
    repo_slug: str = Field(..., description="The slug of the repository containing the pull request."),
    pullrequest_id: str = Field(..., description="The unique numeric identifier of the pull request within the repository."),
    app_key: str = Field(..., description="The key identifying the Connect app that owns the property, used to namespace properties and avoid conflicts between apps."),
    property_name: str = Field(..., description="The name of the application property to retrieve, scoped under the specified Connect app key."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific application property value stored against a pull request in a Bitbucket repository. Useful for reading custom metadata attached to a pull request by a Connect app."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesPullrequestsPropertiesRequest(
            path=_models.GetRepositoriesPullrequestsPropertiesRequestPath(workspace=workspace, repo_slug=repo_slug, pullrequest_id=pullrequest_id, app_key=app_key, property_name=property_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pull_request_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pullrequest_id}/properties/{app_key}/{property_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pullrequest_id}/properties/{app_key}/{property_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pull_request_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pull_request_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pull_request_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def update_pull_request_property(
    workspace: str = Field(..., description="The workspace containing the repository, identified by its slug or UUID (UUID must be wrapped in curly braces)."),
    repo_slug: str = Field(..., description="The slug of the repository that contains the pull request."),
    pullrequest_id: str = Field(..., description="The unique numeric identifier of the pull request whose property is being updated."),
    app_key: str = Field(..., description="The key identifying the Connect app that owns this property, used to namespace properties and prevent collisions between apps."),
    property_name: str = Field(..., description="The name of the application property to update, scoped under the specified app key."),
) -> dict[str, Any] | ToolResult:
    """Update the value of a named application property stored against a specific pull request. Application properties allow Connect apps to attach custom metadata to Bitbucket resources."""

    # Construct request model with validation
    try:
        _request = _models.PutRepositoriesPullrequestsPropertiesRequest(
            path=_models.PutRepositoriesPullrequestsPropertiesRequestPath(workspace=workspace, repo_slug=repo_slug, pullrequest_id=pullrequest_id, app_key=app_key, property_name=property_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_pull_request_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pullrequest_id}/properties/{app_key}/{property_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pullrequest_id}/properties/{app_key}/{property_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_pull_request_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_pull_request_property", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_pull_request_property",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def delete_pull_request_property(
    workspace: str = Field(..., description="The workspace containing the repository, identified by its slug or UUID (UUID must be wrapped in curly braces)."),
    repo_slug: str = Field(..., description="The slug of the repository containing the pull request."),
    pullrequest_id: str = Field(..., description="The unique numeric identifier of the pull request whose property should be deleted."),
    app_key: str = Field(..., description="The key identifying the Connect app that owns the property being deleted."),
    property_name: str = Field(..., description="The name of the application property to delete from the pull request."),
) -> dict[str, Any] | ToolResult:
    """Deletes a specific application property value stored against a pull request. Use this to remove custom metadata associated with a pull request by a Connect app."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesPullrequestsPropertiesRequest(
            path=_models.DeleteRepositoriesPullrequestsPropertiesRequestPath(workspace=workspace, repo_slug=repo_slug, pullrequest_id=pullrequest_id, app_key=app_key, property_name=property_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_pull_request_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/pullrequests/{pullrequest_id}/properties/{app_key}/{property_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/pullrequests/{pullrequest_id}/properties/{app_key}/{property_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_pull_request_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_pull_request_property", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_pull_request_property",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Refs
@mcp.tool()
async def list_repository_refs(
    repo_slug: str = Field(..., description="The repository identifier, either the URL-friendly slug or the repository UUID enclosed in curly braces."),
    workspace: str = Field(..., description="The workspace identifier, either the workspace slug or the workspace UUID enclosed in curly braces."),
    q: str | None = Field(None, description="A query string to filter the returned refs using Bitbucket's filtering and sorting syntax, allowing you to narrow results by properties such as name or type."),
    sort: str | None = Field(None, description="The field by which to sort results using Bitbucket's filtering and sorting syntax; specifying 'name' applies natural sort order so numerical segments are ordered numerically rather than lexicographically."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all branches and tags (refs) for a given repository in a Bitbucket workspace. Results default to lexical ordering but can be sorted naturally by name using the sort parameter."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesRefsRequest(
            path=_models.GetRepositoriesRefsRequestPath(repo_slug=repo_slug, workspace=workspace),
            query=_models.GetRepositoriesRefsRequestQuery(q=q, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_refs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/refs", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/refs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_refs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_refs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_refs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Refs
@mcp.tool()
async def list_branches(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly-braces."),
    q: str | None = Field(None, description="A filter expression to narrow down the list of branches returned, following Bitbucket's filtering and sorting syntax."),
    sort: str | None = Field(None, description="The field by which to sort the returned branches, following Bitbucket's filtering and sorting syntax. Sorting by name applies natural ordering so numerical segments are interpreted as numbers rather than strings."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all open branches for the specified repository, returned in the order the source control manager provides them. Supports filtering and natural sorting by branch name via query parameters."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugRefsBranchesRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugRefsBranchesRequestPath(repo_slug=repo_slug, workspace=workspace),
            query=_models.GetRepositoriesByWorkspaceByRepoSlugRefsBranchesRequestQuery(q=q, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_branches: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/refs/branches", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/refs/branches"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_branches")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_branches", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_branches",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Refs
@mcp.tool()
async def create_branch(
    repo_slug: str = Field(..., description="The repository identifier, either as a slug (URL-friendly name) or as a UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (workspace ID) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Creates a new branch in the specified repository by providing a branch name and a target commit hash. Requires authentication with appropriate repository access."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesRefsBranchesRequest(
            path=_models.PostRepositoriesRefsBranchesRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_branch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/refs/branches", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/refs/branches"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_branch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_branch", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_branch",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Refs
@mcp.tool()
async def get_branch(
    name: str = Field(..., description="The name of the branch to retrieve. For Git repositories, omit any prefix such as 'refs/heads' and provide only the bare branch name."),
    repo_slug: str = Field(..., description="The repository identifier, either as a human-readable slug or as a UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace identifier, either as a human-readable slug or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves details for a specific branch within a repository by its name. Authentication is required, and private repositories require appropriate account authorization."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugRefsBranchesByNameRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugRefsBranchesByNameRequestPath(name=name, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_branch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/refs/branches/{name}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/refs/branches/{name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_branch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_branch", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_branch",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Refs
@mcp.tool()
async def delete_branch(
    name: str = Field(..., description="The name of the branch to delete, provided without any prefix such as refs/heads."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository; UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace; UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Deletes a branch from the specified repository. The main branch cannot be deleted; branch names should be provided without any prefix such as refs/heads."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesRefsBranchesRequest(
            path=_models.DeleteRepositoriesRefsBranchesRequestPath(name=name, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_branch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/refs/branches/{name}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/refs/branches/{name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_branch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_branch", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_branch",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Refs
@mcp.tool()
async def list_repository_tags(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace. UUIDs must be surrounded by curly-braces."),
    q: str | None = Field(None, description="A query string to filter the returned tags using Bitbucket's filtering and sorting syntax."),
    sort: str | None = Field(None, description="The field by which to sort results using Bitbucket's filtering and sorting syntax. Sorting by the name field applies natural ordering, treating numeric segments as numbers rather than strings."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all tags for a given repository in a workspace. Supports filtering and sorting, including natural sort order for version-style tag names when sorting by name."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugRefsTagsRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugRefsTagsRequestPath(repo_slug=repo_slug, workspace=workspace),
            query=_models.GetRepositoriesByWorkspaceByRepoSlugRefsTagsRequestQuery(q=q, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_tags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/refs/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/refs/tags"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_tags")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_tags", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_tags",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Refs
@mcp.tool()
async def create_tag(
    repo_slug: str = Field(..., description="The repository identifier, either the repository slug or the repository UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace identifier, either the workspace slug or the workspace UUID surrounded by curly-braces."),
    body: _models.Tag | None = Field(None, description="JSON document containing the tag name, the target commit hash, and an optional annotation message. A full commit hash is preferred over a short prefix to avoid ambiguity."),
) -> dict[str, Any] | ToolResult:
    """Creates a new annotated tag in the specified repository, associating it with a target commit hash. An optional message may be provided; if omitted, a default message is generated automatically."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesRefsTagsRequest(
            path=_models.PostRepositoriesRefsTagsRequestPath(repo_slug=repo_slug, workspace=workspace),
            body=_models.PostRepositoriesRefsTagsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/refs/tags", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/refs/tags"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
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

# Tags: Refs
@mcp.tool()
async def get_repository_tag(
    name: str = Field(..., description="The name of the tag to retrieve."),
    repo_slug: str = Field(..., description="The repository slug or UUID (surrounded by curly-braces) that uniquely identifies the repository within the workspace."),
    workspace: str = Field(..., description="The workspace slug or UUID (surrounded by curly-braces) that uniquely identifies the workspace containing the repository."),
) -> dict[str, Any] | ToolResult:
    """Retrieves details for a specific tag in a repository, including the tag's target commit, tagger information, date, and associated links."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugRefsTagsByNameRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugRefsTagsByNameRequestPath(name=name, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/refs/tags/{name}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/refs/tags/{name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_tag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_tag", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_tag",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Refs
@mcp.tool()
async def delete_tag(
    name: str = Field(..., description="The name of the tag to delete, without any ref prefixes."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace. UUIDs must be surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a tag from the specified repository. Provide only the tag name without any ref prefixes such as refs/tags."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRepositoriesRefsTagsRequest(
            path=_models.DeleteRepositoriesRefsTagsRequestPath(name=name, repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_tag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/refs/tags/{name}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/refs/tags/{name}"
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

# Tags: Source, Repositories
@mcp.tool()
async def get_repository_root_src(
    repo_slug: str = Field(..., description="The repository identifier, either as a URL-friendly slug or as a UUID wrapped in curly-braces."),
    workspace: str = Field(..., description="The workspace identifier, either as a URL-friendly slug or as a UUID wrapped in curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the root directory listing of a repository's main branch, automatically resolving the branch name and latest commit. This is a convenience redirect equivalent to browsing the root path of the main branch directly."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugSrcRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugSrcRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_root_src: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/src", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/src"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_root_src")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_root_src", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_root_src",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Source, Repositories
@mcp.tool()
async def create_commit_with_files(
    repo_slug: str = Field(..., description="The repository slug or UUID (surrounded by curly-braces) identifying the target repository."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID (surrounded by curly-braces) that owns the repository."),
    message: str | None = Field(None, description="The commit message to associate with the new commit. When omitted, Bitbucket uses a default canned message."),
    author: str | None = Field(None, description="The author identity for the new commit in 'Full Name <email>' format. When omitted, the authenticated user's display name and primary email are used; anonymous commits are not permitted."),
    files: str | None = Field(None, description="One or more repository-relative file paths that this request is manipulating. Listing a path here without a corresponding file field body causes that file to be deleted; paths not referenced in this field or as file fields are carried over unchanged from the parent commit."),
    branch: str | None = Field(None, description="The name of the branch on which to create the new commit. If omitted, the commit is placed on the repository's main branch. Providing a new branch name creates that branch; providing an existing branch name advances it, with optional parent SHA1 validation to guard against concurrent changes."),
) -> dict[str, Any] | ToolResult:
    """Creates a new commit in a repository by uploading, modifying, or deleting files via multipart/form-data or URL-encoded form data. Supports setting commit message, author, target branch, and file attributes such as executable or symlink."""

    # Construct request model with validation
    try:
        _request = _models.PostRepositoriesSrcRequest(
            path=_models.PostRepositoriesSrcRequestPath(repo_slug=repo_slug, workspace=workspace),
            query=_models.PostRepositoriesSrcRequestQuery(message=message, author=author, files=files, branch=branch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_commit_with_files: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/src", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/src"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_commit_with_files")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_commit_with_files", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_commit_with_files",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Source, Repositories
@mcp.tool()
async def get_repository_src(
    commit: str = Field(..., description="The full SHA1 hash of the commit to retrieve file or directory contents from."),
    path: str = Field(..., description="The path to the target file or directory within the repository, relative to the repository root. Append a trailing slash when targeting the root directory."),
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the repository. UUIDs must be surrounded by curly braces."),
    workspace: str = Field(..., description="The workspace slug or UUID identifying the workspace that owns the repository. UUIDs must be surrounded by curly braces."),
    format_: Literal["meta", "rendered"] | None = Field(None, alias="format", description="Controls the response format: 'meta' returns JSON metadata about the file or directory (size, attributes, links) instead of raw contents; 'rendered' returns HTML-rendered markup for supported plain-text file types (.md, .rst, .textile, etc.) instead of raw contents."),
    q: str | None = Field(None, description="A filter expression to narrow directory listing results using Bitbucket's filtering syntax, such as filtering by file size or attributes."),
    sort: str | None = Field(None, description="A sort expression to order directory listing results using Bitbucket's sorting syntax, such as sorting by size ascending or descending."),
    max_depth: int | None = Field(None, description="Maximum directory depth to recurse into when listing directory contents. Performs a breadth-first traversal; very large values may cause the request to time out with a 555 error. Defaults to 1 (non-recursive, direct children only)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the raw contents of a file or a paginated directory listing at a specific commit in a Bitbucket repository. Supports metadata retrieval, rendered markup output, recursive directory traversal, and filtering/sorting for directory listings."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesByWorkspaceByRepoSlugSrcByCommitByPathRequest(
            path=_models.GetRepositoriesByWorkspaceByRepoSlugSrcByCommitByPathRequestPath(commit=commit, path=path, repo_slug=repo_slug, workspace=workspace),
            query=_models.GetRepositoriesByWorkspaceByRepoSlugSrcByCommitByPathRequestQuery(format_=format_, q=q, sort=sort, max_depth=max_depth)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_repository_src: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/src/{commit}/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/src/{commit}/{path}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_repository_src")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_repository_src", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_repository_src",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories
@mcp.tool()
async def list_repository_watchers(
    repo_slug: str = Field(..., description="The repository identifier, either as a slug (URL-friendly name) or as a UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (URL-friendly name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all users watching the specified repository. Useful for understanding a repository's audience and engagement."""

    # Construct request model with validation
    try:
        _request = _models.GetRepositoriesWatchersRequest(
            path=_models.GetRepositoriesWatchersRequestPath(repo_slug=repo_slug, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_watchers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/repositories/{workspace}/{repo_slug}/watchers", _request.path.model_dump(by_alias=True)) if _request.path else "/repositories/{workspace}/{repo_slug}/watchers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_watchers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_watchers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_watchers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def create_snippet() -> dict[str, Any] | ToolResult:
    """Creates a new snippet under the authenticated user's account, supporting multiple text and binary files via multipart/form-data or multipart/related requests. Snippets can be public or private and optionally organized under a specific workspace."""

    # Extract parameters for API call
    _http_path = "/snippets"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_snippet")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_snippet", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_snippet",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def list_workspace_snippets(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
    role: Literal["owner", "contributor", "member"] | None = Field(None, description="Filters results to snippets where the authenticated user holds the specified role: owner (created the snippet), contributor (has edit access), or member (has view access)."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all snippets owned by a specific workspace, optionally filtered by the authenticated user's role within that workspace."""

    # Construct request model with validation
    try:
        _request = _models.GetSnippetsByWorkspaceRequest(
            path=_models.GetSnippetsByWorkspaceRequestPath(workspace=workspace),
            query=_models.GetSnippetsByWorkspaceRequestQuery(role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_snippets: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_snippets")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_snippets", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_snippets",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def create_workspace_snippet(workspace: str = Field(..., description="The workspace in which to create the snippet, identified by either its slug (human-readable ID) or its UUID surrounded by curly-braces.")) -> dict[str, Any] | ToolResult:
    """Creates a new snippet scoped to the specified workspace. Behaves identically to the global snippet creation endpoint, but associates the snippet with the given workspace."""

    # Construct request model with validation
    try:
        _request = _models.PostSnippetsForWorkspaceRequest(
            path=_models.PostSnippetsForWorkspaceRequestPath(workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_workspace_snippet: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_workspace_snippet")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_workspace_snippet", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_workspace_snippet",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def get_snippet(
    encoded_id: str = Field(..., description="The unique identifier of the snippet to retrieve."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (e.g. a short name) or as a UUID surrounded by curly braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single snippet by its ID within a workspace. Supports multiple response content types: application/json (default, metadata and file links only), multipart/related (full snippet including file contents in one response), and multipart/form-data (flat structure with file contents)."""

    # Construct request model with validation
    try:
        _request = _models.GetSnippetsByWorkspaceByEncodedIdRequest(
            path=_models.GetSnippetsByWorkspaceByEncodedIdRequestPath(encoded_id=encoded_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_snippet: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_snippet")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_snippet", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_snippet",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def update_snippet(
    encoded_id: str = Field(..., description="The unique identifier of the snippet to update."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (e.g. a short name) or as a UUID surrounded by curly braces."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing snippet in the specified workspace, allowing changes to its title and files via differential payloads. Supports adding, updating, or deleting files atomically using JSON, multipart/related, or multipart/form-data content types."""

    # Construct request model with validation
    try:
        _request = _models.PutSnippetsForWorkspaceForEncodedIdRequest(
            path=_models.PutSnippetsForWorkspaceForEncodedIdRequestPath(encoded_id=encoded_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_snippet: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_snippet")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_snippet", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_snippet",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def delete_snippet(
    encoded_id: str = Field(..., description="The unique identifier of the snippet to delete."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (e.g. my-team) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific snippet from the given workspace. Returns an empty response upon successful deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSnippetsForWorkspaceForEncodedIdRequest(
            path=_models.DeleteSnippetsForWorkspaceForEncodedIdRequestPath(encoded_id=encoded_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_snippet: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_snippet")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_snippet", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_snippet",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def list_snippet_comments(
    encoded_id: str = Field(..., description="The unique identifier of the snippet whose comments are being retrieved."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all comments on a specific snippet within a workspace. Results are sorted oldest to newest by default and can be overridden with the sort query parameter."""

    # Construct request model with validation
    try:
        _request = _models.GetSnippetsByWorkspaceByEncodedIdCommentsRequest(
            path=_models.GetSnippetsByWorkspaceByEncodedIdCommentsRequestPath(encoded_id=encoded_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_snippet_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/comments"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_snippet_comments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_snippet_comments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_snippet_comments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def create_snippet_comment(
    encoded_id: str = Field(..., description="The unique identifier of the snippet to comment on."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (e.g. my-team) or as a UUID surrounded by curly-braces."),
    body: _models.SnippetComment | None = Field(None, description="The comment payload. Must include the required field `content.raw` containing the comment text. Optionally include `parent.id` to post a threaded reply to an existing comment."),
) -> dict[str, Any] | ToolResult:
    """Creates a new comment on a specific snippet in a workspace. Supports threaded replies by including a parent comment ID in the request body."""

    # Construct request model with validation
    try:
        _request = _models.PostSnippetsCommentsRequest(
            path=_models.PostSnippetsCommentsRequestPath(encoded_id=encoded_id, workspace=workspace),
            body=_models.PostSnippetsCommentsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_snippet_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/comments", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/comments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_snippet_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_snippet_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_snippet_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def get_snippet_comment(
    comment_id: str = Field(..., description="The unique numeric identifier of the comment to retrieve."),
    encoded_id: str = Field(..., description="The unique identifier of the snippet, as assigned by Bitbucket."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific comment on a snippet within a workspace. Returns the full comment details for the given comment ID."""

    _comment_id = _parse_int(comment_id)

    # Construct request model with validation
    try:
        _request = _models.GetSnippetsByWorkspaceByEncodedIdCommentsByCommentIdRequest(
            path=_models.GetSnippetsByWorkspaceByEncodedIdCommentsByCommentIdRequestPath(comment_id=_comment_id, encoded_id=encoded_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_snippet_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/comments/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/comments/{comment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_snippet_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_snippet_comment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_snippet_comment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def update_snippet_comment(
    comment_id: str = Field(..., description="The unique numeric identifier of the comment to update."),
    encoded_id: str = Field(..., description="The unique identifier of the snippet to which the comment belongs."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (e.g. a short name) or as a UUID surrounded by curly-braces."),
    body: _models.SnippetComment | None = Field(None, description="The request body containing the updated comment data. Must include `content.raw` with the new comment text in raw markup format."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing comment on a snippet. Only the comment's author can make updates, and the request body must include the `content.raw` field."""

    _comment_id = _parse_int(comment_id)

    # Construct request model with validation
    try:
        _request = _models.PutSnippetsCommentsRequest(
            path=_models.PutSnippetsCommentsRequestPath(comment_id=_comment_id, encoded_id=encoded_id, workspace=workspace),
            body=_models.PutSnippetsCommentsRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_snippet_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/comments/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/comments/{comment_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_snippet_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_snippet_comment", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_snippet_comment",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def delete_snippet_comment(
    comment_id: str = Field(..., description="The unique numeric identifier of the comment to delete."),
    encoded_id: str = Field(..., description="The unique identifier of the snippet, as assigned by Bitbucket."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific comment from a snippet. This action is restricted to the comment author, snippet creator, or a workspace admin."""

    _comment_id = _parse_int(comment_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteSnippetsCommentsRequest(
            path=_models.DeleteSnippetsCommentsRequestPath(comment_id=_comment_id, encoded_id=encoded_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_snippet_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/comments/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/comments/{comment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_snippet_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_snippet_comment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_snippet_comment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def list_snippet_commits(
    encoded_id: str = Field(..., description="The unique identifier of the snippet whose commit history is being retrieved."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the commit history for a specific snippet, returning all changes made over time. Useful for auditing edits or tracking the evolution of a snippet's content."""

    # Construct request model with validation
    try:
        _request = _models.GetSnippetsByWorkspaceByEncodedIdCommitsRequest(
            path=_models.GetSnippetsByWorkspaceByEncodedIdCommitsRequestPath(encoded_id=encoded_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_snippet_commits: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/commits", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/commits"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_snippet_commits")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_snippet_commits", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_snippet_commits",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def get_snippet_commit_changes(
    encoded_id: str = Field(..., description="The unique identifier of the snippet whose commit changes you want to retrieve."),
    revision: str = Field(..., description="The SHA1 hash of the commit whose changes you want to inspect."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the changes made to a specific snippet in a given commit. Use this to inspect what was modified in a snippet at a particular point in its history."""

    # Construct request model with validation
    try:
        _request = _models.GetSnippetsByWorkspaceByEncodedIdCommitsByRevisionRequest(
            path=_models.GetSnippetsByWorkspaceByEncodedIdCommitsByRevisionRequestPath(encoded_id=encoded_id, revision=revision, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_snippet_commit_changes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/commits/{revision}", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/commits/{revision}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_snippet_commit_changes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_snippet_commit_changes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_snippet_commit_changes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def get_snippet_file_content(
    encoded_id: str = Field(..., description="The unique identifier of the snippet to retrieve the file from."),
    path: str = Field(..., description="The relative path to the target file within the snippet."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the raw content of a specific file within a snippet at its HEAD revision, bypassing the need to first fetch the snippet and extract versioned file links."""

    # Construct request model with validation
    try:
        _request = _models.GetSnippetsByWorkspaceByEncodedIdFilesByPathRequest(
            path=_models.GetSnippetsByWorkspaceByEncodedIdFilesByPathRequestPath(encoded_id=encoded_id, path=path, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_snippet_file_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/files/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/files/{path}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_snippet_file_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_snippet_file_content", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_snippet_file_content",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def check_snippet_watch_status(
    encoded_id: str = Field(..., description="The unique identifier of the snippet to check watch status for."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Checks whether the currently authenticated user is watching a specific snippet. Returns 204 if watching, 404 if not watching or if the request is made anonymously."""

    # Construct request model with validation
    try:
        _request = _models.GetSnippetsWatchRequest(
            path=_models.GetSnippetsWatchRequestPath(encoded_id=encoded_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_snippet_watch_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/watch", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/watch"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_snippet_watch_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_snippet_watch_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_snippet_watch_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def watch_snippet(
    encoded_id: str = Field(..., description="The unique identifier of the snippet to watch."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Subscribes the authenticated user to watch a specific snippet, enabling notifications for changes. Returns 204 No Content on success."""

    # Construct request model with validation
    try:
        _request = _models.PutSnippetsWatchRequest(
            path=_models.PutSnippetsWatchRequestPath(encoded_id=encoded_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for watch_snippet: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/watch", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/watch"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("watch_snippet")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("watch_snippet", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="watch_snippet",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def unwatch_snippet(
    encoded_id: str = Field(..., description="The unique identifier of the snippet to stop watching."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Stops watching a specific snippet so the authenticated user no longer receives updates for it. Returns 204 No Content on success."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSnippetsWatchRequest(
            path=_models.DeleteSnippetsWatchRequestPath(encoded_id=encoded_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unwatch_snippet: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/watch", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/watch"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unwatch_snippet")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unwatch_snippet", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unwatch_snippet",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def get_snippet_revision(
    encoded_id: str = Field(..., description="The unique identifier of the snippet to retrieve."),
    node_id: str = Field(..., description="The commit revision SHA1 hash identifying the specific historical version of the snippet to retrieve."),
    workspace: str = Field(..., description="The workspace containing the snippet, specified as either the workspace slug or the workspace UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the file contents of a snippet at a specific historical revision identified by a commit SHA1. Unlike the standard snippet endpoint, this returns the snapshot of file contents at the given revision rather than the current version."""

    # Construct request model with validation
    try:
        _request = _models.GetSnippetsByWorkspaceByEncodedIdByNodeIdRequest(
            path=_models.GetSnippetsByWorkspaceByEncodedIdByNodeIdRequestPath(encoded_id=encoded_id, node_id=node_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_snippet_revision: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/{node_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/{node_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_snippet_revision")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_snippet_revision", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_snippet_revision",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def update_snippet_at_revision(
    encoded_id: str = Field(..., description="The unique identifier of the snippet to update."),
    node_id: str = Field(..., description="The SHA1 commit revision that must match the snippet's current HEAD; the update is rejected if this is not the most recent revision."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Updates a snippet only if the specified commit revision matches the current HEAD, acting as a Compare-And-Swap (CAS) operation to prevent overwriting concurrent modifications. Fails with a 405 if the provided revision is not the latest."""

    # Construct request model with validation
    try:
        _request = _models.PutSnippetsForWorkspaceForEncodedIdForNodeIdRequest(
            path=_models.PutSnippetsForWorkspaceForEncodedIdForNodeIdRequestPath(encoded_id=encoded_id, node_id=node_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_snippet_at_revision: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/{node_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/{node_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_snippet_at_revision")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_snippet_at_revision", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_snippet_at_revision",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def delete_snippet_revision(
    encoded_id: str = Field(..., description="The unique identifier of the snippet to delete."),
    node_id: str = Field(..., description="The SHA1 commit hash identifying the specific revision of the snippet; must point to the latest commit or the request will fail."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Deletes a snippet at a specific versioned commit, but only if that commit is the latest revision. To delete a snippet unconditionally, use the base snippet delete endpoint instead."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSnippetsForWorkspaceForEncodedIdForNodeIdRequest(
            path=_models.DeleteSnippetsForWorkspaceForEncodedIdForNodeIdRequestPath(encoded_id=encoded_id, node_id=node_id, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_snippet_revision: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/{node_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/{node_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_snippet_revision")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_snippet_revision", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_snippet_revision",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def get_snippet_file_contents(
    encoded_id: str = Field(..., description="The unique identifier of the snippet to retrieve the file from."),
    node_id: str = Field(..., description="The commit revision SHA1 hash identifying the specific version of the snippet to retrieve the file from."),
    path: str = Field(..., description="The path to the target file within the snippet, relative to the snippet's root."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the raw contents of a specific file within a snippet at a given commit revision. The response includes appropriate Content-Type and Content-Disposition headers based on the file's name and type."""

    # Construct request model with validation
    try:
        _request = _models.GetSnippetsByWorkspaceByEncodedIdByNodeIdFilesByPathRequest(
            path=_models.GetSnippetsByWorkspaceByEncodedIdByNodeIdFilesByPathRequestPath(encoded_id=encoded_id, node_id=node_id, path=path, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_snippet_file_contents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/{node_id}/files/{path}", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/{node_id}/files/{path}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_snippet_file_contents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_snippet_file_contents", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_snippet_file_contents",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def get_snippet_diff(
    encoded_id: str = Field(..., description="The unique identifier of the snippet whose diff is being retrieved."),
    revision: str = Field(..., description="A revspec expression identifying the commit or range to diff, such as a commit SHA1, a branch/tag ref name, or a two-dot compare expression to diff between two refs."),
    workspace: str = Field(..., description="The workspace containing the snippet, specified as either the workspace slug or the workspace UUID surrounded by curly braces."),
    path: str | None = Field(None, description="When provided, restricts the diff output to only the specified file path within the snippet, rather than showing all changed files."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the diff of a specific snippet commit against its first parent, showing what changed in that revision. Optionally filter the diff to a single file using the path parameter."""

    # Construct request model with validation
    try:
        _request = _models.GetSnippetsDiffRequest(
            path=_models.GetSnippetsDiffRequestPath(encoded_id=encoded_id, revision=revision, workspace=workspace),
            query=_models.GetSnippetsDiffRequestQuery(path=path)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_snippet_diff: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/{revision}/diff", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/{revision}/diff"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_snippet_diff")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_snippet_diff", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_snippet_diff",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Snippets
@mcp.tool()
async def get_snippet_patch(
    encoded_id: str = Field(..., description="The unique identifier of the snippet to retrieve the patch for."),
    revision: str = Field(..., description="A revspec expression identifying the commit or range to patch against its first parent, such as a commit SHA1, a ref name, or a range expression using double-dot notation."),
    workspace: str = Field(..., description="The workspace containing the snippet, specified as either the workspace slug or the workspace UUID surrounded by curly braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the patch of a specific snippet commit against its first parent, including commit headers such as username and message. Unlike a diff, this returns separate patches for each commit on the second parent's ancestry up to the oldest common ancestor for merge commits."""

    # Construct request model with validation
    try:
        _request = _models.GetSnippetsPatchRequest(
            path=_models.GetSnippetsPatchRequestPath(encoded_id=encoded_id, revision=revision, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_snippet_patch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snippets/{workspace}/{encoded_id}/{revision}/patch", _request.path.model_dump(by_alias=True)) if _request.path else "/snippets/{workspace}/{encoded_id}/{revision}/patch"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_snippet_patch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_snippet_patch", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_snippet_patch",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Search
@mcp.tool()
async def search_team_code(
    username: str = Field(..., description="The team account to search within, specified as either the team's username or its UUID wrapped in curly braces."),
    search_query: str = Field(..., description="The search query string used to find matching code; supports advanced syntax such as scoping to a specific repository using the `repo:` qualifier, and combining multiple terms."),
    page: str | None = Field(None, description="The page number of search results to retrieve, starting at 1 for the first page."),
    pagelen: str | None = Field(None, description="The number of search results to return per page; controls pagination granularity."),
) -> dict[str, Any] | ToolResult:
    """Search across all repositories belonging to a team for code matching a given query, with results that can match file content, file paths, or both. Supports advanced query syntax for scoping searches to specific repositories and customizing returned fields."""

    _page = _parse_int(page)
    _pagelen = _parse_int(pagelen)

    # Construct request model with validation
    try:
        _request = _models.GetTeamsSearchCodeRequest(
            path=_models.GetTeamsSearchCodeRequestPath(username=username),
            query=_models.GetTeamsSearchCodeRequestQuery(search_query=search_query, page=_page, pagelen=_pagelen)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_team_code: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{username}/search/code", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{username}/search/code"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_team_code")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_team_code", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_team_code",
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
    """Retrieves the profile and details of the currently authenticated user. Useful for confirming identity or accessing user-specific information tied to the active session."""

    # Extract parameters for API call
    _http_path = "/user"
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
async def list_user_emails() -> dict[str, Any] | ToolResult:
    """Retrieves all email addresses associated with the currently authenticated user. Includes both confirmed and unconfirmed addresses."""

    # Extract parameters for API call
    _http_path = "/user/emails"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_emails")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_emails", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_emails",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def get_email(email: str = Field(..., description="The full email address to look up among the authenticated user's registered email addresses.")) -> dict[str, Any] | ToolResult:
    """Retrieves details for a specific email address belonging to the authenticated user. The response includes whether the address has been confirmed and whether it is the user's primary email."""

    # Construct request model with validation
    try:
        _request = _models.GetUserEmailsByEmailRequest(
            path=_models.GetUserEmailsByEmailRequestPath(email=email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user/emails/{email}", _request.path.model_dump(by_alias=True)) if _request.path else "/user/emails/{email}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_email", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_email",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool()
async def list_workspaces(
    sort: str | None = Field(None, description="Property name to sort the returned workspaces by; only sorting by slug is supported."),
    administrator: bool | None = Field(None, description="When set to true, returns only workspaces where the caller has admin permissions; when set to false, returns only workspaces where the caller does not have admin permissions. Omit to return all accessible workspaces regardless of admin status."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all workspaces accessible to the authenticated user, including each workspace's details and the caller's admin permissions status. Supports filtering by admin role, sorting, and pagination."""

    # Construct request model with validation
    try:
        _request = _models.GetUserWorkspacesRequest(
            query=_models.GetUserWorkspacesRequestQuery(sort=sort, administrator=administrator)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspaces: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user/workspaces"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool()
async def get_workspace_permission(workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")) -> dict[str, Any] | ToolResult:
    """Retrieves the calling user's effective (highest) permission role for a specified workspace. If the user belongs to multiple groups with different roles, only the highest privilege level is returned."""

    # Construct request model with validation
    try:
        _request = _models.GetUserWorkspacesPermissionRequest(
            path=_models.GetUserWorkspacesPermissionRequestPath(workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workspace_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user/workspaces/{workspace}/permission", _request.path.model_dump(by_alias=True)) if _request.path else "/user/workspaces/{workspace}/permission"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workspace_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workspace_permission", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workspace_permission",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Repositories
@mcp.tool()
async def list_workspace_repository_permissions_for_user(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces."),
    q: str | None = Field(None, description="A filter expression to narrow results by repository or permission level, using Bitbucket's filtering and sorting syntax. Values must be URL-encoded (e.g., encode `=` as `%3D`)."),
    sort: str | None = Field(None, description="The response property name to sort results by, using Bitbucket's filtering and sorting syntax."),
) -> dict[str, Any] | ToolResult:
    """Retrieves each repository within the specified workspace where the authenticated user has been explicitly granted access, along with their highest effective permission level (admin, write, or read). Public repositories without explicit grants are excluded from results."""

    # Construct request model with validation
    try:
        _request = _models.GetUserWorkspacesPermissionsRepositoriesRequest(
            path=_models.GetUserWorkspacesPermissionsRepositoriesRequestPath(workspace=workspace),
            query=_models.GetUserWorkspacesPermissionsRepositoriesRequestQuery(q=q, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_repository_permissions_for_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user/workspaces/{workspace}/permissions/repositories", _request.path.model_dump(by_alias=True)) if _request.path else "/user/workspaces/{workspace}/permissions/repositories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_repository_permissions_for_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_repository_permissions_for_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_repository_permissions_for_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def get_user(selected_user: str = Field(..., description="The identifier of the user to retrieve, accepted as either an Atlassian Account ID or a UUID wrapped in curly braces.")) -> dict[str, Any] | ToolResult:
    """Retrieves public profile information for a specified Bitbucket user account. Private profiles omit location, website, and account creation date fields."""

    # Construct request model with validation
    try:
        _request = _models.GetUsersRequest(
            path=_models.GetUsersRequestPath(selected_user=selected_user)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{selected_user}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{selected_user}"
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

# Tags: GPG
@mcp.tool()
async def list_user_gpg_keys(selected_user: str = Field(..., description="The identifier of the user whose GPG keys will be listed, accepted as either an Atlassian Account ID or an account UUID wrapped in curly braces.")) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of GPG public keys associated with a specified Bitbucket user. The key and subkeys fields can be included in the response using partial response syntax."""

    # Construct request model with validation
    try:
        _request = _models.GetUsersBySelectedUserGpgKeysRequest(
            path=_models.GetUsersBySelectedUserGpgKeysRequestPath(selected_user=selected_user)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_gpg_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{selected_user}/gpg-keys", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{selected_user}/gpg-keys"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_gpg_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_gpg_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_gpg_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: GPG
@mcp.tool()
async def add_gpg_key(
    selected_user: str = Field(..., description="The account identifier for the target user, accepted as either an Atlassian Account ID or a UUID surrounded by curly-braces."),
    body: _models.GpgAccountKey | None = Field(None, description="The request body containing the GPG public key to be added to the user account."),
) -> dict[str, Any] | ToolResult:
    """Adds a new GPG public key to the specified user account, enabling cryptographic verification of commits and other signed content. Returns the newly created GPG key object upon success."""

    # Construct request model with validation
    try:
        _request = _models.PostUsersGpgKeysRequest(
            path=_models.PostUsersGpgKeysRequestPath(selected_user=selected_user),
            body=_models.PostUsersGpgKeysRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_gpg_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{selected_user}/gpg-keys", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{selected_user}/gpg-keys"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_gpg_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_gpg_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_gpg_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: GPG
@mcp.tool()
async def get_user_gpg_key(
    fingerprint: str = Field(..., description="The fingerprint uniquely identifying the GPG key to retrieve."),
    selected_user: str = Field(..., description="The user whose GPG key is being retrieved, specified as either an Atlassian Account ID or a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific GPG public key belonging to a user, identified by its fingerprint. Supports partial responses to include the full key and subkey fields."""

    # Construct request model with validation
    try:
        _request = _models.GetUsersBySelectedUserGpgKeysByFingerprintRequest(
            path=_models.GetUsersBySelectedUserGpgKeysByFingerprintRequestPath(fingerprint=fingerprint, selected_user=selected_user)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_gpg_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{selected_user}/gpg-keys/{fingerprint}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{selected_user}/gpg-keys/{fingerprint}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_gpg_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_gpg_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_gpg_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: GPG
@mcp.tool()
async def delete_user_gpg_key(
    fingerprint: str = Field(..., description="The unique fingerprint identifying the GPG key to delete, used to locate the specific key within the user's account."),
    selected_user: str = Field(..., description="The account identifier for the target user, accepted as either an Atlassian Account ID or a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a specific GPG public key from a user's account, identified by its fingerprint. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteUsersGpgKeysRequest(
            path=_models.DeleteUsersGpgKeysRequestPath(fingerprint=fingerprint, selected_user=selected_user)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user_gpg_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{selected_user}/gpg-keys/{fingerprint}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{selected_user}/gpg-keys/{fingerprint}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_user_gpg_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_user_gpg_key", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_user_gpg_key",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def get_user_app_property(
    selected_user: str = Field(..., description="The identifier of the target user account, either as an Atlassian Account ID or a UUID wrapped in curly braces."),
    app_key: str = Field(..., description="The unique key identifying the Connect app whose property is being retrieved."),
    property_name: str = Field(..., description="The name of the application property to retrieve from the specified user and Connect app."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific application property value stored against a Bitbucket user account. Use this to read Connect app metadata associated with a particular user."""

    # Construct request model with validation
    try:
        _request = _models.GetUsersPropertiesRequest(
            path=_models.GetUsersPropertiesRequestPath(selected_user=selected_user, app_key=app_key, property_name=property_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_app_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{selected_user}/properties/{app_key}/{property_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{selected_user}/properties/{app_key}/{property_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_app_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_app_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_app_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def update_user_app_property(
    selected_user: str = Field(..., description="The unique identifier of the target user account, either as an Atlassian Account ID or a UUID wrapped in curly braces."),
    app_key: str = Field(..., description="The key identifying the Connect app whose property is being updated. This must correspond to a registered Connect app key."),
    property_name: str = Field(..., description="The name of the application property to update. This identifies which property value will be overwritten for the specified user and app."),
) -> dict[str, Any] | ToolResult:
    """Updates the value of a named application property stored against a specific user for a given Connect app. Use this to persist or overwrite app-specific metadata associated with a Bitbucket user account."""

    # Construct request model with validation
    try:
        _request = _models.PutUsersPropertiesRequest(
            path=_models.PutUsersPropertiesRequestPath(selected_user=selected_user, app_key=app_key, property_name=property_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user_app_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{selected_user}/properties/{app_key}/{property_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{selected_user}/properties/{app_key}/{property_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user_app_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user_app_property", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user_app_property",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: properties
@mcp.tool()
async def delete_user_app_property(
    selected_user: str = Field(..., description="The identifier of the target user account, either as an Atlassian Account ID or a UUID wrapped in curly braces."),
    app_key: str = Field(..., description="The unique key identifying the Bitbucket Connect app whose property is being deleted."),
    property_name: str = Field(..., description="The name of the application property to delete from the user's account."),
) -> dict[str, Any] | ToolResult:
    """Deletes a specific application property value stored against a Bitbucket user account. Targets a property by its Connect app key and property name."""

    # Construct request model with validation
    try:
        _request = _models.DeleteUsersPropertiesRequest(
            path=_models.DeleteUsersPropertiesRequestPath(selected_user=selected_user, app_key=app_key, property_name=property_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user_app_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{selected_user}/properties/{app_key}/{property_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{selected_user}/properties/{app_key}/{property_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_user_app_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_user_app_property", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_user_app_property",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Search
@mcp.tool()
async def search_user_code(
    selected_user: str = Field(..., description="The unique identifier of the user whose repositories will be searched — either an Atlassian Account ID or a UUID wrapped in curly braces."),
    search_query: str = Field(..., description="The search query string used to find matching code; supports advanced syntax such as scoping results to a specific repository using the `repo:` qualifier and combining multiple terms."),
    page: str | None = Field(None, description="The page number of search results to retrieve, starting at 1 for the first page."),
    pagelen: str | None = Field(None, description="The number of search results to return per page; controls pagination granularity."),
) -> dict[str, Any] | ToolResult:
    """Search across all repositories belonging to a specified user, matching against file content and/or file paths. Supports advanced query syntax including repository-scoped searches and field expansion for richer results."""

    _page = _parse_int(page)
    _pagelen = _parse_int(pagelen)

    # Construct request model with validation
    try:
        _request = _models.GetUsersSearchCodeRequest(
            path=_models.GetUsersSearchCodeRequestPath(selected_user=selected_user),
            query=_models.GetUsersSearchCodeRequestQuery(search_query=search_query, page=_page, pagelen=_pagelen)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_user_code: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{selected_user}/search/code", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{selected_user}/search/code"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_user_code")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_user_code", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_user_code",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: SSH
@mcp.tool()
async def list_user_ssh_keys(selected_user: str = Field(..., description="The identifier of the user whose SSH keys will be listed — either an Atlassian Account ID or an account UUID wrapped in curly braces.")) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of SSH public keys associated with the specified user account. Useful for auditing or managing a user's SSH authentication credentials."""

    # Construct request model with validation
    try:
        _request = _models.GetUsersBySelectedUserSshKeysRequest(
            path=_models.GetUsersBySelectedUserSshKeysRequestPath(selected_user=selected_user)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_ssh_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{selected_user}/ssh-keys", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{selected_user}/ssh-keys"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_ssh_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_ssh_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_ssh_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SSH
@mcp.tool()
async def add_ssh_key(
    selected_user: str = Field(..., description="The account identifier for the target user, either as an Atlassian Account ID or as an account UUID surrounded by curly braces."),
    body: _models.SshAccountKey | None = Field(None, description="The SSH public key payload to add to the user account, including the key type, public key string, and optional label."),
) -> dict[str, Any] | ToolResult:
    """Adds a new SSH public key to the specified user account. Returns the resulting SSH key object upon success."""

    # Construct request model with validation
    try:
        _request = _models.PostUsersSshKeysRequest(
            path=_models.PostUsersSshKeysRequestPath(selected_user=selected_user),
            body=_models.PostUsersSshKeysRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_ssh_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{selected_user}/ssh-keys", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{selected_user}/ssh-keys"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_ssh_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_ssh_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_ssh_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: SSH
@mcp.tool()
async def get_user_ssh_key(
    key_id: str = Field(..., description="The unique identifier (UUID) of the SSH key to retrieve."),
    selected_user: str = Field(..., description="The user account to retrieve the SSH key from, specified as either an Atlassian Account ID or an account UUID wrapped in curly braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific SSH public key belonging to a user account. Useful for inspecting key details such as label, value, and creation date for a given user."""

    # Construct request model with validation
    try:
        _request = _models.GetUsersBySelectedUserSshKeysByKeyIdRequest(
            path=_models.GetUsersBySelectedUserSshKeysByKeyIdRequestPath(key_id=key_id, selected_user=selected_user)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_ssh_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{selected_user}/ssh-keys/{key_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{selected_user}/ssh-keys/{key_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_ssh_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_ssh_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_ssh_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: SSH
@mcp.tool()
async def update_ssh_key(
    key_id: str = Field(..., description="The unique UUID identifier of the SSH key to update."),
    selected_user: str = Field(..., description="The account identifier for the target user, either as an Atlassian Account ID or as an account UUID surrounded by curly braces."),
    body: _models.SshAccountKey | None = Field(None, description="Request body containing the SSH key fields to update. Only the comment/label field is supported for updates."),
) -> dict[str, Any] | ToolResult:
    """Updates the comment/label of a specific SSH public key on a user's account. Note that only the comment field can be modified; to change the key itself, delete and re-add it."""

    # Construct request model with validation
    try:
        _request = _models.PutUsersSshKeysRequest(
            path=_models.PutUsersSshKeysRequestPath(key_id=key_id, selected_user=selected_user),
            body=_models.PutUsersSshKeysRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_ssh_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{selected_user}/ssh-keys/{key_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{selected_user}/ssh-keys/{key_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_ssh_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_ssh_key", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_ssh_key",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: SSH
@mcp.tool()
async def delete_user_ssh_key(
    key_id: str = Field(..., description="The unique UUID identifier of the SSH key to delete."),
    selected_user: str = Field(..., description="The account identifier for the target user, accepted as either an Atlassian Account ID or an account UUID wrapped in curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a specific SSH public key from a user's account, revoking any access associated with that key."""

    # Construct request model with validation
    try:
        _request = _models.DeleteUsersSshKeysRequest(
            path=_models.DeleteUsersSshKeysRequestPath(key_id=key_id, selected_user=selected_user)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user_ssh_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{selected_user}/ssh-keys/{key_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{selected_user}/ssh-keys/{key_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_user_ssh_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_user_ssh_key", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_user_ssh_key",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool()
async def get_workspace(workspace: str = Field(..., description="The unique identifier for the workspace, accepted as either a slug (short name) or a UUID wrapped in curly braces.")) -> dict[str, Any] | ToolResult:
    """Retrieves details for a specific Bitbucket workspace. Returns workspace metadata including settings, links, and membership information."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspaceRequest(
            path=_models.GetWorkspacesByWorkspaceRequestPath(workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workspace: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}"
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

# Tags: Workspaces, Webhooks
@mcp.tool()
async def list_workspace_webhooks(workspace: str = Field(..., description="The unique identifier for the workspace, accepted as either a slug (short name) or a UUID surrounded by curly-braces.")) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of all webhooks installed on the specified workspace. Useful for auditing or managing webhook integrations configured at the workspace level."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspaceHooksRequest(
            path=_models.GetWorkspacesByWorkspaceHooksRequestPath(workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_webhooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/hooks", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/hooks"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_webhooks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_webhooks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_webhooks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces, Webhooks
@mcp.tool()
async def get_workspace_webhook(
    uid: str = Field(..., description="The unique identifier of the installed webhook to retrieve."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the details of a specific webhook installed on a workspace, identified by its unique ID. Useful for inspecting webhook configuration, events, and status for a given workspace."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspaceHooksByUidRequest(
            path=_models.GetWorkspacesByWorkspaceHooksByUidRequestPath(uid=uid, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workspace_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/hooks/{uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/hooks/{uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workspace_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workspace_webhook", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workspace_webhook",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces, Webhooks
@mcp.tool()
async def update_workspace_webhook(
    uid: str = Field(..., description="The unique identifier of the installed webhook subscription to update."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing webhook subscription for a workspace, allowing modification of its description, URL, secret, active status, and subscribed events. The webhook secret is used to generate an HMAC hex digest signature sent in the X-Hub-Signature header on delivery."""

    # Construct request model with validation
    try:
        _request = _models.PutWorkspacesHooksRequest(
            path=_models.PutWorkspacesHooksRequestPath(uid=uid, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_workspace_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/hooks/{uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/hooks/{uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_workspace_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_workspace_webhook", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_workspace_webhook",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces, Webhooks
@mcp.tool()
async def delete_workspace_webhook(
    uid: str = Field(..., description="The unique identifier of the installed webhook subscription to delete."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific webhook subscription from a workspace, stopping all future event deliveries for that hook."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWorkspacesHooksRequest(
            path=_models.DeleteWorkspacesHooksRequestPath(uid=uid, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_workspace_webhook: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/hooks/{uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/hooks/{uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_workspace_webhook")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_workspace_webhook", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_workspace_webhook",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool()
async def list_workspace_members(workspace: str = Field(..., description="The unique identifier of the workspace, either as a slug (e.g., a short name/alias) or as a UUID surrounded by curly braces.")) -> dict[str, Any] | ToolResult:
    """Retrieves all members belonging to the specified workspace. Supports filtering by email address (up to 90 at a time) when called by a workspace administrator, integration, or workspace access token."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspaceMembersRequest(
            path=_models.GetWorkspacesByWorkspaceMembersRequestPath(workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/members", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/members"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool()
async def get_workspace_member(
    member: str = Field(..., description="The unique identifier of the member to look up, either their UUID or Atlassian account ID."),
    workspace: str = Field(..., description="The unique identifier of the workspace, either its slug (human-readable ID) or its UUID wrapped in curly braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the membership details for a specific user in a given workspace, including the full User and Workspace objects associated with that membership."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspaceMembersByMemberRequest(
            path=_models.GetWorkspacesByWorkspaceMembersByMemberRequestPath(member=member, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workspace_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/members/{member}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/members/{member}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workspace_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workspace_member", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workspace_member",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool()
async def list_workspace_permissions(
    workspace: str = Field(..., description="The workspace identifier, either the workspace slug (short name) or the workspace UUID enclosed in curly braces."),
    q: str | None = Field(None, description="A filter expression to narrow results by permission level, using Bitbucket's filtering and sorting syntax."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all members of a workspace along with their assigned permission levels (owner, collaborator, or member). Results can be filtered by permission level using the query parameter."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesPermissionsRequest(
            path=_models.GetWorkspacesPermissionsRequestPath(workspace=workspace),
            query=_models.GetWorkspacesPermissionsRequestQuery(q=q)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/permissions", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/permissions"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_permissions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_permissions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool()
async def list_workspace_repository_permissions(
    workspace: str = Field(..., description="The workspace identifier, either the workspace slug or the workspace UUID enclosed in curly braces."),
    q: str | None = Field(None, description="A query string to filter results by repository, user, or permission level using Bitbucket's filtering syntax; values must be URL-encoded."),
    sort: str | None = Field(None, description="The response property name to sort results by, using Bitbucket's sorting syntax to control the order of returned permissions."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the effective repository permissions for all repositories in a workspace, returning the highest permission level each user holds. Accessible only to workspace admins; results can be filtered and sorted by repository, user, or permission level."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspacePermissionsRepositoriesRequest(
            path=_models.GetWorkspacesByWorkspacePermissionsRepositoriesRequestPath(workspace=workspace),
            query=_models.GetWorkspacesByWorkspacePermissionsRepositoriesRequestQuery(q=q, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_repository_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/permissions/repositories", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/permissions/repositories"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_repository_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_repository_permissions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_repository_permissions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool()
async def list_repository_user_permissions_workspace(
    repo_slug: str = Field(..., description="The repository slug or UUID identifying the target repository. UUIDs must be surrounded by curly-braces."),
    workspace: str = Field(..., description="The workspace ID (slug) or UUID identifying the workspace. UUIDs must be surrounded by curly-braces."),
    q: str | None = Field(None, description="A filter expression to narrow results by user or permission level, following Bitbucket's filtering and sorting syntax. Values must be URL-encoded."),
    sort: str | None = Field(None, description="A response property name to sort results by, following Bitbucket's sorting syntax, such as a user display name field."),
) -> dict[str, Any] | ToolResult:
    """Returns the effective permission level for each user in a specified repository within a workspace. Only users with admin permission on the repository can access this resource."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspacePermissionsRepositoriesByRepoSlugRequest(
            path=_models.GetWorkspacesByWorkspacePermissionsRepositoriesByRepoSlugRequestPath(repo_slug=repo_slug, workspace=workspace),
            query=_models.GetWorkspacesByWorkspacePermissionsRepositoriesByRepoSlugRequestQuery(q=q, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_user_permissions_workspace: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/permissions/repositories/{repo_slug}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/permissions/repositories/{repo_slug}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_user_permissions_workspace")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_user_permissions_workspace", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_user_permissions_workspace",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def list_workspace_runners(workspace: str = Field(..., description="The unique identifier for the workspace, accepted as either a slug (short name) or a UUID enclosed in curly braces.")) -> dict[str, Any] | ToolResult:
    """Retrieve all pipeline runners configured for a specific workspace. Runners are used to execute Bitbucket Pipelines builds within the workspace."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspacePipelinesConfigRunnersRequest(
            path=_models.GetWorkspacesByWorkspacePipelinesConfigRunnersRequestPath(workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_runners: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/pipelines-config/runners", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/pipelines-config/runners"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_runners")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_runners", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_runners",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def create_workspace_runner(workspace: str = Field(..., description="The workspace identifier, either the workspace slug (human-readable short name) or the workspace UUID enclosed in curly braces.")) -> dict[str, Any] | ToolResult:
    """Creates a new runner for the specified workspace, enabling custom build infrastructure to execute Bitbucket Pipelines jobs."""

    # Construct request model with validation
    try:
        _request = _models.PostWorkspacesPipelinesConfigRunnersRequest(
            path=_models.PostWorkspacesPipelinesConfigRunnersRequestPath(workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_workspace_runner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/pipelines-config/runners", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/pipelines-config/runners"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_workspace_runner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_workspace_runner", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_workspace_runner",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def get_workspace_runner(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces."),
    runner_uuid: str = Field(..., description="The unique UUID identifying the runner to retrieve within the specified workspace."),
) -> dict[str, Any] | ToolResult:
    """Retrieves details for a specific Pipelines runner configured in a workspace. Useful for inspecting runner status, configuration, and metadata by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspacePipelinesConfigRunnersByRunnerUuidRequest(
            path=_models.GetWorkspacesByWorkspacePipelinesConfigRunnersByRunnerUuidRequestPath(workspace=workspace, runner_uuid=runner_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workspace_runner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/pipelines-config/runners/{runner_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/pipelines-config/runners/{runner_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workspace_runner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workspace_runner", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workspace_runner",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def update_workspace_runner(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces."),
    runner_uuid: str = Field(..., description="The unique identifier (UUID) of the runner to update within the specified workspace."),
) -> dict[str, Any] | ToolResult:
    """Updates the configuration or metadata of a specific runner within a workspace. Use this to modify runner settings such as labels, status, or other properties."""

    # Construct request model with validation
    try:
        _request = _models.PutWorkspacesPipelinesConfigRunnersRequest(
            path=_models.PutWorkspacesPipelinesConfigRunnersRequestPath(workspace=workspace, runner_uuid=runner_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_workspace_runner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/pipelines-config/runners/{runner_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/pipelines-config/runners/{runner_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_workspace_runner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_workspace_runner", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_workspace_runner",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def delete_workspace_runner(
    workspace: str = Field(..., description="The workspace identifier, either the workspace slug (short name) or the workspace UUID enclosed in curly braces."),
    runner_uuid: str = Field(..., description="The unique identifier (UUID) of the runner to delete."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific Pipelines runner from a workspace using its UUID. This removes the runner's registration and it will no longer be available to execute pipeline steps."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWorkspacesPipelinesConfigRunnersRequest(
            path=_models.DeleteWorkspacesPipelinesConfigRunnersRequestPath(workspace=workspace, runner_uuid=runner_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_workspace_runner: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/pipelines-config/runners/{runner_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/pipelines-config/runners/{runner_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_workspace_runner")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_workspace_runner", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_workspace_runner",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def list_workspace_pipeline_variables(workspace: str = Field(..., description="The unique identifier for the workspace, accepted as either a slug (human-readable short name) or a UUID wrapped in curly braces.")) -> dict[str, Any] | ToolResult:
    """Retrieves all pipeline configuration variables defined at the workspace level. These variables are available across all pipelines within the specified workspace."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspacePipelinesConfigVariablesRequest(
            path=_models.GetWorkspacesByWorkspacePipelinesConfigVariablesRequestPath(workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_pipeline_variables: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/pipelines-config/variables", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/pipelines-config/variables"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_pipeline_variables")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_pipeline_variables", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_pipeline_variables",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def create_pipeline_variable(workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID enclosed in curly braces.")) -> dict[str, Any] | ToolResult:
    """Creates a new variable at the workspace level for use across Bitbucket Pipelines. Workspace-level variables are available to all pipelines within the specified workspace."""

    # Construct request model with validation
    try:
        _request = _models.PostWorkspacesPipelinesConfigVariablesRequest(
            path=_models.PostWorkspacesPipelinesConfigVariablesRequestPath(workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_pipeline_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/pipelines-config/variables", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/pipelines-config/variables"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_pipeline_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_pipeline_variable", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_pipeline_variable",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def get_workspace_pipeline_variable(
    workspace: str = Field(..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces."),
    variable_uuid: str = Field(..., description="The unique identifier (UUID) of the workspace pipeline configuration variable to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific pipeline configuration variable at the workspace level by its UUID. Use this to inspect the details of a single workspace-scoped pipeline variable."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspacePipelinesConfigVariablesByVariableUuidRequest(
            path=_models.GetWorkspacesByWorkspacePipelinesConfigVariablesByVariableUuidRequestPath(workspace=workspace, variable_uuid=variable_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_workspace_pipeline_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/pipelines-config/variables/{variable_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/pipelines-config/variables/{variable_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_workspace_pipeline_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_workspace_pipeline_variable", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_workspace_pipeline_variable",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def update_workspace_pipeline_variable(
    workspace: str = Field(..., description="The unique identifier for the workspace, accepted as either a slug (human-readable short name) or a UUID surrounded by curly-braces."),
    variable_uuid: str = Field(..., description="The UUID of the pipeline configuration variable to update, uniquely identifying the variable within the workspace."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing pipeline configuration variable at the workspace level. Changes apply to all pipelines within the specified workspace that reference this variable."""

    # Construct request model with validation
    try:
        _request = _models.PutWorkspacesPipelinesConfigVariablesRequest(
            path=_models.PutWorkspacesPipelinesConfigVariablesRequestPath(workspace=workspace, variable_uuid=variable_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_workspace_pipeline_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/pipelines-config/variables/{variable_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/pipelines-config/variables/{variable_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_workspace_pipeline_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_workspace_pipeline_variable", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_workspace_pipeline_variable",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pipelines
@mcp.tool()
async def delete_workspace_pipeline_variable(
    workspace: str = Field(..., description="The unique identifier for the workspace, accepted as either a slug (human-readable short name) or a UUID surrounded by curly-braces."),
    variable_uuid: str = Field(..., description="The UUID of the workspace pipeline variable to delete. This uniquely identifies the specific variable to be permanently removed."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a specific pipeline configuration variable at the workspace level. This action cannot be undone and will remove the variable from all pipelines that reference it within the workspace."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWorkspacesPipelinesConfigVariablesRequest(
            path=_models.DeleteWorkspacesPipelinesConfigVariablesRequestPath(workspace=workspace, variable_uuid=variable_uuid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_workspace_pipeline_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/pipelines-config/variables/{variable_uuid}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/pipelines-config/variables/{variable_uuid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_workspace_pipeline_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_workspace_pipeline_variable", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_workspace_pipeline_variable",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces
@mcp.tool()
async def list_workspace_projects(workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly braces.")) -> dict[str, Any] | ToolResult:
    """Retrieves all projects belonging to a specified workspace. Returns a list of project resources associated with the given workspace identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspaceProjectsRequest(
            path=_models.GetWorkspacesByWorkspaceProjectsRequestPath(workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_projects: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_workspace_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_workspace_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_workspace_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def create_project(workspace: str = Field(..., description="The workspace in which to create the project, specified as either the workspace slug (human-readable ID) or the workspace UUID surrounded by curly braces.")) -> dict[str, Any] | ToolResult:
    """Creates a new project within the specified workspace, supporting optional avatar images via data-URL or external URL, privacy settings, and a unique project key."""

    # Construct request model with validation
    try:
        _request = _models.PostWorkspacesProjectsRequest(
            path=_models.PostWorkspacesProjectsRequestPath(workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects, Workspaces
@mcp.tool()
async def get_project(
    project_key: str = Field(..., description="The unique key assigned to the project, used to identify it within the workspace."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (human-readable ID) or a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves details for a specific project within a workspace. Returns project metadata including its key, name, and associated settings."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspaceProjectsByProjectKeyRequest(
            path=_models.GetWorkspacesByWorkspaceProjectsByProjectKeyRequestPath(project_key=project_key, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects/{project_key}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects/{project_key}"
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

# Tags: Projects
@mcp.tool()
async def update_project(
    project_key: str = Field(..., description="The unique key identifying the project within the workspace. This is the short alphanumeric identifier assigned to the project, not its name or UUID."),
    workspace: str = Field(..., description="The workspace in which the project resides, specified as either the workspace slug or the workspace UUID enclosed in curly braces."),
) -> dict[str, Any] | ToolResult:
    """Creates or updates a project within a workspace using the specified project key. If the key is changed in the request body, the project is relocated and the new URL is returned in the Location response header."""

    # Construct request model with validation
    try:
        _request = _models.PutWorkspacesProjectsRequest(
            path=_models.PutWorkspacesProjectsRequestPath(project_key=project_key, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects/{project_key}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects/{project_key}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def delete_project(
    project_key: str = Field(..., description="The unique key assigned to the project, identifying which project to delete."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (human-readable ID) or a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Permanently deletes a project from the specified workspace. The project must have no repositories; delete or transfer all repositories before attempting deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWorkspacesProjectsRequest(
            path=_models.DeleteWorkspacesProjectsRequestPath(project_key=project_key, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects/{project_key}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects/{project_key}"
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

# Tags: Branching model
@mcp.tool()
async def get_project_branching_model(
    project_key: str = Field(..., description="The unique key assigned to the project within the workspace."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (human-readable ID) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the read-only branching model configured at the project level, including development and production branch settings and all enabled branch types. To modify these settings, use the branching model settings endpoint."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesProjectsBranchingModelRequest(
            path=_models.GetWorkspacesProjectsBranchingModelRequestPath(project_key=project_key, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_branching_model: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects/{project_key}/branching-model", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects/{project_key}/branching-model"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_branching_model")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_branching_model", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_branching_model",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Branching model
@mcp.tool()
async def get_project_branching_model_settings(
    project_key: str = Field(..., description="The unique key assigned to the project within the workspace, used to identify which project's branching model settings to retrieve."),
    workspace: str = Field(..., description="The workspace identifier, accepted as either the workspace slug or the workspace UUID enclosed in curly braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves the raw branching model configuration for a project, including development and production branch settings, branch types, and default branch deletion behavior. Use the active branching model endpoint instead if you need to see the configuration resolved against actual current branches."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesProjectsBranchingModelSettingsRequest(
            path=_models.GetWorkspacesProjectsBranchingModelSettingsRequestPath(project_key=project_key, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_branching_model_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects/{project_key}/branching-model/settings", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects/{project_key}/branching-model/settings"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_branching_model_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_branching_model_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_branching_model_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_project_default_reviewers(
    project_key: str = Field(..., description="The unique key assigned to the project, used to identify the project within the workspace."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all default reviewers configured for a project within a workspace. These users are automatically added as reviewers to pull requests in any repository belonging to the project."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspaceProjectsByProjectKeyDefaultReviewersRequest(
            path=_models.GetWorkspacesByWorkspaceProjectsByProjectKeyDefaultReviewersRequestPath(project_key=project_key, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_default_reviewers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects/{project_key}/default-reviewers", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects/{project_key}/default-reviewers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_default_reviewers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_default_reviewers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_default_reviewers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def get_project_default_reviewer(
    project_key: str = Field(..., description="The unique identifier of the project, either its short key or its UUID surrounded by curly-braces."),
    selected_user: str = Field(..., description="The unique identifier of the default reviewer to retrieve, either their username or their account UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The unique identifier of the workspace containing the project, either its slug or its UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific default reviewer for a project within a workspace. Returns reviewer details for the specified user if they are configured as a default reviewer on the project."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspaceProjectsByProjectKeyDefaultReviewersBySelectedUserRequest(
            path=_models.GetWorkspacesByWorkspaceProjectsByProjectKeyDefaultReviewersBySelectedUserRequestPath(project_key=project_key, selected_user=selected_user, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_default_reviewer: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects/{project_key}/default-reviewers/{selected_user}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects/{project_key}/default-reviewers/{selected_user}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_default_reviewer")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_default_reviewer", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_default_reviewer",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def add_project_default_reviewer(
    project_key: str = Field(..., description="The unique identifier for the project, either its short key or its UUID surrounded by curly-braces."),
    selected_user: str = Field(..., description="The unique identifier for the user to add as a default reviewer, either their username or their account UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The unique identifier for the workspace, either its slug (ID) or its UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Adds a specified user to the default reviewers list for a project in a workspace. This operation is idempotent, so adding an already-listed reviewer will not cause errors."""

    # Construct request model with validation
    try:
        _request = _models.PutWorkspacesProjectsDefaultReviewersRequest(
            path=_models.PutWorkspacesProjectsDefaultReviewersRequestPath(project_key=project_key, selected_user=selected_user, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_project_default_reviewer: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects/{project_key}/default-reviewers/{selected_user}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects/{project_key}/default-reviewers/{selected_user}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_project_default_reviewer")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_project_default_reviewer", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_project_default_reviewer",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def remove_project_default_reviewer(
    project_key: str = Field(..., description="The unique identifier of the project, either its short key or its UUID surrounded by curly-braces."),
    selected_user: str = Field(..., description="The unique identifier of the user to remove as a default reviewer, either their username or their account UUID surrounded by curly-braces."),
    workspace: str = Field(..., description="The unique identifier of the workspace containing the project, either its slug or its UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Removes a specific user from a project's default reviewers list. Once removed, the user will no longer be automatically added as a reviewer on new pull requests in that project."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWorkspacesProjectsDefaultReviewersRequest(
            path=_models.DeleteWorkspacesProjectsDefaultReviewersRequestPath(project_key=project_key, selected_user=selected_user, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_project_default_reviewer: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects/{project_key}/default-reviewers/{selected_user}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects/{project_key}/default-reviewers/{selected_user}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_project_default_reviewer")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_project_default_reviewer", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_project_default_reviewer",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deployments
@mcp.tool()
async def list_project_deploy_keys(
    project_key: str = Field(..., description="The unique key identifier assigned to the project, used to target the specific project whose deploy keys will be listed."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (human-readable short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all deploy keys associated with a specific project in a workspace. Deploy keys grant read or read/write access to a repository for CI/CD and automation purposes."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspaceProjectsByProjectKeyDeployKeysRequest(
            path=_models.GetWorkspacesByWorkspaceProjectsByProjectKeyDeployKeysRequestPath(project_key=project_key, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_deploy_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects/{project_key}/deploy-keys", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects/{project_key}/deploy-keys"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_deploy_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_deploy_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_deploy_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deployments
@mcp.tool()
async def create_project_deploy_key(
    project_key: str = Field(..., description="The unique key identifier assigned to the project (e.g., 'TEST_PROJECT'). This is the short key label, not the project name or UUID."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (human-readable ID) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Creates a new deploy key for a specified project within a workspace, enabling secure read or read/write access to the project's repositories."""

    # Construct request model with validation
    try:
        _request = _models.PostWorkspacesProjectsDeployKeysRequest(
            path=_models.PostWorkspacesProjectsDeployKeysRequestPath(project_key=project_key, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project_deploy_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects/{project_key}/deploy-keys", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects/{project_key}/deploy-keys"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_project_deploy_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_project_deploy_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_project_deploy_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deployments
@mcp.tool()
async def get_project_deploy_key(
    key_id: str = Field(..., description="The unique numeric identifier of the deploy key to retrieve."),
    project_key: str = Field(..., description="The unique key assigned to the project, used to identify it within the workspace."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific deploy key associated with a project, identified by its key ID. Returns the full deploy key details for the given workspace and project."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspaceProjectsByProjectKeyDeployKeysByKeyIdRequest(
            path=_models.GetWorkspacesByWorkspaceProjectsByProjectKeyDeployKeysByKeyIdRequestPath(key_id=key_id, project_key=project_key, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_deploy_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects/{project_key}/deploy-keys/{key_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects/{project_key}/deploy-keys/{key_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_deploy_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_deploy_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_deploy_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Deployments
@mcp.tool()
async def delete_project_deploy_key(
    key_id: str = Field(..., description="The unique numeric identifier of the deploy key to be deleted from the project."),
    project_key: str = Field(..., description="The unique key identifier assigned to the project, used to reference the project within the workspace."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Permanently removes a specific deploy key from a project in the given workspace. This revokes any access granted to systems using that key."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWorkspacesProjectsDeployKeysRequest(
            path=_models.DeleteWorkspacesProjectsDeployKeysRequestPath(key_id=key_id, project_key=project_key, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project_deploy_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects/{project_key}/deploy-keys/{key_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects/{project_key}/deploy-keys/{key_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_project_deploy_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_project_deploy_key", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_project_deploy_key",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_project_group_permissions(
    project_key: str = Field(..., description="The unique key identifying the project within the workspace, as assigned when the project was created."),
    workspace: str = Field(..., description="The workspace identifier, accepted as either the workspace slug or the workspace UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of explicit group-level permissions configured for a specific project within a workspace. Only explicitly assigned group permissions are returned; inherited or implicit permissions are not included."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspaceProjectsByProjectKeyPermissionsConfigGroupsRequest(
            path=_models.GetWorkspacesByWorkspaceProjectsByProjectKeyPermissionsConfigGroupsRequestPath(project_key=project_key, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_group_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects/{project_key}/permissions-config/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects/{project_key}/permissions-config/groups"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_group_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_group_permissions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_group_permissions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Projects
@mcp.tool()
async def list_project_user_permissions(
    project_key: str = Field(..., description="The unique key identifying the project within the workspace, as assigned when the project was created."),
    workspace: str = Field(..., description="The workspace identifier, either as a slug (short name) or as a UUID surrounded by curly-braces."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of explicit user-level permissions configured for a specific project within a workspace. Only directly assigned user permissions are returned; inherited or group-based permissions are not included."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesByWorkspaceProjectsByProjectKeyPermissionsConfigUsersRequest(
            path=_models.GetWorkspacesByWorkspaceProjectsByProjectKeyPermissionsConfigUsersRequestPath(project_key=project_key, workspace=workspace)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_user_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/projects/{project_key}/permissions-config/users", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/projects/{project_key}/permissions-config/users"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_user_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_user_permissions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_user_permissions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Workspaces, Pullrequests
@mcp.tool()
async def list_user_pull_requests_in_workspace(
    selected_user: str = Field(..., description="The identifier of the pull request author — accepts a username, an Atlassian ID, or a UUID wrapped in curly braces."),
    workspace: str = Field(..., description="The identifier of the workspace — accepts a workspace slug or a UUID wrapped in curly braces."),
    state: Literal["OPEN", "MERGED", "DECLINED", "SUPERSEDED"] | None = Field(None, description="Filters results to pull requests in the specified state. Repeat this parameter to include multiple states simultaneously; omitting it returns only open pull requests."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all pull requests authored by a specified user within a given workspace. Supports filtering by one or more states and allows sorting and filtering of results."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesPullrequestsRequest(
            path=_models.GetWorkspacesPullrequestsRequestPath(selected_user=selected_user, workspace=workspace),
            query=_models.GetWorkspacesPullrequestsRequestQuery(state=state)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_pull_requests_in_workspace: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/pullrequests/{selected_user}", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/pullrequests/{selected_user}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_pull_requests_in_workspace")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_pull_requests_in_workspace", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_pull_requests_in_workspace",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Search
@mcp.tool()
async def search_workspace_code(
    workspace: str = Field(..., description="The workspace to search within, specified as either the workspace slug or its UUID wrapped in curly braces."),
    search_query: str = Field(..., description="The search query string used to match code content or file paths, supporting the same syntax as the Bitbucket UI including repository-scoped filters."),
    page: str | None = Field(None, description="The page number of search results to retrieve, starting at 1 for the first page."),
    pagelen: str | None = Field(None, description="The number of search results to return per page; controls pagination granularity."),
) -> dict[str, Any] | ToolResult:
    """Search across all repositories in a workspace by code content, file path, or both. Supports scoped queries (e.g., limiting to a specific repository) and field expansion for richer response data."""

    _page = _parse_int(page)
    _pagelen = _parse_int(pagelen)

    # Construct request model with validation
    try:
        _request = _models.GetWorkspacesSearchCodeRequest(
            path=_models.GetWorkspacesSearchCodeRequestPath(workspace=workspace),
            query=_models.GetWorkspacesSearchCodeRequestQuery(search_query=search_query, page=_page, pagelen=_pagelen)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_workspace_code: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/workspaces/{workspace}/search/code", _request.path.model_dump(by_alias=True)) if _request.path else "/workspaces/{workspace}/search/code"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_workspace_code")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_workspace_code", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_workspace_code",
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
        print("  python bitbucket_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Bitbucket MCP Server")

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
    logger.info("Starting Bitbucket MCP Server")
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

#!/usr/bin/env python3
"""
Notion MCP Server

API Info:
- Terms of Service: https://notion.notion.site/Terms-and-Privacy-28ffdd083dc3473e9c2da6ec011b58ac

Generated: 2026-04-23 21:30:15 UTC
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

BASE_URL = os.getenv("BASE_URL", "https://api.notion.com")
SERVER_NAME = "Notion"
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
    'bearerAuth',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["bearerAuth"] = _auth.OAuth2Auth()
    logging.info("Authentication configured: bearerAuth")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for bearerAuth not configured: {error_msg}")
    _auth_handlers["bearerAuth"] = None

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

mcp = FastMCP("Notion", middleware=[_JsonCoercionMiddleware()])

# Tags: Users
@mcp.tool()
async def get_self(notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version 2026-03-11.")) -> dict[str, Any] | ToolResult:
    """Retrieve the bot user associated with your API token. This returns information about the authenticated user making the request."""

    # Construct request model with validation
    try:
        _request = _models.GetSelfRequest(
            header=_models.GetSelfRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_self: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/users/me"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_self")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_self", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_self",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Users
@mcp.tool()
async def get_user(
    user_id: str = Field(..., description="The unique identifier of the user to retrieve."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version 2026-03-11."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific user by their ID. Returns the user's profile information and details."""

    # Construct request model with validation
    try:
        _request = _models.GetUserRequest(
            path=_models.GetUserRequestPath(user_id=user_id),
            header=_models.GetUserRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/users/{user_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

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

# Tags: Users
@mcp.tool()
async def list_users(
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="API version to use for this request. Must be set to the latest version 2026-03-11 to ensure compatibility with current API behavior."),
    page_size: float | None = Field(None, description="Number of users to return per page for pagination. Controls the batch size of results in the response."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of all users in the system. Use pagination parameters to control result size and navigate through user records."""

    # Construct request model with validation
    try:
        _request = _models.GetUsersRequest(
            query=_models.GetUsersRequestQuery(page_size=page_size),
            header=_models.GetUsersRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/users"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

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

# Tags: Pages
@mcp.tool()
async def create_page(
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version 2026-03-11."),
    parent: _models.PostPageBodyParentV0 | _models.PostPageBodyParentV1 | _models.PostPageBodyParentV2 | _models.PostPageBodyParentV3 | None = Field(None, description="The parent location where the page will be created, typically a database or another page."),
    properties: dict[str, _models.PostPageBodyPropertiesValueV0 | _models.PostPageBodyPropertiesValueV1 | _models.PostPageBodyPropertiesValueV2 | _models.PostPageBodyPropertiesValueV3 | _models.PostPageBodyPropertiesValueV4 | _models.PostPageBodyPropertiesValueV5 | _models.PostPageBodyPropertiesValueV6 | _models.PostPageBodyPropertiesValueV7 | _models.PostPageBodyPropertiesValueV8 | _models.PostPageBodyPropertiesValueV9 | _models.PostPageBodyPropertiesValueV10 | _models.PostPageBodyPropertiesValueV11 | _models.PostPageBodyPropertiesValueV12 | _models.PostPageBodyPropertiesValueV13 | _models.PostPageBodyPropertiesValueV14 | _models.PostPageBodyPropertiesValueV15] | None = Field(None, description="The page properties (title, custom fields, etc.) to set on the new page."),
    icon: _models.FileUploadPageIconRequest | _models.EmojiPageIconRequest | _models.ExternalPageIconRequest | _models.CustomEmojiPageIconRequest | _models.IconPageIconRequest | None = Field(None, description="An optional icon to display for the page (emoji, file reference, or external URL)."),
    cover: _models.FileUploadPageCoverRequest | _models.ExternalPageCoverRequest | None = Field(None, description="An optional cover image to display at the top of the page (file reference or external URL)."),
    children: list[_models.BlockObjectRequest] | None = Field(None, description="An optional array of child blocks to add to the page during creation. Maximum of 100 blocks allowed.", max_length=100),
    template: _models.PostPageBodyTemplate | None = Field(None, description="An optional template configuration to apply to the page upon creation."),
    position: _models.PagePositionSchema | None = Field(None, description="An optional position specification to control where the page appears relative to siblings (e.g., before/after another page)."),
) -> dict[str, Any] | ToolResult:
    """Creates a new page in Notion. Specify the parent location, page properties, and optional visual elements like icons and covers. You can also include child blocks and apply templates during creation."""

    # Construct request model with validation
    try:
        _request = _models.PostPageRequest(
            header=_models.PostPageRequestHeader(notion_version=notion_version),
            body=_models.PostPageRequestBody(parent=parent, properties=properties, icon=icon, cover=cover, children=children, template=template, position=position)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_page: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pages"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_page")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_page", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_page",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pages
@mcp.tool()
async def get_page(
    page_id: str = Field(..., description="The unique identifier of the page to retrieve."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11."),
    filter_properties: list[str] | None = Field(None, description="Optional list of property IDs to include in the response. Only properties that exist on the page will be returned; up to 100 properties can be specified. Properties not in this list will be excluded from the response.", max_length=100),
) -> dict[str, Any] | ToolResult:
    """Retrieve a single page by its ID from Notion. Optionally filter the response to include only specified properties."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAPageRequest(
            path=_models.RetrieveAPageRequestPath(page_id=page_id),
            query=_models.RetrieveAPageRequestQuery(filter_properties=filter_properties),
            header=_models.RetrieveAPageRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_page: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pages/{page_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pages/{page_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_page")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_page", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_page",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pages
@mcp.tool()
async def update_page(
    page_id: str = Field(..., description="The unique identifier of the page to update."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11."),
    properties: dict[str, _models.PatchPageBodyPropertiesValueV0 | _models.PatchPageBodyPropertiesValueV1 | _models.PatchPageBodyPropertiesValueV2 | _models.PatchPageBodyPropertiesValueV3 | _models.PatchPageBodyPropertiesValueV4 | _models.PatchPageBodyPropertiesValueV5 | _models.PatchPageBodyPropertiesValueV6 | _models.PatchPageBodyPropertiesValueV7 | _models.PatchPageBodyPropertiesValueV8 | _models.PatchPageBodyPropertiesValueV9 | _models.PatchPageBodyPropertiesValueV10 | _models.PatchPageBodyPropertiesValueV11 | _models.PatchPageBodyPropertiesValueV12 | _models.PatchPageBodyPropertiesValueV13 | _models.PatchPageBodyPropertiesValueV14 | _models.PatchPageBodyPropertiesValueV15] | None = Field(None, description="Page properties to update, such as title and custom property values. Structure depends on the page's database schema."),
    icon: _models.FileUploadPageIconRequest | _models.EmojiPageIconRequest | _models.ExternalPageIconRequest | _models.CustomEmojiPageIconRequest | _models.IconPageIconRequest | None = Field(None, description="The page's icon, which can be an emoji, external URL, or file reference."),
    cover: _models.FileUploadPageCoverRequest | _models.ExternalPageCoverRequest | None = Field(None, description="The page's cover image, which can be an external URL or file reference."),
    is_locked: bool | None = Field(None, description="Whether to lock the page from editing in the Notion app UI. If not provided, the current lock state remains unchanged."),
    template: _models.PatchPageBodyTemplate | None = Field(None, description="A template object containing content to apply to the page. When combined with erase_content, the template content replaces existing content."),
    erase_content: bool | None = Field(None, description="Whether to erase all existing page content. When used with a template, the template content replaces the erased content. When used alone, simply clears the page."),
    in_trash: bool | None = Field(None, description="Whether to move the page to or restore it from trash."),
    is_archived: bool | None = Field(None, description="Whether to archive the page, hiding it from the workspace while preserving its content."),
) -> dict[str, Any] | ToolResult:
    """Update a Notion page's properties, appearance, content, and metadata. Supports modifying page title/properties, icon, cover image, lock status, archived state, and content via template replacement or erasure."""

    # Construct request model with validation
    try:
        _request = _models.PatchPageRequest(
            path=_models.PatchPageRequestPath(page_id=page_id),
            header=_models.PatchPageRequestHeader(notion_version=notion_version),
            body=_models.PatchPageRequestBody(properties=properties, icon=icon, cover=cover, is_locked=is_locked, template=template, erase_content=erase_content, in_trash=in_trash, is_archived=is_archived)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_page: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pages/{page_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pages/{page_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_page")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_page", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_page",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pages
@mcp.tool()
async def move_page(
    page_id: str = Field(..., description="The unique identifier of the page to move."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version 2026-03-11."),
    parent: _models.MovePageBodyParentV0 | _models.MovePageBodyParentV1 = Field(..., description="The new parent location for the page. This specifies where the page will be moved to in the hierarchy."),
) -> dict[str, Any] | ToolResult:
    """Move a page to a new parent location within Notion. The page will be relocated under the specified parent, updating its position in the page hierarchy."""

    # Construct request model with validation
    try:
        _request = _models.MovePageRequest(
            path=_models.MovePageRequestPath(page_id=page_id),
            header=_models.MovePageRequestHeader(notion_version=notion_version),
            body=_models.MovePageRequestBody(parent=parent)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for move_page: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pages/{page_id}/move", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pages/{page_id}/move"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("move_page")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("move_page", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="move_page",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pages
@mcp.tool()
async def get_page_property(
    page_id: str = Field(..., description="The unique identifier of the Notion page containing the property."),
    property_id: str = Field(..., description="The unique identifier of the property to retrieve from the page."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to 2026-03-11 or later for compatibility with current API features."),
    page_size: int | None = Field(None, description="The maximum number of items to return in the response. Controls pagination size for the property results."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific property item from a Notion page. Use this to fetch individual property values associated with a page."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAPagePropertyRequest(
            path=_models.RetrieveAPagePropertyRequestPath(page_id=page_id, property_id=property_id),
            query=_models.RetrieveAPagePropertyRequestQuery(page_size=page_size),
            header=_models.RetrieveAPagePropertyRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_page_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pages/{page_id}/properties/{property_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pages/{page_id}/properties/{property_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_page_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_page_property", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_page_property",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pages
@mcp.tool()
async def get_page_markdown(
    page_id: str = Field(..., description="The unique identifier of the Notion page to retrieve."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11."),
    include_transcript: bool | None = Field(None, description="Whether to include full meeting note transcripts in the markdown output. When false (default), meeting notes are represented as placeholders with URLs instead of full transcript text."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a Notion page in markdown format. Optionally include meeting note transcripts or use placeholder URLs instead."""

    # Construct request model with validation
    try:
        _request = _models.RetrievePageMarkdownRequest(
            path=_models.RetrievePageMarkdownRequestPath(page_id=page_id),
            query=_models.RetrievePageMarkdownRequestQuery(include_transcript=include_transcript),
            header=_models.RetrievePageMarkdownRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_page_markdown: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pages/{page_id}/markdown", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pages/{page_id}/markdown"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_page_markdown")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_page_markdown", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_page_markdown",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pages
@mcp.tool()
async def update_page_markdown(
    page_id: str = Field(..., description="The unique identifier of the page to update."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version: 2026-03-11."),
    type_: Literal["insert_content"] = Field(..., alias="type", description="The operation type. Must always be set to 'insert_content' to specify the content modification mode."),
    insert_content: _models.UpdatePageMarkdownBodyInsertContent | None = Field(None, description="Configuration for inserting new markdown content into the page at a specified location."),
    replace_content_range: _models.UpdatePageMarkdownBodyReplaceContentRange | None = Field(None, description="Configuration for replacing a specific range of content within the page using markdown."),
    update_content: _models.UpdatePageMarkdownBodyUpdateContent | None = Field(None, description="Configuration for updating content using search-and-replace operations to find and modify specific text."),
    replace_content: _models.UpdatePageMarkdownBodyReplaceContent | None = Field(None, description="Configuration for replacing the entire page content with new markdown, removing all existing content."),
) -> dict[str, Any] | ToolResult:
    """Update a Notion page's content using markdown. Supports inserting new content, replacing specific ranges, performing search-and-replace operations, or replacing the entire page content."""

    # Construct request model with validation
    try:
        _request = _models.UpdatePageMarkdownRequest(
            path=_models.UpdatePageMarkdownRequestPath(page_id=page_id),
            header=_models.UpdatePageMarkdownRequestHeader(notion_version=notion_version),
            body=_models.UpdatePageMarkdownRequestBody(type_=type_, insert_content=insert_content, replace_content_range=replace_content_range, update_content=update_content, replace_content=replace_content)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_page_markdown: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pages/{page_id}/markdown", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pages/{page_id}/markdown"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_page_markdown")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_page_markdown", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_page_markdown",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Blocks
@mcp.tool()
async def get_block(
    block_id: str = Field(..., description="The unique identifier of the block to retrieve."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to 2026-03-11 (the latest version)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific block by its ID from Notion. Returns the block's properties and content."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveABlockRequest(
            path=_models.RetrieveABlockRequestPath(block_id=block_id),
            header=_models.RetrieveABlockRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_block: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/blocks/{block_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/blocks/{block_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_block")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_block", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_block",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Blocks
@mcp.tool()
async def update_block(
    block_id: str = Field(..., description="The unique identifier of the block to update."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11."),
    body: _models.UpdateABlockBodyV0V0 | _models.UpdateABlockBodyV0V1 | _models.UpdateABlockBodyV0V2 | _models.UpdateABlockBodyV0V3 | _models.UpdateABlockBodyV0V4 | _models.UpdateABlockBodyV0V5 | _models.UpdateABlockBodyV0V6 | _models.UpdateABlockBodyV0V7 | _models.UpdateABlockBodyV0V8 | _models.UpdateABlockBodyV0V9 | _models.UpdateABlockBodyV0V10 | _models.UpdateABlockBodyV0V11 | _models.UpdateABlockBodyV0V12 | _models.UpdateABlockBodyV0V13 | _models.UpdateABlockBodyV0V14 | _models.UpdateABlockBodyV0V15 | _models.UpdateABlockBodyV0V16 | _models.UpdateABlockBodyV0V17 | _models.UpdateABlockBodyV0V18 | _models.UpdateABlockBodyV0V19 | _models.UpdateABlockBodyV0V20 | _models.UpdateABlockBodyV0V21 | _models.UpdateABlockBodyV0V22 | _models.UpdateABlockBodyV0V23 | _models.UpdateABlockBodyV0V24 | _models.UpdateABlockBodyV0V25 | _models.UpdateABlockBodyV0V26 | _models.UpdateABlockBodyV0V27 | _models.UpdateABlockBodyV0V28 | _models.UpdateABlockBodyV0V29 | _models.UpdateABlockBodyV1 = Field(..., description="The block update payload containing the properties to modify."),
) -> dict[str, Any] | ToolResult:
    """Update the properties of an existing block in Notion. Modify block content, formatting, or other attributes using the provided block ID."""

    # Construct request model with validation
    try:
        _request = _models.UpdateABlockRequest(
            path=_models.UpdateABlockRequestPath(block_id=block_id),
            header=_models.UpdateABlockRequestHeader(notion_version=notion_version),
            body=_models.UpdateABlockRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_block: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/blocks/{block_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/blocks/{block_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_block")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_block", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_block",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Blocks
@mcp.tool()
async def delete_block(
    block_id: str = Field(..., description="The unique identifier of the block to delete."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11."),
) -> dict[str, Any] | ToolResult:
    """Permanently delete a block from a Notion workspace. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteABlockRequest(
            path=_models.DeleteABlockRequestPath(block_id=block_id),
            header=_models.DeleteABlockRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_block: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/blocks/{block_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/blocks/{block_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_block")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_block", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_block",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Blocks
@mcp.tool()
async def list_block_children(
    block_id: str = Field(..., description="The unique identifier of the parent block whose children you want to retrieve."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to 2026-03-11 or later for compatibility with current API features."),
    page_size: float | None = Field(None, description="The maximum number of child blocks to return in a single response. Use pagination to retrieve additional results if needed."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all child blocks contained within a specified parent block. Use this to navigate the hierarchical structure of Notion blocks and access nested content."""

    # Construct request model with validation
    try:
        _request = _models.GetBlockChildrenRequest(
            path=_models.GetBlockChildrenRequestPath(block_id=block_id),
            query=_models.GetBlockChildrenRequestQuery(page_size=page_size),
            header=_models.GetBlockChildrenRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_block_children: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/blocks/{block_id}/children", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/blocks/{block_id}/children"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_block_children")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_block_children", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_block_children",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Blocks
@mcp.tool()
async def append_block_children(
    block_id: str = Field(..., description="The unique identifier of the parent block to which children will be appended."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11."),
    children: list[_models.BlockObjectRequest] = Field(..., description="An array of child block objects to append. Maximum of 100 blocks per request. Order in the array determines the sequence of appended blocks.", max_length=100),
    position: _models.ContentPositionSchema | None = Field(None, description="Optional positioning configuration that specifies where the child blocks should be inserted relative to existing children."),
) -> dict[str, Any] | ToolResult:
    """Append child blocks to a parent block. Allows adding up to 100 child blocks in a single request, with optional positioning control."""

    # Construct request model with validation
    try:
        _request = _models.PatchBlockChildrenRequest(
            path=_models.PatchBlockChildrenRequestPath(block_id=block_id),
            header=_models.PatchBlockChildrenRequestHeader(notion_version=notion_version),
            body=_models.PatchBlockChildrenRequestBody(children=children, position=position)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for append_block_children: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/blocks/{block_id}/children", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/blocks/{block_id}/children"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("append_block_children")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("append_block_children", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="append_block_children",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Data sources
@mcp.tool()
async def get_data_source(
    data_source_id: str = Field(..., description="The unique identifier of the data source to retrieve."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version 2026-03-11."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific data source by its ID. Returns the complete configuration and metadata for the requested data source."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveADataSourceRequest(
            path=_models.RetrieveADataSourceRequestPath(data_source_id=data_source_id),
            header=_models.RetrieveADataSourceRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_data_source: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/data_sources/{data_source_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/data_sources/{data_source_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_data_source")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_data_source", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_data_source",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Data sources
@mcp.tool()
async def update_data_source(
    data_source_id: str = Field(..., description="The unique identifier of the data source to update."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11."),
    database_id: str = Field(..., description="The unique identifier of the parent database containing this data source. Accepts the ID with or without dashes (e.g., 195de9221179449fab8075a27c979105)."),
    title: list[_models.RichTextItemRequest] | None = Field(None, description="The display title of the data source as it appears in Notion. Maximum length is 100 characters.", max_length=100),
    icon: _models.FileUploadPageIconRequest | _models.EmojiPageIconRequest | _models.ExternalPageIconRequest | _models.CustomEmojiPageIconRequest | _models.IconPageIconRequest | None = Field(None, description="The icon to display for the data source page."),
    properties: dict[str, _models.UpdateADataSourceBodyPropertiesValueV0 | _models.UpdateADataSourceBodyPropertiesValueV1] | None = Field(None, description="The property schema configuration for the data source. Provide an object where keys are property names or IDs and values are property configuration objects. Set a property to null to remove it."),
    in_trash: bool | None = Field(None, description="Whether to move the data source to or from the trash. If not provided, the trash status remains unchanged."),
) -> dict[str, Any] | ToolResult:
    """Update a data source in Notion, including its title, icon, properties, and trash status. Use the database_id to specify the parent database containing this data source."""

    # Construct request model with validation
    try:
        _request = _models.UpdateADataSourceRequest(
            path=_models.UpdateADataSourceRequestPath(data_source_id=data_source_id),
            header=_models.UpdateADataSourceRequestHeader(notion_version=notion_version),
            body=_models.UpdateADataSourceRequestBody(title=title, icon=icon, properties=properties, in_trash=in_trash,
                parent=_models.UpdateADataSourceRequestBodyParent(database_id=database_id))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_data_source: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/data_sources/{data_source_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/data_sources/{data_source_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_data_source")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_data_source", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_data_source",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Data sources
@mcp.tool()
async def query_data_source(
    data_source_id: str = Field(..., description="The unique identifier of the data source to query."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version: 2026-03-11."),
    filter_properties: list[str] | None = Field(None, description="An array of properties to filter results by. Order and format depend on the data source schema."),
    sorts: list[_models.PostDatabaseQueryBodySortsItemV0 | _models.PostDatabaseQueryBodySortsItemV1] | None = Field(None, description="An array of sort specifications to order results. Order of array elements determines sort priority."),
    filter_: _models.PostDatabaseQueryBodyFilterV0V0 | _models.PostDatabaseQueryBodyFilterV0V1 | _models.PropertyFilter | _models.TimestampCreatedTimeFilter | _models.TimestampLastEditedTimeFilter | None = Field(None, alias="filter", description="A filter object to narrow results based on data source properties and values."),
    page_size: float | None = Field(None, description="The maximum number of results to return per request. Used for pagination control."),
    in_trash: bool | None = Field(None, description="If true, include only items in the trash. If false or omitted, exclude trashed items."),
    result_type: Literal["page", "data_source"] | None = Field(None, description="Optionally restrict results to a specific type: 'page' for pages only, or 'data_source' for data sources only. Defaults to returning both types (wiki databases only)."),
) -> dict[str, Any] | ToolResult:
    """Execute a query against a data source to retrieve filtered, sorted results. Supports pagination and optional filtering by result type (pages or data sources)."""

    # Construct request model with validation
    try:
        _request = _models.PostDatabaseQueryRequest(
            path=_models.PostDatabaseQueryRequestPath(data_source_id=data_source_id),
            query=_models.PostDatabaseQueryRequestQuery(filter_properties=filter_properties),
            header=_models.PostDatabaseQueryRequestHeader(notion_version=notion_version),
            body=_models.PostDatabaseQueryRequestBody(sorts=sorts, filter_=filter_, page_size=page_size, in_trash=in_trash, result_type=result_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for query_data_source: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/data_sources/{data_source_id}/query", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/data_sources/{data_source_id}/query"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("query_data_source")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("query_data_source", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="query_data_source",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Data sources
@mcp.tool()
async def create_data_source(
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version 2026-03-11."),
    database_id: str = Field(..., description="The unique identifier of the parent Notion database where the data source will be created. Accepts the ID with or without dashes (e.g., 195de9221179449fab8075a27c979105)."),
    properties: dict[str, _models.PropertyConfigurationRequest] = Field(..., description="The property schema object that defines the structure and types of properties for this data source."),
    title: list[_models.RichTextItemRequest] | None = Field(None, description="The display name for the data source as it will appear in Notion. Limited to a maximum of 100 characters.", max_length=100),
    icon: _models.FileUploadPageIconRequest | _models.EmojiPageIconRequest | _models.ExternalPageIconRequest | _models.CustomEmojiPageIconRequest | _models.IconPageIconRequest | None = Field(None, description="An icon to visually represent the data source in the Notion interface."),
) -> dict[str, Any] | ToolResult:
    """Create a new data source within a Notion database by defining its property schema. This establishes the structure and metadata for how data will be organized in the specified parent database."""

    # Construct request model with validation
    try:
        _request = _models.CreateADatabaseRequest(
            header=_models.CreateADatabaseRequestHeader(notion_version=notion_version),
            body=_models.CreateADatabaseRequestBody(properties=properties, title=title, icon=icon,
                parent=_models.CreateADatabaseRequestBodyParent(database_id=database_id))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_data_source: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/data_sources"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_data_source")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_data_source", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_data_source",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Data sources
@mcp.tool()
async def list_data_source_templates(
    data_source_id: str = Field(..., description="The unique identifier of the data source containing the templates to list."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Currently supports version 2026-03-11."),
    name: str | None = Field(None, description="Filter templates by name using case-insensitive substring matching. Only templates whose names contain this value will be returned."),
    page_size: int | None = Field(None, description="The maximum number of templates to return in the response. Must be between 1 and 100 items.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of templates available within a specific data source, with optional filtering by name."""

    # Construct request model with validation
    try:
        _request = _models.ListDataSourceTemplatesRequest(
            path=_models.ListDataSourceTemplatesRequestPath(data_source_id=data_source_id),
            query=_models.ListDataSourceTemplatesRequestQuery(name=name, page_size=page_size),
            header=_models.ListDataSourceTemplatesRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_data_source_templates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/data_sources/{data_source_id}/templates", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/data_sources/{data_source_id}/templates"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_data_source_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_data_source_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_data_source_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Databases
@mcp.tool()
async def get_database(
    database_id: str = Field(..., description="The unique identifier of the database to retrieve."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version 2026-03-11."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific database by its ID. Returns the database's properties, configuration, and metadata."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveDatabaseRequest(
            path=_models.RetrieveDatabaseRequestPath(database_id=database_id),
            header=_models.RetrieveDatabaseRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_database: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/databases/{database_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/databases/{database_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_database")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_database", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_database",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Databases
@mcp.tool()
async def update_database(
    database_id: str = Field(..., description="The unique identifier of the database to update."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11."),
    parent: _models.UpdateDatabaseBodyParent | None = Field(None, description="The parent page or workspace to move the database to. If omitted, the database location remains unchanged."),
    title: list[_models.RichTextItemRequest] | None = Field(None, description="The new title for the database. Must not exceed 100 characters. If omitted, the current title is preserved.", max_length=100),
    description: list[_models.RichTextItemRequest] | None = Field(None, description="The new description for the database. Must not exceed 100 characters. If omitted, the current description is preserved.", max_length=100),
    is_inline: bool | None = Field(None, description="Whether the database should be displayed inline within its parent page. If omitted, the current inline status is preserved."),
    icon: _models.FileUploadPageIconRequest | _models.EmojiPageIconRequest | _models.ExternalPageIconRequest | _models.CustomEmojiPageIconRequest | _models.IconPageIconRequest | None = Field(None, description="The new icon for the database. If omitted, the current icon is preserved."),
    cover: _models.FileUploadPageCoverRequest | _models.ExternalPageCoverRequest | None = Field(None, description="The new cover image for the database. If omitted, the current cover is preserved."),
    in_trash: bool | None = Field(None, description="Whether to move the database to trash (true) or restore it from trash (false). If omitted, the current trash status is preserved."),
    is_locked: bool | None = Field(None, description="Whether to lock the database from editing in the Notion app UI. If omitted, the current lock state is preserved."),
) -> dict[str, Any] | ToolResult:
    """Update properties of an existing database in Notion, including its title, description, icon, cover, parent location, inline display status, trash status, and lock state. Only provided fields will be updated; omitted fields remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.UpdateDatabaseRequest(
            path=_models.UpdateDatabaseRequestPath(database_id=database_id),
            header=_models.UpdateDatabaseRequestHeader(notion_version=notion_version),
            body=_models.UpdateDatabaseRequestBody(parent=parent, title=title, description=description, is_inline=is_inline, icon=icon, cover=cover, in_trash=in_trash, is_locked=is_locked)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_database: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/databases/{database_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/databases/{database_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_database")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_database", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_database",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Databases
@mcp.tool()
async def create_database(
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version 2026-03-11."),
    parent: _models.CreateDatabaseBodyParent = Field(..., description="The parent page or workspace where the database will be created. This determines the location and context of the new database."),
    title: list[_models.RichTextItemRequest] | None = Field(None, description="The title of the database. Limited to 100 characters maximum.", max_length=100),
    description: list[_models.RichTextItemRequest] | None = Field(None, description="A description of the database's purpose or contents. Limited to 100 characters maximum.", max_length=100),
    is_inline: bool | None = Field(None, description="Whether the database should be displayed inline within the parent page rather than as a separate entity. Defaults to false."),
    properties: dict[str, _models.PropertyConfigurationRequest] | None = Field(None, description="The property schema defining the initial columns and data structure for the database. Use this to pre-configure database fields when creating the database."),
    icon: _models.FileUploadPageIconRequest | _models.EmojiPageIconRequest | _models.ExternalPageIconRequest | _models.CustomEmojiPageIconRequest | _models.IconPageIconRequest | None = Field(None, description="An icon to visually represent the database in the Notion interface."),
    cover: _models.FileUploadPageCoverRequest | _models.ExternalPageCoverRequest | None = Field(None, description="A cover image displayed at the top of the database page."),
) -> dict[str, Any] | ToolResult:
    """Creates a new database in Notion within a specified parent page or workspace. Optionally configure the database with a title, description, properties schema, icon, and cover image."""

    # Construct request model with validation
    try:
        _request = _models.CreateDatabaseRequest(
            header=_models.CreateDatabaseRequestHeader(notion_version=notion_version),
            body=_models.CreateDatabaseRequestBody(parent=parent, title=title, description=description, is_inline=is_inline, icon=icon, cover=cover,
                initial_data_source=_models.CreateDatabaseRequestBodyInitialDataSource(properties=properties) if any(v is not None for v in [properties]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_database: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/databases"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_database")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_database", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_database",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Search
@mcp.tool()
async def search_pages_by_property(
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11."),
    timestamp: Literal["last_edited_time"] = Field(..., description="The property to sort results by. Currently supports sorting by last_edited_time."),
    direction: Literal["ascending", "descending"] = Field(..., description="The sort direction for results: ascending (oldest first) or descending (newest first)."),
    property_: Literal["object"] = Field(..., alias="property", description="The type of object to search within. Currently limited to searching within pages."),
    value: Literal["page", "data_source"] = Field(..., description="The type of result to return: page (for Notion pages) or data_source (for connected data sources)."),
    query: str | None = Field(None, description="The search query text to filter pages by title or content. Leave empty to retrieve all results without text filtering."),
    page_size: float | None = Field(None, description="The maximum number of results to return per request. Use for pagination control."),
) -> dict[str, Any] | ToolResult:
    """Search for pages in Notion by filtering on a specific property value, with results sorted by last edited time in your preferred direction."""

    # Construct request model with validation
    try:
        _request = _models.PostSearchRequest(
            header=_models.PostSearchRequestHeader(notion_version=notion_version),
            body=_models.PostSearchRequestBody(query=query, page_size=page_size,
                sort=_models.PostSearchRequestBodySort(timestamp=timestamp, direction=direction),
                filter_=_models.PostSearchRequestBodyFilter(property_=property_, value=value))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_pages_by_property: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/search"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_pages_by_property")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_pages_by_property", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_pages_by_property",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def list_comments(
    block_id: str = Field(..., description="The unique identifier of the block for which to retrieve comments."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11."),
    page_size: int | None = Field(None, description="The maximum number of comments to return in the response. Must be between 1 and 100 items.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of comments for a specific block in Notion. Use pagination parameters to control the number of results returned."""

    # Construct request model with validation
    try:
        _request = _models.ListCommentsRequest(
            query=_models.ListCommentsRequestQuery(block_id=block_id, page_size=page_size),
            header=_models.ListCommentsRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_comments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/comments"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_comments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_comments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_comments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def create_comment(
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be set to `2026-03-11`, which is the latest supported version."),
    body: _models.CreateACommentBody = Field(..., description="The request body containing the comment data to be created, including content and any required metadata fields."),
) -> dict[str, Any] | ToolResult:
    """Creates a new comment in Notion. The request body should contain the comment content and metadata required by the Notion API."""

    # Construct request model with validation
    try:
        _request = _models.CreateACommentRequest(
            header=_models.CreateACommentRequestHeader(notion_version=notion_version),
            body=_models.CreateACommentRequestBody(body=body)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/comments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_body = next(iter(_http_body.values()), None) if _http_body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_comment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_comment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Comments
@mcp.tool()
async def get_comment(
    comment_id: str = Field(..., description="The unique identifier of the comment to retrieve."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version 2026-03-11."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific comment by its ID from the Notion API. Returns the full comment object with all associated metadata."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveCommentRequest(
            path=_models.RetrieveCommentRequestPath(comment_id=comment_id),
            header=_models.RetrieveCommentRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/comments/{comment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/comments/{comment_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_comment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_comment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: File uploads
@mcp.tool()
async def list_file_uploads(
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="API version to use for this request. Must be set to the latest version: 2026-03-11."),
    status: Literal["pending", "uploaded", "expired", "failed"] | None = Field(None, description="Filter results to only include file uploads with a specific status: pending (awaiting processing), uploaded (successfully completed), expired (no longer available), or failed (encountered an error)."),
    page_size: int | None = Field(None, description="Number of file uploads to return per page, between 1 and 100 items. Use this to control pagination size for large result sets.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of file uploads with optional filtering by status. Use this to monitor the progress and state of files being uploaded to the system."""

    # Construct request model with validation
    try:
        _request = _models.ListFileUploadsRequest(
            query=_models.ListFileUploadsRequestQuery(status=status, page_size=page_size),
            header=_models.ListFileUploadsRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_file_uploads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/file_uploads"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_file_uploads")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_file_uploads", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_file_uploads",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: File uploads
@mcp.tool()
async def create_file_upload(
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be set to `2026-03-11` or later."),
    mode: Literal["single_part", "multi_part", "external_url"] | None = Field(None, description="Upload mode: `single_part` for files under 20MB (default), `multi_part` for larger files, or `external_url` to import from a public HTTPS URL."),
    filename: str | None = Field(None, description="The filename for the uploaded file, including file extension. Required when using `multi_part` mode; optional otherwise to override the original filename."),
    content_type: str | None = Field(None, description="MIME type of the file (e.g., `application/pdf`, `image/png`). Recommended for multi-part uploads and must match both the file being sent and the filename extension if provided."),
    number_of_parts: int | None = Field(None, description="For multi-part uploads, specify the total number of parts you will upload. Must be between 1 and 10,000 and match the final part number sent.", ge=1, le=10000),
    external_url: str | None = Field(None, description="When using `external_url` mode, provide the HTTPS URL of a publicly accessible file to import into your workspace."),
) -> dict[str, Any] | ToolResult:
    """Initiate a file upload to Notion, supporting single-part uploads for files under 20MB, multi-part uploads for larger files, or external URL imports for publicly hosted files."""

    # Construct request model with validation
    try:
        _request = _models.CreateFileRequest(
            header=_models.CreateFileRequestHeader(notion_version=notion_version),
            body=_models.CreateFileRequestBody(mode=mode, filename=filename, content_type=content_type, number_of_parts=number_of_parts, external_url=external_url)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_file_upload: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/file_uploads"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_file_upload")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_file_upload", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_file_upload",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: File uploads
@mcp.tool()
async def send_file_upload(
    file_upload_id: str = Field(..., description="The unique identifier for the file upload session to which the file contents are being sent."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be `2026-03-11` or later."),
    file_: dict[str, Any] = Field(..., alias="file", description="The raw binary file contents to upload."),
    part_number: str | None = Field(None, description="The current part number when uploading files in multiple parts (required for files larger than 20MB). Must be an integer between 1 and 1,000."),
) -> dict[str, Any] | ToolResult:
    """Upload file contents to a file upload session, supporting multipart uploads for files larger than 20MB."""

    # Construct request model with validation
    try:
        _request = _models.UploadFileRequest(
            path=_models.UploadFileRequestPath(file_upload_id=file_upload_id),
            header=_models.UploadFileRequestHeader(notion_version=notion_version),
            body=_models.UploadFileRequestBody(file_=file_, part_number=part_number)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_file_upload: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/file_uploads/{file_upload_id}/send", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/file_uploads/{file_upload_id}/send"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_file_upload")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_file_upload", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_file_upload",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: File uploads
@mcp.tool()
async def complete_file_upload(
    file_upload_id: str = Field(..., description="The unique identifier of the file upload session to complete."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be set to `2026-03-11` or later for compatibility with current API features."),
) -> dict[str, Any] | ToolResult:
    """Finalize a multi-part file upload by marking it as complete. This operation signals that all file chunks have been uploaded and the file is ready for processing."""

    # Construct request model with validation
    try:
        _request = _models.CompleteFileUploadRequest(
            path=_models.CompleteFileUploadRequestPath(file_upload_id=file_upload_id),
            header=_models.CompleteFileUploadRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for complete_file_upload: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/file_uploads/{file_upload_id}/complete", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/file_uploads/{file_upload_id}/complete"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("complete_file_upload")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("complete_file_upload", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="complete_file_upload",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: File uploads
@mcp.tool()
async def get_file_upload(
    file_upload_id: str = Field(..., description="The unique identifier of the file upload to retrieve."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be set to `2026-03-11` for the latest version."),
) -> dict[str, Any] | ToolResult:
    """Retrieve details about a specific file upload by its ID. Use this to check the status and metadata of a previously initiated file upload."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveFileUploadRequest(
            path=_models.RetrieveFileUploadRequestPath(file_upload_id=file_upload_id),
            header=_models.RetrieveFileUploadRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_file_upload: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/file_uploads/{file_upload_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/file_uploads/{file_upload_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_file_upload")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_file_upload", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_file_upload",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Custom emojis
@mcp.tool()
async def list_custom_emojis(
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11."),
    page_size: int | None = Field(None, description="Maximum number of custom emojis to return in the response, between 1 and 100 items.", ge=1, le=100),
    name: str | None = Field(None, description="Filter results to a custom emoji with an exact name match. Useful for looking up a specific emoji's ID by name."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of custom emojis from your Notion workspace. Optionally filter by exact name match to resolve a specific emoji to its ID."""

    # Construct request model with validation
    try:
        _request = _models.ListCustomEmojisRequest(
            query=_models.ListCustomEmojisRequestQuery(page_size=page_size, name=name),
            header=_models.ListCustomEmojisRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_custom_emojis: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/custom_emojis"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_custom_emojis")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_custom_emojis", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_custom_emojis",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def list_views(
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="API version to use for this request. Must be set to the latest version (2026-03-11) to ensure compatibility with current features."),
    database_id: str | None = Field(None, description="Filter results to views belonging to a specific database. Omit to include views from all databases."),
    data_source_id: str | None = Field(None, description="Filter results to views associated with a specific data source. Omit to include views from all data sources."),
    page_size: int | None = Field(None, description="Number of views to return per page. Must be between 1 and 100 items. Defaults to a server-determined limit if not specified.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of views, optionally filtered by database or data source. Use this to discover available views in your workspace."""

    # Construct request model with validation
    try:
        _request = _models.ListViewsRequest(
            query=_models.ListViewsRequestQuery(database_id=database_id, data_source_id=data_source_id, page_size=page_size),
            header=_models.ListViewsRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_views: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/views"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_views")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_views", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_views",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def create_view(
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be the latest version 2026-03-11."),
    data_source_id: str = Field(..., description="The ID of the data source (database or view) that this view should be scoped to."),
    name: str = Field(..., description="The display name for the view."),
    type_: Literal["table", "board", "list", "calendar", "timeline", "gallery", "form", "chart", "map", "dashboard"] = Field(..., alias="type", description="The view type to create: table, board, list, calendar, timeline, gallery, form, chart, map, or dashboard."),
    parent_type: Literal["page_id"] = Field(..., alias="parentType", description="The parent container type for the new database. Must be 'page_id' when creating a database."),
    position_type: Literal["after_block"] = Field(..., alias="positionType", description="The positioning strategy for the new database. Use 'after_block' to place it after a specified block in the page."),
    page_id: str = Field(..., description="The ID of the page where the new database should be created. Required when using create_database."),
    block_id: str = Field(..., description="The ID of an existing block in the page after which the new database will be positioned. Required when using create_database."),
    database_id: str | None = Field(None, description="The ID of an existing database to create this view in. Cannot be used together with view_id or create_database."),
    view_id: str | None = Field(None, description="The ID of a dashboard view to add this view to as a widget. Cannot be used together with database_id or create_database."),
    filter_: dict[str, Any] | None = Field(None, alias="filter", description="A filter condition to apply to the view using the same format as data source query filters."),
    sorts: list[_models.ViewSortRequest] | None = Field(None, description="An ordered array of sort conditions to apply to the view using the same format as data source query sorts. Maximum 100 sorts allowed.", max_length=100),
    quick_filters: dict[str, _models.QuickFilterConditionRequest] | None = Field(None, description="Quick filter conditions to pin in the view's filter bar. Keys are property names or IDs; values are filter conditions that appear as clickable pills independent of the advanced filter."),
    configuration: _models.TableViewConfigRequest | _models.BoardViewConfigRequest | _models.CalendarViewConfigRequest | _models.TimelineViewConfigRequest | _models.GalleryViewConfigRequest | _models.ListViewConfigRequest | _models.MapViewConfigRequest | _models.FormViewConfigRequest | _models.ChartViewConfigRequest | None = Field(None, description="View-specific presentation configuration. The configuration type must match the specified view type."),
    position: _models.CreateViewBodyPosition | None = Field(None, description="The position where this view should appear in the database's view tab bar. Only applicable when database_id is provided. Defaults to appending at the end."),
    placement: _models.CreateViewBodyPlacement | None = Field(None, description="The placement location for this widget within a dashboard view. Only applicable when view_id is provided. Defaults to creating a new row at the end."),
) -> dict[str, Any] | ToolResult:
    """Create a new view within a database, dashboard, or as a new database on a page. Views can be tables, boards, lists, calendars, timelines, galleries, forms, charts, maps, or dashboards with optional filtering, sorting, and quick filters."""

    # Construct request model with validation
    try:
        _request = _models.CreateViewRequest(
            header=_models.CreateViewRequestHeader(notion_version=notion_version),
            body=_models.CreateViewRequestBody(data_source_id=data_source_id, name=name, type_=type_, database_id=database_id, view_id=view_id, filter_=filter_, sorts=sorts, quick_filters=quick_filters, configuration=configuration, position=position, placement=placement,
                create_database=_models.CreateViewRequestBodyCreateDatabase(
                    parent=_models.CreateViewRequestBodyCreateDatabaseParent(type_=parent_type, page_id=page_id),
                    position=_models.CreateViewRequestBodyCreateDatabasePosition(type_=position_type, block_id=block_id)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/views"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_view", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_view",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def get_view(
    view_id: str = Field(..., description="The unique identifier of the view to retrieve."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version 2026-03-11."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific view by its ID from Notion. Returns the view's configuration and metadata."""

    # Construct request model with validation
    try:
        _request = _models.RetrieveAViewRequest(
            path=_models.RetrieveAViewRequestPath(view_id=view_id),
            header=_models.RetrieveAViewRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/views/{view_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/views/{view_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_view", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_view",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def update_view(
    view_id: str = Field(..., description="The unique identifier of the view to update."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version: 2026-03-11."),
    name: str | None = Field(None, description="The new display name for the view."),
    filter_: dict[str, Any] | None = Field(None, alias="filter", description="A filter condition to apply to the view using the same format as data source query filters. Pass null to remove any existing filter."),
    sorts: list[_models.ViewPropertySortRequest] | None = Field(None, description="An ordered list of property-based sorts to apply to the view (up to 100 sorts). Pass null to clear all sorts.", max_length=100),
    quick_filters: dict[str, _models.QuickFilterConditionRequest] | None = Field(None, description="Quick filter definitions for the view's filter bar, keyed by property name or ID. Set a key to a filter condition to add or update that quick filter, set it to null to remove it, or pass null for the entire field to clear all quick filters. Unspecified quick filters are preserved."),
    configuration: _models.TableViewConfigRequest | _models.BoardViewConfigRequest | _models.CalendarViewConfigRequest | _models.TimelineViewConfigRequest | _models.GalleryViewConfigRequest | _models.ListViewConfigRequest | _models.MapViewConfigRequest | _models.FormViewConfigRequest | _models.ChartViewConfigRequest | None = Field(None, description="View presentation configuration object. The type field must match the view's type. Individual fields within the configuration can be set to null to clear them."),
) -> dict[str, Any] | ToolResult:
    """Update a view's configuration, including its name, filters, sorts, quick filters, and presentation settings. Changes are applied to the specified view."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAViewRequest(
            path=_models.UpdateAViewRequestPath(view_id=view_id),
            header=_models.UpdateAViewRequestHeader(notion_version=notion_version),
            body=_models.UpdateAViewRequestBody(name=name, filter_=filter_, sorts=sorts, quick_filters=quick_filters, configuration=configuration)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/views/{view_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/views/{view_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_view", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_view",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def delete_view(
    view_id: str = Field(..., description="The unique identifier of the view to delete."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version 2026-03-11."),
) -> dict[str, Any] | ToolResult:
    """Permanently delete a view by its ID. This operation removes the view and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteViewRequest(
            path=_models.DeleteViewRequestPath(view_id=view_id),
            header=_models.DeleteViewRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_view: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/views/{view_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/views/{view_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_view")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_view", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_view",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def create_view_query(
    view_id: str = Field(..., description="The unique identifier of the view where the query will be created."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Currently supports version 2026-03-11."),
    page_size: int | None = Field(None, description="The maximum number of results to return per page, between 1 and 100 items.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Create a new query within a Notion view to retrieve filtered or sorted results. Specify pagination preferences to control the number of results returned per request."""

    # Construct request model with validation
    try:
        _request = _models.CreateViewQueryRequest(
            path=_models.CreateViewQueryRequestPath(view_id=view_id),
            header=_models.CreateViewQueryRequestHeader(notion_version=notion_version),
            body=_models.CreateViewQueryRequestBody(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_view_query: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/views/{view_id}/queries", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/views/{view_id}/queries"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_view_query")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_view_query", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_view_query",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def get_view_query_results(
    view_id: str = Field(..., description="The unique identifier of the Notion view containing the query."),
    query_id: str = Field(..., description="The unique identifier of the query whose results should be retrieved."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The Notion API version to use for this request. Must be set to 2026-03-11 or later."),
    page_size: int | None = Field(None, description="Number of results to return per page, between 1 and 100 inclusive. Defaults to a standard page size if not specified.", ge=1, le=100),
) -> dict[str, Any] | ToolResult:
    """Retrieve the results of a query executed against a Notion view. Returns paginated results from the specified view and query."""

    # Construct request model with validation
    try:
        _request = _models.GetViewQueryResultsRequest(
            path=_models.GetViewQueryResultsRequestPath(view_id=view_id, query_id=query_id),
            query=_models.GetViewQueryResultsRequestQuery(page_size=page_size),
            header=_models.GetViewQueryResultsRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_view_query_results: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/views/{view_id}/queries/{query_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/views/{view_id}/queries/{query_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_view_query_results")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_view_query_results", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_view_query_results",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Views
@mcp.tool()
async def delete_view_query(
    view_id: str = Field(..., description="The unique identifier of the view containing the query to delete."),
    query_id: str = Field(..., description="The unique identifier of the query to delete."),
    notion_version: Literal["2026-03-11"] = Field(..., alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version: 2026-03-11."),
) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific query from a view. This operation removes the query and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteViewQueryRequest(
            path=_models.DeleteViewQueryRequestPath(view_id=view_id, query_id=query_id),
            header=_models.DeleteViewQueryRequestHeader(notion_version=notion_version)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_view_query: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/views/{view_id}/queries/{query_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/views/{view_id}/queries/{query_id}"
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_view_query")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_view_query", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_view_query",
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
        print("  python notion_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Notion MCP Server")

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
    logger.info("Starting Notion MCP Server")
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

#!/usr/bin/env python3
"""
Grafana MCP Server

API Info:
- Contact: Grafana Labs <hello@grafana.com> (https://grafana.com)

Generated: 2026-04-23 21:23:28 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

import argparse
import asyncio
import collections
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

# Server variables (from OpenAPI spec, overridable via SERVER_* env vars)
_SERVER_VARS = {
    "grafana_url": os.getenv("SERVER_GRAFANA_URL", "grafana1776699204"),
}
BASE_URL = os.getenv("BASE_URL", "https://{grafana_url}.grafana.net/api".format_map(collections.defaultdict(str, _SERVER_VARS)))
SERVER_NAME = "Grafana"
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
    'api_key',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["api_key"] = _auth.BearerTokenAuth(env_var="BEARER_TOKEN", token_format="Bearer")
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

mcp = FastMCP("Grafana", middleware=[_JsonCoercionMiddleware()])

# Tags: access_control, enterprise
@mcp.tool()
async def list_roles(
    delegatable: bool | None = Field(None, description="When enabled, filters the results to only include roles that the signed-in user has permission to assign to others."),
    include_hidden: bool | None = Field(None, alias="includeHidden", description="When enabled, includes roles that are marked as hidden from the standard role list."),
    target_org_id: str | None = Field(None, alias="targetOrgId", description="The numeric identifier of the target organization. When specified, retrieves roles for that organization instead of the signed-in user's current organization."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all available roles for the signed-in user's organization, including both global and organization-local roles. Requires the `roles:read` permission with `roles:*` scope."""

    _target_org_id = _parse_int(target_org_id)

    # Construct request model with validation
    try:
        _request = _models.ListRolesRequest(
            query=_models.ListRolesRequestQuery(delegatable=delegatable, include_hidden=include_hidden, target_org_id=_target_org_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_roles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/access-control/roles"
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

# Tags: access_control, enterprise
@mcp.tool()
async def get_role(role_uid: str = Field(..., alias="roleUID", description="The unique identifier of the role to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific role by its unique identifier. Requires `roles:read` permission with `roles:*` scope."""

    # Construct request model with validation
    try:
        _request = _models.GetRoleRequest(
            path=_models.GetRoleRequestPath(role_uid=role_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/access-control/roles/{roleUID}", _request.path.model_dump(by_alias=True)) if _request.path else "/access-control/roles/{roleUID}"
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

# Tags: access_control, enterprise
@mcp.tool()
async def list_role_assignments(role_uid: str = Field(..., alias="roleUID", description="The unique identifier of the role for which to retrieve assignments.")) -> dict[str, Any] | ToolResult:
    """Retrieve all user and team assignments for a specific role. This returns direct role assignments only and excludes assignments inherited through group attribute synchronization."""

    # Construct request model with validation
    try:
        _request = _models.GetRoleAssignmentsRequest(
            path=_models.GetRoleAssignmentsRequestPath(role_uid=role_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_role_assignments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/access-control/roles/{roleUID}/assignments", _request.path.model_dump(by_alias=True)) if _request.path else "/access-control/roles/{roleUID}/assignments"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_role_assignments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_role_assignments", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_role_assignments",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_control, enterprise
@mcp.tool()
async def list_team_roles_search(
    include_hidden: bool | None = Field(None, alias="includeHidden", description="Whether to include hidden roles in the results. Set to true to show roles that are normally hidden from view."),
    team_ids: list[int] | None = Field(None, alias="teamIds", description="Array of team identifiers to retrieve roles for. If provided, only roles assigned to these teams will be returned."),
    user_ids: list[int] | None = Field(None, alias="userIds", description="Array of user identifiers to filter results. If provided, only roles assigned to users within the specified teams will be included."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all roles that have been directly assigned to specified teams. Requires `teams.roles:read` permission with `teams:id:*` scope."""

    # Construct request model with validation
    try:
        _request = _models.ListTeamsRolesRequest(
            body=_models.ListTeamsRolesRequestBody(include_hidden=include_hidden, team_ids=team_ids, user_ids=user_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_roles_search: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/access-control/teams/roles/search"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_team_roles_search")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_team_roles_search", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_team_roles_search",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_control, enterprise
@mcp.tool()
async def list_team_roles(
    team_id: str = Field(..., alias="teamId", description="The unique identifier of the team whose roles you want to retrieve. Must be a positive integer."),
    target_org_id: str | None = Field(None, alias="targetOrgId", description="Optional organization ID to scope the role listing to a specific organization context. Must be a positive integer if provided."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all roles assigned to a team. Requires `teams.roles:read` permission scoped to the specified team."""

    _team_id = _parse_int(team_id)
    _target_org_id = _parse_int(target_org_id)

    # Construct request model with validation
    try:
        _request = _models.ListTeamRolesRequest(
            path=_models.ListTeamRolesRequestPath(team_id=_team_id),
            query=_models.ListTeamRolesRequestQuery(target_org_id=_target_org_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_roles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/access-control/teams/{teamId}/roles", _request.path.model_dump(by_alias=True)) if _request.path else "/access-control/teams/{teamId}/roles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_team_roles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_team_roles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_team_roles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_control, enterprise
@mcp.tool()
async def assign_team_role(
    team_id: str = Field(..., alias="teamId", description="The unique identifier of the team to which the role will be assigned. Must be a valid 64-bit integer."),
    role_uid: str | None = Field(None, alias="roleUid", description="The unique identifier of the role to assign to the team. Identifies which role permissions and capabilities the team will receive."),
) -> dict[str, Any] | ToolResult:
    """Assign a role to a team. Requires permission to delegate team roles within your organization."""

    _team_id = _parse_int(team_id)

    # Construct request model with validation
    try:
        _request = _models.AddTeamRoleRequest(
            path=_models.AddTeamRoleRequestPath(team_id=_team_id),
            body=_models.AddTeamRoleRequestBody(role_uid=role_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for assign_team_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/access-control/teams/{teamId}/roles", _request.path.model_dump(by_alias=True)) if _request.path else "/access-control/teams/{teamId}/roles"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("assign_team_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("assign_team_role", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="assign_team_role",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_control, enterprise
@mcp.tool()
async def update_team_roles(
    team_id: str = Field(..., alias="teamId", description="The unique identifier of the team whose roles are being updated. Must be a positive integer."),
    target_org_id: str | None = Field(None, alias="targetOrgId", description="The organization ID to scope the role update to. Optional; if provided, must be a positive integer."),
    include_hidden: bool | None = Field(None, alias="includeHidden", description="Whether to include hidden roles in the operation. Optional boolean flag."),
    role_uids: list[str] | None = Field(None, alias="roleUids", description="Array of role unique identifiers to assign to the team. Order may be significant for role precedence or application sequence."),
) -> dict[str, Any] | ToolResult:
    """Update the roles assigned to a team. Requires permissions to both add and remove team roles with delegation scope."""

    _team_id = _parse_int(team_id)
    _target_org_id = _parse_int(target_org_id)

    # Construct request model with validation
    try:
        _request = _models.SetTeamRolesRequest(
            path=_models.SetTeamRolesRequestPath(team_id=_team_id),
            query=_models.SetTeamRolesRequestQuery(target_org_id=_target_org_id),
            body=_models.SetTeamRolesRequestBody(include_hidden=include_hidden, role_uids=role_uids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_team_roles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/access-control/teams/{teamId}/roles", _request.path.model_dump(by_alias=True)) if _request.path else "/access-control/teams/{teamId}/roles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_team_roles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_team_roles", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_team_roles",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_control, enterprise
@mcp.tool()
async def remove_team_role(
    role_uid: str = Field(..., alias="roleUID", description="The unique identifier of the role to remove from the team."),
    team_id: str = Field(..., alias="teamId", description="The unique identifier of the team from which the role will be removed. Must be a valid positive integer."),
) -> dict[str, Any] | ToolResult:
    """Remove a role assignment from a team. Requires permission to delegate team roles."""

    _team_id = _parse_int(team_id)

    # Construct request model with validation
    try:
        _request = _models.RemoveTeamRoleRequest(
            path=_models.RemoveTeamRoleRequestPath(role_uid=role_uid, team_id=_team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_team_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/access-control/teams/{teamId}/roles/{roleUID}", _request.path.model_dump(by_alias=True)) if _request.path else "/access-control/teams/{teamId}/roles/{roleUID}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_team_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_team_role", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_team_role",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_control, enterprise
@mcp.tool()
async def search_user_roles(
    include_hidden: bool | None = Field(None, alias="includeHidden", description="Include hidden roles in the search results. When enabled, returns roles that are marked as hidden in addition to visible roles."),
    team_ids: list[int] | None = Field(None, alias="teamIds", description="Filter results by team identifiers. Specify as an array of team IDs to limit role search to users belonging to these teams."),
    user_ids: list[int] | None = Field(None, alias="userIds", description="Filter results by user identifiers. Specify as an array of user IDs to search for roles assigned to these specific users."),
) -> dict[str, Any] | ToolResult:
    """Search for roles directly assigned to specified users. Returns custom roles only, excluding built-in roles (Viewer, Editor, Admin, Grafana Admin) and team-inherited roles. Requires `users.roles:read` permission with `users:id:*` scope."""

    # Construct request model with validation
    try:
        _request = _models.ListUsersRolesRequest(
            body=_models.ListUsersRolesRequestBody(include_hidden=include_hidden, team_ids=team_ids, user_ids=user_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_user_roles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/access-control/users/roles/search"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_user_roles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_user_roles", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_user_roles",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_control, enterprise
@mcp.tool()
async def list_user_roles(
    user_id: str = Field(..., alias="userId", description="The unique identifier of the user whose roles should be listed. Must be a positive integer."),
    include_hidden: bool | None = Field(None, alias="includeHidden", description="Whether to include hidden roles in the response. When enabled, returns roles that are normally hidden from the user interface."),
    target_org_id: str | None = Field(None, alias="targetOrgId", description="The organization ID to scope the role query to. When specified, returns roles within that organization context. Must be a positive integer."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all directly assigned roles for a specific user. This returns only explicitly assigned roles and excludes built-in roles (Viewer, Editor, Admin, Grafana Admin) and roles inherited from team membership."""

    _user_id = _parse_int(user_id)
    _target_org_id = _parse_int(target_org_id)

    # Construct request model with validation
    try:
        _request = _models.ListUserRolesRequest(
            path=_models.ListUserRolesRequestPath(user_id=_user_id),
            query=_models.ListUserRolesRequestQuery(include_hidden=include_hidden, target_org_id=_target_org_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_roles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/access-control/users/{userId}/roles", _request.path.model_dump(by_alias=True)) if _request.path else "/access-control/users/{userId}/roles"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_roles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_roles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_roles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_control, enterprise
@mcp.tool()
async def revoke_user_role(
    role_uid: str = Field(..., alias="roleUID", description="The unique identifier of the role to revoke from the user."),
    user_id: str = Field(..., alias="userId", description="The numeric identifier of the user from whom the role will be removed. Must be a valid 64-bit integer."),
    global_: bool | None = Field(None, alias="global", description="Whether the role assignment is global or organization-scoped. When false, the authenticated user's default organization will be used for the removal."),
) -> dict[str, Any] | ToolResult:
    """Revoke a role assignment from a user. Requires permission to remove user roles with delegate scope to prevent privilege escalation. For bulk role updates, use the set user role assignments operation instead."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.RemoveUserRoleRequest(
            path=_models.RemoveUserRoleRequestPath(role_uid=role_uid, user_id=_user_id),
            query=_models.RemoveUserRoleRequestQuery(global_=global_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_user_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/access-control/users/{userId}/roles/{roleUID}", _request.path.model_dump(by_alias=True)) if _request.path else "/access-control/users/{userId}/roles/{roleUID}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_user_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_user_role", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_user_role",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_control
@mcp.tool()
async def assign_resource_permissions(
    resource: str = Field(..., description="The type of resource to assign permissions for. Must be one of: datasources, teams, dashboards, folders, or serviceaccounts."),
    resource_id: str = Field(..., alias="resourceID", description="The unique identifier of the specific resource instance for which permissions are being assigned."),
    permissions: list[_models.SetResourcePermissionCommand] | None = Field(None, description="An array of permission assignment objects that define who has access and what actions they can perform. Refer to the resource description endpoint to see valid permission types for the specified resource."),
) -> dict[str, Any] | ToolResult:
    """Assign or update permissions for a resource (datasource, team, dashboard, folder, or service account) by specifying the resource type and ID along with the desired permission assignments."""

    # Construct request model with validation
    try:
        _request = _models.SetResourcePermissionsRequest(
            path=_models.SetResourcePermissionsRequestPath(resource=resource, resource_id=resource_id),
            body=_models.SetResourcePermissionsRequestBody(permissions=permissions)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for assign_resource_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/access-control/{resource}/{resourceID}", _request.path.model_dump(by_alias=True)) if _request.path else "/access-control/{resource}/{resourceID}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("assign_resource_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("assign_resource_permissions", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="assign_resource_permissions",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_control
@mcp.tool()
async def grant_team_resource_permissions(
    resource: str = Field(..., description="The type of resource to grant permissions for. Must be one of: datasources, teams, dashboards, folders, or serviceaccounts."),
    resource_id: str = Field(..., alias="resourceID", description="The unique identifier of the resource for which permissions are being granted."),
    team_id: str = Field(..., alias="teamID", description="The unique identifier of the team receiving the permissions. Must be a positive integer."),
    permission: str | None = Field(None, description="The permission level or role to assign to the team. Refer to the resource-specific permissions endpoint for valid values."),
) -> dict[str, Any] | ToolResult:
    """Grants or updates permissions for a team to access a specific resource. Supports permissions on datasources, teams, dashboards, folders, and service accounts."""

    _team_id = _parse_int(team_id)

    # Construct request model with validation
    try:
        _request = _models.SetResourcePermissionsForTeamRequest(
            path=_models.SetResourcePermissionsForTeamRequestPath(resource=resource, resource_id=resource_id, team_id=_team_id),
            body=_models.SetResourcePermissionsForTeamRequestBody(permission=permission)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for grant_team_resource_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/access-control/{resource}/{resourceID}/teams/{teamID}", _request.path.model_dump(by_alias=True)) if _request.path else "/access-control/{resource}/{resourceID}/teams/{teamID}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("grant_team_resource_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("grant_team_resource_permissions", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="grant_team_resource_permissions",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_control
@mcp.tool()
async def grant_resource_permission(
    resource: str = Field(..., description="The type of resource to grant permissions for. Must be one of: datasources, teams, dashboards, folders, or serviceaccounts."),
    resource_id: str = Field(..., alias="resourceID", description="The unique identifier of the resource instance for which permissions are being granted."),
    user_id: str = Field(..., alias="userID", description="The numeric ID of the user or service account to grant permissions to. Must be a positive integer."),
    permission: str | None = Field(None, description="The permission level to assign. Refer to the resource-specific permissions endpoint for valid permission values for the chosen resource type."),
) -> dict[str, Any] | ToolResult:
    """Grant or update a user's permissions for a specific resource. Supports datasources, teams, dashboards, folders, and service accounts."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.SetResourcePermissionsForUserRequest(
            path=_models.SetResourcePermissionsForUserRequestPath(resource=resource, resource_id=resource_id, user_id=_user_id),
            body=_models.SetResourcePermissionsForUserRequestBody(permission=permission)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for grant_resource_permission: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/access-control/{resource}/{resourceID}/users/{userID}", _request.path.model_dump(by_alias=True)) if _request.path else "/access-control/{resource}/{resourceID}/users/{userID}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("grant_resource_permission")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("grant_resource_permission", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="grant_resource_permission",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: admin_ldap
@mcp.tool()
async def sync_ldap_user(user_id: str = Field(..., description="The unique identifier of the Grafana user to synchronize with LDAP, specified as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Synchronize a single Grafana user's account with LDAP directory. Requires the `ldap.user:sync` permission in Grafana Enterprise with Fine-grained access control enabled."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.PostSyncUserWithLdapRequest(
            path=_models.PostSyncUserWithLdapRequestPath(user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for sync_ldap_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/ldap/sync/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/ldap/sync/{user_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("sync_ldap_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("sync_ldap_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="sync_ldap_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: admin_ldap
@mcp.tool()
async def lookup_ldap_user(user_name: str = Field(..., description="The LDAP username to look up. This is the unique identifier used in your LDAP directory to retrieve the user's attributes and preview their Grafana mapping.")) -> dict[str, Any] | ToolResult:
    """Retrieves LDAP user details by username to preview how the user will be mapped and synchronized in Grafana. Requires the `ldap.user:read` permission when Fine-grained access control is enabled in Grafana Enterprise."""

    # Construct request model with validation
    try:
        _request = _models.GetUserFromLdapRequest(
            path=_models.GetUserFromLdapRequestPath(user_name=user_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for lookup_ldap_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/ldap/{user_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/ldap/{user_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("lookup_ldap_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("lookup_ldap_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="lookup_ldap_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: admin_users
@mcp.tool()
async def create_user(
    email: str | None = Field(None, description="Email address for the new user. Used for user identification and communication."),
    login: str | None = Field(None, description="Login username for the new user. Used for authentication and user identification within Grafana."),
    password: str | None = Field(None, description="Initial password for the new user account. Should meet Grafana's password security requirements."),
) -> dict[str, Any] | ToolResult:
    """Create a new user in Grafana. Requires the `users:create` permission in Grafana Enterprise with Fine-grained access control enabled. Optionally assign the user to a different organization using the OrgId parameter when `auto_assign_org` is enabled."""

    # Construct request model with validation
    try:
        _request = _models.AdminCreateUserRequest(
            body=_models.AdminCreateUserRequestBody(email=email, login=login, password=password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/users"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: admin_users
@mcp.tool()
async def delete_user(user_id: str = Field(..., description="The unique identifier of the user to delete, specified as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a global user from Grafana. Requires the `users:delete` permission with `global.users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.AdminDeleteUserRequest(
            path=_models.AdminDeleteUserRequestPath(user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/users/{user_id}"
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

# Tags: admin_users
@mcp.tool()
async def list_user_auth_tokens(user_id: str = Field(..., description="The unique identifier of the user whose authentication tokens should be retrieved. Must be a positive integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve all active authentication tokens (devices) for a specific user. Requires Fine-grained access control permission `users.authtoken:list` with `global.users:*` scope in Grafana Enterprise."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.AdminGetUserAuthTokensRequest(
            path=_models.AdminGetUserAuthTokensRequestPath(user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_auth_tokens: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/users/{user_id}/auth-tokens", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/users/{user_id}/auth-tokens"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_auth_tokens")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_auth_tokens", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_auth_tokens",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: admin_users
@mcp.tool()
async def disable_user(user_id: str = Field(..., description="The unique identifier of the user to disable, specified as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Disable a user account in Grafana. Requires the `users:disable` permission with `global.users:1` scope in Grafana Enterprise with Fine-grained access control enabled."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.AdminDisableUserRequest(
            path=_models.AdminDisableUserRequestPath(user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for disable_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/users/{user_id}/disable", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/users/{user_id}/disable"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("disable_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("disable_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="disable_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: admin_users
@mcp.tool()
async def enable_user(user_id: str = Field(..., description="The unique identifier of the user to enable, specified as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Activate a disabled user account in Grafana. Requires the `users:enable` permission with `global.users:1` scope in Grafana Enterprise with Fine-grained access control enabled."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.AdminEnableUserRequest(
            path=_models.AdminEnableUserRequestPath(user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for enable_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/users/{user_id}/enable", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/users/{user_id}/enable"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("enable_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("enable_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="enable_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: admin_users
@mcp.tool()
async def revoke_user_sessions(user_id: str = Field(..., description="The unique identifier of the user whose sessions should be revoked. Must be a positive integer.")) -> dict[str, Any] | ToolResult:
    """Revokes all active authentication tokens and sessions for a user across all devices. The user will be logged out immediately and must re-authenticate on next access. Requires the `users.logout` permission with `global.users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.AdminLogoutUserRequest(
            path=_models.AdminLogoutUserRequestPath(user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_user_sessions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/users/{user_id}/logout", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/users/{user_id}/logout"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_user_sessions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_user_sessions", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_user_sessions",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: admin_users
@mcp.tool()
async def set_user_password(
    user_id: str = Field(..., description="The unique identifier of the user whose password will be updated. Must be a positive integer."),
    password: str | None = Field(None, description="The new password to set for the user. If not provided, the password will not be changed."),
) -> dict[str, Any] | ToolResult:
    """Set or reset a user's password. Requires the `users.password:update` permission with `global.users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.AdminUpdateUserPasswordRequest(
            path=_models.AdminUpdateUserPasswordRequestPath(user_id=_user_id),
            body=_models.AdminUpdateUserPasswordRequestBody(password=password)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_user_password: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/users/{user_id}/password", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/users/{user_id}/password"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_user_password")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_user_password", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_user_password",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: quota, admin_users
@mcp.tool()
async def get_user_quota(user_id: str = Field(..., description="The unique identifier of the user whose quota information should be retrieved. Must be a positive integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve quota information for a specific user. Requires Fine-grained access control with `users.quotas:list` permission and `global.users:1` scope in Grafana Enterprise."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.GetUserQuotaRequest(
            path=_models.GetUserQuotaRequestPath(user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_quota: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/users/{user_id}/quotas", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/users/{user_id}/quotas"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_quota")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_quota", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_quota",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: quota, admin_users
@mcp.tool()
async def update_user_quota(
    quota_target: str = Field(..., description="The quota target type to update (e.g., 'dashboard', 'api_calls', 'storage'). Identifies which quota category to modify for the user."),
    user_id: str = Field(..., description="The unique identifier of the user whose quota is being updated. Must be a positive integer."),
    limit: str | None = Field(None, description="The new quota limit value as a positive integer. Specifies the maximum allowed usage for the quota target."),
) -> dict[str, Any] | ToolResult:
    """Update a user's quota limit for a specific quota target. Requires the `users.quotas:update` permission with global user scope in Grafana Enterprise with Fine-grained access control enabled."""

    _user_id = _parse_int(user_id)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.UpdateUserQuotaRequest(
            path=_models.UpdateUserQuotaRequestPath(quota_target=quota_target, user_id=_user_id),
            body=_models.UpdateUserQuotaRequestBody(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user_quota: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/users/{user_id}/quotas/{quota_target}", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/users/{user_id}/quotas/{quota_target}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user_quota")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user_quota", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user_quota",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: admin_users
@mcp.tool()
async def revoke_user_auth_token(
    user_id: str = Field(..., description="The unique identifier of the user whose authentication token should be revoked. Must be a positive integer."),
    auth_token_id: str | None = Field(None, alias="authTokenId", description="The unique identifier of the specific authentication token (device session) to revoke. If not provided, a default token may be revoked. Must be a positive integer if specified."),
) -> dict[str, Any] | ToolResult:
    """Revoke an authentication token for a user, forcing them to re-authenticate on their next activity. This invalidates the specified device session and logs out the user from that device."""

    _user_id = _parse_int(user_id)
    _auth_token_id = _parse_int(auth_token_id)

    # Construct request model with validation
    try:
        _request = _models.AdminRevokeUserAuthTokenRequest(
            path=_models.AdminRevokeUserAuthTokenRequestPath(user_id=_user_id),
            body=_models.AdminRevokeUserAuthTokenRequestBody(auth_token_id=_auth_token_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_user_auth_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/users/{user_id}/revoke-auth-token", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/users/{user_id}/revoke-auth-token"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_user_auth_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_user_auth_token", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_user_auth_token",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: annotations
@mcp.tool()
async def list_annotations(
    alert_uid: str | None = Field(None, alias="alertUID", description="Filter annotations by a specific alert rule using its unique identifier (UID)."),
    dashboard_uid: str | None = Field(None, alias="dashboardUID", description="Filter annotations to those associated with a specific dashboard using its unique identifier (UID)."),
    limit: str | None = Field(None, description="Maximum number of annotation results to return in the response."),
    tags: list[str] | None = Field(None, description="Filter organization-level annotations by one or more tags. Organization annotations come from annotation data sources and are not tied to a specific dashboard or panel. Provide tags as an array of strings."),
    match_any: bool | None = Field(None, alias="matchAny", description="When filtering by tags, set to true to match annotations with any of the specified tags, or false to match only annotations with all specified tags."),
) -> dict[str, Any] | ToolResult:
    """Retrieve annotations from your Grafana instance, optionally filtered by alert rule, dashboard, tags, or other criteria. Annotations can be scoped to specific dashboards or be organization-wide from annotation data sources."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetAnnotationsRequest(
            query=_models.GetAnnotationsRequestQuery(alert_uid=alert_uid, dashboard_uid=dashboard_uid, limit=_limit, tags=tags, match_any=match_any)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_annotations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/annotations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_annotations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_annotations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_annotations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: annotations
@mcp.tool()
async def create_annotation(
    text: str = Field(..., description="The annotation text content that will be displayed. This is the primary descriptive information for the annotation."),
    dashboard_uid: str | None = Field(None, alias="dashboardUID", description="The unique identifier of the dashboard where this annotation will be created. If omitted, the annotation is created at the organization level and can be queried from any dashboard using the Grafana annotations data source."),
    tags: list[str] | None = Field(None, description="An array of tag strings to categorize and organize the annotation for easier filtering and discovery."),
    time_: str | None = Field(None, alias="time", description="The start time of the annotation as an epoch timestamp in millisecond resolution. Required for all annotations; use timeEnd to create a region annotation spanning a time period."),
    time_end: str | None = Field(None, alias="timeEnd", description="The end time for a region annotation as an epoch timestamp in millisecond resolution. When specified, creates a region annotation spanning from time to timeEnd instead of a point-in-time annotation."),
) -> dict[str, Any] | ToolResult:
    """Creates an annotation in Grafana that can be scoped to a specific dashboard and panel, or created as an organization-wide annotation. For region annotations spanning a time period, include both time and timeEnd properties."""

    _time_ = _parse_int(time_)
    _time_end = _parse_int(time_end)

    # Construct request model with validation
    try:
        _request = _models.PostAnnotationRequest(
            body=_models.PostAnnotationRequestBody(dashboard_uid=dashboard_uid, tags=tags, text=text, time_=_time_, time_end=_time_end)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_annotation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/annotations"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_annotation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_annotation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_annotation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: annotations
@mcp.tool()
async def create_graphite_annotation(
    tags: Any | None = Field(None, description="Space-separated list of tags to associate with the annotation. Supports both modern and legacy Graphite tag formats (pre-0.10.0)."),
    what: str | None = Field(None, description="Human-readable description or title of the annotation event."),
    when: str | None = Field(None, description="Unix timestamp (in seconds) indicating when the annotation occurred. If omitted, the current server time will be used."),
) -> dict[str, Any] | ToolResult:
    """Creates an annotation using Graphite-compatible event format. The annotation timestamp defaults to the current time if not specified, and tags can use either modern or pre-0.10.0 Graphite formats."""

    _when = _parse_int(when)

    # Construct request model with validation
    try:
        _request = _models.PostGraphiteAnnotationRequest(
            body=_models.PostGraphiteAnnotationRequestBody(tags=tags, what=what, when=_when)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_graphite_annotation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/annotations/graphite"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_graphite_annotation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_graphite_annotation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_graphite_annotation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: annotations
@mcp.tool()
async def delete_annotations(
    annotation_id: str | None = Field(None, alias="annotationId", description="The unique identifier of a specific annotation to delete. Provide one or more annotation IDs to target specific annotations across dashboards."),
    dashboard_uid: str | None = Field(None, alias="dashboardUID", description="The unique identifier of a dashboard. When provided, all annotations associated with this dashboard will be deleted."),
) -> dict[str, Any] | ToolResult:
    """Delete one or more annotations from dashboards. Specify either annotation IDs or a dashboard UID to remove annotations in bulk."""

    _annotation_id = _parse_int(annotation_id)

    # Construct request model with validation
    try:
        _request = _models.MassDeleteAnnotationsRequest(
            body=_models.MassDeleteAnnotationsRequestBody(annotation_id=_annotation_id, dashboard_uid=dashboard_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_annotations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/annotations/mass-delete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_annotations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_annotations", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_annotations",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: annotations
@mcp.tool()
async def list_annotation_tags(
    tag: str | None = Field(None, description="Filter tags by a specific string value to narrow results to matching tags."),
    limit: str | None = Field(None, description="Maximum number of results to return in the response, defaulting to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all event tags that have been created in annotations, with optional filtering and pagination support."""

    # Construct request model with validation
    try:
        _request = _models.GetAnnotationTagsRequest(
            query=_models.GetAnnotationTagsRequestQuery(tag=tag, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_annotation_tags: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/annotations/tags"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_annotation_tags")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_annotation_tags", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_annotation_tags",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: annotations
@mcp.tool()
async def get_annotation(annotation_id: str = Field(..., description="The unique identifier of the annotation to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific annotation by its unique identifier. Returns the full annotation details including metadata and content."""

    # Construct request model with validation
    try:
        _request = _models.GetAnnotationByIdRequest(
            path=_models.GetAnnotationByIdRequestPath(annotation_id=annotation_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_annotation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/annotations/{annotation_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/annotations/{annotation_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_annotation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_annotation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_annotation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: annotations
@mcp.tool()
async def update_annotation(
    annotation_id: str = Field(..., description="The unique identifier of the annotation to update."),
    tags: list[str] | None = Field(None, description="An array of tags to associate with the annotation for categorization and filtering."),
    text: str | None = Field(None, description="The text content of the annotation."),
    time_: str | None = Field(None, alias="time", description="The start time of the annotation as a Unix timestamp in milliseconds."),
    time_end: str | None = Field(None, alias="timeEnd", description="The end time of the annotation as a Unix timestamp in milliseconds."),
) -> dict[str, Any] | ToolResult:
    """Update all properties of an annotation by its ID. Use this operation to replace the entire annotation; for partial updates, use the patch annotation operation instead."""

    _time_ = _parse_int(time_)
    _time_end = _parse_int(time_end)

    # Construct request model with validation
    try:
        _request = _models.UpdateAnnotationRequest(
            path=_models.UpdateAnnotationRequestPath(annotation_id=annotation_id),
            body=_models.UpdateAnnotationRequestBody(tags=tags, text=text, time_=_time_, time_end=_time_end)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_annotation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/annotations/{annotation_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/annotations/{annotation_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_annotation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_annotation", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_annotation",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: annotations
@mcp.tool()
async def update_annotation_partial(
    annotation_id: str = Field(..., description="The unique identifier of the annotation to update."),
    tags: list[str] | None = Field(None, description="Array of tag strings to associate with the annotation. Tags are used for organizing and filtering annotations."),
    text: str | None = Field(None, description="The text content or description of the annotation."),
    time_: str | None = Field(None, alias="time", description="The start time of the annotation as a Unix timestamp in milliseconds."),
    time_end: str | None = Field(None, alias="timeEnd", description="The end time of the annotation as a Unix timestamp in milliseconds."),
) -> dict[str, Any] | ToolResult:
    """Update one or more properties of an annotation by its ID. Supports modifying text content, tags, start time, and end time. Available in Grafana 6.0.0-beta2 and later."""

    _time_ = _parse_int(time_)
    _time_end = _parse_int(time_end)

    # Construct request model with validation
    try:
        _request = _models.PatchAnnotationRequest(
            path=_models.PatchAnnotationRequestPath(annotation_id=annotation_id),
            body=_models.PatchAnnotationRequestBody(tags=tags, text=text, time_=_time_, time_end=_time_end)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_annotation_partial: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/annotations/{annotation_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/annotations/{annotation_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_annotation_partial")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_annotation_partial", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_annotation_partial",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: annotations
@mcp.tool()
async def delete_annotation(annotation_id: str = Field(..., description="The unique identifier of the annotation to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes an annotation by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAnnotationByIdRequest(
            path=_models.DeleteAnnotationByIdRequestPath(annotation_id=annotation_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_annotation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/annotations/{annotation_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/annotations/{annotation_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_annotation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_annotation", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_annotation",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: devices
@mcp.tool()
async def list_devices() -> dict[str, Any] | ToolResult:
    """Retrieves all devices that have been active or registered within the last 30 days. Use this to get a current inventory of devices in your system."""

    # Extract parameters for API call
    _http_path = "/anonymous/devices"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_devices")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_devices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_devices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: devices
@mcp.tool()
async def list_devices_search() -> dict[str, Any] | ToolResult:
    """Retrieves all devices that have been active or registered within the last 30 days. Useful for monitoring recent device activity and inventory."""

    # Extract parameters for API call
    _http_path = "/anonymous/search"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_devices_search")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_devices_search", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_devices_search",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: migrations
@mcp.tool()
async def list_migration_sessions() -> dict[str, Any] | ToolResult:
    """Retrieve all cloud migration sessions that have been created, providing an overview of migration projects and their current state."""

    # Extract parameters for API call
    _http_path = "/cloudmigration/migration"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_migration_sessions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_migration_sessions", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_migration_sessions",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: migrations
@mcp.tool()
async def create_migration_session() -> dict[str, Any] | ToolResult:
    """Initiate a new cloud migration session to begin the migration process. This creates a session that can be used to manage and track migration activities."""

    # Extract parameters for API call
    _http_path = "/cloudmigration/migration"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_migration_session")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_migration_session", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_migration_session",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: migrations
@mcp.tool()
async def get_migration_session(uid: str = Field(..., description="The unique identifier of the migration session to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details of a cloud migration session by its unique identifier. Use this to check the status, configuration, and progress of a specific migration."""

    # Construct request model with validation
    try:
        _request = _models.GetSessionRequest(
            path=_models.GetSessionRequestPath(uid=uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_migration_session: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/cloudmigration/migration/{uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/cloudmigration/migration/{uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_migration_session")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_migration_session", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_migration_session",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: migrations
@mcp.tool()
async def delete_migration_session(uid: str = Field(..., description="The unique identifier of the migration session to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a cloud migration session by its unique identifier. This action removes the migration session and its associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSessionRequest(
            path=_models.DeleteSessionRequestPath(uid=uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_migration_session: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/cloudmigration/migration/{uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/cloudmigration/migration/{uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_migration_session")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_migration_session", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_migration_session",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: migrations
@mcp.tool()
async def create_migration_snapshot(
    uid: str = Field(..., description="The unique identifier of the migration session for which to create a snapshot."),
    resource_types: list[Literal["DASHBOARD", "DATASOURCE", "FOLDER", "LIBRARY_ELEMENT", "ALERT_RULE", "ALERT_RULE_GROUP", "CONTACT_POINT", "NOTIFICATION_POLICY", "NOTIFICATION_TEMPLATE", "MUTE_TIMING", "PLUGIN"]] | None = Field(None, alias="resourceTypes", description="Optional list of resource types to include in the snapshot. Specifies which resource categories should be captured."),
) -> dict[str, Any] | ToolResult:
    """Initiates the creation of an instance snapshot for a cloud migration session. Returns the snapshot UID upon successful initialization."""

    # Construct request model with validation
    try:
        _request = _models.CreateSnapshotRequest(
            path=_models.CreateSnapshotRequestPath(uid=uid),
            body=_models.CreateSnapshotRequestBody(resource_types=resource_types)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_migration_snapshot: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/cloudmigration/migration/{uid}/snapshot", _request.path.model_dump(by_alias=True)) if _request.path else "/cloudmigration/migration/{uid}/snapshot"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_migration_snapshot")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_migration_snapshot", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_migration_snapshot",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: migrations
@mcp.tool()
async def get_snapshot(
    uid: str = Field(..., description="The unique identifier of the migration session containing the snapshot."),
    snapshot_uid: str = Field(..., alias="snapshotUid", description="The unique identifier of the snapshot to retrieve metadata for."),
    result_page: str | None = Field(None, alias="resultPage", description="Page number for paginating through snapshot results, starting from page 1. Use with resultLimit to control result sets."),
    result_limit: str | None = Field(None, alias="resultLimit", description="Maximum number of snapshot results to return per page, up to 100 results. Defaults to 100 if not specified."),
    result_sort_column: str | None = Field(None, alias="resultSortColumn", description="Column to sort results by. Valid options are 'name' (resource name), 'resource_type' (type of resource), or 'status' (processing status). Defaults to system-defined sorting if not specified."),
    result_sort_order: str | None = Field(None, alias="resultSortOrder", description="Sort direction for results: 'ASC' for ascending or 'DESC' for descending order. Defaults to ascending."),
    errors_only: bool | None = Field(None, alias="errorsOnly", description="When enabled, returns only resources with error statuses, filtering out successful results. Defaults to false (all results returned)."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed metadata about a migration snapshot, including its processing status and results. Use pagination and filtering options to navigate large result sets."""

    _result_page = _parse_int(result_page)
    _result_limit = _parse_int(result_limit)

    # Construct request model with validation
    try:
        _request = _models.GetSnapshotRequest(
            path=_models.GetSnapshotRequestPath(uid=uid, snapshot_uid=snapshot_uid),
            query=_models.GetSnapshotRequestQuery(result_page=_result_page, result_limit=_result_limit, result_sort_column=result_sort_column, result_sort_order=result_sort_order, errors_only=errors_only)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_snapshot: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/cloudmigration/migration/{uid}/snapshot/{snapshotUid}", _request.path.model_dump(by_alias=True)) if _request.path else "/cloudmigration/migration/{uid}/snapshot/{snapshotUid}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_snapshot")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_snapshot", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_snapshot",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: migrations
@mcp.tool()
async def cancel_snapshot(
    uid: str = Field(..., description="The unique identifier of the cloud migration session containing the snapshot to be cancelled."),
    snapshot_uid: str = Field(..., alias="snapshotUid", description="The unique identifier of the snapshot to cancel."),
) -> dict[str, Any] | ToolResult:
    """Cancel an in-progress snapshot within a cloud migration session. This operation will halt the snapshot processing at any stage of its execution pipeline."""

    # Construct request model with validation
    try:
        _request = _models.CancelSnapshotRequest(
            path=_models.CancelSnapshotRequestPath(uid=uid, snapshot_uid=snapshot_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for cancel_snapshot: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/cloudmigration/migration/{uid}/snapshot/{snapshotUid}/cancel", _request.path.model_dump(by_alias=True)) if _request.path else "/cloudmigration/migration/{uid}/snapshot/{snapshotUid}/cancel"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("cancel_snapshot")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("cancel_snapshot", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="cancel_snapshot",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: migrations
@mcp.tool()
async def upload_snapshot(
    uid: str = Field(..., description="The unique identifier of the migration session to which this snapshot belongs."),
    snapshot_uid: str = Field(..., alias="snapshotUid", description="The unique identifier of the snapshot being uploaded for processing."),
) -> dict[str, Any] | ToolResult:
    """Upload a snapshot to the Grafana Migration Service for processing. This operation ingests snapshot data associated with a migration session for analysis and migration preparation."""

    # Construct request model with validation
    try:
        _request = _models.UploadSnapshotRequest(
            path=_models.UploadSnapshotRequestPath(uid=uid, snapshot_uid=snapshot_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_snapshot: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/cloudmigration/migration/{uid}/snapshot/{snapshotUid}/upload", _request.path.model_dump(by_alias=True)) if _request.path else "/cloudmigration/migration/{uid}/snapshot/{snapshotUid}/upload"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_snapshot")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_snapshot", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_snapshot",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: migrations
@mcp.tool()
async def list_snapshots(
    uid: str = Field(..., description="The unique identifier of the migration session for which to retrieve snapshots."),
    limit: str | None = Field(None, description="Maximum number of snapshots to return in the response. Defaults to 100 if not specified."),
    sort: str | None = Field(None, description="Sort order for results. Set to 'latest' to return snapshots in descending order by creation date."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of snapshots for a cloud migration session. Results can be paginated and sorted by creation date."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetShapshotListRequest(
            path=_models.GetShapshotListRequestPath(uid=uid),
            query=_models.GetShapshotListRequestQuery(limit=_limit, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_snapshots: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/cloudmigration/migration/{uid}/snapshots", _request.path.model_dump(by_alias=True)) if _request.path else "/cloudmigration/migration/{uid}/snapshots"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_snapshots")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_snapshots", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_snapshots",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: migrations
@mcp.tool()
async def list_resource_dependencies() -> dict[str, Any] | ToolResult:
    """Retrieve the dependency graph for all resources currently eligible for migration, showing how resources depend on each other."""

    # Extract parameters for API call
    _http_path = "/cloudmigration/resources/dependencies"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_resource_dependencies")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_resource_dependencies", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_resource_dependencies",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: migrations
@mcp.tool()
async def fetch_cloud_migration_token() -> dict[str, Any] | ToolResult:
    """Retrieve the cloud migration token if one has been previously generated. This token is required for authenticating cloud migration operations."""

    # Extract parameters for API call
    _http_path = "/cloudmigration/token"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("fetch_cloud_migration_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("fetch_cloud_migration_token", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="fetch_cloud_migration_token",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: migrations
@mcp.tool()
async def revoke_cloud_migration_token(uid: str = Field(..., description="The unique identifier of the cloud migration token to revoke.")) -> dict[str, Any] | ToolResult:
    """Revokes and removes a cloud migration token, preventing further use for cloud migration operations. This action is permanent and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCloudMigrationTokenRequest(
            path=_models.DeleteCloudMigrationTokenRequestPath(uid=uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_cloud_migration_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/cloudmigration/token/{uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/cloudmigration/token/{uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_cloud_migration_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_cloud_migration_token", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_cloud_migration_token",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: convert_prometheus
@mcp.tool()
async def list_prometheus_alert_rules() -> dict[str, Any] | ToolResult:
    """Retrieves all Grafana-managed alert rules that were imported from Prometheus-compatible sources, organized by namespace for easy navigation and management."""

    # Extract parameters for API call
    _http_path = "/convert/api/prom/rules"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_prometheus_alert_rules")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_prometheus_alert_rules", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_prometheus_alert_rules",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: convert_prometheus
@mcp.tool()
async def convert_prometheus_rules_to_grafana() -> dict[str, Any] | ToolResult:
    """Converts Prometheus or Cortex rule groups into Grafana-Managed Rules format for use within Grafana's alerting system."""

    # Extract parameters for API call
    _http_path = "/convert/api/prom/rules"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_prometheus_rules_to_grafana")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_prometheus_rules_to_grafana", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_prometheus_rules_to_grafana",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: convert_prometheus
@mcp.tool()
async def list_prometheus_alert_rules_by_namespace(namespace_title: str = Field(..., alias="NamespaceTitle", description="The name of the namespace (folder) containing the alert rules to retrieve. This identifies which rule group to query.")) -> dict[str, Any] | ToolResult:
    """Retrieves Grafana-managed alert rules that were imported from Prometheus-compatible sources for a specified namespace. This operation allows you to view rules organized within a particular folder or namespace."""

    # Construct request model with validation
    try:
        _request = _models.RouteConvertPrometheusCortexGetNamespaceRequest(
            path=_models.RouteConvertPrometheusCortexGetNamespaceRequestPath(namespace_title=namespace_title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_prometheus_alert_rules_by_namespace: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/convert/api/prom/rules/{NamespaceTitle}", _request.path.model_dump(by_alias=True)) if _request.path else "/convert/api/prom/rules/{NamespaceTitle}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_prometheus_alert_rules_by_namespace")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_prometheus_alert_rules_by_namespace", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_prometheus_alert_rules_by_namespace",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: convert_prometheus
@mcp.tool()
async def convert_prometheus_rule_group(
    namespace_title: str = Field(..., alias="NamespaceTitle", description="The name of the namespace where the rule group will be created or updated."),
    x_grafana_alerting_datasource_uid: str | None = Field(None, alias="x-grafana-alerting-datasource-uid", description="The unique identifier of the Grafana datasource to use for alerting rules."),
    x_grafana_alerting_recording_rules_paused: bool | None = Field(None, alias="x-grafana-alerting-recording-rules-paused", description="Whether to pause all recording rules in the converted rule group."),
    x_grafana_alerting_alert_rules_paused: bool | None = Field(None, alias="x-grafana-alerting-alert-rules-paused", description="Whether to pause all alert rules in the converted rule group."),
    x_grafana_alerting_target_datasource_uid: str | None = Field(None, alias="x-grafana-alerting-target-datasource-uid", description="The unique identifier of the target datasource for rule evaluation."),
    x_grafana_alerting_folder_uid: str | None = Field(None, alias="x-grafana-alerting-folder-uid", description="The unique identifier of the Grafana folder where the rule group will be stored."),
    x_grafana_alerting_notification_settings: str | None = Field(None, alias="x-grafana-alerting-notification-settings", description="Configuration for notification settings applied to the rule group, specified as a JSON string."),
    interval: str | None = Field(None, description="The evaluation interval for the rule group, specified in nanoseconds as a 64-bit integer. Represents the elapsed time between rule evaluations."),
    labels: dict[str, str] | None = Field(None, description="Custom labels to attach to all rules in the group, specified as key-value pairs."),
    limit: str | None = Field(None, description="Maximum number of rules to process from the Prometheus rule group, specified as a 64-bit integer."),
    query_offset: str | None = Field(None, description="Time offset for query evaluation, specified as a duration string (e.g., ISO 8601 format)."),
    rules: list[_models.PrometheusRule] | None = Field(None, description="Array of Prometheus rules to convert. Each rule is converted to Grafana's rule format and included in the group."),
) -> dict[str, Any] | ToolResult:
    """Converts a Prometheus rule group into a Grafana-compatible rule group and creates or updates it within the specified namespace. Existing groups that were not originally imported from a Prometheus source will not be replaced and will return an error."""

    _interval = _parse_int(interval)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.RouteConvertPrometheusCortexPostRuleGroupRequest(
            path=_models.RouteConvertPrometheusCortexPostRuleGroupRequestPath(namespace_title=namespace_title),
            header=_models.RouteConvertPrometheusCortexPostRuleGroupRequestHeader(x_grafana_alerting_datasource_uid=x_grafana_alerting_datasource_uid, x_grafana_alerting_recording_rules_paused=x_grafana_alerting_recording_rules_paused, x_grafana_alerting_alert_rules_paused=x_grafana_alerting_alert_rules_paused, x_grafana_alerting_target_datasource_uid=x_grafana_alerting_target_datasource_uid, x_grafana_alerting_folder_uid=x_grafana_alerting_folder_uid, x_grafana_alerting_notification_settings=x_grafana_alerting_notification_settings),
            body=_models.RouteConvertPrometheusCortexPostRuleGroupRequestBody(interval=_interval, labels=labels, limit=_limit, query_offset=query_offset, rules=rules)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_prometheus_rule_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/convert/api/prom/rules/{NamespaceTitle}", _request.path.model_dump(by_alias=True)) if _request.path else "/convert/api/prom/rules/{NamespaceTitle}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/yaml"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_prometheus_rule_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_prometheus_rule_group", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_prometheus_rule_group",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/yaml",
        headers=_http_headers,
    )

    return _response_data

# Tags: convert_prometheus
@mcp.tool()
async def delete_prometheus_rules_by_namespace(namespace_title: str = Field(..., alias="NamespaceTitle", description="The name of the namespace containing the Prometheus-compatible rule groups to delete. This identifier specifies which namespace's rules will be removed.")) -> dict[str, Any] | ToolResult:
    """Permanently deletes all rule groups that were imported from Prometheus-compatible sources within a specified namespace. This operation removes the entire namespace and its associated rules."""

    # Construct request model with validation
    try:
        _request = _models.RouteConvertPrometheusCortexDeleteNamespaceRequest(
            path=_models.RouteConvertPrometheusCortexDeleteNamespaceRequestPath(namespace_title=namespace_title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_prometheus_rules_by_namespace: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/convert/api/prom/rules/{NamespaceTitle}", _request.path.model_dump(by_alias=True)) if _request.path else "/convert/api/prom/rules/{NamespaceTitle}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_prometheus_rules_by_namespace")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_prometheus_rules_by_namespace", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_prometheus_rules_by_namespace",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: convert_prometheus
@mcp.tool()
async def get_prometheus_rule_group(
    namespace_title: str = Field(..., alias="NamespaceTitle", description="The name of the namespace containing the rule group. This identifies the organizational container where the rule group is stored."),
    group: str = Field(..., alias="Group", description="The name of the rule group to retrieve. This identifies the specific group of Prometheus rules within the namespace."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single rule group in Prometheus-compatible format from a namespace. This operation is available only for rule groups that were imported from a Prometheus-compatible source."""

    # Construct request model with validation
    try:
        _request = _models.RouteConvertPrometheusCortexGetRuleGroupRequest(
            path=_models.RouteConvertPrometheusCortexGetRuleGroupRequestPath(namespace_title=namespace_title, group=group)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_prometheus_rule_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/convert/api/prom/rules/{NamespaceTitle}/{Group}", _request.path.model_dump(by_alias=True)) if _request.path else "/convert/api/prom/rules/{NamespaceTitle}/{Group}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_prometheus_rule_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_prometheus_rule_group", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_prometheus_rule_group",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: convert_prometheus
@mcp.tool()
async def delete_prometheus_rule_group(
    namespace_title: str = Field(..., alias="NamespaceTitle", description="The namespace title that contains the rule group to delete. This identifies the logical grouping or project under which the rules are organized."),
    group: str = Field(..., alias="Group", description="The name of the rule group to delete. This identifies the specific group of alert rules within the namespace."),
) -> dict[str, Any] | ToolResult:
    """Deletes a specific rule group from Prometheus-compatible alerting rules. This operation only succeeds if the rule group was originally imported from a Prometheus-compatible source."""

    # Construct request model with validation
    try:
        _request = _models.RouteConvertPrometheusCortexDeleteRuleGroupRequest(
            path=_models.RouteConvertPrometheusCortexDeleteRuleGroupRequestPath(namespace_title=namespace_title, group=group)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_prometheus_rule_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/convert/api/prom/rules/{NamespaceTitle}/{Group}", _request.path.model_dump(by_alias=True)) if _request.path else "/convert/api/prom/rules/{NamespaceTitle}/{Group}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_prometheus_rule_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_prometheus_rule_group", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_prometheus_rule_group",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: convert_prometheus
@mcp.tool()
async def list_prometheus_alert_rules_from_config() -> dict[str, Any] | ToolResult:
    """Retrieves all Grafana-managed alert rules that were imported from Prometheus-compatible sources, organized by namespace for easy navigation and management."""

    # Extract parameters for API call
    _http_path = "/convert/prometheus/config/v1/rules"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_prometheus_alert_rules_from_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_prometheus_alert_rules_from_config", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_prometheus_alert_rules_from_config",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: convert_prometheus
@mcp.tool()
async def convert_prometheus_rules() -> dict[str, Any] | ToolResult:
    """Converts Prometheus rule groups into Grafana-Managed Rules format, enabling centralized rule management within Grafana."""

    # Extract parameters for API call
    _http_path = "/convert/prometheus/config/v1/rules"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_prometheus_rules")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_prometheus_rules", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_prometheus_rules",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: convert_prometheus
@mcp.tool()
async def get_prometheus_alert_rules(namespace_title: str = Field(..., alias="NamespaceTitle", description="The name of the namespace (folder) containing the Prometheus-imported alert rules to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieves Grafana-managed alert rules that were imported from Prometheus-compatible sources for a specified namespace (folder)."""

    # Construct request model with validation
    try:
        _request = _models.RouteConvertPrometheusGetNamespaceRequest(
            path=_models.RouteConvertPrometheusGetNamespaceRequestPath(namespace_title=namespace_title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_prometheus_alert_rules: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/convert/prometheus/config/v1/rules/{NamespaceTitle}", _request.path.model_dump(by_alias=True)) if _request.path else "/convert/prometheus/config/v1/rules/{NamespaceTitle}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_prometheus_alert_rules")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_prometheus_alert_rules", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_prometheus_alert_rules",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: convert_prometheus
@mcp.tool()
async def convert_prometheus_rule_group_config(
    namespace_title: str = Field(..., alias="NamespaceTitle", description="The title of the namespace where the rule group will be created or updated."),
    x_grafana_alerting_datasource_uid: str | None = Field(None, alias="x-grafana-alerting-datasource-uid", description="The unique identifier of the Grafana datasource to use for alerting rules."),
    x_grafana_alerting_recording_rules_paused: bool | None = Field(None, alias="x-grafana-alerting-recording-rules-paused", description="Whether to pause all recording rules in the converted rule group."),
    x_grafana_alerting_alert_rules_paused: bool | None = Field(None, alias="x-grafana-alerting-alert-rules-paused", description="Whether to pause all alert rules in the converted rule group."),
    x_grafana_alerting_target_datasource_uid: str | None = Field(None, alias="x-grafana-alerting-target-datasource-uid", description="The unique identifier of the target datasource for rule evaluation."),
    x_grafana_alerting_folder_uid: str | None = Field(None, alias="x-grafana-alerting-folder-uid", description="The unique identifier of the Grafana folder where the rule group will be stored."),
    x_grafana_alerting_notification_settings: str | None = Field(None, alias="x-grafana-alerting-notification-settings", description="Configuration for notification settings applied to the rule group, specified as a JSON string."),
    interval: str | None = Field(None, description="The evaluation interval for the rule group, specified in nanoseconds as a 64-bit integer. Represents the elapsed time between rule evaluations."),
    labels: dict[str, str] | None = Field(None, description="Custom labels to attach to all rules in the group as key-value pairs."),
    limit: str | None = Field(None, description="Maximum number of rules to process from the Prometheus rule group, specified as a 64-bit integer."),
    query_offset: str | None = Field(None, description="Time offset for query evaluation, specified as a duration string (e.g., ISO 8601 format)."),
    rules: list[_models.PrometheusRule] | None = Field(None, description="Array of Prometheus rules to convert. Each rule is converted to Grafana's rule format and included in the group."),
) -> dict[str, Any] | ToolResult:
    """Converts a Prometheus rule group into a Grafana-compatible rule group and creates or updates it in the specified namespace. Existing groups that were not originally imported from Prometheus sources will not be replaced and will return an error."""

    _interval = _parse_int(interval)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.RouteConvertPrometheusPostRuleGroupRequest(
            path=_models.RouteConvertPrometheusPostRuleGroupRequestPath(namespace_title=namespace_title),
            header=_models.RouteConvertPrometheusPostRuleGroupRequestHeader(x_grafana_alerting_datasource_uid=x_grafana_alerting_datasource_uid, x_grafana_alerting_recording_rules_paused=x_grafana_alerting_recording_rules_paused, x_grafana_alerting_alert_rules_paused=x_grafana_alerting_alert_rules_paused, x_grafana_alerting_target_datasource_uid=x_grafana_alerting_target_datasource_uid, x_grafana_alerting_folder_uid=x_grafana_alerting_folder_uid, x_grafana_alerting_notification_settings=x_grafana_alerting_notification_settings),
            body=_models.RouteConvertPrometheusPostRuleGroupRequestBody(interval=_interval, labels=labels, limit=_limit, query_offset=query_offset, rules=rules)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_prometheus_rule_group_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/convert/prometheus/config/v1/rules/{NamespaceTitle}", _request.path.model_dump(by_alias=True)) if _request.path else "/convert/prometheus/config/v1/rules/{NamespaceTitle}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = _request.header.model_dump(by_alias=True, exclude_none=True) if _request.header else {}
    _http_headers["Content-Type"] = "application/yaml"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_prometheus_rule_group_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_prometheus_rule_group_config", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_prometheus_rule_group_config",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/yaml",
        headers=_http_headers,
    )

    return _response_data

# Tags: convert_prometheus
@mcp.tool()
async def delete_prometheus_rules_namespace(namespace_title: str = Field(..., alias="NamespaceTitle", description="The name of the namespace containing the Prometheus-imported rule groups to delete. This identifier specifies which namespace's rules will be removed.")) -> dict[str, Any] | ToolResult:
    """Deletes all rule groups that were imported from Prometheus-compatible sources within a specified namespace. This operation removes the entire namespace and its associated rules."""

    # Construct request model with validation
    try:
        _request = _models.RouteConvertPrometheusDeleteNamespaceRequest(
            path=_models.RouteConvertPrometheusDeleteNamespaceRequestPath(namespace_title=namespace_title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_prometheus_rules_namespace: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/convert/prometheus/config/v1/rules/{NamespaceTitle}", _request.path.model_dump(by_alias=True)) if _request.path else "/convert/prometheus/config/v1/rules/{NamespaceTitle}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_prometheus_rules_namespace")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_prometheus_rules_namespace", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_prometheus_rules_namespace",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: convert_prometheus
@mcp.tool()
async def get_prometheus_rule_group_config(
    namespace_title: str = Field(..., alias="NamespaceTitle", description="The title or identifier of the namespace containing the rule group."),
    group: str = Field(..., alias="Group", description="The name of the rule group to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a single rule group in Prometheus-compatible format from a previously imported Prometheus-compatible source configuration."""

    # Construct request model with validation
    try:
        _request = _models.RouteConvertPrometheusGetRuleGroupRequest(
            path=_models.RouteConvertPrometheusGetRuleGroupRequestPath(namespace_title=namespace_title, group=group)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_prometheus_rule_group_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/convert/prometheus/config/v1/rules/{NamespaceTitle}/{Group}", _request.path.model_dump(by_alias=True)) if _request.path else "/convert/prometheus/config/v1/rules/{NamespaceTitle}/{Group}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_prometheus_rule_group_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_prometheus_rule_group_config", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_prometheus_rule_group_config",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: convert_prometheus
@mcp.tool()
async def delete_prometheus_rule_group_config(
    namespace_title: str = Field(..., alias="NamespaceTitle", description="The namespace title that contains the rule group to be deleted."),
    group: str = Field(..., alias="Group", description="The name of the rule group to delete within the specified namespace."),
) -> dict[str, Any] | ToolResult:
    """Deletes a specific rule group from a Prometheus-compatible source. This operation only succeeds if the rule group was originally imported from Prometheus."""

    # Construct request model with validation
    try:
        _request = _models.RouteConvertPrometheusDeleteRuleGroupRequest(
            path=_models.RouteConvertPrometheusDeleteRuleGroupRequestPath(namespace_title=namespace_title, group=group)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_prometheus_rule_group_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/convert/prometheus/config/v1/rules/{NamespaceTitle}/{Group}", _request.path.model_dump(by_alias=True)) if _request.path else "/convert/prometheus/config/v1/rules/{NamespaceTitle}/{Group}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_prometheus_rule_group_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_prometheus_rule_group_config", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_prometheus_rule_group_config",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dashboards, snapshots
@mcp.tool()
async def list_dashboard_snapshots(limit: str | None = Field(None, description="Maximum number of snapshots to return in the response. Defaults to 1000 if not specified.")) -> dict[str, Any] | ToolResult:
    """Retrieve a list of dashboard snapshots. Use the limit parameter to control the number of results returned."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.SearchDashboardSnapshotsRequest(
            query=_models.SearchDashboardSnapshotsRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dashboard_snapshots: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/dashboard/snapshots"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dashboard_snapshots")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dashboard_snapshots", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dashboard_snapshots",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: dashboards
@mcp.tool()
async def import_dashboard(
    dashboard: dict[str, Any] | None = Field(None, description="The dashboard configuration object containing the dashboard definition, settings, and panels to be imported."),
    folder_uid: str | None = Field(None, alias="folderUid", description="The unique identifier of the folder where the imported dashboard will be stored. If not specified, the dashboard will be placed in the default location."),
    inputs: list[_models.ImportDashboardInput] | None = Field(None, description="An array of input variables used for template substitution within the dashboard configuration. Each input provides values for dashboard variables or placeholders."),
    overwrite: bool | None = Field(None, description="Whether to overwrite an existing dashboard with the same name or UID. When true, the import will replace any conflicting dashboard; when false, the import will fail if a conflict exists."),
    path: str | None = Field(None, description="The file path or location identifier for the dashboard being imported. Used to identify the source of the dashboard configuration."),
    plugin_id: str | None = Field(None, alias="pluginId", description="The plugin identifier associated with the dashboard, if the dashboard depends on or is specific to a particular Grafana plugin."),
) -> dict[str, Any] | ToolResult:
    """Import a dashboard configuration into Grafana, optionally overwriting existing dashboards and placing them in a specified folder. Supports variable substitution through inputs for dynamic dashboard provisioning."""

    # Construct request model with validation
    try:
        _request = _models.ImportDashboardRequest(
            body=_models.ImportDashboardRequestBody(dashboard=dashboard, folder_uid=folder_uid, inputs=inputs, overwrite=overwrite, path=path, plugin_id=plugin_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for import_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/dashboards/import"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("import_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("import_dashboard", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="import_dashboard",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: dashboards, dashboard_public
@mcp.tool()
async def list_dashboards() -> dict[str, Any] | ToolResult:
    """Retrieve a list of all publicly accessible dashboards. Use this to discover and display available dashboards that don't require authentication."""

    # Extract parameters for API call
    _http_path = "/dashboards/public-dashboards"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: dashboards, dashboard_public
@mcp.tool()
async def get_public_dashboard(dashboard_uid: str = Field(..., alias="dashboardUid", description="The unique identifier of the dashboard to retrieve. This is the dashboard's UID that has been configured for public access.")) -> dict[str, Any] | ToolResult:
    """Retrieve a publicly shared dashboard by its unique identifier. This endpoint allows access to dashboards that have been configured for public sharing."""

    # Construct request model with validation
    try:
        _request = _models.GetPublicDashboardRequest(
            path=_models.GetPublicDashboardRequestPath(dashboard_uid=dashboard_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_public_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/dashboards/uid/{dashboardUid}/public-dashboards", _request.path.model_dump(by_alias=True)) if _request.path else "/dashboards/uid/{dashboardUid}/public-dashboards"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_public_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_public_dashboard", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_public_dashboard",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dashboards, dashboard_public
@mcp.tool()
async def create_public_dashboard(
    dashboard_uid: str = Field(..., alias="dashboardUid", description="The unique identifier of the dashboard to make public."),
    annotations_enabled: bool | None = Field(None, alias="annotationsEnabled", description="Enable or disable annotations visibility in the public dashboard."),
    is_enabled: bool | None = Field(None, alias="isEnabled", description="Enable or disable the public dashboard link."),
    share: str | None = Field(None, description="Access level or sharing mode for the public dashboard (e.g., view-only, edit permissions)."),
    time_selection_enabled: bool | None = Field(None, alias="timeSelectionEnabled", description="Enable or disable time range selection controls in the public dashboard."),
) -> dict[str, Any] | ToolResult:
    """Create a public dashboard link for an existing dashboard, enabling external sharing with configurable access controls and features."""

    # Construct request model with validation
    try:
        _request = _models.CreatePublicDashboardRequest(
            path=_models.CreatePublicDashboardRequestPath(dashboard_uid=dashboard_uid),
            body=_models.CreatePublicDashboardRequestBody(annotations_enabled=annotations_enabled, is_enabled=is_enabled, share=share, time_selection_enabled=time_selection_enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_public_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/dashboards/uid/{dashboardUid}/public-dashboards", _request.path.model_dump(by_alias=True)) if _request.path else "/dashboards/uid/{dashboardUid}/public-dashboards"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_public_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_public_dashboard", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_public_dashboard",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: dashboards, dashboard_public
@mcp.tool()
async def update_public_dashboard(
    dashboard_uid: str = Field(..., alias="dashboardUid", description="The unique identifier of the dashboard that contains the public dashboard configuration to be updated."),
    uid: str = Field(..., description="The unique identifier of the public dashboard instance to update."),
    uid2: str | None = Field(None, alias="uid", description="The unique identifier for the public dashboard (optional override if different from the path parameter)."),
    annotations_enabled: bool | None = Field(None, alias="annotationsEnabled", description="Enable or disable annotations display on the public dashboard."),
    is_enabled: bool | None = Field(None, alias="isEnabled", description="Enable or disable the public dashboard, controlling whether it is accessible to viewers."),
    share: str | None = Field(None, description="The sharing access level or mode for the public dashboard (e.g., public, restricted, or specific user/team access)."),
    time_selection_enabled: bool | None = Field(None, alias="timeSelectionEnabled", description="Enable or disable the time range selection controls, allowing viewers to modify the dashboard's time window."),
) -> dict[str, Any] | ToolResult:
    """Update the configuration and sharing settings of a public dashboard, including visibility, annotation display, time selection controls, and access permissions."""

    # Construct request model with validation
    try:
        _request = _models.UpdatePublicDashboardRequest(
            path=_models.UpdatePublicDashboardRequestPath(dashboard_uid=dashboard_uid, uid=uid),
            body=_models.UpdatePublicDashboardRequestBody(uid2=uid2, annotations_enabled=annotations_enabled, is_enabled=is_enabled, share=share, time_selection_enabled=time_selection_enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_public_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/dashboards/uid/{dashboardUid}/public-dashboards/{uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/dashboards/uid/{dashboardUid}/public-dashboards/{uid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_public_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_public_dashboard", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_public_dashboard",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: dashboards, dashboard_public
@mcp.tool()
async def delete_public_dashboard(
    dashboard_uid: str = Field(..., alias="dashboardUid", description="The unique identifier of the dashboard that contains the public dashboard link to be deleted."),
    uid: str = Field(..., description="The unique identifier of the public dashboard link to be removed."),
) -> dict[str, Any] | ToolResult:
    """Remove a public dashboard link from a dashboard, preventing public access to the dashboard's shared view."""

    # Construct request model with validation
    try:
        _request = _models.DeletePublicDashboardRequest(
            path=_models.DeletePublicDashboardRequestPath(dashboard_uid=dashboard_uid, uid=uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_public_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/dashboards/uid/{dashboardUid}/public-dashboards/{uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/dashboards/uid/{dashboardUid}/public-dashboards/{uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_public_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_public_dashboard", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_public_dashboard",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: datasources
@mcp.tool()
async def list_data_sources() -> dict[str, Any] | ToolResult:
    """Retrieve all configured data sources in Grafana. Requires the `datasources:read` permission with `datasources:*` scope when Fine-grained access control is enabled in Grafana Enterprise."""

    # Extract parameters for API call
    _http_path = "/datasources"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_data_sources")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_data_sources", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_data_sources",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: datasources
@mcp.tool()
async def create_datasource(
    access: str | None = Field(None, description="Access mode for the data source, determining how Grafana communicates with it (e.g., direct browser access or server-side proxy)."),
    database: str | None = Field(None, description="Database name or identifier for the data source connection."),
    is_default: bool | None = Field(None, alias="isDefault", description="Whether this data source should be the default for new panels and queries."),
    json_data: dict[str, Any] | None = Field(None, alias="jsonData", description="Additional JSON configuration specific to the data source type, such as timeout settings, SSL options, or type-specific parameters."),
    secure_json_data: dict[str, str] | None = Field(None, alias="secureJsonData", description="Sensitive credentials stored as encrypted JSON, such as `password` and `basicAuthPassword`. These fields are encrypted at rest and returned as `secureJsonFields` in the response."),
    url: str | None = Field(None, description="Connection URL or endpoint for the data source (e.g., database host, API endpoint)."),
    user: str | None = Field(None, description="Username for authenticating with the data source."),
    with_credentials: bool | None = Field(None, alias="withCredentials", description="Whether to send credentials (cookies, authorization headers) with cross-origin requests to the data source."),
) -> dict[str, Any] | ToolResult:
    """Create a new data source in Grafana. Sensitive credentials like passwords are automatically encrypted and stored securely in the database. Requires `datasources:create` permission in Grafana Enterprise with Fine-grained access control enabled."""

    # Construct request model with validation
    try:
        _request = _models.AddDataSourceRequest(
            body=_models.AddDataSourceRequestBody(access=access, database=database, is_default=is_default, json_data=json_data, secure_json_data=secure_json_data, url=url, user=user, with_credentials=with_credentials)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_datasource: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/datasources"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_datasource")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_datasource", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_datasource",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: datasources, correlations
@mcp.tool()
async def list_correlations(
    limit: str | None = Field(None, description="Maximum number of correlations to return per page, up to 1000. Defaults to 100 if not specified."),
    source_uid: list[str] | None = Field(None, alias="sourceUID", description="Filter correlations by one or more source datasource UIDs. Only correlations involving the specified sources will be returned."),
) -> dict[str, Any] | ToolResult:
    """Retrieves all correlations across datasources, with optional filtering and pagination. Use this to discover relationships between data sources."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetCorrelationsRequest(
            query=_models.GetCorrelationsRequestQuery(limit=_limit, source_uid=source_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_correlations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/datasources/correlations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_correlations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_correlations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_correlations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: datasources, correlations
@mcp.tool()
async def list_correlations_by_source(source_uid: str = Field(..., alias="sourceUID", description="The unique identifier of the data source for which to retrieve correlations.")) -> dict[str, Any] | ToolResult:
    """Retrieves all correlations that originate from a specified data source. Use this to discover relationships and dependencies associated with a particular data source."""

    # Construct request model with validation
    try:
        _request = _models.GetCorrelationsBySourceUidRequest(
            path=_models.GetCorrelationsBySourceUidRequestPath(source_uid=source_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_correlations_by_source: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/datasources/uid/{sourceUID}/correlations", _request.path.model_dump(by_alias=True)) if _request.path else "/datasources/uid/{sourceUID}/correlations"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_correlations_by_source")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_correlations_by_source", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_correlations_by_source",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: datasources, correlations
@mcp.tool()
async def create_correlation(
    source_uid: str = Field(..., alias="sourceUID", description="The unique identifier of the source data source where the correlation will be attached."),
    field: str = Field(..., description="The field name in the source data that will serve as the attachment point for the correlation link (e.g., 'message')."),
    target: dict[str, Any] = Field(..., description="The target data query definition as a key-value object that specifies what data to correlate to."),
    transformations: list[_models.Transformation] | None = Field(None, description="Optional array of transformations to apply to the correlation data before display or processing."),
    description: str | None = Field(None, description="Optional human-readable description of the correlation's purpose (e.g., 'Logs to Traces')."),
    label: str | None = Field(None, description="Optional label to identify and organize the correlation within the data source."),
    target_uid: str | None = Field(None, alias="targetUID", description="The unique identifier of the target data source for the correlation. Required when the correlation type is a query."),
) -> dict[str, Any] | ToolResult:
    """Create a correlation link between two data sources, enabling navigation from a field in the source to related data in a target source or query."""

    # Construct request model with validation
    try:
        _request = _models.CreateCorrelationRequest(
            path=_models.CreateCorrelationRequestPath(source_uid=source_uid),
            body=_models.CreateCorrelationRequestBody(description=description, label=label, target_uid=target_uid,
                config=_models.CreateCorrelationRequestBodyConfig(field=field, target=target, transformations=transformations))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_correlation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/datasources/uid/{sourceUID}/correlations", _request.path.model_dump(by_alias=True)) if _request.path else "/datasources/uid/{sourceUID}/correlations"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_correlation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_correlation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_correlation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: datasources, correlations
@mcp.tool()
async def get_correlation(
    source_uid: str = Field(..., alias="sourceUID", description="The unique identifier of the data source containing the correlation."),
    correlation_uid: str = Field(..., alias="correlationUID", description="The unique identifier of the correlation to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific correlation by its unique identifier from a data source. Use this to fetch detailed information about a correlation relationship between data elements."""

    # Construct request model with validation
    try:
        _request = _models.GetCorrelationRequest(
            path=_models.GetCorrelationRequestPath(source_uid=source_uid, correlation_uid=correlation_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_correlation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/datasources/uid/{sourceUID}/correlations/{correlationUID}", _request.path.model_dump(by_alias=True)) if _request.path else "/datasources/uid/{sourceUID}/correlations/{correlationUID}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_correlation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_correlation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_correlation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: datasources, correlations
@mcp.tool()
async def update_correlation(
    source_uid: str = Field(..., alias="sourceUID", description="The unique identifier of the data source containing the correlation to update."),
    correlation_uid: str = Field(..., alias="correlationUID", description="The unique identifier of the correlation to update."),
    field: str | None = Field(None, description="The field name where the correlation link will be attached (e.g., 'message'). This determines which field in the source data carries the correlation reference."),
    transformations: list[_models.Transformation] | None = Field(None, description="An ordered array of transformation operations to apply to source data before correlation. Each transformation is an object specifying a type (such as 'logfmt' for log format parsing or 'regex' for pattern matching) and relevant parameters like 'expression' and 'variable' for regex transformations."),
    description: str | None = Field(None, description="An optional human-readable description explaining the purpose or context of this correlation (e.g., 'Logs to Traces')."),
    label: str | None = Field(None, description="An optional label to identify and organize the correlation within your data source."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing correlation configuration for a data source, allowing you to modify the field attachment point, data transformations, description, and label."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCorrelationRequest(
            path=_models.UpdateCorrelationRequestPath(source_uid=source_uid, correlation_uid=correlation_uid),
            body=_models.UpdateCorrelationRequestBody(description=description, label=label,
                config=_models.UpdateCorrelationRequestBodyConfig(field=field, transformations=transformations) if any(v is not None for v in [field, transformations]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_correlation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/datasources/uid/{sourceUID}/correlations/{correlationUID}", _request.path.model_dump(by_alias=True)) if _request.path else "/datasources/uid/{sourceUID}/correlations/{correlationUID}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_correlation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_correlation", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_correlation",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: datasources
@mcp.tool()
async def get_datasource(uid: str = Field(..., description="The unique identifier of the data source to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a single data source by its unique identifier. Requires datasources:read permission with appropriate scopes in Grafana Enterprise with Fine-grained access control enabled."""

    # Construct request model with validation
    try:
        _request = _models.GetDataSourceByUidRequest(
            path=_models.GetDataSourceByUidRequestPath(uid=uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_datasource: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/datasources/uid/{uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/datasources/uid/{uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_datasource")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_datasource", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_datasource",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: datasources
@mcp.tool()
async def update_datasource(
    uid: str = Field(..., description="The unique identifier of the data source to update."),
    access: str | None = Field(None, description="The access mode for the data source, determining how Grafana communicates with it (e.g., direct or proxy)."),
    database: str | None = Field(None, description="The default database name to use for queries against this data source."),
    is_default: bool | None = Field(None, alias="isDefault", description="Whether this data source should be the default for its type in Grafana."),
    json_data: dict[str, Any] | None = Field(None, alias="jsonData", description="Additional JSON configuration data specific to the data source type, such as authentication details or connection parameters."),
    secure_json_data: dict[str, str] | None = Field(None, alias="secureJsonData", description="Sensitive configuration data that will be encrypted before storage, such as passwords and basic authentication credentials. These fields should not be included in jsonData."),
    url: str | None = Field(None, description="The URL endpoint or connection string for the data source."),
    user: str | None = Field(None, description="The username for authenticating with the data source."),
    with_credentials: bool | None = Field(None, alias="withCredentials", description="Whether to send credentials (cookies, authorization headers) when making cross-origin requests to the data source."),
) -> dict[str, Any] | ToolResult:
    """Update an existing data source configuration. Sensitive credentials like passwords should be provided in secureJsonData to ensure they are encrypted and stored securely in the database."""

    # Construct request model with validation
    try:
        _request = _models.UpdateDataSourceByUidRequest(
            path=_models.UpdateDataSourceByUidRequestPath(uid=uid),
            body=_models.UpdateDataSourceByUidRequestBody(access=access, database=database, is_default=is_default, json_data=json_data, secure_json_data=secure_json_data, url=url, user=user, with_credentials=with_credentials)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_datasource: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/datasources/uid/{uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/datasources/uid/{uid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_datasource")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_datasource", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_datasource",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: datasources
@mcp.tool()
async def delete_datasource(uid: str = Field(..., description="The unique identifier of the data source to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a data source by its unique identifier. Requires datasources:delete permission with appropriate scopes in Grafana Enterprise with Fine-grained access control enabled."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDataSourceByUidRequest(
            path=_models.DeleteDataSourceByUidRequestPath(uid=uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_datasource: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/datasources/uid/{uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/datasources/uid/{uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_datasource")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_datasource", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_datasource",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: datasources, correlations
@mcp.tool()
async def delete_correlation(
    uid: str = Field(..., description="The unique identifier of the datasource containing the correlation to delete."),
    correlation_uid: str = Field(..., alias="correlationUID", description="The unique identifier of the correlation to delete."),
) -> dict[str, Any] | ToolResult:
    """Remove a correlation from a datasource. This permanently deletes the specified correlation relationship."""

    # Construct request model with validation
    try:
        _request = _models.DeleteCorrelationRequest(
            path=_models.DeleteCorrelationRequestPath(uid=uid, correlation_uid=correlation_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_correlation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/datasources/uid/{uid}/correlations/{correlationUID}", _request.path.model_dump(by_alias=True)) if _request.path else "/datasources/uid/{uid}/correlations/{correlationUID}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_correlation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_correlation", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_correlation",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: datasources, health
@mcp.tool()
async def check_datasource_health(uid: str = Field(..., description="The unique identifier of the datasource to check. This UID is used to locate and verify the health status of the specific plugin datasource.")) -> dict[str, Any] | ToolResult:
    """Performs a health check on a plugin datasource to verify its connectivity and operational status. Returns the health status of the datasource identified by the provided UID."""

    # Construct request model with validation
    try:
        _request = _models.CheckDatasourceHealthWithUidRequest(
            path=_models.CheckDatasourceHealthWithUidRequestPath(uid=uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_datasource_health: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/datasources/uid/{uid}/health", _request.path.model_dump(by_alias=True)) if _request.path else "/datasources/uid/{uid}/health"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_datasource_health")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_datasource_health", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_datasource_health",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: datasources
@mcp.tool()
async def fetch_datasource_resource(
    datasource_proxy_route: str = Field(..., description="The unique identifier of the data source to query."),
    uid: str = Field(..., description="The proxy route path that specifies which resource endpoint within the data source to access."),
) -> dict[str, Any] | ToolResult:
    """Retrieve data from a specific data source resource by its unique identifier and proxy route. This operation allows you to access data source resources through their configured proxy endpoints."""

    # Construct request model with validation
    try:
        _request = _models.CallDatasourceResourceWithUidRequest(
            path=_models.CallDatasourceResourceWithUidRequestPath(datasource_proxy_route=datasource_proxy_route, uid=uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for fetch_datasource_resource: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/datasources/uid/{uid}/resources/{datasource_proxy_route}", _request.path.model_dump(by_alias=True)) if _request.path else "/datasources/uid/{uid}/resources/{datasource_proxy_route}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("fetch_datasource_resource")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("fetch_datasource_resource", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="fetch_datasource_resource",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: enterprise
@mcp.tool()
async def get_datasource_cache_config(
    data_source_uid: str = Field(..., alias="dataSourceUID", description="The unique identifier of the data source for which to retrieve cache configuration."),
    data_source_type: str | None = Field(None, alias="dataSourceType", description="Optional type identifier for the data source, used to filter or validate the cache configuration retrieval."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the cache configuration settings for a specific data source. Returns caching policies and parameters that control how data from this source is cached."""

    # Construct request model with validation
    try:
        _request = _models.GetDataSourceCacheConfigRequest(
            path=_models.GetDataSourceCacheConfigRequestPath(data_source_uid=data_source_uid),
            query=_models.GetDataSourceCacheConfigRequestQuery(data_source_type=data_source_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_datasource_cache_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/datasources/{dataSourceUID}/cache", _request.path.model_dump(by_alias=True)) if _request.path else "/datasources/{dataSourceUID}/cache"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_datasource_cache_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_datasource_cache_config", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_datasource_cache_config",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: enterprise
@mcp.tool()
async def configure_datasource_cache(
    data_source_uid: str = Field(..., alias="dataSourceUID", description="The unique identifier of the data source to configure caching for."),
    data_source_type: str | None = Field(None, alias="dataSourceType", description="The type of data source (e.g., Prometheus, Graphite, InfluxDB). Used to identify the data source category."),
    data_source_id: str | None = Field(None, alias="dataSourceID", description="The numeric identifier of the data source. Used as an alternative or supplementary identifier for the data source."),
    enabled: bool | None = Field(None, description="Enable or disable caching for this data source. When disabled, cached data will not be used or stored."),
    ttl_queries_ms: str | None = Field(None, alias="ttlQueriesMs", description="Time-to-live for cached queries in milliseconds. Specifies how long query results remain in the cache before expiration. Only used if UseDefaultTTL is disabled."),
    ttl_resources_ms: str | None = Field(None, alias="ttlResourcesMs", description="Time-to-live for cached resources in milliseconds. Specifies how long resource data remains in the cache before expiration. Only used if UseDefaultTTL is disabled."),
    use_default_ttl: bool | None = Field(None, alias="useDefaultTTL", description="When enabled, ignores the TTLQueriesMs and TTLResourcesMs values and uses the default TTL settings from the Grafana configuration file instead."),
) -> dict[str, Any] | ToolResult:
    """Configure caching behavior for a specific data source, including TTL settings for queries and resources. Use this to optimize performance by controlling how long cached data persists."""

    _data_source_id = _parse_int(data_source_id)
    _ttl_queries_ms = _parse_int(ttl_queries_ms)
    _ttl_resources_ms = _parse_int(ttl_resources_ms)

    # Construct request model with validation
    try:
        _request = _models.SetDataSourceCacheConfigRequest(
            path=_models.SetDataSourceCacheConfigRequestPath(data_source_uid=data_source_uid),
            query=_models.SetDataSourceCacheConfigRequestQuery(data_source_type=data_source_type),
            body=_models.SetDataSourceCacheConfigRequestBody(data_source_id=_data_source_id, enabled=enabled, ttl_queries_ms=_ttl_queries_ms, ttl_resources_ms=_ttl_resources_ms, use_default_ttl=use_default_ttl)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for configure_datasource_cache: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/datasources/{dataSourceUID}/cache", _request.path.model_dump(by_alias=True)) if _request.path else "/datasources/{dataSourceUID}/cache"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("configure_datasource_cache")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("configure_datasource_cache", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="configure_datasource_cache",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: enterprise
@mcp.tool()
async def disable_datasource_cache(
    data_source_uid: str = Field(..., alias="dataSourceUID", description="The unique identifier of the data source for which caching should be disabled."),
    data_source_type: str | None = Field(None, alias="dataSourceType", description="The type or category of the data source, used to provide additional context for the cache disabling operation."),
) -> dict[str, Any] | ToolResult:
    """Disable caching for a specific data source to ensure fresh data is fetched on subsequent queries. This operation clears the cache configuration for the specified data source."""

    # Construct request model with validation
    try:
        _request = _models.DisableDataSourceCacheRequest(
            path=_models.DisableDataSourceCacheRequestPath(data_source_uid=data_source_uid),
            query=_models.DisableDataSourceCacheRequestQuery(data_source_type=data_source_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for disable_datasource_cache: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/datasources/{dataSourceUID}/cache/disable", _request.path.model_dump(by_alias=True)) if _request.path else "/datasources/{dataSourceUID}/cache/disable"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("disable_datasource_cache")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("disable_datasource_cache", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="disable_datasource_cache",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: enterprise
@mcp.tool()
async def enable_datasource_cache(
    data_source_uid: str = Field(..., alias="dataSourceUID", description="The unique identifier of the data source for which caching should be enabled."),
    data_source_type: str | None = Field(None, alias="dataSourceType", description="The type of data source (e.g., Prometheus, Graphite, Elasticsearch). Used to apply type-specific cache configuration if needed."),
) -> dict[str, Any] | ToolResult:
    """Enable caching for a data source to improve query performance and reduce load on the underlying data source."""

    # Construct request model with validation
    try:
        _request = _models.EnableDataSourceCacheRequest(
            path=_models.EnableDataSourceCacheRequestPath(data_source_uid=data_source_uid),
            query=_models.EnableDataSourceCacheRequestQuery(data_source_type=data_source_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for enable_datasource_cache: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/datasources/{dataSourceUID}/cache/enable", _request.path.model_dump(by_alias=True)) if _request.path else "/datasources/{dataSourceUID}/cache/enable"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("enable_datasource_cache")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("enable_datasource_cache", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="enable_datasource_cache",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: datasources
@mcp.tool()
async def query_metrics(
    from_: str = Field(..., alias="from", description="Start time for the query range as an epoch timestamp in milliseconds or a relative Grafana time unit (e.g., 'now-1h', 'now-24h'). Relative units are calculated from the current time."),
    queries: list[_models.Json] = Field(..., description="Array of query objects to execute. Each query must specify a unique datasourceId and can optionally include a refId identifier (defaults to 'A'), maxDataPoints for rendering limits (defaults to 100), and intervalMs for time series granularity in milliseconds (defaults to 1000). Query objects support datasource-specific fields like rawSql for SQL queries and format specification (e.g., 'table')."),
    to: str = Field(..., description="End time for the query range as an epoch timestamp in milliseconds or a relative Grafana time unit (e.g., 'now'). Relative units are calculated from the current time."),
) -> dict[str, Any] | ToolResult:
    """Execute metric queries against a data source with support for expressions and custom time ranges. Requires datasources:query permission in Grafana Enterprise with Fine-grained access control enabled."""

    # Construct request model with validation
    try:
        _request = _models.QueryMetricsWithExpressionsRequest(
            body=_models.QueryMetricsWithExpressionsRequestBody(from_=from_, queries=queries, to=to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for query_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/ds/query"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("query_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("query_metrics", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="query_metrics",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: folders, permissions
@mcp.tool()
async def set_folder_permissions(
    folder_uid: str = Field(..., description="The unique identifier of the folder whose permissions should be updated."),
    items: list[_models.DashboardAclUpdateItem] | None = Field(None, description="An array of permission objects defining who has access to the folder and what level of access they have. Permissions not included in this list will be removed from the folder."),
) -> dict[str, Any] | ToolResult:
    """Sets permissions for a folder by replacing all existing permissions with the ones specified in the request. Any permissions not included will be removed."""

    # Construct request model with validation
    try:
        _request = _models.UpdateFolderPermissionsRequest(
            path=_models.UpdateFolderPermissionsRequestPath(folder_uid=folder_uid),
            body=_models.UpdateFolderPermissionsRequestBody(items=items)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_folder_permissions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/folders/{folder_uid}/permissions", _request.path.model_dump(by_alias=True)) if _request.path else "/folders/{folder_uid}/permissions"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_folder_permissions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_folder_permissions", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_folder_permissions",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: group_attribute_sync, enterprise
@mcp.tool()
async def list_mapped_groups() -> dict[str, Any] | ToolResult:
    """Retrieve all groups that have attribute mappings configured. This endpoint is experimental and requires the groupAttributeSync feature flag to be enabled."""

    # Extract parameters for API call
    _http_path = "/groupsync/groups"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_mapped_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_mapped_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_mapped_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: group_attribute_sync, enterprise
@mcp.tool()
async def list_group_roles(group_id: str = Field(..., description="The unique identifier of the group for which to retrieve mapped roles.")) -> dict[str, Any] | ToolResult:
    """Retrieve all roles mapped to a specific group. This endpoint is experimental and requires the `groupAttributeSync` feature flag to be enabled."""

    # Construct request model with validation
    try:
        _request = _models.GetGroupRolesRequest(
            path=_models.GetGroupRolesRequestPath(group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_group_roles: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groupsync/groups/{group_id}/roles", _request.path.model_dump(by_alias=True)) if _request.path else "/groupsync/groups/{group_id}/roles"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_group_roles")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_group_roles", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_group_roles",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: library_elements
@mcp.tool()
async def list_library_elements(
    search_string: str | None = Field(None, alias="searchString", description="Search for library elements by matching text against their name or description fields."),
    sort_direction: Literal["alpha-asc", "alpha-desc"] | None = Field(None, alias="sortDirection", description="Sort the returned elements alphabetically in ascending or descending order."),
    type_filter: str | None = Field(None, alias="typeFilter", description="Filter results to include only elements of specified types. Provide multiple types as a comma-separated list."),
    exclude_uid: str | None = Field(None, alias="excludeUid", description="Exclude a specific element from the search results by providing its unique identifier (UID)."),
    folder_filter_ui_ds: str | None = Field(None, alias="folderFilterUIDs", description="Filter results to include only elements located in specified folders. Provide multiple folder UIDs as a comma-separated list."),
    per_page: str | None = Field(None, alias="perPage", description="Set the maximum number of elements to return per page. Defaults to 100 results per page."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of all library elements that the authenticated user has permission to view. Results can be filtered, searched, and sorted to find specific elements."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetLibraryElementsRequest(
            query=_models.GetLibraryElementsRequestQuery(search_string=search_string, sort_direction=sort_direction, type_filter=type_filter, exclude_uid=exclude_uid, folder_filter_ui_ds=folder_filter_ui_ds, per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_library_elements: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/library-elements"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_library_elements")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_library_elements", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_library_elements",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: library_elements
@mcp.tool()
async def create_library_element(
    folder_uid: str | None = Field(None, alias="folderUid", description="The unique identifier of the folder where this library element will be stored. If not provided, the element will be created in the default location."),
    model: dict[str, Any] | None = Field(None, description="The JSON configuration object defining the library element's properties, type, and settings. This object structure depends on the type of library element being created."),
) -> dict[str, Any] | ToolResult:
    """Creates a new library element that can be reused across dashboards and other resources. Optionally specify a folder location and provide the element configuration as a JSON model."""

    # Construct request model with validation
    try:
        _request = _models.CreateLibraryElementRequest(
            body=_models.CreateLibraryElementRequestBody(folder_uid=folder_uid, model=model)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_library_element: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/library-elements"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_library_element")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_library_element", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_library_element",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: library_elements
@mcp.tool()
async def get_library_element_by_name(library_element_name: str = Field(..., description="The name of the library element to retrieve. This is the unique identifier used to look up the library element.")) -> dict[str, Any] | ToolResult:
    """Retrieve a library element by its name. Returns the library element matching the specified name."""

    # Construct request model with validation
    try:
        _request = _models.GetLibraryElementByNameRequest(
            path=_models.GetLibraryElementByNameRequestPath(library_element_name=library_element_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_library_element_by_name: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/library-elements/name/{library_element_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/library-elements/name/{library_element_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_library_element_by_name")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_library_element_by_name", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_library_element_by_name",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: library_elements
@mcp.tool()
async def get_library_element(library_element_uid: str = Field(..., description="The unique identifier of the library element to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific library element by its unique identifier. Returns the complete library element details for the given UID."""

    # Construct request model with validation
    try:
        _request = _models.GetLibraryElementByUidRequest(
            path=_models.GetLibraryElementByUidRequestPath(library_element_uid=library_element_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_library_element: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/library-elements/{library_element_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/library-elements/{library_element_uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_library_element")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_library_element", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_library_element",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: library_elements
@mcp.tool()
async def update_library_element(
    library_element_uid: str = Field(..., description="The unique identifier of the library element to update."),
    folder_uid: str | None = Field(None, alias="folderUid", description="The unique identifier of the folder where the library element should be stored or moved to."),
    model: dict[str, Any] | None = Field(None, description="The JSON model containing the library element's properties and configuration to be updated."),
) -> dict[str, Any] | ToolResult:
    """Update an existing library element by modifying its properties, folder location, or model configuration. Specify the library element by its unique identifier and provide the fields you want to change."""

    # Construct request model with validation
    try:
        _request = _models.UpdateLibraryElementRequest(
            path=_models.UpdateLibraryElementRequestPath(library_element_uid=library_element_uid),
            body=_models.UpdateLibraryElementRequestBody(folder_uid=folder_uid, model=model)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_library_element: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/library-elements/{library_element_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/library-elements/{library_element_uid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_library_element")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_library_element", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_library_element",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: library_elements
@mcp.tool()
async def delete_library_element(library_element_uid: str = Field(..., description="The unique identifier of the library element to delete. Must reference an unconnected library element.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a library element by its unique identifier. This action cannot be undone and will fail if the library element is currently connected to other resources."""

    # Construct request model with validation
    try:
        _request = _models.DeleteLibraryElementByUidRequest(
            path=_models.DeleteLibraryElementByUidRequestPath(library_element_uid=library_element_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_library_element: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/library-elements/{library_element_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/library-elements/{library_element_uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_library_element")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_library_element", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_library_element",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: library_elements
@mcp.tool()
async def list_library_element_connections(library_element_uid: str = Field(..., description="The unique identifier of the library element for which to retrieve connections.")) -> dict[str, Any] | ToolResult:
    """Retrieve all connections associated with a specific library element. Returns a list of dashboards, panels, or other resources that reference the library element."""

    # Construct request model with validation
    try:
        _request = _models.GetLibraryElementConnectionsRequest(
            path=_models.GetLibraryElementConnectionsRequestPath(library_element_uid=library_element_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_library_element_connections: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/library-elements/{library_element_uid}/connections/", _request.path.model_dump(by_alias=True)) if _request.path else "/library-elements/{library_element_uid}/connections/"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_library_element_connections")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_library_element_connections", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_library_element_connections",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: licensing, enterprise
@mcp.tool()
async def create_license_token(instance: str | None = Field(None, description="The instance identifier for which to create the license token. If not specified, the token is created for the default instance.")) -> dict[str, Any] | ToolResult:
    """Generate a new license token for the specified instance. Requires licensing:write permission to perform this operation."""

    # Construct request model with validation
    try:
        _request = _models.PostLicenseTokenRequest(
            body=_models.PostLicenseTokenRequestBody(instance=instance)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_license_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/licensing/token"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_license_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_license_token", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_license_token",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: licensing, enterprise
@mcp.tool()
async def remove_license_token(instance: str | None = Field(None, description="The Grafana instance identifier or URL where the license token should be removed.")) -> dict[str, Any] | ToolResult:
    """Remove the license token from the Grafana database. This operation permanently deletes the stored license and requires the `licensing:delete` permission. Available in Grafana Enterprise v7.4+."""

    # Construct request model with validation
    try:
        _request = _models.DeleteLicenseTokenRequest(
            body=_models.DeleteLicenseTokenRequestBody(instance=instance)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_license_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/licensing/token"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_license_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_license_token", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_license_token",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: org
@mcp.tool()
async def get_organization() -> dict[str, Any] | ToolResult:
    """Retrieve the current organization's details and configuration. This returns metadata about the organization associated with the authenticated user or API key."""

    # Extract parameters for API call
    _http_path = "/org"
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

# Tags: org
@mcp.tool()
async def update_organization_current() -> dict[str, Any] | ToolResult:
    """Update the settings and details of the current organization. This operation modifies the organization's profile information and configuration."""

    # Extract parameters for API call
    _http_path = "/org"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_organization_current")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_organization_current", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_organization_current",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: org
@mcp.tool()
async def update_organization_address(
    address1: str | None = Field(None, description="The primary street address line for the organization's location."),
    address2: str | None = Field(None, description="The secondary street address line (e.g., suite, apartment, or unit number) for the organization's location."),
    city: str | None = Field(None, description="The city where the organization is located."),
    country: str | None = Field(None, description="The country where the organization is located."),
    state: str | None = Field(None, description="The state or province where the organization is located."),
    zipcode: str | None = Field(None, description="The postal or ZIP code for the organization's location."),
) -> dict[str, Any] | ToolResult:
    """Update the address information for the current organization. Provide any address fields that need to be changed; omitted fields will remain unchanged."""

    # Construct request model with validation
    try:
        _request = _models.UpdateCurrentOrgAddressRequest(
            body=_models.UpdateCurrentOrgAddressRequestBody(address1=address1, address2=address2, city=city, country=country, state=state, zipcode=zipcode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_organization_address: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/org/address"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_organization_address")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_organization_address", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_organization_address",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: org, invites
@mcp.tool()
async def list_pending_org_invites() -> dict[str, Any] | ToolResult:
    """Retrieve all pending organization invitations that have been sent but not yet accepted. Use this to track outstanding invites and their status."""

    # Extract parameters for API call
    _http_path = "/org/invites"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pending_org_invites")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pending_org_invites", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pending_org_invites",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: org, invites
@mcp.tool()
async def invite_organization_member(
    login_or_email: str | None = Field(None, alias="loginOrEmail", description="The login username or email address of the person to invite to the organization."),
    role: Literal["None", "Viewer", "Editor", "Admin"] | None = Field(None, description="The role to assign to the invited member. Must be one of: None, Viewer, Editor, or Admin. Determines the member's permissions within the organization."),
    send_email: bool | None = Field(None, alias="sendEmail", description="Whether to send a notification email to the invitee. If true, an invitation email will be delivered; if false, the invite is created silently."),
) -> dict[str, Any] | ToolResult:
    """Send an invitation to join an organization with a specified role. The invitee can be identified by their login or email address, and an optional notification email can be sent to them."""

    # Construct request model with validation
    try:
        _request = _models.AddOrgInviteRequest(
            body=_models.AddOrgInviteRequestBody(login_or_email=login_or_email, role=role, send_email=send_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for invite_organization_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/org/invites"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("invite_organization_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("invite_organization_member", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="invite_organization_member",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: org, invites
@mcp.tool()
async def revoke_invitation(invitation_code: str = Field(..., description="The unique code identifying the invitation to revoke. This code was provided when the invitation was created.")) -> dict[str, Any] | ToolResult:
    """Revoke a pending organization invitation, preventing the recipient from accepting it. This operation invalidates the invitation code immediately."""

    # Construct request model with validation
    try:
        _request = _models.RevokeInviteRequest(
            path=_models.RevokeInviteRequestPath(invitation_code=invitation_code)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_invitation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/org/invites/{invitation_code}/revoke", _request.path.model_dump(by_alias=True)) if _request.path else "/org/invites/{invitation_code}/revoke"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_invitation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_invitation", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_invitation",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: quota, org
@mcp.tool()
async def get_organization_quota() -> dict[str, Any] | ToolResult:
    """Retrieve the current quota limits and usage for your organization. Requires the `orgs.quotas:read` permission in Grafana Enterprise with Fine-grained access control enabled."""

    # Extract parameters for API call
    _http_path = "/org/quotas"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_organization_quota")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_organization_quota", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_organization_quota",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: org
@mcp.tool()
async def list_organization_users(limit: str | None = Field(None, description="Maximum number of users to return in the response. Specify as a positive integer to limit result set size.")) -> dict[str, Any] | ToolResult:
    """Retrieve all users in the current organization. Requires org admin role or the `org.users:read` permission in Grafana Enterprise with Fine-grained access control enabled."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetOrgUsersForCurrentOrgRequest(
            query=_models.GetOrgUsersForCurrentOrgRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/org/users"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_users")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_users", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_users",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: org
@mcp.tool()
async def add_user_to_organization(
    login_or_email: str | None = Field(None, alias="loginOrEmail", description="The login username or email address of the global user to add to the organization."),
    role: Literal["None", "Viewer", "Editor", "Admin"] | None = Field(None, description="The role to assign to the user within the organization. Must be one of: None, Viewer, Editor, or Admin."),
) -> dict[str, Any] | ToolResult:
    """Adds an existing global user to the current organization with a specified role. Requires the `org.users:add` permission with `users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""

    # Construct request model with validation
    try:
        _request = _models.AddOrgUserToCurrentOrgRequest(
            body=_models.AddOrgUserToCurrentOrgRequestBody(login_or_email=login_or_email, role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_user_to_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/org/users"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_user_to_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_user_to_organization", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_user_to_organization",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: org
@mcp.tool()
async def list_organization_users_lookup(limit: str | None = Field(None, description="Maximum number of users to return in the response. Specify as a positive integer to limit the result set size.")) -> dict[str, Any] | ToolResult:
    """Retrieve a list of all users in the current organization with basic information. This lightweight endpoint is designed for UI operations like team member selection and permission management, and requires org admin role or admin privileges in any folder or team."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.GetOrgUsersForCurrentOrgLookupRequest(
            query=_models.GetOrgUsersForCurrentOrgLookupRequestQuery(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_users_lookup: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/org/users/lookup"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_users_lookup")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_users_lookup", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_users_lookup",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: org
@mcp.tool()
async def update_org_user_role(
    user_id: str = Field(..., description="The unique identifier of the user to update, specified as a 64-bit integer."),
    role: Literal["None", "Viewer", "Editor", "Admin"] | None = Field(None, description="The new role to assign to the user. Must be one of: None, Viewer, Editor, or Admin."),
) -> dict[str, Any] | ToolResult:
    """Updates a user's role within the current organization. Requires the `org.users.role:update` permission with `users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateOrgUserForCurrentOrgRequest(
            path=_models.UpdateOrgUserForCurrentOrgRequestPath(user_id=_user_id),
            body=_models.UpdateOrgUserForCurrentOrgRequestBody(role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_org_user_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/org/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/org/users/{user_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_org_user_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_org_user_role", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_org_user_role",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: org
@mcp.tool()
async def remove_organization_user(user_id: str = Field(..., description="The unique identifier of the user to remove from the organization. Must be a positive integer.")) -> dict[str, Any] | ToolResult:
    """Remove a user from the current organization. Requires the `org.users:remove` permission with `users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.RemoveOrgUserForCurrentOrgRequest(
            path=_models.RemoveOrgUserForCurrentOrgRequestPath(user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_organization_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/org/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/org/users/{user_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_organization_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_organization_user", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_organization_user",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: orgs
@mcp.tool()
async def list_organizations(perpage: str | None = Field(None, description="Number of organizations to return per page. Defaults to 1000 items per page; use this with the totalCount response field to navigate through all results.")) -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of all organizations. Use the totalCount field in the response to determine pagination, where each page contains up to the specified number of items."""

    _perpage = _parse_int(perpage)

    # Construct request model with validation
    try:
        _request = _models.SearchOrgsRequest(
            query=_models.SearchOrgsRequestQuery(perpage=_perpage)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organizations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/orgs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organizations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organizations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organizations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: orgs
@mcp.tool()
async def create_organization() -> dict[str, Any] | ToolResult:
    """Create a new organization in Grafana. This operation requires the allow_org_create configuration setting to be enabled by your Grafana administrator."""

    # Extract parameters for API call
    _http_path = "/orgs"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: orgs
@mcp.tool()
async def get_organization_by_name(org_name: str = Field(..., description="The name of the organization to retrieve. This should be the exact organization name as it exists in the system.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific organization by its name. Use this operation to look up organization details when you know the organization's name."""

    # Construct request model with validation
    try:
        _request = _models.GetOrgByNameRequest(
            path=_models.GetOrgByNameRequestPath(org_name=org_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization_by_name: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/orgs/name/{org_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/orgs/name/{org_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_organization_by_name")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_organization_by_name", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_organization_by_name",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: orgs
@mcp.tool()
async def get_organization_by_id(org_id: str = Field(..., description="The unique identifier of the organization to retrieve, provided as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific organization by its unique identifier. Returns detailed organization information including metadata and configuration."""

    _org_id = _parse_int(org_id)

    # Construct request model with validation
    try:
        _request = _models.GetOrgByIdRequest(
            path=_models.GetOrgByIdRequestPath(org_id=_org_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization_by_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/orgs/{org_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/orgs/{org_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_organization_by_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_organization_by_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_organization_by_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: orgs
@mcp.tool()
async def update_organization(org_id: str = Field(..., description="The unique identifier of the organization to update, specified as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Update an existing organization's details and configuration. Requires the organization ID to identify which organization to modify."""

    _org_id = _parse_int(org_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateOrgRequest(
            path=_models.UpdateOrgRequestPath(org_id=_org_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/orgs/{org_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/orgs/{org_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_organization", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_organization",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: orgs
@mcp.tool()
async def delete_organization(org_id: str = Field(..., description="The unique identifier of the organization to delete, specified as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Permanently delete an organization and all associated data. This action cannot be undone."""

    _org_id = _parse_int(org_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteOrgByIdRequest(
            path=_models.DeleteOrgByIdRequestPath(org_id=_org_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/orgs/{org_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/orgs/{org_id}"
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

# Tags: orgs
@mcp.tool()
async def update_organization_address_by_id(
    org_id: str = Field(..., description="The unique identifier of the organization whose address will be updated. Must be a valid 64-bit integer."),
    address1: str | None = Field(None, description="The primary street address line (e.g., street number and name)."),
    address2: str | None = Field(None, description="The secondary street address line for additional address details (e.g., suite, apartment, or unit number)."),
    city: str | None = Field(None, description="The city or municipality name."),
    country: str | None = Field(None, description="The country name or code."),
    state: str | None = Field(None, description="The state, province, or region name or code."),
    zipcode: str | None = Field(None, description="The postal or ZIP code for the address."),
) -> dict[str, Any] | ToolResult:
    """Update the physical address information for an organization. Provide any combination of address fields to update the organization's location details."""

    _org_id = _parse_int(org_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateOrgAddressRequest(
            path=_models.UpdateOrgAddressRequestPath(org_id=_org_id),
            body=_models.UpdateOrgAddressRequestBody(address1=address1, address2=address2, city=city, country=country, state=state, zipcode=zipcode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_organization_address_by_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/orgs/{org_id}/address", _request.path.model_dump(by_alias=True)) if _request.path else "/orgs/{org_id}/address"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_organization_address_by_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_organization_address_by_id", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_organization_address_by_id",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: quota, orgs
@mcp.tool()
async def get_organization_quota_by_id(org_id: str = Field(..., description="The unique identifier of the organization whose quota information should be retrieved. Must be a positive integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve the quota limits and usage for a specific organization. Requires the `orgs.quotas:read` permission with the appropriate organization scope in Grafana Enterprise with Fine-grained access control enabled."""

    _org_id = _parse_int(org_id)

    # Construct request model with validation
    try:
        _request = _models.GetOrgQuotaRequest(
            path=_models.GetOrgQuotaRequestPath(org_id=_org_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_organization_quota_by_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/orgs/{org_id}/quotas", _request.path.model_dump(by_alias=True)) if _request.path else "/orgs/{org_id}/quotas"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_organization_quota_by_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_organization_quota_by_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_organization_quota_by_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: quota, orgs
@mcp.tool()
async def update_org_quota(
    quota_target: str = Field(..., description="The quota target type to update (e.g., users, dashboards, data sources). Identifies which resource quota to modify."),
    org_id: str = Field(..., description="The organization ID as a 64-bit integer. Identifies which organization's quota to update."),
    limit: str | None = Field(None, description="The new quota limit as a 64-bit integer. Specifies the maximum number of resources allowed for the quota target."),
) -> dict[str, Any] | ToolResult:
    """Update the quota limit for a specific target within an organization. Requires the `orgs.quotas:write` permission in Grafana Enterprise with Fine-grained access control enabled."""

    _org_id = _parse_int(org_id)
    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.UpdateOrgQuotaRequest(
            path=_models.UpdateOrgQuotaRequestPath(quota_target=quota_target, org_id=_org_id),
            body=_models.UpdateOrgQuotaRequestBody(limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_org_quota: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/orgs/{org_id}/quotas/{quota_target}", _request.path.model_dump(by_alias=True)) if _request.path else "/orgs/{org_id}/quotas/{quota_target}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_org_quota")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_org_quota", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_org_quota",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: orgs
@mcp.tool()
async def list_organization_users_by_id(org_id: str = Field(..., description="The unique identifier of the organization. Must be a positive integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve all users in a Grafana organization. Requires the `org.users:read` permission with `users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""

    _org_id = _parse_int(org_id)

    # Construct request model with validation
    try:
        _request = _models.GetOrgUsersRequest(
            path=_models.GetOrgUsersRequestPath(org_id=_org_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_organization_users_by_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/orgs/{org_id}/users", _request.path.model_dump(by_alias=True)) if _request.path else "/orgs/{org_id}/users"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_organization_users_by_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_organization_users_by_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_organization_users_by_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: orgs
@mcp.tool()
async def add_organization_user(
    org_id: str = Field(..., description="The unique identifier of the organization to which the user will be added. Must be a positive integer."),
    login_or_email: str | None = Field(None, alias="loginOrEmail", description="The login username or email address of the global user to add to the organization."),
    role: Literal["None", "Viewer", "Editor", "Admin"] | None = Field(None, description="The role to assign to the user within the organization. Valid options are: None, Viewer, Editor, or Admin. If not specified, defaults to None."),
) -> dict[str, Any] | ToolResult:
    """Add an existing global user to the current organization with an optional role assignment. Requires the `org.users:add` permission with `users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""

    _org_id = _parse_int(org_id)

    # Construct request model with validation
    try:
        _request = _models.AddOrgUserRequest(
            path=_models.AddOrgUserRequestPath(org_id=_org_id),
            body=_models.AddOrgUserRequestBody(login_or_email=login_or_email, role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_organization_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/orgs/{org_id}/users", _request.path.model_dump(by_alias=True)) if _request.path else "/orgs/{org_id}/users"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_organization_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_organization_user", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_organization_user",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: orgs
@mcp.tool()
async def search_organization_users(org_id: str = Field(..., description="The unique identifier of the organization to search users in. Must be a positive integer.")) -> dict[str, Any] | ToolResult:
    """Search for users within a specific organization. Requires the `org.users:read` permission with `users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""

    _org_id = _parse_int(org_id)

    # Construct request model with validation
    try:
        _request = _models.SearchOrgUsersRequest(
            path=_models.SearchOrgUsersRequestPath(org_id=_org_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_organization_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/orgs/{org_id}/users/search", _request.path.model_dump(by_alias=True)) if _request.path else "/orgs/{org_id}/users/search"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_organization_users")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_organization_users", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_organization_users",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: orgs
@mcp.tool()
async def update_organization_user_role(
    org_id: str = Field(..., description="The unique identifier of the organization containing the user. Must be a positive integer."),
    user_id: str = Field(..., description="The unique identifier of the user to update. Must be a positive integer."),
    role: Literal["None", "Viewer", "Editor", "Admin"] | None = Field(None, description="The new role to assign to the user. Valid options are: None, Viewer, Editor, or Admin. If not specified, the user's current role remains unchanged."),
) -> dict[str, Any] | ToolResult:
    """Update a user's role within an organization. Requires the `org.users.role:update` permission with `users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""

    _org_id = _parse_int(org_id)
    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateOrgUserRequest(
            path=_models.UpdateOrgUserRequestPath(org_id=_org_id, user_id=_user_id),
            body=_models.UpdateOrgUserRequestBody(role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_organization_user_role: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/orgs/{org_id}/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/orgs/{org_id}/users/{user_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_organization_user_role")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_organization_user_role", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_organization_user_role",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: orgs
@mcp.tool()
async def remove_organization_user_by_id(
    org_id: str = Field(..., description="The unique identifier of the organization from which the user will be removed. Must be a positive integer."),
    user_id: str = Field(..., description="The unique identifier of the user to be removed from the organization. Must be a positive integer."),
) -> dict[str, Any] | ToolResult:
    """Remove a user from the current organization. Requires the `org.users:remove` permission with `users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""

    _org_id = _parse_int(org_id)
    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.RemoveOrgUserRequest(
            path=_models.RemoveOrgUserRequestPath(org_id=_org_id, user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_organization_user_by_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/orgs/{org_id}/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/orgs/{org_id}/users/{user_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_organization_user_by_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_organization_user_by_id", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_organization_user_by_id",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dashboards, dashboard_public
@mcp.tool()
async def get_public_dashboard_access(access_token: str = Field(..., alias="accessToken", description="The unique access token that grants permission to view the public dashboard. This token is provided when a dashboard is shared publicly.")) -> dict[str, Any] | ToolResult:
    """Retrieve a publicly shared dashboard using its access token. This allows viewing dashboards that have been made publicly available without requiring authentication."""

    # Construct request model with validation
    try:
        _request = _models.ViewPublicDashboardRequest(
            path=_models.ViewPublicDashboardRequestPath(access_token=access_token)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_public_dashboard_access: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/public/dashboards/{accessToken}", _request.path.model_dump(by_alias=True)) if _request.path else "/public/dashboards/{accessToken}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_public_dashboard_access")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_public_dashboard_access", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_public_dashboard_access",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dashboards, annotations, dashboard_public
@mcp.tool()
async def list_dashboard_annotations(access_token: str = Field(..., alias="accessToken", description="The unique access token that grants permission to view the public dashboard and its associated annotations.")) -> dict[str, Any] | ToolResult:
    """Retrieve all annotations for a public dashboard using its access token. Annotations provide contextual notes and markers associated with dashboard visualizations."""

    # Construct request model with validation
    try:
        _request = _models.GetPublicAnnotationsRequest(
            path=_models.GetPublicAnnotationsRequestPath(access_token=access_token)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dashboard_annotations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/public/dashboards/{accessToken}/annotations", _request.path.model_dump(by_alias=True)) if _request.path else "/public/dashboards/{accessToken}/annotations"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dashboard_annotations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dashboard_annotations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dashboard_annotations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dashboards, dashboard_public
@mcp.tool()
async def query_dashboard_panel(
    access_token: str = Field(..., alias="accessToken", description="The access token that grants permission to query this public dashboard. This token authenticates your request and determines which dashboard you can access."),
    panel_id: str = Field(..., alias="panelId", description="The unique identifier of the panel within the dashboard whose data you want to query. This is a numeric ID that specifies which panel's results to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Execute a query against a specific panel on a public dashboard and retrieve the results. Use the dashboard's access token and panel identifier to fetch panel data."""

    _panel_id = _parse_int(panel_id)

    # Construct request model with validation
    try:
        _request = _models.QueryPublicDashboardRequest(
            path=_models.QueryPublicDashboardRequestPath(access_token=access_token, panel_id=_panel_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for query_dashboard_panel: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/public/dashboards/{accessToken}/panels/{panelId}/query", _request.path.model_dump(by_alias=True)) if _request.path else "/public/dashboards/{accessToken}/panels/{panelId}/query"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("query_dashboard_panel")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("query_dashboard_panel", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="query_dashboard_panel",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: query_history
@mcp.tool()
async def list_queries(
    datasource_uid: list[str] | None = Field(None, alias="datasourceUid", description="Filter results to include only queries from specific data sources by their unique identifiers."),
    search_string: str | None = Field(None, alias="searchString", description="Search for queries containing specific text in the query content or associated comments."),
    only_starred: bool | None = Field(None, alias="onlyStarred", description="When enabled, return only queries that have been marked as starred or favorited."),
    sort: Literal["time-desc", "time-asc"] | None = Field(None, description="Order results by timestamp in descending order (newest first) or ascending order (oldest first). Defaults to newest first."),
    limit: str | None = Field(None, description="Maximum number of queries to return in a single response. Defaults to 100 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Retrieve queries from history filtered by data source, search terms, or starred status. Results are paginated with a default limit of 100 queries per page."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.SearchQueriesRequest(
            query=_models.SearchQueriesRequestQuery(datasource_uid=datasource_uid, search_string=search_string, only_starred=only_starred, sort=sort, limit=_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_queries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query-history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_queries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_queries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_queries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: query_history
@mcp.tool()
async def save_query(
    queries: dict[str, Any] = Field(..., description="One or more query objects to add to the history. Each query object contains the query details to be persisted."),
    datasource_uid: str | None = Field(None, alias="datasourceUid", description="The unique identifier of the data source where queries will be stored. Use the data source UID (e.g., PE1C5CBDA0504A6A3) to target a specific data source."),
) -> dict[str, Any] | ToolResult:
    """Save one or more queries to the query history for a specified data source. This allows you to persist and track queries for later retrieval and analysis."""

    # Construct request model with validation
    try:
        _request = _models.CreateQueryRequest(
            body=_models.CreateQueryRequestBody(datasource_uid=datasource_uid, queries=queries)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for save_query: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/query-history"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("save_query")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("save_query", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="save_query",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: query_history
@mcp.tool()
async def star_query_history(query_history_uid: str = Field(..., description="The unique identifier of the query history entry to star.")) -> dict[str, Any] | ToolResult:
    """Mark a query in your history as starred for quick access and organization. This helps you keep track of frequently used or important queries."""

    # Construct request model with validation
    try:
        _request = _models.StarQueryRequest(
            path=_models.StarQueryRequestPath(query_history_uid=query_history_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for star_query_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/query-history/star/{query_history_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/query-history/star/{query_history_uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("star_query_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("star_query_history", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="star_query_history",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: query_history
@mcp.tool()
async def remove_query_star(query_history_uid: str = Field(..., description="The unique identifier of the query history entry to unstar.")) -> dict[str, Any] | ToolResult:
    """Remove a star from a saved query in your query history. This operation unmarks a previously starred query, making it easier to manage your frequently used queries."""

    # Construct request model with validation
    try:
        _request = _models.UnstarQueryRequest(
            path=_models.UnstarQueryRequestPath(query_history_uid=query_history_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_query_star: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/query-history/star/{query_history_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/query-history/star/{query_history_uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_query_star")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_query_star", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_query_star",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: query_history
@mcp.tool()
async def update_query_comment(
    query_history_uid: str = Field(..., description="The unique identifier of the query history record to update."),
    comment: str | None = Field(None, description="The new comment text to associate with the query. Provide the complete comment as it should appear in the query history."),
) -> dict[str, Any] | ToolResult:
    """Updates the comment associated with a specific query in the query history. Use this to add, modify, or replace notes for a previously executed query."""

    # Construct request model with validation
    try:
        _request = _models.PatchQueryCommentRequest(
            path=_models.PatchQueryCommentRequestPath(query_history_uid=query_history_uid),
            body=_models.PatchQueryCommentRequestBody(comment=comment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_query_comment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/query-history/{query_history_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/query-history/{query_history_uid}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_query_comment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_query_comment", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_query_comment",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: query_history
@mcp.tool()
async def delete_query_history(query_history_uid: str = Field(..., description="The unique identifier of the query history entry to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently removes a query from the query history by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteQueryRequest(
            path=_models.DeleteQueryRequestPath(query_history_uid=query_history_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_query_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/query-history/{query_history_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/query-history/{query_history_uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_query_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_query_history", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_query_history",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: recording_rules, enterprise
@mcp.tool()
async def list_recording_rules() -> dict[str, Any] | ToolResult:
    """Retrieves all recording rules from the database, including both active and deleted rules. Use this to view the complete rule inventory for auditing or management purposes."""

    # Extract parameters for API call
    _http_path = "/recording-rules"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_recording_rules")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_recording_rules", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_recording_rules",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: recording_rules, enterprise
@mcp.tool()
async def create_recording_rule(
    active: bool | None = Field(None, description="Whether the recording rule is enabled and actively collecting metrics upon creation."),
    count: bool | None = Field(None, description="Whether to return the count of matching time series instead of the series data itself."),
    description: str | None = Field(None, description="A human-readable description of the recording rule's purpose and behavior."),
    dest_data_source_uid: str | None = Field(None, description="The unique identifier of the destination data source where recorded metrics will be stored."),
    interval: str | None = Field(None, description="The evaluation interval in milliseconds at which the recording rule queries will be executed."),
    prom_name: str | None = Field(None, description="The name to assign to the recorded metric in the Prometheus data source."),
    queries: list[dict[str, Any]] | None = Field(None, description="An array of metric queries to execute for this recording rule. Order matters and determines query execution sequence."),
    range_: str | None = Field(None, alias="range", description="The time range in milliseconds over which each query will look back when evaluating the recording rule."),
    target_ref_id: str | None = Field(None, description="The reference identifier of the target query within the queries array that produces the final recorded metric."),
) -> dict[str, Any] | ToolResult:
    """Create and register a new recording rule that automatically starts collecting metrics according to the specified query and interval configuration."""

    _interval = _parse_int(interval)
    _range_ = _parse_int(range_)

    # Construct request model with validation
    try:
        _request = _models.CreateRecordingRuleRequest(
            body=_models.CreateRecordingRuleRequestBody(active=active, count=count, description=description, dest_data_source_uid=dest_data_source_uid, interval=_interval, prom_name=prom_name, queries=queries, range_=_range_, target_ref_id=target_ref_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_recording_rule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/recording-rules"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_recording_rule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_recording_rule", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_recording_rule",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: recording_rules, enterprise
@mcp.tool()
async def update_recording_rule(
    active: bool | None = Field(None, description="Enable or disable the recording rule. When active, the rule will be evaluated according to its schedule; when inactive, evaluations are skipped."),
    count: bool | None = Field(None, description="Whether to count results from the recording rule evaluation. When enabled, the rule tracks the number of matching records."),
    description: str | None = Field(None, description="A human-readable description of the recording rule's purpose and behavior."),
    dest_data_source_uid: str | None = Field(None, description="The unique identifier of the destination data source where recorded metrics will be stored."),
    interval: str | None = Field(None, description="The evaluation interval in milliseconds. Defines how frequently the recording rule is executed."),
    prom_name: str | None = Field(None, description="The Prometheus metric name for the recorded data. This is the name used to reference the recorded metric in queries."),
    queries: list[dict[str, Any]] | None = Field(None, description="An array of query objects that define what data to record. Each query specifies the metrics or logs to capture."),
    range_: str | None = Field(None, alias="range", description="The time range in milliseconds for each evaluation. Defines the lookback window of data considered during rule execution."),
    target_ref_id: str | None = Field(None, description="The reference identifier for the target query or panel. Used to link the recording rule to a specific query definition."),
) -> dict[str, Any] | ToolResult:
    """Update an existing recording rule's configuration, including its active status, query parameters, and data source settings. This operation allows modification of rule behavior such as evaluation interval, range, and target data source."""

    _interval = _parse_int(interval)
    _range_ = _parse_int(range_)

    # Construct request model with validation
    try:
        _request = _models.UpdateRecordingRuleRequest(
            body=_models.UpdateRecordingRuleRequestBody(active=active, count=count, description=description, dest_data_source_uid=dest_data_source_uid, interval=_interval, prom_name=prom_name, queries=queries, range_=_range_, target_ref_id=target_ref_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_recording_rule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/recording-rules"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_recording_rule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_recording_rule", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_recording_rule",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: recording_rules, enterprise
@mcp.tool()
async def test_recording_rule(
    active: bool | None = Field(None, description="Whether the recording rule is enabled and should be actively processed."),
    count: bool | None = Field(None, description="Whether to return the count of matching results instead of the full dataset."),
    description: str | None = Field(None, description="A human-readable description of the recording rule's purpose and behavior."),
    dest_data_source_uid: str | None = Field(None, description="The unique identifier of the destination data source where recorded metrics will be stored."),
    interval: str | None = Field(None, description="The evaluation interval in milliseconds at which the recording rule will be executed."),
    prom_name: str | None = Field(None, description="The name of the metric as it will be recorded in the destination data source."),
    queries: list[dict[str, Any]] | None = Field(None, description="An array of query objects that define the data to be recorded. Order matters as queries are evaluated sequentially."),
    range_: str | None = Field(None, alias="range", description="The time range in milliseconds over which the recording rule will evaluate data during the test."),
    target_ref_id: str | None = Field(None, description="The reference identifier of the target query or data source to use as the recording source."),
) -> dict[str, Any] | ToolResult:
    """Validate a recording rule configuration by testing it against the specified data source and queries. This operation allows you to verify the rule's behavior before applying it to production."""

    _interval = _parse_int(interval)
    _range_ = _parse_int(range_)

    # Construct request model with validation
    try:
        _request = _models.TestCreateRecordingRuleRequest(
            body=_models.TestCreateRecordingRuleRequestBody(active=active, count=count, description=description, dest_data_source_uid=dest_data_source_uid, interval=_interval, prom_name=prom_name, queries=queries, range_=_range_, target_ref_id=target_ref_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for test_recording_rule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/recording-rules/test"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("test_recording_rule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("test_recording_rule", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="test_recording_rule",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: recording_rules, enterprise
@mcp.tool()
async def create_remote_write_target(
    data_source_uid: str | None = Field(None, description="The unique identifier of the Prometheus data source to associate with this remote write target."),
    remote_write_path: str | None = Field(None, description="The endpoint path where Prometheus will send remote write requests for this target."),
) -> dict[str, Any] | ToolResult:
    """Create a remote write target for Prometheus recording rules. Requires an existing Prometheus data source to be configured, otherwise returns a 422 error."""

    # Construct request model with validation
    try:
        _request = _models.CreateRecordingRuleWriteTargetRequest(
            body=_models.CreateRecordingRuleWriteTargetRequestBody(data_source_uid=data_source_uid, remote_write_path=remote_write_path)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_remote_write_target: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/recording-rules/writer"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_remote_write_target")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_remote_write_target", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_remote_write_target",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: recording_rules, enterprise
@mcp.tool()
async def delete_recording_write_target() -> dict[str, Any] | ToolResult:
    """Remove the remote write target configuration for recording rules. This stops forwarding recorded metrics to the configured remote destination."""

    # Extract parameters for API call
    _http_path = "/recording-rules/writer"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_recording_write_target")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_recording_write_target", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_recording_write_target",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: recording_rules, enterprise
@mcp.tool()
async def delete_recording_rule(recording_rule_id: str = Field(..., alias="recordingRuleID", description="The unique identifier of the recording rule to delete. Must be a valid 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a recording rule from the registry and stop its execution. The rule will no longer be active after deletion."""

    _recording_rule_id = _parse_int(recording_rule_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteRecordingRuleRequest(
            path=_models.DeleteRecordingRuleRequestPath(recording_rule_id=_recording_rule_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_recording_rule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/recording-rules/{recordingRuleID}", _request.path.model_dump(by_alias=True)) if _request.path else "/recording-rules/{recordingRuleID}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_recording_rule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_recording_rule", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_recording_rule",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: reports, enterprise
@mcp.tool()
async def list_reports() -> dict[str, Any] | ToolResult:
    """Retrieve all reports available in the organization. Only accessible to organization administrators with a valid or expired license and the `reports:read` permission."""

    # Extract parameters for API call
    _http_path = "/reports"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_reports")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_reports", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_reports",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: reports, enterprise
@mcp.tool()
async def create_report(
    dashboards: list[_models.ReportDashboard] | None = Field(None, description="Array of dashboard IDs to include in the report. Dashboards will be rendered in the order specified."),
    enable_csv: bool | None = Field(None, alias="enableCsv", description="Enable CSV export format for the report output."),
    enable_dashboard_url: bool | None = Field(None, alias="enableDashboardUrl", description="Include direct URLs to dashboards in the report for easy navigation."),
    formats: list[str] | None = Field(None, description="Array of output formats for the report (e.g., PDF, PNG, CSV). Specifies which file formats to generate."),
    message: str | None = Field(None, description="Custom message to include in the report body or email delivery."),
    layout: str | None = Field(None, description="Page layout for PDF rendering (e.g., portrait, landscape, grid)."),
    orientation: str | None = Field(None, description="Page orientation for PDF output (portrait or landscape)."),
    pdf_combine_one_file: bool | None = Field(None, alias="pdfCombineOneFile", description="Combine all PDF pages into a single file instead of separate files per dashboard."),
    pdf_show_template_variables: bool | None = Field(None, alias="pdfShowTemplateVariables", description="Include template variable definitions and values in the PDF output for reference."),
    recipients: str | None = Field(None, description="Comma-separated list of email addresses to receive the report."),
    reply_to: str | None = Field(None, alias="replyTo", description="Reply-to email address for report delivery notifications."),
    scale_factor: str | None = Field(None, alias="scaleFactor", description="Scale factor for rendering dashboard content in the report. Specified as an integer representing the scaling percentage."),
    day_of_month: str | None = Field(None, alias="dayOfMonth", description="Day of the month for monthly recurring reports (1-31). Only applicable when frequency is set to monthly."),
    end_date: str | None = Field(None, alias="endDate", description="End date for the report schedule in ISO 8601 format. Report will stop being generated after this date."),
    frequency: str | None = Field(None, description="Frequency of report generation (e.g., once, daily, weekly, monthly, yearly)."),
    interval_amount: str | None = Field(None, alias="intervalAmount", description="Number of intervals between report generations. Used with intervalFrequency to define custom schedules."),
    interval_frequency: str | None = Field(None, alias="intervalFrequency", description="Time unit for the interval (e.g., hours, days, weeks, months). Defines the period between recurring reports."),
    start_date: str | None = Field(None, alias="startDate", description="Start date for the report schedule in ISO 8601 format. Report generation begins on this date."),
    time_zone: str | None = Field(None, alias="timeZone", description="Time zone for scheduling report generation and delivery (e.g., UTC, America/New_York). Affects when scheduled reports run."),
    workdays_only: bool | None = Field(None, alias="workdaysOnly", description="Generate reports only on business days, excluding weekends and holidays."),
    state: str | None = Field(None, description="Current state of the report (e.g., draft, active, paused, archived). Controls whether the report is actively generated."),
    subject: str | None = Field(None, description="Subject line for report email delivery."),
) -> dict[str, Any] | ToolResult:
    """Create a scheduled or on-demand report with customizable formatting, delivery options, and distribution settings. Requires organization admin privileges and a valid license with the `reports.admin:create` permission."""

    _scale_factor = _parse_int(scale_factor)
    _interval_amount = _parse_int(interval_amount)

    # Construct request model with validation
    try:
        _request = _models.CreateReportRequest(
            body=_models.CreateReportRequestBody(dashboards=dashboards, enable_csv=enable_csv, enable_dashboard_url=enable_dashboard_url, formats=formats, message=message, recipients=recipients, reply_to=reply_to, scale_factor=_scale_factor, state=state, subject=subject,
                options=_models.CreateReportRequestBodyOptions(layout=layout, orientation=orientation, pdf_combine_one_file=pdf_combine_one_file, pdf_show_template_variables=pdf_show_template_variables) if any(v is not None for v in [layout, orientation, pdf_combine_one_file, pdf_show_template_variables]) else None,
                schedule=_models.CreateReportRequestBodySchedule(day_of_month=day_of_month, end_date=end_date, frequency=frequency, interval_amount=_interval_amount, interval_frequency=interval_frequency, start_date=start_date, time_zone=time_zone, workdays_only=workdays_only) if any(v is not None for v in [day_of_month, end_date, frequency, interval_amount, interval_frequency, start_date, time_zone, workdays_only]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/reports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_report", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_report",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: reports, enterprise
@mcp.tool()
async def list_reports_by_dashboard(uid: str = Field(..., description="The unique identifier of the dashboard for which to retrieve associated reports.")) -> dict[str, Any] | ToolResult:
    """Retrieve all reports associated with a specific dashboard. Requires org admin privileges and a valid or expired license, with `reports:read` permission."""

    # Construct request model with validation
    try:
        _request = _models.GetReportsByDashboardUidRequest(
            path=_models.GetReportsByDashboardUidRequestPath(uid=uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_reports_by_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/reports/dashboards/{uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/reports/dashboards/{uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_reports_by_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_reports_by_dashboard", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_reports_by_dashboard",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: reports, enterprise
@mcp.tool()
async def send_report(emails: str | None = Field(None, description="Comma-separated list of email addresses to receive the report. If not provided, the report will be sent to default recipients based on your organization settings.")) -> dict[str, Any] | ToolResult:
    """Generate and send a report via email. This operation waits for report generation to complete before returning, so allow at least 60 seconds for the request to finish. Requires Grafana Enterprise v7.0+ with admin privileges and a valid license."""

    # Construct request model with validation
    try:
        _request = _models.SendReportRequest(
            body=_models.SendReportRequestBody(emails=emails)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/reports/email"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_report", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_report",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: reports, enterprise
@mcp.tool()
async def retrieve_branding_image(image: str = Field(..., description="Image filename to retrieve")) -> dict[str, Any] | ToolResult:
    """Retrieve a custom branding report image for your organization. Requires admin access and a valid or expired license."""

    # Construct request model with validation
    try:
        _request = _models.GetSettingsImageRequest(
            path=_models.GetSettingsImageRequestPath(image=image)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for retrieve_branding_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/reports/images/{image}", _request.path.model_dump(by_alias=True)) if _request.path else "/reports/images/{image}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("retrieve_branding_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("retrieve_branding_image", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="retrieve_branding_image",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: reports, enterprise
@mcp.tool()
async def download_csv_report(
    dashboards: str | None = Field(None, description="Comma-separated list of dashboard identifiers to include in the report. If omitted, the report includes all available dashboards."),
    title: str | None = Field(None, description="Custom title for the generated CSV report. If omitted, a default title is used."),
) -> dict[str, Any] | ToolResult:
    """Download a CSV-formatted report. Available to all users with a valid license."""

    # Construct request model with validation
    try:
        _request = _models.RenderReportCsVsRequest(
            query=_models.RenderReportCsVsRequestQuery(dashboards=dashboards, title=title)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for download_csv_report: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/reports/render/csvs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("download_csv_report")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("download_csv_report", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="download_csv_report",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reports, enterprise
@mcp.tool()
async def render_report_pdfs(
    dashboards: str | None = Field(None, description="Comma-separated list of dashboard identifiers to include in the report. Specifies which dashboards will be rendered into the PDF output."),
    orientation: str | None = Field(None, description="Page orientation for the PDF output. Controls whether the report renders in portrait or landscape format."),
    layout: str | None = Field(None, description="Layout configuration for dashboard arrangement. Determines how multiple dashboards are positioned and sized within the PDF pages."),
    title: str | None = Field(None, description="Custom title text to display at the top of the generated PDF report."),
    scale_factor: str | None = Field(None, alias="scaleFactor", description="Scaling factor to adjust the size of rendered content. Controls zoom level of dashboards in the final PDF output."),
    include_tables: str | None = Field(None, alias="includeTables", description="Flag to include or exclude data tables associated with the dashboards in the PDF report."),
) -> dict[str, Any] | ToolResult:
    """Generate a PDF report rendering multiple dashboards with customizable layout, orientation, and styling options. Available to all licensed users."""

    # Construct request model with validation
    try:
        _request = _models.RenderReportPdFsRequest(
            query=_models.RenderReportPdFsRequestQuery(dashboards=dashboards, orientation=orientation, layout=layout, title=title, scale_factor=scale_factor, include_tables=include_tables)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for render_report_pdfs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/reports/render/pdfs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("render_report_pdfs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("render_report_pdfs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="render_report_pdfs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: reports, enterprise
@mcp.tool()
async def send_test_report_email(
    dashboards: list[_models.ReportDashboard] | None = Field(None, description="List of dashboard IDs to include in the report."),
    enable_csv: bool | None = Field(None, alias="enableCsv", description="Include CSV format export in the email."),
    enable_dashboard_url: bool | None = Field(None, alias="enableDashboardUrl", description="Include a direct URL link to the dashboard in the email."),
    formats: list[str] | None = Field(None, description="Array of output formats for the report (e.g., PDF, PNG, CSV)."),
    message: str | None = Field(None, description="Custom message body to include in the email."),
    layout: str | None = Field(None, description="Page layout for rendered reports (e.g., portrait, landscape)."),
    orientation: str | None = Field(None, description="Page orientation for PDF output (portrait or landscape)."),
    pdf_combine_one_file: bool | None = Field(None, alias="pdfCombineOneFile", description="Combine multiple pages into a single PDF file."),
    pdf_show_template_variables: bool | None = Field(None, alias="pdfShowTemplateVariables", description="Include template variable definitions in the PDF output."),
    recipients: str | None = Field(None, description="Email address or comma-separated list of recipient email addresses."),
    reply_to: str | None = Field(None, alias="replyTo", description="Reply-to email address for responses."),
    scale_factor: str | None = Field(None, alias="scaleFactor", description="Scale factor for rendering, specified as an integer value."),
    day_of_month: str | None = Field(None, alias="dayOfMonth", description="Day of month for recurring reports (1-31)."),
    end_date: str | None = Field(None, alias="endDate", description="End date for the report schedule in ISO 8601 format."),
    frequency: str | None = Field(None, description="Frequency of report delivery (e.g., daily, weekly, monthly)."),
    interval_amount: str | None = Field(None, alias="intervalAmount", description="Number of intervals between report deliveries."),
    interval_frequency: str | None = Field(None, alias="intervalFrequency", description="Unit of time for the interval (e.g., days, weeks, months)."),
    start_date: str | None = Field(None, alias="startDate", description="Start date for the report schedule in ISO 8601 format."),
    time_zone: str | None = Field(None, alias="timeZone", description="Timezone for scheduling report delivery (e.g., UTC, America/New_York)."),
    workdays_only: bool | None = Field(None, alias="workdaysOnly", description="Deliver reports only on business days (Monday-Friday)."),
    state: str | None = Field(None, description="Current state of the report schedule (e.g., active, paused, draft)."),
    subject: str | None = Field(None, description="Email subject line for the report."),
) -> dict[str, Any] | ToolResult:
    """Send a test report via email to verify configuration before scheduling. Requires organization admin privileges and a valid license with the `reports:send` permission."""

    _scale_factor = _parse_int(scale_factor)
    _interval_amount = _parse_int(interval_amount)

    # Construct request model with validation
    try:
        _request = _models.SendTestEmailRequest(
            body=_models.SendTestEmailRequestBody(dashboards=dashboards, enable_csv=enable_csv, enable_dashboard_url=enable_dashboard_url, formats=formats, message=message, recipients=recipients, reply_to=reply_to, scale_factor=_scale_factor, state=state, subject=subject,
                options=_models.SendTestEmailRequestBodyOptions(layout=layout, orientation=orientation, pdf_combine_one_file=pdf_combine_one_file, pdf_show_template_variables=pdf_show_template_variables) if any(v is not None for v in [layout, orientation, pdf_combine_one_file, pdf_show_template_variables]) else None,
                schedule=_models.SendTestEmailRequestBodySchedule(day_of_month=day_of_month, end_date=end_date, frequency=frequency, interval_amount=_interval_amount, interval_frequency=interval_frequency, start_date=start_date, time_zone=time_zone, workdays_only=workdays_only) if any(v is not None for v in [day_of_month, end_date, frequency, interval_amount, interval_frequency, start_date, time_zone, workdays_only]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_test_report_email: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/reports/test-email"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_test_report_email")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_test_report_email", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_test_report_email",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: search
@mcp.tool()
async def search_dashboards(
    tag: list[str] | None = Field(None, description="Filter results by one or more tags. Only dashboards matching all specified tags will be returned."),
    dashboard_ui_ds: list[str] | None = Field(None, alias="dashboardUIDs", description="Filter results to specific dashboards by their unique identifiers (UIDs)."),
    folder_ui_ds: list[str] | None = Field(None, alias="folderUIDs", description="Limit search scope to dashboards within specific folders by their UIDs. Use an empty string to search only top-level folders."),
    starred: bool | None = Field(None, description="When enabled, return only dashboards that have been marked as starred by the user."),
    limit: str | None = Field(None, description="Maximum number of results to return, up to 5000 results per request."),
    permission: Literal["Edit", "View"] | None = Field(None, description="Filter by user permissions: 'View' returns dashboards the user can view, 'Edit' returns only dashboards the user can edit. Defaults to 'View'."),
    sort: Literal["alpha-asc", "alpha-desc"] | None = Field(None, description="Sort results by dashboard name in ascending or descending alphabetical order. Defaults to ascending alphabetical order."),
    deleted: bool | None = Field(None, description="When enabled, return only dashboards that have been soft deleted (not permanently removed)."),
) -> dict[str, Any] | ToolResult:
    """Search for dashboards and folders by tags, UIDs, starred status, and other criteria. Returns matching dashboards with optional filtering by permissions and deletion status."""

    _limit = _parse_int(limit)

    # Construct request model with validation
    try:
        _request = _models.SearchRequest(
            query=_models.SearchRequestQuery(tag=tag, dashboard_ui_ds=dashboard_ui_ds, folder_ui_ds=folder_ui_ds, starred=starred, limit=_limit, permission=permission, sort=sort, deleted=deleted)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_dashboards: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_dashboards")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_dashboards", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_dashboards",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: search
@mcp.tool()
async def list_sort_options() -> dict[str, Any] | ToolResult:
    """Retrieve available sorting options for search results. Use this to discover valid sort fields and ordering directions supported by the search API."""

    # Extract parameters for API call
    _http_path = "/search/sorting"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_sort_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_sort_options", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_sort_options",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: service_accounts
@mcp.tool()
async def create_service_account(
    is_disabled: bool | None = Field(None, alias="isDisabled", description="Whether the service account should be created in a disabled state. Defaults to false (enabled)."),
    role: Literal["None", "Viewer", "Editor", "Admin"] | None = Field(None, description="The role to assign to the service account. Must be one of: None, Viewer, Editor, or Admin. Defaults to None if not specified."),
    name: str | None = Field(None),
) -> dict[str, Any] | ToolResult:
    """Create a new service account in Grafana for programmatic access. Requires Grafana Admin privileges and basic authentication."""

    # Construct request model with validation
    try:
        _request = _models.CreateServiceAccountRequest(
            body=_models.CreateServiceAccountRequestBody(is_disabled=is_disabled, role=role, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_service_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/serviceaccounts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_service_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_service_account", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_service_account",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: service_accounts
@mcp.tool()
async def list_service_accounts(
    disabled: bool | None = Field(None, alias="Disabled", description="Filter to include only disabled service accounts when set to true, or only active accounts when false."),
    expired_tokens: bool | None = Field(None, alias="expiredTokens", description="Filter to include only service accounts with expired tokens when set to true."),
    perpage: str | None = Field(None, description="Number of service accounts to return per page. Defaults to 1000 if not specified."),
) -> dict[str, Any] | ToolResult:
    """Search and retrieve service accounts with pagination support. Requires `serviceaccounts:read` permission with `serviceaccounts:*` scope."""

    _perpage = _parse_int(perpage)

    # Construct request model with validation
    try:
        _request = _models.SearchOrgServiceAccountsWithPagingRequest(
            query=_models.SearchOrgServiceAccountsWithPagingRequestQuery(disabled=disabled, expired_tokens=expired_tokens, perpage=_perpage)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_service_accounts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/serviceaccounts/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_service_accounts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_service_accounts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_service_accounts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: service_accounts
@mcp.tool()
async def get_service_account(service_account_id: str = Field(..., alias="serviceAccountId", description="The unique identifier of the service account to retrieve. Must be a positive integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific service account by its ID. Requires serviceaccounts:read permission with scope limited to the requested service account."""

    _service_account_id = _parse_int(service_account_id)

    # Construct request model with validation
    try:
        _request = _models.RetrieveServiceAccountRequest(
            path=_models.RetrieveServiceAccountRequestPath(service_account_id=_service_account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_service_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/serviceaccounts/{serviceAccountId}", _request.path.model_dump(by_alias=True)) if _request.path else "/serviceaccounts/{serviceAccountId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_service_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_service_account", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_service_account",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: service_accounts
@mcp.tool()
async def update_service_account(
    service_account_id: str = Field(..., alias="serviceAccountId", description="The unique identifier of the service account to update. Must be a valid 64-bit integer."),
    is_disabled: bool | None = Field(None, alias="isDisabled", description="Whether the service account is disabled. Set to true to deactivate the account or false to enable it."),
    role: Literal["None", "Viewer", "Editor", "Admin"] | None = Field(None, description="The role to assign to the service account. Must be one of: None, Viewer, Editor, or Admin."),
) -> dict[str, Any] | ToolResult:
    """Modify an existing service account's configuration, including its enabled status and role assignment. Requires serviceaccounts:write permission for the specific service account."""

    _service_account_id = _parse_int(service_account_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateServiceAccountRequest(
            path=_models.UpdateServiceAccountRequestPath(service_account_id=_service_account_id),
            body=_models.UpdateServiceAccountRequestBody(is_disabled=is_disabled, role=role)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_service_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/serviceaccounts/{serviceAccountId}", _request.path.model_dump(by_alias=True)) if _request.path else "/serviceaccounts/{serviceAccountId}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_service_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_service_account", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_service_account",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: service_accounts
@mcp.tool()
async def delete_service_account(service_account_id: str = Field(..., alias="serviceAccountId", description="The unique identifier of the service account to delete. Must be a positive integer.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a service account by its ID. Requires serviceaccounts:delete permission and serviceaccounts:id:{serviceAccountId} scope."""

    _service_account_id = _parse_int(service_account_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteServiceAccountRequest(
            path=_models.DeleteServiceAccountRequestPath(service_account_id=_service_account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_service_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/serviceaccounts/{serviceAccountId}", _request.path.model_dump(by_alias=True)) if _request.path else "/serviceaccounts/{serviceAccountId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_service_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_service_account", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_service_account",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: service_accounts
@mcp.tool()
async def list_service_account_tokens(service_account_id: str = Field(..., alias="serviceAccountId", description="The unique identifier of the service account. Must be a positive integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve all API tokens associated with a specific service account. Requires Grafana Admin privileges and the serviceaccounts:read permission for the target service account."""

    _service_account_id = _parse_int(service_account_id)

    # Construct request model with validation
    try:
        _request = _models.ListTokensRequest(
            path=_models.ListTokensRequestPath(service_account_id=_service_account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_service_account_tokens: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/serviceaccounts/{serviceAccountId}/tokens", _request.path.model_dump(by_alias=True)) if _request.path else "/serviceaccounts/{serviceAccountId}/tokens"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_service_account_tokens")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_service_account_tokens", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_service_account_tokens",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: service_accounts
@mcp.tool()
async def create_service_account_token(
    service_account_id: str = Field(..., alias="serviceAccountId", description="The unique identifier of the service account for which to create the token. Must be a positive integer."),
    seconds_to_live: str | None = Field(None, alias="secondsToLive", description="Optional token lifetime in seconds. If specified, the token will automatically expire after this duration. If omitted, the token will not expire."),
    name: str | None = Field(None),
) -> dict[str, Any] | ToolResult:
    """Generate a new authentication token for a service account. The token can be configured with an optional expiration time in seconds."""

    _service_account_id = _parse_int(service_account_id)
    _seconds_to_live = _parse_int(seconds_to_live)

    # Construct request model with validation
    try:
        _request = _models.CreateTokenRequest(
            path=_models.CreateTokenRequestPath(service_account_id=_service_account_id),
            body=_models.CreateTokenRequestBody(seconds_to_live=_seconds_to_live, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_service_account_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/serviceaccounts/{serviceAccountId}/tokens", _request.path.model_dump(by_alias=True)) if _request.path else "/serviceaccounts/{serviceAccountId}/tokens"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_service_account_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_service_account_token", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_service_account_token",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: service_accounts
@mcp.tool()
async def revoke_service_account_token(
    token_id: str = Field(..., alias="tokenId", description="The unique identifier of the service account token to revoke. Must be a positive integer."),
    service_account_id: str = Field(..., alias="serviceAccountId", description="The unique identifier of the service account that owns the token. Must be a positive integer."),
) -> dict[str, Any] | ToolResult:
    """Revoke and delete a specific token for a service account. Requires Grafana Admin privileges and the serviceaccounts:write permission for the target service account."""

    _token_id = _parse_int(token_id)
    _service_account_id = _parse_int(service_account_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteTokenRequest(
            path=_models.DeleteTokenRequestPath(token_id=_token_id, service_account_id=_service_account_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_service_account_token: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/serviceaccounts/{serviceAccountId}/tokens/{tokenId}", _request.path.model_dump(by_alias=True)) if _request.path else "/serviceaccounts/{serviceAccountId}/tokens/{tokenId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_service_account_token")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_service_account_token", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_service_account_token",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: snapshots
@mcp.tool()
async def list_snapshot_sharing_options() -> dict[str, Any] | ToolResult:
    """Retrieve the available sharing settings and options for snapshots. Use this to understand what sharing configurations are supported before sharing a snapshot."""

    # Extract parameters for API call
    _http_path = "/snapshot/shared-options"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_snapshot_sharing_options")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_snapshot_sharing_options", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_snapshot_sharing_options",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dashboards, snapshots
@mcp.tool()
async def create_snapshot(
    dashboard: dict[str, Any] = Field(..., description="The complete dashboard model object to snapshot."),
    delete_key: str | None = Field(None, alias="deleteKey", description="A unique key that grants deletion permissions for this snapshot. Required when storing the snapshot externally. Only the snapshot creator should have access to this key."),
    expires: str | None = Field(None, description="The number of seconds before the snapshot automatically expires and becomes unavailable. Omit or set to 0 to keep the snapshot indefinitely."),
    external: bool | None = Field(None, description="When enabled, stores the snapshot on an external server instead of locally. Requires both `key` and `deleteKey` to be provided."),
    key: str | None = Field(None, description="A unique identifier for this snapshot. Required when storing the snapshot externally. Used to reference and retrieve the snapshot."),
) -> dict[str, Any] | ToolResult:
    """Create a snapshot of a dashboard for sharing or archival. Requires either public snapshot mode to be enabled or valid authentication credentials."""

    _expires = _parse_int(expires)

    # Construct request model with validation
    try:
        _request = _models.CreateDashboardSnapshotRequest(
            body=_models.CreateDashboardSnapshotRequestBody(delete_key=delete_key, expires=_expires, external=external, key=key, dashboard=dashboard)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_snapshot: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/snapshots"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_snapshot")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_snapshot", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_snapshot",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: dashboards, snapshots
@mcp.tool()
async def delete_snapshot_by_delete_key(delete_key: str = Field(..., alias="deleteKey", description="The unique delete key that identifies the snapshot to be deleted. This key is typically provided when the snapshot is created or shared.")) -> dict[str, Any] | ToolResult:
    """Delete a snapshot using its unique delete key. Requires either public snapshot mode to be enabled or valid authentication credentials."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDashboardSnapshotByDeleteKeyRequest(
            path=_models.DeleteDashboardSnapshotByDeleteKeyRequestPath(delete_key=delete_key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_snapshot_by_delete_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snapshots-delete/{deleteKey}", _request.path.model_dump(by_alias=True)) if _request.path else "/snapshots-delete/{deleteKey}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_snapshot_by_delete_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_snapshot_by_delete_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_snapshot_by_delete_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dashboards, snapshots
@mcp.tool()
async def get_snapshot_by_key(key: str = Field(..., description="The unique identifier of the snapshot to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a dashboard snapshot by its unique identifier. Returns the snapshot data associated with the provided key."""

    # Construct request model with validation
    try:
        _request = _models.GetDashboardSnapshotRequest(
            path=_models.GetDashboardSnapshotRequestPath(key=key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_snapshot_by_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snapshots/{key}", _request.path.model_dump(by_alias=True)) if _request.path else "/snapshots/{key}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_snapshot_by_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_snapshot_by_key", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_snapshot_by_key",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dashboards, snapshots
@mcp.tool()
async def delete_snapshot(key: str = Field(..., description="The unique identifier of the snapshot to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a dashboard snapshot by its unique key. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDashboardSnapshotRequest(
            path=_models.DeleteDashboardSnapshotRequestPath(key=key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_snapshot: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/snapshots/{key}", _request.path.model_dump(by_alias=True)) if _request.path else "/snapshots/{key}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_snapshot")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_snapshot", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_snapshot",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: teams
@mcp.tool()
async def create_team(
    name: str = Field(..., description="The name of the team. This is a required identifier used to distinguish the team from others."),
    email: str | None = Field(None, description="Email address associated with the team for contact and notifications purposes."),
) -> dict[str, Any] | ToolResult:
    """Create a new team with a required name and optional email contact. This establishes a new team entity that can be used to organize users and resources."""

    # Construct request model with validation
    try:
        _request = _models.CreateTeamRequest(
            body=_models.CreateTeamRequestBody(email=email, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/teams"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

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
        headers=_http_headers,
    )

    return _response_data

# Tags: teams
@mcp.tool()
async def list_teams(
    perpage: str | None = Field(None, description="Number of teams to return per page for pagination. Defaults to 1000 items per page. Use this with totalCount from the response to navigate through all results."),
    sort: str | None = Field(None, description="Field to sort results by. Specify the team attribute name to order the returned teams."),
) -> dict[str, Any] | ToolResult:
    """Search and retrieve teams with pagination support. Use the totalCount field in the response to determine the number of pages available."""

    _perpage = _parse_int(perpage)

    # Construct request model with validation
    try:
        _request = _models.SearchTeamsRequest(
            query=_models.SearchTeamsRequestQuery(perpage=_perpage, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_teams: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/teams/search"
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

# Tags: sync_team_groups, enterprise
@mcp.tool()
async def list_team_groups(team_id: str = Field(..., alias="teamId", description="The unique identifier of the team for which to retrieve associated external groups.")) -> dict[str, Any] | ToolResult:
    """Retrieve all external groups associated with a specific team. This returns a list of groups that have been configured for the team."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamGroupsApiRequest(
            path=_models.GetTeamGroupsApiRequestPath(team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{teamId}/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{teamId}/groups"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_team_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_team_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_team_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: sync_team_groups, enterprise
@mcp.tool()
async def add_group_to_team(
    team_id: str = Field(..., alias="teamId", description="The unique identifier of the team to which the group will be added."),
    group_id: str | None = Field(None, alias="groupId", description="The unique identifier of the external group to add to the team."),
) -> dict[str, Any] | ToolResult:
    """Add an external group to a team, enabling group-level access and collaboration within the team."""

    # Construct request model with validation
    try:
        _request = _models.AddTeamGroupApiRequest(
            path=_models.AddTeamGroupApiRequestPath(team_id=team_id),
            body=_models.AddTeamGroupApiRequestBody(group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_group_to_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{teamId}/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{teamId}/groups"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_group_to_team")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_group_to_team", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_group_to_team",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: sync_team_groups, enterprise
@mcp.tool()
async def remove_team_group(
    team_id: str = Field(..., alias="teamId", description="The unique identifier of the team from which the group will be removed."),
    group_id: str | None = Field(None, alias="groupId", description="The unique identifier of the external group to remove from the team."),
) -> dict[str, Any] | ToolResult:
    """Remove an external group from a team. This operation deletes the association between a specific group and the team."""

    # Construct request model with validation
    try:
        _request = _models.RemoveTeamGroupApiQueryRequest(
            path=_models.RemoveTeamGroupApiQueryRequestPath(team_id=team_id),
            query=_models.RemoveTeamGroupApiQueryRequestQuery(group_id=group_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_team_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{teamId}/groups", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{teamId}/groups"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_team_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_team_group", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_team_group",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: sync_team_groups, enterprise
@mcp.tool()
async def search_groups(
    team_id: str = Field(..., alias="teamId", description="The unique identifier of the team to search groups within. Required to scope the search to a specific team."),
    perpage: str | None = Field(None, description="Maximum number of results to return per page. Defaults to 1000 items if not specified."),
) -> dict[str, Any] | ToolResult:
    """Search for groups within a team with optional filtering and pagination support. Returns matching groups based on search criteria with configurable result limits."""

    _team_id = _parse_int(team_id)
    _perpage = _parse_int(perpage)

    # Construct request model with validation
    try:
        _request = _models.SearchTeamGroupsRequest(
            path=_models.SearchTeamGroupsRequestPath(team_id=_team_id),
            query=_models.SearchTeamGroupsRequestQuery(perpage=_perpage)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_groups: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{teamId}/groups/search", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{teamId}/groups/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: teams
@mcp.tool()
async def get_team(team_id: str = Field(..., description="The unique identifier of the team to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific team by its unique identifier. Returns the team's details including name, members, and configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamByIdRequest(
            path=_models.GetTeamByIdRequestPath(team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_id}"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: teams
@mcp.tool()
async def update_team(
    team_id: str = Field(..., description="The unique identifier of the team to update."),
    email: str | None = Field(None, description="The email address to associate with the team."),
) -> dict[str, Any] | ToolResult:
    """Update an existing team's information, such as the associated email address. Provide the team ID and any fields you want to modify."""

    # Construct request model with validation
    try:
        _request = _models.UpdateTeamRequest(
            path=_models.UpdateTeamRequestPath(team_id=team_id),
            body=_models.UpdateTeamRequestBody(email=email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

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
        headers=_http_headers,
    )

    return _response_data

# Tags: teams
@mcp.tool()
async def delete_team(team_id: str = Field(..., description="The unique identifier of the team to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a team by its ID. This action removes the team and all associated data."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTeamByIdRequest(
            path=_models.DeleteTeamByIdRequestPath(team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_team: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_id}"
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

# Tags: teams
@mcp.tool()
async def list_team_members(team_id: str = Field(..., description="The unique identifier of the team whose members you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve all members belonging to a specific team. Returns a list of team members with their associated details and roles."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamMembersRequest(
            path=_models.GetTeamMembersRequestPath(team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_team_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_id}/members", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_id}/members"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_team_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_team_members", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_team_members",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: teams
@mcp.tool()
async def add_team_member(
    team_id: str = Field(..., description="The unique identifier of the team to which the member will be added."),
    user_id: str = Field(..., alias="userId", description="The unique identifier of the user to add to the team, specified as a 64-bit integer."),
) -> dict[str, Any] | ToolResult:
    """Add a user to a team by their user ID. The user will gain access to the team's resources and collaboration features."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.AddTeamMemberRequest(
            path=_models.AddTeamMemberRequestPath(team_id=team_id),
            body=_models.AddTeamMemberRequestBody(user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_team_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_id}/members", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_id}/members"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_team_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_team_member", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_team_member",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: teams
@mcp.tool()
async def update_team_members(
    team_id: str = Field(..., description="The unique identifier of the team to update."),
    admins: list[str] | None = Field(None, description="List of user email addresses to set as team admins. Users should be specified by their email addresses. Omit or provide an empty list to remove all admins."),
    members: list[str] | None = Field(None, description="List of user email addresses to set as team members. Users should be specified by their email addresses. Omit or provide an empty list to remove all members."),
) -> dict[str, Any] | ToolResult:
    """Update team membership by replacing the current members and admins with the provided lists. Any existing members or admins not included in the new lists will be removed from the team."""

    # Construct request model with validation
    try:
        _request = _models.SetTeamMembershipsRequest(
            path=_models.SetTeamMembershipsRequestPath(team_id=team_id),
            body=_models.SetTeamMembershipsRequestBody(admins=admins, members=members)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_team_members: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_id}/members", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_id}/members"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_team_members")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_team_members", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_team_members",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: teams
@mcp.tool()
async def update_team_member(
    team_id: str = Field(..., description="The unique identifier of the team containing the member to be updated."),
    user_id: str = Field(..., description="The unique identifier of the user whose team membership and permissions should be updated. This is a 64-bit integer value."),
    permission: str | None = Field(None, description="The permission level to assign to the team member, specified as a 64-bit integer. This determines the member's access rights and capabilities within the team."),
) -> dict[str, Any] | ToolResult:
    """Update a team member's information and permissions within a specific team. Modify the member's role or access level by specifying their permission level."""

    _user_id = _parse_int(user_id)
    _permission = _parse_int(permission)

    # Construct request model with validation
    try:
        _request = _models.UpdateTeamMemberRequest(
            path=_models.UpdateTeamMemberRequestPath(team_id=team_id, user_id=_user_id),
            body=_models.UpdateTeamMemberRequestBody(permission=_permission)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_team_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_id}/members/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_id}/members/{user_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_team_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_team_member", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_team_member",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: teams
@mcp.tool()
async def remove_team_member(
    team_id: str = Field(..., description="The unique identifier of the team from which the member will be removed."),
    user_id: str = Field(..., description="The unique identifier of the user to be removed from the team. Must be a valid 64-bit integer."),
) -> dict[str, Any] | ToolResult:
    """Remove a user from a team, revoking their access and team membership. The user will no longer have permissions to view or interact with team resources."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.RemoveTeamMemberRequest(
            path=_models.RemoveTeamMemberRequestPath(team_id=team_id, user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_team_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_id}/members/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_id}/members/{user_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_team_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_team_member", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_team_member",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: teams, preferences
@mcp.tool()
async def get_team_preferences(team_id: str = Field(..., description="The unique identifier of the team whose preferences you want to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve the preferences and settings configured for a specific team, including notification defaults, display options, and other team-level configurations."""

    # Construct request model with validation
    try:
        _request = _models.GetTeamPreferencesRequest(
            path=_models.GetTeamPreferencesRequestPath(team_id=team_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_team_preferences: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/teams/{team_id}/preferences", _request.path.model_dump(by_alias=True)) if _request.path else "/teams/{team_id}/preferences"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_team_preferences")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_team_preferences", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_team_preferences",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: signed_in_user
@mcp.tool()
async def get_current_user() -> dict[str, Any] | ToolResult:
    """Retrieve the profile and details of the currently authenticated user. This operation requires valid authentication credentials."""

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

# Tags: signed_in_user
@mcp.tool()
async def update_user_profile(
    email: str | None = Field(None, description="The new email address for the user account. Must be a valid email format."),
    login: str | None = Field(None, description="The new login username for the user account. Used for authentication and account identification."),
    theme: str | None = Field(None, description="The preferred display theme for the user interface (e.g., light, dark, auto)."),
) -> dict[str, Any] | ToolResult:
    """Update the profile information for the currently signed-in user, including email address, login username, and display theme preference."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSignedInUserRequest(
            body=_models.UpdateSignedInUserRequestBody(email=email, login=login, theme=theme)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user_profile: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user_profile")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user_profile", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user_profile",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: signed_in_user
@mcp.tool()
async def list_auth_tokens() -> dict[str, Any] | ToolResult:
    """Retrieve all active authentication tokens for the current user, showing all devices and sessions currently logged in."""

    # Extract parameters for API call
    _http_path = "/user/auth-tokens"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_auth_tokens")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_auth_tokens", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_auth_tokens",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: signed_in_user
@mcp.tool()
async def clear_help_flags() -> dict[str, Any] | ToolResult:
    """Clear all help flags for the current user. This resets any tutorial or onboarding prompts that may have been dismissed."""

    # Extract parameters for API call
    _http_path = "/user/helpflags/clear"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("clear_help_flags")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("clear_help_flags", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="clear_help_flags",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: signed_in_user
@mcp.tool()
async def enable_help_flag(flag_id: str = Field(..., description="The unique identifier of the help flag to enable.")) -> dict[str, Any] | ToolResult:
    """Enable a specific help flag for the user to control which help features or guidance are displayed."""

    # Construct request model with validation
    try:
        _request = _models.SetHelpFlagRequest(
            path=_models.SetHelpFlagRequestPath(flag_id=flag_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for enable_help_flag: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user/helpflags/{flag_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/user/helpflags/{flag_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("enable_help_flag")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("enable_help_flag", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="enable_help_flag",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: signed_in_user
@mcp.tool()
async def list_user_organizations() -> dict[str, Any] | ToolResult:
    """Retrieve all organizations that the currently authenticated user belongs to or has access to."""

    # Extract parameters for API call
    _http_path = "/user/orgs"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_organizations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_organizations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_organizations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: signed_in_user, preferences
@mcp.tool()
async def get_user_preferences() -> dict[str, Any] | ToolResult:
    """Retrieve the current user's preference settings, including display options, notification settings, and other personalization choices."""

    # Extract parameters for API call
    _http_path = "/user/preferences"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_preferences")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_preferences", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_preferences",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: signed_in_user, preferences
@mcp.tool()
async def update_user_preferences_partial(
    home_dashboard_uid: str | None = Field(None, alias="homeDashboardUID", description="The unique identifier of the dashboard to set as the user's home dashboard."),
    language: str | None = Field(None, description="The user's preferred language for the interface."),
    regional_format: str | None = Field(None, alias="regionalFormat", description="The user's preferred regional format for displaying dates, numbers, and currency."),
    theme: Literal["light", "dark"] | None = Field(None, description="The user's preferred color theme. Choose between light mode or dark mode."),
    timezone_: str | None = Field(None, alias="timezone", description="The user's timezone for displaying times and scheduling. Accepts any IANA timezone identifier (e.g., America/New_York), 'utc' for UTC, 'browser' to use the browser's timezone, or an empty string for no preference."),
    week_start: str | None = Field(None, alias="weekStart", description="The day of the week to display as the first day in calendar views."),
) -> dict[str, Any] | ToolResult:
    """Update user preferences for dashboard, display, and localization settings. Allows customization of theme, timezone, language, and other UI preferences."""

    # Construct request model with validation
    try:
        _request = _models.PatchUserPreferencesRequest(
            body=_models.PatchUserPreferencesRequestBody(home_dashboard_uid=home_dashboard_uid, language=language, regional_format=regional_format, theme=theme, timezone_=timezone_, week_start=week_start)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user_preferences_partial: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/user/preferences"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_user_preferences_partial")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_user_preferences_partial", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_user_preferences_partial",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: quota, signed_in_user
@mcp.tool()
async def list_user_quotas() -> dict[str, Any] | ToolResult:
    """Retrieve the current quota limits and usage for the authenticated user across all resources and services."""

    # Extract parameters for API call
    _http_path = "/user/quotas"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_quotas")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_quotas", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_quotas",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: signed_in_user
@mcp.tool()
async def star_dashboard(dashboard_uid: str = Field(..., description="The unique identifier of the dashboard to star.")) -> dict[str, Any] | ToolResult:
    """Add a dashboard to the current user's starred dashboards. Starred dashboards appear in the user's favorites for quick access."""

    # Construct request model with validation
    try:
        _request = _models.StarDashboardByUidRequest(
            path=_models.StarDashboardByUidRequestPath(dashboard_uid=dashboard_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for star_dashboard: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user/stars/dashboard/uid/{dashboard_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/user/stars/dashboard/uid/{dashboard_uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("star_dashboard")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("star_dashboard", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="star_dashboard",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: signed_in_user
@mcp.tool()
async def remove_dashboard_star(dashboard_uid: str = Field(..., description="The unique identifier of the dashboard to unstar. This is the dashboard's UID that was previously starred by the user.")) -> dict[str, Any] | ToolResult:
    """Remove a dashboard from the current user's starred list. This action deletes the star marking for the specified dashboard."""

    # Construct request model with validation
    try:
        _request = _models.UnstarDashboardByUidRequest(
            path=_models.UnstarDashboardByUidRequestPath(dashboard_uid=dashboard_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_dashboard_star: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user/stars/dashboard/uid/{dashboard_uid}", _request.path.model_dump(by_alias=True)) if _request.path else "/user/stars/dashboard/uid/{dashboard_uid}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_dashboard_star")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_dashboard_star", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_dashboard_star",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: signed_in_user
@mcp.tool()
async def list_user_teams() -> dict[str, Any] | ToolResult:
    """Retrieve all teams that the currently authenticated user is a member of. This returns the complete list of teams associated with the user's account."""

    # Extract parameters for API call
    _http_path = "/user/teams"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_teams")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_teams", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_teams",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: signed_in_user
@mcp.tool()
async def switch_organization(org_id: str = Field(..., description="The unique identifier of the organization to switch to. Must be a valid 64-bit integer representing an existing organization the user has access to.")) -> dict[str, Any] | ToolResult:
    """Switch the authenticated user's active organization context to the specified organization. This changes which organization's data and resources the user will access in subsequent operations."""

    _org_id = _parse_int(org_id)

    # Construct request model with validation
    try:
        _request = _models.UserSetUsingOrgRequest(
            path=_models.UserSetUsingOrgRequestPath(org_id=_org_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for switch_organization: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/user/using/{org_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/user/using/{org_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("switch_organization")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("switch_organization", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="switch_organization",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_users(perpage: str | None = Field(None, description="Maximum number of users to return per page. Defaults to 1000 if not specified.")) -> dict[str, Any] | ToolResult:
    """Retrieve all users that the authenticated user has permission to view. Requires admin permission to access this operation."""

    _perpage = _parse_int(perpage)

    # Construct request model with validation
    try:
        _request = _models.SearchUsersRequest(
            query=_models.SearchUsersRequestQuery(perpage=_perpage)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users"
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

# Tags: users
@mcp.tool()
async def lookup_user(login_or_email: str = Field(..., alias="loginOrEmail", description="The user's login name or email address to search for. Accepts either format to locate the user account.")) -> dict[str, Any] | ToolResult:
    """Retrieve a user account by their login name or email address. Use this to find user details when you have either identifier available."""

    # Construct request model with validation
    try:
        _request = _models.GetUserByLoginOrEmailRequest(
            query=_models.GetUserByLoginOrEmailRequestQuery(login_or_email=login_or_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for lookup_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/users/lookup"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("lookup_user")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("lookup_user", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="lookup_user",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_users_paginated() -> dict[str, Any] | ToolResult:
    """Retrieve a paginated list of users from the system. Use this operation to browse users with built-in pagination support for efficient data retrieval."""

    # Extract parameters for API call
    _http_path = "/users/search"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_users_paginated")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_users_paginated", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_users_paginated",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_user(user_id: str = Field(..., description="The unique identifier of the user to retrieve, specified as a 64-bit integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific user by their unique identifier. Returns the user's profile information and details."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.GetUserByIdRequest(
            path=_models.GetUserByIdRequestPath(user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}"
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

# Tags: users
@mcp.tool()
async def update_user(
    user_id: str = Field(..., description="The unique identifier of the user to update. Must be a positive integer."),
    email: str | None = Field(None, description="The user's email address. Optional field for updating contact information."),
    login: str | None = Field(None, description="The user's login username or identifier. Optional field for updating authentication credentials."),
    theme: str | None = Field(None, description="The user's preferred display theme or UI preference. Optional field for customizing the user experience."),
) -> dict[str, Any] | ToolResult:
    """Update user account details including email, login credentials, and display preferences. Modifies the user record identified by the provided user ID."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.UpdateUserRequest(
            path=_models.UpdateUserRequestPath(user_id=_user_id),
            body=_models.UpdateUserRequestBody(email=email, login=login, theme=theme)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_user: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

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
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_user_organizations_by_id(user_id: str = Field(..., description="The unique identifier of the user. Must be a positive integer value.")) -> dict[str, Any] | ToolResult:
    """Retrieve all organizations associated with a specific user. Returns a list of organizations where the user is a member or has access."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.GetUserOrgListRequest(
            path=_models.GetUserOrgListRequestPath(user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_organizations_by_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/orgs", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/orgs"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_organizations_by_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_organizations_by_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_organizations_by_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_user_teams_by_id(user_id: str = Field(..., description="The unique identifier of the user. Must be a positive integer.")) -> dict[str, Any] | ToolResult:
    """Retrieve all teams that a user is a member of. Returns a list of teams associated with the specified user."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.GetUserTeamsRequest(
            path=_models.GetUserTeamsRequestPath(user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_user_teams_by_id: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/users/{user_id}/teams", _request.path.model_dump(by_alias=True)) if _request.path else "/users/{user_id}/teams"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_user_teams_by_id")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_user_teams_by_id", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_user_teams_by_id",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def export_alert_rules(
    format_: Literal["yaml", "json", "hcl"] | None = Field(None, alias="format", description="File format for the exported rules. Choose from YAML, JSON, or HCL. Defaults to YAML if not specified. The query parameter takes precedence over the Accept header."),
    folder_uid: list[str] | None = Field(None, alias="folderUid", description="Filter export to specific folders by their UIDs. Provide one or more folder UIDs to limit the rules exported to those folders only."),
    group: str | None = Field(None, description="Filter export to a specific rule group by name. Can only be used together with a single folder UID. Ignored if multiple folders or no folder is specified."),
    rule_uid: str | None = Field(None, alias="ruleUid", description="Export a single alert rule by its UID. When specified, folderUid and group parameters must be empty. Takes precedence over folder and group filters."),
) -> dict[str, Any] | ToolResult:
    """Export all alert rules or a filtered subset in provisioning file format (YAML, JSON, or HCL). Useful for backing up, version controlling, or migrating alert rule configurations."""

    # Construct request model with validation
    try:
        _request = _models.RouteGetAlertRulesExportRequest(
            query=_models.RouteGetAlertRulesExportRequestQuery(format_=format_, folder_uid=folder_uid, group=group, rule_uid=rule_uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_alert_rules: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/provisioning/alert-rules/export"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_alert_rules")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_alert_rules", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_alert_rules",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def export_alert_rule(
    uid: str = Field(..., alias="UID", description="The unique identifier of the alert rule to export."),
    format_: Literal["yaml", "json", "hcl"] | None = Field(None, alias="format", description="The file format for the exported alert rule. Choose from YAML, JSON, or HCL. Defaults to YAML if not specified."),
) -> dict[str, Any] | ToolResult:
    """Export an alert rule in provisioning file format (YAML, JSON, or HCL) for use in infrastructure-as-code workflows."""

    # Construct request model with validation
    try:
        _request = _models.RouteGetAlertRuleExportRequest(
            path=_models.RouteGetAlertRuleExportRequestPath(uid=uid),
            query=_models.RouteGetAlertRuleExportRequestQuery(format_=format_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_alert_rule: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/provisioning/alert-rules/{UID}/export", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/provisioning/alert-rules/{UID}/export"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_alert_rule")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_alert_rule", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_alert_rule",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def list_contact_points() -> dict[str, Any] | ToolResult:
    """Retrieve all configured contact points for notifications and alerts. Contact points define where and how notifications are sent."""

    # Extract parameters for API call
    _http_path = "/v1/provisioning/contact-points"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_contact_points")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_contact_points", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_contact_points",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def create_contact_point(
    settings: dict[str, Any] = Field(..., description="Configuration settings for the contact point. The structure and required fields depend on the selected type (e.g., webhook URL, email address, API credentials)."),
    type_: Literal["alertmanager", "dingding", "discord", "email", "googlechat", "kafka", "line", "opsgenie", "pagerduty", "pushover", "sensugo", "slack", "teams", "telegram", "threema", "victorops", "webhook", "wecom"] = Field(..., alias="type", description="The type of contact point to create. Choose from supported integrations including alertmanager, dingding, discord, email, googlechat, kafka, line, opsgenie, pagerduty, pushover, sensugo, slack, teams, telegram, threema, victorops, webhook, or wecom."),
    disable_resolve_message: bool | None = Field(None, alias="disableResolveMessage", description="Whether to disable the resolve message when alerts are resolved. Defaults to false, meaning resolve messages are sent."),
    name: str | None = Field(None, description="Name is used as grouping key in the UI. Contact points with the same name will be grouped in the UI."),
) -> dict[str, Any] | ToolResult:
    """Create a new contact point for alert notifications. Specify the contact point type and configure its settings to enable routing of alerts to external services."""

    # Construct request model with validation
    try:
        _request = _models.RoutePostContactpointsRequest(
            body=_models.RoutePostContactpointsRequestBody(disable_resolve_message=disable_resolve_message, settings=settings, type_=type_, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_contact_point: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/provisioning/contact-points"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_contact_point")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_contact_point", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_contact_point",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def export_contact_points(
    format_: Literal["yaml", "json", "hcl"] | None = Field(None, alias="format", description="File format for the exported contact points. Choose from YAML, JSON, or HCL. Defaults to YAML if not specified."),
    decrypt: bool | None = Field(None, description="Whether to decrypt sensitive settings in the export. When false (default), secure settings are redacted. Only org admins can view decrypted values."),
) -> dict[str, Any] | ToolResult:
    """Export all provisioned contact points in your preferred format (YAML, JSON, or HCL). Optionally decrypt secure settings if you have org admin permissions."""

    # Construct request model with validation
    try:
        _request = _models.RouteGetContactpointsExportRequest(
            query=_models.RouteGetContactpointsExportRequestQuery(format_=format_, decrypt=decrypt)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_contact_points: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/provisioning/contact-points/export"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_contact_points")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_contact_points", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_contact_points",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def update_contact_point(
    uid: str = Field(..., alias="UID", description="The unique identifier of the contact point to update."),
    settings: dict[str, Any] = Field(..., description="Configuration settings specific to the contact point type. Structure and required fields vary based on the notification channel type selected."),
    type_: Literal["alertmanager", "dingding", "discord", "email", "googlechat", "kafka", "line", "opsgenie", "pagerduty", "pushover", "sensugo", "slack", "teams", "telegram", "threema", "victorops", "webhook", "wecom"] = Field(..., alias="type", description="The notification channel type for this contact point. Supported types include webhook, email, Slack, PagerDuty, Telegram, Discord, and other integration platforms."),
    disable_resolve_message: bool | None = Field(None, alias="disableResolveMessage", description="Whether to disable message resolution notifications. Defaults to false, meaning resolution messages are sent by default."),
    name: str | None = Field(None, description="Name is used as grouping key in the UI. Contact points with the\nsame name will be grouped in the UI."),
) -> dict[str, Any] | ToolResult:
    """Update an existing contact point configuration with new settings and notification type. Allows modification of contact point details such as notification channel type and delivery preferences."""

    # Construct request model with validation
    try:
        _request = _models.RoutePutContactpointRequest(
            path=_models.RoutePutContactpointRequestPath(uid=uid),
            body=_models.RoutePutContactpointRequestBody(disable_resolve_message=disable_resolve_message, settings=settings, type_=type_, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_contact_point: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/provisioning/contact-points/{UID}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/provisioning/contact-points/{UID}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_contact_point")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_contact_point", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_contact_point",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def delete_contact_point(uid: str = Field(..., alias="UID", description="The unique identifier of the contact point to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a contact point by its unique identifier. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.RouteDeleteContactpointsRequest(
            path=_models.RouteDeleteContactpointsRequestPath(uid=uid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_contact_point: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/provisioning/contact-points/{UID}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/provisioning/contact-points/{UID}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_contact_point")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_contact_point", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_contact_point",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def export_alert_rule_group(
    folder_uid: str = Field(..., alias="FolderUID", description="The unique identifier of the folder containing the alert rule group to export."),
    group: str = Field(..., alias="Group", description="The name or identifier of the alert rule group to export."),
    format_: Literal["yaml", "json", "hcl"] | None = Field(None, alias="format", description="The file format for the exported provisioning file. Supports YAML, JSON, or HCL formats. Defaults to YAML if not specified."),
) -> dict[str, Any] | ToolResult:
    """Export an alert rule group in provisioning file format (YAML, JSON, or HCL) for backup, version control, or migration purposes."""

    # Construct request model with validation
    try:
        _request = _models.RouteGetAlertRuleGroupExportRequest(
            path=_models.RouteGetAlertRuleGroupExportRequestPath(folder_uid=folder_uid, group=group),
            query=_models.RouteGetAlertRuleGroupExportRequestQuery(format_=format_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_alert_rule_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/provisioning/folder/{FolderUID}/rule-groups/{Group}/export", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/provisioning/folder/{FolderUID}/rule-groups/{Group}/export"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_alert_rule_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_alert_rule_group", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_alert_rule_group",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def list_mute_timings() -> dict[str, Any] | ToolResult:
    """Retrieve all configured mute timings that control when notifications and alerts are suppressed in the system."""

    # Extract parameters for API call
    _http_path = "/v1/provisioning/mute-timings"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_mute_timings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_mute_timings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_mute_timings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def export_mute_timings(format_: Literal["yaml", "json", "hcl"] | None = Field(None, alias="format", description="File format for the exported mute timings. Choose from YAML, JSON, or HCL formats. Defaults to YAML if not specified.")) -> dict[str, Any] | ToolResult:
    """Export all configured mute timings in provisioning format. Returns mute timing definitions that can be used for infrastructure-as-code deployment."""

    # Construct request model with validation
    try:
        _request = _models.RouteExportMuteTimingsRequest(
            query=_models.RouteExportMuteTimingsRequestQuery(format_=format_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_mute_timings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/provisioning/mute-timings/export"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_mute_timings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_mute_timings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_mute_timings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def get_mute_timing(name: str = Field(..., description="The unique identifier of the mute timing to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific mute timing configuration by name. Mute timings define periods when alerts and notifications are suppressed."""

    # Construct request model with validation
    try:
        _request = _models.RouteGetMuteTimingRequest(
            path=_models.RouteGetMuteTimingRequestPath(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_mute_timing: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/provisioning/mute-timings/{name}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/provisioning/mute-timings/{name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_mute_timing")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_mute_timing", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_mute_timing",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def update_mute_timing(
    name: str = Field(..., description="The unique identifier of the mute timing to replace. Must match an existing mute timing name in the system."),
    time_intervals: list[_models.TimeInterval] | None = Field(None, description="Array of time intervals during which alerts should be muted. Each interval defines a period when muting is active. The order of intervals may affect evaluation logic."),
) -> dict[str, Any] | ToolResult:
    """Replace an existing mute timing configuration with new time intervals. This operation completely overwrites the mute timing identified by name with the provided settings."""

    # Construct request model with validation
    try:
        _request = _models.RoutePutMuteTimingRequest(
            path=_models.RoutePutMuteTimingRequestPath(name=name),
            body=_models.RoutePutMuteTimingRequestBody(time_intervals=time_intervals)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_mute_timing: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/provisioning/mute-timings/{name}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/provisioning/mute-timings/{name}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_mute_timing")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_mute_timing", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_mute_timing",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def delete_mute_timing(name: str = Field(..., description="The name of the mute timing to delete. Must match an existing mute timing configuration.")) -> dict[str, Any] | ToolResult:
    """Delete a mute timing configuration by name. This removes the specified mute timing rule from the provisioning system."""

    # Construct request model with validation
    try:
        _request = _models.RouteDeleteMuteTimingRequest(
            path=_models.RouteDeleteMuteTimingRequestPath(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_mute_timing: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/provisioning/mute-timings/{name}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/provisioning/mute-timings/{name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_mute_timing")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_mute_timing", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_mute_timing",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def export_mute_timing(
    name: str = Field(..., description="The name of the mute timing to export."),
    format_: Literal["yaml", "json", "hcl"] | None = Field(None, alias="format", description="The format for the exported file. Choose from YAML, JSON, or HCL. Defaults to YAML if not specified."),
) -> dict[str, Any] | ToolResult:
    """Export a mute timing configuration in the specified provisioning format (YAML, JSON, or HCL) for use in infrastructure-as-code workflows."""

    # Construct request model with validation
    try:
        _request = _models.RouteExportMuteTimingRequest(
            path=_models.RouteExportMuteTimingRequestPath(name=name),
            query=_models.RouteExportMuteTimingRequestQuery(format_=format_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for export_mute_timing: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/provisioning/mute-timings/{name}/export", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/provisioning/mute-timings/{name}/export"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("export_mute_timing")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("export_mute_timing", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="export_mute_timing",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def list_notification_templates() -> dict[str, Any] | ToolResult:
    """Retrieve all available notification template groups. Use this to discover what templates are configured in your provisioning system."""

    # Extract parameters for API call
    _http_path = "/v1/provisioning/templates"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_notification_templates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_notification_templates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_notification_templates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def get_notification_template(name: str = Field(..., description="The name of the notification template group to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a notification template group by name. Returns the template configuration for the specified template group."""

    # Construct request model with validation
    try:
        _request = _models.RouteGetTemplateRequest(
            path=_models.RouteGetTemplateRequestPath(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_notification_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/provisioning/templates/{name}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/provisioning/templates/{name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_notification_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_notification_template", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_notification_template",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def update_notification_template(
    name: str = Field(..., description="The unique identifier of the notification template group to update. Used to locate and modify the specific template configuration."),
    template: str | None = Field(None, description="The updated template content or configuration for the notification template group. Defines the structure and content of notifications sent through this template."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing notification template group with new configuration. Allows modification of template settings for the specified template group name."""

    # Construct request model with validation
    try:
        _request = _models.RoutePutTemplateRequest(
            path=_models.RoutePutTemplateRequestPath(name=name),
            body=_models.RoutePutTemplateRequestBody(template=template)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_notification_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/provisioning/templates/{name}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/provisioning/templates/{name}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_notification_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_notification_template", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_notification_template",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: provisioning
@mcp.tool()
async def delete_notification_template(name: str = Field(..., description="The name of the notification template group to delete. Must be an exact match to an existing template group.")) -> dict[str, Any] | ToolResult:
    """Delete a notification template group by name. This operation permanently removes the template group and all associated configurations."""

    # Construct request model with validation
    try:
        _request = _models.RouteDeleteTemplateRequest(
            path=_models.RouteDeleteTemplateRequestPath(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_notification_template: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/provisioning/templates/{name}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/provisioning/templates/{name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_notification_template")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_notification_template", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_notification_template",
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
        print("  python grafana_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Grafana MCP Server")

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
    logger.info("Starting Grafana MCP Server")
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
